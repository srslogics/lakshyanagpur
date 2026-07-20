from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AttendanceEntry, AttendanceRegister, Batch, ClassSession, Enrollment, Room, Student, Subject, User
from ..operations_schemas import AttendanceCorrection, AttendanceSave
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/attendance", tags=["attendance"])
ROLES = ("owner", "academic_coordinator", "faculty")


def _session_query(db: Session):
    return db.query(ClassSession, Batch, Subject, User, Room, AttendanceRegister).join(Batch, Batch.id == ClassSession.batch_id).join(Subject, Subject.id == ClassSession.subject_id).join(User, User.id == ClassSession.faculty_id).join(Room, Room.id == ClassSession.room_id).outerjoin(AttendanceRegister, AttendanceRegister.class_session_id == ClassSession.id)


def _get_session(db: Session, session_id: str, user: User):
    row = _session_query(db).filter(ClassSession.id == session_id).first()
    if not row:
        raise HTTPException(404, "Class session not found")
    if user.role == "faculty" and row[0].faculty_id != user.id:
        raise HTTPException(403, "Faculty can access only their own classes")
    return row


def _eligible_students(db: Session, batch: Batch):
    return db.query(Student).join(Enrollment, Enrollment.student_id == Student.id).filter(Enrollment.is_active.is_(True), Enrollment.batch == batch.name).order_by(Student.full_name).all()


def _session_summary(db: Session, row):
    session, batch, subject, faculty, room, register = row
    students = db.query(func.count(func.distinct(Enrollment.student_id))).filter(Enrollment.is_active.is_(True), Enrollment.batch == batch.name).scalar() or 0
    marked = db.query(AttendanceEntry).filter_by(register_id=register.id).count() if register else 0
    return {"id": session.id, "batch": batch.name, "subject": subject.name, "faculty": faculty.full_name, "room": room.name, "startsAt": session.starts_at, "endsAt": session.ends_at, "registerStatus": register.status if register else "not_started", "studentCount": students, "markedCount": marked}


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    query = _session_query(db)
    if user.role == "faculty": query = query.filter(ClassSession.faculty_id == user.id)
    return [_session_summary(db, row) for row in query.order_by(ClassSession.starts_at.desc()).all()]


@router.get("/sessions/{session_id}")
def attendance_roster(session_id: str, db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    row = _get_session(db, session_id, user)
    session, batch, subject, faculty, room, register = row
    students = _eligible_students(db, batch)
    entries = {item.student_id: item for item in db.query(AttendanceEntry).filter_by(register_id=register.id).all()} if register else {}
    return {"session": _session_summary(db, row), "entries": [{"studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "status": entries[student.id].status if student.id in entries else "present", "reason": entries[student.id].reason if student.id in entries else ""} for student in students]}


def _save(session_id: str, payload: AttendanceSave, db: Session, actor: User):
    row = _get_session(db, session_id, actor)
    session, batch, _, _, _, register = row
    eligible = {student.id for student in _eligible_students(db, batch)}
    incoming = {item.student_id for item in payload.entries}
    if len(incoming) != len(payload.entries):
        raise HTTPException(422, "A student appears more than once")
    if not incoming.issubset(eligible):
        raise HTTPException(409, "Attendance contains students who are not actively enrolled in this batch")
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
    register = _save(session_id, payload, db, actor)
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
