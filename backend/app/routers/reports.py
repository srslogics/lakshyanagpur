import csv
from datetime import date, datetime, timedelta, timezone
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Assignment,
    AttendanceEntry,
    AttendancePeriodSummary,
    AttendanceRegister,
    AuditLog,
    Batch,
    ClassSession,
    DailyAttendanceEntry,
    Enrollment,
    FeeAgreement,
    Lead,
    Notice,
    PaymentTransaction,
    Student,
    Subject,
    User,
)
from ..security import require_roles
from ..services import payment_effect, received_effect
from ..report_downloads import IST, excel_download, local_datetime
from ..report_catalog import REPORTS, REPORT_BY_ID, detailed_sheets, student_supporting_sheets
from ..permissions import effective_permissions, has_permission
from ..payroll import month_bounds

router = APIRouter(prefix="/api/reports", tags=["reports"])
REPORT_ROLES = ("owner", "accounts", "academic_coordinator")


def _available_reports(db, user):
    permissions = effective_permissions(db, user)
    return [item for item in REPORTS if permissions.get(item["module"], {}).get("read")]


def _safe_csv_cell(value):
    """Prevent exported user data from becoming a spreadsheet formula."""
    if value is None:
        return ""
    text = str(value)
    if isinstance(value, str) and text.lstrip().startswith(("=", "+", "-", "@")):
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
    response.headers["Cache-Control"] = "no-store"
    return response


def _report_download(filename, headings, rows, export_format, title, scope, sheets=None, additional_sheets=None):
    if export_format == "xlsx":
        return excel_download(filename.removesuffix(".csv") + ".xlsx", (sheets or [(title, headings, rows, scope)]) + (additional_sheets or []))
    return _csv_download(filename, headings, rows)


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*REPORT_ROLES)),
):
    now = datetime.now(timezone.utc)
    lead_rows = db.query(Lead.stage, func.count(Lead.id)).group_by(Lead.stage).all()
    latest_period_end = db.query(func.max(AttendancePeriodSummary.period_end)).filter(
        AttendancePeriodSummary.status == "confirmed",
    ).scalar()
    if latest_period_end:
        present, absent = db.query(
            func.coalesce(func.sum(AttendancePeriodSummary.present_days), 0),
            func.coalesce(func.sum(AttendancePeriodSummary.absent_days), 0),
        ).filter(
            AttendancePeriodSummary.period_end == latest_period_end,
            AttendancePeriodSummary.status == "confirmed",
        ).one()
        attendance = {"present": int(present), "absent": int(absent)}
        # The client-confirmed workbook is a historical baseline. Extend it
        # with newer submitted daily registers so Reports matches the Student,
        # Parent and Operations attendance views. Standalone registers are the
        # authoritative daily source and the import path consolidates any
        # biometric/manual duplicate for the same batch and date.
        submitted_rows = (
            db.query(AttendanceEntry.status, func.count())
            .join(
                AttendanceRegister,
                AttendanceRegister.id == AttendanceEntry.register_id,
            )
            .filter(
                AttendanceRegister.status == "submitted",
                AttendanceRegister.class_session_id.is_(None),
                AttendanceRegister.register_kind.in_(("manual", "biometric")),
                AttendanceRegister.attendance_date > latest_period_end,
            )
            .group_by(AttendanceEntry.status)
            .all()
        )
        for status, count in submitted_rows:
            attendance[status] = attendance.get(status, 0) + int(count)
    else:
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
    paid = sum(
        received_effect(row)
        for row, _student in db.query(PaymentTransaction, Student)
        .join(Student, Student.id == PaymentTransaction.student_id)
        .filter(Student.is_test_account.is_(False))
        .all()
    )
    recent = db.query(AuditLog, User).outerjoin(User, User.id == AuditLog.actor_id).filter((User.id.is_(None)) | (User.is_test_account.is_(False))).order_by(AuditLog.created_at.desc()).limit(10).all()
    result = {
        "exports": _available_reports(db, user),
        "metrics": {
            "students": db.query(Student).filter(
                Student.is_test_account.is_(False),
                Student.status == "active",
            ).count(),
            "activeUsers": db.query(User).filter(User.is_active.is_(True), User.is_test_account.is_(False)).count(),
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
    permissions = effective_permissions(db, user)
    metric_modules = {
        "students": "students", "activeUsers": "reports", "scheduledClasses": "timetable",
        "publishedNotices": "communication", "assignments": "academics",
        "overdueAssignments": "academics", "recordedPayments": "finance", "attendanceRate": "attendance",
    }
    result["metrics"] = {key: value for key, value in result["metrics"].items() if permissions.get(metric_modules[key], {}).get("read")}
    if not permissions.get("admissions", {}).get("read"):
        result["leadFunnel"] = []
    if not permissions.get("attendance", {}).get("read"):
        result["attendance"] = []
    return result


@router.get("/exports")
def available_exports(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*REPORT_ROLES)),
):
    return _available_reports(db, user)


@router.get("/export/{report_name}")
def export_report(
    report_name: str,
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    export_format: Literal["csv", "xlsx"] = Query(default="csv", alias="format"),
    month: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*REPORT_ROLES)),
):
    definition = REPORT_BY_ID.get(report_name)
    if not definition:
        raise HTTPException(404, "Unknown report")
    if not has_permission(db, user, definition["module"]):
        raise HTTPException(403, "You do not have access to this report's module")
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "'from' date must be on or before 'to' date")
    stamp = datetime.now(IST).date().isoformat()
    if definition["period"] != "range" and (date_from or date_to):
        raise HTTPException(422, "Use a month for payroll. Snapshot reports do not accept date filters.")
    if report_name == "payroll":
        month = month or stamp[:7]
        try:
            month_bounds(month)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
    elif month:
        raise HTTPException(422, "Month selection applies only to payroll")
    sheets = detailed_sheets(db, report_name, date_from, date_to, month)
    if sheets:
        if export_format != "xlsx" and len(sheets) > 1:
            raise HTTPException(422, "This report contains multiple sheets. Choose Excel (.xlsx) to download all details.")
        filename = f"lakshya-{report_name}-{month if report_name == 'payroll' else stamp}.csv"
        title, headings, rows, scope = sheets[0]
        if export_format == "csv":
            rows = [tuple(local_datetime(value) if isinstance(value, datetime) else value for value in row) for row in rows]
        return _report_download(filename, headings, rows, export_format, title, scope, sheets)
    if report_name == "students":
        enrollment_rows = {}
        for row in (
            db.query(Enrollment)
            .order_by(
                Enrollment.is_active.desc(),
                Enrollment.created_at.desc(),
                Enrollment.id.desc(),
            )
            .all()
        ):
            enrollment_rows.setdefault(row.student_id, row)
        students = db.query(Student).filter(Student.is_test_account.is_(False)).order_by(Student.full_name).all()
        return _report_download(
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
            export_format, "Student register",
            "All non-test students, including drafts and opted-out records. Filter Status to view active students only. Latest active enrolment is shown.",
            additional_sheets=student_supporting_sheets(db) if export_format == "xlsx" else None,
        )
    if report_name == "fees":
        agreements = (
            db.query(FeeAgreement, Student)
            .join(Student, Student.id == FeeAgreement.student_id)
            .filter(Student.is_test_account.is_(False))
            .order_by(Student.full_name, FeeAgreement.created_at.desc())
            .all()
        )
        effects: dict[str, int] = {}
        receipts: dict[str, int] = {}
        for transaction in db.query(PaymentTransaction).all():
            effects[transaction.fee_agreement_id] = (
                effects.get(transaction.fee_agreement_id, 0)
                + payment_effect(transaction)
            )
            receipts[transaction.fee_agreement_id] = (
                receipts.get(transaction.fee_agreement_id, 0)
                + received_effect(transaction)
            )
        headings = [
                "Admission number",
                "Student",
                "Agreed fee",
                "Received",
                "Outstanding",
                "Currency",
                "Agreement status",
                "Student status",
                "Account scope",
                "Balance adjustments",
                "Credit balance",
                "Agreement ID",
            ]
        rows = []
        for agreement, student in agreements:
            closed = student.status in {"inactive", "forfeited"} or agreement.status == "inactive"
            balance = agreement.agreed_amount - effects.get(agreement.id, 0)
            rows.append((
                    student.admission_number,
                    student.full_name,
                    agreement.agreed_amount,
                    receipts.get(agreement.id, 0),
                    0 if closed else max(0, balance),
                    agreement.currency,
                    agreement.status,
                    student.status,
                    "Closed" if closed else "Open",
                    effects.get(agreement.id, 0) - receipts.get(agreement.id, 0),
                    max(0, -balance),
                    agreement.id,
            ))
        scope = "Current balances in INR. Received is net cash after refunds/reversals. Balance adjustments change dues, not cash. Closed accounts are excluded from outstanding."
        # Keep the reader-facing summaries compact, with reconciliation fields separate.
        display_columns = (0, 1, 2, 3, 4, 9, 10, 7)
        display_headings = [headings[index] for index in display_columns]
        return _report_download(
            f"lakshya-fee-balances-{stamp}.csv", headings, rows,
            export_format, "Fee balances", scope,
            sheets=[
                ("Open accounts", display_headings, [tuple(row[index] for index in display_columns) for row in rows if row[8] == "Open"], scope),
                ("Closed accounts", display_headings, [tuple(row[index] for index in display_columns) for row in rows if row[8] == "Closed"], "Historical accounts in INR. Excluded from current agreed fees and outstanding. Add received totals from both sheets for all-time collections."),
                ("Agreement details", headings, rows, "Same accounts as the first two sheets, with agreement IDs, currency and statuses for reconciliation. Do not add these totals to the first two sheets."),
            ],
        )
    if report_name == "attendance":
        submitted = (
            db.query(
                AttendanceEntry,
                AttendanceRegister,
                ClassSession,
                Student,
                Batch,
                Subject,
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
            .outerjoin(Batch, Batch.id == ClassSession.batch_id)
            .outerjoin(Subject, Subject.id == ClassSession.subject_id)
            .filter(AttendanceRegister.status == "submitted", Student.is_test_account.is_(False))
            .order_by(AttendanceEntry.updated_at.desc(), AttendanceRegister.id.desc())
            .all()
        )
        rows = []
        daily_rows = {}
        class_rows = []
        for entry, register, session, student, batch, subject in submitted:
            attendance_date = register.attendance_date or (
                local_datetime(session.starts_at).date() if session else None
            )
            if date_from and (not attendance_date or attendance_date < date_from):
                continue
            if date_to and (not attendance_date or attendance_date > date_to):
                continue
            record = (
                    attendance_date,
                    student.admission_number,
                    student.full_name,
                    register.batch_name or (batch.name if batch else ""),
                    "All programs" if register.stream_name == "__all__" else register.stream_name or (batch.program if batch else ""),
                    register.subject_name or (subject.name if subject else ""),
                    entry.status,
                    entry.reason,
                    "class" if session else register.register_kind,
                )
            if session:
                class_rows.append(record + (session.starts_at,))
            else:
                key = (student.id, attendance_date or register.id)
                priority = 3 if register.register_kind == "manual" else 2
                if key not in daily_rows or priority > daily_rows[key][0]:
                    daily_rows[key] = (priority, record)
        daily_query = (
            db.query(DailyAttendanceEntry, Student)
            .join(Student, Student.id == DailyAttendanceEntry.student_id)
            .filter(Student.is_test_account.is_(False))
            .order_by(DailyAttendanceEntry.updated_at.desc(), DailyAttendanceEntry.id.desc())
        )
        if date_from:
            daily_query = daily_query.filter(
                DailyAttendanceEntry.attendance_date >= date_from
            )
        if date_to:
            daily_query = daily_query.filter(
                DailyAttendanceEntry.attendance_date <= date_to
            )
        for entry, student in daily_query.all():
            key = (student.id, entry.attendance_date or entry.source_date_label)
            record = (
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
            daily_rows.setdefault(key, (1, record))
        daily_records = sorted((value[1] for value in daily_rows.values()), key=lambda row: (str(row[0]), row[2]), reverse=True)
        class_rows.sort(key=lambda row: (str(row[0]), row[2]), reverse=True)
        rows.extend(daily_records)
        rows.extend(row[:9] for row in class_rows)
        summary_query = (
            db.query(AttendancePeriodSummary, Student)
            .join(Student, Student.id == AttendancePeriodSummary.student_id)
            .filter(AttendancePeriodSummary.status == "confirmed", Student.is_test_account.is_(False))
            .order_by(AttendancePeriodSummary.period_end.desc(), Student.full_name)
        )
        if date_from:
            summary_query = summary_query.filter(
                AttendancePeriodSummary.period_end >= date_from,
            )
        if date_to:
            summary_query = summary_query.filter(
                AttendancePeriodSummary.period_start <= date_to,
            )
        summaries = summary_query.all()
        rows.extend(
            (
                f"{summary.period_start.isoformat()} to {summary.period_end.isoformat()}",
                student.admission_number,
                student.full_name,
                summary.batch_name,
                "",
                "Period summary",
                f"{float(summary.attendance_rate):.1f}%",
                f"{summary.present_days} present / {summary.working_days} working days",
                "client-confirmed summary",
            )
            for summary, student in summaries
        )
        rows.sort(key=lambda item: (str(item[0]), item[2]), reverse=True)
        headings = [
                "Date",
                "Admission number",
                "Student",
                "Batch",
                "Program",
                "Subject",
                "Status",
                "Reason / source value",
                "Source",
            ]
        period = f"Dates: {date_from or 'earliest'} to {date_to or 'latest'}. "
        scope = period + "One daily record per student/date. Signed manual entries take precedence over biometric and older imports. Missing days are not absences."
        summary_headings = ["Period start", "Period end", "Admission number", "Student", "Batch", "Present days", "Absent days", "Working days", "Attendance rate", "Source"]
        summary_records = [(summary.period_start, summary.period_end, student.admission_number, student.full_name, summary.batch_name, summary.present_days, summary.absent_days, summary.working_days, float(summary.attendance_rate) / 100, summary.source_name) for summary, student in summaries]
        return _report_download(
            f"lakshya-attendance-{stamp}.csv", headings, rows,
            export_format, "Daily attendance", scope,
            sheets=[
                ("Daily attendance", headings, daily_records, scope),
                ("Class attendance", headings + ["Class starts (IST)"], class_rows, period + "Submitted class-level entries. These can overlap daily attendance and must not be added to daily totals."),
                ("Period summaries", summary_headings, summary_records, period + "Historical confirmed totals, not individual days. Overlapping periods are shown in full, not prorated. Do not add these to overlapping daily entries."),
            ],
        )
    if report_name == "audit":
        query = (
            db.query(AuditLog, User)
            .outerjoin(User, User.id == AuditLog.actor_id)
            .filter((User.id.is_(None)) | (User.is_test_account.is_(False)))
            .order_by(AuditLog.created_at.desc())
        )
        if date_from:
            query = query.filter(
                AuditLog.created_at
                >= datetime.combine(date_from, datetime.min.time()).replace(
                    tzinfo=IST,
                ).astimezone(timezone.utc)
            )
        if date_to:
            query = query.filter(
                AuditLog.created_at
                < datetime.combine(date_to, datetime.min.time()).replace(
                    tzinfo=IST,
                ).astimezone(timezone.utc)
                + timedelta(days=1)
            )
        return _report_download(
            f"lakshya-audit-{stamp}.csv",
            [
                "Timestamp (IST)",
                "Actor",
                "Role",
                "Action",
                "Record type",
                "Record ID",
            ],
            (
                (
                    local_datetime(log.created_at).replace(tzinfo=IST),
                    actor.full_name if actor else "System",
                    actor.role if actor else "",
                    log.action,
                    log.entity_type,
                    log.entity_id,
                )
                for log, actor in query.all()
            ),
            export_format, "Audit trail",
            f"Dates: {date_from or 'earliest'} to {date_to or 'latest'}. All timestamps and date filters use India Standard Time. Test-account activity is excluded.",
        )
    raise HTTPException(404, "Report export not found")
