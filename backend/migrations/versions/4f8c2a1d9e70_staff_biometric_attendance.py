"""staff biometric attendance

Revision ID: 4f8c2a1d9e70
Revises: d2e8f4a1c630
"""

from datetime import date, datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "4f8c2a1d9e70"
down_revision = "d2e8f4a1c630"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "device_attendance_identities",
        sa.Column("staff_user_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "device_attendance_identities",
        sa.Column("is_staff_device", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_foreign_key(
        "fk_device_attendance_identity_staff",
        "device_attendance_identities",
        "users",
        ["staff_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_device_attendance_identities_staff_user_id",
        "device_attendance_identities",
        ["staff_user_id"],
    )
    op.create_unique_constraint(
        "uq_device_attendance_staff",
        "device_attendance_identities",
        ["device_key", "staff_user_id"],
    )

    op.add_column(
        "biometric_attendance_days",
        sa.Column("staff_user_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "biometric_attendance_days",
        sa.Column("last_punch_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_biometric_attendance_day_staff",
        "biometric_attendance_days",
        "users",
        ["staff_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_biometric_attendance_days_staff_user_id",
        "biometric_attendance_days",
        ["staff_user_id"],
    )
    op.create_index(
        "ix_biometric_attendance_days_last_punch_at",
        "biometric_attendance_days",
        ["last_punch_at"],
    )

    # The supplied Form-J exports identify the only staff punch as device ID 50,
    # without an employee name. Preserve it as unassigned staff until the owner
    # links that device ID to the correct account.
    connection = op.get_bind()
    batch = connection.execute(sa.text("""
        SELECT id, actor_id
        FROM biometric_import_batches
        WHERE device_key = :device_key
          AND source_hash IN (:first_hash, :second_hash)
        ORDER BY created_at DESC
        LIMIT 1
    """), {
        "device_key": "x2008-abfr220607313",
        "first_hash": "164a269dd3700944d8112e4110f183451fafafbc74c830e8064ee9fabfa08efc",
        "second_hash": "fa467ecce3ba16b9daae802f3150c3d2262f06e45b410810f48610a054cda048",
    }).mappings().first()
    if batch:
        now = datetime.now(timezone.utc)
        existing_mapping = connection.execute(sa.text("""
            SELECT id FROM device_attendance_identities
            WHERE device_key = :device_key AND device_user_id = :device_user_id
        """), {"device_key": "x2008-abfr220607313", "device_user_id": "50"}).scalar_one_or_none()
        if existing_mapping:
            connection.execute(sa.text("""
                UPDATE device_attendance_identities
                SET student_id = NULL, staff_user_id = NULL,
                    is_staff_device = :is_staff_device, is_ignored = :is_ignored,
                    updated_at = :updated_at
                WHERE id = :mapping_id
            """), {
                "mapping_id": existing_mapping,
                "is_staff_device": True,
                "is_ignored": False,
                "updated_at": now,
            })
        else:
            connection.execute(sa.text("""
                INSERT INTO device_attendance_identities
                    (id, device_key, device_user_id, student_id, staff_user_id,
                     is_staff_device, is_ignored, created_by, created_at, updated_at)
                VALUES
                    (:id, :device_key, :device_user_id, NULL, NULL,
                     :is_staff_device, :is_ignored, :created_by, :created_at, :updated_at)
            """), {
                "id": "dai_staff_device_50",
                "device_key": "x2008-abfr220607313",
                "device_user_id": "50",
                "is_staff_device": True,
                "is_ignored": False,
                "created_by": batch["actor_id"],
                "created_at": now,
                "updated_at": now,
            })
        existing_day = connection.execute(sa.text("""
            SELECT id FROM biometric_attendance_days
            WHERE device_key = :device_key
              AND device_user_id = :device_user_id
              AND attendance_date = :attendance_date
        """), {
            "device_key": "x2008-abfr220607313",
            "device_user_id": "50",
            "attendance_date": date(2026, 8, 10),
        }).scalar_one_or_none()
        if not existing_day:
            connection.execute(sa.text("""
                INSERT INTO biometric_attendance_days
                    (id, import_batch_id, device_key, device_user_id, student_id,
                     staff_user_id, attendance_date, first_punch_at, last_punch_at,
                     created_at, updated_at)
                VALUES
                    (:id, :import_batch_id, :device_key, :device_user_id, NULL,
                     NULL, :attendance_date, :first_punch_at, NULL,
                     :created_at, :updated_at)
            """), {
                "id": "bad_staff_device_50_20260810",
                "import_batch_id": batch["id"],
                "device_key": "x2008-abfr220607313",
                "device_user_id": "50",
                "attendance_date": date(2026, 8, 10),
                "first_punch_at": datetime(2026, 8, 10, 7, 55, tzinfo=timezone.utc),
                "created_at": now,
                "updated_at": now,
            })


def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("""
        DELETE FROM biometric_attendance_days WHERE id = :id
    """), {"id": "bad_staff_device_50_20260810"})
    connection.execute(sa.text("""
        DELETE FROM device_attendance_identities WHERE id = :id
    """), {"id": "dai_staff_device_50"})
    op.drop_index("ix_biometric_attendance_days_last_punch_at", table_name="biometric_attendance_days")
    op.drop_index("ix_biometric_attendance_days_staff_user_id", table_name="biometric_attendance_days")
    op.drop_constraint("fk_biometric_attendance_day_staff", "biometric_attendance_days", type_="foreignkey")
    op.drop_column("biometric_attendance_days", "last_punch_at")
    op.drop_column("biometric_attendance_days", "staff_user_id")

    op.drop_constraint("uq_device_attendance_staff", "device_attendance_identities", type_="unique")
    op.drop_index("ix_device_attendance_identities_staff_user_id", table_name="device_attendance_identities")
    op.drop_constraint("fk_device_attendance_identity_staff", "device_attendance_identities", type_="foreignkey")
    op.drop_column("device_attendance_identities", "is_staff_device")
    op.drop_column("device_attendance_identities", "staff_user_id")
