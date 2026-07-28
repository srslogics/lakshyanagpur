"""add mandatory initial password change state"""

from alembic import op
import sqlalchemy as sa


revision = "e5a21c7d9b40"
down_revision = "c4d9a8f13b72"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column("users", "must_change_password")
