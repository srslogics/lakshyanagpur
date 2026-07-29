"""invalidate issued sessions after credential changes

Revision ID: b91c4a72e608
Revises: aa42d7e91c30
"""

from alembic import op
import sqlalchemy as sa


revision = "b91c4a72e608"
down_revision = "aa42d7e91c30"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column(
                "token_version",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_column("token_version")
