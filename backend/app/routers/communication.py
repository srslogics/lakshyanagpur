from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Batch, Notice, User
from ..operations_schemas import NoticeCreate
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/communication", tags=["communication"])
ROLES = ("owner", "admissions_manager", "academic_coordinator", "front_desk")


def _serialize(row: Notice, batch: Batch | None):
    return {"id": row.id, "title": row.title, "body": row.body, "audience": row.audience, "channel": row.channel, "batchId": row.batch_id, "batch": batch.name if batch else None, "status": row.status, "publishedAt": row.published_at, "createdAt": row.created_at}


@router.get("/notices")
def list_notices(db: Session = Depends(get_db), user: User = Depends(require_roles(*ROLES))):
    rows = db.query(Notice, Batch).outerjoin(Batch, Batch.id == Notice.batch_id).order_by(Notice.created_at.desc()).all()
    return [_serialize(*row) for row in rows]


@router.post("/notices", status_code=201)
def create_notice(payload: NoticeCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles(*ROLES))):
    batch = db.get(Batch, payload.batch_id) if payload.batch_id else None
    if payload.batch_id and not batch:
        raise HTTPException(404, "Batch not found")
    row = Notice(title=payload.title.strip(), body=payload.body.strip(), audience=payload.audience, channel=payload.channel, batch_id=payload.batch_id, status=payload.status, published_at=datetime.now(timezone.utc) if payload.status == "published" else None, created_by=actor.id)
    db.add(row); db.flush()
    audit(db, actor, "communication.notice.create", "notice", row.id, after={"audience": row.audience, "channel": row.channel, "status": row.status, "batch_id": row.batch_id})
    db.commit()
    return _serialize(row, batch)
