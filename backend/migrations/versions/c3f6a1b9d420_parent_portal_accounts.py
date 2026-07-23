"""separate student and parent portal identities"""

from alembic import op
import sqlalchemy as sa


revision = "c3f6a1b9d420"
down_revision = "a91d6e20c4f8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "parent_accounts",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("contact_type", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_parent_accounts_student_id", "parent_accounts", ["student_id"])
    op.create_index("ix_parent_accounts_contact_type", "parent_accounts", ["contact_type"])
    op.execute(
        """
        UPDATE users
        SET role = 'student'
        WHERE role = 'parent_student'
          AND id IN (SELECT user_id FROM student_accounts)
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE users
        SET role = 'parent_student'
        WHERE role = 'student'
          AND id IN (SELECT user_id FROM student_accounts)
        """
    )
    op.drop_index("ix_parent_accounts_contact_type", table_name="parent_accounts")
    op.drop_index("ix_parent_accounts_student_id", table_name="parent_accounts")
    op.drop_table("parent_accounts")
