from datetime import datetime
from zoneinfo import ZoneInfo

from app.models import AuditLog, Enrollment, FeeAgreement, PaymentTransaction, Student


def _account(database):
    student = Student(
        admission_number="LI-2026-00801",
        full_name="Ledger Student",
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
        agreed_amount=100000,
        legacy_registration_total=0,
        currency="INR",
        status="active",
    )
    database.add(agreement)
    database.commit()
    return student


def test_accounts_post_payment_and_owner_reverses_with_append_only_receipts(
    client,
    database,
    owner_headers,
):
    student = _account(database)
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    posted = client.post(
        "/api/finance/payments",
        json={
            "studentId": student.id,
            "transactionDate": today,
            "amount": 25000,
            "method": "upi",
            "reference": "UTR-123",
            "notes": "First instalment",
        },
        headers=owner_headers,
    )
    assert posted.status_code == 201
    payment = posted.json()
    assert payment["receiptNumber"].startswith("LI-RCPT-")
    assert payment["signedAmount"] == 25000
    assert payment["status"] == "posted"

    reversed_response = client.post(
        f"/api/finance/payments/{payment['id']}/reverse",
        json={
            "transactionDate": today,
            "kind": "reversal",
            "amount": 25000,
            "reason": "Duplicate collection",
        },
        headers=owner_headers,
    )
    assert reversed_response.status_code == 201
    reversal = reversed_response.json()
    assert reversal["receiptNumber"].startswith("LI-CN-")
    assert reversal["signedAmount"] == -25000
    assert reversal["relatedTransactionId"] == payment["id"]

    register = client.get("/api/finance/transactions", headers=owner_headers)
    assert register.status_code == 200
    assert register.json()["total"] == 2
    assert database.query(PaymentTransaction).count() == 2
    assert database.query(AuditLog).filter(
        AuditLog.action.in_(("finance.payment.post", "finance.payment.reversal"))
    ).count() == 2


def test_create_fee_agreement_for_existing_manual_student(
    client,
    database,
    owner_headers,
):
    student = Student(
        admission_number="LI-2026-00802",
        full_name="Manual Account",
        status="active",
    )
    database.add(student)
    database.flush()
    database.add(
        Enrollment(
            student_id=student.id,
            program="Boards",
            batch="Essential",
            status="active",
            is_active=True,
        )
    )
    database.commit()

    response = client.post(
        "/api/finance/agreements",
        json={
            "studentId": student.id,
            "agreedAmount": 40000,
            "currency": "INR",
            "status": "active",
        },
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["agreedAmount"] == 40000
    assert response.json()["legacyRegistrationTotal"] == 0
