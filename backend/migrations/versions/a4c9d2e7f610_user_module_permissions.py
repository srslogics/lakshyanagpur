"""user module permissions

Revision ID: a4c9d2e7f610
Revises: e1f4a7b2c903
"""

from alembic import op
import sqlalchemy as sa


revision = "a4c9d2e7f610"
down_revision = "e1f4a7b2c903"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_module_permissions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("can_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_create", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_edit", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "module", name="uq_user_module_permission"),
    )
    op.create_index("ix_user_module_permissions_user_id", "user_module_permissions", ["user_id"])
    op.create_index("ix_user_module_permissions_module", "user_module_permissions", ["module"])


def downgrade():
    op.drop_index("ix_user_module_permissions_module", table_name="user_module_permissions")
    op.drop_index("ix_user_module_permissions_user_id", table_name="user_module_permissions")
    op.drop_table("user_module_permissions")
