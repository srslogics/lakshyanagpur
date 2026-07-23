from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog, Batch, ParentAccount, Room, Student, StudentAccount, Subject, User
from ..operations_schemas import BatchCreate, ParentAccessCreate, RoomCreate, StudentAccessCreate, SubjectCreate, UserCreate
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
    return {
        "users": [{"id": item.id, "fullName": item.full_name, "email": item.email, "role": item.role, "isActive": item.is_active} for item in users],
        "batches": [_batch(item) for item in db.query(Batch).order_by(Batch.program, Batch.name).all()],
        "subjects": [_subject(item) for item in db.query(Subject).order_by(Subject.program, Subject.name).all()],
        "rooms": [_room(item) for item in db.query(Room).order_by(Room.name).all()],
        "studentAccess": [{"studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "email": account_user.email, "isActive": account_user.is_active} for account, student, account_user in db.query(StudentAccount, Student, User).join(Student, Student.id == StudentAccount.student_id).join(User, User.id == StudentAccount.user_id).order_by(Student.full_name).all()],
        "parentAccess": [{
            "userId": account.user_id,
            "studentId": student.id,
            "admissionNumber": student.admission_number,
            "studentName": student.full_name,
            "fullName": account_user.full_name,
            "email": account_user.email,
            "contactType": account.contact_type,
            "isActive": account_user.is_active,
        } for account, student, account_user in db.query(ParentAccount, Student, User).join(
            Student, Student.id == ParentAccount.student_id
        ).join(User, User.id == ParentAccount.user_id).order_by(Student.full_name, User.full_name).all()],
    }


@router.post("/users", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "A user with this email already exists")
    row = User(email=email, full_name=payload.full_name.strip(), role=payload.role, password_hash=hash_password(payload.password))
    db.add(row); db.flush()
    audit(db, actor, "settings.user.create", "user", row.id, after={"email": row.email, "role": row.role})
    db.commit()
    return {"id": row.id, "fullName": row.full_name, "email": row.email, "role": row.role, "isActive": row.is_active}


@router.post("/student-access", status_code=201)
def create_student_access(payload: StudentAccessCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    if db.query(StudentAccount).filter_by(student_id=student.id).first():
        raise HTTPException(409, "This student already has portal access")
    if db.query(StudentAccount).count() >= 100:
        raise HTTPException(409, "The student portal is configured for a maximum of 100 accounts")
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "A user with this email already exists")
    account_user = User(email=email, full_name=student.full_name, role="student", password_hash=hash_password(payload.password))
    db.add(account_user); db.flush()
    db.add(StudentAccount(user_id=account_user.id, student_id=student.id))
    audit(db, actor, "settings.student_access.create", "student", student.id, after={"user_id": account_user.id, "email": email})
    db.commit()
    return {"studentId": student.id, "admissionNumber": student.admission_number, "fullName": student.full_name, "email": email, "isActive": True}


@router.post("/parent-access", status_code=201)
def create_parent_access(payload: ParentAccessCreate, db: Session = Depends(get_db), actor: User = Depends(require_roles("owner"))):
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "A user with this email already exists")
    account_user = User(
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


@router.get("/audit")
def list_audit(limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles("owner"))):
    rows = db.query(AuditLog, User).outerjoin(User, User.id == AuditLog.actor_id).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [{"id": log.id, "action": log.action, "entityType": log.entity_type, "entityId": log.entity_id, "actor": actor.full_name if actor else "System", "createdAt": log.created_at} for log, actor in rows]
