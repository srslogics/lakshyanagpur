"""snapshot examination rosters and add immutable stock movements

Revision ID: c15d8a42f901
Revises: b91c4a72e608
"""

from alembic import op
import sqlalchemy as sa


revision = "c15d8a42f901"
down_revision = "b91c4a72e608"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("inventory_items") as batch:
        batch.add_column(
            sa.Column(
                "reorder_level",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch.add_column(
            sa.Column("vendor_reference", sa.String(length=255), nullable=True)
        )
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("item_id", sa.String(length=64), nullable=False),
        sa.Column("movement_type", sa.String(length=24), nullable=False),
        sa.Column("quantity_delta", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("target_type", sa.String(length=24), nullable=True),
        sa.Column("target_reference", sa.String(length=255), nullable=True),
        sa.Column("student_id", sa.String(length=64), nullable=True),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["item_id"], ["inventory_items.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_inventory_movements_item_id",
        "inventory_movements",
        ["item_id"],
    )
    op.create_index(
        "ix_inventory_movements_movement_type",
        "inventory_movements",
        ["movement_type"],
    )
    op.create_index(
        "ix_inventory_movements_occurred_on",
        "inventory_movements",
        ["occurred_on"],
    )
    op.create_index(
        "ix_inventory_movements_target_type",
        "inventory_movements",
        ["target_type"],
    )
    op.create_index(
        "ix_inventory_movements_student_id",
        "inventory_movements",
        ["student_id"],
    )
    op.create_index(
        "ix_inventory_movements_created_by",
        "inventory_movements",
        ["created_by"],
    )
    op.create_table(
        "examination_participants",
        sa.Column("exam_id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("admission_number", sa.String(length=32), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["exam_id"],
            ["examinations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("exam_id", "student_id"),
    )
    op.create_index(
        "ix_examination_participants_student_id",
        "examination_participants",
        ["student_id"],
    )
    op.execute(
        sa.text(
            """
            INSERT INTO examination_participants
                (exam_id, student_id, admission_number, full_name, created_at)
            SELECT DISTINCT
                examinations.id,
                students.id,
                students.admission_number,
                students.full_name,
                CURRENT_TIMESTAMP
            FROM examinations
            JOIN batches ON batches.id = examinations.batch_id
            JOIN enrollments
              ON enrollments.batch = batches.name
             AND enrollments.program = batches.program
             AND enrollments.is_active = true
            JOIN students ON students.id = enrollments.student_id
            WHERE students.status = 'active'
            """
        )
    )


def downgrade():
    op.drop_index(
        "ix_examination_participants_student_id",
        table_name="examination_participants",
    )
    op.drop_table("examination_participants")
    op.drop_index(
        "ix_inventory_movements_created_by",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_student_id",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_target_type",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_occurred_on",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_movement_type",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_item_id",
        table_name="inventory_movements",
    )
    op.drop_table("inventory_movements")
    with op.batch_alter_table("inventory_items") as batch:
        batch.drop_column("vendor_reference")
        batch.drop_column("reorder_level")
