from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import AttendanceStatus


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class AttendanceCreate(BaseModel):
    employee_id: str = Field(min_length=2, max_length=32)
    date: date
    status: AttendanceStatus

    @field_validator("employee_id")
    @classmethod
    def normalize_employee_id(cls, value: str) -> str:
        return _normalize_text(value)


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    employee_name: str
    department: str
    date: date
    status: AttendanceStatus
    created_at: datetime
