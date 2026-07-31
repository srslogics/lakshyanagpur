"""archive production test accounts and complete faculty mobile identities

Revision ID: d31f7a9c2e10
Revises: c15d8a42f901
"""

from alembic import op
import sqlalchemy as sa


revision = "d31f7a9c2e10"
down_revision = "c15d8a42f901"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column(
                "is_test_account",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch.create_index("ix_users_is_test_account", ["is_test_account"])
    with op.batch_alter_table("students") as batch:
        batch.add_column(
            sa.Column(
                "is_test_account",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch.create_index("ix_students_is_test_account", ["is_test_account"])

    op.execute(
        sa.text(
            """
            UPDATE users
               SET is_test_account = true,
                   is_active = false,
                   token_version = token_version + 1
             WHERE mobile IN ('9000000101', '9000000102', '9000000103', '9000000104')
                OR full_name IN (
                    'Lakshya Student Test',
                    'Lakshya Parent Test',
                    'Lakshya Faculty Test',
                    'Lakshya Attendance Test'
                )
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE students
               SET is_test_account = true,
                   status = 'inactive'
             WHERE admission_number = 'LI-TEST-00001'
                OR legacy_import_id = 'system-portal-test-student'
            """
        )
    )

    faculty_mobiles = {
        "Meet Sir": "9325511100",
        "Meet Kakwani Sir": "9325511100",
        "Kanchan Ma'am": "9049834525",
        "Kanchan Maam": "9049834525",
        "Anita Ma'am": "9923057717",
        "Anita Bamratwar": "9923057717",
        "Jitendra Sir": "9850242456",
        "Kajal Ma'am": "9156376488",
        "Kajal Dodeja": "9156376488",
    }
    for full_name, mobile in faculty_mobiles.items():
        op.execute(
            sa.text(
                """
                UPDATE users
                   SET mobile = :mobile
                 WHERE role = 'faculty'
                   AND full_name = :full_name
                   AND mobile IS NULL
                   AND NOT EXISTS (
                       SELECT 1 FROM users AS existing
                        WHERE existing.mobile = :mobile
                   )
                """
            ).bindparams(full_name=full_name, mobile=mobile)
        )


def downgrade():
    with op.batch_alter_table("students") as batch:
        batch.drop_index("ix_students_is_test_account")
        batch.drop_column("is_test_account")
    with op.batch_alter_table("users") as batch:
        batch.drop_index("ix_users_is_test_account")
        batch.drop_column("is_test_account")
