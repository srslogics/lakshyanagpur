from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Notice, NotificationDelivery, PushSubscription, User
from ..push_notifications import public_key, user_can_receive_notice
from ..security import current_user


router = APIRouter(prefix="/api/push", tags=["push"])


class SubscriptionKeys(BaseModel):
    p256dh: str = Field(min_length=16, max_length=1024)
    auth: str = Field(min_length=8, max_length=512)


class SubscriptionUpsert(BaseModel):
    endpoint: HttpUrl
    keys: SubscriptionKeys
    portal: Literal["operations", "student", "parent", "faculty", "attendance"]
    user_agent: str = Field(default="", alias="userAgent", max_length=500)
    model_config = {"populate_by_name": True}


class SubscriptionDelete(BaseModel):
    endpoint: HttpUrl


def _portal_allowed(user: User, portal: str) -> bool:
    if portal == "student":
        return user.role == "student"
    if portal == "parent":
        return user.role in {"parent", "parent_student"}
    if portal == "faculty":
        return user.role == "faculty"
    if portal == "attendance":
        return user.role == "attendance_operator"
    return user.role not in {"student", "parent", "parent_student", "faculty", "attendance_operator"}


@router.get("/config")
def push_config(user: User = Depends(current_user)):
    return {"available": True, "publicKey": public_key()}


@router.put("/subscriptions")
def upsert_subscription(
    payload: SubscriptionUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if not _portal_allowed(user, payload.portal):
        raise HTTPException(403, "This account cannot subscribe from that portal")
    endpoint = str(payload.endpoint)
    row = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).one_or_none()
    if not row:
        row = PushSubscription(user_id=user.id, endpoint=endpoint, p256dh="", auth="", portal=payload.portal)
        db.add(row)
    row.user_id = user.id
    row.p256dh = payload.keys.p256dh
    row.auth = payload.keys.auth
    row.portal = payload.portal
    row.user_agent = payload.user_agent
    row.is_active = True
    row.last_error = ""
    db.commit()
    return {"subscribed": True}


@router.delete("/subscriptions")
def remove_subscription(
    payload: SubscriptionDelete,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    row = db.query(PushSubscription).filter(
        PushSubscription.endpoint == str(payload.endpoint),
        PushSubscription.user_id == user.id,
    ).one_or_none()
    if row:
        row.is_active = False
        db.commit()
    return {"subscribed": False}


@router.post("/notices/{notice_id}/opened")
def mark_opened(
    notice_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    notice = db.get(Notice, notice_id)
    if not notice or not user_can_receive_notice(db, user, notice):
        raise HTTPException(404, "Announcement not found")
    now = datetime.now(timezone.utc)
    rows = db.query(NotificationDelivery).filter(
        NotificationDelivery.notice_id == notice.id,
        NotificationDelivery.user_id == user.id,
    ).all()
    for row in rows:
        row.status = "opened"
        row.opened_at = now
    db.commit()
    return {"opened": True}
