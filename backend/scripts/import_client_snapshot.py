"""Import the client-confirmed 3 August 2026 operational snapshot.

The command is a strict dry run unless ``--apply`` is supplied. It preserves
the original payment ledger by posting non-cash balance reconciliation entries
and stores attendance as aggregate period summaries because no daily dates were
provided in the client report.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    AttendancePeriodSummary,
    AuditLog,
    Batch,
    ClassSession,
    Enrollment,
    FacultyTeachingAssignment,
    FeeAgreement,
    FeeInstallment,
    ParentAccount,
    PaymentTransaction,
    Room,
    Student,
    StudentAcademicProfile,
    StudentAccount,
    Subject,
    User,
)
from app.security import hash_password
from app.services import payment_effect


DEFAULT_MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "imports"
    / "client_snapshot_2026_08_03.json"
)
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _name_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _iso_date(value: str) -> date:
    return date.fromisoformat(value)


def _local_datetime(day: date, clock: str) -> datetime:
    hour, minute = (int(part) for part in clock.split(":"))
    return datetime.combine(day, time(hour, minute), INDIA_TZ).astimezone(timezone.utc)


def _audit(db: Session, snapshot_id: str, action: str, entity_type: str, entity_id: str, before=None, after=None):
    db.add(AuditLog(
        actor_id=None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        request_id=snapshot_id,
    ))


def _load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    rows = manifest.get("activeStudents", [])
    if manifest.get("schemaVersion") != 1 or len(rows) != 62:
        raise RuntimeError("Unsupported or incomplete client snapshot")
    if len({_name_key(row["name"]) for row in rows}) != len(rows):
        raise RuntimeError("Client snapshot contains duplicate student names")
    if sum(int(row["balance"]) for row in rows) != 3_282_900:
        raise RuntimeError("Client balance control total does not equal ₹32,82,900")
    if Counter(row["batch"] for row in rows) != Counter({"Tatva": 23, "Essential": 39}):
        raise RuntimeError("Client attendance batch controls do not reconcile")
    for row in rows:
        if int(row["present"]) + int(row["absent"]) != int(row["workingDays"]):
            raise RuntimeError(f"Attendance total does not reconcile for {row['name']}")
        calculated = round(int(row["present"]) / int(row["workingDays"]) * 100, 1)
        if calculated != float(row["rate"]):
            raise RuntimeError(f"Attendance rate does not reconcile for {row['name']}")
    return manifest


def _strict_students(db: Session, manifest: dict) -> dict[str, Student]:
    students = db.query(Student).filter(Student.is_test_account.is_(False)).all()
    by_key: dict[str, Student] = {}
    duplicates = set()
    for student in students:
        key = _name_key(student.full_name)
        if key in by_key:
            duplicates.add(key)
        by_key[key] = student
    if duplicates:
        raise RuntimeError("Production contains duplicate normalized student names")
    matched = {}
    for source in manifest["activeStudents"]:
        student = by_key.get(_name_key(source["name"]))
        if not student:
            raise RuntimeError(f"Student not found: {source['name']}")
        profile = db.get(StudentAcademicProfile, student.id)
        if not profile:
            raise RuntimeError(f"Academic profile not found: {source['name']}")
        accepted_codes = {source["code"], *source.get("previousCodes", [])}
        if profile.source_student_code not in accepted_codes:
            raise RuntimeError(
                f"Source code mismatch for {source['name']}: "
                f"{profile.source_student_code} != {source['code']}"
            )
        matched[source["name"]] = student
    return matched


def _archive_students(db: Session, manifest: dict, students_by_name: dict[str, Student], apply: bool) -> list[str]:
    archived = []
    production_by_key = {
        _name_key(row.full_name): row
        for row in db.query(Student).filter(Student.is_test_account.is_(False)).all()
    }
    for name in manifest["archiveFromActiveRoster"]:
        student = production_by_key.get(_name_key(name))
        if not student:
            raise RuntimeError(f"Archive target not found: {name}")
        if student.status != "active":
            continue
        archived.append(student.full_name)
        if not apply:
            continue
        before = {"status": student.status}
        student.status = "inactive"
        for enrollment in db.query(Enrollment).filter_by(student_id=student.id, is_active=True).all():
            enrollment.is_active = False
            enrollment.status = "inactive"
        for agreement in db.query(FeeAgreement).filter_by(student_id=student.id, status="active").all():
            agreement.status = "inactive"
        for installment in db.query(FeeInstallment).filter_by(student_id=student.id, status="scheduled").all():
            installment.status = "cancelled"
        linked_users = {
            link.user_id for link in db.query(StudentAccount).filter_by(student_id=student.id).all()
        } | {
            link.user_id for link in db.query(ParentAccount).filter_by(student_id=student.id).all()
        }
        linked_accounts = (
            db.query(User).filter(User.id.in_(linked_users)).all()
            if linked_users
            else []
        )
        for user in linked_accounts:
            user.is_active = False
            user.token_version += 1
        _audit(
            db,
            manifest["snapshotId"],
            "student.archive.client_snapshot",
            "student",
            student.id,
            before=before,
            after={"status": "inactive", "source": manifest["sources"]["attendance"]},
        )
    return archived


def _attendance(db: Session, manifest: dict, students_by_name: dict[str, Student], apply: bool) -> int:
    period_start = _iso_date(manifest["attendancePeriod"]["start"])
    period_end = _iso_date(manifest["attendancePeriod"]["end"])
    changed = 0
    for source in manifest["activeStudents"]:
        student = students_by_name[source["name"]]
        row = (
            db.query(AttendancePeriodSummary)
            .filter_by(student_id=student.id, period_start=period_start, period_end=period_end)
            .first()
        )
        values = {
            "source_student_code": source["code"],
            "batch_name": source["batch"],
            "mentor_name": source["mentor"],
            "present_days": int(source["present"]),
            "absent_days": int(source["absent"]),
            "working_days": int(source["workingDays"]),
            "attendance_rate": float(source["rate"]),
            "source_name": manifest["sources"]["attendance"],
            "source_reference": manifest["snapshotId"],
            "status": "confirmed",
        }
        if row and all(getattr(row, key) == value for key, value in values.items() if key != "attendance_rate") and float(row.attendance_rate) == values["attendance_rate"]:
            continue
        changed += 1
        if not apply:
            continue
        if not row:
            row = AttendancePeriodSummary(
                student_id=student.id,
                period_start=period_start,
                period_end=period_end,
                **values,
            )
            db.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)
        profile = db.get(StudentAcademicProfile, student.id)
        enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=student.id, is_active=True)
            .order_by(Enrollment.created_at.desc())
            .first()
        )
        before_profile = {
            "sourceStudentCode": profile.source_student_code,
            "batch": profile.batch_name,
            "mentor": profile.mentor_name,
            "enrollmentBatch": enrollment.batch if enrollment else None,
        }
        if profile.source_student_code != source["code"]:
            profile.source_student_code = source["code"]
        profile.batch_name = source["batch"]
        profile.mentor_name = source["mentor"]
        if enrollment:
            enrollment.batch = source["batch"]
        after_profile = {
            "sourceStudentCode": profile.source_student_code,
            "batch": profile.batch_name,
            "mentor": profile.mentor_name,
            "enrollmentBatch": enrollment.batch if enrollment else None,
        }
        if before_profile != after_profile:
            _audit(
                db,
                manifest["snapshotId"],
                "student.roster.update.client_snapshot",
                "student",
                student.id,
                before=before_profile,
                after=after_profile,
            )
    return changed


def _finance(db: Session, manifest: dict, students_by_name: dict[str, Student], apply: bool) -> dict:
    snapshot_id = manifest["snapshotId"]
    created = 0
    unchanged = 0
    total_before = 0
    total_target = 0
    for line, source in enumerate(manifest["activeStudents"], 1):
        student = students_by_name[source["name"]]
        agreement = (
            db.query(FeeAgreement)
            .filter_by(student_id=student.id, status="active")
            .order_by(FeeAgreement.created_at.desc())
            .first()
        )
        if not agreement:
            raise RuntimeError(f"Active fee agreement not found: {source['name']}")
        transactions = db.query(PaymentTransaction).filter_by(fee_agreement_id=agreement.id).all()
        current_balance = agreement.agreed_amount - sum(payment_effect(row) for row in transactions)
        target = int(source["balance"])
        total_before += current_balance
        total_target += target
        existing = next(
            (
                row for row in transactions
                if row.legacy_import_id == snapshot_id and row.legacy_line_number == line
            ),
            None,
        )
        if existing:
            if current_balance != target:
                raise RuntimeError(f"Existing balance reconciliation no longer matches {source['name']}")
            unchanged += 1
            continue
        delta = current_balance - target
        if delta == 0:
            unchanged += 1
            continue
        created += 1
        if not apply:
            continue
        db.add(PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            legacy_import_id=snapshot_id,
            legacy_line_number=line,
            transaction_date=_iso_date(manifest["effectiveDate"]),
            amount=abs(delta),
            method="client_statement",
            transaction_type="balance_credit" if delta > 0 else "balance_debit",
            source_note=f"Client-confirmed balance as on 3 August 2026: ₹{target:,}",
            reference=manifest["sources"]["balances"],
            notes="Balance reconciliation only; this is not a payment receipt.",
            created_by=None,
            status="posted",
            reconciliation_status="ready",
        ))
    return {
        "entriesCreated": created,
        "accountsUnchanged": unchanged,
        "totalBefore": total_before,
        "totalTarget": total_target,
    }


def _resource(db: Session, model, defaults: dict, **lookup):
    row = db.query(model).filter_by(**lookup).first()
    if row:
        for key, value in defaults.items():
            setattr(row, key, value)
        return row, False
    row = model(**lookup, **defaults)
    db.add(row)
    db.flush()
    return row, True


def _timetable(db: Session, manifest: dict, apply: bool) -> dict:
    schedule = manifest["timetable"]
    source_note = f"Imported from {manifest['sources']['timetable']} [{manifest['snapshotId']}]"
    class_slots = [row for row in schedule["slots"] if row["kind"] == "class"]
    expected_sessions = 0
    start = max(_iso_date(schedule["effectiveFrom"]), _iso_date(manifest["effectiveDate"]))
    end = _iso_date(schedule["materializeThrough"])
    days = []
    cursor = start
    while cursor <= end:
        if cursor.strftime("%A") in schedule["days"]:
            days.append(cursor)
        cursor += timedelta(days=1)
    expected_sessions = len(days) * len(class_slots)
    existing_sessions = db.query(ClassSession).filter(ClassSession.notes == source_note).count()
    if existing_sessions:
        if existing_sessions != expected_sessions:
            raise RuntimeError("Partially imported timetable snapshot detected")
        return {"sessionsCreated": 0, "sessionsUnchanged": existing_sessions}
    if not apply:
        return {"sessionsCreated": expected_sessions, "sessionsUnchanged": 0}

    batches = {}
    rooms = {}
    for batch_name, capacity in (("Tatva", 23), ("Essential", 39)):
        batches[batch_name], _ = _resource(
            db,
            Batch,
            {"is_active": True},
            name=batch_name,
            program="All programs",
        )
        rooms[batch_name], _ = _resource(
            db,
            Room,
            {"capacity": capacity, "is_active": True},
            name=f"{batch_name} Classroom",
        )

    subjects = {
        row.name: row
        for row in db.query(Subject).filter(Subject.name.in_({slot["activity"] for slot in class_slots})).all()
    }
    missing_subjects = {slot["activity"] for slot in class_slots} - set(subjects)
    if missing_subjects:
        raise RuntimeError(f"Timetable subjects not found: {sorted(missing_subjects)}")

    faculty = {
        row.full_name: row
        for row in db.query(User).filter(User.role == "faculty").all()
    }
    if "Kumar Sir" not in faculty:
        kumar = User(
            mobile=None,
            email=None,
            full_name="Kumar Sir",
            password_hash=hash_password(secrets.token_urlsafe(32)),
            role="faculty",
            is_active=True,
            must_change_password=False,
            is_test_account=False,
        )
        db.add(kumar)
        db.flush()
        faculty[kumar.full_name] = kumar
    missing_faculty = {slot["faculty"] for slot in class_slots} - set(faculty)
    if missing_faculty:
        raise RuntimeError(f"Timetable faculty not found: {sorted(missing_faculty)}")

    official_pairs = {
        (slot["batch"], slot["activity"]): faculty[slot["faculty"]].id
        for slot in class_slots
    }
    for assignment, batch, subject in (
        db.query(FacultyTeachingAssignment, Batch, Subject)
        .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
        .join(Subject, Subject.id == FacultyTeachingAssignment.subject_id)
        .filter(Batch.name.in_(batches), Subject.name.in_(subjects))
        .all()
    ):
        official_faculty_id = official_pairs.get((batch.name, subject.name))
        if official_faculty_id and assignment.faculty_id != official_faculty_id:
            assignment.is_active = False

    for slot in class_slots:
        batch = batches[slot["batch"]]
        subject = subjects[slot["activity"]]
        teacher = faculty[slot["faculty"]]
        assignment = (
            db.query(FacultyTeachingAssignment)
            .filter_by(faculty_id=teacher.id, batch_id=batch.id, subject_id=subject.id)
            .first()
        )
        if assignment:
            assignment.is_active = True
        else:
            db.add(FacultyTeachingAssignment(
                faculty_id=teacher.id,
                batch_id=batch.id,
                subject_id=subject.id,
                is_active=True,
                created_by=None,
            ))
        for day in days:
            db.add(ClassSession(
                batch_id=batch.id,
                subject_id=subject.id,
                faculty_id=teacher.id,
                room_id=rooms[slot["batch"]].id,
                starts_at=_local_datetime(day, slot["start"]),
                ends_at=_local_datetime(day, slot["end"]),
                status="scheduled",
                notes=source_note,
                override_reason=None,
                created_by=None,
            ))
    return {"sessionsCreated": expected_sessions, "sessionsUnchanged": 0}


def import_snapshot(db: Session, manifest: dict, apply: bool) -> dict:
    students = _strict_students(db, manifest)
    archived = _archive_students(db, manifest, students, apply)
    attendance_changed = _attendance(db, manifest, students, apply)
    finance = _finance(db, manifest, students, apply)
    timetable = _timetable(db, manifest, apply)
    result = {
        "snapshotId": manifest["snapshotId"],
        "activeStudents": len(students),
        "archivedStudents": archived,
        "attendanceSummariesChanged": attendance_changed,
        "finance": finance,
        "timetable": timetable,
        "applied": apply,
    }
    if apply:
        _audit(
            db,
            manifest["snapshotId"],
            "client_snapshot.import",
            "client_snapshot",
            manifest["snapshotId"],
            after=result,
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    manifest = _load_manifest(args.manifest)
    with SessionLocal() as db:
        result = import_snapshot(db, manifest, args.apply)
        if args.apply:
            db.commit()
        else:
            db.rollback()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
