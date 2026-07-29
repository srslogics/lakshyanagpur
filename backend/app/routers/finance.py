from datetime import datetime
from secrets import token_hex
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Enrollment, FeeAgreement, FeeInstallment, PaymentTransaction, Student, User
from ..operations_schemas import (
    FeeAgreementCreate,
    FeeAgreementUpdate,
    FeeInstallmentCreate,
    FeeInstallmentUpdate,
    PaymentCreate,
    PaymentReversalCreate,
    PaymentReviewUpdate,
)
from ..security import require_roles
from ..services import audit, payment_effect

router = APIRouter(prefix="/api/finance", tags=["finance"])
FINANCE_ROLES = ("owner", "accounts", "admissions_manager")


def _india_today():
    return datetime.now(ZoneInfo("Asia/Kolkata")).date()


def _installment_payload(row: FeeInstallment, student: Student):
    return {
        "id": row.id,
        "studentId": student.id,
        "studentName": student.full_name,
        "admissionNumber": student.admission_number,
        "date": row.due_date,
        "amount": row.amount,
        "method": row.expected_method,
        "type": "scheduled_payment",
        "sourceNote": row.notes,
        "status": row.status,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
    }


def _receipt_number(kind: str = "receipt"):
    prefix = "RCPT" if kind == "receipt" else "CN"
    return f"LI-{prefix}-{_india_today().year}-{token_hex(4).upper()}"


def _transaction_effect(row: PaymentTransaction) -> int:
    return payment_effect(row)


def _payment_payload(row: PaymentTransaction, student: Student):
    return {
        "id": row.id,
        "studentId": student.id,
        "studentName": student.full_name,
        "admissionNumber": student.admission_number,
        "legacyImportId": row.legacy_import_id,
        "line": row.legacy_line_number,
        "receiptNumber": row.receipt_number,
        "date": row.transaction_date,
        "amount": row.amount,
        "signedAmount": _transaction_effect(row),
        "method": row.method,
        "type": row.transaction_type,
        "sourceNote": row.source_note,
        "reference": row.reference,
        "notes": row.notes,
        "relatedTransactionId": row.related_transaction_id,
        "status": row.status,
        "reconciliationStatus": row.reconciliation_status,
        "createdAt": row.created_at,
    }


def _create_posted_payment(
    db: Session,
    *,
    student: Student,
    agreement: FeeAgreement,
    actor: User,
    transaction_date,
    amount: int,
    method: str,
    reference: str | None,
    notes: str,
):
    row = PaymentTransaction(
        student_id=student.id,
        fee_agreement_id=agreement.id,
        receipt_number=_receipt_number(),
        transaction_date=transaction_date,
        amount=amount,
        method=method,
        transaction_type="payment",
        source_note="ERP payment receipt",
        reference=(reference or "").strip() or None,
        notes=notes.strip(),
        created_by=actor.id,
        status="posted",
        reconciliation_status="ready",
    )
    db.add(row)
    db.flush()
    return row


@router.get("/agreements")
def fee_agreements(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles(*FINANCE_ROLES))):
    query = db.query(FeeAgreement, Student).join(Student, Student.id == FeeAgreement.student_id)
    total = query.count()
    rows = query.order_by(Student.full_name).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [{"id": fee.id, "studentId": student.id, "studentName": student.full_name, "admissionNumber": student.admission_number, "agreedAmount": fee.agreed_amount, "legacyRegistrationTotal": fee.legacy_registration_total, "currency": fee.currency, "status": fee.status} for fee, student in rows], "total": total, "page": page, "pageSize": page_size}


@router.post("/agreements", status_code=201)
def create_agreement(
    payload: FeeAgreementCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*FINANCE_ROLES)),
):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    if db.query(FeeAgreement).filter_by(student_id=student.id).first():
        raise HTTPException(409, "This student already has a fee agreement")
    enrollment = (
        db.query(Enrollment)
        .filter_by(student_id=student.id)
        .order_by(Enrollment.is_active.desc(), Enrollment.created_at.desc())
        .first()
    )
    if not enrollment:
        raise HTTPException(409, "Create an enrollment before the fee agreement")
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        legacy_import_id=None,
        agreed_amount=payload.agreed_amount,
        legacy_registration_total=0,
        currency=payload.currency.upper(),
        status=payload.status,
    )
    db.add(agreement)
    db.flush()
    after = {
        "studentId": student.id,
        "agreedAmount": agreement.agreed_amount,
    }
    audit(db, actor, "finance.agreement.create", "fee_agreement", agreement.id, after=after)
    db.commit()
    return {
        "id": agreement.id,
        "studentId": student.id,
        "studentName": student.full_name,
        "admissionNumber": student.admission_number,
        "agreedAmount": agreement.agreed_amount,
        "legacyRegistrationTotal": agreement.legacy_registration_total,
        "currency": agreement.currency,
        "status": agreement.status,
    }


@router.get("/staged-payments")
def staged_payments(reconciliation_status: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles(*FINANCE_ROLES))):
    query = db.query(PaymentTransaction, Student).join(Student, Student.id == PaymentTransaction.student_id).filter(PaymentTransaction.status == "staged")
    if reconciliation_status:
        query = query.filter(PaymentTransaction.reconciliation_status == reconciliation_status)
    total = query.count()
    rows = query.order_by(PaymentTransaction.transaction_date, Student.full_name).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [{"id": payment.id, "studentId": student.id, "studentName": student.full_name, "legacyImportId": payment.legacy_import_id, "line": payment.legacy_line_number, "date": payment.transaction_date, "amount": payment.amount, "method": payment.method, "type": payment.transaction_type, "sourceNote": payment.source_note, "status": payment.status, "reconciliationStatus": payment.reconciliation_status} for payment, student in rows], "total": total, "page": page, "pageSize": page_size}


@router.get("/transactions")
def transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*FINANCE_ROLES)),
):
    query = db.query(PaymentTransaction, Student).join(
        Student,
        Student.id == PaymentTransaction.student_id,
    )
    total = query.count()
    rows = (
        query.order_by(
            PaymentTransaction.transaction_date.desc().nullslast(),
            PaymentTransaction.created_at.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_payment_payload(row, student) for row, student in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


@router.post("/payments", status_code=201)
def post_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner", "accounts")),
):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    agreement = db.query(FeeAgreement).filter_by(student_id=student.id).first()
    if not agreement:
        raise HTTPException(409, "Create a fee agreement before recording a payment")
    if agreement.status not in {"active", "draft"}:
        raise HTTPException(409, "The fee agreement is not open for payments")
    if payload.transaction_date > _india_today():
        raise HTTPException(422, "Payment date cannot be in the future")
    row = _create_posted_payment(
        db,
        student=student,
        agreement=agreement,
        actor=actor,
        transaction_date=payload.transaction_date,
        amount=payload.amount,
        method=payload.method,
        reference=payload.reference,
        notes=payload.notes,
    )
    after = _payment_payload(row, student)
    audit(db, actor, "finance.payment.post", "payment_transaction", row.id, after=after)
    db.commit()
    return after


@router.post("/payments/{payment_id}/reverse", status_code=201)
def reverse_payment(
    payment_id: str,
    payload: PaymentReversalCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner", "accounts")),
):
    original = db.get(PaymentTransaction, payment_id)
    if not original or original.status != "posted" or original.transaction_type != "payment":
        raise HTTPException(404, "Posted payment not found")
    if payload.transaction_date < (original.transaction_date or payload.transaction_date):
        raise HTTPException(422, "Reversal date cannot be before the payment date")
    if payload.transaction_date > _india_today():
        raise HTTPException(422, "Reversal date cannot be in the future")
    prior = (
        db.query(func.coalesce(func.sum(PaymentTransaction.amount), 0))
        .filter(
            PaymentTransaction.related_transaction_id == original.id,
            PaymentTransaction.transaction_type.in_(("reversal", "refund", "void")),
            PaymentTransaction.status == "posted",
        )
        .scalar()
        or 0
    )
    remaining = original.amount - int(prior)
    if remaining <= 0:
        raise HTTPException(409, "This payment has already been fully reversed")
    amount = remaining if payload.amount is None else payload.amount
    if amount > remaining:
        raise HTTPException(409, f"Only ₹{remaining:,} remains available to reverse")
    if payload.kind in {"reversal", "void"} and amount != remaining:
        raise HTTPException(422, f"{payload.kind.title()} must offset the full remaining payment")
    student = db.get(Student, original.student_id)
    row = PaymentTransaction(
        student_id=original.student_id,
        fee_agreement_id=original.fee_agreement_id,
        receipt_number=_receipt_number("credit_note"),
        transaction_date=payload.transaction_date,
        amount=amount,
        method=original.method,
        transaction_type=payload.kind,
        source_note=f"{payload.kind.title()} of {original.receipt_number}",
        reference=(payload.reference or "").strip() or None,
        notes=payload.reason.strip(),
        related_transaction_id=original.id,
        created_by=actor.id,
        status="posted",
        reconciliation_status="ready",
    )
    db.add(row)
    db.flush()
    after = _payment_payload(row, student)
    audit(
        db,
        actor,
        f"finance.payment.{payload.kind}",
        "payment_transaction",
        row.id,
        after=after,
    )
    db.commit()
    return after


@router.get("/installments")
def installments(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*FINANCE_ROLES)),
):
    query = db.query(FeeInstallment, Student).join(
        Student,
        Student.id == FeeInstallment.student_id,
    )
    total = query.count()
    rows = query.order_by(
        FeeInstallment.due_date,
        Student.full_name,
    ).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_installment_payload(row, student) for row, student in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


@router.post("/installments", status_code=201)
def create_installment(
    payload: FeeInstallmentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*FINANCE_ROLES)),
):
    student = db.get(Student, payload.studentId)
    if not student:
        raise HTTPException(404, "Student not found")
    agreement = db.query(FeeAgreement).filter_by(student_id=student.id).first()
    if not agreement:
        raise HTTPException(409, "Create a fee agreement before scheduling a payment")
    if payload.dueDate < _india_today():
        raise HTTPException(422, "Future payment date cannot be in the past")
    row = FeeInstallment(
        student_id=student.id,
        fee_agreement_id=agreement.id,
        due_date=payload.dueDate,
        amount=payload.amount,
        expected_method=payload.expectedMethod,
        notes=payload.notes.strip(),
        status="scheduled",
        created_by=actor.id,
    )
    db.add(row)
    db.flush()
    audit(
        db,
        actor,
        "finance.installment.create",
        "fee_installment",
        row.id,
        after=_installment_payload(row, student),
    )
    db.commit()
    return _installment_payload(row, student)


@router.patch("/installments/{installment_id}")
def update_installment(
    installment_id: str,
    payload: FeeInstallmentUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*FINANCE_ROLES)),
):
    row = db.get(FeeInstallment, installment_id)
    if not row:
        raise HTTPException(404, "Future payment not found")
    student = db.get(Student, row.student_id)
    before = _installment_payload(row, student)
    row.due_date = payload.dueDate
    row.amount = payload.amount
    row.expected_method = payload.expectedMethod
    row.notes = payload.notes.strip()
    row.status = payload.status
    db.flush()
    audit(
        db,
        actor,
        "finance.installment.update",
        "fee_installment",
        row.id,
        before=before,
        after=_installment_payload(row, student),
    )
    db.commit()
    return _installment_payload(row, student)


@router.patch("/agreements/{agreement_id}")
def update_agreement(agreement_id: str, payload: FeeAgreementUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles(*FINANCE_ROLES))):
    row = db.get(FeeAgreement, agreement_id)
    if not row:
        raise HTTPException(404, "Fee agreement not found")
    before = {"agreedAmount": row.agreed_amount, "legacyRegistrationTotal": row.legacy_registration_total, "currency": row.currency, "status": row.status}
    row.agreed_amount = payload.agreed_amount
    row.legacy_registration_total = payload.legacy_registration_total
    row.currency = payload.currency.upper()
    row.status = payload.status
    audit(db, actor, "finance.agreement.update", "fee_agreement", row.id, before=before, after=payload.model_dump(by_alias=True))
    db.commit()
    student = db.get(Student, row.student_id)
    return {"id": row.id, "studentId": student.id, "studentName": student.full_name, "admissionNumber": student.admission_number, "agreedAmount": row.agreed_amount, "legacyRegistrationTotal": row.legacy_registration_total, "currency": row.currency, "status": row.status}


@router.patch("/staged-payments/{payment_id}/review")
def update_payment_review(payment_id: str, payload: PaymentReviewUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles(*FINANCE_ROLES))):
    row = db.get(PaymentTransaction, payment_id)
    if not row:
        raise HTTPException(404, "Staged payment not found")
    before = {"reconciliationStatus": row.reconciliation_status}
    row.reconciliation_status = payload.reconciliation_status
    audit(db, actor, "finance.payment.review", "payment_transaction", row.id, before=before, after=payload.model_dump(by_alias=True))
    db.commit()
    return {"id": row.id, "reconciliationStatus": row.reconciliation_status}
