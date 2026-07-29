from datetime import date

from app.models import Enrollment, FeeAgreement, PaymentTransaction, Student, User
from app.security import create_token, hash_password


def _finance_records(db):
    student = Student(
        admission_number="LI-2026-00991",
        full_name="Export Student",
        mobile="9000000991",
        status="active",
    )
    db.add(student)
    db.flush()
    enrollment = Enrollment(
        student_id=student.id,
        program="JEE",
        batch="Tatva",
        enrollment_date=date(2026, 7, 1),
        status="active",
        is_active=True,
    )
    db.add(enrollment)
    db.flush()
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        agreed_amount=80_000,
        legacy_registration_total=0,
        currency="INR",
        status="active",
    )
    db.add(agreement)
    db.flush()
    db.add(
        PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            transaction_date=date(2026, 7, 2),
            amount=5_000,
            method="upi",
            transaction_type="payment",
            source_note="ERP receipt",
            status="posted",
            reconciliation_status="ready",
        )
    )
    db.commit()


def test_owner_can_export_student_and_fee_csv(
    client,
    database,
    owner_headers,
):
    _finance_records(database)
    students = client.get(
        "/api/reports/export/students",
        headers=owner_headers,
    )
    assert students.status_code == 200
    assert students.headers["content-type"].startswith("text/csv")
    assert "lakshya-students-" in students.headers["content-disposition"]
    assert "LI-2026-00991,Export Student" in students.text
    assert ",JEE,Tatva,2026-07-01,active," in students.text

    fees = client.get("/api/reports/export/fees", headers=owner_headers)
    assert fees.status_code == 200
    assert "80000,5000,75000,INR,active" in fees.text


def test_accounts_can_export_but_students_cannot(
    client,
    database,
    parent_headers,
):
    accounts = User(
        mobile="9000000998",
        full_name="Accounts User",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    database.add(accounts)
    database.commit()
    accounts_headers = {
        "Authorization": f"Bearer {create_token(accounts)}",
    }
    assert client.get(
        "/api/reports/exports",
        headers=accounts_headers,
    ).status_code == 200
    assert client.get(
        "/api/reports/export/audit",
        headers=accounts_headers,
    ).status_code == 200
    assert client.get(
        "/api/reports/export/students",
        headers=parent_headers,
    ).status_code == 403


def test_report_date_range_validation(client, owner_headers):
    response = client.get(
        "/api/reports/export/attendance?from=2026-07-20&to=2026-07-01",
        headers=owner_headers,
    )
    assert response.status_code == 422

