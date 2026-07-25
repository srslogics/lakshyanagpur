"""mobile login identity

Revision ID: d52f18a47b90
Revises: c74e29f61a08
"""

from alembic import op
import sqlalchemy as sa


revision = "d52f18a47b90"
down_revision = "c74e29f61a08"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("mobile", sa.String(length=10), nullable=True))
        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=255),
            nullable=True,
        )
        batch_op.create_index("ix_users_mobile", ["mobile"], unique=True)


def downgrade():
    connection = op.get_bind()
    missing_email = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE email IS NULL")
    ).scalar_one()
    if missing_email:
        raise RuntimeError("Cannot downgrade while users without email addresses exist")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_mobile")
        batch_op.drop_column("mobile")
        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=255),
            nullable=False,
        )
