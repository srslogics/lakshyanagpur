from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Assignment,
    AssignmentRecipient,
    AttendanceEntry,
    AttendanceRegister,
    Batch,
    ClassSession,
    Enrollment,
    Notice,
    Room,
    Subject,
    User,
)
from ..security import require_roles

router = APIRouter(prefix="/api/faculty", tags=["faculty portal"])
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


@router.get("/bootstrap")
def bootstrap(
    db: Session = Depends(get_db),
    faculty_user: User = Depends(require_roles("faculty")),
):
    session_rows = (
        db.query(ClassSession, Batch, Subject, Room, AttendanceRegister)
        .join(Batch, Batch.id == ClassSession.batch_id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .join(Room, Room.id == ClassSession.room_id)
        .outerjoin(AttendanceRegister, AttendanceRegister.class_session_id == ClassSession.id)
        .filter(ClassSession.faculty_id == faculty_user.id)
        .order_by(ClassSession.starts_at)
        .all()
    )

    batch_names = {batch.name for _, batch, _, _, _ in session_rows}
    student_counts = dict(
        db.query(Enrollment.batch, func.count(func.distinct(Enrollment.student_id)))
        .filter(Enrollment.is_active.is_(True), Enrollment.batch.in_(batch_names))
        .group_by(Enrollment.batch)
        .all()
    ) if batch_names else {}

    sessions = []
    teaching_pairs = {}
    now = datetime.now(timezone.utc)
    today = now.astimezone(INDIA_TZ).date()
    for session, batch, subject, room, register in session_rows:
        marked_count = (
            db.query(AttendanceEntry)
            .filter_by(register_id=register.id)
            .count()
            if register
            else 0
        )
        sessions.append({
            "id": session.id,
            "batchId": batch.id,
            "batch": batch.name,
            "program": batch.program,
            "subjectId": subject.id,
            "subject": subject.name,
            "subjectCode": subject.code,
            "room": room.name,
            "startsAt": session.starts_at,
            "endsAt": session.ends_at,
            "status": session.status,
            "notes": session.notes,
            "registerStatus": register.status if register else "not_started",
            "studentCount": student_counts.get(batch.name, 0),
            "markedCount": marked_count,
        })
        teaching_pairs[(batch.id, subject.id)] = {
            "batchId": batch.id,
            "batch": batch.name,
            "program": batch.program,
            "subjectId": subject.id,
            "subject": subject.name,
            "subjectCode": subject.code,
            "studentCount": student_counts.get(batch.name, 0),
        }

    recipient_counts = (
        db.query(
            AssignmentRecipient.assignment_id,
            func.count(AssignmentRecipient.student_id).label("recipients"),
        )
        .group_by(AssignmentRecipient.assignment_id)
        .subquery()
    )
    assignment_rows = (
        db.query(Assignment, Batch, Subject, func.coalesce(recipient_counts.c.recipients, 0))
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
        .outerjoin(recipient_counts, recipient_counts.c.assignment_id == Assignment.id)
        .filter(Assignment.created_by == faculty_user.id)
        .order_by(Assignment.due_at.desc())
        .all()
    )
    assignments = [{
        "id": assignment.id,
        "title": assignment.title,
        "instructions": assignment.instructions,
        "batchId": batch.id,
        "batch": batch.name,
        "subjectId": subject.id,
        "subject": subject.name,
        "dueAt": assignment.due_at,
        "externalUrl": assignment.external_url,
        "status": assignment.status,
        "recipientCount": recipients,
        "createdAt": assignment.created_at,
    } for assignment, batch, subject, recipients in assignment_rows]

    assigned_batch_ids = {pair["batchId"] for pair in teaching_pairs.values()}
    notice_filter = Notice.audience.in_(("all", "faculty"))
    if assigned_batch_ids:
        notice_filter = or_(
            notice_filter,
            and_(
                Notice.audience == "batch",
                Notice.batch_id.in_(assigned_batch_ids),
            ),
        )
    notice_rows = (
        db.query(Notice, Batch)
        .outerjoin(Batch, Batch.id == Notice.batch_id)
        .filter(Notice.status == "published", notice_filter)
        .order_by(Notice.published_at.desc(), Notice.created_at.desc())
        .all()
    )
    notices = [{
        "id": notice.id,
        "title": notice.title,
        "body": notice.body,
        "audience": notice.audience,
        "batch": batch.name if batch else None,
        "publishedAt": notice.published_at or notice.created_at,
    } for notice, batch in notice_rows]

    today_sessions = [
        row for row in sessions
        if (
            row["status"] == "scheduled"
            and _aware(row["startsAt"]).astimezone(INDIA_TZ).date() == today
        )
    ]
    attendance_actions = [
        row for row in sessions
        if (
            row["status"] == "scheduled"
            and _aware(row["startsAt"]) <= now
            and row["registerStatus"] != "submitted"
        )
    ]
    open_assignments = [
        row for row in assignments
        if _aware(row["dueAt"]) >= now and row["status"] == "published"
    ]

    return {
        "profile": {
            "id": faculty_user.id,
            "fullName": faculty_user.full_name,
            "email": faculty_user.email,
            "role": faculty_user.role,
        },
        "summary": {
            "todayClasses": len(today_sessions),
            "attendanceActions": len(attendance_actions),
            "openAssignments": len(open_assignments),
            "activeBatches": len({pair["batchId"] for pair in teaching_pairs.values()}),
        },
        "sessions": sessions,
        "teachingPairs": sorted(
            teaching_pairs.values(),
            key=lambda item: (item["batch"], item["subject"]),
        ),
        "assignments": assignments,
        "notices": notices,
    }
