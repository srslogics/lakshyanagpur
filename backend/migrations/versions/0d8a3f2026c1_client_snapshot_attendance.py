"""client-confirmed attendance period summaries

Revision ID: 0d8a3f2026c1
Revises: f63a1d9b7e20
"""

from alembic import op
import sqlalchemy as sa


revision = "0d8a3f2026c1"
down_revision = "f63a1d9b7e20"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("class_sessions") as batch:
        batch.alter_column(
            "created_by",
            existing_type=sa.String(length=64),
            nullable=True,
        )
    op.create_table(
        "attendance_period_summaries",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("source_student_code", sa.String(length=24), nullable=False),
        sa.Column("batch_name", sa.String(length=120), nullable=False),
        sa.Column("mentor_name", sa.String(length=255), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("present_days", sa.Integer(), nullable=False),
        sa.Column("absent_days", sa.Integer(), nullable=False),
        sa.Column("working_days", sa.Integer(), nullable=False),
        sa.Column("attendance_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_reference", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id",
            "period_start",
            "period_end",
            name="uq_attendance_period_student",
        ),
    )
    op.create_index(
        "ix_attendance_period_summaries_student_id",
        "attendance_period_summaries",
        ["student_id"],
    )
    op.create_index(
        "ix_attendance_period_summaries_source_student_code",
        "attendance_period_summaries",
        ["source_student_code"],
    )
    op.create_index(
        "ix_attendance_period_summaries_batch_name",
        "attendance_period_summaries",
        ["batch_name"],
    )
    op.create_index(
        "ix_attendance_period_summaries_mentor_name",
        "attendance_period_summaries",
        ["mentor_name"],
    )
    op.create_index(
        "ix_attendance_period_summaries_period_start",
        "attendance_period_summaries",
        ["period_start"],
    )
    op.create_index(
        "ix_attendance_period_summaries_period_end",
        "attendance_period_summaries",
        ["period_end"],
    )
    op.create_index(
        "ix_attendance_period_summaries_source_reference",
        "attendance_period_summaries",
        ["source_reference"],
    )
    op.create_index(
        "ix_attendance_period_summaries_status",
        "attendance_period_summaries",
        ["status"],
    )


def downgrade():
    op.drop_table("attendance_period_summaries")
    with op.batch_alter_table("class_sessions") as batch:
        batch.alter_column(
            "created_by",
            existing_type=sa.String(length=64),
            nullable=False,
        )
