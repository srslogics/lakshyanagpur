"""Assign client-confirmed faculty mobile numbers with audit records."""

from __future__ import annotations

import argparse

from sqlalchemy.orm import Session

from app.client_master import FACULTIES, FACULTY_MOBILE_SOURCE
from app.database import SessionLocal
from app.identity import normalize_mobile
from app.models import User
from app.services import audit


FACULTY_MOBILES = {
    definition["name"]: normalize_mobile(definition["mobile"])
    for definition in FACULTIES
}


def assign_faculty_mobiles(
    db: Session,
    actor: User,
    *,
    apply: bool,
) -> dict:
    if actor.role != "owner" or not actor.is_active:
        raise RuntimeError("An active owner account is required")

    faculty_by_name = {
        row.full_name: row
        for row in db.query(User).filter(User.role == "faculty").all()
    }
    users_by_mobile = {
        row.mobile: row
        for row in db.query(User).filter(User.mobile.is_not(None)).all()
        if row.mobile
    }
    eligible: list[tuple[User, str]] = []
    existing: list[dict] = []
    missing_profiles: list[dict] = []
    conflicts: list[dict] = []

    for full_name, mobile in FACULTY_MOBILES.items():
        faculty = faculty_by_name.get(full_name)
        if not faculty:
            missing_profiles.append({"fullName": full_name, "mobile": mobile})
            continue
        if faculty.mobile == mobile:
            existing.append({"fullName": full_name, "mobile": mobile})
            continue
        if faculty.mobile:
            conflicts.append({
                "fullName": full_name,
                "mobile": mobile,
                "reason": "Faculty profile already has a different mobile number",
            })
            continue
        conflicting_user = users_by_mobile.get(mobile)
        if conflicting_user and conflicting_user.id != faculty.id:
            conflicts.append({
                "fullName": full_name,
                "mobile": mobile,
                "reason": f"Mobile number belongs to {conflicting_user.full_name}",
            })
            continue
        eligible.append((faculty, mobile))

    if apply:
        for faculty, mobile in eligible:
            before = {"mobile": faculty.mobile}
            faculty.mobile = mobile
            audit(
                db,
                actor,
                "settings.faculty_access.mobile_assign",
                "user",
                faculty.id,
                before=before,
                after={
                    "mobile": mobile,
                    "source": FACULTY_MOBILE_SOURCE,
                },
            )

    return {
        "facultyProfiles": len(FACULTY_MOBILES),
        "existingAssignments": len(existing),
        "eligibleAssignments": len(eligible),
        "assignedMobiles": len(eligible) if apply else 0,
        "missingProfiles": missing_profiles,
        "conflicts": conflicts,
    }


def _print_summary(result: dict) -> None:
    print(f"Confirmed faculty profiles: {result['facultyProfiles']}")
    print(f"Existing mobile assignments: {result['existingAssignments']}")
    print(f"Eligible mobile assignments: {result['eligibleAssignments']}")
    print(f"Assigned mobile numbers: {result['assignedMobiles']}")
    print(f"Missing profiles: {len(result['missingProfiles'])}")
    print(f"Conflicts: {len(result['conflicts'])}")
    for item in result["missingProfiles"]:
        print(f"MISSING PROFILE: {item['fullName']}")
    for item in result["conflicts"]:
        print(f"CONFLICT: {item['fullName']} · {item['reason']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--actor-mobile")
    args = parser.parse_args()
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

        result = assign_faculty_mobiles(db, actor, apply=args.apply)
        _print_summary(result)
        if args.apply:
            db.commit()
        else:
            db.rollback()
            print("Dry run only. No mobile numbers were assigned.")


if __name__ == "__main__":
    main()
