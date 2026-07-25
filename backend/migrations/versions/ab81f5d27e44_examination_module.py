"""examination module

Revision ID: ab81f5d27e44
Revises: 91b7d45e2ac0
"""

from alembic import op
import sqlalchemy as sa


revision = "ab81f5d27e44"
down_revision = "91b7d45e2ac0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "examinations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("batch_id", sa.String(length=64), nullable=False),
        sa.Column("subject_id", sa.String(length=64), nullable=False),
        sa.Column("faculty_id", sa.String(length=64), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("max_marks", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("pass_marks", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["faculty_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_examinations_batch_id", "examinations", ["batch_id"])
    op.create_index("ix_examinations_created_by", "examinations", ["created_by"])
    op.create_index("ix_examinations_faculty_id", "examinations", ["faculty_id"])
    op.create_index("ix_examinations_name", "examinations", ["name"])
    op.create_index("ix_examinations_published_at", "examinations", ["published_at"])
    op.create_index("ix_examinations_scheduled_at", "examinations", ["scheduled_at"])
    op.create_index("ix_examinations_status", "examinations", ["status"])
    op.create_index("ix_examinations_subject_id", "examinations", ["subject_id"])

    op.create_table(
        "examination_results",
        sa.Column("exam_id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("marks_obtained", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("result_status", sa.String(length=24), nullable=False),
        sa.Column("remarks", sa.String(length=500), nullable=False),
        sa.Column("entered_by", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["exam_id"], ["examinations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("exam_id", "student_id"),
    )
    op.create_index("ix_examination_results_entered_by", "examination_results", ["entered_by"])
    op.create_index("ix_examination_results_result_status", "examination_results", ["result_status"])


def downgrade():
    op.drop_index("ix_examination_results_result_status", table_name="examination_results")
    op.drop_index("ix_examination_results_entered_by", table_name="examination_results")
    op.drop_table("examination_results")
    op.drop_index("ix_examinations_subject_id", table_name="examinations")
    op.drop_index("ix_examinations_status", table_name="examinations")
    op.drop_index("ix_examinations_scheduled_at", table_name="examinations")
    op.drop_index("ix_examinations_published_at", table_name="examinations")
    op.drop_index("ix_examinations_name", table_name="examinations")
    op.drop_index("ix_examinations_faculty_id", table_name="examinations")
    op.drop_index("ix_examinations_created_by", table_name="examinations")
    op.drop_index("ix_examinations_batch_id", table_name="examinations")
    op.drop_table("examinations")
