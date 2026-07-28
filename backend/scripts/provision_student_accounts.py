"""Provision student portal accounts from verified student mobile numbers.

The command is dry-run by default. Use ``--apply`` with an active owner mobile
to create accounts and write the generated one-time credentials to a
permission-restricted CSV file.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import secrets
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.identity import normalize_mobile
from app.models import Student, StudentAccount, User
from app.security import hash_password, verify_password
from app.services import audit


PORTAL_ACCOUNT_LIMIT = 100


@dataclass(frozen=True)
class ProvisionedCredential:
    admission_number: str
    full_name: str
    mobile: str
    temporary_password: str


def generate_temporary_password() -> str:
    """Generate an unambiguous password containing every required character class."""
    upper = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    lower = "abcdefghijkmnopqrstuvwxyz"
    digits = "23456789"
    symbols = "@#%"
    random = secrets.SystemRandom()
    characters = [
        random.choice(upper),
        random.choice(lower),
        random.choice(digits),
        random.choice(symbols),
    ]
    alphabet = upper + lower + digits + symbols
    characters.extend(random.choice(alphabet) for _ in range(10))
    random.shuffle(characters)
    return "".join(characters)


def _canonical_mobile(student: Student) -> str | None:
    if not student.mobile or not student.mobile.strip():
        return None
    try:
        return normalize_mobile(student.mobile)
    except ValueError:
        return None


def provision_student_accounts(
    db: Session,
    actor: User,
    *,
    apply: bool,
    password_factory: Callable[[], str] = generate_temporary_password,
) -> dict:
    if actor.role != "owner" or not actor.is_active:
        raise RuntimeError("An active owner account is required")

    students = (
        db.query(Student)
        .filter(Student.status == "active")
        .order_by(Student.full_name, Student.admission_number)
        .all()
    )
    existing_links = {
        row.student_id: row
        for row in db.query(StudentAccount).all()
    }
    users_by_mobile = {
        row.mobile: row
        for row in db.query(User).filter(User.mobile.is_not(None)).all()
        if row.mobile
    }
    seen_student_mobiles: dict[str, Student] = {}
    eligible: list[tuple[Student, str]] = []
    missing_mobile: list[dict] = []
    invalid_mobile: list[dict] = []
    duplicate_mobile: list[dict] = []
    conflicts: list[dict] = []
    existing: list[dict] = []

    for student in students:
        if student.id in existing_links:
            existing.append({
                "admissionNumber": student.admission_number,
                "fullName": student.full_name,
            })
            continue
        if not student.mobile or not student.mobile.strip():
            missing_mobile.append({
                "admissionNumber": student.admission_number,
                "fullName": student.full_name,
            })
            continue
        mobile = _canonical_mobile(student)
        if not mobile:
            invalid_mobile.append({
                "admissionNumber": student.admission_number,
                "fullName": student.full_name,
                "mobile": student.mobile,
            })
            continue
        if mobile in seen_student_mobiles:
            first = seen_student_mobiles[mobile]
            duplicate_mobile.append({
                "mobile": mobile,
                "students": [
                    {
                        "admissionNumber": first.admission_number,
                        "fullName": first.full_name,
                    },
                    {
                        "admissionNumber": student.admission_number,
                        "fullName": student.full_name,
                    },
                ],
            })
            eligible = [item for item in eligible if item[1] != mobile]
            continue
        seen_student_mobiles[mobile] = student
        existing_user = users_by_mobile.get(mobile)
        if existing_user:
            conflicts.append({
                "admissionNumber": student.admission_number,
                "fullName": student.full_name,
                "mobile": mobile,
                "existingRole": existing_user.role,
            })
            continue
        eligible.append((student, mobile))

    current_account_count = db.query(StudentAccount).count()
    available_slots = max(0, PORTAL_ACCOUNT_LIMIT - current_account_count)
    if len(eligible) > available_slots:
        raise RuntimeError(
            f"{len(eligible)} accounts are eligible but only {available_slots} portal slots remain"
        )

    credentials: list[ProvisionedCredential] = []
    if apply:
        for student, mobile in eligible:
            password = password_factory()
            account_user = User(
                mobile=mobile,
                full_name=student.full_name,
                role="student",
                password_hash=hash_password(password),
                is_active=True,
                must_change_password=True,
            )
            db.add(account_user)
            db.flush()
            db.add(StudentAccount(user_id=account_user.id, student_id=student.id))
            audit(
                db,
                actor,
                "settings.student_access.bulk_create",
                "student",
                student.id,
                after={"user_id": account_user.id, "mobile": mobile},
            )
            credentials.append(ProvisionedCredential(
                admission_number=student.admission_number,
                full_name=student.full_name,
                mobile=mobile,
                temporary_password=password,
            ))

    return {
        "activeStudents": len(students),
        "existingAccounts": len(existing),
        "eligibleAccounts": len(eligible),
        "createdAccounts": len(credentials),
        "missingMobile": missing_mobile,
        "invalidMobile": invalid_mobile,
        "duplicateMobile": duplicate_mobile,
        "conflicts": conflicts,
        "credentials": credentials,
    }


def write_credentials(path: Path, credentials: list[ProvisionedCredential]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
        text=True,
    )
    temporary_path = Path(temporary_name)
    try:
        os.chmod(temporary_path, 0o600)
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([
                "Admission number",
                "Student name",
                "Mobile number",
                "Temporary password",
            ])
            for item in credentials:
                writer.writerow([
                    item.admission_number,
                    item.full_name,
                    item.mobile,
                    item.temporary_password,
                ])
        temporary_path.replace(path)
        os.chmod(path, 0o600)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def verify_credentials(
    db: Session,
    path: Path,
    *,
    login_url: str | None = None,
) -> dict:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    verified = 0
    for row in rows:
        mobile = normalize_mobile(row["Mobile number"])
        user = db.query(User).filter_by(mobile=mobile).first()
        if (
            not user
            or user.role != "student"
            or not user.is_active
            or not user.must_change_password
        ):
            raise RuntimeError(f"Student account verification failed for {mobile}")
        if not db.query(StudentAccount).filter_by(user_id=user.id).first():
            raise RuntimeError(f"Student link verification failed for {mobile}")
        if not verify_password(row["Temporary password"], user.password_hash):
            raise RuntimeError(f"Password verification failed for {mobile}")
        verified += 1

    login_checks = 0
    if login_url and rows:
        sample_indexes = sorted({0, len(rows) // 2, len(rows) - 1})
        base_url = login_url.rstrip("/")
        for index in sample_indexes:
            row = rows[index]
            payload = json.dumps({
                "mobile": normalize_mobile(row["Mobile number"]),
                "password": row["Temporary password"],
            }).encode()
            request = urllib.request.Request(
                f"{base_url}/api/auth/login",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = json.load(response)
            except urllib.error.HTTPError as error:
                raise RuntimeError(
                    f"Live login verification failed with HTTP {error.code}"
                ) from error
            token = body.get("access_token")
            if not token or body.get("user", {}).get("role") != "student":
                raise RuntimeError("Live login returned an invalid student session")
            logout = urllib.request.Request(
                f"{base_url}/api/auth/logout",
                data=b"",
                headers={"Authorization": f"Bearer {token}"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(logout, timeout=60) as response:
                    if response.status != 204:
                        raise RuntimeError("Live logout verification failed")
            except urllib.error.HTTPError as error:
                raise RuntimeError(
                    f"Live logout verification failed with HTTP {error.code}"
                ) from error
            login_checks += 1
    return {"credentials": verified, "liveLogins": login_checks}


def _print_summary(result: dict) -> None:
    print(f"Active students: {result['activeStudents']}")
    print(f"Existing portal accounts: {result['existingAccounts']}")
    print(f"Eligible new accounts: {result['eligibleAccounts']}")
    print(f"Created accounts: {result['createdAccounts']}")
    print(f"Missing mobile: {len(result['missingMobile'])}")
    print(f"Invalid mobile: {len(result['invalidMobile'])}")
    print(f"Duplicate mobile conflicts: {len(result['duplicateMobile'])}")
    print(f"Existing user conflicts: {len(result['conflicts'])}")
    for item in result["missingMobile"]:
        print(f"MISSING MOBILE: {item['admissionNumber']} · {item['fullName']}")
    for item in result["invalidMobile"]:
        print(
            f"INVALID MOBILE: {item['admissionNumber']} · "
            f"{item['fullName']} · {item['mobile']}"
        )
    for item in result["conflicts"]:
        print(
            f"ACCOUNT CONFLICT: {item['admissionNumber']} · "
            f"{item['fullName']} · {item['mobile']} ({item['existingRole']})"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--actor-mobile")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-credentials", type=Path)
    parser.add_argument("--login-url")
    args = parser.parse_args()

    if args.verify_credentials:
        with SessionLocal() as db:
            result = verify_credentials(
                db,
                args.verify_credentials,
                login_url=args.login_url,
            )
        print(f"Verified credential records: {result['credentials']}")
        print(f"Verified live login/logout samples: {result['liveLogins']}")
        return

    if args.apply and (not args.actor_mobile or not args.output):
        parser.error("--apply requires --actor-mobile and --output")

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

        result = provision_student_accounts(db, actor, apply=args.apply)
        _print_summary(result)
        if args.apply:
            try:
                write_credentials(args.output, result["credentials"])
                db.commit()
            except Exception:
                db.rollback()
                args.output.unlink(missing_ok=True)
                raise
            print(f"Credentials written securely to: {args.output}")
        else:
            db.rollback()
            print("Dry run only. No accounts were created.")


if __name__ == "__main__":
    main()
