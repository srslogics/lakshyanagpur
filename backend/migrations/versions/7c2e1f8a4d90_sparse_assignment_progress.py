"""store assignment progress only when a student completes work"""

from alembic import op


revision = "7c2e1f8a4d90"
down_revision = "c3f6a1b9d420"
branch_labels = None
depends_on = None


def upgrade():
    # Published and draft rows only repeated batch membership. Visibility is now
    # resolved from active enrolments, while completed progress remains stored.
    op.execute(
        """
        DELETE FROM assignment_recipients
        WHERE status IN ('draft', 'published')
        """
    )


def downgrade():
    # Recreate the former recipient snapshot from current active enrolments.
    op.execute(
        """
        INSERT INTO assignment_recipients (
            assignment_id,
            student_id,
            status,
            updated_at
        )
        SELECT
            assignments.id,
            enrollments.student_id,
            assignments.status,
            CURRENT_TIMESTAMP
        FROM assignments
        JOIN batches
          ON batches.id = assignments.batch_id
        JOIN enrollments
          ON enrollments.batch = batches.name
         AND enrollments.program = batches.program
         AND enrollments.is_active = TRUE
        WHERE assignments.status IN ('draft', 'published')
          AND NOT EXISTS (
              SELECT 1
              FROM assignment_recipients
              WHERE assignment_recipients.assignment_id = assignments.id
                AND assignment_recipients.student_id = enrollments.student_id
          )
        """
    )
