"""Report contents and uncapped read-only exports, separate from screen pagination."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, or_

from .models import (
    Batch, ClassSession, Examination, ExaminationParticipant, ExaminationResult,
    FeeAgreement, FeeInstallment, InventoryItem, InventoryMovement, Lead, LeadActivity,
    PaymentTransaction, Room, StaffPayroll, Student, Subject, User,
    Enrollment, Guardian, StudentGuardian, FacultyTeachingAssignment,
)
from .report_downloads import local_datetime
from .services import payment_effect, received_effect


def report(id, label, module, description, sheets, period="range"):
    return dict(id=id, label=label, module=module, description=description, sheets=sheets, period=period)


REPORTS = [
    report("students", "Student register", "students", "Contacts, current enrolment, guardian contacts and enrolment history, including inactive students.", ["Student register", "Guardian contacts", "Enrolment history"], "snapshot"),
    report("fees", "Fee balances", "finance", "Agreed fees, receipts, adjustments, outstanding amounts, credits and agreement-level details.", ["Open accounts", "Closed accounts", "Agreement details"], "snapshot"),
    report("payments", "Payment ledger", "finance", "Every transaction, receipt, refund and adjustment, with posting and reconciliation status.", ["Payment ledger"]),
    report("installments", "Instalment schedule", "finance", "Due dates, scheduled amounts, methods and agreement status. Not a payment-allocation report.", ["Instalment schedule"]),
    report("attendance", "Student attendance", "attendance", "Student-level dates, statuses, reasons and sources; class and historical records stay separate.", ["Daily attendance", "Class attendance", "Period summaries"]),
    report("staff-attendance", "Staff attendance & work time", "attendance", "Daily arrival, departure, work time and overtime, with monthly totals. Directors are separate.", ["Staff daily", "Director daily", "Monthly totals"]),
    report("payroll", "Monthly payroll", "payroll", "Salary, absence, payable days, advance and net payable, plus the saved attendance basis.", ["Payroll register", "Saved attendance"], "month"),
    report("examinations", "Examinations & results", "examinations", "Exam schedule and each eligible student's marks, absence, pending results and publication status.", ["Examinations", "Student results"]),
    report("admissions", "Enquiries & follow-ups", "admissions", "Enquiry contacts, programme, stage, counsellor, next action and complete follow-up history.", ["Enquiries", "Follow-up history"]),
    report("inventory", "Inventory & stock movements", "inventory", "Current stock levels and the full issue, return, inward and adjustment ledger.", ["Current stock", "Stock movements"]),
    report("timetable", "Timetable & faculty allocations", "timetable", "Class timings, cancellations and rooms, plus current faculty-to-subject allocations.", ["Class timetable", "Faculty allocations"]),
    report("academics", "Academic profiles & subjects", "academics", "Student codes, mentors, streams, schools and recorded subject selections.", ["Academic profiles", "Subject selections"], "snapshot"),
    report("assignments", "Assignments & student progress", "academics", "Due dates, instructions, recipient progress and PDF download history, plus material details.", ["Assignments", "Student progress", "Material details"]),
    report("announcements", "Announcements", "communication", "Announcement text, audience, batch, subject, author and publication status.", ["Announcements"]),
    report("audit", "Audit trail", "reports", "Actor, role, action, record identifier and time. Sensitive change payloads are excluded.", ["Audit trail"]),
]
REPORT_BY_ID = {item["id"]: item for item in REPORTS}


def student_supporting_sheets(db):
    guardians = db.query(Student, Guardian, StudentGuardian).join(StudentGuardian, StudentGuardian.student_id == Student.id).join(Guardian, Guardian.id == StudentGuardian.guardian_id).filter(Student.is_test_account.is_(False)).order_by(Student.full_name, StudentGuardian.is_primary.desc()).all()
    enrollments = db.query(Student, Enrollment).join(Enrollment, Enrollment.student_id == Student.id).filter(Student.is_test_account.is_(False)).order_by(Student.full_name, Enrollment.enrollment_date).all()
    return [
        ("Guardian contacts", ["Admission number", "Student", "Guardian", "Mobile", "Relationship", "Primary contact", "Verified"], [(s.admission_number, s.full_name, g.full_name, g.mobile, link.relationship, "Yes" if link.is_primary else "No", "Yes" if g.verified else "No") for s, g, link in guardians], "Linked guardian contacts only. Blank or missing links are not inferred from student mobile numbers."),
        ("Enrolment history", ["Admission number", "Student", "Program", "Batch", "Enrolment date", "Status", "Active", "Source", "Enrolment ID"], [(s.admission_number, s.full_name, e.program, e.batch, e.enrollment_date, e.status, "Yes" if e.is_active else "No", e.source_type, e.id) for s, e in enrollments], "All enrolments, including historical/inactive records. The first sheet shows the latest active enrolment where available."),
    ]


def in_range(value, start, end):
    if isinstance(value, datetime):
        value = local_datetime(value).date()
    return (not start and not end) or (value is not None and (not start or value >= start) and (not end or value <= end))


def detailed_sheets(db, name, start, end, month):
    scope = f"Dates: {start or 'beginning'} to {end or 'latest'} (IST), inclusive. All matching records; no screen pagination limit."
    if name in {"academics", "assignments", "announcements"}:
        from .report_academics import academic_sheets, assignment_sheets, announcement_sheets
        if name == "academics":
            return academic_sheets(db)
        if name == "assignments":
            return assignment_sheets(db, start, end, in_range, scope)
        return announcement_sheets(db, start, end, in_range, scope)
    if name == "payments":
        records = db.query(PaymentTransaction, Student).join(Student, Student.id == PaymentTransaction.student_id).filter(Student.is_test_account.is_(False)).order_by(PaymentTransaction.transaction_date, PaymentTransaction.created_at).all()
        rows = [(p.transaction_date, s.admission_number, s.full_name, p.receipt_number, p.transaction_type, p.amount, received_effect(p), payment_effect(p), p.method, p.status, p.reconciliation_status, p.reference, p.notes, p.source_note, p.id, p.fee_agreement_id, p.related_transaction_id) for p, s in records if in_range(p.transaction_date, start, end)]
        return [("Payment ledger", ["Date", "Admission number", "Student", "Receipt", "Type", "Transaction amount", "Net received", "Balance effect", "Method", "Status", "Reconciliation", "Reference", "Notes", "Source", "Transaction ID", "Agreement ID", "Related transaction"], rows, scope + " Net effects follow the fee ledger: posted and ready staged entries count unless excluded. Other rows have zero effect. Undated entries appear only without date filters.")]
    if name == "installments":
        records = db.query(FeeInstallment, Student, FeeAgreement).join(Student, Student.id == FeeInstallment.student_id).join(FeeAgreement, FeeAgreement.id == FeeInstallment.fee_agreement_id).filter(Student.is_test_account.is_(False)).order_by(FeeInstallment.due_date, Student.full_name).all()
        return [("Instalment schedule", ["Due date", "Admission number", "Student", "Scheduled amount", "Expected method", "Instalment status", "Agreement status", "Student status", "Notes", "Agreement ID", "Instalment ID"], [(i.due_date, s.admission_number, s.full_name, i.amount, i.expected_method, i.status, a.status, s.status, i.notes, a.id, i.id) for i, s, a in records if in_range(i.due_date, start, end)], scope + " Filtered by due date. Scheduled amounts are not outstanding balances; receipts are held against fee agreements.")]
    if name == "admissions":
        records = db.query(Lead).outerjoin(Student, Student.id == Lead.converted_student_id).filter(or_(Student.id.is_(None), Student.is_test_account.is_(False))).order_by(Lead.created_at, Lead.id).all()
        records = [r for r in records if in_range(r.created_at, start, end)]
        leads = {r.id: r for r in records}
        history = db.query(LeadActivity, User).outerjoin(User, User.id == LeadActivity.actor_id).filter(LeadActivity.lead_id.in_(leads), or_(User.id.is_(None), User.is_test_account.is_(False))).order_by(LeadActivity.created_at).all() if leads else []
        return [
            ("Enquiries", ["Created (IST)", "Student", "Mobile", "Email", "Parent", "Parent mobile", "Program", "Source", "Counsellor", "Stage", "Priority", "Next follow-up (IST)", "Next action", "Summary", "Converted (IST)", "Lead ID"], [(r.created_at, r.student, r.mobile, r.email, r.parent, r.parent_mobile, r.program, r.source, r.counsellor, r.stage, r.priority, r.next_follow_up_at, r.next_action, r.summary, r.converted_at, r.id) for r in records], scope + " Enquiries filtered by creation date."),
            ("Follow-up history", ["Lead ID", "Student", "Time (IST)", "Kind", "Note", "Actor"], [(r.lead_id, leads[r.lead_id].student, r.created_at, r.kind, r.note, u.full_name if u else "System") for r, u in history], "Complete activity history for the enquiries in the first sheet, including follow-ups outside the selected creation dates."),
        ]
    if name == "staff-attendance":
        from .routers.attendance import staff_attendance_report
        data = staff_attendance_report(db, date_from=start, date_to=end)
        headings = ["Date", "Name", "Designation", "Device", "Device ID", "Status", "Arrival (IST)", "Departure (IST)", "Work time", "Overtime", "Punch count", "Source"]
        def dt(value):
            return datetime.fromisoformat(value) if value else None
        def row(r):
            return (date.fromisoformat(r["date"]), r["fullName"], r["designation"] or r["role"].replace("_", " ").title(), r["deviceKey"], r["deviceUserId"], r["attendanceStatus"], dt(r["arrivalAt"]), dt(r["departureAt"]), timedelta(minutes=r["workDurationMinutes"]) if r["workDurationMinutes"] is not None else None, timedelta(minutes=r["overtimeMinutes"]), r["punchCount"], r["source"])
        note = scope + " Missing dates are not absences. Monthly work-duration records supersede punch spans; punch spans are elapsed time on site, not net work time."
        totals = [(r["month"], r["fullName"], r["attendanceGroup"], r["personKey"], r["recordedDays"], r["absentDays"], r["halfDays"], r["weeklyOffDays"], timedelta(minutes=r["totalWorkMinutes"]) if r["durationRecordedDays"] else None, timedelta(minutes=r["overtimeMinutes"]), r["durationRecordedDays"], r["durationMissingDays"]) for r in data["monthlyTotals"]]
        return [("Staff daily", headings, [row(r) for r in data["records"] if r["attendanceGroup"] == "staff"], note), ("Director daily", headings, [row(r) for r in data["records"] if r["attendanceGroup"] == "directors"], note), ("Monthly totals", ["Month", "Name", "Group", "Person key", "Recorded present days", "Full absent days", "Half days", "Weekly off days", "Known work time", "Overtime", "Days with duration", "Days missing duration"], totals, note + " Totals cover only selected dates and known durations, not necessarily complete months. Half days count as recorded present days. Days count device records.")]
    if name == "payroll":
        from .payroll import calculate_payroll
        from .routers.payroll import _people
        people = _people(db, month)
        stored = {r.person_key: r for r in db.query(StaffPayroll).filter_by(month=month).all()}
        rows, attendance = [], []
        for key in sorted(set(people) | set(stored)):
            saved = stored.get(key)
            linked_user = db.get(User, key.removeprefix("user:")) if key.startswith("user:") else None
            if linked_user and linked_user.is_test_account:
                continue
            snapshot = saved.snapshot or {} if saved else {}
            person = people.get(key) or snapshot.get("attendance", {})
            # Keep finalized financial values and their attendance basis immutable.
            calc = (snapshot.get("calculation") if saved.status == "finalized" else calculate_payroll(month, saved.monthly_salary, saved.absent_days, saved.advance_given)) if saved else None
            calc = calc or {}
            changed = bool(saved and (not people.get(key) or saved.attendance_fingerprint != person.get("attendanceFingerprint")))
            def money(field):
                return Decimal(str(calc[field])) if calc.get(field) is not None else None
            rows.append((month, snapshot.get("fullName") or person.get("fullName", key), saved.status if saved else "not_prepared", money("monthlySalary"), calc.get("daysInMonth"), calc.get("absentDays"), calc.get("payableDays"), money("perDayRate"), money("payableAmount"), money("advanceGiven"), money("netPayable"), "Yes" if changed else "No", saved.notes if saved else "", saved.updated_at if saved else None, key))
            basis = snapshot.get("attendance", {})
            logged_dates = set()
            for day in basis.get("dailyWorkLog", []):
                logged_dates.add(day["date"])
                attendance.append((month, snapshot.get("fullName") or person.get("fullName", key), date.fromisoformat(day["date"]), day["status"], timedelta(minutes=day["workMinutes"]) if day.get("workMinutes") is not None else None, timedelta(minutes=day["overtimeMinutes"]) if day.get("overtimeMinutes") is not None else None, key))
            for day in sorted(set(basis.get("presentDates", [])) - logged_dates):
                attendance.append((month, snapshot.get("fullName") or person.get("fullName", key), date.fromisoformat(day), "present", None, None, key))
        note = f"Month: {month}. Not-prepared rows have no amounts. Finalized values retain their saved snapshot; drafts are estimates. Totals combine drafts and finalized rows, not confirmed payments. Work time introduces no additional deductions."
        return [("Payroll register", ["Month", "Name", "Status", "Monthly salary", "Days in month", "Absent days", "Payable days", "Per-day rate", "Payable amount", "Advance", "Net payable", "Attendance changed", "Notes", "Updated (IST)", "Person key"], rows, note), ("Saved attendance", ["Month", "Name", "Date", "Status", "Work time", "Overtime", "Person key"], attendance, "Presence and daily work-duration evidence captured when payroll was saved. Blank durations are unknown, not zero. Unsaved payroll has no captured evidence. See Staff attendance & work time for current records.")]
    if name == "examinations":
        exams = db.query(Examination, Batch, Subject, User).join(Batch, Batch.id == Examination.batch_id).join(Subject, Subject.id == Examination.subject_id).join(User, User.id == Examination.faculty_id).filter(User.is_test_account.is_(False)).order_by(Examination.scheduled_at).all()
        exams = {e.id: (e, b, s, u) for e, b, s, u in exams if in_range(e.scheduled_at, start, end)}
        results = db.query(ExaminationParticipant, ExaminationResult).join(Student, Student.id == ExaminationParticipant.student_id).outerjoin(ExaminationResult, and_(ExaminationResult.exam_id == ExaminationParticipant.exam_id, ExaminationResult.student_id == ExaminationParticipant.student_id)).filter(ExaminationParticipant.exam_id.in_(exams), Student.is_test_account.is_(False)).order_by(ExaminationParticipant.exam_id, ExaminationParticipant.full_name).all() if exams else []
        return [
            ("Examinations", ["Exam ID", "Exam", "Scheduled (IST)", "Batch", "Subject", "Faculty", "Duration (minutes)", "Maximum marks", "Pass marks", "Status", "Published (IST)", "Instructions"], [(e.id, e.name, e.scheduled_at, b.name, s.name, u.full_name, e.duration_minutes, e.max_marks, e.pass_marks, e.status, e.published_at, e.instructions) for e, b, s, u in exams.values()], scope + " Filtered by scheduled date; includes drafts and unpublished exams."),
            ("Student results", ["Exam ID", "Exam", "Admission number", "Student", "Batch", "Subject", "Maximum marks", "Pass marks", "Marks obtained", "Result status", "Remarks", "Publication status"], [(p.exam_id, exams[p.exam_id][0].name, p.admission_number, p.full_name, exams[p.exam_id][1].name, exams[p.exam_id][2].name, exams[p.exam_id][0].max_marks, exams[p.exam_id][0].pass_marks, r.marks_obtained if r else None, r.result_status if r else "not_entered", r.remarks if r else "", exams[p.exam_id][0].status) for p, r in results], "One row per eligible student per exam, including missing results. Blank marks are not zero; unpublished results are internal only."),
        ]
    if name == "inventory":
        items = db.query(InventoryItem).order_by(InventoryItem.name).all()
        moves = db.query(InventoryMovement, InventoryItem, Student).join(InventoryItem, InventoryItem.id == InventoryMovement.item_id).outerjoin(Student, Student.id == InventoryMovement.student_id).filter(or_(Student.id.is_(None), Student.is_test_account.is_(False))).order_by(InventoryMovement.occurred_on, InventoryMovement.created_at).all()
        return [("Current stock", ["SKU", "Item", "Category", "Unit", "Quantity on hand", "Reorder level", "Active", "Vendor", "Notes"], [(i.sku, i.name, i.category, i.unit, i.quantity_on_hand, i.reorder_level, "Yes" if i.is_active else "No", i.vendor_reference, i.notes) for i in items], "Current stock snapshot, including inactive items; NOT a historical closing stock balance. Blank quantities are unknown, not zero."), ("Stock movements", ["Date", "SKU", "Item", "Type", "Quantity change", "Balance after", "Recipient type", "Recipient", "Admission number", "Student", "Reference", "Reason", "Movement ID"], [(m.occurred_on, i.sku, i.name, m.movement_type, m.quantity_delta, m.balance_after, m.target_type, m.target_reference, s.admission_number if s else None, s.full_name if s else None, m.reference, m.reason, m.id) for m, i, s in moves if in_range(m.occurred_on, start, end)], scope)]
    if name == "timetable":
        rows = db.query(ClassSession, Batch, Subject, User, Room).join(Batch, Batch.id == ClassSession.batch_id).join(Subject, Subject.id == ClassSession.subject_id).join(User, User.id == ClassSession.faculty_id).join(Room, Room.id == ClassSession.room_id).filter(User.is_test_account.is_(False)).order_by(ClassSession.starts_at).all()
        allocations = db.query(FacultyTeachingAssignment, User, Batch, Subject).join(User, User.id == FacultyTeachingAssignment.faculty_id).join(Batch, Batch.id == FacultyTeachingAssignment.batch_id).join(Subject, Subject.id == FacultyTeachingAssignment.subject_id).filter(User.is_test_account.is_(False)).order_by(User.full_name, Batch.name, Subject.name).all()
        return [
            ("Class timetable", ["Start (IST)", "End (IST)", "Batch", "Subject", "Faculty", "Room", "Status", "Notes", "Override reason", "Session ID"], [(c.starts_at, c.ends_at, b.name, s.name, u.full_name, r.name, c.status, c.notes, c.override_reason, c.id) for c, b, s, u, r in rows if in_range(c.starts_at, start, end)], scope + " Filtered by class start date; cancelled classes retain their status."),
            ("Faculty allocations", ["Faculty", "Batch", "Program", "Subject", "Active", "Allocation ID"], [(u.full_name, b.name, b.program, s.name, "Yes" if a.is_active else "No", a.id) for a, u, b, s in allocations], "Current faculty assignments, including inactive allocations. Date filters apply only to class sessions, not this snapshot."),
        ]
    return None
