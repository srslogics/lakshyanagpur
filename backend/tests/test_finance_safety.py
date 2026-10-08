from datetime import date, timedelta

from app.models import FeeAgreement, FeeInstallment, PaymentTransaction
from app.routers.portal import fee_summary
from app.services import payment_effect
from test_finance_posting import _account


def post(client, headers, student, **changes):
    data = dict(studentId=student.id, transactionDate="2026-08-01", amount=1000, method="cash")
    data.update(changes)
    return client.post("/api/finance/payments", json=data, headers=headers)


def test_request_replay_and_mismatched_payload(client, database, owner_headers):
    student = _account(database)
    headers = {**owner_headers, "Idempotency-Key": "payment-test-key-0001"}
    first = post(client, headers, student)
    second = post(client, headers, student)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert database.query(PaymentTransaction).count() == 1
    assert post(client, headers, student, amount=2000).status_code == 409


def snapshot(database, student):
    agreement = database.query(FeeAgreement).filter_by(student_id=student.id).one()
    database.add(PaymentTransaction(student_id=student.id, fee_agreement_id=agreement.id,
        transaction_date=date(2026, 8, 3), amount=5000, method="client_statement",
        transaction_type="balance_credit", source_note="Confirmed balance", status="posted", reconciliation_status="ready"))
    database.commit()
    return agreement


def test_void_historical_receipt_restores_balance(client, database, owner_headers):
    student = _account(database)
    snapshot(database, student)
    payment = post(client, owner_headers, student).json()
    result = client.post(f"/api/finance/payments/{payment['id']}/reverse", headers=owner_headers,
        json=dict(transactionDate="2026-08-04", kind="void", reason="Duplicate entry"))
    assert result.status_code == 201
    assert sum(map(payment_effect, database.query(PaymentTransaction).all())) == 5000


def test_review_exclusion_and_reapproval_rebalance(client, database, owner_headers):
    student = _account(database)
    agreement = snapshot(database, student)
    row = PaymentTransaction(student_id=student.id, fee_agreement_id=agreement.id,
        transaction_date=date(2026, 8, 1), amount=1000, method="cash", transaction_type="payment",
        source_note="Imported", status="staged", reconciliation_status="review")
    database.add(row); database.commit()
    url = f"/api/finance/staged-payments/{row.id}/review"
    for state in ("ready", "do_not_import", "ready"):
        response = client.patch(url, headers=owner_headers, json={"reconciliationStatus": state})
        assert response.status_code == 200
        assert sum(map(payment_effect, database.query(PaymentTransaction).all())) == 5000
    response = client.patch(url, headers=owner_headers,
        json={"reconciliationStatus": "ready", "transactionDate": "2026-08-05"})
    assert response.status_code == 200
    assert sum(map(payment_effect, database.query(PaymentTransaction).all())) == 6000


def test_portal_refund_sign_and_credit(client, database, owner_headers):
    student = _account(database)
    payment = post(client, owner_headers, student, amount=110000).json()
    response = client.post(f"/api/finance/payments/{payment['id']}/reverse", headers=owner_headers,
        json=dict(transactionDate="2026-08-04", kind="refund", amount=1000, reason="Return excess"))
    assert response.status_code == 201
    fees = fee_summary(database, student)
    assert fees["creditAmount"] == 9000
    assert fees["payments"][0]["type"] == "refund"
    assert fees["payments"][0]["signedAmount"] == -1000


def test_fee_amendment_retains_history(client, database, owner_headers):
    student = _account(database)
    agreement = database.query(FeeAgreement).filter_by(student_id=student.id).one()
    result = client.patch(f"/api/finance/agreements/{agreement.id}", headers=owner_headers,
        json=dict(agreedAmount=90000, legacyRegistrationTotal=0, currency="INR", status="active"))
    assert result.status_code == 200
    amendment = database.query(PaymentTransaction).one()
    assert amendment.transaction_type == "fee_concession"
    assert amendment.amount == 10000
    assert payment_effect(amendment) == 0  # Agreed fee already contains the amendment.


def test_closed_account_cannot_restore_schedule(client, database, owner_headers):
    student = _account(database)
    agreement = database.query(FeeAgreement).filter_by(student_id=student.id).one()
    scheduled = client.post("/api/finance/installments", headers=owner_headers,
        json=dict(studentId=student.id, dueDate=(date.today() + timedelta(days=2)).isoformat(), amount=1000)).json()
    agreement.status = "inactive"
    row = database.get(FeeInstallment, scheduled["id"])
    row.status = "cancelled"
    database.commit()
    result = client.patch(f"/api/finance/installments/{row.id}", headers=owner_headers,
        json=dict(dueDate=(date.today() + timedelta(days=2)).isoformat(), amount=1000, status="scheduled"))
    assert result.status_code == 409


def test_future_import_cannot_be_approved(client, database, owner_headers):
    student = _account(database)
    agreement = database.query(FeeAgreement).filter_by(student_id=student.id).one()
    row = PaymentTransaction(student_id=student.id, fee_agreement_id=agreement.id,
        transaction_date=date.today() + timedelta(days=5), amount=1000, method="cash",
        transaction_type="payment", source_note="Import", status="staged", reconciliation_status="review")
    database.add(row); database.commit()
    result = client.patch(f"/api/finance/staged-payments/{row.id}/review", headers=owner_headers,
        json={"reconciliationStatus": "ready"})
    assert result.status_code == 422


def test_refund_retry_does_not_refund_twice(client, database, owner_headers):
    student = _account(database)
    payment = post(client, owner_headers, student).json()
    headers = {**owner_headers, "Idempotency-Key": "refund-test-key-00001"}
    body = dict(transactionDate="2026-08-04", kind="refund", amount=100, reason="Partial refund")
    first = client.post(f"/api/finance/payments/{payment['id']}/reverse", headers=headers, json=body)
    second = client.post(f"/api/finance/payments/{payment['id']}/reverse", headers=headers, json=body)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert database.query(PaymentTransaction).filter_by(transaction_type="refund").count() == 1
