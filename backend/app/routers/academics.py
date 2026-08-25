from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from ..assignment_materials import (
    MATERIAL_LIFETIME_HOURS,
    MAX_ASSIGNMENT_PDF_BYTES,
    material_maps,
    purge_expired_assignment_materials,
    serialize_material,
)
from ..database import get_db
from ..models import (
    Assignment,
    AssignmentDownload,
    AssignmentMaterial,
    AssignmentRecipient,
    Batch,
    FacultyTeachingAssignment,
    Subject,
    User,
)
from ..operations_schemas import AssignmentCreate, AssignmentUpdate
from ..security import require_roles
from ..services import SubjectRosterResolver, audit

router = APIRouter(prefix="/api/academics", tags=["academics"])
ROLES = ("owner", "academic_coordinator", "faculty")


def _assignments(db: Session):
    return (
        db.query(Assignment, Batch, Subject)
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
    )


def _progress_counts(db: Session, eligible_by_assignment: dict[str, set[str]]):
    if not eligible_by_assignment:
        return {}
    rows = (
        db.query(
            AssignmentRecipient.assignment_id,
            AssignmentRecipient.student_id,
            AssignmentRecipient.status,
        )
        .filter(AssignmentRecipient.assignment_id.in_(eligible_by_assignment))
        .all()
    )
    counts: dict[str, dict[str, int]] = {}
    for assignment_id, student_id, status in rows:
        if student_id not in eligible_by_assignment[assignment_id]:
            continue
        statuses = counts.setdefault(assignment_id, {})
        statuses[status] = statuses.get(status, 0) + 1
    return counts


def _serialize(row, batch, subject, recipients, progress=None, material=None, downloaded=0):
    progress = progress or {}
    return {"id": row.id, "title": row.title, "instructions": row.instructions, "batchId": batch.id, "batch": batch.name, "program": batch.program, "subjectId": subject.id, "subject": subject.name, "dueAt": row.due_at, "externalUrl": row.external_url or None, "status": row.status, "recipientCount": recipients, "progress": {"notStarted": max(0, int(recipients) - sum(progress.values())), "viewed": progress.get("viewed", 0), "submitted": progress.get("submitted", 0), "completed": progress.get("completed", 0), "downloaded": int(downloaded)}, "material": serialize_material(material, downloaded_count=downloaded), "createdAt": row.created_at}


def _manage_assignment(db: Session, assignment_id: str, actor: User) -> Assignment:
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    if actor.role == "faculty" and assignment.created_by != actor.id:
        raise HTTPException(403, "Faculty can manage only their own assignments")
    return assignment


def _material_response(material: AssignmentMaterial) -> Response:
    safe_name = material.filename.replace("\r", "").replace("\n", "")
    return Response(
        content=material.content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(safe_name, safe='')}",
            "Content-Length": str(material.size_bytes),
            "Cache-Control": "private, no-store",
            "Content-Security-Policy": "sandbox",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/assignments")
def list_assignments(db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    query = _assignments(db)
    if user.role == "faculty": query = query.filter(Assignment.created_by == user.id)
    rows = query.order_by(Assignment.due_at.desc()).all()
    roster = SubjectRosterResolver(db)
    eligible = {
        assignment.id: roster.student_ids_for(batch, subject)
        for assignment, batch, subject in rows
    }
    progress = _progress_counts(db, eligible)
    materials, downloads = material_maps(db, set(eligible))
    return [
        _serialize(
            assignment,
            batch,
            subject,
            len(eligible[assignment.id]),
            progress.get(assignment.id, {}),
            materials.get(assignment.id),
            downloads.get(assignment.id, 0),
        )
        for assignment, batch, subject in rows
    ]


@router.post("/assignments", status_code=201)
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles(*ROLES))):
    batch, subject = db.get(Batch, payload.batch_id), db.get(Subject, payload.subject_id)
    if not batch or not subject:
        raise HTTPException(404, "Batch or subject not found")
    if actor.role == "faculty" and not (
        db.query(FacultyTeachingAssignment)
        .filter_by(
            batch_id=batch.id,
            subject_id=subject.id,
            faculty_id=actor.id,
            is_active=True,
        )
        .first()
    ):
        raise HTTPException(
            403,
            "Faculty can publish only to assigned batches and subjects",
        )
    recipient_count = SubjectRosterResolver(db).count_for(batch, subject)
    if not recipient_count:
        raise HTTPException(409, "This batch has no active enrolled students")
    row = Assignment(batch_id=batch.id, subject_id=subject.id, title=payload.title.strip(), instructions=payload.instructions.strip(), due_at=payload.due_at, external_url=str(payload.external_url) if payload.external_url else "", status=payload.status, created_by=actor.id)
    db.add(row)
    db.flush()
    audit(db, actor, "academics.assignment.create", "assignment", row.id, after={"batch_id": batch.id, "subject_id": subject.id, "recipients": recipient_count, "status": payload.status})
    db.commit()
    return _serialize(row, batch, subject, recipient_count)


@router.get("/assignments/{assignment_id}/progress")
def assignment_progress(
    assignment_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    assignment = _manage_assignment(db, assignment_id, actor)
    batch = db.get(Batch, assignment.batch_id)
    subject = db.get(Subject, assignment.subject_id)
    if not batch or not subject:
        raise HTTPException(409, "Assignment batch or subject is no longer available")
    recipients = {
        row.student_id: row
        for row in db.query(AssignmentRecipient)
        .filter_by(assignment_id=assignment.id)
        .all()
    }
    downloads = {
        row.student_id: row
        for row in db.query(AssignmentDownload)
        .filter_by(assignment_id=assignment.id)
        .all()
    }
    students = SubjectRosterResolver(db).students_for(batch, subject)
    return {
        "assignmentId": assignment.id,
        "recipientCount": len(students),
        "students": [
            {
                "studentId": student.id,
                "admissionNumber": student.admission_number,
                "fullName": student.full_name,
                "status": (
                    recipients[student.id].status
                    if student.id in recipients
                    else "not_started"
                ),
                "updatedAt": (
                    recipients[student.id].updated_at
                    if student.id in recipients
                    else None
                ),
                "downloaded": student.id in downloads,
                "downloadedAt": (
                    downloads[student.id].first_downloaded_at
                    if student.id in downloads
                    else None
                ),
            }
            for student in students
        ],
    }


@router.post("/assignments/{assignment_id}/publish")
def publish_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    row = _manage_assignment(db, assignment_id, actor)
    batch, subject = db.get(Batch, row.batch_id), db.get(Subject, row.subject_id)
    if not batch or not subject:
        raise HTTPException(409, "Assignment batch or subject is no longer available")
    if row.status != "published":
        before = {"status": row.status}
        row.status = "published"
        audit(
            db,
            actor,
            "academics.assignment.publish",
            "assignment",
            row.id,
            before=before,
            after={"status": "published"},
        )
        db.commit()
    recipients = SubjectRosterResolver(db).count_for(batch, subject)
    return _serialize(row, batch, subject, recipients)


@router.patch("/assignments/{assignment_id}")
def update_assignment(
    assignment_id: str,
    payload: AssignmentUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    row = _manage_assignment(db, assignment_id, actor)
    batch, subject = db.get(Batch, payload.batch_id), db.get(Subject, payload.subject_id)
    if not batch or not subject:
        raise HTTPException(404, "Batch or subject not found")
    if actor.role == "faculty":
        assigned = db.query(FacultyTeachingAssignment).filter_by(
            batch_id=batch.id,
            subject_id=subject.id,
            faculty_id=actor.id,
            is_active=True,
        ).first()
        if not assigned:
            raise HTTPException(
                403,
                "Faculty can edit assignments only for assigned batches and subjects",
            )
    before = _serialize(row, db.get(Batch, row.batch_id), db.get(Subject, row.subject_id), 0)
    row.batch_id = batch.id
    row.subject_id = subject.id
    row.title = payload.title.strip()
    row.instructions = payload.instructions.strip()
    row.due_at = payload.due_at
    row.external_url = str(payload.external_url) if payload.external_url else ""
    row.status = payload.status
    audit(db, actor, "academics.assignment.update", "assignment", row.id, before=before, after=payload.model_dump(by_alias=True, mode="json"))
    db.commit()
    recipients = SubjectRosterResolver(db).count_for(batch, subject)
    return _serialize(row, batch, subject, recipients)


@router.post("/assignments/{assignment_id}/material")
async def upload_assignment_material(
    assignment_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    assignment = _manage_assignment(db, assignment_id, actor)
    filename = (file.filename or "assignment.pdf").strip()
    if not filename.casefold().endswith(".pdf"):
        raise HTTPException(415, "Only PDF assignment files are accepted")
    content = await file.read(MAX_ASSIGNMENT_PDF_BYTES + 1)
    await file.close()
    if not content.startswith(b"%PDF-"):
        raise HTTPException(415, "The selected file is not a valid PDF")
    if len(content) > MAX_ASSIGNMENT_PDF_BYTES:
        raise HTTPException(413, "PDF must be 15 MB or smaller")
    if not content:
        raise HTTPException(400, "The selected PDF is empty")
    expires_at = datetime.now(timezone.utc) + timedelta(hours=MATERIAL_LIFETIME_HOURS)
    material = db.get(AssignmentMaterial, assignment.id)
    if material:
        material.filename = filename[:255]
        material.mime_type = "application/pdf"
        material.size_bytes = len(content)
        material.content = content
        material.expires_at = expires_at
        material.created_at = datetime.now(timezone.utc)
    else:
        material = AssignmentMaterial(
            assignment_id=assignment.id,
            filename=filename[:255],
            mime_type="application/pdf",
            size_bytes=len(content),
            content=content,
            expires_at=expires_at,
        )
        db.add(material)
    # Download status belongs to the current file, not an older PDF that was
    # replaced on the same assignment.
    db.query(AssignmentDownload).filter_by(
        assignment_id=assignment.id,
    ).delete(synchronize_session=False)
    audit(
        db,
        actor,
        "academics.assignment.material.upload",
        "assignment",
        assignment.id,
        after={
            "filename": filename[:255],
            "sizeBytes": len(content),
            "expiresAt": expires_at.isoformat(),
        },
    )
    db.commit()
    return serialize_material(material)


@router.get("/assignments/{assignment_id}/material")
def download_assignment_material(
    assignment_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    assignment = _manage_assignment(db, assignment_id, actor)
    if purge_expired_assignment_materials(db):
        db.commit()
    material = db.get(AssignmentMaterial, assignment.id)
    if not material:
        raise HTTPException(404, "This PDF is no longer available")
    return _material_response(material)


@router.delete("/assignments/{assignment_id}/material", status_code=204)
def delete_assignment_material(
    assignment_id: str,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    assignment = _manage_assignment(db, assignment_id, actor)
    material = db.get(AssignmentMaterial, assignment.id)
    if material:
        db.delete(material)
        audit(
            db,
            actor,
            "academics.assignment.material.delete",
            "assignment",
            assignment.id,
        )
        db.commit()
    return Response(status_code=204)
