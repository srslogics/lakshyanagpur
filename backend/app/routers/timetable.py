from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Batch,
    ClassSession,
    FacultyTeachingAssignment,
    Room,
    Subject,
    User,
)
from ..operations_schemas import (
    ClassSessionCreate,
    ClassSessionUpdate,
    FacultyTeachingAssignmentCreate,
    FacultyTeachingAssignmentUpdate,
)
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/timetable", tags=["timetable"])
READ_ROLES = ("owner", "academic_coordinator", "faculty", "front_desk")


def _serialize(row, batch, subject, faculty, room):
    return {"id": row.id, "batchId": batch.id, "batch": batch.name, "program": batch.program, "subjectId": subject.id, "subject": subject.name, "facultyId": faculty.id, "faculty": faculty.full_name, "roomId": room.id, "room": room.name, "startsAt": row.starts_at, "endsAt": row.ends_at, "status": row.status, "notes": row.notes, "overrideReason": row.override_reason}


def _query(db: Session):
    return db.query(ClassSession, Batch, Subject, User, Room).join(Batch, Batch.id == ClassSession.batch_id).join(Subject, Subject.id == ClassSession.subject_id).join(User, User.id == ClassSession.faculty_id).join(Room, Room.id == ClassSession.room_id)


def _teaching_assignment_query(db: Session):
    return (
        db.query(FacultyTeachingAssignment, Batch, Subject, User)
        .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
        .join(Subject, Subject.id == FacultyTeachingAssignment.subject_id)
        .join(User, User.id == FacultyTeachingAssignment.faculty_id)
    )


def _teaching_assignment_counts(db: Session):
    return {
        (faculty_id, batch_id, subject_id): count
        for faculty_id, batch_id, subject_id, count in (
            db.query(
                ClassSession.faculty_id,
                ClassSession.batch_id,
                ClassSession.subject_id,
                func.count(ClassSession.id),
            )
            .group_by(
                ClassSession.faculty_id,
                ClassSession.batch_id,
                ClassSession.subject_id,
            )
            .all()
        )
    }


def _serialize_teaching_assignment(row, batch, subject, faculty, session_count=0):
    return {
        "id": row.id,
        "facultyId": faculty.id,
        "faculty": faculty.full_name,
        "batchId": batch.id,
        "batch": batch.name,
        "program": batch.program,
        "subjectId": subject.id,
        "subject": subject.name,
        "subjectCode": subject.code,
        "isActive": row.is_active,
        "sessionCount": session_count,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
    }


def _validate_teaching_resources(
    db: Session,
    faculty_id,
    batch_id,
    subject_id,
    require_active=True,
):
    faculty = db.get(User, faculty_id)
    batch = db.get(Batch, batch_id)
    subject = db.get(Subject, subject_id)
    if not faculty or not batch or not subject:
        raise HTTPException(404, "Faculty, batch, or subject not found")
    if require_active and (
        not faculty.is_active
        or faculty.role not in ("faculty", "academic_coordinator")
        or not batch.is_active
        or not subject.is_active
    ):
        raise HTTPException(409, "Faculty, batch, and subject must be active")
    return faculty, batch, subject


def _ensure_teaching_assignment(
    db: Session,
    faculty_id: str,
    batch_id: str,
    subject_id: str,
    created_by: str,
):
    row = (
        db.query(FacultyTeachingAssignment)
        .filter_by(
            faculty_id=faculty_id,
            batch_id=batch_id,
            subject_id=subject_id,
        )
        .first()
    )
    if row:
        restored = not row.is_active
        row.is_active = True
        return row, "restored" if restored else None
    row = FacultyTeachingAssignment(
        faculty_id=faculty_id,
        batch_id=batch_id,
        subject_id=subject_id,
        created_by=created_by,
    )
    db.add(row)
    db.flush()
    return row, "created"


@router.get("/bootstrap")
def bootstrap(db: Session = Depends(get_db), user: User = Depends(require_roles(*READ_ROLES))):
    query = _query(db)
    if user.role == "faculty": query = query.filter(ClassSession.faculty_id == user.id)
    rows = query.order_by(ClassSession.starts_at).all()
    assignment_query = _teaching_assignment_query(db)
    if user.role == "faculty":
        assignment_query = assignment_query.filter(
            FacultyTeachingAssignment.faculty_id == user.id,
            FacultyTeachingAssignment.is_active.is_(True),
        )
    assignment_rows = assignment_query.order_by(
        User.full_name,
        Batch.name,
        Subject.name,
    ).all()
    session_counts = _teaching_assignment_counts(db)
    return {
        "sessions": [_serialize(*row) for row in rows],
        "teachingAssignments": [
            _serialize_teaching_assignment(
                *row,
                session_counts.get((row[0].faculty_id, row[0].batch_id, row[0].subject_id), 0),
            )
            for row in assignment_rows
        ],
        "batches": [{"id": item.id, "name": item.name, "program": item.program} for item in db.query(Batch).filter_by(is_active=True).order_by(Batch.name).all()],
        "subjects": [{"id": item.id, "name": item.name, "code": item.code, "program": item.program} for item in db.query(Subject).filter_by(is_active=True).order_by(Subject.name).all()],
        "rooms": [{"id": item.id, "name": item.name, "capacity": item.capacity} for item in db.query(Room).filter_by(is_active=True).order_by(Room.name).all()],
        "faculty": [{"id": item.id, "fullName": item.full_name} for item in db.query(User).filter(User.is_active.is_(True), User.role.in_(("faculty", "academic_coordinator"))).order_by(User.full_name).all()],
    }


@router.post("/teaching-assignments", status_code=201)
def create_teaching_assignment(
    payload: FacultyTeachingAssignmentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner", "academic_coordinator")),
):
    faculty, batch, subject = _validate_teaching_resources(
        db,
        payload.faculty_id,
        payload.batch_id,
        payload.subject_id,
    )
    existing = (
        db.query(FacultyTeachingAssignment)
        .filter_by(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=subject.id,
        )
        .first()
    )
    if existing and existing.is_active:
        raise HTTPException(409, "This teaching assignment already exists")
    row, change = _ensure_teaching_assignment(
        db,
        faculty.id,
        batch.id,
        subject.id,
        actor.id,
    )
    audit(
        db,
        actor,
        f"timetable.teaching_assignment.{change}",
        "faculty_teaching_assignment",
        row.id,
        after={
            "faculty_id": faculty.id,
            "batch_id": batch.id,
            "subject_id": subject.id,
            "is_active": True,
        },
    )
    db.commit()
    return _serialize_teaching_assignment(row, batch, subject, faculty)


@router.patch("/teaching-assignments/{assignment_id}")
def update_teaching_assignment(
    assignment_id: str,
    payload: FacultyTeachingAssignmentUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner")),
):
    row = db.get(FacultyTeachingAssignment, assignment_id)
    if not row:
        raise HTTPException(404, "Teaching assignment not found")
    faculty, batch, subject = _validate_teaching_resources(
        db,
        payload.faculty_id,
        payload.batch_id,
        payload.subject_id,
        require_active=payload.is_active,
    )
    duplicate = (
        db.query(FacultyTeachingAssignment)
        .filter(
            FacultyTeachingAssignment.id != row.id,
            FacultyTeachingAssignment.faculty_id == faculty.id,
            FacultyTeachingAssignment.batch_id == batch.id,
            FacultyTeachingAssignment.subject_id == subject.id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(409, "This teaching assignment already exists")
    before = {
        "faculty_id": row.faculty_id,
        "batch_id": row.batch_id,
        "subject_id": row.subject_id,
        "is_active": row.is_active,
    }
    row.faculty_id = faculty.id
    row.batch_id = batch.id
    row.subject_id = subject.id
    row.is_active = payload.is_active
    audit(
        db,
        actor,
        "timetable.teaching_assignment.update",
        "faculty_teaching_assignment",
        row.id,
        before=before,
        after=payload.model_dump(by_alias=True, mode="json"),
    )
    db.commit()
    session_count = (
        db.query(func.count(ClassSession.id))
        .filter_by(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=subject.id,
        )
        .scalar()
        or 0
    )
    return _serialize_teaching_assignment(
        row,
        batch,
        subject,
        faculty,
        session_count,
    )


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
    teaching_assignment, teaching_assignment_change = _ensure_teaching_assignment(
        db,
        faculty.id,
        batch.id,
        subject.id,
        actor.id,
    )
    audit(db, actor, "timetable.session.create", "class_session", row.id, after={"batch_id": batch.id, "subject_id": subject.id, "faculty_id": faculty.id, "room_id": room.id, "starts_at": payload.starts_at.isoformat(), "ends_at": payload.ends_at.isoformat(), "overridden": bool(conflicts)})
    if teaching_assignment_change:
        audit(
            db,
            actor,
            f"timetable.teaching_assignment.{teaching_assignment_change}",
            "faculty_teaching_assignment",
            teaching_assignment.id,
            after={
                "faculty_id": faculty.id,
                "batch_id": batch.id,
                "subject_id": subject.id,
                "is_active": True,
                "source": "class_session",
            },
        )
    db.commit()
    return _serialize(row, batch, subject, faculty, room)


@router.patch("/sessions/{session_id}")
def update_session(session_id: str, payload: ClassSessionUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(ClassSession, session_id)
    if not row:
        raise HTTPException(404, "Class session not found")
    batch, subject, faculty, room = db.get(Batch, payload.batch_id), db.get(Subject, payload.subject_id), db.get(User, payload.faculty_id), db.get(Room, payload.room_id)
    if not all((batch, subject, faculty, room)):
        raise HTTPException(404, "One or more timetable resources were not found")
    if not batch.is_active or not subject.is_active or not room.is_active or not faculty.is_active or faculty.role not in ("faculty", "academic_coordinator"):
        raise HTTPException(409, "Timetable resources must be active and the assigned user must be faculty")
    conflicts = _query(db).filter(
        ClassSession.id != row.id,
        ClassSession.status == "scheduled",
        ClassSession.starts_at < payload.ends_at,
        ClassSession.ends_at > payload.starts_at,
        or_(ClassSession.faculty_id == payload.faculty_id, ClassSession.room_id == payload.room_id, ClassSession.batch_id == payload.batch_id),
    ).all()
    if conflicts and not payload.allow_override:
        raise HTTPException(409, detail={"code": "SCHEDULE_CONFLICT", "message": "The faculty, room, or batch is already scheduled in this time window", "conflicts": jsonable_encoder([_serialize(*item) for item in conflicts])})
    before = _serialize(row, db.get(Batch, row.batch_id), db.get(Subject, row.subject_id), db.get(User, row.faculty_id), db.get(Room, row.room_id))
    row.batch_id = batch.id
    row.subject_id = subject.id
    row.faculty_id = faculty.id
    row.room_id = room.id
    row.starts_at = payload.starts_at
    row.ends_at = payload.ends_at
    row.notes = payload.notes.strip()
    row.status = payload.status
    row.override_reason = (payload.override_reason or "").strip() or None
    teaching_assignment, teaching_assignment_change = _ensure_teaching_assignment(
        db,
        faculty.id,
        batch.id,
        subject.id,
        actor.id,
    )
    audit(db, actor, "timetable.session.update", "class_session", row.id, before=jsonable_encoder(before), after=payload.model_dump(by_alias=True, mode="json"))
    if teaching_assignment_change:
        audit(
            db,
            actor,
            f"timetable.teaching_assignment.{teaching_assignment_change}",
            "faculty_teaching_assignment",
            teaching_assignment.id,
            after={
                "faculty_id": faculty.id,
                "batch_id": batch.id,
                "subject_id": subject.id,
                "is_active": True,
                "source": "class_session",
            },
        )
    db.commit()
    return _serialize(row, batch, subject, faculty, room)
