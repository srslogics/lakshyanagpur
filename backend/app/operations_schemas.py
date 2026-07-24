from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator


class BatchCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    program: str = Field(min_length=2, max_length=255)


class SubjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str = Field(min_length=2, max_length=24)
    program: str = Field(min_length=2, max_length=255)


class RoomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    capacity: int = Field(default=40, ge=1, le=500)


class StudentUpdate(BaseModel):
    admission_number: str = Field(alias="admissionNumber", min_length=3, max_length=32)
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    mobile: str | None = Field(default=None, max_length=20)
    secondary_mobile: str | None = Field(default=None, alias="secondaryMobile", max_length=20)
    email: EmailStr | None = None
    previous_school: str | None = Field(default=None, alias="previousSchool", max_length=255)
    status: Literal["active", "draft", "inactive", "forfeited"]
    data_quality_status: Literal["ready", "review", "blocked"] = Field(alias="dataQualityStatus")
    program: str | None = Field(default=None, max_length=255)
    batch: str | None = Field(default=None, max_length=255)
    enrollment_date: date | None = Field(default=None, alias="enrollmentDate")
    model_config = ConfigDict(populate_by_name=True)


class FeeAgreementUpdate(BaseModel):
    agreed_amount: int = Field(alias="agreedAmount", ge=0)
    legacy_registration_total: int = Field(alias="legacyRegistrationTotal", ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    status: Literal["active", "draft", "inactive", "completed"] = "active"
    model_config = ConfigDict(populate_by_name=True)


class PaymentReviewUpdate(BaseModel):
    reconciliation_status: Literal["ready", "review", "do_not_import"] = Field(alias="reconciliationStatus")
    model_config = ConfigDict(populate_by_name=True)


class UserCreate(BaseModel):
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    role: Literal["admissions_manager", "counsellor", "front_desk", "accounts", "academic_coordinator", "faculty", "storekeeper", "student", "parent", "parent_student"]
    model_config = ConfigDict(populate_by_name=True)


class UserUpdate(BaseModel):
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    email: EmailStr
    role: Literal["owner", "admissions_manager", "counsellor", "front_desk", "accounts", "academic_coordinator", "faculty", "storekeeper", "student", "parent", "parent_student"]
    is_active: bool = Field(alias="isActive")
    password: str | None = Field(default=None, min_length=10, max_length=128)
    model_config = ConfigDict(populate_by_name=True)


class BatchUpdate(BatchCreate):
    is_active: bool = Field(alias="isActive")
    model_config = ConfigDict(populate_by_name=True)


class SubjectUpdate(SubjectCreate):
    is_active: bool = Field(alias="isActive")
    model_config = ConfigDict(populate_by_name=True)


class RoomUpdate(RoomCreate):
    is_active: bool = Field(alias="isActive")
    model_config = ConfigDict(populate_by_name=True)


class StudentAccessCreate(BaseModel):
    student_id: str = Field(alias="studentId")
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    model_config = ConfigDict(populate_by_name=True)


class ParentAccessCreate(BaseModel):
    student_id: str = Field(alias="studentId")
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    contact_type: Literal["primary_contact", "secondary_contact"] = Field(
        default="primary_contact",
        alias="contactType",
    )
    model_config = ConfigDict(populate_by_name=True)


class StudentAssignmentStatusUpdate(BaseModel):
    status: Literal["published", "completed"]


class ClassSessionCreate(BaseModel):
    batch_id: str = Field(alias="batchId")
    subject_id: str = Field(alias="subjectId")
    faculty_id: str = Field(alias="facultyId")
    room_id: str = Field(alias="roomId")
    starts_at: datetime = Field(alias="startsAt")
    ends_at: datetime = Field(alias="endsAt")
    notes: str = Field(default="", max_length=2000)
    allow_override: bool = Field(default=False, alias="allowOverride")
    override_reason: str | None = Field(default=None, alias="overrideReason", max_length=1000)
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def valid_window(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("endsAt must be after startsAt")
        if self.allow_override and not (self.override_reason or "").strip():
            raise ValueError("overrideReason is required when allowOverride is true")
        return self


class ClassSessionUpdate(ClassSessionCreate):
    status: Literal["scheduled", "completed", "cancelled"] = "scheduled"


class AssignmentCreate(BaseModel):
    batch_id: str = Field(alias="batchId")
    subject_id: str = Field(alias="subjectId")
    title: str = Field(min_length=2, max_length=255)
    instructions: str = Field(default="", max_length=5000)
    due_at: datetime = Field(alias="dueAt")
    external_url: HttpUrl = Field(alias="externalUrl")
    status: Literal["draft", "published"] = "published"
    model_config = ConfigDict(populate_by_name=True)


class AssignmentUpdate(AssignmentCreate):
    pass


AttendanceStatus = Literal["present", "late", "absent", "excused"]


class AttendanceMark(BaseModel):
    student_id: str = Field(alias="studentId")
    status: AttendanceStatus
    reason: str = Field(default="", max_length=1000)
    model_config = ConfigDict(populate_by_name=True)


class AttendanceSave(BaseModel):
    entries: list[AttendanceMark] = Field(min_length=1)


class AttendanceCorrection(BaseModel):
    status: AttendanceStatus
    reason: str = Field(min_length=3, max_length=1000)


class NoticeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    body: str = Field(min_length=2, max_length=5000)
    audience: Literal["all", "parents", "students", "faculty", "batch"]
    channel: Literal["in_app", "email", "sms", "whatsapp"] = "in_app"
    batch_id: str | None = Field(default=None, alias="batchId")
    status: Literal["draft", "published"] = "published"
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def batch_audience_requires_batch(self):
        if self.audience == "batch" and not self.batch_id:
            raise ValueError("batchId is required for a batch audience")
        return self


class NoticeUpdate(NoticeCreate):
    pass
