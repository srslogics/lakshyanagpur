from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Batch, Notice, User
from ..operations_schemas import NoticeCreate, NoticeUpdate
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/communication", tags=["communication"])
ROLES = ("owner", "admissions_manager", "academic_coordinator", "front_desk")


def _serialize(row: Notice, batch: Batch | None):
    delivery_status = (
        "delivered"
        if row.status == "published" and row.channel == "in_app"
        else "draft"
        if row.status == "draft"
        else "provider_required"
    )
    return {"id": row.id, "title": row.title, "body": row.body, "audience": row.audience, "channel": row.channel, "batchId": row.batch_id, "batch": batch.name if batch else None, "program": batch.program if batch else None, "status": row.status, "deliveryStatus": delivery_status, "publishedAt": row.published_at, "createdAt": row.created_at}


def _validate_delivery(channel: str, status: str):
    if status == "published" and channel != "in_app":
        raise HTTPException(
            409,
            detail={
                "code": "DELIVERY_PROVIDER_REQUIRED",
                "message": (
                    "Email, SMS and WhatsApp delivery require a connected "
                    "provider. Save this notice as a draft or publish it in-app."
                ),
            },
        )


@router.get("/capabilities")
def delivery_capabilities(
    user: User = Depends(require_roles(*ROLES)),
):
    return {
        "channels": [
            {"id": "in_app", "label": "In app", "available": True},
            {
                "id": "email",
                "label": "Email",
                "available": False,
                "reason": "Delivery provider not connected",
            },
            {
                "id": "sms",
                "label": "SMS",
                "available": False,
                "reason": "Delivery provider not connected",
            },
            {
                "id": "whatsapp",
                "label": "WhatsApp",
                "available": False,
                "reason": "Delivery provider not connected",
            },
        ]
    }


@router.get("/notices")
def list_notices(db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    rows = db.query(Notice, Batch).outerjoin(Batch, Batch.id == Notice.batch_id).order_by(Notice.created_at.desc()).all()
    return [_serialize(*row) for row in rows]


@router.post("/notices", status_code=201)
def create_notice(payload: NoticeCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles(*ROLES))):
    _validate_delivery(payload.channel, payload.status)
    batch = db.get(Batch, payload.batch_id) if payload.batch_id else None
    if payload.batch_id and not batch:
        raise HTTPException(404, "Batch not found")
    row = Notice(title=payload.title.strip(), body=payload.body.strip(), audience=payload.audience, channel=payload.channel, batch_id=payload.batch_id, status=payload.status, published_at=datetime.now(timezone.utc) if payload.status == "published" else None, created_by=actor.id)
    db.add(row); db.flush()
    audit(db, actor, "communication.notice.create", "notice", row.id, after={"audience": row.audience, "channel": row.channel, "status": row.status, "batch_id": row.batch_id})
    db.commit()
    return _serialize(row, batch)


@router.patch("/notices/{notice_id}")
def update_notice(notice_id: str, payload: NoticeUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(Notice, notice_id)
    if not row:
        raise HTTPException(404, "Notice not found")
    _validate_delivery(payload.channel, payload.status)
    batch = db.get(Batch, payload.batch_id) if payload.batch_id else None
    if payload.batch_id and not batch:
        raise HTTPException(404, "Batch not found")
    before = _serialize(row, db.get(Batch, row.batch_id) if row.batch_id else None)
    row.title = payload.title.strip()
    row.body = payload.body.strip()
    row.audience = payload.audience
    row.channel = payload.channel
    row.batch_id = payload.batch_id
    row.status = payload.status
    row.published_at = datetime.now(timezone.utc) if payload.status == "published" and not row.published_at else (None if payload.status == "draft" else row.published_at)
    audit(db, actor, "communication.notice.update", "notice", row.id, before=before, after=payload.model_dump(by_alias=True))
    db.commit()
    return _serialize(row, batch)
