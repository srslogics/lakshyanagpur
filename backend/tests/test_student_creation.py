from datetime import date

from app.models import AuditLog, Enrollment, Student


def test_owner_creates_student_and_enrollment_atomically(
    client,
    database,
    owner_headers,
):
    response = client.post(
        "/api/students",
        json={
            "fullName": "New Student",
            "mobile": "+91 98765 43210",
            "secondaryMobile": "9123456780",
            "email": "NEW.STUDENT@example.com",
            "previousSchool": "Central School",
            "program": "JEE",
            "batch": "Tatva",
            "enrollmentDate": "2026-07-29",
            "status": "active",
        },
        headers=owner_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["admissionNumber"] == "LI-2026-00001"
    assert body["mobile"] == "9876543210"
    assert body["program"] == "JEE"
    assert body["batch"] == "Tatva"

    student = database.query(Student).one()
    enrollment = database.query(Enrollment).filter_by(student_id=student.id).one()
    assert student.email == "new.student@example.com"
    assert enrollment.enrollment_date == date(2026, 7, 29)
    assert enrollment.source_type == "owner_entry"
    assert enrollment.is_active is True
    assert database.query(AuditLog).filter_by(
        action="students.create",
        entity_id=student.id,
    ).count() == 1


def test_student_creation_requires_owner_and_unique_contact(
    client,
    database,
    owner_headers,
    parent_headers,
):
    existing = Student(
        admission_number="LI-2026-00001",
        full_name="Existing Student",
        secondary_mobile="9876543210",
        status="active",
    )
    database.add(existing)
    database.commit()
    payload = {
        "fullName": "Duplicate Contact",
        "mobile": "9876543210",
        "secondaryMobile": None,
        "email": None,
        "previousSchool": None,
        "program": "NEET",
        "batch": "Tatva",
        "enrollmentDate": "2026-07-29",
        "status": "active",
    }

    denied = client.post(
        "/api/students",
        json=payload,
        headers=parent_headers,
    )
    assert denied.status_code == 403

    duplicate = client.post(
        "/api/students",
        json=payload,
        headers=owner_headers,
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "Mobile number is already assigned to Existing Student"
    )
    assert database.query(Student).count() == 1


def test_student_creation_validates_mobile_numbers(
    client,
    owner_headers,
):
    response = client.post(
        "/api/students",
        json={
            "fullName": "Invalid Contact",
            "mobile": "12345",
            "program": "MHT-CET",
            "batch": "Essential",
            "enrollmentDate": "2026-07-29",
            "status": "draft",
        },
        headers=owner_headers,
    )

    assert response.status_code == 422

    blank_name = client.post(
        "/api/students",
        json={
            "fullName": "  ",
            "program": "JEE",
            "batch": "Tatva",
            "enrollmentDate": "2026-07-29",
        },
        headers=owner_headers,
    )
    assert blank_name.status_code == 422
