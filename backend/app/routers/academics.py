from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Assignment, AssignmentRecipient, Batch, ClassSession, Enrollment, Subject, User
from ..operations_schemas import AssignmentCreate
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/academics", tags=["academics"])
ROLES = ("owner", "academic_coordinator", "faculty")


def _assignments(db: Session):
    counts = db.query(AssignmentRecipient.assignment_id, func.count(AssignmentRecipient.student_id).label("recipients")).group_by(AssignmentRecipient.assignment_id).subquery()
    return db.query(Assignment, Batch, Subject, func.coalesce(counts.c.recipients, 0)).join(Batch, Batch.id == Assignment.batch_id).join(Subject, Subject.id == Assignment.subject_id).outerjoin(counts, counts.c.assignment_id == Assignment.id)


def _serialize(row, batch, subject, recipients):
    return {"id": row.id, "title": row.title, "instructions": row.instructions, "batchId": batch.id, "batch": batch.name, "subjectId": subject.id, "subject": subject.name, "dueAt": row.due_at, "externalUrl": row.external_url, "status": row.status, "recipientCount": recipients, "createdAt": row.created_at}


@router.get("/assignments")
def list_assignments(db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    query = _assignments(db)
    if user.role == "faculty": query = query.filter(Assignment.created_by == user.id)
    return [_serialize(*row) for row in query.order_by(Assignment.due_at.desc()).all()]


@router.post("/assignments", status_code=201)
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles(*ROLES))):
    batch, subject = db.get(Batch, payload.batch_id), db.get(Subject, payload.subject_id)
    if not batch or not subject:
        raise HTTPException(404, "Batch or subject not found")
    if actor.role == "faculty" and not db.query(ClassSession).filter_by(batch_id=batch.id, subject_id=subject.id, faculty_id=actor.id).first():
        raise HTTPException(403, "Faculty can publish only to batches and subjects assigned in the timetable")
    eligible = db.query(Enrollment.student_id).filter(Enrollment.is_active.is_(True), Enrollment.batch == batch.name).distinct().all()
    if not eligible:
        raise HTTPException(409, "This batch has no active enrolled students")
    row = Assignment(batch_id=batch.id, subject_id=subject.id, title=payload.title.strip(), instructions=payload.instructions.strip(), due_at=payload.due_at, external_url=str(payload.external_url), status=payload.status, created_by=actor.id)
    db.add(row); db.flush()
    db.add_all([AssignmentRecipient(assignment_id=row.id, student_id=student_id, status=payload.status) for (student_id,) in eligible])
    audit(db, actor, "academics.assignment.create", "assignment", row.id, after={"batch_id": batch.id, "subject_id": subject.id, "recipients": len(eligible), "status": payload.status})
    db.commit()
    return _serialize(row, batch, subject, len(eligible))
