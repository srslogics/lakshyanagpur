from datetime import date, datetime, timezone

import pytest

from app.models import (
    AttendanceEntry, AttendanceRegister, Batch, Enrollment, Examination,
    ExaminationParticipant, ExaminationResult, Student, StudentSubjectSelection,
    Subject, User,
)
from test_report_exports import _workbook


def people(db):
    owner = db.query(User).filter_by(role="owner").one()
    students = [Student(admission_number=f"SUMMARY-{i}", full_name=name, status="active", is_test_account=i == 3)
                for i, name in enumerate(["Alice", "Bob", "Cara", "Demo"])]
    db.add_all(students)
    db.flush()
    for i, student in enumerate(students):
        db.add(Enrollment(student_id=student.id, batch="Essential" if i == 2 else "Tatva", program="JEE", status="active", enrollment_date=date(2026, 9, 1)))
    db.commit()
    return owner, students


def rows(sheet):
    headings = [cell.value for cell in sheet[6]]
    return [dict(zip(headings, row)) for row in sheet.iter_rows(min_row=7, values_only=True)]


def test_attendance_deduplicates_conflicts_gaps_and_unknowns(client, database, owner_headers):
    owner, students = people(database)
    def register(day, kind, statuses, status="submitted"):
        reg = AttendanceRegister(attendance_date=date(2026, 9, day), batch_name="Tatva", register_kind=kind, status=status)
        database.add(reg)
        database.flush()
        for sid, state in statuses:
            database.add(AttendanceEntry(register_id=reg.id, student_id=students[sid].id, status=state, marked_by=owner.id))
    register(1, "manual", [(0, "present"), (1, "absent"), (3, "present")])
    register(1, "biometric", [(0, "late"), (1, "absent")])
    register(2, "manual", [(0, "absent"), (1, "present")])
    register(2, "biometric", [(0, "present")])
    register(3, "manual", [(0, "excused")])
    register(4, "manual", [(0, "absent")], status="draft")
    register(5, "manual", [(0, "absent")])
    database.commit()
    book = _workbook(client, owner_headers, "attendance-summary", "&from=2026-09-01&to=2026-09-05")
    alice, bob = rows(book["Tatva"])
    assert alice["Recorded attendance days"] == 4
    assert alice["Days present"] == 1
    assert alice["Days absent"] == 1
    assert alice["Attendance %"] == 0.5
    assert alice["Excused days"] == 1
    assert alice["Conflict days"] == 1
    assert bob["Missing on batch dates"] == 2
    assert rows(book["Essential"])[0]["Attendance %"] is None
    coverage = rows(book["Date coverage"])
    assert next(r for r in coverage if r["Batch"] == "Tatva" and r["Date"].day == 4)["Coverage"].startswith("No daily records")
    evidence = rows(book["Daily evidence"])
    assert len([r for r in evidence if r["Name"] == "Alice" and r["Date"].day == 1]) == 1
    assert evidence[0]["Duplicate rows collapsed"] == 1
    assert book["Tatva"]["F7"].number_format == "0.0%"
    assert all(r["Name"] != "Demo" for r in rows(book["Tatva"]))


def exam_data(db):
    owner, students = people(db)
    batch = Batch(name="Tatva", program="JEE")
    db.add(batch)
    db.flush()
    def exam(subject_name, status, results, when=None):
        subject = Subject(name=subject_name, code=f"SUM-{subject_name}", program="JEE")
        db.add(subject)
        db.flush()
        exam = Examination(name=f"{subject_name} test", batch_id=batch.id, subject_id=subject.id, faculty_id=owner.id,
                           created_by=owner.id, scheduled_at=when or datetime(2026, 9, 10, 4, tzinfo=timezone.utc),
                           max_marks=100, pass_marks=40, status=status)
        db.add(exam)
        db.flush()
        for i, state, score in results:
            student = students[i]
            db.add(ExaminationParticipant(exam_id=exam.id, student_id=student.id, full_name=student.full_name, admission_number=student.admission_number))
            if state:
                db.add(ExaminationResult(exam_id=exam.id, student_id=student.id, marks_obtained=score, result_status=state, entered_by=owner.id))
        return exam
    exam("Physics", "published", [(0, "graded", -4.25), (1, "graded", 0), (3, "graded", 100)])
    exam("Chemistry", "published", [(0, "absent", None), (1, None, None)])
    exam("Maths", "published", [(0, "withheld", None)])
    exam("Biology", "scheduled", [(0, "graded", 90)])
    for subject in ("Physics", "Chemistry", "Maths", "Biology"):
        db.add(StudentSubjectSelection(student_id=students[0].id, subject_name=subject, source_value="yes"))
    db.add(StudentSubjectSelection(student_id=students[1].id, subject_name="Maths", source_value="yes"))
    db.commit()
    return exam, students


@pytest.mark.parametrize("policy,maximum,percentage", [("unconfirmed", 100, None), ("zero", 200, -0.02125), ("exclude", 100, -0.0425)])
def test_exam_totals_negative_scores_and_explicit_absence_policy(client, database, owner_headers, policy, maximum, percentage):
    exam_data(database)
    book = _workbook(client, owner_headers, "exam-summary", f"&month=2026-09&absencePolicy={policy}")
    alice, bob = rows(book["Tatva"])
    assert alice["Total obtained"] == -4.25
    assert alice["Total maximum"] == maximum
    assert alice["Marks %"] == percentage
    assert alice["Result completeness"] == "Partial"
    assert alice["Maths status"] == "Withheld: 1"
    assert "Unpublished: 1" in alice["Biology status"]
    assert alice["Biology obtained"] is None
    assert bob["Physics obtained"] == 0
    assert bob["Chemistry status"] == "Pending: 1"
    assert bob["Maths status"] == "No exam in range"
    assert bob["Result completeness"] == "Partial"
    assert len(rows(book["Tatva"])) == 2
    assert book["Tatva"]["Q7"].number_format == "0.0%"


def test_exam_ist_dates_cancelled_and_historical_roster(client, database, owner_headers):
    make_exam, students = exam_data(database)
    make_exam("phy", "published", [(0, "graded", 50)], datetime(2026, 9, 30, 18, 30, tzinfo=timezone.utc))
    make_exam("chem", "cancelled", [(0, "graded", 100)], datetime(2026, 9, 30, 18, 30, tzinfo=timezone.utc))
    students[0].status = "inactive"
    database.commit()
    book = _workbook(client, owner_headers, "exam-summary", "&from=2026-10-01&to=2026-10-01")
    alice = next(r for r in rows(book["Tatva"]) if r["Name"] == "Alice")
    assert alice["Physics obtained"] == 50
    assert alice["Total maximum"] == 100
    assert len(rows(book["Exam detail"])) == 1


@pytest.mark.parametrize("report", ["attendance-summary", "exam-summary"])
def test_summary_filters_formats_and_permissions(client, owner_headers, parent_headers, report):
    root = f"/api/reports/export/{report}?format=xlsx"
    for suffix in ("&month=invalid", "&month=2026-09&from=2026-09-01", "&from=2026-10-01&to=2026-09-01", "&absencePolicy=invalid"):
        assert client.get(root + suffix, headers=owner_headers).status_code == 422
    assert client.get(root, headers=parent_headers).status_code == 403
    assert client.get(f"/api/reports/export/{report}?format=csv", headers=owner_headers).status_code == 422


def test_summary_month_matches_equivalent_range(client, database, owner_headers):
    exam_data(database)
    for report in ("attendance-summary", "exam-summary"):
        monthly = _workbook(client, owner_headers, report, "&month=2026-09")
        ranged = _workbook(client, owner_headers, report, "&from=2026-09-01&to=2026-09-30")
        for name in monthly.sheetnames:
            assert rows(monthly[name]) == rows(ranged[name])


def test_other_subject_results_are_partial_not_missing(client, database, owner_headers):
    make_exam, _ = exam_data(database)
    make_exam("English", "published", [(0, "graded", 75)], datetime(2026, 10, 2, 4, tzinfo=timezone.utc))
    database.commit()
    book = _workbook(client, owner_headers, "exam-summary", "&month=2026-10")
    alice = next(r for r in rows(book["Tatva"]) if r["Name"] == "Alice")
    assert alice["Result completeness"] == "Partial"
    assert alice["Total obtained"] is None
    assert rows(book["Exam detail"])[0]["Marks obtained"] == 75
