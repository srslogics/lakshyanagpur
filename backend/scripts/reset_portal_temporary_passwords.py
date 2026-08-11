"""Apply one shared temporary password with mandatory first-login replacement."""

from __future__ import annotations

import argparse
import os

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.identity import normalize_mobile
from app.models import Student, StudentAccount, User
from app.security import hash_password, verify_password
from app.services import audit


PORTAL_ROLES = (
    "student",
    "parent",
    "parent_student",
    "faculty",
    "attendance_operator",
)
DEFAULT_SHARED_TEMPORARY_PASSWORD = "Lakshaya@2026"


def reset_portal_passwords(
    db: Session,
    actor: User,
    temporary_password: str,
    *,
    apply: bool,
) -> dict:
    if actor.role != "owner" or not actor.is_active:
        raise RuntimeError("An active owner account is required")
    if len(temporary_password) < 6:
        raise RuntimeError("The shared temporary password must contain at least 6 characters")

    student_users = (
        db.query(User)
        .join(StudentAccount, StudentAccount.user_id == User.id)
        .join(Student, Student.id == StudentAccount.student_id)
        .filter(
            User.role == "student",
            User.is_active.is_(True),
            User.is_test_account.is_(False),
            Student.status == "active",
        )
        .order_by(User.full_name)
        .all()
    )
    other_portal_users = (
        db.query(User)
        .filter(
            User.role.in_(PORTAL_ROLES[1:]),
            User.is_active.is_(True),
            User.is_test_account.is_(False),
        )
        .order_by(User.full_name)
        .all()
    )
    targets = [*student_users, *other_portal_users]
    pending = [
        user for user in targets
        if not user.must_change_password
        or not verify_password(temporary_password, user.password_hash)
    ]

    if apply:
        for user in pending:
            user.password_hash = hash_password(temporary_password)
            user.must_change_password = True
            user.token_version += 1
            audit(
                db,
                actor,
                "auth.temporary_password.reset",
                "user",
                user.id,
                after={
                    "role": user.role,
                    "mustChangePassword": True,
                },
            )

    return {
        "studentAccounts": len(student_users),
        "facultyAccounts": sum(user.role == "faculty" for user in targets),
        "parentAccounts": sum(user.role in {"parent", "parent_student"} for user in targets),
        "attendanceAccounts": sum(user.role == "attendance_operator" for user in targets),
        "targetAccounts": len(targets),
        "pendingAccounts": len(pending),
        "resetAccounts": len(pending) if apply else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--actor-mobile")
    args = parser.parse_args()
    temporary_password = os.getenv(
        "PORTAL_SHARED_TEMP_PASSWORD",
        DEFAULT_SHARED_TEMPORARY_PASSWORD,
    )
    if len(temporary_password) < 6:
        raise SystemExit("PORTAL_SHARED_TEMP_PASSWORD must contain at least 6 characters")
    if args.apply and not args.actor_mobile:
        parser.error("--apply requires --actor-mobile")

    with SessionLocal() as db:
        if args.actor_mobile:
            try:
                actor_mobile = normalize_mobile(args.actor_mobile)
            except ValueError as error:
                raise SystemExit(str(error)) from error
            actor = db.query(User).filter_by(mobile=actor_mobile).first()
        else:
            actor = (
                db.query(User)
                .filter(User.role == "owner", User.is_active.is_(True))
                .order_by(User.created_at)
                .first()
            )
        if not actor:
            raise SystemExit("No matching active owner account was found")

        result = reset_portal_passwords(
            db,
            actor,
            temporary_password,
            apply=args.apply,
        )
        if args.apply:
            db.commit()
        else:
            db.rollback()
        print(f"Active student accounts: {result['studentAccounts']}")
        print(f"Faculty accounts: {result['facultyAccounts']}")
        print(f"Parent accounts: {result['parentAccounts']}")
        print(f"Attendance accounts: {result['attendanceAccounts']}")
        print(f"Accounts requiring reset: {result['pendingAccounts']}")
        print(f"Accounts reset: {result['resetAccounts']}")
        print("Shared temporary password was not printed.")


if __name__ == "__main__":
    main()
