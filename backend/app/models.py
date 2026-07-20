from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, event
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
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(64), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


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


class FeeAgreement(TimestampMixin, Base):
    __tablename__ = "fee_agreements"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("fee"))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    enrollment_id: Mapped[str] = mapped_column(ForeignKey("enrollments.id"), unique=True)
    legacy_import_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
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
    legacy_import_id: Mapped[str] = mapped_column(String(80), index=True)
    legacy_line_number: Mapped[int] = mapped_column(Integer)
    transaction_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[int] = mapped_column(Integer)
    method: Mapped[str] = mapped_column(String(24))
    transaction_type: Mapped[str] = mapped_column(String(32), default="payment")
    source_note: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="staged", index=True)
    reconciliation_status: Mapped[str] = mapped_column(String(32), default="review", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


@event.listens_for(PaymentTransaction, "before_update")
@event.listens_for(PaymentTransaction, "before_delete")
def payment_transactions_are_immutable(mapper, connection, target):
    raise ValueError("Payment transactions are immutable; create a reversal or adjustment instead")


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
