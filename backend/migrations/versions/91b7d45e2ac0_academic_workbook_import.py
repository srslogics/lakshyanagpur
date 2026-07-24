"""academic workbook import, student profiles, subjects and daily attendance"""

from alembic import op
import sqlalchemy as sa


revision = "91b7d45e2ac0"
down_revision = "7c2e1f8a4d90"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "academic_import_batches",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("active_student_rows", sa.Integer(), nullable=False),
        sa.Column("attendance_entries", sa.Integer(), nullable=False),
        sa.Column("subject_selections", sa.Integer(), nullable=False),
        sa.Column("staged_source_rows", sa.Integer(), nullable=False),
        sa.Column("unresolved_items", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_academic_import_batches_source_hash", "academic_import_batches", ["source_hash"], unique=True)
    op.create_index("ix_academic_import_batches_status", "academic_import_batches", ["status"], unique=False)

    op.create_table(
        "academic_source_records",
        sa.Column("id", sa.String(length=96), nullable=False),
        sa.Column("import_batch_id", sa.String(length=64), nullable=False),
        sa.Column("source_sheet", sa.String(length=255), nullable=False),
        sa.Column("source_row", sa.Integer(), nullable=False),
        sa.Column("record_type", sa.String(length=40), nullable=False),
        sa.Column("source_key", sa.String(length=120), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=False),
        sa.Column("normalized_data", sa.JSON(), nullable=False),
        sa.Column("issues", sa.JSON(), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["academic_import_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_academic_source_records_import_batch_id", "academic_source_records", ["import_batch_id"], unique=False)
    op.create_index("ix_academic_source_records_record_type", "academic_source_records", ["record_type"], unique=False)
    op.create_index("ix_academic_source_records_source_key", "academic_source_records", ["source_key"], unique=False)
    op.create_index("ix_academic_source_records_source_sheet", "academic_source_records", ["source_sheet"], unique=False)
    op.create_index("ix_academic_source_records_student_id", "academic_source_records", ["student_id"], unique=False)

    op.create_table(
        "student_academic_profiles",
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("source_student_code", sa.String(length=24), nullable=False),
        sa.Column("batch_name", sa.String(length=120), nullable=False),
        sa.Column("source_stream", sa.String(length=120), nullable=True),
        sa.Column("mentor_name", sa.String(length=255), nullable=True),
        sa.Column("source_school_name", sa.String(length=255), nullable=True),
        sa.Column("source_primary_mobile", sa.String(length=20), nullable=True),
        sa.Column("source_secondary_mobile", sa.String(length=20), nullable=True),
        sa.Column("import_batch_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["academic_import_batches.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index("ix_student_academic_profiles_batch_name", "student_academic_profiles", ["batch_name"], unique=False)
    op.create_index("ix_student_academic_profiles_import_batch_id", "student_academic_profiles", ["import_batch_id"], unique=False)
    op.create_index("ix_student_academic_profiles_mentor_name", "student_academic_profiles", ["mentor_name"], unique=False)
    op.create_index("ix_student_academic_profiles_source_stream", "student_academic_profiles", ["source_stream"], unique=False)
    op.create_index("ix_student_academic_profiles_source_student_code", "student_academic_profiles", ["source_student_code"], unique=True)

    op.create_table(
        "student_subject_selections",
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("subject_name", sa.String(length=120), nullable=False),
        sa.Column("source_value", sa.String(length=120), nullable=False),
        sa.Column("import_batch_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["academic_import_batches.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "subject_name"),
    )
    op.create_index("ix_student_subject_selections_import_batch_id", "student_subject_selections", ["import_batch_id"], unique=False)

    op.create_table(
        "daily_attendance_entries",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("import_batch_id", sa.String(length=64), nullable=False),
        sa.Column("source_student_code", sa.String(length=24), nullable=False),
        sa.Column("batch_name", sa.String(length=120), nullable=False),
        sa.Column("source_sheet", sa.String(length=255), nullable=False),
        sa.Column("source_row", sa.Integer(), nullable=False),
        sa.Column("source_column", sa.Integer(), nullable=False),
        sa.Column("source_date_label", sa.String(length=40), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=True),
        sa.Column("raw_status", sa.String(length=16), nullable=False),
        sa.Column("normalized_status", sa.String(length=24), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["academic_import_batches.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "source_sheet", "source_date_label", name="uq_daily_attendance_source_day"),
    )
    for column in (
        "attendance_date",
        "batch_name",
        "import_batch_id",
        "normalized_status",
        "raw_status",
        "source_date_label",
        "source_sheet",
        "source_student_code",
        "student_id",
    ):
        op.create_index(f"ix_daily_attendance_entries_{column}", "daily_attendance_entries", [column], unique=False)


def downgrade():
    op.drop_table("daily_attendance_entries")
    op.drop_table("student_subject_selections")
    op.drop_table("student_academic_profiles")
    op.drop_table("academic_source_records")
    op.drop_table("academic_import_batches")
