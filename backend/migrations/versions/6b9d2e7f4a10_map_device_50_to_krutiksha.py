"""map device 50 to Krutiksha Ukey

Revision ID: 6b9d2e7f4a10
Revises: 4f8c2a1d9e70
"""

from alembic import op
import sqlalchemy as sa


revision = "6b9d2e7f4a10"
down_revision = "4f8c2a1d9e70"
branch_labels = None
depends_on = None


DEVICE_KEY = "x2008-abfr220607313"


def upgrade():
    # A person can be re-enrolled on the biometric device under a new code.
    # Keep both codes mapped to the same student and merge them by student/day
    # when the attendance register is built.
    op.drop_constraint(
        "uq_device_attendance_student",
        "device_attendance_identities",
        type_="unique",
    )

    connection = op.get_bind()
    krutiksha_id = connection.execute(sa.text("""
        SELECT id
        FROM students
        WHERE lower(trim(full_name)) = lower(:full_name)
        ORDER BY created_at DESC
        LIMIT 1
    """), {"full_name": "Krutiksha Ukey"}).scalar_one_or_none()
    if not krutiksha_id:
        return

    connection.execute(sa.text("""
        UPDATE device_attendance_identities
        SET student_id = :student_id,
            staff_user_id = NULL,
            is_staff_device = :is_staff_device,
            is_ignored = :is_ignored,
            updated_at = CURRENT_TIMESTAMP
        WHERE device_key = :device_key
          AND device_user_id = :device_user_id
    """), {
        "student_id": krutiksha_id,
        "is_staff_device": False,
        "is_ignored": False,
        "device_key": DEVICE_KEY,
        "device_user_id": "50",
    })
    connection.execute(sa.text("""
        UPDATE biometric_attendance_days
        SET student_id = :student_id,
            staff_user_id = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE device_key = :device_key
          AND device_user_id = :device_user_id
    """), {
        "student_id": krutiksha_id,
        "device_key": DEVICE_KEY,
        "device_user_id": "50",
    })


def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE device_attendance_identities
        SET student_id = NULL,
            staff_user_id = NULL,
            is_staff_device = :is_staff_device,
            is_ignored = :is_ignored,
            updated_at = CURRENT_TIMESTAMP
        WHERE device_key = :device_key
          AND device_user_id = :device_user_id
    """), {
        "is_staff_device": True,
        "is_ignored": False,
        "device_key": DEVICE_KEY,
        "device_user_id": "50",
    })
    connection.execute(sa.text("""
        UPDATE biometric_attendance_days
        SET student_id = NULL,
            staff_user_id = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE device_key = :device_key
          AND device_user_id = :device_user_id
    """), {"device_key": DEVICE_KEY, "device_user_id": "50"})
    op.create_unique_constraint(
        "uq_device_attendance_student",
        "device_attendance_identities",
        ["device_key", "student_id"],
    )
