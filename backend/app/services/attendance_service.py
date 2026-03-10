from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.models import AttendanceStatus
from app.repositories import attendance_repository
from app.schemas import AttendanceCreate, AttendanceResponse
from app.services.employee_service import get_employee_or_raise
from app.services.mappers import to_attendance_response


def list_attendance(
    db: Session,
    *,
    employee_id: str | None = None,
    attendance_date: date | None = None,
    status_filter: AttendanceStatus | None = None,
) -> list[AttendanceResponse]:
    records = attendance_repository.list_records(
        db,
        employee_id=employee_id,
        attendance_date=attendance_date,
        status_filter=status_filter,
    )
    return [to_attendance_response(record) for record in records]


def list_employee_attendance(db: Session, employee_id: str) -> list[AttendanceResponse]:
    employee = get_employee_or_raise(db, employee_id)
    records = attendance_repository.list_by_employee(db, employee_ref=employee.id)
    return [to_attendance_response(record) for record in records]


def create_attendance(db: Session, payload: AttendanceCreate) -> AttendanceResponse:
    employee = get_employee_or_raise(db, payload.employee_id)
    existing_record = attendance_repository.get_by_employee_and_date(
        db,
        employee_ref=employee.id,
        attendance_date=payload.date,
    )
    if existing_record:
        raise ConflictError("Attendance for this employee and date already exists.")

    record = attendance_repository.create(
        db,
        employee_ref=employee.id,
        attendance_date=payload.date,
        status=payload.status,
    )
    db.commit()
    db.refresh(record)
    record.employee = employee
    return to_attendance_response(record)
