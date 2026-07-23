from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
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
    FeeAgreement,
    Notice,
    ParentAccount,
    PaymentTransaction,
    Room,
    Student,
    StudentAccount,
    Subject,
    User,
)
from ..security import require_roles

router = APIRouter(prefix="/api/portal", tags=["student portal"])
parent_router = APIRouter(prefix="/api/parent", tags=["parent portal"])


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _student_for_account(db: Session, model, user: User):
    account = db.query(model).filter_by(user_id=user.id).first()
    if not account:
        raise HTTPException(403, "This account is not linked to a student record")
    student = db.get(Student, account.student_id)
    if not student:
        raise HTTPException(404, "Student record not found")
    enrollment = (
        db.query(Enrollment)
        .filter_by(student_id=student.id, is_active=True)
        .order_by(Enrollment.created_at.desc())
        .first()
    )
    return account, student, enrollment


def schedule_rows(db: Session, enrollment: Enrollment | None):
    if not enrollment or not enrollment.batch:
        return []
    rows = (
        db.query(ClassSession, Batch, Subject, User, Room)
        .join(Batch, Batch.id == ClassSession.batch_id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .join(User, User.id == ClassSession.faculty_id)
        .join(Room, Room.id == ClassSession.room_id)
        .filter(Batch.name == enrollment.batch, ClassSession.status == "scheduled")
        .order_by(ClassSession.starts_at)
        .all()
    )
    return [{
        "id": session.id,
        "subject": subject.name,
        "subjectCode": subject.code,
        "faculty": faculty.full_name,
        "room": room.name,
        "startsAt": session.starts_at,
        "endsAt": session.ends_at,
    } for session, _, subject, faculty, room in rows]


def assignment_rows(db: Session, student: Student):
    rows = (
        db.query(Assignment, Batch, Subject, AssignmentRecipient)
        .join(AssignmentRecipient, AssignmentRecipient.assignment_id == Assignment.id)
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
        .filter(
            AssignmentRecipient.student_id == student.id,
            Assignment.status == "published",
        )
        .order_by(Assignment.due_at)
        .all()
    )
    return [{
        "id": assignment.id,
        "title": assignment.title,
        "instructions": assignment.instructions,
        "subject": subject.name,
        "batch": batch.name,
        "dueAt": assignment.due_at,
        "externalUrl": assignment.external_url,
        "status": recipient.status,
    } for assignment, batch, subject, recipient in rows]


def attendance_rows(db: Session, student: Student):
    rows = (
        db.query(AttendanceEntry, AttendanceRegister, ClassSession, Subject)
        .join(AttendanceRegister, AttendanceRegister.id == AttendanceEntry.register_id)
        .join(ClassSession, ClassSession.id == AttendanceRegister.class_session_id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .filter(
            AttendanceEntry.student_id == student.id,
            AttendanceRegister.status == "submitted",
        )
        .order_by(ClassSession.starts_at.desc())
        .all()
    )
    return [{
        "sessionId": session.id,
        "subject": subject.name,
        "startsAt": session.starts_at,
        "status": entry.status,
        "reason": entry.reason,
    } for entry, _, session, subject in rows]


def notice_rows(db: Session, enrollment: Enrollment | None, audience: str):
    direct_audiences = ("all", audience)
    query = (
        db.query(Notice, Batch)
        .outerjoin(Batch, Batch.id == Notice.batch_id)
        .filter(Notice.status == "published")
    )
    if enrollment and enrollment.batch:
        query = query.filter(or_(
            Notice.audience.in_(direct_audiences),
            and_(Notice.audience == "batch", Batch.name == enrollment.batch),
        ))
    else:
        query = query.filter(Notice.audience.in_(direct_audiences))
    rows = query.order_by(
        Notice.published_at.desc(),
        Notice.created_at.desc(),
    ).all()
    return [{
        "id": notice.id,
        "title": notice.title,
        "body": notice.body,
        "channel": notice.channel,
        "batch": batch.name if batch else None,
        "publishedAt": notice.published_at or notice.created_at,
    } for notice, batch in rows]


def fee_summary(db: Session, student: Student):
    agreement = (
        db.query(FeeAgreement)
        .filter_by(student_id=student.id)
        .order_by(FeeAgreement.created_at.desc())
        .first()
    )
    if not agreement:
        return {
            "agreedAmount": 0,
            "paidAmount": 0,
            "outstandingAmount": 0,
            "currency": "INR",
            "payments": [],
        }
    transactions = (
        db.query(PaymentTransaction)
        .filter_by(student_id=student.id, fee_agreement_id=agreement.id)
        .order_by(
            PaymentTransaction.transaction_date.desc(),
            PaymentTransaction.created_at.desc(),
        )
        .all()
    )
    paid = sum(
        item.amount
        for item in transactions
        if item.transaction_type == "payment" and item.status != "void"
    )
    adjustments = sum(
        item.amount
        for item in transactions
        if item.transaction_type in ("adjustment", "reversal") and item.status != "void"
    )
    return {
        "agreedAmount": agreement.agreed_amount,
        "paidAmount": max(0, paid + adjustments),
        "outstandingAmount": max(0, agreement.agreed_amount - paid - adjustments),
        "currency": agreement.currency,
        "payments": [{
            "id": item.id,
            "date": item.transaction_date,
            "amount": item.amount,
            "method": item.method,
            "status": item.status,
        } for item in transactions],
    }


def _student_profile(student: Student, enrollment: Enrollment | None):
    return {
        "id": student.id,
        "fullName": student.full_name,
        "admissionNumber": student.admission_number,
        "mobile": student.mobile,
        "email": student.email,
        "program": enrollment.program if enrollment else None,
        "batch": enrollment.batch if enrollment else None,
    }


def _portal_payload(
    db: Session,
    student: Student,
    enrollment: Enrollment | None,
    notice_audience: str,
):
    schedule = schedule_rows(db, enrollment)
    assignments = assignment_rows(db, student)
    attendance = attendance_rows(db, student)
    notices = notice_rows(db, enrollment, notice_audience)
    fees = fee_summary(db, student)
    now = datetime.now(timezone.utc)
    present = sum(
        1 for row in attendance
        if row["status"] in ("present", "late", "excused")
    )
    return {
        "profile": _student_profile(student, enrollment),
        "summary": {
            "upcomingClasses": sum(
                1 for row in schedule if _aware(row["startsAt"]) >= now
            ),
            "openAssignments": sum(
                1 for row in assignments if _aware(row["dueAt"]) >= now
            ),
            "attendanceRate": (
                round(present / len(attendance) * 100, 1)
                if attendance else None
            ),
            "outstandingAmount": fees["outstandingAmount"],
        },
        "schedule": schedule,
        "assignments": assignments,
        "attendance": attendance,
        "notices": notices,
        "fees": fees,
    }


@router.get("/bootstrap")
def student_bootstrap(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student", "parent_student")),
):
    _, student, enrollment = _student_for_account(db, StudentAccount, user)
    return _portal_payload(db, student, enrollment, "students")


@parent_router.get("/bootstrap")
def parent_bootstrap(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("parent")),
):
    account, student, enrollment = _student_for_account(db, ParentAccount, user)
    payload = _portal_payload(db, student, enrollment, "parents")
    payload["account"] = {
        "id": user.id,
        "fullName": user.full_name,
        "email": user.email,
        "contactType": account.contact_type,
    }
    return payload
