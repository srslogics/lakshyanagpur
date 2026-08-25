from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import AssignmentDownload, AssignmentMaterial


MATERIAL_LIFETIME_HOURS = 48
MAX_ASSIGNMENT_PDF_BYTES = 15 * 1024 * 1024


def aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def purge_expired_assignment_materials(
    db: Session,
    *,
    current_time: datetime | None = None,
) -> int:
    """Delete expired PDF bytes while retaining assignment and download history."""

    cutoff = current_time or datetime.now(timezone.utc)
    expired = (
        db.query(AssignmentMaterial)
        .filter(AssignmentMaterial.expires_at <= cutoff)
        .all()
    )
    for material in expired:
        db.delete(material)
    if expired:
        db.flush()
    return len(expired)


def material_maps(db: Session, assignment_ids: list[str] | set[str]):
    ids = list(assignment_ids)
    if not ids:
        return {}, {}
    purged = purge_expired_assignment_materials(db)
    if purged:
        db.commit()
    materials = {
        row.assignment_id: row
        for row in db.query(AssignmentMaterial)
        .filter(AssignmentMaterial.assignment_id.in_(ids))
        .all()
    }
    downloads = {
        assignment_id: int(count)
        for assignment_id, count in (
            db.query(
                AssignmentDownload.assignment_id,
                func.count(AssignmentDownload.student_id),
            )
            .filter(AssignmentDownload.assignment_id.in_(ids))
            .group_by(AssignmentDownload.assignment_id)
            .all()
        )
    }
    return materials, downloads


def serialize_material(
    material: AssignmentMaterial | None,
    *,
    downloaded_count: int = 0,
) -> dict:
    if not material:
        return {
            "available": False,
            "filename": None,
            "sizeBytes": 0,
            "expiresAt": None,
            "downloadedCount": int(downloaded_count),
        }
    return {
        "available": True,
        "filename": material.filename,
        "sizeBytes": material.size_bytes,
        "expiresAt": aware(material.expires_at),
        "downloadedCount": int(downloaded_count),
    }
