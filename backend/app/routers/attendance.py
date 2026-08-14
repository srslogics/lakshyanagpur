from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    AttendanceEntry,
    AttendancePeriodSummary,
    AttendanceRegister,
    Batch,
    ClassSession,
    Enrollment,
    Notice,
    Room,
    Student,
    StudentAcademicProfile,
    StudentSubjectSelection,
    Subject,
    User,
)
from ..operations_schemas import (
    AttendanceCorrection,
    AttendanceSave,
    ManualAttendanceRegisterOpen,
)
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/attendance", tags=["attendance"])
ROLES = ("owner", "academic_coordinator", "attendance_operator")
INDIA_TZ = ZoneInfo("Asia/Kolkata")
BATCH_WIDE_STREAM = "__all__"
BATCH_WIDE_SUBJECT = "Attendance"


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _arrival_at(status: str, supplied: datetime | None, existing: AttendanceEntry | None = None):
    """Keep the first recorded arrival separate from later attendance edits."""
    if status not in {"present", "late"}:
        return None
    if supplied:
        return _aware(supplied).astimezone(timezone.utc)
    if existing and existing.arrival_at:
        return existing.arrival_at
    return datetime.now(timezone.utc)


def _entry_arrival(entry: AttendanceEntry | None):
    return _aware(entry.arrival_at) if entry and entry.arrival_at else None


def _arrival_iso(entry: AttendanceEntry | None):
    value = _entry_arrival(entry)
    return value.isoformat() if value else None


def _session_query(db: Session):
    return db.query(ClassSession, Batch, Subject, User, Room, AttendanceRegister).join(Batch, Batch.id == ClassSession.batch_id).join(Subject, Subject.id == ClassSession.subject_id).join(User, User.id == ClassSession.faculty_id).join(Room, Room.id == ClassSession.room_id).outerjoin(AttendanceRegister, AttendanceRegister.class_session_id == ClassSession.id)


def _get_session(db: Session, session_id: str, user: User):
    row = _session_query(db).filter(ClassSession.id == session_id).first()
    if not row:
        raise HTTPException(404, "Class session not found")
    return row


def _eligible_students(db: Session, batch: Batch):
    query = (
        db.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Student.status == "active",
            Enrollment.is_active.is_(True),
            Enrollment.batch == batch.name,
        )
    )
    if batch.program != "All programs":
        query = query.filter(Enrollment.program == batch.program)
    return query.distinct().order_by(Student.full_name).all()


def _eligible_manual_students(
    db: Session,
    batch_name: str,
    stream_name: str,
    subject_name: str,
):
    query = (
        db.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .join(
            StudentAcademicProfile,
            StudentAcademicProfile.student_id == Student.id,
        )
        .filter(
            Student.status == "active",
            Enrollment.is_active.is_(True),
            Enrollment.batch == batch_name,
            StudentAcademicProfile.batch_name == batch_name,
        )
    )
    if stream_name != BATCH_WIDE_STREAM:
        query = (
            query.join(
                StudentSubjectSelection,
                StudentSubjectSelection.student_id == Student.id,
            )
            .filter(
                StudentAcademicProfile.source_stream == stream_name,
                StudentSubjectSelection.subject_name == subject_name,
            )
        )
    return query.distinct().order_by(Student.full_name).all()


def _attendance_catalog(db: Session):
    roster_rows = (
        db.query(
            Student.id,
            StudentAcademicProfile.batch_name,
            StudentAcademicProfile.source_stream,
        )
        .join(
            StudentAcademicProfile,
            StudentAcademicProfile.student_id == Student.id,
        )
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Student.status == "active",
            Enrollment.is_active.is_(True),
            Enrollment.batch == StudentAcademicProfile.batch_name,
            StudentAcademicProfile.source_stream.isnot(None),
        )
        .distinct()
        .all()
    )
    subject_rows = (
        db.query(
            Student.id,
            StudentAcademicProfile.batch_name,
            StudentAcademicProfile.source_stream,
            StudentSubjectSelection.subject_name,
        )
        .join(
            StudentAcademicProfile,
            StudentAcademicProfile.student_id == Student.id,
        )
        .join(Enrollment, Enrollment.student_id == Student.id)
        .join(
            StudentSubjectSelection,
            StudentSubjectSelection.student_id == Student.id,
        )
        .filter(
            Student.status == "active",
            Enrollment.is_active.is_(True),
            Enrollment.batch == StudentAcademicProfile.batch_name,
            StudentAcademicProfile.source_stream.isnot(None),
        )
        .distinct()
        .all()
    )
    group_students = {}
    stream_students = {}
    subject_students = {}
    for student_id, batch_name, stream_name in roster_rows:
        if batch_name not in {"Tatva", "Essential"}:
            continue
        group_students.setdefault(batch_name, set()).add(student_id)
        stream_students.setdefault(
            (batch_name, stream_name),
            set(),
        ).add(student_id)
    for student_id, batch_name, stream_name, subject_name in subject_rows:
        if batch_name not in {"Tatva", "Essential"}:
            continue
        subject_students.setdefault(
            (batch_name, stream_name, subject_name),
            set(),
        ).add(student_id)
    batch_order = {"Tatva": 0, "Essential": 1}
    stream_order = {"JEE": 0, "NEET": 1, "MHT-CET": 2, "Boards": 3}
    groups = []
    for batch_name, students in sorted(
        group_students.items(),
        key=lambda item: (batch_order.get(item[0], 99), item[0]),
    ):
        streams = []
        for (batch, stream_name), stream_roster in sorted(
            stream_students.items(),
            key=lambda item: (
                batch_order.get(item[0][0], 99),
                stream_order.get(item[0][1], 99),
                item[0][1],
            ),
        ):
            if batch != batch_name:
                continue
            subjects = [
                {"name": subject, "studentCount": len(subject_roster)}
                for (
                    subject_batch,
                    subject_stream,
                    subject,
                ), subject_roster in sorted(
                    subject_students.items(),
                    key=lambda item: item[0][2],
                )
                if subject_batch == batch_name and subject_stream == stream_name
            ]
            streams.append({
                "name": stream_name,
                "studentCount": len(stream_roster),
                "subjects": subjects,
            })
        groups.append({
            "name": batch_name,
            "studentCount": len(students),
            "streams": streams,
        })
    return {
        "studentCount": sum(len(students) for students in group_students.values()),
        "groups": groups,
    }


def _session_summary(db: Session, row):
    session, batch, subject, faculty, room, register = row
    student_query = (
        db.query(func.count(func.distinct(Enrollment.student_id)))
        .join(Student, Student.id == Enrollment.student_id)
        .filter(
            Student.status == "active",
            Enrollment.is_active.is_(True),
            Enrollment.batch == batch.name,
        )
    )
    if batch.program != "All programs":
        student_query = student_query.filter(Enrollment.program == batch.program)
    students = student_query.scalar() or 0
    marked = db.query(AttendanceEntry).filter_by(register_id=register.id).count() if register else 0
    return {"id": session.id, "batch": batch.name, "program": batch.program, "subject": subject.name, "faculty": faculty.full_name, "room": room.name, "startsAt": _aware(session.starts_at), "endsAt": _aware(session.ends_at), "status": session.status, "registerStatus": register.status if register else "not_started", "studentCount": students, "markedCount": marked}


def _session_summaries(db: Session, rows):
    if not rows:
        return []
    batch_keys = {(row[1].name, row[1].program) for row in rows}
    batch_names = {name for name, _ in batch_keys}
    programs = {program for _, program in batch_keys}
    student_counts = {
        (batch_name, program): count
        for batch_name, program, count in (
            db.query(
                Enrollment.batch,
                Enrollment.program,
                func.count(func.distinct(Enrollment.student_id)),
            )
            .join(Student, Student.id == Enrollment.student_id)
            .filter(
                Student.status == "active",
                Enrollment.is_active.is_(True),
                Enrollment.batch.in_(batch_names),
                Enrollment.program.in_(programs),
            )
            .group_by(Enrollment.batch, Enrollment.program)
            .all()
        )
    }
    for batch_name, program in batch_keys:
        if program == "All programs":
            student_counts[(batch_name, program)] = (
                db.query(func.count(func.distinct(Enrollment.student_id)))
                .join(Student, Student.id == Enrollment.student_id)
                .filter(
                    Student.status == "active",
                    Enrollment.is_active.is_(True),
                    Enrollment.batch == batch_name,
                )
                .scalar()
                or 0
            )
    register_ids = [row[5].id for row in rows if row[5]]
    marked_counts = {
        register_id: count
        for register_id, count in (
            db.query(AttendanceEntry.register_id, func.count(AttendanceEntry.student_id))
            .filter(AttendanceEntry.register_id.in_(register_ids))
            .group_by(AttendanceEntry.register_id)
            .all()
        )
    } if register_ids else {}
    return [{
        "id": session.id,
        "batch": batch.name,
        "program": batch.program,
        "subject": subject.name,
        "faculty": faculty.full_name,
        "room": room.name,
        "startsAt": _aware(session.starts_at),
        "endsAt": _aware(session.ends_at),
        "status": session.status,
        "registerStatus": register.status if register else "not_started",
        "studentCount": student_counts.get((batch.name, batch.program), 0),
        "markedCount": marked_counts.get(register.id, 0) if register else 0,
    } for session, batch, subject, faculty, room, register in rows]


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    return _session_summaries(
        db,
        _session_query(db).order_by(ClassSession.starts_at.desc()).all(),
    )


@router.get("/bootstrap")
def attendance_portal_bootstrap(
    day: date | None = None,
    db: Session = Depends(get_db),
    operator: User = Depends(require_roles("attendance_operator")),
):
    selected_day = day or datetime.now(INDIA_TZ).date()
    local_start = datetime.combine(selected_day, time.min, tzinfo=INDIA_TZ)
    start = local_start.astimezone(timezone.utc)
    end = (local_start + timedelta(days=1)).astimezone(timezone.utc)
    rows = (
        _session_query(db)
        .filter(ClassSession.starts_at >= start, ClassSession.starts_at < end)
        .order_by(ClassSession.starts_at)
        .all()
    )
    sessions = _session_summaries(db, rows)
    desk_registers = (
        db.query(AttendanceRegister)
        .filter(
            AttendanceRegister.register_kind.in_(("manual", "biometric")),
            AttendanceRegister.attendance_date == selected_day,
        )
        .order_by(AttendanceRegister.batch_name)
        .all()
    )
    for register in desk_registers:
        student_count = len(_eligible_manual_students(
            db,
            register.batch_name,
            register.stream_name,
            register.subject_name,
        ))
        marked_count = db.query(AttendanceEntry).filter_by(register_id=register.id).count()
        sessions.append(_manual_register_summary(register, student_count, marked_count))
    now = datetime.now(timezone.utc)
    pending = [
        item for item in sessions
        if item["registerStatus"] != "submitted"
        and _aware(item["startsAt"]) <= now
        and item["status"] == "scheduled"
    ]
    upcoming = [
        item for item in sessions
        if _aware(item["startsAt"]) > now and item["status"] == "scheduled"
    ]
    submitted = [item for item in sessions if item["registerStatus"] == "submitted"]
    notice_rows = (
        db.query(Notice)
        .filter(Notice.status == "published", Notice.audience == "all")
        .order_by(Notice.published_at.desc(), Notice.created_at.desc())
        .limit(5)
        .all()
    )
    latest_period_end = db.query(func.max(AttendancePeriodSummary.period_end)).filter(
        AttendancePeriodSummary.status == "confirmed",
    ).scalar()
    history = []
    if latest_period_end:
        history = [{
            "batch": batch_name,
            "presentDays": int(present),
            "workingDays": int(working),
            "attendanceRate": round(int(present) / int(working) * 100, 1) if working else None,
            "periodEnd": latest_period_end,
        } for batch_name, present, working in (
            db.query(
                AttendancePeriodSummary.batch_name,
                func.sum(AttendancePeriodSummary.present_days),
                func.sum(AttendancePeriodSummary.working_days),
            )
            .filter(
                AttendancePeriodSummary.period_end == latest_period_end,
                AttendancePeriodSummary.status == "confirmed",
            )
            .group_by(AttendancePeriodSummary.batch_name)
            .order_by(AttendancePeriodSummary.batch_name)
            .all()
        )]
    return {
        "profile": {
            "id": operator.id,
            "fullName": operator.full_name,
            "mobile": operator.mobile,
            "email": operator.email,
            "role": operator.role,
        },
        "selectedDate": selected_day,
        "summary": {
            "scheduled": sum(item["status"] == "scheduled" for item in sessions),
            "pending": len(pending),
            "upcoming": len(upcoming),
            "submitted": len(submitted),
        },
        "sessions": sessions,
        "catalog": _attendance_catalog(db),
        "history": history,
        "notices": [{
            "id": notice.id,
            "title": notice.title,
            "body": notice.body,
            "publishedAt": _aware(notice.published_at or notice.created_at),
        } for notice in notice_rows],
    }


def _manual_register(db: Session, register_id: str):
    register = (
        db.query(AttendanceRegister)
        .filter(
            AttendanceRegister.id == register_id,
            AttendanceRegister.register_kind.in_(("manual", "biometric")),
        )
        .first()
    )
    if not register:
        raise HTTPException(404, "Attendance register not found")
    return register


def _manual_register_summary(
    register: AttendanceRegister,
    student_count: int,
    marked_count: int,
):
    batch_wide = register.stream_name == BATCH_WIDE_STREAM
    starts_at = datetime.combine(
        register.attendance_date,
        time.min,
        tzinfo=INDIA_TZ,
    ).astimezone(timezone.utc)
    return {
        "id": register.id,
        "registerKind": register.register_kind,
        "batch": register.batch_name,
        "stream": "" if batch_wide else register.stream_name,
        "subject": register.subject_name,
        "faculty": "Attendance Desk",
        "room": "Attendance Desk" if batch_wide else register.stream_name,
        "startsAt": starts_at,
        "endsAt": starts_at,
        "status": "scheduled",
        "registerStatus": register.status,
        "studentCount": student_count,
        "markedCount": marked_count,
    }


def _manual_register_payload(db: Session, register: AttendanceRegister):
    students = _eligible_manual_students(
        db,
        register.batch_name,
        register.stream_name,
        register.subject_name,
    )
    entries = {
        item.student_id: item
        for item in db.query(AttendanceEntry)
        .filter_by(register_id=register.id)
        .all()
    }
    return {
        "session": _manual_register_summary(
            register,
            len(students),
            len(entries),
        ),
        "entries": [{
            "studentId": student.id,
            "admissionNumber": student.admission_number,
            "fullName": student.full_name,
            "status": (
                entries[student.id].status
                if student.id in entries
                else ("absent" if register.register_kind == "biometric" else "present")
            ),
            "reason": (
                entries[student.id].reason
                if student.id in entries
                else ""
            ),
            "arrivalAt": _entry_arrival(entries.get(student.id)),
        } for student in students],
    }


@router.post("/manual-registers")
def open_manual_register(
    payload: ManualAttendanceRegisterOpen,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("attendance_operator")),
):
    if payload.date > datetime.now(INDIA_TZ).date():
        raise HTTPException(409, "Attendance cannot be opened for a future date")
    batch_name = payload.batch.strip()
    if batch_name not in {"Tatva", "Essential"}:
        raise HTTPException(422, "Choose either Tatva or Essential")
    stream_name = payload.stream.strip() if payload.stream else BATCH_WIDE_STREAM
    subject_name = payload.subject.strip() if payload.subject else BATCH_WIDE_SUBJECT
    students = _eligible_manual_students(
        db,
        batch_name,
        stream_name,
        subject_name,
    )
    if not students:
        raise HTTPException(404, "No active students match this selection")
    register = (
        db.query(AttendanceRegister)
        .filter_by(
            register_kind="manual",
            attendance_date=payload.date,
            batch_name=batch_name,
            stream_name=stream_name,
            subject_name=subject_name,
        )
        .first()
    )
    if not register:
        register = AttendanceRegister(
            class_session_id=None,
            register_kind="manual",
            attendance_date=payload.date,
            batch_name=batch_name,
            stream_name=stream_name,
            subject_name=subject_name,
            status="draft",
        )
        db.add(register)
        db.flush()
        audit(
            db,
            actor,
            "attendance.manual.open",
            "attendance_register",
            register.id,
            after={
                "date": payload.date.isoformat(),
                "batch": batch_name,
                "stream": stream_name,
                "subject": subject_name,
                "students": len(students),
            },
        )
        db.commit()
    return _manual_register_payload(db, register)


@router.get("/manual-registers/{register_id}")
def manual_attendance_roster(
    register_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ROLES)),
):
    return _manual_register_payload(db, _manual_register(db, register_id))


def _save_manual(
    register_id: str,
    payload: AttendanceSave,
    db: Session,
    actor: User,
    require_complete: bool = False,
):
    register = _manual_register(db, register_id)
    students = _eligible_manual_students(
        db,
        register.batch_name,
        register.stream_name,
        register.subject_name,
    )
    eligible = {student.id for student in students}
    incoming = {item.student_id for item in payload.entries}
    if len(incoming) != len(payload.entries):
        raise HTTPException(422, "A student appears more than once")
    if not incoming.issubset(eligible):
        raise HTTPException(
            409,
            "Attendance contains students outside the selected roster",
        )
    if require_complete and incoming != eligible:
        raise HTTPException(
            409,
            "Every active student must be included before attendance can be submitted",
        )
    if register.status == "submitted":
        raise HTTPException(
            409,
            "Submitted attendance is locked; use an authorised correction",
        )
    existing = {
        item.student_id: item
        for item in db.query(AttendanceEntry)
        .filter_by(register_id=register.id)
        .all()
    }
    for item in payload.entries:
        entry = existing.get(item.student_id)
        if entry:
            entry.status = item.status
            entry.reason = item.reason.strip()
            entry.marked_by = actor.id
            entry.arrival_at = _arrival_at(item.status, item.arrival_at, entry)
        else:
            db.add(AttendanceEntry(
                register_id=register.id,
                student_id=item.student_id,
                status=item.status,
                reason=item.reason.strip(),
                marked_by=actor.id,
                arrival_at=_arrival_at(item.status, item.arrival_at),
            ))
    audit(
        db,
        actor,
        "attendance.manual.draft.save",
        "attendance_register",
        register.id,
        after={"entries": len(payload.entries)},
    )
    db.commit()
    return register


@router.put("/manual-registers/{register_id}")
def save_manual_attendance(
    register_id: str,
    payload: AttendanceSave,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    register = _save_manual(register_id, payload, db, actor)
    return {"id": register.id, "status": register.status}


@router.post("/manual-registers/{register_id}/submit")
def submit_manual_attendance(
    register_id: str,
    payload: AttendanceSave,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    register = _save_manual(
        register_id,
        payload,
        db,
        actor,
        require_complete=True,
    )
    register.status = "submitted"
    register.submitted_at = datetime.now(timezone.utc)
    register.submitted_by = actor.id
    audit(
        db,
        actor,
        "attendance.manual.submit",
        "attendance_register",
        register.id,
        after={"status": "submitted"},
    )
    db.commit()
    return {
        "id": register.id,
        "status": register.status,
        "submittedAt": register.submitted_at,
    }


@router.post("/manual-registers/{register_id}/corrections/{student_id}")
def correct_manual_attendance(
    register_id: str,
    student_id: str,
    payload: AttendanceCorrection,
    db: Session = Depends(get_db),
    actor: User = Depends(
        require_roles("owner", "academic_coordinator"),
    ),
):
    register = _manual_register(db, register_id)
    if register.status != "submitted":
        raise HTTPException(409, "Only submitted attendance can be corrected")
    entry = (
        db.query(AttendanceEntry)
        .filter_by(register_id=register.id, student_id=student_id)
        .first()
    )
    if not entry:
        raise HTTPException(404, "Attendance entry not found")
    before = {"status": entry.status, "reason": entry.reason, "arrivalAt": _arrival_iso(entry)}
    entry.status = payload.status
    entry.reason = payload.reason.strip()
    entry.marked_by = actor.id
    entry.arrival_at = _arrival_at(payload.status, None, entry)
    audit(
        db,
        actor,
        "attendance.manual.correction",
        "attendance_entry",
        f"{register.id}:{student_id}",
        before=before,
        after={"status": entry.status, "reason": entry.reason, "arrivalAt": _arrival_iso(entry)},
    )
    db.commit()
    return {
        "studentId": student_id,
        "status": entry.status,
        "reason": entry.reason,
        "arrivalAt": _entry_arrival(entry),
    }


@router.get("/sessions/{session_id}")
def attendance_roster(session_id: str, db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    row = _get_session(db, session_id, user)
    session, batch, subject, faculty, room, register = row
    students = _eligible_students(db, batch)
    entries = {item.student_id: item for item in db.query(AttendanceEntry).filter_by(register_id=register.id).all()} if register else {}
    return {"session": _session_summary(db, row), "entries": [{"studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "status": entries[student.id].status if student.id in entries else "present", "reason": entries[student.id].reason if student.id in entries else "", "arrivalAt": _entry_arrival(entries.get(student.id))} for student in students]}


def _save(
    session_id: str,
    payload: AttendanceSave,
    db: Session,
    actor: User,
    require_complete: bool = False,
):
    row = _get_session(db, session_id, actor)
    session, batch, _, _, _, register = row
    eligible = {student.id for student in _eligible_students(db, batch)}
    incoming = {item.student_id for item in payload.entries}
    if len(incoming) != len(payload.entries):
        raise HTTPException(422, "A student appears more than once")
    if not incoming.issubset(eligible):
        raise HTTPException(409, "Attendance contains students who are not actively enrolled in this batch")
    if require_complete and incoming != eligible:
        raise HTTPException(409, "Every active student must be included before attendance can be submitted")
    if register and register.status == "submitted":
        raise HTTPException(409, "Submitted attendance is locked; use a correction with a reason")
    if not register:
        register = AttendanceRegister(class_session_id=session.id, status="draft")
        db.add(register); db.flush()
    existing = {item.student_id: item for item in db.query(AttendanceEntry).filter_by(register_id=register.id).all()}
    for item in payload.entries:
        entry = existing.get(item.student_id)
        if entry:
            entry.status, entry.reason, entry.marked_by = item.status, item.reason.strip(), actor.id
            entry.arrival_at = _arrival_at(item.status, item.arrival_at, entry)
        else:
            db.add(AttendanceEntry(register_id=register.id, student_id=item.student_id, status=item.status, reason=item.reason.strip(), marked_by=actor.id, arrival_at=_arrival_at(item.status, item.arrival_at)))
    audit(db, actor, "attendance.draft.save", "attendance_register", register.id, after={"session_id": session.id, "entries": len(payload.entries)})
    db.commit()
    return register


@router.put("/sessions/{session_id}")
def save_attendance(session_id: str, payload: AttendanceSave, db: Session = Depends(get_db), actor: User = Depends(require_roles(*ROLES))):
    register = _save(session_id, payload, db, actor)
    return {"id": register.id, "status": register.status}


@router.post("/sessions/{session_id}/submit")
def submit_attendance(session_id: str, payload: AttendanceSave, db: Session = Depends(get_db), actor: User = Depends(require_roles(*ROLES))):
    row = _get_session(db, session_id, actor)
    session = row[0]
    if session.status != "scheduled":
        raise HTTPException(409, "Attendance can be submitted only for a scheduled class")
    if _aware(session.starts_at) > datetime.now(timezone.utc):
        raise HTTPException(409, "Attendance can be submitted only after the class begins")
    register = _save(session_id, payload, db, actor, require_complete=True)
    register.status = "submitted"; register.submitted_at = datetime.now(timezone.utc); register.submitted_by = actor.id
    audit(db, actor, "attendance.submit", "attendance_register", register.id, after={"session_id": session_id, "status": "submitted"})
    db.commit()
    return {"id": register.id, "status": register.status, "submittedAt": register.submitted_at}


@router.post("/sessions/{session_id}/corrections/{student_id}")
def correct_attendance(session_id: str, student_id: str, payload: AttendanceCorrection, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner", "academic_coordinator"))):
    row = _get_session(db, session_id, actor)
    register = row[5]
    if not register or register.status != "submitted":
        raise HTTPException(409, "Only submitted attendance can be corrected")
    entry = db.query(AttendanceEntry).filter_by(register_id=register.id, student_id=student_id).first()
    if not entry:
        raise HTTPException(404, "Attendance entry not found")
    before = {"status": entry.status, "reason": entry.reason, "arrivalAt": _arrival_iso(entry)}
    entry.status, entry.reason, entry.marked_by = payload.status, payload.reason.strip(), actor.id
    entry.arrival_at = _arrival_at(payload.status, None, entry)
    audit(db, actor, "attendance.correction", "attendance_entry", f"{register.id}:{student_id}", before=before, after={"status": entry.status, "reason": entry.reason, "arrivalAt": _arrival_iso(entry)})
    db.commit()
    return {"studentId": student_id, "status": entry.status, "reason": entry.reason, "arrivalAt": _entry_arrival(entry)}
