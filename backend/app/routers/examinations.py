from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Batch,
    Enrollment,
    Examination,
    ExaminationParticipant,
    ExaminationResult,
    FacultyTeachingAssignment,
    Student,
    Subject,
    User,
)
from ..operations_schemas import ExaminationCreate, ExaminationMarksSave, ExaminationUpdate
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/examinations", tags=["examinations"])
ROLES = ("owner", "academic_coordinator", "faculty")


def _can_manage(actor: User, exam: Examination) -> bool:
    return actor.role in ("owner", "academic_coordinator") or exam.faculty_id == actor.id


def _active_roster(db: Session, batch: Batch):
    return (
        db.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Enrollment.is_active.is_(True),
            Enrollment.batch == batch.name,
            Enrollment.program == batch.program,
            Student.status == "active",
        )
        .order_by(Student.full_name)
        .all()
    )


def _snapshot_roster(
    db: Session,
    exam: Examination,
    students: list[Student],
):
    for student in students:
        db.add(
            ExaminationParticipant(
                exam_id=exam.id,
                student_id=student.id,
                admission_number=student.admission_number,
                full_name=student.full_name,
            )
        )


def _exam_roster(db: Session, exam: Examination):
    return (
        db.query(ExaminationParticipant)
        .filter_by(exam_id=exam.id)
        .order_by(ExaminationParticipant.full_name)
        .all()
    )


def _exam_rows(db: Session, actor: User):
    query = (
        db.query(Examination, Batch, Subject, User)
        .join(Batch, Batch.id == Examination.batch_id)
        .join(Subject, Subject.id == Examination.subject_id)
        .join(User, User.id == Examination.faculty_id)
    )
    if actor.role == "faculty":
        query = query.filter(Examination.faculty_id == actor.id)
    return query.order_by(Examination.scheduled_at.desc()).all()


def _result_stats(db: Session, exam_ids: list[str]):
    if not exam_ids:
        return {}
    rows = (
        db.query(
            ExaminationResult.exam_id,
            func.count(ExaminationResult.student_id),
            func.avg(ExaminationResult.marks_obtained),
            func.max(ExaminationResult.marks_obtained),
        )
        .filter(
            ExaminationResult.exam_id.in_(exam_ids),
            ExaminationResult.result_status != "pending",
        )
        .group_by(ExaminationResult.exam_id)
        .all()
    )
    return {
        exam_id: {
            "entered": count,
            "average": float(average) if average is not None else None,
            "highest": float(highest) if highest is not None else None,
        }
        for exam_id, count, average, highest in rows
    }


def _serialize(exam, batch, subject, faculty, participant_count, stats):
    return {
        "id": exam.id,
        "name": exam.name,
        "batchId": batch.id,
        "batch": batch.name,
        "program": batch.program,
        "subjectId": subject.id,
        "subject": subject.name,
        "subjectCode": subject.code,
        "facultyId": faculty.id,
        "faculty": faculty.full_name,
        "scheduledAt": exam.scheduled_at,
        "durationMinutes": exam.duration_minutes,
        "maxMarks": float(exam.max_marks),
        "passMarks": float(exam.pass_marks),
        "instructions": exam.instructions,
        "status": exam.status,
        "publishedAt": exam.published_at,
        "participantCount": participant_count,
        "marksEntered": stats.get("entered", 0),
        "averageMarks": stats.get("average"),
        "highestMarks": stats.get("highest"),
    }


def _serialize_many(db: Session, rows):
    exam_ids = [exam.id for exam, *_ in rows]
    stats = _result_stats(db, exam_ids)
    roster_counts = dict(
        db.query(
            ExaminationParticipant.exam_id,
            func.count(ExaminationParticipant.student_id),
        )
        .filter(ExaminationParticipant.exam_id.in_(exam_ids))
        .group_by(ExaminationParticipant.exam_id)
        .all()
    ) if exam_ids else {}
    payload = []
    for exam, batch, subject, faculty in rows:
        payload.append(
            _serialize(
                exam,
                batch,
                subject,
                faculty,
                roster_counts.get(exam.id, 0),
                stats.get(exam.id, {}),
            )
        )
    return payload


def _get_exam_row(db: Session, exam_id: str):
    row = (
        db.query(Examination, Batch, Subject, User)
        .join(Batch, Batch.id == Examination.batch_id)
        .join(Subject, Subject.id == Examination.subject_id)
        .join(User, User.id == Examination.faculty_id)
        .filter(Examination.id == exam_id)
        .first()
    )
    if not row:
        raise HTTPException(404, "Examination not found")
    return row


def _validate_references(db: Session, payload, actor: User):
    batch = db.get(Batch, payload.batch_id)
    subject = db.get(Subject, payload.subject_id)
    faculty = db.get(User, payload.faculty_id)
    if not batch or not subject or not faculty or faculty.role != "faculty":
        raise HTTPException(404, "Batch, subject, or faculty not found")
    if actor.role == "faculty":
        if faculty.id != actor.id:
            raise HTTPException(403, "Faculty can schedule only their own examinations")
        assigned = db.query(FacultyTeachingAssignment).filter_by(
            batch_id=batch.id,
            subject_id=subject.id,
            faculty_id=actor.id,
            is_active=True,
        ).first()
        if not assigned:
            raise HTTPException(
                403,
                "Faculty can schedule examinations only for assigned batches and subjects",
            )
    if not _active_roster(db, batch):
        raise HTTPException(409, "This batch has no active enrolled students")
    return batch, subject, faculty


@router.get("")
def list_examinations(
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    return _serialize_many(db, _exam_rows(db, actor))


@router.post("", status_code=201)
def create_examination(
    payload: ExaminationCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    batch, subject, faculty = _validate_references(db, payload, actor)
    exam = Examination(
        name=payload.name.strip(),
        batch_id=batch.id,
        subject_id=subject.id,
        faculty_id=faculty.id,
        scheduled_at=payload.scheduled_at,
        duration_minutes=payload.duration_minutes,
        max_marks=payload.max_marks,
        pass_marks=payload.pass_marks,
        instructions=payload.instructions.strip(),
        status=payload.status,
        created_by=actor.id,
    )
    db.add(exam)
    db.flush()
    roster = _active_roster(db, batch)
    _snapshot_roster(db, exam, roster)
    audit(
        db,
        actor,
        "examinations.create",
        "examination",
        exam.id,
        after={
            "batchId": batch.id,
            "subjectId": subject.id,
            "facultyId": faculty.id,
            "status": exam.status,
        },
    )
    db.commit()
    return _serialize(
        exam,
        batch,
        subject,
        faculty,
        len(roster),
        {},
    )


@router.get("/{exam_id}")
def examination_detail(
    exam_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    exam, batch, subject, faculty = _get_exam_row(db, exam_id)
    if not _can_manage(actor, exam):
        raise HTTPException(403, "You do not have access to this examination")
    roster = _exam_roster(db, exam)
    results = {
        row.student_id: row
        for row in db.query(ExaminationResult).filter_by(exam_id=exam.id).all()
    }
    stats = _result_stats(db, [exam.id]).get(exam.id, {})
    payload = _serialize(exam, batch, subject, faculty, len(roster), stats)
    payload["students"] = [{
        "studentId": student.student_id,
        "admissionNumber": student.admission_number,
        "fullName": student.full_name,
        "resultStatus": results[student.student_id].result_status if student.student_id in results else "pending",
        "marksObtained": (
            float(results[student.student_id].marks_obtained)
            if student.student_id in results and results[student.student_id].marks_obtained is not None
            else None
        ),
        "remarks": results[student.student_id].remarks if student.student_id in results else "",
    } for student in roster]
    return payload


@router.patch("/{exam_id}")
def update_examination(
    exam_id: str,
    payload: ExaminationUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    exam, old_batch, old_subject, old_faculty = _get_exam_row(db, exam_id)
    if not _can_manage(actor, exam):
        raise HTTPException(403, "You do not have access to this examination")
    if exam.status == "published":
        raise HTTPException(409, "Published examinations cannot be edited")
    batch, subject, faculty = _validate_references(db, payload, actor)
    scope_changed = batch.id != exam.batch_id
    if scope_changed and db.query(ExaminationResult).filter_by(
        exam_id=exam.id,
    ).count():
        raise HTTPException(
            409,
            "The batch cannot change after marks entry has started",
        )
    before = _serialize(exam, old_batch, old_subject, old_faculty, 0, {})
    exam.name = payload.name.strip()
    exam.batch_id = batch.id
    exam.subject_id = subject.id
    exam.faculty_id = faculty.id
    exam.scheduled_at = payload.scheduled_at
    exam.duration_minutes = payload.duration_minutes
    exam.max_marks = payload.max_marks
    exam.pass_marks = payload.pass_marks
    exam.instructions = payload.instructions.strip()
    exam.status = payload.status
    if scope_changed:
        db.query(ExaminationParticipant).filter_by(exam_id=exam.id).delete(
            synchronize_session=False,
        )
        _snapshot_roster(db, exam, _active_roster(db, batch))
    audit(
        db,
        actor,
        "examinations.update",
        "examination",
        exam.id,
        before=before,
        after=payload.model_dump(by_alias=True, mode="json"),
    )
    db.commit()
    stats = _result_stats(db, [exam.id]).get(exam.id, {})
    return _serialize(
        exam,
        batch,
        subject,
        faculty,
        len(_exam_roster(db, exam)),
        stats,
    )


@router.put("/{exam_id}/marks")
def save_marks(
    exam_id: str,
    payload: ExaminationMarksSave,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    exam, batch, _, _ = _get_exam_row(db, exam_id)
    if not _can_manage(actor, exam):
        raise HTTPException(403, "You do not have access to this examination")
    if exam.status in ("published", "cancelled"):
        raise HTTPException(409, "Marks cannot be changed for this examination")
    roster_ids = {
        participant.student_id
        for participant in _exam_roster(db, exam)
    }
    submitted_ids = [entry.student_id for entry in payload.entries]
    if len(submitted_ids) != len(set(submitted_ids)):
        raise HTTPException(422, "Each student can appear only once")
    if not set(submitted_ids).issubset(roster_ids):
        raise HTTPException(422, "Marks include a student outside this examination batch")
    for entry in payload.entries:
        existing = db.get(ExaminationResult, (exam.id, entry.student_id))
        if entry.result_status == "pending":
            if existing:
                db.delete(existing)
            continue
        if (
            entry.result_status == "graded"
            and Decimal(entry.marks_obtained) > Decimal(exam.max_marks)
        ):
            raise HTTPException(422, "Marks obtained cannot exceed maximum marks")
        if not existing:
            existing = ExaminationResult(
                exam_id=exam.id,
                student_id=entry.student_id,
                entered_by=actor.id,
            )
            db.add(existing)
        existing.result_status = entry.result_status
        existing.marks_obtained = entry.marks_obtained
        existing.remarks = entry.remarks.strip()
        existing.entered_by = actor.id
    exam.status = "marks_entry"
    audit(
        db,
        actor,
        "examinations.marks.save",
        "examination",
        exam.id,
        after={"entriesReceived": len(payload.entries), "status": exam.status},
    )
    db.commit()
    return examination_detail(exam.id, db, actor)


@router.post("/{exam_id}/publish")
def publish_results(
    exam_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    exam, batch, subject, faculty = _get_exam_row(db, exam_id)
    if not _can_manage(actor, exam):
        raise HTTPException(403, "You do not have access to this examination")
    if exam.status == "cancelled":
        raise HTTPException(409, "Cancelled examinations cannot be published")
    if exam.status == "published":
        return _serialize_many(db, [(exam, batch, subject, faculty)])[0]
    roster_ids = {
        participant.student_id
        for participant in _exam_roster(db, exam)
    }
    result_ids = {
        student_id
        for student_id, in db.query(ExaminationResult.student_id)
        .filter(
            ExaminationResult.exam_id == exam.id,
            ExaminationResult.result_status != "pending",
        )
        .all()
    }
    missing = len(roster_ids - result_ids)
    if missing:
        raise HTTPException(
            409,
            f"Complete results for all students before publishing ({missing} pending)",
        )
    exam.status = "published"
    exam.published_at = datetime.now(timezone.utc)
    audit(
        db,
        actor,
        "examinations.publish",
        "examination",
        exam.id,
        after={"students": len(roster_ids), "publishedAt": exam.published_at.isoformat()},
    )
    db.commit()
    return _serialize_many(db, [(exam, batch, subject, faculty)])[0]
