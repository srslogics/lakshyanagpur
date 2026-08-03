from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Assignment,
    Batch,
    ClassSession,
    Enrollment,
    FacultyTeachingAssignment,
    Notice,
    RevokedToken,
    Room,
    Subject,
    User,
)
from ..schemas import FacultyMobileActivationRequest
from ..security import bearer, current_user, decode_token, hash_password, require_roles, verify_password
from ..services import audit
from .examinations import _exam_rows, _serialize_many

router = APIRouter(prefix="/api/faculty", tags=["faculty portal"])
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


@router.post("/activate-mobile")
def activate_mobile(
    payload: FacultyMobileActivationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
    faculty_user: User = Depends(current_user),
):
    if faculty_user.role != "faculty":
        raise HTTPException(403, "You do not have permission to perform this action")
    if faculty_user.mobile:
        raise HTTPException(409, "A mobile number is already registered for this account")
    if db.query(User).filter(User.mobile == payload.mobile, User.id != faculty_user.id).first():
        raise HTTPException(409, "This mobile number is already assigned to another account")
    if verify_password(payload.new_password, faculty_user.password_hash):
        raise HTTPException(400, "Choose a personal password different from the temporary password")
    faculty_user.mobile = payload.mobile
    faculty_user.password_hash = hash_password(payload.new_password)
    faculty_user.must_change_password = False
    faculty_user.token_version += 1
    token = decode_token(credentials.credentials)
    expires_at = datetime.fromtimestamp(token["exp"], timezone.utc)
    db.add(RevokedToken(id=token["jti"], user_id=faculty_user.id, expires_at=expires_at))
    audit(
        db,
        faculty_user,
        "faculty.mobile.activate",
        "user",
        faculty_user.id,
        after={"mobile": payload.mobile, "mustChangePassword": False},
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            409,
            "This mobile number is already assigned to another account",
        ) from error
    return {
        "id": faculty_user.id,
        "fullName": faculty_user.full_name,
        "mobile": faculty_user.mobile,
        "email": faculty_user.email,
        "role": faculty_user.role,
    }


@router.get("/bootstrap")
def bootstrap(
    db: Session = Depends(get_db),
    faculty_user: User = Depends(require_roles("faculty")),
):
    session_rows = (
        db.query(
            ClassSession,
            Batch,
            Subject,
            Room,
        )
        .join(Batch, Batch.id == ClassSession.batch_id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .join(Room, Room.id == ClassSession.room_id)
        .filter(ClassSession.faculty_id == faculty_user.id)
        .order_by(ClassSession.starts_at)
        .all()
    )

    teaching_assignment_rows = (
        db.query(FacultyTeachingAssignment, Batch, Subject)
        .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
        .join(Subject, Subject.id == FacultyTeachingAssignment.subject_id)
        .filter(
            FacultyTeachingAssignment.faculty_id == faculty_user.id,
            FacultyTeachingAssignment.is_active.is_(True),
        )
        .order_by(Batch.name, Subject.name)
        .all()
    )
    batch_names = {
        batch.name
        for _, batch, _ in teaching_assignment_rows
    } | {
        batch.name
        for _, batch, _, _ in session_rows
    }
    student_count_rows = (
        db.query(
            Enrollment.batch,
            Enrollment.program,
            func.count(func.distinct(Enrollment.student_id)),
        )
        .filter(Enrollment.is_active.is_(True), Enrollment.batch.in_(batch_names))
        .group_by(Enrollment.batch, Enrollment.program)
        .all()
    ) if batch_names else []
    student_counts = {
        (batch_name, program): count
        for batch_name, program, count in student_count_rows
    }
    batch_totals = {
        batch_name: count
        for batch_name, count in (
            db.query(
                Enrollment.batch,
                func.count(func.distinct(Enrollment.student_id)),
            )
            .filter(
                Enrollment.is_active.is_(True),
                Enrollment.batch.in_(batch_names),
            )
            .group_by(Enrollment.batch)
            .all()
        )
    } if batch_names else {}

    def roster_count(batch):
        if batch.program == "All programs":
            return batch_totals.get(batch.name, 0)
        return student_counts.get((batch.name, batch.program), 0)

    sessions = []
    teaching_pairs = {
        (batch.id, subject.id): {
            "assignmentId": assignment.id,
            "batchId": batch.id,
            "batch": batch.name,
            "program": batch.program,
            "subjectId": subject.id,
            "subject": subject.name,
            "subjectCode": subject.code,
            "studentCount": roster_count(batch),
        }
        for assignment, batch, subject in teaching_assignment_rows
    }
    now = datetime.now(timezone.utc)
    today = now.astimezone(INDIA_TZ).date()
    today_start = datetime.combine(today, time.min, tzinfo=INDIA_TZ).astimezone(timezone.utc)
    tomorrow_start = today_start + timedelta(days=1)
    for session, batch, subject, room in session_rows:
        sessions.append({
            "id": session.id,
            "batchId": batch.id,
            "batch": batch.name,
            "program": batch.program,
            "subjectId": subject.id,
            "subject": subject.name,
            "subjectCode": subject.code,
            "room": room.name,
            "startsAt": _aware(session.starts_at),
            "endsAt": _aware(session.ends_at),
            "status": session.status,
            "notes": session.notes,
            "studentCount": roster_count(batch),
        })
    assignment_rows = (
        db.query(Assignment, Batch, Subject)
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
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
        "dueAt": _aware(assignment.due_at),
        "externalUrl": assignment.external_url,
        "status": assignment.status,
        "recipientCount": roster_count(batch),
        "createdAt": _aware(assignment.created_at),
    } for assignment, batch, subject in assignment_rows]

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
        "publishedAt": _aware(notice.published_at or notice.created_at),
    } for notice, batch in notice_rows]

    today_sessions = [
        row for row in sessions
        if (
            row["status"] == "scheduled"
            and _aware(row["startsAt"]) < tomorrow_start
            and _aware(row["endsAt"]) >= today_start
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
            "mobile": faculty_user.mobile,
            "email": faculty_user.email,
            "role": faculty_user.role,
        },
        "summary": {
            "todayClasses": len(today_sessions),
            "openAssignments": len(open_assignments),
            "activeBatches": len({pair["batchId"] for pair in teaching_pairs.values()}),
        },
        "sessions": sessions,
        "teachingPairs": sorted(
            teaching_pairs.values(),
            key=lambda item: (item["batch"], item["subject"]),
        ),
        "assignments": assignments,
        "examinations": _serialize_many(db, _exam_rows(db, faculty_user)),
        "notices": notices,
    }
