from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Enrollment,
    FeeAgreement,
    FeeInstallment,
    Lead,
    PaymentTransaction,
    Student,
    User,
)
from ..schemas import LEAD_SOURCES, LEAD_STAGES, LeadRead
from ..security import require_roles
from .finance import _installment_payload, _payment_payload
from .students import _list_item


router = APIRouter(prefix="/api/workspace", tags=["workspace"])
ERP_ROLES = (
    "owner",
    "admissions_manager",
    "counsellor",
    "front_desk",
    "accounts",
    "academic_coordinator",
    "faculty",
    "storekeeper",
)
STUDENT_ROLES = {
    "owner",
    "admissions_manager",
    "front_desk",
    "accounts",
    "academic_coordinator",
}
FINANCE_ROLES = {"owner", "accounts", "admissions_manager"}
ADMISSIONS_ROLES = {"owner", "admissions_manager", "counsellor", "front_desk"}


def _students(db: Session):
    latest_enrollment_id = (
        select(Enrollment.id)
        .where(Enrollment.student_id == Student.id)
        .order_by(
            Enrollment.is_active.desc(),
            Enrollment.created_at.desc(),
            Enrollment.id.desc(),
        )
        .limit(1)
        .correlate(Student)
        .scalar_subquery()
    )
    rows = (
        db.query(Student, Enrollment)
        .outerjoin(Enrollment, Enrollment.id == latest_enrollment_id)
        .filter(Student.is_test_account.is_(False))
        .order_by(Enrollment.enrollment_date, Student.full_name)
        .all()
    )
    return [_list_item(student, enrollment) for student, enrollment in rows]


def _finance(db: Session):
    agreements = [
        {
            "id": agreement.id,
            "studentId": student.id,
            "studentName": student.full_name,
            "studentMobile": student.mobile,
            "admissionNumber": student.admission_number,
            "agreedAmount": agreement.agreed_amount,
            "legacyRegistrationTotal": agreement.legacy_registration_total,
            "currency": agreement.currency,
            "status": agreement.status,
        }
        for agreement, student in (
            db.query(FeeAgreement, Student)
            .join(Student, Student.id == FeeAgreement.student_id)
            .filter(Student.is_test_account.is_(False))
            .order_by(Student.full_name)
            .all()
        )
    ]
    payments = [
        _payment_payload(payment, student)
        for payment, student in (
            db.query(PaymentTransaction, Student)
            .join(Student, Student.id == PaymentTransaction.student_id)
            .filter(Student.is_test_account.is_(False))
            .order_by(
                PaymentTransaction.transaction_date.desc().nullslast(),
                PaymentTransaction.created_at.desc(),
            )
            .all()
        )
    ]
    installments = [
        _installment_payload(installment, student)
        for installment, student in (
            db.query(FeeInstallment, Student)
            .join(Student, Student.id == FeeInstallment.student_id)
            .filter(Student.is_test_account.is_(False))
            .order_by(FeeInstallment.due_date, Student.full_name)
            .all()
        )
    ]
    return agreements, payments, installments


@router.get("/bootstrap")
def bootstrap(
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*ERP_ROLES)),
):
    students = _students(db) if actor.role in STUDENT_ROLES else []
    if actor.role in FINANCE_ROLES:
        agreements, payments, installments = _finance(db)
    else:
        agreements, payments, installments = [], [], []

    leads = []
    if actor.role in ADMISSIONS_ROLES:
        query = db.query(Lead)
        if actor.role == "counsellor":
            query = query.filter(Lead.owner_id == actor.id)
        leads = [
            LeadRead.model_validate(lead).model_dump(by_alias=True)
            for lead in query.order_by(
                Lead.next_follow_up_at.asc().nullslast(),
                Lead.created_at.desc(),
            ).all()
        ]

    return {
        "students": students,
        "agreements": agreements,
        "payments": payments,
        "installments": installments,
        "leads": leads,
        "admissionsMeta": {
            "stageOrder": list(LEAD_STAGES),
            "sources": list(LEAD_SOURCES),
        } if actor.role in ADMISSIONS_ROLES else {"stageOrder": [], "sources": []},
    }
