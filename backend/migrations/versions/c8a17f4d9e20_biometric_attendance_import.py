"""biometric attendance file imports

Revision ID: c8a17f4d9e20
Revises: b6d4e91a2f70
"""

from alembic import op
import sqlalchemy as sa


revision = "c8a17f4d9e20"
down_revision = "b6d4e91a2f70"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "device_attendance_identities",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("device_key", sa.String(length=120), nullable=False),
        sa.Column("device_user_id", sa.String(length=120), nullable=False),
        sa.Column("student_id", sa.String(length=64), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True),
        sa.Column("is_ignored", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("device_key", "device_user_id", name="uq_device_attendance_user"),
        sa.UniqueConstraint("device_key", "student_id", name="uq_device_attendance_student"),
    )
    for column in ("device_key", "device_user_id", "student_id", "created_by"):
        op.create_index(f"ix_device_attendance_identities_{column}", "device_attendance_identities", [column])

    op.create_table(
        "biometric_import_batches",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("device_key", sa.String(length=120), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("source_sheet", sa.String(length=255), nullable=True),
        sa.Column("rows_seen", sa.Integer(), nullable=False),
        sa.Column("attendance_days", sa.Integer(), nullable=False),
        sa.Column("matched_students", sa.Integer(), nullable=False),
        sa.Column("ignored_device_ids", sa.Integer(), nullable=False),
        sa.Column("duplicate_rows", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("actor_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_biometric_import_batches_device_key", "biometric_import_batches", ["device_key"])
    op.create_index("ix_biometric_import_batches_source_hash", "biometric_import_batches", ["source_hash"], unique=True)
    op.create_index("ix_biometric_import_batches_status", "biometric_import_batches", ["status"])
    op.create_index("ix_biometric_import_batches_actor_id", "biometric_import_batches", ["actor_id"])

    op.create_table(
        "biometric_attendance_days",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("import_batch_id", sa.String(length=64), sa.ForeignKey("biometric_import_batches.id"), nullable=False),
        sa.Column("device_key", sa.String(length=120), nullable=False),
        sa.Column("device_user_id", sa.String(length=120), nullable=False),
        sa.Column("student_id", sa.String(length=64), sa.ForeignKey("students.id", ondelete="SET NULL"), nullable=True),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("first_punch_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("device_key", "device_user_id", "attendance_date", name="uq_biometric_device_user_day"),
    )
    for column in ("import_batch_id", "device_key", "device_user_id", "student_id", "attendance_date", "first_punch_at"):
        op.create_index(f"ix_biometric_attendance_days_{column}", "biometric_attendance_days", [column])


def downgrade():
    op.drop_table("biometric_attendance_days")
    op.drop_table("biometric_import_batches")
    op.drop_table("device_attendance_identities")
