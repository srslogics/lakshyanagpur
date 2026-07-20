from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FeeAgreement, PaymentTransaction, Student, User
from ..security import require_roles

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
