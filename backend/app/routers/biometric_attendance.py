from __future__ import annotations

import base64
import re
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe
from threading import Lock

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from ..database import get_db
from ..importers.biometric_attendance import (
    MAX_IMPORT_BYTES,
    INDIA_TZ,
    SheetData,
    is_essl_form_j_sheet,
    normalize_device_id,
    parse_essl_form_j_pdf,
    parse_essl_form_j_sheet,
    parse_punches,
    read_workbook,
    sheet_preview,
)
from ..models import (
    AttendanceEntry,
    AttendanceRegister,
    BiometricAttendanceDay,
    BiometricImportBatch,
    DeviceAttendanceIdentity,
    Enrollment,
    Student,
    StudentAcademicProfile,
    User,
)
from ..security import require_roles
from ..services import audit


router = APIRouter(prefix="/api/attendance/biometric-imports", tags=["biometric attendance"])
DEVICE_KEY = "x2008-abfr220607313"
DEVICE_SOURCE_CODE_ALIASES = {
    "51": "E-02",  # Vidhisha patil -> Vidisha Patil
    "52": "E-03",  # Vihan Jamnik -> Vihan R. Jamnik
    "53": "E-04",  # Siddhart Wankhede -> Siddharth Wankhede
    "59": "E-11",  # Kajol Sawarkar -> Kajal Sawarkar
    "80": "E-33",  # Ayush Sangode -> Aayush Sangode
    "82": "E-35",  # Arick Sathe -> Arik Sathe
}
PREVIEW_TTL_SECONDS = 30 * 60
PREVIEW_LIMIT = 4
_PREVIEWS: dict[str, dict] = {}
_PREVIEW_LOCK = Lock()


def _prune_previews():
    now = datetime.now(timezone.utc).timestamp()
    expired = [token for token, item in _PREVIEWS.items() if now - item["createdAt"] > PREVIEW_TTL_SECONDS]
    for token in expired:
        _PREVIEWS.pop(token, None)
    if len(_PREVIEWS) > PREVIEW_LIMIT:
        oldest = sorted(_PREVIEWS, key=lambda token: _PREVIEWS[token]["createdAt"])
        for token in oldest[:len(_PREVIEWS) - PREVIEW_LIMIT]:
            _PREVIEWS.pop(token, None)


def _store_preview(token: str, value: dict):
    with _PREVIEW_LOCK:
        _prune_previews()
        _PREVIEWS[token] = value


def _preview_for(token: str):
    with _PREVIEW_LOCK:
        _prune_previews()
        return _PREVIEWS.get(token)


def _encode(content: bytes) -> str:
    return base64.b64encode(content).decode("ascii")


def _decode(content: str) -> bytes:
    return base64.b64decode(content.encode("ascii"))


def _device_mappings(db: Session) -> dict[str, DeviceAttendanceIdentity]:
    return {
        item.device_user_id: item
        for item in db.query(DeviceAttendanceIdentity).filter_by(device_key=DEVICE_KEY).all()
    }


def _active_students(db: Session):
    rows = (
        db.query(Student, Enrollment, StudentAcademicProfile)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .outerjoin(StudentAcademicProfile, StudentAcademicProfile.student_id == Student.id)
        .filter(Student.status == "active", Enrollment.is_active.is_(True))
        .order_by(Student.full_name)
        .all()
    )
    seen = set()
    result = []
    for student, enrollment, profile in rows:
        if student.id in seen:
            continue
        seen.add(student.id)
        result.append({
            "id": student.id,
            "admissionNumber": student.admission_number,
            "fullName": student.full_name,
            "mobile": student.mobile,
            "batch": (profile.batch_name if profile and profile.batch_name else enrollment.batch),
            "program": enrollment.program,
            "sourceStudentCode": profile.source_student_code if profile else None,
        })
    return result


class BiometricMappingChoice(BaseModel):
    device_user_id: str = Field(alias="deviceUserId", min_length=1, max_length=120)
    student_id: str | None = Field(default=None, alias="studentId")
    ignore: bool = False
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def one_target(self):
        if bool(self.student_id) == bool(self.ignore):
            raise ValueError("Choose one student or mark the device ID as ignored")
        return self


class BiometricImportSelection(BaseModel):
    preview_token: str = Field(alias="previewToken", min_length=10, max_length=255)
    sheet_name: str = Field(alias="sheetName", min_length=1, max_length=255)
    device_id_column: str = Field(alias="deviceIdColumn", min_length=1, max_length=255)
    datetime_column: str | None = Field(default=None, alias="datetimeColumn", max_length=255)
    date_column: str | None = Field(default=None, alias="dateColumn", max_length=255)
    time_column: str | None = Field(default=None, alias="timeColumn", max_length=255)
    name_column: str | None = Field(default=None, alias="nameColumn", max_length=255)
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def time_columns(self):
        if not self.datetime_column and not (self.date_column and self.time_column):
            raise ValueError("Choose a combined timestamp or separate date and time columns")
        return self


class BiometricImportCommit(BiometricImportSelection):
    mappings: list[BiometricMappingChoice] = Field(default_factory=list, max_length=5000)


@router.post("/preview")
async def preview_biometric_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner", "academic_coordinator", "attendance_operator")),
):
    filename = (file.filename or "attendance-export").strip()
    content = await file.read(MAX_IMPORT_BYTES + 1)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    try:
        if extension == "pdf":
            punches, row_errors, report = parse_essl_form_j_pdf(content)
            if row_errors:
                raise ValueError(row_errors[0]["message"])
            report_rows = [{
                "Device Code": item["deviceUserId"],
                "Student Name": item["deviceName"],
                "Date": item["attendanceDate"].isoformat(),
                "InTime": item["firstPunchAt"].astimezone(INDIA_TZ).strftime("%H:%M"),
            } for item in punches[:5]]
            sheets_payload = [{
                "name": f"Form J · {report['reportMonth']}",
                "headers": ["Device Code", "Student Name", "Date", "InTime"],
                "rows": report_rows,
                "rowCount": len(punches),
                "detected": {
                    "device_id": "Device Code",
                    "name": "Student Name",
                    "date": "Date",
                    "time": "InTime",
                    "datetime": None,
                },
            }]
            source_format = "essl_form_j"
            source_report = report
        else:
            sheets = read_workbook(content, filename)
            form_j_sheet = next((sheet for sheet in sheets if is_essl_form_j_sheet(sheet)), None)
            if form_j_sheet:
                punches, row_errors, report = parse_essl_form_j_sheet(form_j_sheet)
                if row_errors:
                    raise ValueError(row_errors[0]["message"])
                report_rows = [{
                    "Device Code": item["deviceUserId"],
                    "Student Name": item["deviceName"],
                    "Date": item["attendanceDate"].isoformat(),
                    "InTime": item["firstPunchAt"].astimezone(INDIA_TZ).strftime("%H:%M"),
                } for item in punches[:5]]
                sheets_payload = [{
                    "name": form_j_sheet.name,
                    "headers": ["Device Code", "Student Name", "Date", "InTime"],
                    "rows": report_rows,
                    "rowCount": len(punches),
                    "detected": {
                        "device_id": "Device Code",
                        "name": "Student Name",
                        "date": "Date",
                        "time": "InTime",
                        "datetime": None,
                    },
                }]
                source_format = "essl_form_j_workbook"
                source_report = {**report, "sourceSheet": form_j_sheet.name}
            else:
                sheets_payload = [sheet_preview(sheet) for sheet in sheets]
                source_format = "workbook"
                source_report = None
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    token = token_urlsafe(32)
    _store_preview(token, {
        "actorId": actor.id,
        "filename": filename,
        "content": _encode(content),
        "sourceFormat": source_format,
        "sourceReport": source_report,
        "createdAt": datetime.now(timezone.utc).timestamp(),
    })
    mappings = _device_mappings(db)
    students = _active_students(db)
    return {
        "previewToken": token,
        "sourceName": filename,
        "device": {
            "key": DEVICE_KEY,
            "name": "X2008",
            "serialNumber": "ABFR220607313",
            "network": "192.168.1.201 · TCP 4370",
        },
        "sourceFormat": source_format,
        "report": source_report,
        "sheets": sheets_payload,
        "students": students,
        "savedMappings": [{
            "deviceUserId": device_user_id,
            "studentId": mapping.student_id,
            "ignore": mapping.is_ignored,
        } for device_user_id, mapping in sorted(mappings.items())],
    }


def _resolve_preview(token: str, actor: User) -> tuple[dict, list[SheetData]]:
    preview = _preview_for(token)
    if not preview or preview["actorId"] != actor.id:
        raise HTTPException(410, "This preview expired. Select the attendance file again")
    try:
        content = _decode(preview["content"])
        if preview.get("sourceFormat") == "essl_form_j":
            return preview, []
        return preview, read_workbook(content, preview["filename"])
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


def _selected_punches(payload: BiometricImportSelection, actor: User):
    preview, sheets = _resolve_preview(payload.preview_token, actor)
    if preview.get("sourceFormat") == "essl_form_j":
        try:
            punches, row_errors, report = parse_essl_form_j_pdf(_decode(preview["content"]))
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        sheet = SheetData(f"Form J · {report['reportMonth']}", [])
    elif preview.get("sourceFormat") == "essl_form_j_workbook":
        sheet = next((item for item in sheets if item.name == payload.sheet_name), None)
        if not sheet:
            raise HTTPException(422, "Choose a valid worksheet")
        try:
            punches, row_errors, _ = parse_essl_form_j_sheet(sheet)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
    else:
        sheet = next((item for item in sheets if item.name == payload.sheet_name), None)
        if not sheet:
            raise HTTPException(422, "Choose a valid worksheet")
        try:
            punches, row_errors = parse_punches(
                sheet,
                payload.device_id_column,
                payload.datetime_column,
                payload.date_column,
                payload.time_column,
                payload.name_column,
            )
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
    if row_errors:
        raise HTTPException(422, {
            "message": "Some attendance rows could not be read",
            "rows": row_errors[:20],
            "additionalErrors": max(0, len(row_errors) - 20),
        })
    if not punches:
        raise HTTPException(422, "No valid attendance punches were found")
    return preview, sheet, punches


@router.post("/analyze")
def analyze_biometric_import(
    payload: BiometricImportSelection,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner", "academic_coordinator", "attendance_operator")),
):
    _, _, punches = _selected_punches(payload, actor)
    mappings = _device_mappings(db)
    people = {}
    for item in punches:
        person = people.setdefault(item["deviceUserId"], {
            "deviceUserId": item["deviceUserId"],
            "deviceName": item["deviceName"],
            "firstDate": item["attendanceDate"],
            "lastDate": item["attendanceDate"],
            "dayCount": 0,
            "studentId": None,
            "ignore": False,
        })
        if not person["deviceName"] and item["deviceName"]:
            person["deviceName"] = item["deviceName"]
        person["firstDate"] = min(person["firstDate"], item["attendanceDate"])
        person["lastDate"] = max(person["lastDate"], item["attendanceDate"])
        person["dayCount"] += 1
    students = _active_students(db)
    by_name = defaultdict(list)
    by_source_code = defaultdict(list)
    for student in students:
        normalized_name = "".join(character for character in student["fullName"].casefold() if character.isalnum())
        by_name[normalized_name].append(student["id"])
        source_code = student.get("sourceStudentCode") or ""
        match = re.fullmatch(r"([A-Za-z]+)[^0-9]*(\d+)", source_code)
        if match:
            by_source_code[f"{match.group(1).upper()}{int(match.group(2))}"].append(student["id"])
    for device_user_id, person in people.items():
        mapping = mappings.get(device_user_id)
        if mapping:
            person["studentId"] = mapping.student_id
            person["ignore"] = mapping.is_ignored
            person["matchReason"] = "Saved mapping"
            continue
        source_identifier = DEVICE_SOURCE_CODE_ALIASES.get(device_user_id, device_user_id)
        code_match = re.fullmatch(r"([A-Za-z]+)[^0-9]*(\d+)", source_identifier)
        normalized_code = f"{code_match.group(1).upper()}{int(code_match.group(2))}" if code_match else ""
        code_candidates = by_source_code.get(normalized_code, [])
        normalized_name = "".join(character for character in person["deviceName"].casefold() if character.isalnum())
        name_candidates = by_name.get(normalized_name, [])
        candidates = code_candidates or name_candidates
        if len(candidates) == 1:
            person["studentId"] = candidates[0]
            person["matchReason"] = "Confirmed name merge" if device_user_id in DEVICE_SOURCE_CODE_ALIASES else "Student code" if code_candidates else "Exact name"
    return {
        "rowsSeen": punches[0].get("rowsSeen", len(punches)),
        "uniqueAttendanceDays": len(punches),
        "duplicateRows": max(0, punches[0].get("rowsSeen", len(punches)) - len(punches)),
        "dateFrom": min(item["attendanceDate"] for item in punches),
        "dateTo": max(item["attendanceDate"] for item in punches),
        "deviceUsers": sorted(people.values(), key=lambda item: item["deviceUserId"]),
    }


def _apply_mapping_choices(
    db: Session,
    actor: User,
    choices: dict[str, BiometricMappingChoice],
    active_ids: set[str],
) -> dict[str, DeviceAttendanceIdentity]:
    """Apply a complete mapping review without one database query per device ID."""
    mappings = _device_mappings(db)
    student_owners = {
        mapping.student_id: device_user_id
        for device_user_id, mapping in mappings.items()
        if device_user_id not in choices and mapping.student_id
    }
    for device_user_id, choice in choices.items():
        if choice.student_id and choice.student_id not in active_ids:
            raise HTTPException(409, f"The selected student for device ID {device_user_id} is not active")
        conflicting_device_id = student_owners.get(choice.student_id) if choice.student_id else None
        if conflicting_device_id and conflicting_device_id != device_user_id:
            raise HTTPException(
                409,
                f"Device IDs {conflicting_device_id} and {device_user_id} cannot be assigned to the same student",
            )
        mapping = mappings.get(device_user_id)
        if mapping:
            mapping.student_id = choice.student_id
            mapping.is_ignored = choice.ignore
            mapping.created_by = actor.id
        else:
            mapping = DeviceAttendanceIdentity(
                device_key=DEVICE_KEY,
                device_user_id=device_user_id,
                student_id=choice.student_id,
                is_ignored=choice.ignore,
                created_by=actor.id,
            )
            db.add(mapping)
            mappings[device_user_id] = mapping
        if choice.student_id:
            student_owners[choice.student_id] = device_user_id
    return mappings


def _open_biometric_register(db: Session, attendance_date, batch_name: str):
    register = (
        db.query(AttendanceRegister)
        .filter_by(
            register_kind="biometric",
            attendance_date=attendance_date,
            batch_name=batch_name,
            stream_name="__all__",
            subject_name="Biometric attendance",
        )
        .one_or_none()
    )
    if not register:
        register = AttendanceRegister(
            class_session_id=None,
            register_kind="biometric",
            attendance_date=attendance_date,
            batch_name=batch_name,
            stream_name="__all__",
            subject_name="Biometric attendance",
            status="draft",
        )
        db.add(register)
        db.flush()
    return register


@router.post("")
def commit_biometric_import(
    payload: BiometricImportCommit,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner", "academic_coordinator", "attendance_operator")),
):
    preview, sheet, punches = _selected_punches(payload, actor)

    raw_content = _decode(preview["content"])
    source_hash = sha256(raw_content).hexdigest()
    duplicate_file = db.query(BiometricImportBatch).filter_by(source_hash=source_hash).one_or_none()
    if duplicate_file:
        with _PREVIEW_LOCK:
            _PREVIEWS.pop(payload.preview_token, None)
        return {
            "id": duplicate_file.id,
            "sourceName": duplicate_file.source_name,
            "attendanceDays": duplicate_file.attendance_days,
            "matchedStudents": duplicate_file.matched_students,
            "ignoredDeviceIds": duplicate_file.ignored_device_ids,
            "punchesCreated": 0,
            "punchesUpdated": 0,
            "registers": [],
            "alreadyImported": True,
            "message": "Attendance was already imported; no duplicate records were created",
        }

    active_students = _active_students(db)
    active_ids = {item["id"] for item in active_students}
    choices = {normalize_device_id(item.device_user_id): item for item in payload.mappings}
    mappings = _apply_mapping_choices(db, actor, choices, active_ids)
    db.flush()
    device_ids = {item["deviceUserId"] for item in punches}
    unresolved = sorted(
        device_id for device_id in device_ids
        if device_id not in mappings
        or (not mappings[device_id].student_id and not mappings[device_id].is_ignored)
    )
    if unresolved:
        raise HTTPException(409, {
            "message": "Assign or ignore every new biometric device ID before importing",
            "deviceUserIds": unresolved,
        })

    ignored_ids = {device_id for device_id in device_ids if mappings[device_id].is_ignored}
    linked = [item for item in punches if item["deviceUserId"] not in ignored_ids]
    import_batch = BiometricImportBatch(
        device_key=DEVICE_KEY,
        source_name=preview["filename"][:255],
        source_hash=source_hash,
        source_sheet=sheet.name[:255],
        rows_seen=punches[0].get("rowsSeen", len(punches)),
        attendance_days=len({item["attendanceDate"] for item in linked}),
        matched_students=len({mappings[item["deviceUserId"]].student_id for item in linked}),
        ignored_device_ids=len(ignored_ids),
        duplicate_rows=max(0, punches[0].get("rowsSeen", len(punches)) - len(punches)),
        status="completed",
        actor_id=actor.id,
    )
    db.add(import_batch)
    db.flush()

    enrollments = {}
    enrollment_rows = (
        db.query(Enrollment)
        .filter(Enrollment.student_id.in_(active_ids), Enrollment.is_active.is_(True))
        .order_by(Enrollment.created_at.desc())
        .all()
    )
    for item in enrollment_rows:
        enrollments.setdefault(item.student_id, item)
    created_punches = 0
    updated_punches = 0
    register_student_rows: dict[tuple, dict[str, datetime]] = defaultdict(dict)
    existing_days = {}
    if linked:
        attendance_date_from = min(item["attendanceDate"] for item in linked)
        attendance_date_to = max(item["attendanceDate"] for item in linked)
        existing_days = {
            (item.device_user_id, item.attendance_date): item
            for item in (
                db.query(BiometricAttendanceDay)
                .filter(
                    BiometricAttendanceDay.device_key == DEVICE_KEY,
                    BiometricAttendanceDay.device_user_id.in_({item["deviceUserId"] for item in linked}),
                    BiometricAttendanceDay.attendance_date.between(attendance_date_from, attendance_date_to),
                )
                .all()
            )
        }
    for item in linked:
        mapping = mappings[item["deviceUserId"]]
        student_id = mapping.student_id
        attendance_key = (item["deviceUserId"], item["attendanceDate"])
        existing = existing_days.get(attendance_key)
        if existing:
            existing_punch = existing.first_punch_at
            if existing_punch.tzinfo is None:
                existing_punch = existing_punch.replace(tzinfo=timezone.utc)
            if item["firstPunchAt"] < existing_punch:
                existing.first_punch_at = item["firstPunchAt"]
                existing.student_id = student_id
                existing.import_batch_id = import_batch.id
                updated_punches += 1
                existing_punch = item["firstPunchAt"]
            first_punch = min(existing_punch, item["firstPunchAt"])
        else:
            attendance_day = BiometricAttendanceDay(
                import_batch_id=import_batch.id,
                device_key=DEVICE_KEY,
                device_user_id=item["deviceUserId"],
                student_id=student_id,
                attendance_date=item["attendanceDate"],
                first_punch_at=item["firstPunchAt"],
            )
            db.add(attendance_day)
            existing_days[attendance_key] = attendance_day
            first_punch = item["firstPunchAt"]
            created_punches += 1
        enrollment = enrollments.get(student_id)
        batch_name = enrollment.batch if enrollment else None
        if batch_name in {"Tatva", "Essential"}:
            register_student_rows[(item["attendanceDate"], batch_name)][student_id] = first_punch

    batch_rosters: dict[str, set[str]] = defaultdict(set)
    for student in active_students:
        if student["batch"] in {"Tatva", "Essential"}:
            batch_rosters[student["batch"]].add(student["id"])

    registers = []
    for (attendance_date, batch_name), arrivals in register_student_rows.items():
        register = _open_biometric_register(db, attendance_date, batch_name)
        eligible_student_ids = batch_rosters.get(batch_name, set())
        existing_entries = {
            row.student_id: row
            for row in db.query(AttendanceEntry).filter_by(register_id=register.id).all()
        }
        for student_id in eligible_student_ids:
            first_punch = arrivals.get(student_id)
            entry = existing_entries.get(student_id)
            if first_punch:
                if entry:
                    entry.status = "present"
                    entry.reason = "Biometric first punch"
                    entry.marked_by = actor.id
                    if not entry.arrival_at or first_punch < entry.arrival_at:
                        entry.arrival_at = first_punch
                else:
                    db.add(AttendanceEntry(
                        register_id=register.id,
                        student_id=student_id,
                        status="present",
                        reason="Biometric first punch",
                        marked_by=actor.id,
                        arrival_at=first_punch,
                    ))
            elif register.status != "submitted":
                if entry:
                    entry.status = "absent"
                    entry.reason = "No biometric punch"
                    entry.marked_by = actor.id
                    entry.arrival_at = None
                else:
                    db.add(AttendanceEntry(
                        register_id=register.id,
                        student_id=student_id,
                        status="absent",
                        reason="No biometric punch",
                        marked_by=actor.id,
                        arrival_at=None,
                    ))

        if register.status != "submitted":
            register.status = "submitted"
            register.submitted_at = datetime.now(timezone.utc)
            register.submitted_by = actor.id
        present_count = len(set(arrivals) & eligible_student_ids)
        registers.append({
            "id": register.id,
            "date": attendance_date.isoformat(),
            "batch": batch_name,
            "present": present_count,
            "absent": max(0, len(eligible_student_ids) - present_count),
            "students": len(eligible_student_ids),
            "status": register.status,
        })

    audit(
        db,
        actor,
        "attendance.biometric.import",
        "biometric_import_batch",
        import_batch.id,
        after={
            "sourceName": preview["filename"],
            "sourceHash": source_hash,
            "device": DEVICE_KEY,
            "punchesCreated": created_punches,
            "punchesUpdated": updated_punches,
            "ignoredDeviceIds": sorted(ignored_ids),
            "registers": registers,
        },
    )
    db.commit()
    with _PREVIEW_LOCK:
        _PREVIEWS.pop(payload.preview_token, None)
    return {
        "id": import_batch.id,
        "sourceName": import_batch.source_name,
        "attendanceDays": import_batch.attendance_days,
        "matchedStudents": import_batch.matched_students,
        "ignoredDeviceIds": import_batch.ignored_device_ids,
        "punchesCreated": created_punches,
        "punchesUpdated": updated_punches,
        "registers": registers,
        "message": "Attendance imported and published to student and parent accounts",
    }
