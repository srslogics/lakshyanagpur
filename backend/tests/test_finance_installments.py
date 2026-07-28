from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.models import (
    AuditLog,
    Enrollment,
    FeeAgreement,
    FeeInstallment,
    PaymentTransaction,
    Student,
)


def _account(database):
    student = Student(
        admission_number="LI-2026-00901",
        full_name="Future Payment Student",
        status="active",
        data_quality_status="ready",
    )
    database.add(student)
    database.flush()
    enrollment = Enrollment(
        student_id=student.id,
        program="JEE",
        batch="Tatva",
        status="active",
        is_active=True,
    )
    database.add(enrollment)
    database.flush()
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        legacy_import_id="future-payment-student",
        agreed_amount=100000,
        legacy_registration_total=0,
        currency="INR",
        status="active",
    )
    database.add(agreement)
    database.commit()
    return student, agreement


def test_owner_can_schedule_and_edit_future_payment_without_posting_it(
    client,
    database,
    owner_headers,
):
    student, _agreement = _account(database)
    due_date = (
        datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=30)
    )
    response = client.post(
        "/api/finance/installments",
        json={
            "studentId": student.id,
            "dueDate": due_date.isoformat(),
            "amount": 25000,
            "expectedMethod": "upi",
            "notes": "Second instalment",
        },
        headers=owner_headers,
    )

    assert response.status_code == 201
    item = response.json()
    assert item["studentName"] == "Future Payment Student"
    assert item["type"] == "scheduled_payment"
    assert item["status"] == "scheduled"
    assert item["amount"] == 25000
    assert database.query(PaymentTransaction).count() == 0
    assert database.query(FeeInstallment).count() == 1

    register = client.get(
        "/api/finance/installments",
        headers=owner_headers,
    )
    assert register.status_code == 200
    assert register.json()["total"] == 1
    assert register.json()["items"][0]["date"] == due_date.isoformat()

    update = client.patch(
        f"/api/finance/installments/{item['id']}",
        json={
            "dueDate": (due_date + timedelta(days=7)).isoformat(),
            "amount": 20000,
            "expectedMethod": "bank_transfer",
            "notes": "Client revised the commitment",
            "status": "cancelled",
        },
        headers=owner_headers,
    )
    assert update.status_code == 200
    assert update.json()["status"] == "cancelled"
    assert update.json()["amount"] == 20000
    assert database.query(AuditLog).filter(
        AuditLog.action.in_(
            ["finance.installment.create", "finance.installment.update"]
        )
    ).count() == 2


def test_future_payment_requires_owner_and_non_past_date(
    client,
    database,
    owner_headers,
    parent_headers,
):
    student, _agreement = _account(database)
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    payload = {
        "studentId": student.id,
        "dueDate": (today + timedelta(days=1)).isoformat(),
        "amount": 10000,
        "expectedMethod": "not_decided",
        "notes": "",
    }

    denied = client.post(
        "/api/finance/installments",
        json=payload,
        headers=parent_headers,
    )
    assert denied.status_code == 403

    payload["dueDate"] = (today - timedelta(days=1)).isoformat()
    invalid = client.post(
        "/api/finance/installments",
        json=payload,
        headers=owner_headers,
    )
    assert invalid.status_code == 422
    assert invalid.json()["detail"] == "Future payment date cannot be in the past"
