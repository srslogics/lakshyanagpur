"""manual attendance registers from academic student groups"""

from alembic import op
import sqlalchemy as sa


revision = "f7b31d9a2c40"
down_revision = "d52f18a47b90"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("attendance_registers") as batch_op:
        batch_op.alter_column(
            "class_session_id",
            existing_type=sa.String(length=64),
            nullable=True,
        )
        batch_op.add_column(
            sa.Column(
                "register_kind",
                sa.String(length=24),
                nullable=False,
                server_default="scheduled",
            ),
        )
        batch_op.add_column(
            sa.Column("attendance_date", sa.Date(), nullable=True),
        )
        batch_op.add_column(
            sa.Column("batch_name", sa.String(length=120), nullable=True),
        )
        batch_op.add_column(
            sa.Column("stream_name", sa.String(length=120), nullable=True),
        )
        batch_op.add_column(
            sa.Column("subject_name", sa.String(length=120), nullable=True),
        )
        for column in (
            "register_kind",
            "attendance_date",
            "batch_name",
            "stream_name",
            "subject_name",
        ):
            batch_op.create_index(
                f"ix_attendance_registers_{column}",
                [column],
                unique=False,
            )
        batch_op.create_unique_constraint(
            "uq_attendance_register_manual_scope",
            ["attendance_date", "batch_name", "stream_name", "subject_name"],
        )


def downgrade():
    with op.batch_alter_table("attendance_registers") as batch_op:
        batch_op.drop_constraint(
            "uq_attendance_register_manual_scope",
            type_="unique",
        )
        for column in (
            "subject_name",
            "stream_name",
            "batch_name",
            "attendance_date",
            "register_kind",
        ):
            batch_op.drop_index(f"ix_attendance_registers_{column}")
            batch_op.drop_column(column)
        batch_op.alter_column(
            "class_session_id",
            existing_type=sa.String(length=64),
            nullable=False,
        )
