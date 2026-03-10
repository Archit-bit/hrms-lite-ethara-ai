from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class EmployeeCreate(BaseModel):
    employee_id: str = Field(min_length=2, max_length=32)
    full_name: str = Field(min_length=2, max_length=120)
    email_address: EmailStr
    department: str = Field(min_length=2, max_length=80)

    @field_validator("employee_id", "full_name", "department")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return _normalize_text(value)

    @field_validator("email_address")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    full_name: str
    email_address: str
    department: str
    created_at: datetime
    total_present_days: int = 0
