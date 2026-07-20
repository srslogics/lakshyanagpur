from datetime import datetime, timezone
from sqlalchemy.orm import Session

from .models import AuditLog, Enrollment, FinanceHandoff, Guardian, Lead, LeadActivity, Student, StudentGuardian, User, new_id
from .schemas import ConversionRequest


def audit(db: Session, actor: User, action: str, entity_type: str, entity_id: str, before=None, after=None):
    db.add(AuditLog(actor_id=actor.id, action=action, entity_type=entity_type, entity_id=entity_id, before=before, after=after))


def admission_number(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(Student).filter(Student.admission_number.like(f"LI-{year}-%")).count()
    return f"LI-{year}-{count + 1:05d}"


def convert_lead(db: Session, lead: Lead, payload: ConversionRequest, actor: User):
    if lead.converted_student_id:
        student = db.get(Student, lead.converted_student_id)
        enrollment = db.query(Enrollment).filter_by(student_id=student.id).first()
        guardian_link = db.query(StudentGuardian).filter_by(student_id=student.id).first()
        finance = db.query(FinanceHandoff).filter_by(student_id=student.id).first()
        return student, db.get(Guardian, guardian_link.guardian_id), enrollment, finance

    student = Student(admission_number=admission_number(db), full_name=lead.student, mobile=lead.mobile, email=lead.email, status="draft")
    guardian = Guardian(full_name=lead.parent, mobile=lead.parent_mobile or lead.mobile)
    db.add_all([student, guardian]); db.flush()
    db.add(StudentGuardian(student_id=student.id, guardian_id=guardian.id, relationship=payload.guardian_relationship))
    enrollment = Enrollment(student_id=student.id, program=lead.program, batch=payload.batch, status="draft")
    db.add(enrollment); db.flush()
    finance = FinanceHandoff(student_id=student.id, enrollment_id=enrollment.id, concession_requested=payload.concession_requested)
    db.add(finance)
    lead.stage = "Converted"; lead.converted_at = datetime.now(timezone.utc); lead.converted_student_id = student.id
    db.add(LeadActivity(lead_id=lead.id, kind="conversion", note="Admission converted; onboarding and finance handoff created.", actor_id=actor.id))
    audit(db, actor, "admissions.convert", "lead", lead.id, after={"student_id": student.id, "enrollment_id": enrollment.id, "finance_handoff_id": finance.id})
    db.commit()
    return student, guardian, enrollment, finance
