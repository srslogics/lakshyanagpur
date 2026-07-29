import csv
from datetime import date, datetime, timedelta, timezone
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Assignment,
    AttendanceEntry,
    AttendanceRegister,
    AuditLog,
    ClassSession,
    DailyAttendanceEntry,
    Enrollment,
    FeeAgreement,
    Lead,
    Notice,
    PaymentTransaction,
    Student,
    User,
)
from ..security import require_roles
from ..services import payment_effect

router = APIRouter(prefix="/api/reports", tags=["reports"])
REPORT_ROLES = ("owner", "accounts", "academic_coordinator")


def _safe_csv_cell(value):
    """Prevent exported user data from becoming a spreadsheet formula."""
    if value is None:
        return ""
    text = str(value)
    if text.startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


def _csv_download(filename: str, headings: list[str], rows):
    output = StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headings)
    for row in rows:
        writer.writerow([_safe_csv_cell(value) for value in row])
    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
    )
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*REPORT_ROLES)),
):
    now = datetime.now(timezone.utc)
    lead_rows = db.query(Lead.stage, func.count(Lead.id)).group_by(Lead.stage).all()
    attendance_rows = db.query(AttendanceEntry.status, func.count()).group_by(AttendanceEntry.status).all()
    attendance = {status: count for status, count in attendance_rows}
    daily_rows = (
        db.query(DailyAttendanceEntry.normalized_status, func.count())
        .group_by(DailyAttendanceEntry.normalized_status)
        .all()
    )
    for status, count in daily_rows:
        key = status or "unclassified"
        attendance[key] = attendance.get(key, 0) + count
    attendance_total = sum(
        count for status, count in attendance.items() if status != "unclassified"
    )
    paid = sum(payment_effect(row) for row in db.query(PaymentTransaction).all())
    recent = db.query(AuditLog, User).outerjoin(User, User.id == AuditLog.actor_id).order_by(AuditLog.created_at.desc()).limit(10).all()
    return {
        "metrics": {
            "students": db.query(Student).count(),
            "activeUsers": db.query(User).filter(User.is_active.is_(True)).count(),
            "scheduledClasses": db.query(ClassSession).filter(ClassSession.starts_at >= now).count(),
            "publishedNotices": db.query(Notice).filter_by(status="published").count(),
            "assignments": db.query(Assignment).count(),
            "overdueAssignments": db.query(Assignment).filter(Assignment.status == "published", Assignment.due_at < now).count(),
            "recordedPayments": paid,
            "attendanceRate": round(((attendance_total - attendance.get("absent", 0)) / attendance_total * 100), 1) if attendance_total else None,
        },
        "leadFunnel": [{"stage": stage, "count": count} for stage, count in lead_rows],
        "attendance": [{"status": status, "count": count} for status, count in sorted(attendance.items())],
        "recentAudit": [{"id": log.id, "action": log.action, "entityType": log.entity_type, "actor": actor.full_name if actor else "System", "createdAt": log.created_at} for log, actor in recent],
    }


@router.get("/exports")
def available_exports(
    user: User = Depends(require_roles(*REPORT_ROLES)),
):
    return [
        {
            "id": "students",
            "label": "Student register",
            "description": "Admissions, enrolment, contact and status records.",
        },
        {
            "id": "fees",
            "label": "Fee balances",
            "description": "Agreed, received and outstanding amounts by student.",
        },
        {
            "id": "attendance",
            "label": "Attendance entries",
            "description": "Submitted class, manual and imported attendance.",
        },
        {
            "id": "audit",
            "label": "Audit trail",
            "description": "Who changed which ERP record and when.",
        },
    ]


@router.get("/export/{report_name}")
def export_report(
    report_name: str,
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*REPORT_ROLES)),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "'from' date must be on or before 'to' date")
    stamp = datetime.now(timezone.utc).date().isoformat()
    if report_name == "students":
        enrollment_rows = {
            row.student_id: row
            for row in (
                db.query(Enrollment)
                .filter(Enrollment.is_active.is_(True))
                .order_by(Enrollment.created_at.desc())
                .all()
            )
        }
        students = db.query(Student).order_by(Student.full_name).all()
        return _csv_download(
            f"lakshya-students-{stamp}.csv",
            [
                "Admission number",
                "Student",
                "Mobile",
                "Secondary mobile",
                "Email",
                "Program",
                "Batch",
                "Enrolment date",
                "Status",
                "Data quality",
            ],
            (
                (
                    student.admission_number,
                    student.full_name,
                    student.mobile,
                    student.secondary_mobile,
                    student.email,
                    enrollment_rows.get(student.id).program
                    if enrollment_rows.get(student.id)
                    else "",
                    enrollment_rows.get(student.id).batch
                    if enrollment_rows.get(student.id)
                    else "",
                    enrollment_rows.get(student.id).enrollment_date
                    if enrollment_rows.get(student.id)
                    else "",
                    student.status,
                    student.data_quality_status,
                )
                for student in students
            ),
        )
    if report_name == "fees":
        agreements = (
            db.query(FeeAgreement, Student)
            .join(Student, Student.id == FeeAgreement.student_id)
            .order_by(Student.full_name, FeeAgreement.created_at.desc())
            .all()
        )
        effects: dict[str, int] = {}
        for transaction in db.query(PaymentTransaction).all():
            effects[transaction.fee_agreement_id] = (
                effects.get(transaction.fee_agreement_id, 0)
                + payment_effect(transaction)
            )
        return _csv_download(
            f"lakshya-fee-balances-{stamp}.csv",
            [
                "Admission number",
                "Student",
                "Agreed fee",
                "Received",
                "Outstanding",
                "Currency",
                "Agreement status",
            ],
            (
                (
                    student.admission_number,
                    student.full_name,
                    agreement.agreed_amount,
                    max(0, effects.get(agreement.id, 0)),
                    max(
                        0,
                        agreement.agreed_amount
                        - effects.get(agreement.id, 0),
                    ),
                    agreement.currency,
                    agreement.status,
                )
                for agreement, student in agreements
            ),
        )
    if report_name == "attendance":
        submitted = (
            db.query(
                AttendanceEntry,
                AttendanceRegister,
                ClassSession,
                Student,
            )
            .join(
                AttendanceRegister,
                AttendanceRegister.id == AttendanceEntry.register_id,
            )
            .outerjoin(
                ClassSession,
                ClassSession.id == AttendanceRegister.class_session_id,
            )
            .join(Student, Student.id == AttendanceEntry.student_id)
            .filter(AttendanceRegister.status == "submitted")
            .all()
        )
        rows = []
        for entry, register, session, student in submitted:
            attendance_date = register.attendance_date or (
                session.starts_at.date() if session else None
            )
            if date_from and attendance_date and attendance_date < date_from:
                continue
            if date_to and attendance_date and attendance_date > date_to:
                continue
            rows.append(
                (
                    attendance_date,
                    student.admission_number,
                    student.full_name,
                    register.batch_name,
                    register.stream_name,
                    register.subject_name,
                    entry.status,
                    entry.reason,
                    register.register_kind,
                )
            )
        daily_query = (
            db.query(DailyAttendanceEntry, Student)
            .join(Student, Student.id == DailyAttendanceEntry.student_id)
        )
        if date_from:
            daily_query = daily_query.filter(
                DailyAttendanceEntry.attendance_date >= date_from
            )
        if date_to:
            daily_query = daily_query.filter(
                DailyAttendanceEntry.attendance_date <= date_to
            )
        rows.extend(
            (
                entry.attendance_date or entry.source_date_label,
                student.admission_number,
                student.full_name,
                entry.batch_name,
                "",
                "Daily attendance",
                entry.normalized_status or "unclassified",
                entry.raw_status,
                "imported",
            )
            for entry, student in daily_query.all()
        )
        rows.sort(key=lambda item: (str(item[0]), item[2]), reverse=True)
        return _csv_download(
            f"lakshya-attendance-{stamp}.csv",
            [
                "Date",
                "Admission number",
                "Student",
                "Batch",
                "Program",
                "Subject",
                "Status",
                "Reason / source value",
                "Source",
            ],
            rows,
        )
    if report_name == "audit":
        query = (
            db.query(AuditLog, User)
            .outerjoin(User, User.id == AuditLog.actor_id)
            .order_by(AuditLog.created_at.desc())
        )
        if date_from:
            query = query.filter(
                AuditLog.created_at
                >= datetime.combine(date_from, datetime.min.time()).replace(
                    tzinfo=timezone.utc,
                )
            )
        if date_to:
            query = query.filter(
                AuditLog.created_at
                < datetime.combine(date_to, datetime.min.time()).replace(
                    tzinfo=timezone.utc,
                )
                + timedelta(days=1)
            )
        return _csv_download(
            f"lakshya-audit-{stamp}.csv",
            [
                "Timestamp",
                "Actor",
                "Role",
                "Action",
                "Record type",
                "Record ID",
            ],
            (
                (
                    log.created_at,
                    actor.full_name if actor else "System",
                    actor.role if actor else "",
                    log.action,
                    log.entity_type,
                    log.entity_id,
                )
                for log, actor in query.all()
            ),
        )
    raise HTTPException(404, "Report export not found")
