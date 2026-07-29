"""Provision first-login credentials for the confirmed faculty roster.

Faculty with a confirmed mobile number sign in with mobile from the beginning.
Email is retained as a recovery/contact identity and is only a first-login
fallback while no mobile number has been assigned.
"""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.identity import normalize_mobile
from app.models import User
from app.security import hash_password, verify_password
from app.services import audit
from scripts.provision_student_accounts import generate_temporary_password


FACULTY_EMAILS = {
    "Meet Sir": "meet.faculty@lakshyanagpur.in",
    "Jitendra Sir": "jitendra.faculty@lakshyanagpur.in",
    "Anita Ma'am": "anita.faculty@lakshyanagpur.in",
    "Kanchan Ma'am": "kanchan.faculty@lakshyanagpur.in",
    "Kajal Ma'am": "kajal.faculty@lakshyanagpur.in",
}


@dataclass(frozen=True)
class FacultyCredential:
    full_name: str
    email: str
    mobile: str | None
    temporary_password: str


def provision_faculty_accounts(
    db: Session,
    actor: User,
    *,
    apply: bool,
    password_factory: Callable[[], str] = generate_temporary_password,
) -> dict:
    if actor.role != "owner" or not actor.is_active:
        raise RuntimeError("An active owner account is required")

    faculty_by_name = {
        row.full_name: row
        for row in db.query(User).filter(User.role == "faculty").all()
    }
    users_by_email = {
        str(row.email).lower(): row
        for row in db.query(User).filter(User.email.is_not(None)).all()
        if row.email
    }
    eligible: list[tuple[User, str]] = []
    existing: list[dict] = []
    missing_profiles: list[dict] = []
    conflicts: list[dict] = []

    for full_name, email in FACULTY_EMAILS.items():
        faculty = faculty_by_name.get(full_name)
        if not faculty:
            missing_profiles.append({"fullName": full_name, "email": email})
            continue
        if (
            faculty.mobile
            and faculty.password_hash != "unprovisioned"
        ) or (
            faculty.email
            and str(faculty.email).lower() == email
            and faculty.password_hash != "unprovisioned"
        ):
            existing.append({
                "fullName": full_name,
                "email": faculty.email,
                "mobile": faculty.mobile,
            })
            continue
        conflicting_user = users_by_email.get(email)
        if conflicting_user and conflicting_user.id != faculty.id:
            conflicts.append({
                "fullName": full_name,
                "email": email,
                "existingRole": conflicting_user.role,
            })
            continue
        eligible.append((faculty, email))

    credentials: list[FacultyCredential] = []
    if apply:
        for faculty, email in eligible:
            password = password_factory()
            before = {
                "email": faculty.email,
                "mobile": faculty.mobile,
                "provisioned": faculty.password_hash != "unprovisioned",
            }
            faculty.email = email
            faculty.password_hash = hash_password(password)
            faculty.is_active = True
            faculty.must_change_password = True
            audit(
                db,
                actor,
                "settings.faculty_access.email_onboard",
                "user",
                faculty.id,
                before=before,
                after={
                    "email": email,
                    "mobile": faculty.mobile,
                    "provisioned": True,
                    "mustChangePassword": True,
                },
            )
            credentials.append(FacultyCredential(
                full_name=faculty.full_name,
                email=email,
                mobile=faculty.mobile,
                temporary_password=password,
            ))

    return {
        "facultyProfiles": len(FACULTY_EMAILS),
        "existingAccounts": len(existing),
        "eligibleAccounts": len(eligible),
        "createdAccounts": len(credentials),
        "missingProfiles": missing_profiles,
        "conflicts": conflicts,
        "credentials": credentials,
    }


def write_credentials(path: Path, credentials: list[FacultyCredential]) -> None:
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
                "Faculty name",
                "Mobile number",
                "First-login email",
                "Temporary password",
            ])
            for item in credentials:
                writer.writerow([
                    item.full_name,
                    item.mobile or "",
                    item.email,
                    item.temporary_password,
                ])
        temporary_path.replace(path)
        os.chmod(path, 0o600)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def verify_credentials(db: Session, path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        email = row["First-login email"].strip().lower()
        faculty = db.query(User).filter_by(email=email, role="faculty").first()
        expected_mobile = normalize_mobile(row["Mobile number"]) if row["Mobile number"] else None
        if (
            not faculty
            or not faculty.is_active
            or not faculty.must_change_password
            or faculty.mobile != expected_mobile
        ):
            raise RuntimeError(f"Faculty first-login account verification failed for {email}")
        if not verify_password(row["Temporary password"], faculty.password_hash):
            raise RuntimeError(f"Faculty password verification failed for {email}")
    return len(rows)


def _print_summary(result: dict) -> None:
    print(f"Confirmed faculty profiles: {result['facultyProfiles']}")
    print(f"Existing configured accounts: {result['existingAccounts']}")
    print(f"Eligible new accounts: {result['eligibleAccounts']}")
    print(f"Created accounts: {result['createdAccounts']}")
    print(f"Missing profiles: {len(result['missingProfiles'])}")
    print(f"Email conflicts: {len(result['conflicts'])}")
    for item in result["missingProfiles"]:
        print(f"MISSING PROFILE: {item['fullName']}")
    for item in result["conflicts"]:
        print(
            f"EMAIL CONFLICT: {item['fullName']} · "
            f"{item['email']} ({item['existingRole']})"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--actor-mobile")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-credentials", type=Path)
    args = parser.parse_args()

    with SessionLocal() as db:
        if args.verify_credentials:
            verified = verify_credentials(db, args.verify_credentials)
            print(f"Verified faculty credential records: {verified}")
            return

        if args.apply and (not args.actor_mobile or not args.output):
            parser.error("--apply requires --actor-mobile and --output")
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

        result = provision_faculty_accounts(db, actor, apply=args.apply)
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
