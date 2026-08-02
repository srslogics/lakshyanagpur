from datetime import date

from app.models import AuditLog, Enrollment, FeeAgreement, Student, StudentAcademicProfile, StudentSubjectSelection


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
            "subjects": ["Physics", "Chemistry", "Mathematics"],
            "agreedAmount": 80000,
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
    academic = database.get(StudentAcademicProfile, student.id)
    agreement = database.query(FeeAgreement).filter_by(student_id=student.id).one()
    assert student.email == "new.student@example.com"
    assert enrollment.enrollment_date == date(2026, 7, 29)
    assert enrollment.source_type == "owner_entry"
    assert enrollment.is_active is True
    assert academic.batch_name == "Tatva"
    assert academic.source_stream == "JEE"
    assert agreement.agreed_amount == 80000
    assert {
        row.subject_name
        for row in database.query(StudentSubjectSelection).filter_by(student_id=student.id)
    } == {"Physics", "Chemistry", "Mathematics"}
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
        "subjects": ["Physics", "Chemistry", "Biology"],
        "agreedAmount": 75000,
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
            "subjects": ["Physics"],
            "agreedAmount": 40000,
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
            "subjects": ["Physics"],
            "agreedAmount": 40000,
        },
        headers=owner_headers,
    )
    assert blank_name.status_code == 422


def test_student_picker_is_server_filtered_and_finance_scoped(
    client,
    database,
    owner_headers,
):
    with_agreement = Student(
        admission_number="LI-2026-00101",
        full_name="Aarav Searchable",
        mobile="9876500101",
        status="active",
    )
    without_agreement = Student(
        admission_number="LI-2026-00102",
        full_name="Aarushi Searchable",
        mobile="9876500102",
        status="active",
    )
    hidden_test = Student(
        admission_number="LI-TEST-00103",
        full_name="Searchable Test Student",
        mobile="9876500103",
        status="active",
        is_test_account=True,
    )
    database.add_all([with_agreement, without_agreement, hidden_test])
    database.flush()
    enrollment = Enrollment(
        student_id=with_agreement.id,
        program="JEE",
        batch="Tatva",
        enrollment_date=date(2026, 7, 29),
        status="active",
        is_active=True,
    )
    database.add(enrollment)
    database.flush()
    database.add(FeeAgreement(
        student_id=with_agreement.id,
        enrollment_id=enrollment.id,
        agreed_amount=80000,
        legacy_registration_total=0,
        currency="INR",
        status="active",
    ))
    database.commit()

    by_mobile = client.get(
        "/api/students/picker?search=9876500101&scope=with_agreement",
        headers=owner_headers,
    )
    assert by_mobile.status_code == 200
    assert [item["id"] for item in by_mobile.json()["items"]] == [with_agreement.id]

    missing_agreement = client.get(
        "/api/students/picker?search=Searchable&scope=without_agreement",
        headers=owner_headers,
    )
    assert [item["id"] for item in missing_agreement.json()["items"]] == [without_agreement.id]
    assert all("email" not in item for item in missing_agreement.json()["items"])
