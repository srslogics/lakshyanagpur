from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Batch,
    CommunicationMessage,
    CommunicationThread,
    Enrollment,
    FacultyTeachingAssignment,
    Notice,
    ParentAccount,
    Student,
    StudentAccount,
    Subject,
    User,
)
from ..operations_schemas import (
    CommunicationMessageCreate,
    CommunicationThreadCreate,
    CommunicationThreadStatusUpdate,
    NoticeCreate,
    NoticeUpdate,
)
from ..permissions import has_permission
from ..security import require_roles
from ..services import SubjectRosterResolver, audit

router = APIRouter(prefix="/api/communication", tags=["communication"])
ROLES = ("owner", "admissions_manager", "academic_coordinator", "front_desk")
CONVERSATION_ROLES = (*ROLES, "student", "parent_student", "parent", "faculty")
PORTAL_CREATOR_ROLES = ("student", "parent_student", "parent")


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


def _linked_student(db: Session, user: User) -> Student:
    model = ParentAccount if user.role == "parent" else StudentAccount
    student = (
        db.query(Student)
        .join(model, model.student_id == Student.id)
        .filter(model.user_id == user.id, Student.is_test_account.is_(False))
        .first()
    )
    if not student:
        raise HTTPException(403, "This account is not linked to a student record")
    return student


def _active_enrollment(db: Session, student_id: str) -> Enrollment | None:
    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id, Enrollment.is_active.is_(True))
        .order_by(Enrollment.created_at.desc(), Enrollment.id.desc())
        .first()
    )


def _student_subjects(db: Session, student_id: str):
    enrollment = _active_enrollment(db, student_id)
    if not enrollment or not enrollment.batch:
        return []
    rows = (
        db.query(Subject, User, Batch)
        .join(
            FacultyTeachingAssignment,
            and_(
                FacultyTeachingAssignment.subject_id == Subject.id,
                FacultyTeachingAssignment.is_active.is_(True),
            ),
        )
        .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
        .join(User, User.id == FacultyTeachingAssignment.faculty_id)
        .filter(
            Batch.name == enrollment.batch,
            or_(
                Batch.program == enrollment.program,
                Batch.program == "All programs",
            ),
            Batch.is_active.is_(True),
            Subject.is_active.is_(True),
            User.is_active.is_(True),
        )
        .order_by(Subject.name, User.full_name)
        .all()
    )
    resolver = SubjectRosterResolver(db)
    grouped = {}
    for subject, faculty, batch in rows:
        if student_id not in resolver.student_ids_for(batch, subject):
            continue
        item = grouped.setdefault(subject.id, {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "faculty": [],
        })
        if faculty.full_name not in item["faculty"]:
            item["faculty"].append(faculty.full_name)
    return list(grouped.values())


def _faculty_assignments(db: Session, faculty_id: str):
    return (
        db.query(FacultyTeachingAssignment, Batch, Subject)
        .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
        .join(Subject, Subject.id == FacultyTeachingAssignment.subject_id)
        .filter(
            FacultyTeachingAssignment.faculty_id == faculty_id,
            FacultyTeachingAssignment.is_active.is_(True),
            Batch.is_active.is_(True),
            Subject.is_active.is_(True),
        )
        .all()
    )


def _faculty_can_access(db: Session, faculty_id: str, thread: CommunicationThread) -> bool:
    if not thread.subject_id:
        return False
    resolver = SubjectRosterResolver(db)
    for _, batch, subject in _faculty_assignments(db, faculty_id):
        if subject.id != thread.subject_id:
            continue
        if thread.student_id in resolver.student_ids_for(batch, subject):
            return True
    return False


def _can_access_thread(db: Session, user: User, thread: CommunicationThread) -> bool:
    if user.role in ROLES or has_permission(db, user, "communication", "read"):
        return True
    if user.role in PORTAL_CREATOR_ROLES:
        return _linked_student(db, user).id == thread.student_id
    if user.role == "faculty":
        return _faculty_can_access(db, user.id, thread)
    return False


def _thread_or_404(db: Session, user: User, thread_id: str) -> CommunicationThread:
    thread = db.get(CommunicationThread, thread_id)
    if not thread or not _can_access_thread(db, user, thread):
        raise HTTPException(404, "Conversation not found")
    return thread


def _thread_rows(db: Session, user: User):
    query = (
        db.query(CommunicationThread, Student, Subject, User)
        .join(Student, Student.id == CommunicationThread.student_id)
        .outerjoin(Subject, Subject.id == CommunicationThread.subject_id)
        .join(User, User.id == CommunicationThread.created_by)
        .filter(Student.is_test_account.is_(False))
    )
    if user.role in PORTAL_CREATOR_ROLES:
        query = query.filter(CommunicationThread.student_id == _linked_student(db, user).id)
    elif user.role == "faculty":
        assignments = _faculty_assignments(db, user.id)
        conditions = [
            and_(
                CommunicationThread.subject_id == assignment.subject_id,
                Enrollment.batch == batch.name,
                or_(
                    Enrollment.program == batch.program,
                    batch.program == "All programs",
                ),
            )
            for assignment, batch, _ in assignments
        ]
        if not conditions:
            return []
        query = query.join(
            Enrollment,
            and_(
                Enrollment.student_id == CommunicationThread.student_id,
                Enrollment.is_active.is_(True),
            ),
        ).filter(or_(*conditions))
    return query.order_by(CommunicationThread.updated_at.desc()).all()


def _last_messages(db: Session, thread_ids: list[str]):
    if not thread_ids:
        return {}
    rows = (
        db.query(CommunicationMessage, User)
        .join(User, User.id == CommunicationMessage.sender_id)
        .filter(CommunicationMessage.thread_id.in_(thread_ids))
        .order_by(CommunicationMessage.created_at.desc())
        .all()
    )
    latest = {}
    for message, sender in rows:
        latest.setdefault(message.thread_id, (message, sender))
    return latest


def _serialize_thread(row, last=None):
    thread, student, subject, creator = row
    last_message, last_sender = last or (None, None)
    return {
        "id": thread.id,
        "studentId": student.id,
        "studentName": student.full_name,
        "admissionNumber": student.admission_number,
        "subjectId": subject.id if subject else None,
        "subject": subject.name if subject else "Institute office",
        "topic": thread.topic,
        "status": thread.status,
        "originRole": creator.role,
        "originName": creator.full_name,
        "createdAt": thread.created_at,
        "updatedAt": thread.updated_at,
        "lastMessage": last_message.body if last_message else "",
        "lastMessageAt": last_message.created_at if last_message else thread.created_at,
        "lastSender": last_sender.full_name if last_sender else creator.full_name,
    }


def _serialize_messages(db: Session, thread_id: str):
    rows = (
        db.query(CommunicationMessage, User)
        .join(User, User.id == CommunicationMessage.sender_id)
        .filter(CommunicationMessage.thread_id == thread_id)
        .order_by(CommunicationMessage.created_at)
        .all()
    )
    return [{
        "id": message.id,
        "body": message.body,
        "senderId": sender.id,
        "senderName": sender.full_name,
        "senderRole": sender.role,
        "createdAt": message.created_at,
    } for message, sender in rows]


@router.get("/inbox")
def communication_inbox(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*CONVERSATION_ROLES)),
):
    rows = _thread_rows(db, user)
    latest = _last_messages(db, [thread.id for thread, *_ in rows])
    subjects = []
    if user.role in PORTAL_CREATOR_ROLES:
        subjects = _student_subjects(db, _linked_student(db, user).id)
    elif user.role == "faculty":
        seen = set()
        for _, _, subject in _faculty_assignments(db, user.id):
            if subject.id not in seen:
                subjects.append({"id": subject.id, "name": subject.name, "code": subject.code})
                seen.add(subject.id)
    return {
        "threads": [
            _serialize_thread(row, latest.get(row[0].id))
            for row in rows
        ],
        "subjects": subjects,
        "canCreate": user.role in PORTAL_CREATOR_ROLES,
        "canAnnounce": has_permission(db, user, "communication", "create"),
    }


@router.post("/threads", status_code=201)
def create_thread(
    payload: CommunicationThreadCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*PORTAL_CREATOR_ROLES)),
):
    topic = payload.topic.strip()
    body = payload.body.strip()
    if len(topic) < 2 or not body:
        raise HTTPException(422, "Topic and message are required")
    student = _linked_student(db, actor)
    if payload.subject_id:
        allowed_subjects = {
            item["id"] for item in _student_subjects(db, student.id)
        }
        if payload.subject_id not in allowed_subjects:
            raise HTTPException(403, "This subject is not available for the student's active batch")
    thread = CommunicationThread(
        student_id=student.id,
        subject_id=payload.subject_id,
        topic=topic,
        status="open",
        created_by=actor.id,
    )
    db.add(thread)
    db.flush()
    message = CommunicationMessage(
        thread_id=thread.id,
        sender_id=actor.id,
        body=body,
    )
    db.add(message)
    audit(
        db,
        actor,
        "communication.thread.create",
        "communication_thread",
        thread.id,
        after={
            "student_id": student.id,
            "subject_id": payload.subject_id,
            "origin_role": actor.role,
        },
    )
    db.commit()
    db.refresh(thread)
    subject = db.get(Subject, thread.subject_id) if thread.subject_id else None
    return {
        **_serialize_thread((thread, student, subject, actor), (message, actor)),
        "messages": _serialize_messages(db, thread.id),
    }


@router.get("/threads/{thread_id}")
def thread_detail(
    thread_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*CONVERSATION_ROLES)),
):
    thread = _thread_or_404(db, user, thread_id)
    row = (
        db.query(CommunicationThread, Student, Subject, User)
        .join(Student, Student.id == CommunicationThread.student_id)
        .outerjoin(Subject, Subject.id == CommunicationThread.subject_id)
        .join(User, User.id == CommunicationThread.created_by)
        .filter(CommunicationThread.id == thread.id)
        .one()
    )
    return {
        **_serialize_thread(row),
        "messages": _serialize_messages(db, thread.id),
        "canReply": thread.status == "open",
        "canClose": has_permission(db, user, "communication", "edit"),
    }


@router.post("/threads/{thread_id}/messages", status_code=201)
def reply_to_thread(
    thread_id: str,
    payload: CommunicationMessageCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*CONVERSATION_ROLES)),
):
    thread = _thread_or_404(db, actor, thread_id)
    if thread.status != "open":
        raise HTTPException(409, "This conversation is closed")
    body = payload.body.strip()
    if not body:
        raise HTTPException(422, "Message is required")
    message = CommunicationMessage(
        thread_id=thread.id,
        sender_id=actor.id,
        body=body,
    )
    thread.updated_at = datetime.now(timezone.utc)
    db.add(message)
    audit(
        db,
        actor,
        "communication.message.create",
        "communication_thread",
        thread.id,
        after={"sender_role": actor.role},
    )
    db.commit()
    return {
        "id": message.id,
        "body": message.body,
        "senderId": actor.id,
        "senderName": actor.full_name,
        "senderRole": actor.role,
        "createdAt": message.created_at,
    }


@router.patch("/threads/{thread_id}/status")
def update_thread_status(
    thread_id: str,
    payload: CommunicationThreadStatusUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ROLES)),
):
    thread = db.get(CommunicationThread, thread_id)
    if not thread:
        raise HTTPException(404, "Conversation not found")
    before = thread.status
    thread.status = payload.status
    thread.updated_at = datetime.now(timezone.utc)
    audit(
        db,
        actor,
        "communication.thread.status",
        "communication_thread",
        thread.id,
        before={"status": before},
        after={"status": thread.status},
    )
    db.commit()
    return {"id": thread.id, "status": thread.status, "updatedAt": thread.updated_at}


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
