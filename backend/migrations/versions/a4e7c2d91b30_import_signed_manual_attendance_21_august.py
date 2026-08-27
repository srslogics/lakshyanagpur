"""import signed manual attendance for 21 August 2026

Revision ID: a4e7c2d91b30
Revises: 9a6d4e2b1c80

The two paper registers supplied after the original August import are the
authoritative daily source for Tatva and Essential on 21 August. Existing
derived daily registers for that scope are consolidated to avoid double
counting. Raw biometric punch rows remain untouched.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re

from alembic import op
import sqlalchemy as sa


revision = "a4e7c2d91b30"
down_revision = "9a6d4e2b1c80"
branch_labels = None
depends_on = None


SOURCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "imports"
    / "manual_attendance_2026_08_18_27.json"
)
TARGET_DATE = "2026-08-21"


def _normalized_name(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").casefold())


def _tables():
    users = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("role", sa.String),
    )
    students = sa.table(
        "students",
        sa.column("id", sa.String),
        sa.column("full_name", sa.String),
    )
    profiles = sa.table(
        "student_academic_profiles",
        sa.column("student_id", sa.String),
        sa.column("source_student_code", sa.String),
    )
    registers = sa.table(
        "attendance_registers",
        sa.column("id", sa.String),
        sa.column("class_session_id", sa.String),
        sa.column("register_kind", sa.String),
        sa.column("attendance_date", sa.Date),
        sa.column("batch_name", sa.String),
        sa.column("stream_name", sa.String),
        sa.column("subject_name", sa.String),
        sa.column("status", sa.String),
        sa.column("submitted_at", sa.DateTime(timezone=True)),
        sa.column("submitted_by", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    entries = sa.table(
        "attendance_entries",
        sa.column("register_id", sa.String),
        sa.column("student_id", sa.String),
        sa.column("status", sa.String),
        sa.column("reason", sa.Text),
        sa.column("marked_by", sa.String),
        sa.column("arrival_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    audit_logs = sa.table(
        "audit_logs",
        sa.column("id", sa.String),
        sa.column("actor_id", sa.String),
        sa.column("action", sa.String),
        sa.column("entity_type", sa.String),
        sa.column("entity_id", sa.String),
        sa.column("before", sa.JSON),
        sa.column("after", sa.JSON),
        sa.column("request_id", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    return users, students, profiles, registers, entries, audit_logs


def _actor_id(connection, users):
    rows = connection.execute(
        sa.select(users.c.id, users.c.role).where(
            users.c.role.in_(("owner", "academic_coordinator", "attendance_operator"))
        )
    ).all()
    priority = {"owner": 0, "academic_coordinator": 1, "attendance_operator": 2}
    return min(rows, key=lambda row: priority.get(row.role, 99)).id if rows else None


def _student_maps(connection, students, profiles):
    student_rows = connection.execute(
        sa.select(students.c.id, students.c.full_name)
    ).all()
    profile_rows = connection.execute(
        sa.select(profiles.c.student_id, profiles.c.source_student_code)
    ).all()
    by_code = {row.source_student_code: row.student_id for row in profile_rows}
    by_name: dict[str, list[str]] = {}
    for row in student_rows:
        by_name.setdefault(_normalized_name(row.full_name), []).append(row.id)
    return by_code, by_name


def _resolve_roster(connection, manifest, students, profiles):
    by_code, by_name = _student_maps(connection, students, profiles)
    resolved: dict[str, dict[str, str]] = {}
    unresolved: list[dict[str, str]] = []
    for batch_name, roster in manifest["rosters"].items():
        resolved[batch_name] = {}
        for source in roster:
            code = source["code"]
            student_id = by_code.get(code)
            if not student_id:
                candidates = by_name.get(_normalized_name(source["name"]), [])
                if len(candidates) == 1:
                    student_id = candidates[0]
            if student_id:
                resolved[batch_name][code] = student_id
            else:
                unresolved.append(
                    {"batch": batch_name, "code": code, "name": source["name"]}
                )
    return resolved, unresolved


def _canonical_register(
    connection,
    registers,
    entries,
    attendance_date,
    batch_name,
    actor_id,
    now,
):
    existing = connection.execute(
        sa.select(
            registers.c.id,
            registers.c.register_kind,
        ).where(
            registers.c.class_session_id.is_(None),
            registers.c.attendance_date == attendance_date,
            registers.c.batch_name == batch_name,
            registers.c.stream_name == "__all__",
            registers.c.register_kind.in_(("manual", "biometric")),
        )
    ).all()
    deterministic_id = (
        f"reg_manual_{attendance_date.strftime('%Y%m%d')}_{batch_name.casefold()}"
    )
    canonical = next(
        (row for row in existing if row.id == deterministic_id),
        None,
    ) or next(
        (row for row in existing if row.register_kind == "manual"),
        None,
    ) or (existing[0] if existing else None)
    canonical_id = canonical.id if canonical else deterministic_id

    for row in existing:
        connection.execute(entries.delete().where(entries.c.register_id == row.id))
        if row.id != canonical_id:
            connection.execute(registers.delete().where(registers.c.id == row.id))

    values = {
        "class_session_id": None,
        "register_kind": "manual",
        "attendance_date": attendance_date,
        "batch_name": batch_name,
        "stream_name": "__all__",
        "subject_name": "Daily attendance",
        "status": "submitted",
        "submitted_at": now,
        "submitted_by": actor_id,
        "updated_at": now,
    }
    if canonical:
        connection.execute(
            registers.update().where(registers.c.id == canonical_id).values(**values)
        )
    else:
        connection.execute(
            registers.insert().values(id=canonical_id, created_at=now, **values)
        )
    return canonical_id, [row.id for row in existing]


def upgrade():
    manifest = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    sources = [row for row in manifest["registers"] if row["date"] == TARGET_DATE]
    if {row["batch"] for row in sources} != {"Tatva", "Essential"}:
        raise RuntimeError("The 21 August Tatva and Essential sources are required")

    connection = op.get_bind()
    users, students, profiles, registers, entries, audit_logs = _tables()
    actor_id = _actor_id(connection, users)
    if not actor_id:
        return

    resolved, unresolved = _resolve_roster(connection, manifest, students, profiles)
    if not any(resolved.values()):
        return

    now = datetime.now(timezone.utc)
    for source in sources:
        attendance_date = datetime.strptime(source["date"], "%Y-%m-%d").date()
        batch_name = source["batch"]
        absent_codes = set(source["absentCodes"])
        register_id, replaced_register_ids = _canonical_register(
            connection,
            registers,
            entries,
            attendance_date,
            batch_name,
            actor_id,
            now,
        )

        imported = 0
        present = 0
        absent = 0
        missing_codes = []
        for student in manifest["rosters"][batch_name]:
            code = student["code"]
            student_id = resolved[batch_name].get(code)
            if not student_id:
                missing_codes.append(code)
                continue
            is_absent = code in absent_codes
            connection.execute(
                entries.insert().values(
                    register_id=register_id,
                    student_id=student_id,
                    status="absent" if is_absent else "present",
                    reason=(
                        "Marked absent on signed paper register"
                        if is_absent
                        else "Signature present on signed paper register"
                    ),
                    marked_by=actor_id,
                    arrival_at=None,
                    updated_at=now,
                )
            )
            imported += 1
            present += int(not is_absent)
            absent += int(is_absent)

        audit_id = f"aud_manual_20260821_{batch_name.casefold()}"
        connection.execute(audit_logs.delete().where(audit_logs.c.id == audit_id))
        connection.execute(
            audit_logs.insert().values(
                id=audit_id,
                actor_id=actor_id,
                action="attendance.manual.paper_import",
                entity_type="attendance_register",
                entity_id=register_id,
                before={"replacedRegisterIds": replaced_register_ids},
                after={
                    "importId": "manual-attendance-2026-08-21-supplement",
                    "sourceImage": source["sourceImage"],
                    "date": source["date"],
                    "batch": batch_name,
                    "studentsImported": imported,
                    "present": present,
                    "absent": absent,
                    "unresolvedCodes": missing_codes,
                    "dateInferred": False,
                },
                request_id="manual-attendance-2026-08-21-supplement",
                created_at=now,
            )
        )

    if unresolved:
        unresolved_id = "aud_manual_attendance_unresolved_20260821"
        connection.execute(
            audit_logs.delete().where(audit_logs.c.id == unresolved_id)
        )
        connection.execute(
            audit_logs.insert().values(
                id=unresolved_id,
                actor_id=actor_id,
                action="attendance.manual.paper_import.unresolved",
                entity_type="attendance_import",
                entity_id="manual-attendance-2026-08-21-supplement",
                before=None,
                after={"unresolved": unresolved},
                request_id="manual-attendance-2026-08-21-supplement",
                created_at=now,
            )
        )


def downgrade():
    # Attendance is an auditable business record. Corrections are forward-only.
    pass
