from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import AttendanceStatus
from app.schemas import AttendanceCreate, AttendanceResponse
from app.services.attendance_service import create_attendance, list_attendance


router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.get("", response_model=list[AttendanceResponse])
async def list_attendance_records(
    employee_id: str | None = Query(default=None),
    attendance_date: date | None = Query(default=None, alias="date"),
    status_filter: AttendanceStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[AttendanceResponse]:
    return list_attendance(
        db,
        employee_id=employee_id,
        attendance_date=attendance_date,
        status_filter=status_filter,
    )


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance_record(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
) -> AttendanceResponse:
    return create_attendance(db, payload)
