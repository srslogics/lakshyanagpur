from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Enrollment,
    FeeAgreement,
    LegacyAdmissionRow,
    Student,
    StudentAcademicProfile,
    StudentSubjectSelection,
    User,
)
from ..security import require_roles
from ..operations_schemas import StudentCreate, StudentUpdate
from ..services import admission_number, audit, canonical_program

READ_ROLES = ("owner", "admissions_manager", "front_desk", "accounts", "academic_coordinator")
router = APIRouter(prefix="/api/students", tags=["students"])


def _list_item(student: Student, enrollment: Enrollment | None):
    return {
        "id": student.id,
        "admissionNumber": student.admission_number,
        "fullName": student.full_name,
        "mobile": student.mobile,
        "secondaryMobile": student.secondary_mobile,
        "email": student.email,
        "previousSchool": student.previous_school,
        "program": enrollment.program if enrollment else None,
        "batch": enrollment.batch if enrollment else None,
        "enrollmentDate": enrollment.enrollment_date if enrollment else None,
        "status": student.status,
        "dataQualityStatus": student.data_quality_status,
        "legacyImportId": student.legacy_import_id,
    }


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
    latest_enrollment_id = (
        select(Enrollment.id)
        .where(Enrollment.student_id == Student.id)
        .order_by(Enrollment.is_active.desc(), Enrollment.created_at.desc(), Enrollment.id.desc())
        .limit(1)
        .correlate(Student)
        .scalar_subquery()
    )
    query = db.query(Student, Enrollment).outerjoin(
        Enrollment,
        Enrollment.id == latest_enrollment_id,
    ).filter(Student.is_test_account.is_(False))
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
        "items": [_list_item(student, enrollment) for student, enrollment in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


@router.get("/picker")
def student_picker(
    search: str = Query("", max_length=120),
    scope: Literal["all", "with_agreement", "without_agreement"] = "all",
    limit: int = Query(20, ge=1, le=30),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*READ_ROLES)),
):
    """Return a small, server-filtered result set for student comboboxes.

    This endpoint intentionally returns only identity fields and never sends the
    complete student directory to a form. Finance scopes also prevent a stale
    browser list from offering an ineligible student.
    """
    query = db.query(Student).filter(
        Student.is_test_account.is_(False),
        Student.status.in_(("active", "draft")),
    )
    agreement_exists = db.query(FeeAgreement.id).filter(
        FeeAgreement.student_id == Student.id,
    ).exists()
    if scope == "with_agreement":
        query = query.filter(agreement_exists)
    elif scope == "without_agreement":
        query = query.filter(~agreement_exists)

    needle = search.strip()
    if needle:
        term = f"%{needle}%"
        query = query.filter(or_(
            Student.full_name.ilike(term),
            Student.admission_number.ilike(term),
            Student.mobile.ilike(term),
            Student.secondary_mobile.ilike(term),
        ))

    rows = query.order_by(Student.full_name, Student.admission_number).limit(limit).all()
    return {
        "items": [
            {
                "id": student.id,
                "fullName": student.full_name,
                "admissionNumber": student.admission_number,
                "mobile": student.mobile,
            }
            for student in rows
        ],
        "query": needle,
        "limit": limit,
    }


@router.post("", status_code=201)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner")),
):
    contacts = [value for value in (payload.mobile, payload.secondaryMobile) if value]
    if contacts:
        duplicate = db.query(Student).filter(
            or_(
                Student.mobile.in_(contacts),
                Student.secondary_mobile.in_(contacts),
            )
        ).first()
        if duplicate:
            raise HTTPException(
                409,
                f"Mobile number is already assigned to {duplicate.full_name}",
            )

    student = Student(
        admission_number=admission_number(db),
        full_name=payload.fullName.strip(),
        mobile=payload.mobile,
        secondary_mobile=payload.secondaryMobile,
        email=str(payload.email).lower() if payload.email else None,
        previous_school=(payload.previousSchool or "").strip() or None,
        status=payload.status,
        data_quality_status="ready",
    )
    db.add(student)
    db.flush()
    program = canonical_program(payload.program)
    enrollment = Enrollment(
        student_id=student.id,
        program=program,
        batch=payload.batch,
        enrollment_date=payload.enrollmentDate,
        source_type="owner_entry",
        status=payload.status,
        is_active=payload.status == "active",
    )
    db.add(enrollment)
    db.flush()
    academic = StudentAcademicProfile(
        student_id=student.id,
        source_student_code=f"ERP-{student.admission_number}",
        batch_name=payload.batch,
        source_stream=program,
        mentor_name=None,
        source_school_name=student.previous_school,
        source_primary_mobile=student.mobile,
        source_secondary_mobile=student.secondary_mobile,
        import_batch_id=None,
    )
    db.add(academic)
    selected_subjects = sorted(
        {value.strip() for value in payload.subjects if value.strip()}
    )
    for subject in selected_subjects:
        db.add(
            StudentSubjectSelection(
                student_id=student.id,
                subject_name=subject,
                source_value="owner_entry",
                import_batch_id=None,
            )
        )
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        legacy_import_id=None,
        agreed_amount=payload.agreedAmount,
        legacy_registration_total=0,
        currency="INR",
        status="active" if payload.status == "active" else "draft",
    )
    db.add(agreement)
    db.flush()
    result = _list_item(student, enrollment)
    audit(
        db,
        actor,
        "students.create",
        "student",
        student.id,
        after={
            **result,
            "subjects": selected_subjects,
            "feeAgreementId": agreement.id,
            "agreedAmount": agreement.agreed_amount,
        },
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            409,
            "Admission number or enrollment conflicts with an existing record",
        ) from error
    return result


@router.get("/{student_id}")
def student_detail(student_id: str, db: Session = Depends(get_db), user: User = Depends(require_roles(*READ_ROLES))):
    student = db.get(Student, student_id)
    if not student or student.is_test_account:
        raise HTTPException(404, "Student not found")
    enrollment = (
        db.query(Enrollment)
        .filter_by(student_id=student.id)
        .order_by(Enrollment.is_active.desc(), Enrollment.created_at.desc())
        .first()
    )
    fee = db.query(FeeAgreement).filter_by(student_id=student.id).first()
    legacy = db.query(LegacyAdmissionRow).filter_by(student_id=student.id).first()
    academic = db.get(StudentAcademicProfile, student.id)
    subjects = (
        db.query(StudentSubjectSelection)
        .filter_by(student_id=student.id)
        .order_by(StudentSubjectSelection.subject_name)
        .all()
    )
    return {
        "id": student.id,
        "admissionNumber": student.admission_number,
        "fullName": student.full_name,
        "mobile": student.mobile,
        "secondaryMobile": student.secondary_mobile,
        "email": student.email,
        "previousSchool": student.previous_school,
        "status": student.status,
        "dataQualityStatus": student.data_quality_status,
        "enrollment": None if not enrollment else {"id": enrollment.id, "program": enrollment.program, "batch": enrollment.batch, "enrollmentDate": enrollment.enrollment_date, "status": enrollment.status},
        "feeAgreement": None if not fee else {"id": fee.id, "agreedAmount": fee.agreed_amount, "legacyRegistrationTotal": fee.legacy_registration_total, "currency": fee.currency, "status": fee.status},
        "academicProfile": None if not academic else {
            "sourceStudentCode": academic.source_student_code,
            "batch": academic.batch_name,
            "sourceStream": academic.source_stream,
            "mentorName": academic.mentor_name,
            "sourceSchoolName": academic.source_school_name,
            "sourcePrimaryMobile": academic.source_primary_mobile,
            "sourceSecondaryMobile": academic.source_secondary_mobile,
            "subjects": [subject.subject_name for subject in subjects],
        },
        "migration": None if not legacy else {"legacyId": legacy.id, "sourceRow": legacy.source_row, "readiness": legacy.import_readiness, "issues": legacy.issues},
    }


@router.patch("/{student_id}")
def update_student(
    student_id: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner")),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    enrollment = (
        db.query(Enrollment)
        .filter_by(student_id=student.id)
        .order_by(Enrollment.is_active.desc(), Enrollment.created_at.desc())
        .first()
    )
    before = {
        "admissionNumber": student.admission_number,
        "fullName": student.full_name,
        "mobile": student.mobile,
        "secondaryMobile": student.secondary_mobile,
        "email": student.email,
        "previousSchool": student.previous_school,
        "status": student.status,
        "dataQualityStatus": student.data_quality_status,
        "program": enrollment.program if enrollment else None,
        "batch": enrollment.batch if enrollment else None,
        "enrollmentDate": enrollment.enrollment_date.isoformat() if enrollment and enrollment.enrollment_date else None,
    }
    student.admission_number = payload.admission_number.strip()
    student.full_name = payload.full_name.strip()
    student.mobile = (payload.mobile or "").strip() or None
    student.secondary_mobile = (payload.secondary_mobile or "").strip() or None
    student.email = str(payload.email).lower() if payload.email else None
    student.previous_school = (payload.previous_school or "").strip() or None
    student.status = payload.status
    student.data_quality_status = payload.data_quality_status
    if payload.program:
        if not enrollment:
            enrollment = Enrollment(student_id=student.id, program=canonical_program(payload.program), source_type="owner_edit")
            db.add(enrollment)
        enrollment.program = canonical_program(payload.program)
        enrollment.batch = (payload.batch or "").strip() or None
        enrollment.enrollment_date = payload.enrollment_date
        enrollment.status = "active" if payload.status == "active" else payload.status
        enrollment.is_active = payload.status == "active"
    elif enrollment:
        enrollment.batch = (payload.batch or "").strip() or None
        enrollment.enrollment_date = payload.enrollment_date
        enrollment.status = "active" if payload.status == "active" else payload.status
        enrollment.is_active = payload.status == "active"
    academic = db.get(StudentAcademicProfile, student.id)
    if academic and enrollment:
        academic.batch_name = enrollment.batch or academic.batch_name
        academic.source_stream = enrollment.program or academic.source_stream
        academic.source_school_name = student.previous_school
        academic.source_primary_mobile = student.mobile
        academic.source_secondary_mobile = student.secondary_mobile
    elif enrollment and enrollment.batch and enrollment.program:
        db.add(
            StudentAcademicProfile(
                student_id=student.id,
                source_student_code=f"ERP-{student.admission_number}",
                batch_name=enrollment.batch,
                source_stream=enrollment.program,
                source_school_name=student.previous_school,
                source_primary_mobile=student.mobile,
                source_secondary_mobile=student.secondary_mobile,
                import_batch_id=None,
            )
        )
    if payload.subjects is not None:
        selected_subjects = sorted(
            {value.strip() for value in payload.subjects if value.strip()}
        )
        if not selected_subjects:
            raise HTTPException(422, "Select at least one subject")
        db.query(StudentSubjectSelection).filter_by(student_id=student.id).delete(
            synchronize_session=False
        )
        for subject in selected_subjects:
            db.add(
                StudentSubjectSelection(
                    student_id=student.id,
                    subject_name=subject,
                    source_value="owner_edit",
                    import_batch_id=None,
                )
            )
    after = payload.model_dump(by_alias=True, mode="json")
    audit(db, actor, "students.update", "student", student.id, before=before, after=after)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "Admission number or enrollment conflicts with an existing record") from error
    db.refresh(student)
    return _list_item(student, enrollment)
