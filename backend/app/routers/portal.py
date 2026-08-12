from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..operations_schemas import StudentAssignmentStatusUpdate
from ..models import (
    Assignment,
    AssignmentRecipient,
    AttendanceEntry,
    AttendancePeriodSummary,
    AttendanceRegister,
    Batch,
    ClassSession,
    DailyAttendanceEntry,
    Enrollment,
    Examination,
    ExaminationParticipant,
    ExaminationResult,
    FeeAgreement,
    Notice,
    ParentAccount,
    PaymentTransaction,
    Room,
    Student,
    StudentAccount,
    StudentSubjectSelection,
    Subject,
    User,
)
from ..security import require_roles
from ..services import payment_effect, received_effect
from ..services import audit

router = APIRouter(prefix="/api/portal", tags=["student portal"])
parent_router = APIRouter(prefix="/api/parent", tags=["parent portal"])


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _student_for_account(db: Session, model, user: User):
    latest_enrollment_id = (
        select(Enrollment.id)
        .where(Enrollment.student_id == Student.id)
        .order_by(
            Enrollment.is_active.desc(),
            Enrollment.created_at.desc(),
            Enrollment.id.desc(),
        )
        .limit(1)
        .correlate(Student)
        .scalar_subquery()
    )
    row = (
        db.query(model, Student, Enrollment)
        .join(Student, Student.id == model.student_id)
        .outerjoin(Enrollment, Enrollment.id == latest_enrollment_id)
        .filter(
            model.user_id == user.id,
            Student.is_test_account.is_(False),
            Student.status == "active",
        )
        .first()
    )
    if not row:
        raise HTTPException(403, "This account is not linked to a student record")
    return row


def schedule_rows(db: Session, student: Student, enrollment: Enrollment | None):
    if not enrollment or not enrollment.batch:
        return []
    selected_subjects = {
        name for name, in db.query(StudentSubjectSelection.subject_name)
        .filter(StudentSubjectSelection.student_id == student.id)
        .all()
    }
    query = (
        db.query(ClassSession, Batch, Subject, User, Room)
        .join(Batch, Batch.id == ClassSession.batch_id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .join(User, User.id == ClassSession.faculty_id)
        .join(Room, Room.id == ClassSession.room_id)
        .filter(
            Batch.name == enrollment.batch,
            or_(
                Batch.program == enrollment.program,
                Batch.program == "All programs",
            ),
            ClassSession.status == "scheduled",
        )
    )
    if selected_subjects:
        query = query.filter(Subject.name.in_(selected_subjects))
    rows = query.order_by(ClassSession.starts_at).all()
    return [{
        "id": session.id,
        "subject": subject.name,
        "subjectCode": subject.code,
        "faculty": faculty.full_name,
        "room": room.name,
        "startsAt": _aware(session.starts_at),
        "endsAt": _aware(session.ends_at),
    } for session, _, subject, faculty, room in rows]


def assignment_rows(
    db: Session,
    student: Student,
    enrollment: Enrollment | None,
):
    if not enrollment or not enrollment.batch:
        return []
    rows = (
        db.query(Assignment, Batch, Subject, AssignmentRecipient)
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
        .outerjoin(
            AssignmentRecipient,
            and_(
                AssignmentRecipient.assignment_id == Assignment.id,
                AssignmentRecipient.student_id == student.id,
            ),
        )
        .filter(
            Batch.name == enrollment.batch,
            or_(
                Batch.program == enrollment.program,
                Batch.program == "All programs",
            ),
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
        "dueAt": _aware(assignment.due_at),
        "externalUrl": assignment.external_url,
        "status": recipient.status if recipient else "published",
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
    class_rows = [{
        "sessionId": session.id,
        "subject": subject.name,
        "startsAt": _aware(session.starts_at),
        "dateLabel": None,
        "status": entry.status,
        "rawStatus": None,
        "reason": entry.reason,
        "source": "class_register",
    } for entry, _, session, subject in rows]
    manual = (
        db.query(AttendanceEntry, AttendanceRegister)
        .join(
            AttendanceRegister,
            AttendanceRegister.id == AttendanceEntry.register_id,
        )
        .filter(
            AttendanceEntry.student_id == student.id,
            AttendanceRegister.status == "submitted",
            AttendanceRegister.register_kind.in_(("manual", "biometric")),
        )
        .order_by(AttendanceRegister.attendance_date.desc())
        .all()
    )
    manual_rows = [{
        "sessionId": register.id,
        "subject": register.subject_name,
        "startsAt": register.attendance_date,
        "dateLabel": (
            register.attendance_date.isoformat()
            if register.attendance_date else None
        ),
        "status": entry.status,
        "rawStatus": None,
        "reason": entry.reason,
        "source": (
            "biometric_register"
            if register.register_kind == "biometric"
            else "manual_register"
        ),
    } for entry, register in manual]
    daily = (
        db.query(DailyAttendanceEntry)
        .filter_by(student_id=student.id)
        .order_by(
            DailyAttendanceEntry.attendance_date.desc(),
            DailyAttendanceEntry.source_column.desc(),
        )
        .all()
    )
    daily_rows = [{
        "sessionId": entry.id,
        "subject": "Daily attendance",
        "startsAt": entry.attendance_date,
        "dateLabel": entry.source_date_label,
        "status": entry.normalized_status or "unclassified",
        "rawStatus": entry.raw_status,
        "reason": "",
        "source": "imported_daily",
    } for entry in daily]
    return class_rows + manual_rows + daily_rows


def attendance_period_summary(db: Session, student: Student):
    row = (
        db.query(AttendancePeriodSummary)
        .filter(
            AttendancePeriodSummary.student_id == student.id,
            AttendancePeriodSummary.status == "confirmed",
        )
        .order_by(
            AttendancePeriodSummary.period_end.desc(),
            AttendancePeriodSummary.created_at.desc(),
        )
        .first()
    )
    if not row:
        return None
    return {
        "id": row.id,
        "batch": row.batch_name,
        "mentor": row.mentor_name,
        "periodStart": row.period_start,
        "periodEnd": row.period_end,
        "presentDays": row.present_days,
        "absentDays": row.absent_days,
        "workingDays": row.working_days,
        "attendanceRate": float(row.attendance_rate),
        "status": row.status,
        "source": row.source_name,
    }


def examination_rows(
    db: Session,
    student: Student,
    enrollment: Enrollment | None,
):
    if not enrollment or not enrollment.batch:
        return []
    rows = (
        db.query(Examination, Batch, Subject, User, ExaminationResult)
        .join(Batch, Batch.id == Examination.batch_id)
        .join(Subject, Subject.id == Examination.subject_id)
        .join(User, User.id == Examination.faculty_id)
        .outerjoin(
            ExaminationResult,
            and_(
                ExaminationResult.exam_id == Examination.id,
                ExaminationResult.student_id == student.id,
            ),
        )
        .join(
            ExaminationParticipant,
            and_(
                ExaminationParticipant.exam_id == Examination.id,
                ExaminationParticipant.student_id == student.id,
            ),
        )
        .filter(
            Examination.status.in_(("scheduled", "marks_entry", "published")),
        )
        .order_by(Examination.scheduled_at.desc())
        .all()
    )
    payload = []
    for exam, batch, subject, faculty, result in rows:
        published = exam.status == "published"
        marks = (
            float(result.marks_obtained)
            if published and result and result.marks_obtained is not None
            else None
        )
        percentage = (
            round(marks / float(exam.max_marks) * 100, 1)
            if marks is not None and exam.max_marks
            else None
        )
        payload.append({
            "id": exam.id,
            "name": exam.name,
            "batch": batch.name,
            "subject": subject.name,
            "subjectCode": subject.code,
            "faculty": faculty.full_name,
            "scheduledAt": _aware(exam.scheduled_at),
            "durationMinutes": exam.duration_minutes,
            "maxMarks": float(exam.max_marks),
            "passMarks": float(exam.pass_marks),
            "instructions": exam.instructions,
            "status": exam.status,
            "publishedAt": _aware(exam.published_at) if exam.published_at else None,
            "resultStatus": (
                result.result_status
                if published and result
                else "pending"
            ),
            "marksObtained": marks,
            "percentage": percentage,
            "qualified": (
                marks >= float(exam.pass_marks)
                if marks is not None
                else None
            ),
            "remarks": result.remarks if published and result else "",
        })
    return payload


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
            and_(
                Notice.audience == "batch",
                Batch.name == enrollment.batch,
                or_(
                    Batch.program == enrollment.program,
                    Batch.program == "All programs",
                ),
            ),
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
        "publishedAt": _aware(notice.published_at or notice.created_at),
    } for notice, batch in rows]


def fee_summary(db: Session, student: Student):
    latest_agreement_id = (
        select(FeeAgreement.id)
        .where(FeeAgreement.student_id == student.id)
        .order_by(FeeAgreement.created_at.desc(), FeeAgreement.id.desc())
        .limit(1)
        .scalar_subquery()
    )
    rows = (
        db.query(FeeAgreement, PaymentTransaction)
        .outerjoin(
            PaymentTransaction,
            and_(
                PaymentTransaction.fee_agreement_id == FeeAgreement.id,
                PaymentTransaction.student_id == student.id,
            ),
        )
        .filter(FeeAgreement.id == latest_agreement_id)
        .order_by(
            PaymentTransaction.transaction_date.desc(),
            PaymentTransaction.created_at.desc(),
        )
        .all()
    )
    if not rows:
        return {
            "agreedAmount": 0,
            "paidAmount": 0,
            "outstandingAmount": 0,
            "currency": "INR",
            "payments": [],
        }
    agreement = rows[0][0]
    transactions = [transaction for _, transaction in rows if transaction is not None]
    ledger_effect = sum(payment_effect(item) for item in transactions)
    paid = sum(received_effect(item) for item in transactions)
    return {
        "agreedAmount": agreement.agreed_amount,
        "paidAmount": max(0, paid),
        "outstandingAmount": max(0, agreement.agreed_amount - ledger_effect),
        "currency": agreement.currency,
        "payments": [{
            "id": item.id,
            "date": item.transaction_date,
            "amount": item.amount,
            "method": item.method,
            "status": item.status,
        } for item in transactions if item.transaction_type not in {"balance_credit", "balance_debit"}],
    }


def _student_profile(student: Student, enrollment: Enrollment | None):
    return {
        "id": student.id,
        "fullName": student.full_name,
        "admissionNumber": student.admission_number,
        "mobile": student.mobile,
        "secondaryMobile": student.secondary_mobile,
        "email": student.email,
        "program": enrollment.program if enrollment else None,
        "batch": enrollment.batch if enrollment else None,
    }


def _portal_payload(
    db: Session,
    student: Student,
    enrollment: Enrollment | None,
    notice_audience: str,
    include_finance: bool = False,
):
    schedule = schedule_rows(db, student, enrollment)
    assignments = assignment_rows(db, student, enrollment)
    attendance = attendance_rows(db, student)
    period_summary = attendance_period_summary(db, student)
    examinations = examination_rows(db, student, enrollment)
    notices = notice_rows(db, enrollment, notice_audience)
    now = datetime.now(timezone.utc)
    classified_attendance = [
        row for row in attendance if row["status"] != "unclassified"
    ]
    present = sum(
        1 for row in attendance
        if row["status"] in ("present", "late", "excused")
    )
    summary = {
        "upcomingClasses": sum(
            1 for row in schedule if _aware(row["startsAt"]) >= now
        ),
        "openAssignments": sum(
            1 for row in assignments if row["status"] != "completed"
        ),
        "upcomingExams": sum(
            1 for row in examinations
            if row["status"] == "scheduled"
            and _aware(row["scheduledAt"]) >= now
        ),
        "attendanceRate": (
            period_summary["attendanceRate"]
            if period_summary
            else round(present / len(classified_attendance) * 100, 1)
            if classified_attendance else None
        ),
    }
    payload = {
        "profile": _student_profile(student, enrollment),
        "summary": summary,
        "schedule": schedule,
        "assignments": assignments,
        "examinations": examinations,
        "attendance": attendance,
        "attendanceSummary": period_summary,
        "notices": notices,
    }
    if include_finance:
        fees = fee_summary(db, student)
        summary["outstandingAmount"] = fees["outstandingAmount"]
        payload["fees"] = fees
    return payload


@router.get("/bootstrap")
def student_bootstrap(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student", "parent_student")),
):
    _, student, enrollment = _student_for_account(db, StudentAccount, user)
    payload = _portal_payload(db, student, enrollment, "students")
    payload["account"] = {
        "id": user.id,
        "fullName": user.full_name,
        "mobile": user.mobile,
        "email": user.email,
    }
    return payload


@router.patch("/assignments/{assignment_id}/status")
def update_student_assignment_status(
    assignment_id: str,
    payload: StudentAssignmentStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student", "parent_student")),
):
    _, student, enrollment = _student_for_account(db, StudentAccount, user)
    if not enrollment or not enrollment.batch:
        raise HTTPException(404, "Assignment not found for this student")
    assignment = (
        db.query(Assignment)
        .join(Batch, Batch.id == Assignment.batch_id)
        .filter(
            Assignment.id == assignment_id,
            Assignment.status == "published",
            Batch.name == enrollment.batch,
            Batch.program == enrollment.program,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(404, "Assignment not found for this student")
    recipient = db.query(AssignmentRecipient).filter_by(
        assignment_id=assignment_id,
        student_id=student.id,
    ).first()
    previous_status = recipient.status if recipient else "published"
    if payload.status == previous_status:
        return {
            "assignmentId": assignment_id,
            "studentId": student.id,
            "status": payload.status,
        }
    if payload.status in {"viewed", "submitted", "completed"}:
        if recipient:
            recipient.status = payload.status
        else:
            recipient = AssignmentRecipient(
                assignment_id=assignment_id,
                student_id=student.id,
                status=payload.status,
            )
            db.add(recipient)
    elif recipient:
        db.delete(recipient)
    audit(
        db,
        user,
        "portal.assignment.status",
        "assignment_recipient",
        f"{assignment_id}:{student.id}",
        before={"status": previous_status},
        after={"status": payload.status},
    )
    db.commit()
    return {
        "assignmentId": assignment_id,
        "studentId": student.id,
        "status": payload.status,
    }


@parent_router.get("/bootstrap")
def parent_bootstrap(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("parent")),
):
    account, student, enrollment = _student_for_account(db, ParentAccount, user)
    payload = _portal_payload(
        db,
        student,
        enrollment,
        "parents",
        include_finance=True,
    )
    payload["account"] = {
        "id": user.id,
        "fullName": user.full_name,
        "mobile": user.mobile,
        "email": user.email,
        "contactType": account.contact_type,
    }
    return payload
