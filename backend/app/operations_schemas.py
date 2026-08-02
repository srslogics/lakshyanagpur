from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator, model_validator

from .identity import normalize_mobile


class MobileIdentityMixin(BaseModel):
    mobile: str

    @field_validator("mobile")
    @classmethod
    def valid_mobile(cls, value):
        return normalize_mobile(value)

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def empty_email_is_none(cls, value):
        return value or None


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
    subjects: list[str] | None = Field(default=None, max_length=8)
    model_config = ConfigDict(populate_by_name=True)


class StudentCreate(BaseModel):
    fullName: str = Field(min_length=2, max_length=255)
    mobile: str | None = None
    secondaryMobile: str | None = None
    email: EmailStr | None = None
    previousSchool: str | None = Field(default=None, max_length=255)
    program: Literal["JEE", "NEET", "MHT-CET", "Boards", "Boards 11th & 12th Tuition"]
    batch: Literal["Essential", "Tatva"]
    enrollmentDate: date
    status: Literal["active", "draft"] = "active"
    subjects: list[str] = Field(min_length=1, max_length=8)
    agreedAmount: int = Field(ge=0)

    @field_validator("fullName")
    @classmethod
    def valid_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Enter the student's full name")
        return value

    @field_validator("mobile", "secondaryMobile", mode="before")
    @classmethod
    def optional_mobile(cls, value):
        if value is None or not str(value).strip():
            return None
        return normalize_mobile(str(value))

    @model_validator(mode="after")
    def contacts_are_distinct(self):
        if self.mobile and self.secondaryMobile == self.mobile:
            raise ValueError("Primary and secondary mobile numbers must be different")
        return self


class FeeAgreementUpdate(BaseModel):
    agreed_amount: int = Field(alias="agreedAmount", ge=0)
    legacy_registration_total: int = Field(alias="legacyRegistrationTotal", ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    status: Literal["active", "draft", "inactive", "completed"] = "active"
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("currency")
    @classmethod
    def inr_only(cls, value):
        if value.strip().upper() != "INR":
            raise ValueError("currency must be INR")
        return "INR"


class FeeAgreementCreate(BaseModel):
    student_id: str = Field(alias="studentId")
    agreed_amount: int = Field(alias="agreedAmount", ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    status: Literal["active", "draft"] = "active"
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("currency")
    @classmethod
    def inr_only(cls, value):
        if value.strip().upper() != "INR":
            raise ValueError("currency must be INR")
        return "INR"


class PaymentReviewUpdate(BaseModel):
    reconciliation_status: Literal[
        "ready",
        "needs_date",
        "needs_mode",
        "review",
        "do_not_import",
    ] = Field(alias="reconciliationStatus")
    transaction_date: date | None = Field(default=None, alias="transactionDate")
    method: Literal["cash", "upi", "bank_transfer", "cheque", "card", "other"] | None = None
    reference: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    model_config = ConfigDict(populate_by_name=True)


PaymentMethod = Literal[
    "not_decided",
    "cash",
    "upi",
    "bank_transfer",
    "cheque",
    "card",
    "other",
]


class PaymentCreate(BaseModel):
    student_id: str = Field(alias="studentId")
    transaction_date: date = Field(alias="transactionDate")
    amount: int = Field(gt=0)
    method: PaymentMethod
    reference: str | None = Field(default=None, max_length=255)
    notes: str = Field(default="", max_length=2000)
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("method")
    @classmethod
    def decided_method(cls, value):
        if value == "not_decided":
            raise ValueError("Select the payment method")
        return value


class PaymentReversalCreate(BaseModel):
    transaction_date: date = Field(alias="transactionDate")
    kind: Literal["reversal", "refund", "void"] = "reversal"
    amount: int | None = Field(default=None, gt=0)
    reason: str = Field(min_length=3, max_length=2000)
    reference: str | None = Field(default=None, max_length=255)
    model_config = ConfigDict(populate_by_name=True)


class FeeInstallmentCreate(BaseModel):
    studentId: str
    dueDate: date
    amount: int = Field(gt=0)
    expectedMethod: PaymentMethod = "not_decided"
    notes: str = Field(default="", max_length=1000)


class FeeInstallmentUpdate(BaseModel):
    dueDate: date
    amount: int = Field(gt=0)
    expectedMethod: PaymentMethod = "not_decided"
    notes: str = Field(default="", max_length=1000)
    status: Literal["scheduled", "cancelled"] = "scheduled"


class UserCreate(MobileIdentityMixin):
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    email: EmailStr | None = None
    password: str = Field(min_length=10, max_length=128)
    role: Literal["admissions_manager", "counsellor", "front_desk", "accounts", "academic_coordinator", "faculty", "attendance_operator", "storekeeper", "student", "parent", "parent_student"]
    model_config = ConfigDict(populate_by_name=True)


class UserUpdate(MobileIdentityMixin):
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    email: EmailStr | None = None
    role: Literal["owner", "admissions_manager", "counsellor", "front_desk", "accounts", "academic_coordinator", "faculty", "attendance_operator", "storekeeper", "student", "parent", "parent_student"]
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


class StudentAccessCreate(MobileIdentityMixin):
    student_id: str = Field(alias="studentId")
    email: EmailStr | None = None
    password: str = Field(min_length=10, max_length=128)
    model_config = ConfigDict(populate_by_name=True)


class ParentAccessCreate(MobileIdentityMixin):
    student_id: str = Field(alias="studentId")
    full_name: str = Field(alias="fullName", min_length=2, max_length=255)
    email: EmailStr | None = None
    password: str = Field(min_length=10, max_length=128)
    contact_type: Literal["primary_contact", "secondary_contact"] = Field(
        default="primary_contact",
        alias="contactType",
    )
    model_config = ConfigDict(populate_by_name=True)


class StudentAssignmentStatusUpdate(BaseModel):
    status: Literal["published", "viewed", "submitted", "completed"]


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


class FacultyTeachingAssignmentCreate(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    batch_id: str = Field(alias="batchId")
    subject_id: str = Field(alias="subjectId")
    model_config = ConfigDict(populate_by_name=True)


class FacultyTeachingAssignmentUpdate(FacultyTeachingAssignmentCreate):
    is_active: bool = Field(alias="isActive")


InventoryCategory = Literal["book", "bag", "apparel", "other"]


class InventoryItemCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=255)
    category: InventoryCategory
    unit: str = Field(default="piece", min_length=1, max_length=40)
    quantityOnHand: int | None = Field(default=None, ge=0)
    reorderLevel: int = Field(default=0, ge=0)
    vendorReference: str | None = Field(default=None, max_length=255)
    notes: str = Field(default="", max_length=2000)


class InventoryItemUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    category: InventoryCategory
    unit: str = Field(min_length=1, max_length=40)
    quantityOnHand: int | None = Field(default=None, ge=0)
    reorderLevel: int = Field(default=0, ge=0)
    vendorReference: str | None = Field(default=None, max_length=255)
    notes: str = Field(default="", max_length=2000)
    isActive: bool


class InventoryMovementCreate(BaseModel):
    movementType: Literal[
        "inward",
        "issue",
        "return",
        "write_off",
        "adjustment",
    ]
    quantity: int
    occurredOn: date
    targetType: Literal[
        "student",
        "batch",
        "faculty",
        "department",
        "vendor",
        "other",
    ] | None = None
    targetReference: str | None = Field(default=None, max_length=255)
    studentId: str | None = None
    reference: str | None = Field(default=None, max_length=255)
    reason: str = Field(min_length=3, max_length=2000)

    @model_validator(mode="after")
    def valid_direction_and_target(self):
        if self.quantity == 0:
            raise ValueError("quantity cannot be zero")
        if self.movementType != "adjustment" and self.quantity < 0:
            raise ValueError(
                "quantity must be positive except for an adjustment",
            )
        if self.targetType == "student" and not self.studentId:
            raise ValueError("studentId is required for a student issue")
        if self.studentId and self.targetType != "student":
            raise ValueError(
                "studentId is allowed only when targetType is student",
            )
        return self


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


class ExaminationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    batch_id: str = Field(alias="batchId")
    subject_id: str = Field(alias="subjectId")
    faculty_id: str = Field(alias="facultyId")
    scheduled_at: datetime = Field(alias="scheduledAt")
    duration_minutes: int = Field(alias="durationMinutes", ge=15, le=480)
    max_marks: Decimal = Field(alias="maxMarks", gt=0, le=10000, decimal_places=2)
    pass_marks: Decimal = Field(alias="passMarks", ge=0, le=10000, decimal_places=2)
    instructions: str = Field(default="", max_length=5000)
    status: Literal["draft", "scheduled"] = "scheduled"
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def valid_marks(self):
        if self.pass_marks > self.max_marks:
            raise ValueError("passMarks cannot exceed maxMarks")
        return self


class ExaminationUpdate(ExaminationCreate):
    status: Literal["draft", "scheduled", "marks_entry", "cancelled"] = "scheduled"


class ExaminationMark(BaseModel):
    student_id: str = Field(alias="studentId")
    result_status: Literal["pending", "graded", "absent", "withheld"] = Field(
        alias="resultStatus",
    )
    marks_obtained: Decimal | None = Field(
        default=None,
        alias="marksObtained",
        ge=0,
        le=10000,
        decimal_places=2,
    )
    remarks: str = Field(default="", max_length=500)
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def status_matches_marks(self):
        if self.result_status == "graded" and self.marks_obtained is None:
            raise ValueError("marksObtained is required for a graded result")
        if self.result_status != "graded" and self.marks_obtained is not None:
            raise ValueError("marksObtained is allowed only for a graded result")
        return self


class ExaminationMarksSave(BaseModel):
    entries: list[ExaminationMark] = Field(min_length=1)


AttendanceStatus = Literal["present", "late", "absent", "excused"]


class AttendanceMark(BaseModel):
    student_id: str = Field(alias="studentId")
    status: AttendanceStatus
    reason: str = Field(default="", max_length=1000)
    model_config = ConfigDict(populate_by_name=True)


class AttendanceSave(BaseModel):
    entries: list[AttendanceMark] = Field(min_length=1)


class ManualAttendanceRegisterOpen(BaseModel):
    date: date
    batch: str = Field(min_length=1, max_length=120)
    stream: str = Field(min_length=1, max_length=120)
    subject: str = Field(min_length=1, max_length=120)


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


class CommunicationThreadCreate(BaseModel):
    subject_id: str | None = Field(default=None, alias="subjectId")
    topic: str = Field(min_length=2, max_length=255)
    body: str = Field(min_length=1, max_length=3000)
    model_config = ConfigDict(populate_by_name=True)


class CommunicationMessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=3000)


class CommunicationThreadStatusUpdate(BaseModel):
    status: Literal["open", "closed"]
