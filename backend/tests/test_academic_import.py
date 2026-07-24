import json
from pathlib import Path

import pytest

from app.importers.academic_workbook import import_manifest as import_academic_manifest
from app.importers.legacy_admissions import import_manifest as import_admission_manifest
from app.models import (
    AcademicImportBatch,
    AcademicSourceRecord,
    DailyAttendanceEntry,
    Enrollment,
    Student,
    StudentAccount,
    StudentAcademicProfile,
    StudentSubjectSelection,
    User,
)


DATA_DIR = Path(__file__).parents[1] / "data" / "imports"
ADMISSIONS = DATA_DIR / "admission_2026_27.json"
ACADEMICS = DATA_DIR / "demo_attendance_2026.json"
pytestmark = pytest.mark.skipif(
    not ADMISSIONS.exists() or not ACADEMICS.exists(),
    reason="Private workbook manifests are intentionally excluded from the repository",
)


def load(path):
    return json.loads(path.read_text())


def test_full_academic_workbook_import_reconciles_and_is_idempotent(database):
    import_admission_manifest(database, load(ADMISSIONS))
    first = import_academic_manifest(database, load(ACADEMICS))
    second = import_academic_manifest(database, load(ACADEMICS))

    assert first == {
        "batch_id": first["batch_id"],
        "idempotent_rerun": False,
        "active_students": 64,
        "batch_counts": {"Tatva": 24, "Essential": 40},
        "mentor_assignments": 64,
        "subject_selections": 219,
        "attendance_entries": 1024,
        "attendance_marks": {"P": 691, "A": 288, "X": 45},
        "source_records": 434,
        "unresolved_items": first["unresolved_items"],
    }
    assert second == {**first, "idempotent_rerun": True}
    assert database.query(AcademicImportBatch).count() == 1


def test_import_links_existing_students_without_overwriting_admission_program(database):
    import_admission_manifest(database, load(ADMISSIONS))
    import_academic_manifest(database, load(ACADEMICS))

    nancy = database.query(Student).filter_by(legacy_import_id="LEGACY-ADM-2026-A-003").one()
    enrollment = database.query(Enrollment).filter_by(student_id=nancy.id, is_active=True).one()
    profile = database.get(StudentAcademicProfile, nancy.id)
    subjects = {
        row.subject_name
        for row in database.query(StudentSubjectSelection).filter_by(student_id=nancy.id)
    }
    assert enrollment.program == "MHT-CET"
    assert enrollment.batch == "Tatva"
    assert profile.source_student_code == "T-03"
    assert profile.source_stream == "NEET"
    assert profile.mentor_name == "Sneha"
    assert subjects == {"Chemistry", "Physics", "Biology"}
    assert database.query(Student).count() == 70


def test_ambiguous_values_are_preserved_without_inventing_meaning(database):
    import_admission_manifest(database, load(ADMISSIONS))
    import_academic_manifest(database, load(ACADEMICS))

    unknown = database.query(DailyAttendanceEntry).filter_by(raw_status="X").all()
    assert len(unknown) == 45
    assert all(row.normalized_status is None for row in unknown)
    assert all(row.attendance_date is None for row in unknown)
    sheets = {
        row.source_sheet
        for row in database.query(AcademicSourceRecord).all()
    }
    assert sheets == {
        "Tatva Attendance",
        "Essential Attendance",
        "Attendance Sheet",
        "Mentor",
        "Pivot Table 5",
        "Subject",
        "Upto 30 June Attendance",
        "TimeTable",
    }
    staged_history = (
        database.query(AcademicSourceRecord)
        .filter_by(record_type="historical_attendance_or_lead")
        .count()
    )
    assert staged_history == 124


def test_academic_profile_is_visible_in_student_record_api(
    client,
    owner_headers,
    database,
):
    import_admission_manifest(database, load(ADMISSIONS))
    import_academic_manifest(database, load(ACADEMICS))
    kamal = database.query(Student).filter_by(legacy_import_id="LEGACY-ADM-2026-A-001").one()

    response = client.get(f"/api/students/{kamal.id}", headers=owner_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["enrollment"]["batch"] == "Tatva"
    assert payload["academicProfile"] == {
        "sourceStudentCode": "T-01",
        "batch": "Tatva",
        "sourceStream": "JEE",
        "mentorName": "Sneha",
        "sourceSchoolName": "Saraswati",
        "sourcePrimaryMobile": "9158178887",
        "sourceSecondaryMobile": None,
        "subjects": ["Chemistry", "Maths", "Physics"],
    }


def test_student_portal_shows_imported_attendance_and_excludes_x_from_rate(
    client,
    parent_headers,
    database,
):
    import_admission_manifest(database, load(ADMISSIONS))
    import_academic_manifest(database, load(ACADEMICS))
    student = database.query(Student).filter_by(
        legacy_import_id="LEGACY-ADM-2026-A-058"
    ).one()
    account = database.query(User).filter_by(role="parent_student").one()
    database.add(StudentAccount(user_id=account.id, student_id=student.id))
    database.commit()

    response = client.get("/api/portal/bootstrap", headers=parent_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["profile"]["batch"] == "Tatva"
    assert payload["summary"]["attendanceRate"] == 75.0
    assert len(payload["attendance"]) == 16
    assert sum(row["status"] == "unclassified" for row in payload["attendance"]) == 4
    assert all(row["dateLabel"] for row in payload["attendance"])


def test_owner_can_import_reviewed_academic_manifest_through_settings(
    client,
    owner_headers,
    database,
):
    import_admission_manifest(database, load(ADMISSIONS))
    response = client.post(
        "/api/settings/imports/academic",
        headers=owner_headers,
        json=load(ACADEMICS),
    )
    assert response.status_code == 200
    assert response.json()["active_students"] == 64
    settings = client.get("/api/settings/bootstrap", headers=owner_headers)
    assert settings.status_code == 200
    imported = settings.json()["academicImports"][0]
    assert imported["activeStudents"] == 64
    assert imported["attendanceEntries"] == 1024
