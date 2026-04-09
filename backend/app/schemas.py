import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    message: str
    error: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ExtractedFields(BaseModel):
    name: str | None = None
    date: str | None = None
    amount: float | None = None
    vendor: str | None = None
    total: float | None = None
    parties: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    summary: str | None = None
    line_items: list[dict[str, Any]] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class StructuredExtraction(BaseModel):
    document_type: Literal["invoice", "resume", "contract", "unknown"] = "unknown"
    extracted_fields: ExtractedFields = Field(default_factory=ExtractedFields)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ExtractRequest(BaseModel):
    document_type_hint: Literal["invoice", "resume", "contract"] | None = None


class ExtractedDataOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    raw_text: str | None = None
    structured_json: dict[str, Any] | None = None
    confidence_score: float | None = None
    extracted_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_url: str
    document_type: str | None = None
    status: str
    processing_error: str | None = None
    uploaded_at: datetime
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    extracted_data: ExtractedDataOut | None = None


class SearchQuery(BaseModel):
    q: str = Field(min_length=1, max_length=200)
    document_type: Literal["invoice", "resume", "contract"] | None = None
