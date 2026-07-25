from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AttendanceEntry, AttendanceRegister, Batch, ClassSession, Enrollment, Room, Student, Subject, User
from ..operations_schemas import AttendanceCorrection, AttendanceSave
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/attendance", tags=["attendance"])
ROLES = ("owner", "academic_coordinator", "attendance_operator")
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _session_query(db: Session):
    return db.query(ClassSession, Batch, Subject, User, Room, AttendanceRegister).join(Batch, Batch.id == ClassSession.batch_id).join(Subject, Subject.id == ClassSession.subject_id).join(User, User.id == ClassSession.faculty_id).join(Room, Room.id == ClassSession.room_id).outerjoin(AttendanceRegister, AttendanceRegister.class_session_id == ClassSession.id)


def _get_session(db: Session, session_id: str, user: User):
    row = _session_query(db).filter(ClassSession.id == session_id).first()
    if not row:
        raise HTTPException(404, "Class session not found")
    return row


def _eligible_students(db: Session, batch: Batch):
    return db.query(Student).join(Enrollment, Enrollment.student_id == Student.id).filter(Enrollment.is_active.is_(True), Enrollment.batch == batch.name).order_by(Student.full_name).all()


def _session_summary(db: Session, row):
    session, batch, subject, faculty, room, register = row
    students = db.query(func.count(func.distinct(Enrollment.student_id))).filter(Enrollment.is_active.is_(True), Enrollment.batch == batch.name).scalar() or 0
    marked = db.query(AttendanceEntry).filter_by(register_id=register.id).count() if register else 0
    return {"id": session.id, "batch": batch.name, "subject": subject.name, "faculty": faculty.full_name, "room": room.name, "startsAt": _aware(session.starts_at), "endsAt": _aware(session.ends_at), "status": session.status, "registerStatus": register.status if register else "not_started", "studentCount": students, "markedCount": marked}


def _session_summaries(db: Session, rows):
    if not rows:
        return []
    batch_names = {row[1].name for row in rows}
    student_counts = {
        batch_name: count
        for batch_name, count in (
            db.query(Enrollment.batch, func.count(func.distinct(Enrollment.student_id)))
            .filter(
                Enrollment.is_active.is_(True),
                Enrollment.batch.in_(batch_names),
            )
            .group_by(Enrollment.batch)
            .all()
        )
    }
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
        "subject": subject.name,
        "faculty": faculty.full_name,
        "room": room.name,
        "startsAt": _aware(session.starts_at),
        "endsAt": _aware(session.ends_at),
        "status": session.status,
        "registerStatus": register.status if register else "not_started",
        "studentCount": student_counts.get(batch.name, 0),
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
    }


@router.get("/sessions/{session_id}")
def attendance_roster(session_id: str, db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    row = _get_session(db, session_id, user)
    session, batch, subject, faculty, room, register = row
    students = _eligible_students(db, batch)
    entries = {item.student_id: item for item in db.query(AttendanceEntry).filter_by(register_id=register.id).all()} if register else {}
    return {"session": _session_summary(db, row), "entries": [{"studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "status": entries[student.id].status if student.id in entries else "present", "reason": entries[student.id].reason if student.id in entries else ""} for student in students]}


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
        else:
            db.add(AttendanceEntry(register_id=register.id, student_id=item.student_id, status=item.status, reason=item.reason.strip(), marked_by=actor.id))
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
    before = {"status": entry.status, "reason": entry.reason}
    entry.status, entry.reason, entry.marked_by = payload.status, payload.reason.strip(), actor.id
    audit(db, actor, "attendance.correction", "attendance_entry", f"{register.id}:{student_id}", before=before, after={"status": entry.status, "reason": entry.reason})
    db.commit()
    return {"studentId": student_id, "status": entry.status, "reason": entry.reason}
