from __future__ import annotations

from app.models import Attendance, Employee
from app.schemas import AttendanceResponse, EmployeeResponse


def to_employee_response(employee: Employee, total_present_days: int) -> EmployeeResponse:
    return EmployeeResponse(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        email_address=employee.email_address,
        department=employee.department,
        created_at=employee.created_at,
        total_present_days=total_present_days,
    )


def to_attendance_response(record: Attendance) -> AttendanceResponse:
    return AttendanceResponse(
        id=record.id,
        employee_id=record.employee.employee_id,
        employee_name=record.employee.full_name,
        department=record.employee.department,
        date=record.date,
        status=record.status,
        created_at=record.created_at,
    )
