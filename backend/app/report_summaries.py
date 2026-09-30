"""Batch summaries of recorded evidence, never inferred calendar-day absences."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_

from .models import (
    AttendanceEntry, AttendanceRegister, Batch, DailyAttendanceEntry, Enrollment,
    Examination, ExaminationParticipant, ExaminationResult, Student,
    StudentAcademicProfile, StudentSubjectSelection, Subject, User,
)
from .report_downloads import IST, local_datetime
from .services import canonical_subject

BATCHES = ("Tatva", "Essential")
SUBJECTS = ("Physics", "Chemistry", "Maths", "Biology")


def batch_label(value):
    return {"tatva": "Tatva", "tatwa": "Tatva", "essential": "Essential"}.get((value or "").strip().casefold())


def roster(db):
    students = {s.id: s for s in db.query(Student).filter(Student.is_test_account.is_(False)).all()}
    groups = {b: {} for b in BATCHES}
    seen = set()
    for e in db.query(Enrollment).filter(Enrollment.is_active.is_(True)).order_by(Enrollment.created_at.desc(), Enrollment.id.desc()).all():
        if e.student_id in seen:
            continue
        seen.add(e.student_id)
        b = batch_label(e.batch)
        if b and e.student_id in students and students[e.student_id].status == "active":
            groups[b][e.student_id] = e.enrollment_date
    for p in db.query(StudentAcademicProfile).all():
        b = batch_label(p.batch_name)
        if b and p.student_id not in seen and p.student_id in students and students[p.student_id].status == "active":
            groups[b][p.student_id] = None
    return students, groups


def attendance_summary(db, start, end):
    students, groups = roster(db)
    evidence = defaultdict(list)
    student_dates = defaultdict(set)
    batch_dates = {b: set() for b in BATCHES}

    def add(batch, sid, day, status, source):
        b = batch_label(batch)
        if not b or sid not in students or not day or (start and day < start) or (end and day > end):
            return
        groups[b].setdefault(sid, None)  # Historical records survive roster changes.
        batch_dates[b].add(day)
        status = "present" if status in {"present", "late"} else status or "unclassified"
        evidence[(b, sid, day)].append((status, source))
        student_dates[(b, sid)].add(day)

    registers = db.query(AttendanceRegister).filter(
        AttendanceRegister.status == "submitted",
        AttendanceRegister.class_session_id.is_(None),
        AttendanceRegister.register_kind.in_(("manual", "biometric")),
    )
    if start:
        registers = registers.filter(AttendanceRegister.attendance_date >= start)
    if end:
        registers = registers.filter(AttendanceRegister.attendance_date <= end)
    registers = {r.id: r for r in registers.all() if batch_label(r.batch_name)}
    # Empty submitted registers still expose coverage gaps, not student absences.
    for r in registers.values():
        if r.attendance_date:
            batch_dates[batch_label(r.batch_name)].add(r.attendance_date)
    for entry in db.query(AttendanceEntry).filter(AttendanceEntry.register_id.in_(registers)).all():
        r = registers[entry.register_id]
        add(r.batch_name, entry.student_id, r.attendance_date, entry.status, r.register_kind)
    legacy = db.query(DailyAttendanceEntry).filter(DailyAttendanceEntry.attendance_date.is_not(None))
    if start:
        legacy = legacy.filter(DailyAttendanceEntry.attendance_date >= start)
    if end:
        legacy = legacy.filter(DailyAttendanceEntry.attendance_date <= end)
    for entry in legacy.all():
        add(entry.batch_name, entry.student_id, entry.attendance_date, entry.normalized_status, "historical daily")

    scope = (f"Dates: {start or 'first recorded'} to {end or 'last recorded'}, inclusive. Daily attendance only; P/C/M classes unavailable. "
             "Percentage = present (including late) / (present + absent). Excused, conflicting and unknown days excluded. Missing is not absent.")
    sheets, details, coverage = [], [], []
    headings = ["Sr No", "Name", "Recorded attendance days", "Days present", "Days absent", "Attendance %", "Excused days", "Conflict days", "Unclassified days", "Missing on batch dates", "Admission number"]
    for b in BATCHES:
        rows = []
        for sid in sorted(groups[b], key=lambda x: (students[x].full_name.casefold(), x)):
            student = students[sid]
            enrolled = groups[b][sid]
            dates = batch_dates[b]
            own_dates = student_dates[(b, sid)]
            applicable = {day for day in dates if not enrolled or day >= enrolled} | own_dates
            counts = defaultdict(int)
            for day in sorted(applicable):
                records = evidence.get((b, sid, day), [])
                statuses = {status for status, _ in records}
                resolved = (next(iter(statuses)) if len(statuses) == 1 else "conflict") if records else "missing"
                if resolved not in {"present", "absent", "excused", "missing", "conflict"}:
                    resolved = "unclassified"
                counts[resolved] += 1
                details.append((b, student.admission_number, student.full_name, day, resolved,
                                ", ".join(sorted(statuses)), ", ".join(sorted({s for _, s in records})), max(0, len(records) - 1)))
            denominator = counts["present"] + counts["absent"]
            rows.append((len(rows) + 1, student.full_name, len(own_dates), counts["present"], counts["absent"],
                         counts["present"] / denominator if denominator else None, counts["excused"], counts["conflict"],
                         counts["unclassified"], counts["missing"], student.admission_number))
        sheets.append((b, headings, rows, scope))
        first = start or min(batch_dates[b], default=None)
        last = end or max(batch_dates[b], default=None)
        if first and last:
            for offset in range((last - first).days + 1):
                day = first + timedelta(days=offset)
                state = "Recorded" if day in batch_dates[b] else "Future date" if day > datetime.now(IST).date() else "No daily records; class/holiday unknown"
                coverage.append((b, day, state))
    return sheets + [
        ("Date coverage", ["Batch", "Date", "Coverage"], coverage, "Dates without daily records are not assumed teaching days or absences. Blank filters cover each batch's first to last recorded date."),
        ("Daily evidence", ["Batch", "Admission number", "Name", "Date", "Resolved status", "Source statuses", "Sources", "Duplicate rows collapsed"], details,
         "One row per student and batch date. Conflicting statuses are excluded, not silently overridden. Missing entries may reflect historical roster differences. Period-only totals and class registers are excluded."),
    ]


def examination_summary(db, start, end, absence_policy="unconfirmed"):
    students, groups = roster(db)
    selected = defaultdict(set)
    for s in db.query(StudentSubjectSelection).all():
        selected[s.student_id].add(canonical_subject(s.subject_name))
    exams = {}
    for exam, batch, subject in db.query(Examination, Batch, Subject).join(Batch, Batch.id == Examination.batch_id).join(Subject, Subject.id == Examination.subject_id).join(User, User.id == Examination.faculty_id).filter(User.is_test_account.is_(False), Examination.status != "cancelled").all():
        day = local_datetime(exam.scheduled_at).date()
        b = batch_label(batch.name)
        if b and (not start or day >= start) and (not end or day <= end):
            exams[exam.id] = (exam, b, canonical_subject(subject.name), day)
    entries = defaultdict(list)
    detail_rows = []
    query = db.query(ExaminationParticipant, ExaminationResult).outerjoin(ExaminationResult, and_(
        ExaminationParticipant.exam_id == ExaminationResult.exam_id,
        ExaminationParticipant.student_id == ExaminationResult.student_id,
    )).filter(ExaminationParticipant.exam_id.in_(exams))
    for participant, result in query.all():
        if participant.student_id not in students:
            continue
        exam, b, subject, day = exams[participant.exam_id]
        groups[b].setdefault(participant.student_id, None)
        state = result.result_status if result else "pending"
        if state == "graded" and result.marks_obtained is None:
            state = "pending"
        marks = Decimal(str(result.marks_obtained)) if result and state == "graded" else None
        entries[(b, participant.student_id, subject)].append((state, marks, Decimal(str(exam.max_marks)), exam.status))
        detail_rows.append((b, participant.admission_number, participant.full_name, day, exam.name, subject,
                            marks, exam.max_marks, state, exam.status, exam.id))
    policy_text = {"unconfirmed": "Unconfirmed: percentages with absences are blank", "zero": "Absent = zero, maximum included", "exclude": "Absent exams excluded from numerator and denominator"}[absence_policy]
    scope = (f"Dates: {start or 'beginning'} to {end or 'latest'} (IST). {policy_text}. "
             "Only published graded scores enter totals. Pending/withheld/unpublished results are excluded and marked Partial. Totals cover counted exams only, not a complete P/C/M total.")
    headings = ["Sr No", "Name"]
    for subject in SUBJECTS:
        headings += [f"{subject} obtained", f"{subject} max", f"{subject} status"]
    headings += ["Total obtained", "Total maximum", "Marks %", "Result completeness", "Admission number", "Percentage basis"]
    sheets = []
    for b in BATCHES:
        rows = []
        for sid in sorted(groups[b], key=lambda x: (students[x].full_name.casefold(), x)):
            row = [len(rows) + 1, students[sid].full_name]
            obtained, maximum = Decimal(0), Decimal(0)
            partial, unresolved_absence, has_records = False, False, False
            for subject in SUBJECTS:
                records = entries.get((b, sid, canonical_subject(subject)), [])
                if not records:
                    applicable = canonical_subject(subject) in selected[sid]
                    row += [None, None, "No exam in range" if applicable else "Not applicable" if selected[sid] else "No eligible exam; selection unknown"]
                    partial |= applicable
                    continue
                has_records = True
                score, max_score = Decimal(0), Decimal(0)
                states = defaultdict(int)
                counted = 0
                for state, marks, max_marks, publication in records:
                    states[state] += 1
                    if publication != "published":
                        states["unpublished"] += 1
                        partial = True
                        continue
                    if state == "graded":
                        score += marks
                        max_score += max_marks
                        counted += 1
                    elif state == "absent":
                        if absence_policy == "zero":
                            max_score += max_marks
                            counted += 1
                        elif absence_policy == "unconfirmed":
                            unresolved_absence = True
                            partial = True
                    else:
                        partial = True
                obtained += score
                maximum += max_score
                row += [score if counted else None, max_score if counted else None, "; ".join(f"{key.title()}: {value}" for key, value in sorted(states.items()))]
            other = {subject for batch, person, subject in entries if batch == b and person == sid} - {canonical_subject(s) for s in SUBJECTS}
            partial |= bool(other)  # Retained in detail, not silently folded into P/C/M/B.
            has_records |= bool(other)
            row += [obtained if maximum else None, maximum if maximum else None,
                    obtained / maximum if maximum and not unresolved_absence else None,
                    "Partial" if partial and has_records else "Complete (recorded exams)" if has_records else "No results in range",
                    students[sid].admission_number, policy_text + ("; other subjects in detail, excluded" if other else "")]
            rows.append(row)
        sheets.append((b, headings, rows, scope))
    return sheets + [("Exam detail", ["Batch", "Admission number", "Name", "Exam date", "Exam", "Subject", "Marks obtained", "Maximum marks", "Result status", "Publication status", "Exam ID"],
                      sorted(detail_rows, key=lambda r: (r[0], r[2].casefold(), r[3], r[4])),
                      "Eligibility uses each exam's saved participant roster, including former students. Cancelled exams excluded. Missing results are pending. Current subject selections identify subjects without exams; unknown selections are not inferred.")]
