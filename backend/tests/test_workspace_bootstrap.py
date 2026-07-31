from datetime import date

from sqlalchemy import event

from app.models import (
    Enrollment,
    FeeAgreement,
    FeeInstallment,
    Lead,
    PaymentTransaction,
    Student,
    User,
)


def test_owner_workspace_bootstrap_replaces_separate_initial_requests(
    client,
    database,
    owner_headers,
    parent_headers,
):
    owner = database.query(User).filter_by(role="owner").one()
    student = Student(
        admission_number="LI-2026-09001",
        full_name="Fast Bootstrap Student",
        mobile="9876509001",
        status="active",
        data_quality_status="ready",
    )
    database.add(student)
    database.flush()
    enrollment = Enrollment(
        student_id=student.id,
        program="JEE",
        batch="Tatva",
        enrollment_date=date(2026, 7, 29),
        status="active",
        is_active=True,
    )
    database.add(enrollment)
    database.flush()
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        agreed_amount=80000,
        legacy_registration_total=2000,
        currency="INR",
        status="active",
    )
    database.add(agreement)
    database.flush()
    database.add_all([
        PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            transaction_date=date(2026, 7, 20),
            amount=5000,
            method="upi",
            transaction_type="payment",
            source_note="ERP payment receipt",
            status="posted",
            reconciliation_status="ready",
        ),
        FeeInstallment(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            due_date=date(2026, 8, 20),
            amount=10000,
            expected_method="upi",
            notes="Second instalment",
            status="scheduled",
            created_by=owner.id,
        ),
        Lead(
            student="Future Student",
            mobile="9876509002",
            parent="Parent Name",
            program="NEET",
            source="phone",
            counsellor="Owner",
            stage="New Enquiry",
            priority="medium",
            next_action="Call parent",
            summary="",
        ),
    ])
    database.commit()

    statements = []

    def record_statement(*args):
        statements.append(args[2])

    event.listen(database.bind, "before_cursor_execute", record_statement)
    try:
        response = client.get("/api/workspace/bootstrap", headers=owner_headers)
    finally:
        event.remove(database.bind, "before_cursor_execute", record_statement)

    assert response.status_code == 200
    body = response.json()
    assert [item["fullName"] for item in body["students"]] == ["Fast Bootstrap Student"]
    assert body["agreements"][0]["agreedAmount"] == 80000
    assert body["payments"][0]["signedAmount"] == 5000
    assert body["installments"][0]["amount"] == 10000
    assert body["leads"][0]["student"] == "Future Student"
    assert body["admissionsMeta"]["stageOrder"][0] == "New Enquiry"
    assert len(statements) <= 7

    denied = client.get("/api/workspace/bootstrap", headers=parent_headers)
    assert denied.status_code == 403
