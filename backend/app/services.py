from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session

from .models import (
    AuditLog,
    Batch,
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
    Subject,
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
    """Return the signed ledger effect used to calculate the balance."""
    if transaction.status not in {"staged", "posted"}:
        return 0
    if transaction.status == "staged" and transaction.reconciliation_status != "ready":
        return 0
    if transaction.reconciliation_status == "do_not_import":
        return 0
    if transaction.transaction_type == "payment":
        return transaction.amount
    if transaction.transaction_type == "balance_credit":
        return transaction.amount
    if transaction.transaction_type == "balance_debit":
        return -transaction.amount
    if transaction.transaction_type in {"adjustment", "reversal", "refund", "void"}:
        return -transaction.amount
    return 0


def received_effect(transaction: PaymentTransaction) -> int:
    """Return actual money received, excluding client balance reconciliations."""
    if transaction.transaction_type in {"balance_credit", "balance_debit"}:
        return 0
    return payment_effect(transaction)


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


def canonical_subject(value: str) -> str:
    """Return the single subject label used across imports and every portal."""
    normalized = "".join(character for character in (value or "").casefold() if character.isalnum())
    aliases = {
        "math": "Maths",
        "maths": "Maths",
        "mathematics": "Maths",
        "phy": "Physics",
        "physics": "Physics",
        "chem": "Chemistry",
        "chemistry": "Chemistry",
        "bio": "Biology",
        "biology": "Biology",
    }
    return aliases.get(normalized, (value or "").strip())


class SubjectRosterResolver:
    """Resolve student eligibility consistently for a batch and subject.

    Active students are matched by batch, by the batch's program (unless the
    timetable batch intentionally spans all programs), and by their recorded
    subject selections. Legacy students without subject rows retain the former
    batch-wide behaviour instead of disappearing from every roster.
    """

    def __init__(self, db: Session):
        enrollment_rows = (
            db.query(Student, Enrollment.batch, Enrollment.program)
            .join(Enrollment, Enrollment.student_id == Student.id)
            .filter(
                Student.status == "active",
                Student.is_test_account.is_(False),
                Enrollment.is_active.is_(True),
            )
            .order_by(Enrollment.created_at.desc(), Enrollment.id.desc())
            .all()
        )
        self._students = []
        seen_students = set()
        for student, batch_name, program in enrollment_rows:
            if student.id in seen_students:
                continue
            seen_students.add(student.id)
            self._students.append((student, batch_name, program))

        self._subjects: dict[str, set[str]] = {}
        for student_id, subject_name in db.query(
            StudentSubjectSelection.student_id,
            StudentSubjectSelection.subject_name,
        ).filter(StudentSubjectSelection.student_id.in_(seen_students)).all():
            self._subjects.setdefault(student_id, set()).add(
                canonical_subject(subject_name)
            )

    def students_for(self, batch: Batch, subject: Subject | str):
        subject_name = canonical_subject(
            subject.name if isinstance(subject, Subject) else subject
        )
        students = []
        for student, batch_name, program in self._students:
            if batch_name != batch.name:
                continue
            if batch.program != "All programs" and program != batch.program:
                continue
            selections = self._subjects.get(student.id, set())
            if selections and subject_name not in selections:
                continue
            students.append(student)
        return sorted(students, key=lambda student: student.full_name.casefold())

    def student_ids_for(self, batch: Batch, subject: Subject | str) -> set[str]:
        return {student.id for student in self.students_for(batch, subject)}

    def count_for(self, batch: Batch, subject: Subject | str) -> int:
        return len(self.students_for(batch, subject))


def selected_subjects(db: Session, student_id: str) -> list[str]:
    return sorted({
        canonical_subject(subject_name)
        for subject_name, in db.query(StudentSubjectSelection.subject_name)
        .filter(StudentSubjectSelection.student_id == student_id)
        .all()
    })


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
    for subject in sorted({canonical_subject(value) for value in payload.subjects if value.strip()}):
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
