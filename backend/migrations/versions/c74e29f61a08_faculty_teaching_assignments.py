"""faculty teaching assignments

Revision ID: c74e29f61a08
Revises: ab81f5d27e44
"""

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "c74e29f61a08"
down_revision = "ab81f5d27e44"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "faculty_teaching_assignments",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("faculty_id", sa.String(length=64), nullable=False),
        sa.Column("batch_id", sa.String(length=64), nullable=False),
        sa.Column("subject_id", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["faculty_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "faculty_id",
            "batch_id",
            "subject_id",
            name="uq_faculty_teaching_assignment",
        ),
    )
    op.create_index(
        "ix_faculty_teaching_assignments_batch_id",
        "faculty_teaching_assignments",
        ["batch_id"],
    )
    op.create_index(
        "ix_faculty_teaching_assignments_created_by",
        "faculty_teaching_assignments",
        ["created_by"],
    )
    op.create_index(
        "ix_faculty_teaching_assignments_faculty_id",
        "faculty_teaching_assignments",
        ["faculty_id"],
    )
    op.create_index(
        "ix_faculty_teaching_assignments_is_active",
        "faculty_teaching_assignments",
        ["is_active"],
    )
    op.create_index(
        "ix_faculty_teaching_assignments_subject_id",
        "faculty_teaching_assignments",
        ["subject_id"],
    )

    connection = op.get_bind()
    class_sessions = sa.table(
        "class_sessions",
        sa.column("faculty_id", sa.String(length=64)),
        sa.column("batch_id", sa.String(length=64)),
        sa.column("subject_id", sa.String(length=64)),
        sa.column("created_by", sa.String(length=64)),
    )
    rows = connection.execute(
        sa.select(
            class_sessions.c.faculty_id,
            class_sessions.c.batch_id,
            class_sessions.c.subject_id,
            sa.func.min(class_sessions.c.created_by).label("created_by"),
        ).group_by(
            class_sessions.c.faculty_id,
            class_sessions.c.batch_id,
            class_sessions.c.subject_id,
        )
    ).mappings()
    assignment_table = sa.table(
        "faculty_teaching_assignments",
        sa.column("id", sa.String(length=64)),
        sa.column("faculty_id", sa.String(length=64)),
        sa.column("batch_id", sa.String(length=64)),
        sa.column("subject_id", sa.String(length=64)),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_by", sa.String(length=64)),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    timestamp = datetime.now(timezone.utc)
    payload = [
        {
            "id": f"fta_{uuid4().hex}",
            "faculty_id": row["faculty_id"],
            "batch_id": row["batch_id"],
            "subject_id": row["subject_id"],
            "is_active": True,
            "created_by": row["created_by"],
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        for row in rows
    ]
    if payload:
        op.bulk_insert(assignment_table, payload)


def downgrade():
    op.drop_index(
        "ix_faculty_teaching_assignments_subject_id",
        table_name="faculty_teaching_assignments",
    )
    op.drop_index(
        "ix_faculty_teaching_assignments_is_active",
        table_name="faculty_teaching_assignments",
    )
    op.drop_index(
        "ix_faculty_teaching_assignments_faculty_id",
        table_name="faculty_teaching_assignments",
    )
    op.drop_index(
        "ix_faculty_teaching_assignments_created_by",
        table_name="faculty_teaching_assignments",
    )
    op.drop_index(
        "ix_faculty_teaching_assignments_batch_id",
        table_name="faculty_teaching_assignments",
    )
    op.drop_table("faculty_teaching_assignments")
