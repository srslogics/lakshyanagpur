from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timedelta, timezone
from threading import Lock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import (
    Batch,
    FacultyTeachingAssignment,
    Notice,
    NotificationDelivery,
    ParentAccount,
    PushSubscription,
    StudentAccount,
    Subject,
    User,
)
from .services import SubjectRosterResolver


_CURVE_ORDER = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
_delivery_lock = Lock()


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _configured_private_key(value: str) -> ec.EllipticCurvePrivateKey:
    """Accept either a PEM key or the URL-safe DER value used by pywebpush."""
    if "-----BEGIN" in value:
        private_key = serialization.load_pem_private_key(value.encode(), password=None)
    else:
        raw = _b64url_decode(value)
        if len(raw) == 32:
            private_key = ec.derive_private_key(int.from_bytes(raw, "big"), ec.SECP256R1())
        else:
            private_key = serialization.load_der_private_key(raw, password=None)
    if not isinstance(private_key, ec.EllipticCurvePrivateKey) or not isinstance(private_key.curve, ec.SECP256R1):
        raise ValueError("WEB_PUSH_PRIVATE_KEY must be a P-256 private key")
    return private_key


def _vapid_keys() -> tuple[str, str]:
    """Return a stable VAPID pair without requiring another production secret.

    A separately provisioned WEB_PUSH_PRIVATE_KEY is preferred. When omitted,
    the key is deterministically derived from the application's production
    SECRET_KEY, which is already required to be stable and private.
    """
    if settings.web_push_private_key:
        private_key = _configured_private_key(settings.web_push_private_key)
    else:
        seed = hashlib.sha256(b"lakshya-web-push-v1\0" + settings.secret_key.encode()).digest()
        private_key = ec.derive_private_key((int.from_bytes(seed, "big") % (_CURVE_ORDER - 1)) + 1, ec.SECP256R1())
    # pywebpush treats an inline string as URL-safe base64 DER. Passing PEM
    # here looks valid but fails only when the first real notification is sent.
    private_value = _b64url(private_key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    derived_public_key = _b64url(private_key.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    ))
    if settings.web_push_public_key and settings.web_push_public_key != derived_public_key:
        raise ValueError("WEB_PUSH_PUBLIC_KEY does not match WEB_PUSH_PRIVATE_KEY")
    public_key = settings.web_push_public_key or derived_public_key
    return private_value, public_key


def public_key() -> str:
    return _vapid_keys()[1]


def _student_user_ids(db: Session, student_ids: set[str]) -> set[str]:
    if not student_ids:
        return set()
    students = {
        user_id for user_id, in db.query(StudentAccount.user_id)
        .filter(StudentAccount.student_id.in_(student_ids)).all()
    }
    parents = {
        user_id for user_id, in db.query(ParentAccount.user_id)
        .filter(ParentAccount.student_id.in_(student_ids)).all()
    }
    return students | parents


def notice_recipient_user_ids(db: Session, notice: Notice) -> set[str]:
    active = db.query(User.id).filter(User.is_active.is_(True), User.is_test_account.is_(False))
    if notice.audience == "all":
        recipients = {row[0] for row in active.all()}
    elif notice.audience == "students":
        recipients = {row[0] for row in active.filter(User.role == "student").all()}
    elif notice.audience == "parents":
        recipients = {row[0] for row in active.filter(User.role.in_(("parent", "parent_student"))).all()}
    elif notice.audience == "faculty":
        recipients = {row[0] for row in active.filter(User.role == "faculty").all()}
    elif notice.audience in {"batch", "subject"}:
        batch = db.get(Batch, notice.batch_id) if notice.batch_id else None
        subject = db.get(Subject, notice.subject_id) if notice.subject_id else None
        if not batch:
            return set()
        resolver = SubjectRosterResolver(db)
        if notice.audience == "subject" and subject:
            student_ids = resolver.student_ids_for(batch, subject)
        else:
            student_ids = set()
            subjects = db.query(Subject).filter(Subject.is_active.is_(True)).all()
            for row in subjects:
                student_ids.update(resolver.student_ids_for(batch, row))
        recipients = _student_user_ids(db, student_ids)
        if notice.audience == "batch":
            recipients.update({
                faculty_id for faculty_id, in db.query(FacultyTeachingAssignment.faculty_id)
                .filter(
                    FacultyTeachingAssignment.batch_id == batch.id,
                    FacultyTeachingAssignment.is_active.is_(True),
                ).all()
            })
    else:
        recipients = set()
    recipients.discard(notice.created_by)
    return recipients


def user_can_receive_notice(db: Session, user: User, notice: Notice) -> bool:
    return user.id == notice.created_by or user.id in notice_recipient_user_ids(db, notice)


def materialize_deliveries(db: Session, notice: Notice) -> int:
    if notice.status != "published" or notice.channel != "in_app":
        return 0
    recipient_ids = notice_recipient_user_ids(db, notice)
    if not recipient_ids:
        return 0
    subscriptions = db.query(PushSubscription).filter(
        PushSubscription.user_id.in_(recipient_ids),
        PushSubscription.is_active.is_(True),
    ).all()
    existing = {
        subscription_id for subscription_id, in db.query(NotificationDelivery.subscription_id)
        .filter(NotificationDelivery.notice_id == notice.id).all()
    }
    created = 0
    for subscription in subscriptions:
        if subscription.id in existing:
            continue
        db.add(NotificationDelivery(
            notice_id=notice.id,
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            status="pending",
        ))
        created += 1
    return created


def _portal_url(subscription: PushSubscription, notice_id: str) -> str:
    routes = {
        "operations": ("/operations/communication", ""),
        "student": ("/student-app/", "#notices"),
        "parent": ("/parent-app/", "#more"),
        "faculty": ("/faculty-app/", "#notices"),
        "attendance": ("/attendance-app/", ""),
    }
    base, fragment = routes.get(subscription.portal, ("/", ""))
    return f"{base}?notice={notice_id}{fragment}"


def dispatch_pending(limit: int = 100) -> int:
    if not _delivery_lock.acquire(blocking=False):
        return 0
    delivered = 0
    try:
        private_key, _ = _vapid_keys()
        with SessionLocal() as db:
            db.query(NotificationDelivery).filter(
                NotificationDelivery.status == "sending",
                NotificationDelivery.updated_at < datetime.now(timezone.utc) - timedelta(minutes=10),
            ).update({NotificationDelivery.status: "failed"}, synchronize_session=False)
            db.commit()
            rows = (
                db.query(NotificationDelivery, PushSubscription, Notice)
                .join(PushSubscription, PushSubscription.id == NotificationDelivery.subscription_id)
                .join(Notice, Notice.id == NotificationDelivery.notice_id)
                .filter(
                    NotificationDelivery.status.in_(("pending", "failed")),
                    NotificationDelivery.attempt_count < 3,
                    PushSubscription.is_active.is_(True),
                )
                .order_by(NotificationDelivery.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
                .all()
            )
            for delivery, _, _ in rows:
                delivery.status = "sending"
                delivery.attempt_count += 1
            db.commit()
            for delivery, subscription, notice in rows:
                payload = json.dumps({
                    "title": "New Lakshya announcement",
                    "body": "Tap to open the app and view it securely.",
                    "noticeId": notice.id,
                    "url": _portal_url(subscription, notice.id),
                })
                try:
                    webpush(
                        subscription_info={
                            "endpoint": subscription.endpoint,
                            "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                        },
                        data=payload,
                        vapid_private_key=private_key,
                        vapid_claims={"sub": settings.web_push_subject},
                        ttl=86400,
                        timeout=10,
                    )
                    now = datetime.now(timezone.utc)
                    delivery.status = "sent"
                    delivery.sent_at = now
                    delivery.last_error = ""
                    subscription.last_success_at = now
                    subscription.last_error = ""
                    delivered += 1
                except WebPushException as error:
                    status_code = getattr(getattr(error, "response", None), "status_code", None)
                    delivery.status = "failed"
                    delivery.last_error = str(error)[:1000]
                    subscription.last_error = delivery.last_error
                    if status_code in {404, 410}:
                        subscription.is_active = False
                except Exception as error:  # provider/network errors must never break the API
                    delivery.status = "failed"
                    delivery.last_error = str(error)[:1000]
                    subscription.last_error = delivery.last_error
                db.commit()
    finally:
        _delivery_lock.release()
    return delivered
