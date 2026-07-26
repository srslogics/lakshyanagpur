"""Provision isolated portal test accounts.

Passwords are accepted only through environment variables so credentials are
never committed to source control. The command is idempotent and may be rerun
to reset the four test-account passwords.
"""

from __future__ import annotations

import os

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ParentAccount, Student, StudentAccount, User
from app.security import hash_password


ACCOUNT_SPECS = {
    "student": {
        "mobile": "9000000101",
        "full_name": "Lakshya Student Test",
        "role": "student",
        "password_env": "TEST_STUDENT_PASSWORD",
    },
    "parent": {
        "mobile": "9000000102",
        "full_name": "Lakshya Parent Test",
        "role": "parent",
        "password_env": "TEST_PARENT_PASSWORD",
    },
    "faculty": {
        "mobile": "9000000103",
        "full_name": "Lakshya Faculty Test",
        "role": "faculty",
        "password_env": "TEST_FACULTY_PASSWORD",
    },
    "attendance": {
        "mobile": "9000000104",
        "full_name": "Lakshya Attendance Test",
        "role": "attendance_operator",
        "password_env": "TEST_ATTENDANCE_PASSWORD",
    },
}

DEMO_ADMISSION_NUMBER = "LI-TEST-00001"
DEMO_LEGACY_ID = "system-portal-test-student"


def _passwords_from_environment() -> dict[str, str]:
    passwords: dict[str, str] = {}
    for key, spec in ACCOUNT_SPECS.items():
        password = os.getenv(spec["password_env"], "")
        if len(password) < 10:
            raise RuntimeError(f"{spec['password_env']} must contain at least 10 characters")
        passwords[key] = password
    return passwords


def _upsert_user(db: Session, key: str, password: str) -> User:
    spec = ACCOUNT_SPECS[key]
    user = db.query(User).filter(User.mobile == spec["mobile"]).first()
    if user and user.role != spec["role"]:
        raise RuntimeError(
            f"Mobile {spec['mobile']} already belongs to a {user.role} account"
        )
    if not user:
        user = User(
            mobile=spec["mobile"],
            full_name=spec["full_name"],
            role=spec["role"],
            password_hash=hash_password(password),
            is_active=True,
        )
        db.add(user)
        db.flush()
    else:
        user.full_name = spec["full_name"]
        user.password_hash = hash_password(password)
        user.is_active = True
    return user


def provision_test_accounts(db: Session, passwords: dict[str, str]) -> dict:
    student = (
        db.query(Student)
        .filter(Student.legacy_import_id == DEMO_LEGACY_ID)
        .first()
    )
    if not student:
        student = Student(
            admission_number=DEMO_ADMISSION_NUMBER,
            full_name="Lakshya Portal Test Student",
            mobile=ACCOUNT_SPECS["student"]["mobile"],
            legacy_import_id=DEMO_LEGACY_ID,
            data_quality_status="ready",
            status="inactive",
        )
        db.add(student)
        db.flush()
    else:
        student.full_name = "Lakshya Portal Test Student"
        student.mobile = ACCOUNT_SPECS["student"]["mobile"]
        student.status = "inactive"

    users = {
        key: _upsert_user(db, key, passwords[key])
        for key in ACCOUNT_SPECS
    }

    student_link = db.get(StudentAccount, users["student"].id)
    conflicting_student_link = (
        db.query(StudentAccount)
        .filter(
            StudentAccount.student_id == student.id,
            StudentAccount.user_id != users["student"].id,
        )
        .first()
    )
    if conflicting_student_link:
        raise RuntimeError("The isolated test student is linked to another account")
    if student_link:
        student_link.student_id = student.id
    else:
        db.add(StudentAccount(user_id=users["student"].id, student_id=student.id))

    parent_link = db.get(ParentAccount, users["parent"].id)
    if parent_link:
        parent_link.student_id = student.id
        parent_link.contact_type = "primary_contact"
    else:
        db.add(
            ParentAccount(
                user_id=users["parent"].id,
                student_id=student.id,
                contact_type="primary_contact",
            )
        )

    db.commit()
    return {
        "studentId": student.id,
        "admissionNumber": student.admission_number,
        "accounts": {
            key: {
                "mobile": spec["mobile"],
                "role": spec["role"],
                "userId": users[key].id,
            }
            for key, spec in ACCOUNT_SPECS.items()
        },
    }


def main() -> None:
    passwords = _passwords_from_environment()
    with SessionLocal() as db:
        result = provision_test_accounts(db, passwords)
    print(f"Provisioned {len(result['accounts'])} isolated test accounts.")
    for key, account in result["accounts"].items():
        print(f"{key}: {account['mobile']} ({account['role']})")


if __name__ == "__main__":
    main()
