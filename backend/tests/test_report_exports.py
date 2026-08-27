from datetime import date

from app.models import (
    AttendanceEntry,
    AttendancePeriodSummary,
    AttendanceRegister,
    Enrollment,
    FeeAgreement,
    PaymentTransaction,
    Student,
    User,
)
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


def test_client_balance_reconciliation_changes_balance_not_cash_received(
    client,
    database,
    owner_headers,
):
    _finance_records(database)
    agreement = database.query(FeeAgreement).one()
    student = database.query(Student).filter_by(full_name="Export Student").one()
    database.add(
        PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            legacy_import_id="client-snapshot-test",
            legacy_line_number=1,
            transaction_date=date(2026, 8, 3),
            amount=7_000,
            method="client_statement",
            transaction_type="balance_credit",
            source_note="Client-confirmed balance",
            status="posted",
            reconciliation_status="ready",
        )
    )
    database.commit()

    fees = client.get("/api/reports/export/fees", headers=owner_headers)
    assert fees.status_code == 200
    assert "80000,5000,68000,INR,active" in fees.text


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


def test_report_overview_extends_confirmed_baseline_with_new_daily_register(
    client,
    database,
    owner_headers,
):
    student = Student(
        admission_number="LI-2026-00992",
        full_name="Attendance Report Student",
        mobile="9000000992",
        status="active",
    )
    database.add(student)
    database.flush()
    database.add(
        AttendancePeriodSummary(
            student_id=student.id,
            source_student_code="T-99",
            batch_name="Tatva",
            period_start=date(2026, 7, 1),
            period_end=date(2026, 8, 3),
            present_days=2,
            absent_days=1,
            working_days=3,
            attendance_rate=66.67,
            source_name="Client workbook",
            source_reference="test.xlsx",
            status="confirmed",
        )
    )
    owner = database.query(User).filter_by(role="owner").one()
    register = AttendanceRegister(
        register_kind="manual",
        attendance_date=date(2026, 8, 18),
        batch_name="Tatva",
        stream_name="__all__",
        subject_name="Daily attendance",
        status="submitted",
        submitted_by=owner.id,
    )
    database.add(register)
    database.flush()
    database.add(
        AttendanceEntry(
            register_id=register.id,
            student_id=student.id,
            status="present",
            reason="Signed paper register",
            marked_by=owner.id,
        )
    )
    database.commit()

    response = client.get("/api/reports/overview", headers=owner_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["attendanceRate"] == 75.0
    assert {row["status"]: row["count"] for row in payload["attendance"]} == {
        "absent": 1,
        "present": 3,
    }
