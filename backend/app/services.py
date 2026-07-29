from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session

from .models import (
    AuditLog,
    Enrollment,
    FeeAgreement,
    FinanceHandoff,
    Guardian,
    Lead,
    LeadActivity,
    PaymentTransaction,
    Student,
    StudentAcademicProfile,
    StudentGuardian,
    StudentSubjectSelection,
    User,
    new_id,
)
from .schemas import ConversionRequest


def audit(db: Session, actor: User, action: str, entity_type: str, entity_id: str, before=None, after=None):
    db.add(
        AuditLog(
            actor_id=actor.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=jsonable_encoder(before) if before is not None else None,
            after=jsonable_encoder(after) if after is not None else None,
        )
    )


def payment_effect(transaction: PaymentTransaction) -> int:
    """Return the canonical signed value used by every financial summary."""
    if transaction.status not in {"staged", "posted"}:
        return 0
    if transaction.reconciliation_status == "do_not_import":
        return 0
    if transaction.transaction_type == "payment":
        return transaction.amount
    if transaction.transaction_type in {"adjustment", "reversal", "refund", "void"}:
        return -transaction.amount
    return 0


def admission_number(db: Session) -> str:
    if db.get_bind().dialect.name == "postgresql":
        # Serialize number allocation across Render workers within this transaction.
        db.execute(text("SELECT pg_advisory_xact_lock(202600001)"))
    year = datetime.now(ZoneInfo("Asia/Kolkata")).year
    prefix = f"LI-{year}-"
    existing = db.query(Student.admission_number).filter(
        Student.admission_number.like(f"{prefix}%")
    ).all()
    highest = max(
        (
            int(value.removeprefix(prefix))
            for value, in existing
            if value.removeprefix(prefix).isdigit()
        ),
        default=0,
    )
    return f"{prefix}{highest + 1:05d}"


def canonical_program(value: str) -> str:
    normalized = " ".join((value or "").strip().lower().replace("_", " ").split())
    if normalized in {
        "boards",
        "board",
        "boards 11th & 12th tuition",
        "11th and 12th boards course tuition",
    }:
        return "Boards"
    if normalized.startswith("jee"):
        return "JEE"
    if normalized.startswith("neet"):
        return "NEET"
    if normalized.startswith("mht-cet") or normalized.startswith("mht cet"):
        return "MHT-CET"
    return (value or "").strip()


def convert_lead(db: Session, lead: Lead, payload: ConversionRequest, actor: User):
    if lead.converted_student_id:
        student = db.get(Student, lead.converted_student_id)
        enrollment = db.query(Enrollment).filter_by(student_id=student.id).first()
        guardian_link = db.query(StudentGuardian).filter_by(student_id=student.id).first()
        finance = db.query(FinanceHandoff).filter_by(student_id=student.id).first()
        return student, db.get(Guardian, guardian_link.guardian_id), enrollment, finance

    student = Student(
        admission_number=admission_number(db),
        full_name=lead.student,
        mobile=lead.mobile,
        email=lead.email,
        status="active",
        data_quality_status="ready",
    )
    guardian = Guardian(full_name=lead.parent, mobile=lead.parent_mobile or lead.mobile)
    db.add_all([student, guardian]); db.flush()
    db.add(StudentGuardian(student_id=student.id, guardian_id=guardian.id, relationship=payload.guardian_relationship))
    program = canonical_program(lead.program)
    enrollment = Enrollment(
        student_id=student.id,
        program=program,
        batch=payload.batch,
        enrollment_date=payload.enrollment_date,
        source_type="lead_conversion",
        status="active",
        is_active=True,
    )
    db.add(enrollment); db.flush()
    db.add(
        StudentAcademicProfile(
            student_id=student.id,
            source_student_code=f"ERP-{student.admission_number}",
            batch_name=payload.batch,
            source_stream=program,
            source_primary_mobile=student.mobile,
            import_batch_id=None,
        )
    )
    for subject in sorted({value.strip() for value in payload.subjects if value.strip()}):
        db.add(
            StudentSubjectSelection(
                student_id=student.id,
                subject_name=subject,
                source_value="lead_conversion",
                import_batch_id=None,
            )
        )
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        legacy_import_id=None,
        agreed_amount=payload.agreed_amount,
        legacy_registration_total=0,
        currency="INR",
        status="active",
    )
    finance = FinanceHandoff(
        student_id=student.id,
        enrollment_id=enrollment.id,
        status="fee_plan_created",
        concession_requested=payload.concession_requested,
    )
    db.add_all([agreement, finance])
    lead.stage = "Converted"; lead.converted_at = datetime.now(timezone.utc); lead.converted_student_id = student.id
    db.add(LeadActivity(lead_id=lead.id, kind="conversion", note="Admission converted; onboarding and finance handoff created.", actor_id=actor.id))
    audit(db, actor, "admissions.convert", "lead", lead.id, after={"student_id": student.id, "enrollment_id": enrollment.id, "finance_handoff_id": finance.id, "fee_agreement_id": agreement.id})
    db.commit()
    return student, guardian, enrollment, finance
