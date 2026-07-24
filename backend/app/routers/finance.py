from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FeeAgreement, PaymentTransaction, Student, User
from ..operations_schemas import FeeAgreementUpdate, PaymentReviewUpdate
from ..security import require_roles
from ..services import audit

router = APIRouter(prefix="/api/finance", tags=["finance"])
FINANCE_ROLES = ("owner", "accounts", "admissions_manager")


@router.get("/agreements")
def fee_agreements(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles(*FINANCE_ROLES))):
    query = db.query(FeeAgreement, Student).join(Student, Student.id == FeeAgreement.student_id)
    total = query.count()
    rows = query.order_by(Student.full_name).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [{"id": fee.id, "studentId": student.id, "studentName": student.full_name, "admissionNumber": student.admission_number, "agreedAmount": fee.agreed_amount, "legacyRegistrationTotal": fee.legacy_registration_total, "currency": fee.currency, "status": fee.status} for fee, student in rows], "total": total, "page": page, "pageSize": page_size}


@router.get("/staged-payments")
def staged_payments(reconciliation_status: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles(*FINANCE_ROLES))):
    query = db.query(PaymentTransaction, Student).join(Student, Student.id == PaymentTransaction.student_id).filter(PaymentTransaction.status == "staged")
    if reconciliation_status:
        query = query.filter(PaymentTransaction.reconciliation_status == reconciliation_status)
    total = query.count()
    rows = query.order_by(PaymentTransaction.transaction_date, Student.full_name).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [{"id": payment.id, "studentId": student.id, "studentName": student.full_name, "legacyImportId": payment.legacy_import_id, "line": payment.legacy_line_number, "date": payment.transaction_date, "amount": payment.amount, "method": payment.method, "type": payment.transaction_type, "sourceNote": payment.source_note, "status": payment.status, "reconciliationStatus": payment.reconciliation_status} for payment, student in rows], "total": total, "page": page, "pageSize": page_size}


@router.patch("/agreements/{agreement_id}")
def update_agreement(agreement_id: str, payload: FeeAgreementUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
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
def update_payment_review(payment_id: str, payload: PaymentReviewUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(PaymentTransaction, payment_id)
    if not row:
        raise HTTPException(404, "Staged payment not found")
    before = {"reconciliationStatus": row.reconciliation_status}
    row.reconciliation_status = payload.reconciliation_status
    audit(db, actor, "finance.payment.review", "payment_transaction", row.id, before=before, after=payload.model_dump(by_alias=True))
    db.commit()
    return {"id": row.id, "reconciliationStatus": row.reconciliation_status}
