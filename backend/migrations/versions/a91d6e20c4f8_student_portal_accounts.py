"""student portal account mapping"""
from alembic import op
import sqlalchemy as sa

revision = "a91d6e20c4f8"
down_revision = "f2a7c91d4b63"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "student_accounts",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_student_accounts_student_id", "student_accounts", ["student_id"], unique=True)


def downgrade():
    op.drop_index("ix_student_accounts_student_id", table_name="student_accounts")
    op.drop_table("student_accounts")
