from datetime import date

import pytest

from app.models import (
    AuditLog,
    Enrollment,
    FeeAgreement,
    FeeInstallment,
    ParentAccount,
    PaymentTransaction,
    Room,
    Student,
    StudentAccount,
    User,
)


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


def test_opt_out_closes_future_fee_liability_and_reactivation_restores_it(
    client, database, owner_headers
):
    student, enrollment = _student_record(database)
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        agreed_amount=100000,
        legacy_registration_total=30000,
        currency="INR",
        status="active",
    )
    database.add(agreement)
    database.flush()
    database.add(
        PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            transaction_date=date(2026, 7, 1),
            amount=30000,
            method="upi",
            transaction_type="payment",
            source_note="ERP payment receipt",
            status="posted",
            reconciliation_status="ready",
        )
    )
    installment = FeeInstallment(
        student_id=student.id,
        fee_agreement_id=agreement.id,
        due_date=date(2026, 9, 1),
        amount=20000,
        expected_method="not_decided",
        notes="Future collection",
        status="scheduled",
        created_by=database.query(User).filter_by(role="owner").one().id,
    )
    student_user = User(
        mobile="9000000003",
        full_name="Student login",
        role="student",
        password_hash="unused-in-test",
    )
    parent_user = database.query(User).filter_by(role="parent_student").one()
    database.add_all([installment, student_user])
    database.flush()
    database.add_all(
        [
            StudentAccount(user_id=student_user.id, student_id=student.id),
            ParentAccount(
                user_id=parent_user.id,
                student_id=student.id,
                contact_type="primary_contact",
            ),
        ]
    )
    database.commit()

    opted_out = client.patch(
        f"/api/students/{student.id}/status",
        json={"status": "inactive", "reason": "Student discontinued the course"},
        headers=owner_headers,
    )
    assert opted_out.status_code == 200
    assert opted_out.json()["lifecycle"] == {
        "adjustmentAmount": 70000,
        "cancelledInstallments": 1,
        "portalAccounts": 2,
    }
    database.refresh(student)
    database.refresh(enrollment)
    database.refresh(agreement)
    database.refresh(installment)
    database.refresh(student_user)
    database.refresh(parent_user)
    assert student.status == "inactive"
    assert enrollment.is_active is False
    assert agreement.status == "inactive"
    assert installment.status == "cancelled"
    assert student_user.is_active is False
    assert parent_user.is_active is False
    closure = database.query(PaymentTransaction).filter_by(
        fee_agreement_id=agreement.id,
        transaction_type="balance_credit",
    ).one()
    assert closure.amount == 70000
    assert closure.source_note == "Student opt-out fee closure"

    reactivated = client.patch(
        f"/api/students/{student.id}/status",
        json={"status": "active", "reason": "Student rejoined the course"},
        headers=owner_headers,
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["lifecycle"]["adjustmentAmount"] == 70000
    database.refresh(agreement)
    database.refresh(installment)
    database.refresh(student_user)
    database.refresh(parent_user)
    assert agreement.status == "active"
    assert installment.status == "cancelled"
    assert student_user.is_active is True
    assert parent_user.is_active is True
    restoration = database.query(PaymentTransaction).filter_by(
        fee_agreement_id=agreement.id,
        transaction_type="balance_debit",
    ).one()
    assert restoration.amount == 70000
    assert restoration.source_note == "Student reactivation fee restoration"


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
        json={
            "reconciliationStatus": "ready",
            "transactionDate": "2026-01-21",
            "method": "cash",
        },
        headers=owner_headers,
    )
    assert review_response.status_code == 200
    database.refresh(payment)
    assert payment.reconciliation_status == "ready"
    assert payment.amount == 20000
    assert payment.transaction_date.isoformat() == "2026-01-21"

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
