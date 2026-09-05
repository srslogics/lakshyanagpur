"""Store staff daily status and work duration from biometric reports."""

import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from alembic import op
import sqlalchemy as sa


revision = "f4b8c1d2e903"
down_revision = "ea51c7b902d4"
branch_labels = None
depends_on = None
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _utc(day: str, clock: str | None):
    if not clock:
        return None
    return datetime.fromisoformat(f"{day}T{clock}:00").replace(tzinfo=INDIA_TZ).astimezone(timezone.utc)


def _seed_august_workdays():
    bind = op.get_bind()
    source = json.loads((Path(__file__).parents[2] / "app/data/august_2026_staff_workdays.json").read_text())
    actor_id = bind.execute(sa.text(
        "SELECT id FROM users WHERE role = 'owner' ORDER BY created_at LIMIT 1"
    )).scalar()
    if not actor_id:
        return
    now = datetime.now(timezone.utc)
    names = {row[0]: row[1] for row in source["rows"]}
    for device_id, device_name in names.items():
        identity_id = bind.execute(sa.text("""
            SELECT id FROM device_attendance_identities
            WHERE device_key = 'x2008-abfr220607313' AND device_user_id = :device_user_id
        """), {"device_user_id": device_id}).scalar()
        if identity_id:
            bind.execute(sa.text("""
                UPDATE device_attendance_identities SET device_name = :device_name, updated_at = :updated_at
                WHERE id = :identity_id
            """), {"device_name": device_name, "updated_at": now, "identity_id": identity_id})
        else:
            bind.execute(sa.text("""
                INSERT INTO device_attendance_identities
                    (id, device_key, device_user_id, device_name, student_id, staff_user_id,
                     is_staff_device, is_ignored, created_by, created_at, updated_at)
                VALUES
                    (:id, 'x2008-abfr220607313', :device_user_id, :device_name, NULL, NULL,
                     1, 0, :created_by, :created_at, :updated_at)
            """), {
                "id": f"dai_staff_aug26_{device_id}",
                "device_user_id": device_id,
                "device_name": device_name,
                "created_by": actor_id,
                "created_at": now,
                "updated_at": now,
            })
    batch_id = bind.execute(sa.text(
        "SELECT id FROM biometric_import_batches WHERE source_hash = :source_hash"
    ), {"source_hash": source["sourceHash"]}).scalar()
    if not batch_id:
        batch_id = "bio_staff_aug_2026_duration"
        bind.execute(sa.text("""
            INSERT INTO biometric_import_batches
                (id, device_key, source_name, source_hash, source_sheet, rows_seen,
                 attendance_days, matched_students, ignored_device_ids, duplicate_rows,
                 status, actor_id, created_at)
            VALUES
                (:id, :device_key, :source_name, :source_hash, :source_sheet, :rows_seen,
                 :attendance_days, 0, 0, 0, 'completed', :actor_id, :created_at)
        """), {
            "id": batch_id,
            "device_key": "x2008-abfr220607313",
            "source_name": source["sourceName"],
            "source_hash": source["sourceHash"],
            "source_sheet": "WorkDurationReportFourPunch",
            "rows_seen": len(source["rows"]),
            "attendance_days": 31,
            "actor_id": actor_id,
            "created_at": now,
        })
    staff_ids = dict(bind.execute(sa.text("""
        SELECT device_user_id, staff_user_id
        FROM device_attendance_identities
        WHERE device_key = 'x2008-abfr220607313'
    """)).all())
    insert = sa.text("""
        INSERT INTO staff_attendance_workdays
            (id, import_batch_id, device_key, device_user_id, staff_user_id,
             attendance_date, attendance_status, first_punch_at, last_punch_at,
             work_duration_minutes, overtime_minutes, punch_count, created_at, updated_at)
        VALUES
            (:id, :import_batch_id, :device_key, :device_user_id, :staff_user_id,
             :attendance_date, :attendance_status, :first_punch_at, :last_punch_at,
             :work_duration_minutes, :overtime_minutes, :punch_count, :created_at, :updated_at)
    """)
    for index, row in enumerate(source["rows"], start=1):
        device_id, _name, day, status, arrival, departure, work_minutes, overtime_minutes, punch_count = row
        bind.execute(insert, {
            "id": f"saw_aug26_{index:03d}",
            "import_batch_id": batch_id,
            "device_key": "x2008-abfr220607313",
            "device_user_id": device_id,
            "staff_user_id": staff_ids.get(device_id),
            "attendance_date": datetime.fromisoformat(day).date(),
            "attendance_status": status,
            "first_punch_at": _utc(day, arrival),
            "last_punch_at": _utc(day, departure),
            "work_duration_minutes": work_minutes,
            "overtime_minutes": overtime_minutes,
            "punch_count": punch_count,
            "created_at": now,
            "updated_at": now,
        })


def upgrade():
    with op.batch_alter_table("staff_payroll") as batch_op:
        batch_op.alter_column(
            "absent_days",
            existing_type=sa.Integer(),
            type_=sa.Numeric(5, 1),
            existing_nullable=False,
        )
    op.create_table(
        "staff_attendance_workdays",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("import_batch_id", sa.String(64), sa.ForeignKey("biometric_import_batches.id"), nullable=False),
        sa.Column("device_key", sa.String(120), nullable=False),
        sa.Column("device_user_id", sa.String(120), nullable=False),
        sa.Column("staff_user_id", sa.String(64), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("attendance_status", sa.String(32), nullable=False),
        sa.Column("first_punch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_punch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("work_duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overtime_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("punch_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("device_key", "device_user_id", "attendance_date", name="uq_staff_attendance_workday"),
    )
    for column in ("import_batch_id", "device_key", "device_user_id", "staff_user_id", "attendance_date", "attendance_status", "first_punch_at", "last_punch_at"):
        op.create_index(f"ix_staff_attendance_workdays_{column}", "staff_attendance_workdays", [column])
    _seed_august_workdays()


def downgrade():
    op.drop_table("staff_attendance_workdays")
    with op.batch_alter_table("staff_payroll") as batch_op:
        batch_op.alter_column(
            "absent_days",
            existing_type=sa.Numeric(5, 1),
            type_=sa.Integer(),
            existing_nullable=False,
        )
