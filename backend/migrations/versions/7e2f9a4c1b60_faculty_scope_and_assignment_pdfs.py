"""align faculty scope and add short-lived assignment PDFs

Revision ID: 7e2f9a4c1b60
Revises: 6b9d2e7f4a10
"""

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "7e2f9a4c1b60"
down_revision = "6b9d2e7f4a10"
branch_labels = None
depends_on = None


# Client-confirmed allocation supplied on 23 August 2026. ``All programs`` is
# the timetable's aggregate representation of the listed JEE/NEET/MHT-CET
# scopes; it is allowed only for the corresponding Tatva/Essential batch.
FACULTY_SCOPE = (
    ("Meet Sir", "9325511100", "PHY", {("Tatva", "JEE"), ("Tatva", "NEET"), ("Tatva", "All programs")}),
    ("Kajal Ma'am", "9156376488", "PHY", {("Essential", "MHT-CET"), ("Essential", "All programs")}),
    ("Jitendra Sir", "9850242456", "CHEM", {("Tatva", "JEE"), ("Tatva", "NEET"), ("Tatva", "All programs"), ("Essential", "MHT-CET"), ("Essential", "All programs")}),
    ("Anita Ma'am", "9923057717", "MATH", {("Tatva", "JEE"), ("Tatva", "All programs"), ("Essential", "MHT-CET"), ("Essential", "All programs")}),
    ("Kanchan Ma'am", "9049834525", "BIO", {("Tatva", "NEET"), ("Tatva", "All programs"), ("Essential", "MHT-CET"), ("Essential", "All programs")}),
)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def upgrade():
    op.create_table(
        "assignment_materials",
        sa.Column("assignment_id", sa.String(length=64), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("assignment_id"),
    )
    op.create_index(
        "ix_assignment_materials_expires_at",
        "assignment_materials",
        ["expires_at"],
    )
    op.create_table(
        "assignment_downloads",
        sa.Column("assignment_id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("first_downloaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("download_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("assignment_id", "student_id"),
    )

    connection = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id", sa.String(length=64)),
        sa.column("full_name", sa.String(length=255)),
        sa.column("mobile", sa.String(length=10)),
        sa.column("role", sa.String(length=64)),
    )
    batches = sa.table(
        "batches",
        sa.column("id", sa.String(length=64)),
        sa.column("name", sa.String(length=120)),
        sa.column("program", sa.String(length=255)),
    )
    subjects = sa.table(
        "subjects",
        sa.column("id", sa.String(length=64)),
        sa.column("code", sa.String(length=24)),
    )
    teaching = sa.table(
        "faculty_teaching_assignments",
        sa.column("id", sa.String(length=64)),
        sa.column("faculty_id", sa.String(length=64)),
        sa.column("batch_id", sa.String(length=64)),
        sa.column("subject_id", sa.String(length=64)),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_by", sa.String(length=64)),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    sessions = sa.table(
        "class_sessions",
        sa.column("faculty_id", sa.String(length=64)),
        sa.column("batch_id", sa.String(length=64)),
        sa.column("subject_id", sa.String(length=64)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    now = datetime.now(timezone.utc)
    batch_rows = {
        (name, program): batch_id
        for batch_id, name, program in connection.execute(
            sa.select(batches.c.id, batches.c.name, batches.c.program)
        )
    }
    subject_rows = {
        code: subject_id
        for subject_id, code in connection.execute(
            sa.select(subjects.c.id, subjects.c.code)
        )
    }

    for faculty_name, mobile, subject_code, allowed_scopes in FACULTY_SCOPE:
        faculty_id = connection.execute(
            sa.select(users.c.id).where(
                users.c.role == "faculty",
                sa.or_(users.c.mobile == mobile, users.c.full_name == faculty_name),
            ).limit(1)
        ).scalar_one_or_none()
        subject_id = subject_rows.get(subject_code)
        if not faculty_id or not subject_id:
            continue

        existing_rows = list(connection.execute(
            sa.select(
                teaching.c.id,
                teaching.c.batch_id,
                teaching.c.subject_id,
            ).where(teaching.c.faculty_id == faculty_id)
        ))
        allowed_keys = {
            (batch_rows[scope], subject_id)
            for scope in allowed_scopes
            if scope in batch_rows
        }
        for teaching_id, batch_id, assigned_subject_id in existing_rows:
            connection.execute(
                teaching.update()
                .where(teaching.c.id == teaching_id)
                .values(
                    is_active=(batch_id, assigned_subject_id) in allowed_keys,
                    updated_at=now,
                )
            )

        existing_keys = {
            (batch_id, assigned_subject_id): teaching_id
            for teaching_id, batch_id, assigned_subject_id in existing_rows
        }
        for batch_id, allowed_subject_id in allowed_keys:
            existing_id = existing_keys.get((batch_id, allowed_subject_id))
            if existing_id:
                connection.execute(
                    teaching.update()
                    .where(teaching.c.id == existing_id)
                    .values(is_active=True, updated_at=now)
                )
            else:
                connection.execute(teaching.insert().values(
                    id=_new_id("fta"),
                    faculty_id=faculty_id,
                    batch_id=batch_id,
                    subject_id=allowed_subject_id,
                    is_active=True,
                    created_by=None,
                    created_at=now,
                    updated_at=now,
                ))

        allowed_batch_ids = [
            batch_rows[scope]
            for scope in allowed_scopes
            if scope in batch_rows
        ]
        if allowed_batch_ids:
            # Correct stale timetable ownership (most importantly the old
            # placeholder "Kumar Sir" chemistry rows) to the confirmed faculty.
            connection.execute(
                sessions.update()
                .where(
                    sessions.c.subject_id == subject_id,
                    sessions.c.batch_id.in_(allowed_batch_ids),
                )
                .values(faculty_id=faculty_id, updated_at=now)
            )


def downgrade():
    op.drop_table("assignment_downloads")
    op.drop_index("ix_assignment_materials_expires_at", table_name="assignment_materials")
    op.drop_table("assignment_materials")
