"""operational modules for academics and administration"""
from alembic import op
import sqlalchemy as sa

revision = "f2a7c91d4b63"
down_revision = "e8c4a9b72d10"
branch_labels = None
depends_on = None


def upgrade():
    timestamps = lambda: [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)]
    op.create_table("batches", sa.Column("id", sa.String(64), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("program", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps(), sa.UniqueConstraint("name", "program", name="uq_batch_name_program"))
    op.create_index("ix_batches_name", "batches", ["name"]); op.create_index("ix_batches_program", "batches", ["program"]); op.create_index("ix_batches_is_active", "batches", ["is_active"])
    op.create_table("subjects", sa.Column("id", sa.String(64), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("code", sa.String(24), nullable=False), sa.Column("program", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps())
    op.create_index("ix_subjects_name", "subjects", ["name"]); op.create_index("ix_subjects_code", "subjects", ["code"], unique=True); op.create_index("ix_subjects_program", "subjects", ["program"]); op.create_index("ix_subjects_is_active", "subjects", ["is_active"])
    op.create_table("rooms", sa.Column("id", sa.String(64), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("capacity", sa.Integer(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps())
    op.create_index("ix_rooms_name", "rooms", ["name"], unique=True); op.create_index("ix_rooms_is_active", "rooms", ["is_active"])
    op.create_table("class_sessions", sa.Column("id", sa.String(64), primary_key=True), sa.Column("batch_id", sa.String(64), sa.ForeignKey("batches.id"), nullable=False), sa.Column("subject_id", sa.String(64), sa.ForeignKey("subjects.id"), nullable=False), sa.Column("faculty_id", sa.String(64), sa.ForeignKey("users.id"), nullable=False), sa.Column("room_id", sa.String(64), sa.ForeignKey("rooms.id"), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("notes", sa.Text(), nullable=False), sa.Column("override_reason", sa.Text()), sa.Column("created_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False), *timestamps())
    for column in ("batch_id", "subject_id", "faculty_id", "room_id", "starts_at", "ends_at", "status", "created_by"): op.create_index(f"ix_class_sessions_{column}", "class_sessions", [column])
    op.create_table("attendance_registers", sa.Column("id", sa.String(64), primary_key=True), sa.Column("class_session_id", sa.String(64), sa.ForeignKey("class_sessions.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("submitted_by", sa.String(64), sa.ForeignKey("users.id")), *timestamps())
    op.create_index("ix_attendance_registers_class_session_id", "attendance_registers", ["class_session_id"], unique=True); op.create_index("ix_attendance_registers_status", "attendance_registers", ["status"])
    op.create_table("assignments", sa.Column("id", sa.String(64), primary_key=True), sa.Column("batch_id", sa.String(64), sa.ForeignKey("batches.id"), nullable=False), sa.Column("subject_id", sa.String(64), sa.ForeignKey("subjects.id"), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("instructions", sa.Text(), nullable=False), sa.Column("due_at", sa.DateTime(timezone=True), nullable=False), sa.Column("external_url", sa.String(1000), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("created_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False), *timestamps())
    for column in ("batch_id", "subject_id", "due_at", "status", "created_by"): op.create_index(f"ix_assignments_{column}", "assignments", [column])
    op.create_table("notices", sa.Column("id", sa.String(64), primary_key=True), sa.Column("title", sa.String(255), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("audience", sa.String(32), nullable=False), sa.Column("channel", sa.String(24), nullable=False), sa.Column("batch_id", sa.String(64), sa.ForeignKey("batches.id")), sa.Column("status", sa.String(24), nullable=False), sa.Column("published_at", sa.DateTime(timezone=True)), sa.Column("created_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False), *timestamps())
    for column in ("audience", "channel", "batch_id", "status", "created_by"): op.create_index(f"ix_notices_{column}", "notices", [column])
    op.create_table("attendance_entries", sa.Column("register_id", sa.String(64), sa.ForeignKey("attendance_registers.id", ondelete="CASCADE"), primary_key=True), sa.Column("student_id", sa.String(64), sa.ForeignKey("students.id", ondelete="CASCADE"), primary_key=True), sa.Column("status", sa.String(16), nullable=False), sa.Column("reason", sa.Text(), nullable=False), sa.Column("marked_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_attendance_entries_status", "attendance_entries", ["status"])
    op.create_table("assignment_recipients", sa.Column("assignment_id", sa.String(64), sa.ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True), sa.Column("student_id", sa.String(64), sa.ForeignKey("students.id", ondelete="CASCADE"), primary_key=True), sa.Column("status", sa.String(24), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_assignment_recipients_status", "assignment_recipients", ["status"])


def downgrade():
    op.drop_table("assignment_recipients")
    op.drop_table("attendance_entries")
    op.drop_table("notices")
    op.drop_table("assignments")
    op.drop_table("attendance_registers")
    op.drop_table("class_sessions")
    op.drop_table("rooms")
    op.drop_table("subjects")
    op.drop_table("batches")
