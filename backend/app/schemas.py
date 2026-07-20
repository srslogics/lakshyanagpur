from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

LEAD_STAGES = ("New Enquiry", "Contact Attempted", "Contacted", "Follow-up Scheduled", "Counselling Planned", "Counselling Done", "Interested", "Documents Pending", "Admission Confirmed", "Converted", "Lost", "Not Interested")
LEAD_SOURCES = ("walk-in", "website", "phone", "whatsapp", "referral", "campaign", "seminar", "social media")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class BootstrapOwnerRequest(BaseModel):
    full_name: Annotated[str, Field(min_length=2, max_length=255, alias="fullName")]
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    model_config = ConfigDict(populate_by_name=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LeadCreate(BaseModel):
    student: str = Field(min_length=2, max_length=255)
    mobile: str
    email: EmailStr | None = None
    parent: str = Field(min_length=2, max_length=255)
    parent_mobile: Annotated[str | None, Field(alias="parentMobile")] = None
    program: str = Field(min_length=2, max_length=255)
    source: str
    counsellor: str = Field(min_length=2, max_length=255)
    stage: str = "New Enquiry"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    next_action: str = Field(min_length=2, max_length=255, alias="nextAction")
    next_follow_up_at: Annotated[datetime | None, Field(alias="nextFollowUpAt")] = None
    summary: str = Field("", max_length=4000)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("mobile", "parent_mobile")
    @classmethod
    def valid_mobile(cls, value):
        if value is None:
            return value
        digits = "".join(c for c in value if c.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("mobile number must contain 10 to 15 digits")
        return digits

    @field_validator("stage")
    @classmethod
    def valid_stage(cls, value):
        if value not in LEAD_STAGES:
            raise ValueError("invalid admissions stage")
        return value

    @field_validator("source")
    @classmethod
    def valid_source(cls, value):
        normalized = value.strip().lower()
        if normalized not in LEAD_SOURCES:
            raise ValueError("invalid lead source")
        return normalized


class LeadRead(BaseModel):
    id: str
    student: str
    mobile: str
    email: str | None
    parent: str
    parent_mobile: Annotated[str | None, Field(alias="parentMobile")]
    program: str
    source: str
    counsellor: str
    stage: str
    priority: str
    next_action: str = Field(alias="nextAction")
    next_follow_up_at: Annotated[datetime | None, Field(alias="nextFollowUpAt")]
    summary: str
    converted_student_id: Annotated[str | None, Field(alias="convertedStudentId")]
    created_at: datetime = Field(alias="createdAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LeadStageUpdate(BaseModel):
    stage: str

    @field_validator("stage")
    @classmethod
    def valid_stage(cls, value):
        if value not in LEAD_STAGES:
            raise ValueError("invalid admissions stage")
        return value


class LeadActivityUpdate(BaseModel):
    kind: Literal["note", "call", "follow_up", "counselling"] = "note"
    note: str = Field(min_length=2, max_length=4000)
    next_action: Annotated[str | None, Field(alias="nextAction", max_length=255)] = None
    next_follow_up_at: Annotated[datetime | None, Field(alias="nextFollowUpAt")] = None
    model_config = ConfigDict(populate_by_name=True)


class ConversionRequest(BaseModel):
    batch: str | None = Field(None, max_length=255)
    guardian_relationship: Annotated[str, Field(alias="guardianRelationship", max_length=32)] = "guardian"
    concession_requested: Annotated[bool, Field(alias="concessionRequested")] = False
    model_config = ConfigDict(populate_by_name=True)


class ConversionResult(BaseModel):
    lead_id: str = Field(alias="leadId")
    student_id: str = Field(alias="studentId")
    guardian_id: str = Field(alias="guardianId")
    enrollment_id: str = Field(alias="enrollmentId")
    finance_handoff_id: str = Field(alias="financeHandoffId")
    model_config = ConfigDict(populate_by_name=True)


class Page(BaseModel):
    items: list[LeadRead]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
    model_config = ConfigDict(populate_by_name=True)
