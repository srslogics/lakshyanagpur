from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, LargeBinary, Numeric, String, Text, UniqueConstraint, event, inspect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .database import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("usr"))
    username: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    mobile: Mapped[str | None] = mapped_column(String(10), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(64), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_test_account: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


class UserModulePermission(TimestampMixin, Base):
    __tablename__ = "user_module_permissions"
    __table_args__ = (UniqueConstraint("user_id", "module", name="uq_user_module_permission"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("prm"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    module: Mapped[str] = mapped_column(String(40), index=True)
    can_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_create: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("lead"))
    student: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    program: Mapped[str] = mapped_column(String(255))
    parent: Mapped[str] = mapped_column(String(255))
    parent_mobile: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(64), index=True)
    counsellor: Mapped[str] = mapped_column(String(255), index=True)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    stage: Mapped[str] = mapped_column(String(64), index=True)
    priority: Mapped[str] = mapped_column(String(16), default="medium", index=True)
    next_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    next_action: Mapped[str] = mapped_column(String(255))
    budget: Mapped[str] = mapped_column(String(255), default="To be discussed")
    summary: Mapped[str] = mapped_column(Text, default="")
    document_checklist: Mapped[dict] = mapped_column(JSON, default=dict)
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    converted_student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id"))


class LeadActivity(Base):
    __tablename__ = "lead_activities"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("act"))
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    note: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Student(TimestampMixin, Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("stu"))
    admission_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    mobile: Mapped[str | None] = mapped_column(String(20), index=True)
    secondary_mobile: Mapped[str | None] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    previous_school: Mapped[str | None] = mapped_column(String(255))
    legacy_import_id: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    data_quality_status: Mapped[str] = mapped_column(String(24), default="ready", index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    is_test_account: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


class Guardian(TimestampMixin, Base):
    __tablename__ = "guardians"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("gdn"))
    full_name: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str] = mapped_column(String(20), index=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)


class StudentGuardian(Base):
    __tablename__ = "student_guardians"
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    guardian_id: Mapped[str] = mapped_column(ForeignKey("guardians.id", ondelete="CASCADE"), primary_key=True)
    relationship: Mapped[str] = mapped_column(String(32), default="guardian")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)


class StudentAccount(TimestampMixin, Base):
    __tablename__ = "student_accounts"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True, index=True)


class ParentAccount(TimestampMixin, Base):
    __tablename__ = "parent_accounts"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    contact_type: Mapped[str] = mapped_column(String(24), default="primary_contact", index=True)


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "program", "batch", "is_active", name="uq_active_enrollment"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("enr"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    program: Mapped[str] = mapped_column(String(255), index=True)
    batch: Mapped[str | None] = mapped_column(String(255), index=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date)
    source_type: Mapped[str] = mapped_column(String(32), default="erp")
    legacy_import_id: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class FinanceHandoff(TimestampMixin, Base):
    __tablename__ = "finance_handoffs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("fin"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), unique=True, index=True)
    enrollment_id: Mapped[str] = mapped_column(ForeignKey("enrollments.id"))
    status: Mapped[str] = mapped_column(String(32), default="fee_plan_pending")
    concession_requested: Mapped[bool] = mapped_column(Boolean, default=False)


class ImportBatch(Base):
    __tablename__ = "import_batches"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("imp"))
    source_name: Mapped[str] = mapped_column(String(255))
    source_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_sheet: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="completed")
    active_rows: Mapped[int] = mapped_column(Integer)
    cancelled_rows: Mapped[int] = mapped_column(Integer)
    fee_total: Mapped[int] = mapped_column(Integer)
    registration_total: Mapped[int] = mapped_column(Integer)
    staged_payment_total: Mapped[int] = mapped_column(Integer)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class LegacyAdmissionRow(Base):
    __tablename__ = "legacy_admission_rows"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    import_batch_id: Mapped[str] = mapped_column(ForeignKey("import_batches.id"), index=True)
    source_row: Mapped[int] = mapped_column(Integer)
    record_status: Mapped[str] = mapped_column(String(24), index=True)
    import_readiness: Mapped[str] = mapped_column(String(24), index=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
    normalized_data: Mapped[dict] = mapped_column(JSON)
    issues: Mapped[list] = mapped_column(JSON, default=list)
    student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class AcademicImportBatch(Base):
    __tablename__ = "academic_import_batches"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("aimp"))
    source_name: Mapped[str] = mapped_column(String(255))
    source_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="completed", index=True)
    active_student_rows: Mapped[int] = mapped_column(Integer)
    attendance_entries: Mapped[int] = mapped_column(Integer)
    subject_selections: Mapped[int] = mapped_column(Integer)
    staged_source_rows: Mapped[int] = mapped_column(Integer)
    unresolved_items: Mapped[int] = mapped_column(Integer, default=0)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class AcademicSourceRecord(Base):
    """Immutable row-level evidence from every workbook sheet."""

    __tablename__ = "academic_source_records"
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    import_batch_id: Mapped[str] = mapped_column(
        ForeignKey("academic_import_batches.id", ondelete="CASCADE"),
        index=True,
    )
    source_sheet: Mapped[str] = mapped_column(String(255), index=True)
    source_row: Mapped[int] = mapped_column(Integer)
    record_type: Mapped[str] = mapped_column(String(40), index=True)
    source_key: Mapped[str | None] = mapped_column(String(120), index=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
    normalized_data: Mapped[dict] = mapped_column(JSON)
    issues: Mapped[list] = mapped_column(JSON, default=list)
    student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class StudentAcademicProfile(TimestampMixin, Base):
    __tablename__ = "student_academic_profiles"
    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_student_code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    batch_name: Mapped[str] = mapped_column(String(120), index=True)
    source_stream: Mapped[str | None] = mapped_column(String(120), index=True)
    mentor_name: Mapped[str | None] = mapped_column(String(255), index=True)
    source_school_name: Mapped[str | None] = mapped_column(String(255))
    source_primary_mobile: Mapped[str | None] = mapped_column(String(20))
    source_secondary_mobile: Mapped[str | None] = mapped_column(String(20))
    import_batch_id: Mapped[str | None] = mapped_column(ForeignKey("academic_import_batches.id"), index=True)


class StudentSubjectSelection(Base):
    __tablename__ = "student_subject_selections"
    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    subject_name: Mapped[str] = mapped_column(String(120), primary_key=True)
    source_value: Mapped[str] = mapped_column(String(120))
    import_batch_id: Mapped[str | None] = mapped_column(ForeignKey("academic_import_batches.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class DailyAttendanceEntry(Base):
    __tablename__ = "daily_attendance_entries"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "source_sheet",
            "source_date_label",
            name="uq_daily_attendance_source_day",
        ),
    )
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("dae"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    import_batch_id: Mapped[str] = mapped_column(ForeignKey("academic_import_batches.id"), index=True)
    source_student_code: Mapped[str] = mapped_column(String(24), index=True)
    batch_name: Mapped[str] = mapped_column(String(120), index=True)
    source_sheet: Mapped[str] = mapped_column(String(255), index=True)
    source_row: Mapped[int] = mapped_column(Integer)
    source_column: Mapped[int] = mapped_column(Integer)
    source_date_label: Mapped[str] = mapped_column(String(40), index=True)
    attendance_date: Mapped[date | None] = mapped_column(Date, index=True)
    raw_status: Mapped[str] = mapped_column(String(16), index=True)
    normalized_status: Mapped[str | None] = mapped_column(String(24), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class AttendancePeriodSummary(TimestampMixin, Base):
    """Client-confirmed aggregate attendance when daily marks are unavailable."""

    __tablename__ = "attendance_period_summaries"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "period_start",
            "period_end",
            name="uq_attendance_period_student",
        ),
    )
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("aps"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    source_student_code: Mapped[str] = mapped_column(String(24), index=True)
    batch_name: Mapped[str] = mapped_column(String(120), index=True)
    mentor_name: Mapped[str | None] = mapped_column(String(255), index=True)
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date] = mapped_column(Date, index=True)
    present_days: Mapped[int] = mapped_column(Integer)
    absent_days: Mapped[int] = mapped_column(Integer)
    working_days: Mapped[int] = mapped_column(Integer)
    attendance_rate: Mapped[float] = mapped_column(Numeric(5, 2))
    source_name: Mapped[str] = mapped_column(String(255))
    source_reference: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(24), default="confirmed", index=True)


class FeeAgreement(TimestampMixin, Base):
    __tablename__ = "fee_agreements"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("fee"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    enrollment_id: Mapped[str] = mapped_column(ForeignKey("enrollments.id"), unique=True)
    legacy_import_id: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    agreed_amount: Mapped[int] = mapped_column(Integer)
    legacy_registration_total: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(32), default="active")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (UniqueConstraint("legacy_import_id", "legacy_line_number", name="uq_legacy_payment_line"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("pay"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    fee_agreement_id: Mapped[str] = mapped_column(ForeignKey("fee_agreements.id"), index=True)
    legacy_import_id: Mapped[str | None] = mapped_column(String(80), index=True)
    legacy_line_number: Mapped[int | None] = mapped_column(Integer)
    receipt_number: Mapped[str | None] = mapped_column(String(48), unique=True, index=True)
    transaction_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[int] = mapped_column(Integer)
    method: Mapped[str] = mapped_column(String(24))
    transaction_type: Mapped[str] = mapped_column(String(32), default="payment")
    source_note: Mapped[str] = mapped_column(Text)
    reference: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(Text, default="")
    related_transaction_id: Mapped[str | None] = mapped_column(
        ForeignKey("payment_transactions.id"),
        index=True,
    )
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="staged", index=True)
    reconciliation_status: Mapped[str] = mapped_column(String(32), default="review", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class FeeInstallment(TimestampMixin, Base):
    __tablename__ = "fee_installments"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("ins"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    fee_agreement_id: Mapped[str] = mapped_column(ForeignKey("fee_agreements.id"), index=True)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    expected_method: Mapped[str] = mapped_column(String(24), default="not_decided")
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="scheduled", index=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


@event.listens_for(PaymentTransaction, "before_update")
def payment_transaction_updates_are_restricted(mapper, connection, target):
    changed = {attribute.key for attribute in inspect(target).attrs if attribute.history.has_changes()}
    if changed <= {"reconciliation_status"}:
        return
    if target.status == "staged" and changed <= {
        "reconciliation_status",
        "transaction_date",
        "method",
        "reference",
        "notes",
    }:
        return
    raise ValueError("Payment transactions are immutable; create a reversal or adjustment instead")


@event.listens_for(PaymentTransaction, "before_delete")
def payment_transactions_cannot_be_deleted(mapper, connection, target):
    raise ValueError("Payment transactions are immutable; create a reversal or adjustment instead")


class Batch(TimestampMixin, Base):
    __tablename__ = "batches"
    __table_args__ = (UniqueConstraint("name", "program", name="uq_batch_name_program"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("bat"))
    name: Mapped[str] = mapped_column(String(120), index=True)
    program: Mapped[str] = mapped_column(String(255), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class Subject(TimestampMixin, Base):
    __tablename__ = "subjects"
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("sub"))
    name: Mapped[str] = mapped_column(String(120), index=True)
    program: Mapped[str] = mapped_column(String(255), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class Room(TimestampMixin, Base):
    __tablename__ = "rooms"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("rom"))
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    capacity: Mapped[int] = mapped_column(Integer, default=40)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class FacultyTeachingAssignment(TimestampMixin, Base):
    __tablename__ = "faculty_teaching_assignments"
    __table_args__ = (
        UniqueConstraint(
            "faculty_id",
            "batch_id",
            "subject_id",
            name="uq_faculty_teaching_assignment",
        ),
    )
    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: new_id("fta"),
    )
    faculty_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)


class InventoryItem(TimestampMixin, Base):
    __tablename__ = "inventory_items"
    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: new_id("inv"),
    )
    sku: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    unit: Mapped[str] = mapped_column(String(40), default="piece")
    quantity_on_hand: Mapped[int | None] = mapped_column(Integer)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    vendor_reference: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(Text, default="")
    source_note: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: new_id("mov"),
    )
    item_id: Mapped[str] = mapped_column(
        ForeignKey("inventory_items.id"),
        index=True,
    )
    movement_type: Mapped[str] = mapped_column(String(24), index=True)
    quantity_delta: Mapped[int] = mapped_column(Integer)
    balance_after: Mapped[int] = mapped_column(Integer)
    occurred_on: Mapped[date] = mapped_column(Date, index=True)
    target_type: Mapped[str | None] = mapped_column(String(24), index=True)
    target_reference: Mapped[str | None] = mapped_column(String(255))
    student_id: Mapped[str | None] = mapped_column(
        ForeignKey("students.id"),
        index=True,
    )
    reference: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now,
        nullable=False,
    )


class ClassSession(TimestampMixin, Base):
    __tablename__ = "class_sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("ses"))
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    faculty_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(24), default="scheduled", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    override_reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)


class AttendanceRegister(TimestampMixin, Base):
    __tablename__ = "attendance_registers"
    __table_args__ = (
        UniqueConstraint(
            "attendance_date",
            "batch_name",
            "stream_name",
            "subject_name",
            name="uq_attendance_register_manual_scope",
        ),
    )
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("reg"))
    class_session_id: Mapped[str | None] = mapped_column(ForeignKey("class_sessions.id", ondelete="CASCADE"), unique=True, index=True)
    register_kind: Mapped[str] = mapped_column(String(24), default="scheduled", index=True)
    attendance_date: Mapped[date | None] = mapped_column(Date, index=True)
    batch_name: Mapped[str | None] = mapped_column(String(120), index=True)
    stream_name: Mapped[str | None] = mapped_column(String(120), index=True)
    subject_name: Mapped[str | None] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))


class AttendanceEntry(Base):
    __tablename__ = "attendance_entries"
    register_id: Mapped[str] = mapped_column(ForeignKey("attendance_registers.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String(16), default="present", index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    marked_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class DeviceAttendanceIdentity(TimestampMixin, Base):
    """Persisted mapping between a biometric enrolment ID and one person."""

    __tablename__ = "device_attendance_identities"
    __table_args__ = (
        UniqueConstraint("device_key", "device_user_id", name="uq_device_attendance_user"),
        UniqueConstraint("device_key", "staff_user_id", name="uq_device_attendance_staff"),
    )
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("dai"))
    device_key: Mapped[str] = mapped_column(String(120), index=True)
    device_user_id: Mapped[str] = mapped_column(String(120), index=True)
    device_name: Mapped[str | None] = mapped_column(String(255))
    student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    staff_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    is_staff_device: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ignored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class BiometricImportBatch(Base):
    """Audit metadata only; uploaded biometric files are never retained."""

    __tablename__ = "biometric_import_batches"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("bio"))
    device_key: Mapped[str] = mapped_column(String(120), index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_sheet: Mapped[str | None] = mapped_column(String(255))
    rows_seen: Mapped[int] = mapped_column(Integer)
    attendance_days: Mapped[int] = mapped_column(Integer)
    matched_students: Mapped[int] = mapped_column(Integer)
    ignored_device_ids: Mapped[int] = mapped_column(Integer)
    duplicate_rows: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="completed", index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class BiometricAttendanceDay(Base):
    """Storage-efficient first and last punches retained for each person and day."""

    __tablename__ = "biometric_attendance_days"
    __table_args__ = (
        UniqueConstraint(
            "device_key",
            "device_user_id",
            "attendance_date",
            name="uq_biometric_device_user_day",
        ),
    )
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("bad"))
    import_batch_id: Mapped[str] = mapped_column(ForeignKey("biometric_import_batches.id"), index=True)
    device_key: Mapped[str] = mapped_column(String(120), index=True)
    device_user_id: Mapped[str] = mapped_column(String(120), index=True)
    student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id", ondelete="SET NULL"), index=True)
    staff_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    attendance_date: Mapped[date] = mapped_column(Date, index=True)
    first_punch_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_punch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class StaffAttendanceWorkday(Base):
    """Auditable daily staff status and worked time from monthly biometric reports."""

    __tablename__ = "staff_attendance_workdays"
    __table_args__ = (
        UniqueConstraint(
            "device_key",
            "device_user_id",
            "attendance_date",
            name="uq_staff_attendance_workday",
        ),
    )
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("saw"))
    import_batch_id: Mapped[str] = mapped_column(ForeignKey("biometric_import_batches.id"), index=True)
    device_key: Mapped[str] = mapped_column(String(120), index=True)
    device_user_id: Mapped[str] = mapped_column(String(120), index=True)
    staff_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    attendance_date: Mapped[date] = mapped_column(Date, index=True)
    attendance_status: Mapped[str] = mapped_column(String(32), index=True)
    first_punch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_punch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    work_duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    overtime_minutes: Mapped[int] = mapped_column(Integer, default=0)
    punch_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class StaffPayroll(TimestampMixin, Base):
    """One monthly calculation per biometric staff identity; never a bank payment."""

    __tablename__ = "staff_payroll"
    __table_args__ = (UniqueConstraint("person_key", "month", name="uq_staff_payroll_month"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("pay"))
    person_key: Mapped[str] = mapped_column(String(150), index=True)
    month: Mapped[str] = mapped_column(String(7), index=True)
    monthly_salary: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    advance_given: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    absent_days: Mapped[Decimal] = mapped_column(Numeric(5, 1))
    attendance_fingerprint: Mapped[str] = mapped_column(String(64))
    notes: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_by: Mapped[str] = mapped_column(ForeignKey("users.id"))


class Assignment(TimestampMixin, Base):
    __tablename__ = "assignments"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("asg"))
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    instructions: Mapped[str] = mapped_column(Text, default="")
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    external_url: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(24), default="published", index=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class AssignmentRecipient(Base):
    """Sparse student progress; no row means the batch assignment is still open."""

    __tablename__ = "assignment_recipients"
    assignment_id: Mapped[str] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String(24), default="completed", index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class AssignmentMaterial(Base):
    """Short-lived PDF attached to an assignment.

    The binary is deliberately isolated from the assignment row so normal
    portal bootstrap queries never load document bytes into memory.
    """

    __tablename__ = "assignment_materials"
    assignment_id: Mapped[str] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf")
    size_bytes: Mapped[int] = mapped_column(Integer)
    # Portal bootstrap queries need only metadata. Defer the PDF bytes until a
    # user explicitly downloads the document so normal app loading stays fast.
    content: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class AssignmentDownload(Base):
    """One compact row per student and assignment, regardless of retries."""

    __tablename__ = "assignment_downloads"
    assignment_id: Mapped[str] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    first_downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    last_downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Examination(TimestampMixin, Base):
    __tablename__ = "examinations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("exm"))
    name: Mapped[str] = mapped_column(String(255), index=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    faculty_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    max_marks: Mapped[float] = mapped_column(Numeric(8, 2))
    pass_marks: Mapped[float] = mapped_column(Numeric(8, 2))
    instructions: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class ExaminationParticipant(Base):
    """Immutable eligibility snapshot captured when an examination is created."""

    __tablename__ = "examination_participants"
    exam_id: Mapped[str] = mapped_column(
        ForeignKey("examinations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        primary_key=True,
        index=True,
    )
    admission_number: Mapped[str] = mapped_column(String(32))
    full_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now,
        nullable=False,
    )


class ExaminationResult(Base):
    """Sparse result storage; no row means marks have not been entered."""

    __tablename__ = "examination_results"
    exam_id: Mapped[str] = mapped_column(
        ForeignKey("examinations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    marks_obtained: Mapped[float | None] = mapped_column(Numeric(8, 2))
    result_status: Mapped[str] = mapped_column(String(24), default="graded", index=True)
    remarks: Mapped[str] = mapped_column(String(500), default="")
    entered_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now,
        onupdate=now,
        nullable=False,
    )


class Notice(TimestampMixin, Base):
    __tablename__ = "notices"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("not"))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    audience: Mapped[str] = mapped_column(String(32), index=True)
    channel: Mapped[str] = mapped_column(String(24), default="in_app", index=True)
    batch_id: Mapped[str | None] = mapped_column(ForeignKey("batches.id"), index=True)
    subject_id: Mapped[str | None] = mapped_column(ForeignKey("subjects.id"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="published", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class PushSubscription(TimestampMixin, Base):
    __tablename__ = "push_subscriptions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("push"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    endpoint: Mapped[str] = mapped_column(Text, unique=True)
    p256dh: Mapped[str] = mapped_column(Text)
    auth: Mapped[str] = mapped_column(Text)
    portal: Mapped[str] = mapped_column(String(24), index=True)
    user_agent: Mapped[str] = mapped_column(String(500), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_error: Mapped[str] = mapped_column(String(1000), default="")
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class NotificationDelivery(TimestampMixin, Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (UniqueConstraint("notice_id", "subscription_id", name="uq_notice_push_subscription"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("delivery"))
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id", ondelete="CASCADE"), index=True)
    subscription_id: Mapped[str] = mapped_column(ForeignKey("push_subscriptions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False, index=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str] = mapped_column(String(1000), default="")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CommunicationThread(TimestampMixin, Base):
    """A student-linked conversation with Operations or assigned faculty."""

    __tablename__ = "communication_threads"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("thread"))
    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        index=True,
    )
    subject_id: Mapped[str | None] = mapped_column(ForeignKey("subjects.id"), index=True)
    topic: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(24), default="open", index=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class CommunicationMessage(Base):
    """Text-only message storage keeps portal communication auditable and compact."""

    __tablename__ = "communication_messages"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("msg"))
    thread_id: Mapped[str] = mapped_column(
        ForeignKey("communication_threads.id", ondelete="CASCADE"),
        index=True,
    )
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now,
        nullable=False,
        index=True,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("aud"))
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    request_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
