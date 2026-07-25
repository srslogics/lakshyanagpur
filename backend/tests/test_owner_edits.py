from datetime import date

import pytest

from app.models import AuditLog, Enrollment, FeeAgreement, PaymentTransaction, Room, Student, User


def _student_record(database):
    student = Student(
        admission_number="LI-2026-00001",
        full_name="Original Student",
        mobile="9000000001",
        secondary_mobile="9000000002",
        email="student@example.com",
        previous_school="Old School",
        status="active",
        data_quality_status="ready",
    )
    database.add(student)
    database.flush()
    enrollment = Enrollment(
        student_id=student.id,
        program="JEE",
        batch="Tatva",
        enrollment_date=date(2026, 6, 1),
        status="active",
        is_active=True,
    )
    database.add(enrollment)
    database.commit()
    return student, enrollment


def test_owner_can_edit_student_and_non_owner_cannot(client, database, owner_headers, parent_headers):
    student, enrollment = _student_record(database)
    payload = {
        "admissionNumber": "LI-2026-00042",
        "fullName": "Updated Student",
        "mobile": "9111111111",
        "secondaryMobile": None,
        "email": "updated@example.com",
        "previousSchool": "New School",
        "status": "inactive",
        "dataQualityStatus": "review",
        "program": "NEET",
        "batch": "Essential",
        "enrollmentDate": "2026-07-10",
    }

    response = client.patch(f"/api/students/{student.id}", json=payload, headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["fullName"] == "Updated Student"
    assert response.json()["program"] == "NEET"
    assert response.json()["email"] == "updated@example.com"

    database.refresh(student)
    database.refresh(enrollment)
    assert student.admission_number == "LI-2026-00042"
    assert student.status == "inactive"
    assert enrollment.batch == "Essential"
    assert enrollment.is_active is False
    assert database.query(AuditLog).filter_by(action="students.update", entity_id=student.id).count() == 1

    denied = client.patch(f"/api/students/{student.id}", json=payload, headers=parent_headers)
    assert denied.status_code == 403


def test_owner_can_edit_fee_agreement_and_only_review_imported_payment(
    client, database, owner_headers, parent_headers
):
    student, enrollment = _student_record(database)
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        legacy_import_id="admission-row-1",
        agreed_amount=100000,
        legacy_registration_total=5000,
        currency="INR",
        status="active",
    )
    database.add(agreement)
    database.flush()
    payment = PaymentTransaction(
        student_id=student.id,
        fee_agreement_id=agreement.id,
        legacy_import_id="admission-row-1",
        legacy_line_number=1,
        transaction_date=None,
        amount=20000,
        method="cash",
        transaction_type="payment",
        source_note="Imported source entry",
        status="staged",
        reconciliation_status="review",
    )
    database.add(payment)
    database.commit()

    agreement_response = client.patch(
        f"/api/finance/agreements/{agreement.id}",
        json={
            "agreedAmount": 95000,
            "legacyRegistrationTotal": 5000,
            "currency": "inr",
            "status": "active",
        },
        headers=owner_headers,
    )
    assert agreement_response.status_code == 200
    assert agreement_response.json()["agreedAmount"] == 95000
    assert agreement_response.json()["currency"] == "INR"

    review_response = client.patch(
        f"/api/finance/staged-payments/{payment.id}/review",
        json={"reconciliationStatus": "ready"},
        headers=owner_headers,
    )
    assert review_response.status_code == 200
    database.refresh(payment)
    assert payment.reconciliation_status == "ready"
    assert payment.amount == 20000
    assert payment.transaction_date is None

    database.delete(payment)
    with pytest.raises(ValueError, match="immutable"):
        database.commit()
    database.rollback()

    denied = client.patch(
        f"/api/finance/staged-payments/{payment.id}/review",
        json={"reconciliationStatus": "do_not_import"},
        headers=parent_headers,
    )
    assert denied.status_code == 403


def test_owner_can_edit_master_data_and_last_owner_is_protected(
    client, database, owner_headers, parent_headers
):
    room = Room(name="Room 1", capacity=40, is_active=True)
    database.add(room)
    database.commit()

    response = client.patch(
        f"/api/settings/rooms/{room.id}",
        json={"name": "Room A", "capacity": 60, "isActive": False},
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": room.id,
        "name": "Room A",
        "capacity": 60,
        "isActive": False,
    }

    denied = client.patch(
        f"/api/settings/rooms/{room.id}",
        json={"name": "Room B", "capacity": 70, "isActive": True},
        headers=parent_headers,
    )
    assert denied.status_code == 403

    owner = database.query(User).filter_by(role="owner").one()
    protected = client.patch(
        f"/api/settings/users/{owner.id}",
        json={
            "fullName": owner.full_name,
            "mobile": owner.mobile,
            "email": owner.email,
            "role": "owner",
            "isActive": False,
            "password": None,
        },
        headers=owner_headers,
    )
    assert protected.status_code == 409
