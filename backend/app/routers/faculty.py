from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Assignment,
    AssignmentRecipient,
    Batch,
    ClassSession,
    FacultyTeachingAssignment,
    Notice,
    RevokedToken,
    Room,
    Subject,
    User,
)
from ..assignment_materials import material_maps, serialize_material
from ..schemas import FacultyMobileActivationRequest
from ..security import bearer, current_user, decode_token, hash_password, require_roles, verify_password
from ..services import SubjectRosterResolver, audit
from .examinations import _exam_rows, _serialize_many

router = APIRouter(prefix="/api/faculty", tags=["faculty portal"])
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


FACULTY_DISPLAY_NAMES_BY_MOBILE = {
    "9325511100": "Meet K.",
    "9923057717": "Anita B.",
    "9156376488": "Kajal D.",
}


def _faculty_display_name(full_name: str, mobile: str | None = None) -> str:
    if mobile and mobile in FACULTY_DISPLAY_NAMES_BY_MOBILE:
        return FACULTY_DISPLAY_NAMES_BY_MOBILE[mobile]
    honorifics = {
        "dr", "prof", "professor", "mr", "mrs", "ms", "miss",
        "sir", "maam", "mam", "madam",
    }
    parts = [
        part.strip(". ,'")
        for part in full_name.split()
        if part.strip(". ,'").casefold() not in honorifics
    ]
    if not parts:
        return "Faculty"
    return parts[0] if len(parts) == 1 else f"{parts[0]} {parts[-1][0].upper()}."


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
        .join(
            FacultyTeachingAssignment,
            and_(
                FacultyTeachingAssignment.faculty_id == ClassSession.faculty_id,
                FacultyTeachingAssignment.batch_id == ClassSession.batch_id,
                FacultyTeachingAssignment.subject_id == ClassSession.subject_id,
                FacultyTeachingAssignment.is_active.is_(True),
            ),
        )
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
    roster = SubjectRosterResolver(db)

    def roster_count(batch, subject):
        return roster.count_for(batch, subject)

    sessions = []
    pair_candidates = [{
            "assignmentId": assignment.id,
            "batchId": batch.id,
            "batch": batch.name,
            "program": batch.program,
            "subjectId": subject.id,
            "subject": subject.name,
            "subjectCode": subject.code,
            "studentCount": roster_count(batch, subject),
        }
        for assignment, batch, subject in teaching_assignment_rows]
    aggregate_groups = {
        (pair["batch"], pair["subjectId"])
        for pair in pair_candidates
        if pair["program"] == "All programs"
    }
    teaching_pairs = {
        (pair["batchId"], pair["subjectId"]): pair
        for pair in pair_candidates
        if (
            pair["program"] == "All programs"
            or (pair["batch"], pair["subjectId"]) not in aggregate_groups
        )
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
            "studentCount": roster_count(batch, subject),
        })
    assignment_rows = (
        db.query(Assignment, Batch, Subject)
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
        .join(
            FacultyTeachingAssignment,
            and_(
                FacultyTeachingAssignment.faculty_id == faculty_user.id,
                FacultyTeachingAssignment.batch_id == Assignment.batch_id,
                FacultyTeachingAssignment.subject_id == Assignment.subject_id,
                FacultyTeachingAssignment.is_active.is_(True),
            ),
        )
        .filter(Assignment.created_by == faculty_user.id)
        .order_by(Assignment.due_at.desc())
        .all()
    )
    assignment_ids = [assignment.id for assignment, _, _ in assignment_rows]
    materials, downloaded_counts = material_maps(db, assignment_ids)
    eligible_by_assignment = {
        assignment.id: roster.student_ids_for(batch, subject)
        for assignment, batch, subject in assignment_rows
    }
    progress: dict[str, dict[str, int]] = {}
    if assignment_ids:
        for assignment_id, student_id, status in (
            db.query(
                AssignmentRecipient.assignment_id,
                AssignmentRecipient.student_id,
                AssignmentRecipient.status,
            )
            .filter(AssignmentRecipient.assignment_id.in_(assignment_ids))
            .all()
        ):
            if student_id not in eligible_by_assignment.get(assignment_id, set()):
                continue
            statuses = progress.setdefault(assignment_id, {})
            statuses[status] = statuses.get(status, 0) + 1
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
        "recipientCount": len(eligible_by_assignment[assignment.id]),
        "progress": {
            "notStarted": max(
                0,
                len(eligible_by_assignment[assignment.id])
                - sum(progress.get(assignment.id, {}).values()),
            ),
            "viewed": progress.get(assignment.id, {}).get("viewed", 0),
            "submitted": progress.get(assignment.id, {}).get("submitted", 0),
            "completed": progress.get(assignment.id, {}).get("completed", 0),
            "downloaded": downloaded_counts.get(assignment.id, 0),
        },
        "material": serialize_material(
            materials.get(assignment.id),
            downloaded_count=downloaded_counts.get(assignment.id, 0),
        ),
        "createdAt": _aware(assignment.created_at),
    } for assignment, batch, subject in assignment_rows]

    assigned_batch_ids = {pair["batchId"] for pair in teaching_pairs.values()}
    assigned_subject_pairs = {
        (pair["batchId"], pair["subjectId"])
        for pair in teaching_pairs.values()
    }
    notice_filter = Notice.audience.in_(("all", "faculty"))
    if assigned_batch_ids:
        notice_filter = or_(
            notice_filter,
            and_(
                Notice.audience == "batch",
                Notice.batch_id.in_(assigned_batch_ids),
            ),
            *[
                and_(
                    Notice.audience == "subject",
                    Notice.batch_id == batch_id,
                    Notice.subject_id == subject_id,
                )
                for batch_id, subject_id in assigned_subject_pairs
            ],
        )
    notice_rows = (
        db.query(Notice, Batch, Subject)
        .outerjoin(Batch, Batch.id == Notice.batch_id)
        .outerjoin(Subject, Subject.id == Notice.subject_id)
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
        "subject": subject.name if subject else None,
        "publishedAt": _aware(notice.published_at or notice.created_at),
    } for notice, batch, subject in notice_rows]

    today_sessions = [
        row for row in sessions
        if (
            row["status"] == "scheduled"
            and _aware(row["startsAt"]) < tomorrow_start
            and _aware(row["endsAt"]) >= today_start
        )
    ]
    local_now = now.astimezone(INDIA_TZ)
    days_until_monday = (7 - local_now.weekday()) % 7 if local_now.weekday() == 6 else -local_now.weekday()
    working_week_start_date = local_now.date() + timedelta(days=days_until_monday)
    working_week_start = datetime.combine(
        working_week_start_date,
        time.min,
        tzinfo=INDIA_TZ,
    ).astimezone(timezone.utc)
    working_week_end = working_week_start + timedelta(days=6)
    week_sessions = [
        row for row in sessions
        if (
            row["status"] == "scheduled"
            and working_week_start <= _aware(row["startsAt"]) < working_week_end
        )
    ]
    week_teaching_days = {
        _aware(row["startsAt"]).astimezone(INDIA_TZ).date()
        for row in week_sessions
    }
    open_assignments = [
        row for row in assignments
        if _aware(row["dueAt"]) >= now and row["status"] == "published"
    ]

    return {
        "profile": {
            "id": faculty_user.id,
            "fullName": faculty_user.full_name,
            "displayName": _faculty_display_name(
                faculty_user.full_name,
                faculty_user.mobile,
            ),
            "mobile": faculty_user.mobile,
            "email": faculty_user.email,
            "role": faculty_user.role,
        },
        "summary": {
            "todayClasses": len(today_sessions),
            "weekTeachingDays": len(week_teaching_days),
            "workingDays": 6,
            "workingWeekStartsAt": working_week_start,
            "workingWeekEndsAt": working_week_end,
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
