from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Enrollment, FeeAgreement, LegacyAdmissionRow, Student, User
from ..security import require_roles

READ_ROLES = ("owner", "admissions_manager", "front_desk", "accounts", "academic_coordinator")
router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("")
def list_students(
    search: str | None = None,
    program: str | None = None,
    data_quality: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*READ_ROLES)),
):
    query = db.query(Student, Enrollment).outerjoin(Enrollment, Enrollment.student_id == Student.id)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Student.full_name.ilike(term), Student.mobile.ilike(term), Student.admission_number.ilike(term)))
    if program:
        query = query.filter(Enrollment.program == program)
    if data_quality:
        query = query.filter(Student.data_quality_status == data_quality.lower())
    total = query.count()
    rows = query.order_by(Enrollment.enrollment_date, Student.full_name).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [{
            "id": student.id,
            "admissionNumber": student.admission_number,
            "fullName": student.full_name,
            "mobile": student.mobile,
            "secondaryMobile": student.secondary_mobile,
            "previousSchool": student.previous_school,
            "program": enrollment.program if enrollment else None,
            "batch": enrollment.batch if enrollment else None,
            "enrollmentDate": enrollment.enrollment_date if enrollment else None,
            "status": student.status,
            "dataQualityStatus": student.data_quality_status,
            "legacyImportId": student.legacy_import_id,
        } for student, enrollment in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


@router.get("/{student_id}")
def student_detail(student_id: str, db: Session = Depends(get_db), user: User = Depends(require_roles(*READ_ROLES))):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    enrollment = (
        db.query(Enrollment)
        .filter_by(student_id=student.id)
        .order_by(Enrollment.is_active.desc(), Enrollment.created_at.desc())
        .first()
    )
    fee = db.query(FeeAgreement).filter_by(student_id=student.id).first()
    legacy = db.query(LegacyAdmissionRow).filter_by(student_id=student.id).first()
    return {
        "id": student.id,
        "admissionNumber": student.admission_number,
        "fullName": student.full_name,
        "mobile": student.mobile,
        "secondaryMobile": student.secondary_mobile,
        "previousSchool": student.previous_school,
        "status": student.status,
        "dataQualityStatus": student.data_quality_status,
        "enrollment": None if not enrollment else {"id": enrollment.id, "program": enrollment.program, "batch": enrollment.batch, "enrollmentDate": enrollment.enrollment_date, "status": enrollment.status},
        "feeAgreement": None if not fee else {"id": fee.id, "agreedAmount": fee.agreed_amount, "legacyRegistrationTotal": fee.legacy_registration_total, "currency": fee.currency, "status": fee.status},
        "migration": None if not legacy else {"legacyId": legacy.id, "sourceRow": legacy.source_row, "readiness": legacy.import_readiness, "issues": legacy.issues},
    }
