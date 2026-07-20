from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Batch, ClassSession, Room, Subject, User
from ..operations_schemas import ClassSessionCreate
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/timetable", tags=["timetable"])
READ_ROLES = ("owner", "academic_coordinator", "faculty", "front_desk")


def _serialize(row, batch, subject, faculty, room):
    return {"id": row.id, "batchId": batch.id, "batch": batch.name, "program": batch.program, "subjectId": subject.id, "subject": subject.name, "facultyId": faculty.id, "faculty": faculty.full_name, "roomId": room.id, "room": room.name, "startsAt": row.starts_at, "endsAt": row.ends_at, "status": row.status, "notes": row.notes, "overrideReason": row.override_reason}


def _query(db: Session):
    return db.query(ClassSession, Batch, Subject, User, Room).join(Batch, Batch.id == ClassSession.batch_id).join(Subject, Subject.id == ClassSession.subject_id).join(User, User.id == ClassSession.faculty_id).join(Room, Room.id == ClassSession.room_id)


@router.get("/bootstrap")
def bootstrap(db: Session = Depends(get_db), user: User = Depends(require_roles(*READ_ROLES))):
    query = _query(db)
    if user.role == "faculty": query = query.filter(ClassSession.faculty_id == user.id)
    rows = query.order_by(ClassSession.starts_at).all()
    return {
        "sessions": [_serialize(*row) for row in rows],
        "batches": [{"id": item.id, "name": item.name, "program": item.program} for item in db.query(Batch).filter_by(is_active=True).order_by(Batch.name).all()],
        "subjects": [{"id": item.id, "name": item.name, "code": item.code, "program": item.program} for item in db.query(Subject).filter_by(is_active=True).order_by(Subject.name).all()],
        "rooms": [{"id": item.id, "name": item.name, "capacity": item.capacity} for item in db.query(Room).filter_by(is_active=True).order_by(Room.name).all()],
        "faculty": [{"id": item.id, "fullName": item.full_name} for item in db.query(User).filter(User.is_active.is_(True), User.role.in_(("faculty", "academic_coordinator"))).order_by(User.full_name).all()],
    }


@router.post("/sessions", status_code=201)
def create_session(payload: ClassSessionCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner", "academic_coordinator"))):
    batch, subject, faculty, room = db.get(Batch, payload.batch_id), db.get(Subject, payload.subject_id), db.get(User, payload.faculty_id), db.get(Room, payload.room_id)
    if not all((batch, subject, faculty, room)):
        raise HTTPException(404, "One or more timetable resources were not found")
    if not batch.is_active or not subject.is_active or not room.is_active or not faculty.is_active or faculty.role not in ("faculty", "academic_coordinator"):
        raise HTTPException(409, "Timetable resources must be active and the assigned user must be faculty")
    conflicts = _query(db).filter(ClassSession.status == "scheduled", ClassSession.starts_at < payload.ends_at, ClassSession.ends_at > payload.starts_at, or_(ClassSession.faculty_id == payload.faculty_id, ClassSession.room_id == payload.room_id, ClassSession.batch_id == payload.batch_id)).all()
    if conflicts and not payload.allow_override:
        raise HTTPException(409, detail={"code": "SCHEDULE_CONFLICT", "message": "The faculty, room, or batch is already scheduled in this time window", "conflicts": jsonable_encoder([_serialize(*row) for row in conflicts])})
    row = ClassSession(batch_id=batch.id, subject_id=subject.id, faculty_id=faculty.id, room_id=room.id, starts_at=payload.starts_at, ends_at=payload.ends_at, notes=payload.notes.strip(), override_reason=(payload.override_reason or "").strip() or None, created_by=actor.id)
    db.add(row); db.flush()
    audit(db, actor, "timetable.session.create", "class_session", row.id, after={"batch_id": batch.id, "subject_id": subject.id, "faculty_id": faculty.id, "room_id": room.id, "starts_at": payload.starts_at.isoformat(), "ends_at": payload.ends_at.isoformat(), "overridden": bool(conflicts)})
    db.commit()
    return _serialize(row, batch, subject, faculty, room)
