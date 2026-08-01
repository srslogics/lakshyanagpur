"""student-linked communication inbox and messages

Revision ID: e42b6c91a730
Revises: d31f7a9c2e10
"""

from alembic import op
import sqlalchemy as sa


revision = "e42b6c91a730"
down_revision = "d31f7a9c2e10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "communication_threads",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("subject_id", sa.String(length=64), nullable=True),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="open"),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_threads_student_id", "communication_threads", ["student_id"])
    op.create_index("ix_communication_threads_subject_id", "communication_threads", ["subject_id"])
    op.create_index("ix_communication_threads_status", "communication_threads", ["status"])
    op.create_index("ix_communication_threads_created_by", "communication_threads", ["created_by"])

    op.create_table(
        "communication_messages",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("thread_id", sa.String(length=64), nullable=False),
        sa.Column("sender_id", sa.String(length=64), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["communication_threads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_messages_thread_id", "communication_messages", ["thread_id"])
    op.create_index("ix_communication_messages_sender_id", "communication_messages", ["sender_id"])
    op.create_index("ix_communication_messages_created_at", "communication_messages", ["created_at"])


def downgrade():
    op.drop_index("ix_communication_messages_created_at", table_name="communication_messages")
    op.drop_index("ix_communication_messages_sender_id", table_name="communication_messages")
    op.drop_index("ix_communication_messages_thread_id", table_name="communication_messages")
    op.drop_table("communication_messages")
    op.drop_index("ix_communication_threads_created_by", table_name="communication_threads")
    op.drop_index("ix_communication_threads_status", table_name="communication_threads")
    op.drop_index("ix_communication_threads_subject_id", table_name="communication_threads")
    op.drop_index("ix_communication_threads_student_id", table_name="communication_threads")
    op.drop_table("communication_threads")
