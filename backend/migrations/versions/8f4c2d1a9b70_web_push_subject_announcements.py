"""add subject announcements and web push delivery

Revision ID: 8f4c2d1a9b70
Revises: 7e2f9a4c1b60
"""

from alembic import op
import sqlalchemy as sa


revision = "8f4c2d1a9b70"
down_revision = "7e2f9a4c1b60"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("notices", sa.Column("subject_id", sa.String(length=64), nullable=True))
    op.create_foreign_key("fk_notices_subject_id", "notices", "subjects", ["subject_id"], ["id"])
    op.create_index("ix_notices_subject_id", "notices", ["subject_id"])
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh", sa.Text(), nullable=False),
        sa.Column("auth", sa.Text(), nullable=False),
        sa.Column("portal", sa.String(length=24), nullable=False),
        sa.Column("user_agent", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_error", sa.String(length=1000), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("endpoint"),
    )
    op.create_index("ix_push_subscriptions_user_id", "push_subscriptions", ["user_id"])
    op.create_index("ix_push_subscriptions_portal", "push_subscriptions", ["portal"])
    op.create_index("ix_push_subscriptions_is_active", "push_subscriptions", ["is_active"])
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("notice_id", sa.String(length=64), nullable=False),
        sa.Column("subscription_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.String(length=1000), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["notice_id"], ["notices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["push_subscriptions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notice_id", "subscription_id", name="uq_notice_push_subscription"),
    )
    op.create_index("ix_notification_deliveries_notice_id", "notification_deliveries", ["notice_id"])
    op.create_index("ix_notification_deliveries_subscription_id", "notification_deliveries", ["subscription_id"])
    op.create_index("ix_notification_deliveries_user_id", "notification_deliveries", ["user_id"])
    op.create_index("ix_notification_deliveries_status", "notification_deliveries", ["status"])


def downgrade():
    op.drop_table("notification_deliveries")
    op.drop_table("push_subscriptions")
    op.drop_index("ix_notices_subject_id", table_name="notices")
    op.drop_constraint("fk_notices_subject_id", "notices", type_="foreignkey")
    op.drop_column("notices", "subject_id")
