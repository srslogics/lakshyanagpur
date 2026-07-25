from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..importers.academic_workbook import AcademicImportConflict, import_manifest as import_academic_manifest
from ..models import AcademicImportBatch, AuditLog, Batch, ParentAccount, Room, Student, StudentAccount, Subject, User
from ..operations_schemas import BatchCreate, BatchUpdate, ParentAccessCreate, RoomCreate, RoomUpdate, StudentAccessCreate, SubjectCreate, SubjectUpdate, UserCreate, UserUpdate
from ..security import hash_password, require_roles
from ..services import audit

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _batch(row: Batch):
    return {"id": row.id, "name": row.name, "program": row.program, "isActive": row.is_active}


def _subject(row: Subject):
    return {"id": row.id, "name": row.name, "code": row.code, "program": row.program, "isActive": row.is_active}


def _room(row: Room):
    return {"id": row.id, "name": row.name, "capacity": row.capacity, "isActive": row.is_active}


@router.get("/bootstrap")
def bootstrap(db: Session = Depends(get_db), user: User = Depends(require_roles("owner"))):
    users = db.query(User).order_by(User.full_name).all()
    academic_imports = (
        db.query(AcademicImportBatch)
        .order_by(AcademicImportBatch.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "users": [{"id": item.id, "fullName": item.full_name, "mobile": item.mobile, "email": item.email, "role": item.role, "isActive": item.is_active} for item in users],
        "batches": [_batch(item) for item in db.query(Batch).order_by(Batch.program, Batch.name).all()],
        "subjects": [_subject(item) for item in db.query(Subject).order_by(Subject.program, Subject.name).all()],
        "rooms": [_room(item) for item in db.query(Room).order_by(Room.name).all()],
        "academicImports": [{
            "id": item.id,
            "sourceName": item.source_name,
            "status": item.status,
            "activeStudents": item.active_student_rows,
            "attendanceEntries": item.attendance_entries,
            "subjectSelections": item.subject_selections,
            "sourceRecords": item.staged_source_rows,
            "unresolvedItems": item.unresolved_items,
            "createdAt": item.created_at,
        } for item in academic_imports],
        "studentAccess": [{"userId": account.user_id, "studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "mobile": account_user.mobile, "email": account_user.email, "isActive": account_user.is_active} for account, student, account_user in db.query(StudentAccount, Student, User).join(Student, Student.id == StudentAccount.student_id).join(User, User.id == StudentAccount.user_id).order_by(Student.full_name).all()],
        "parentAccess": [{
            "userId": account.user_id,
            "studentId": student.id,
            "admissionNumber": student.admission_number,
            "studentName": student.full_name,
            "fullName": account_user.full_name,
            "mobile": account_user.mobile,
            "email": account_user.email,
            "contactType": account.contact_type,
            "isActive": account_user.is_active,
        } for account, student, account_user in db.query(ParentAccount, Student, User).join(
            Student, Student.id == ParentAccount.student_id
        ).join(User, User.id == ParentAccount.user_id).order_by(Student.full_name, User.full_name).all()],
    }


@router.post("/imports/academic")
def import_academic_workbook(
    payload: dict,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner")),
):
    try:
        return import_academic_manifest(db, payload, actor_id=actor.id)
    except AcademicImportConflict as error:
        raise HTTPException(409, str(error)) from error


@router.post("/users", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    if db.query(User).filter(User.mobile == payload.mobile).first():
        raise HTTPException(409, "This mobile number is already assigned to another account")
    email = str(payload.email).lower() if payload.email else None
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "A user with this email already exists")
    row = User(mobile=payload.mobile, email=email, full_name=payload.full_name.strip(), role=payload.role, password_hash=hash_password(payload.password))
    db.add(row); db.flush()
    audit(db, actor, "settings.user.create", "user", row.id, after={"mobile": row.mobile, "email": row.email, "role": row.role})
    db.commit()
    return {"id": row.id, "fullName": row.full_name, "mobile": row.mobile, "email": row.email, "role": row.role, "isActive": row.is_active}


@router.patch("/users/{user_id}")
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(User, user_id)
    if not row:
        raise HTTPException(404, "User not found")
    if row.role == "owner" and (payload.role != "owner" or not payload.is_active):
        active_owners = db.query(User).filter(User.role == "owner", User.is_active.is_(True)).count()
        if active_owners <= 1:
            raise HTTPException(409, "The last active owner cannot be deactivated or reassigned")
    before = {"fullName": row.full_name, "mobile": row.mobile, "email": row.email, "role": row.role, "isActive": row.is_active}
    row.full_name = payload.full_name.strip()
    row.mobile = payload.mobile
    row.email = str(payload.email).lower() if payload.email else None
    row.role = payload.role
    row.is_active = payload.is_active
    if payload.password:
        row.password_hash = hash_password(payload.password)
    audit(db, actor, "settings.user.update", "user", row.id, before=before, after={"fullName": row.full_name, "mobile": row.mobile, "email": row.email, "role": row.role, "isActive": row.is_active, "passwordChanged": bool(payload.password)})
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "This mobile number or email is already assigned to another account") from error
    return {"id": row.id, "fullName": row.full_name, "mobile": row.mobile, "email": row.email, "role": row.role, "isActive": row.is_active}


@router.post("/student-access", status_code=201)
def create_student_access(payload: StudentAccessCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    if db.query(StudentAccount).filter_by(student_id=student.id).first():
        raise HTTPException(409, "This student already has portal access")
    if db.query(StudentAccount).count() >= 100:
        raise HTTPException(409, "The student portal is configured for a maximum of 100 accounts")
    if db.query(User).filter(User.mobile == payload.mobile).first():
        raise HTTPException(409, "This mobile number is already assigned to another account")
    email = str(payload.email).lower() if payload.email else None
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "A user with this email already exists")
    account_user = User(mobile=payload.mobile, email=email, full_name=student.full_name, role="student", password_hash=hash_password(payload.password))
    db.add(account_user); db.flush()
    db.add(StudentAccount(user_id=account_user.id, student_id=student.id))
    audit(db, actor, "settings.student_access.create", "student", student.id, after={"user_id": account_user.id, "mobile": payload.mobile, "email": email})
    db.commit()
    return {"studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "mobile": payload.mobile, "email": email, "isActive": True}


@router.post("/parent-access", status_code=201)
def create_parent_access(payload: ParentAccessCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    if db.query(User).filter(User.mobile == payload.mobile).first():
        raise HTTPException(409, "This mobile number is already assigned to another account")
    email = str(payload.email).lower() if payload.email else None
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "A user with this email already exists")
    account_user = User(
        mobile=payload.mobile,
        email=email,
        full_name=payload.full_name.strip(),
        role="parent",
        password_hash=hash_password(payload.password),
    )
    db.add(account_user)
    db.flush()
    db.add(ParentAccount(
        user_id=account_user.id,
        student_id=student.id,
        contact_type=payload.contact_type,
    ))
    audit(
        db,
        actor,
        "settings.parent_access.create",
        "student",
        student.id,
        after={
            "user_id": account_user.id,
            "mobile": payload.mobile,
            "email": email,
            "contact_type": payload.contact_type,
        },
    )
    db.commit()
    return {
        "userId": account_user.id,
        "studentId": student.id,
        "admissionNumber": student.admission_number,
        "studentName": student.full_name,
        "fullName": account_user.full_name,
        "mobile": payload.mobile,
        "email": email,
        "contactType": payload.contact_type,
        "isActive": True,
    }


def _commit_master(db: Session, actor: User, row, kind: str, after: dict):
    try:
        db.add(row); db.flush()
        audit(db, actor, f"settings.{kind}.create", kind, row.id, after=after)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, f"This {kind} already exists")
    return row


@router.post("/batches", status_code=201)
def create_batch(payload: BatchCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = Batch(name=payload.name.strip(), program=payload.program.strip())
    _commit_master(db, actor, row, "batch", {"name": row.name, "program": row.program})
    return _batch(row)


@router.post("/subjects", status_code=201)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = Subject(name=payload.name.strip(), code=payload.code.strip().upper(), program=payload.program.strip())
    _commit_master(db, actor, row, "subject", {"name": row.name, "code": row.code, "program": row.program})
    return _subject(row)


@router.post("/rooms", status_code=201)
def create_room(payload: RoomCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = Room(name=payload.name.strip(), capacity=payload.capacity)
    _commit_master(db, actor, row, "room", {"name": row.name, "capacity": row.capacity})
    return _room(row)


def _update_master(db: Session, actor: User, row, kind: str, before: dict, after: dict):
    audit(db, actor, f"settings.{kind}.update", kind, row.id, before=before, after=after)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, f"This {kind} conflicts with an existing record") from error


@router.patch("/batches/{batch_id}")
def update_batch(batch_id: str, payload: BatchUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(Batch, batch_id)
    if not row:
        raise HTTPException(404, "Batch not found")
    before = _batch(row)
    row.name, row.program, row.is_active = payload.name.strip(), payload.program.strip(), payload.is_active
    _update_master(db, actor, row, "batch", before, _batch(row))
    return _batch(row)


@router.patch("/subjects/{subject_id}")
def update_subject(subject_id: str, payload: SubjectUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(Subject, subject_id)
    if not row:
        raise HTTPException(404, "Subject not found")
    before = _subject(row)
    row.name, row.code, row.program, row.is_active = payload.name.strip(), payload.code.strip().upper(), payload.program.strip(), payload.is_active
    _update_master(db, actor, row, "subject", before, _subject(row))
    return _subject(row)


@router.patch("/rooms/{room_id}")
def update_room(room_id: str, payload: RoomUpdate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    row = db.get(Room, room_id)
    if not row:
        raise HTTPException(404, "Room not found")
    before = _room(row)
    row.name, row.capacity, row.is_active = payload.name.strip(), payload.capacity, payload.is_active
    _update_master(db, actor, row, "room", before, _room(row))
    return _room(row)


@router.get("/audit")
def list_audit(limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles("owner"))):
    rows = db.query(AuditLog, User).outerjoin(User, User.id == AuditLog.actor_id).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [{"id": log.id, "action": log.action, "entityType": log.entity_type, "entityId": log.entity_id, "actor": actor.full_name if actor else "System", "createdAt": log.created_at} for log, actor in rows]
