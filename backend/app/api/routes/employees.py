from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas import ApiMessage, AttendanceResponse, EmployeeCreate, EmployeeResponse
from app.services.attendance_service import list_employee_attendance
from app.services.employee_service import create_employee, delete_employee, list_employees


router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeResponse])
async def list_employee_records(db: Session = Depends(get_db)) -> list[EmployeeResponse]:
    return list_employees(db)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee_record(payload: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeResponse:
    return create_employee(db, payload)


@router.delete("/{employee_id}", response_model=ApiMessage)
async def delete_employee_record(employee_id: str, db: Session = Depends(get_db)) -> ApiMessage:
    return delete_employee(db, employee_id)


@router.get("/{employee_id}/attendance", response_model=list[AttendanceResponse])
async def list_employee_attendance_records(
    employee_id: str,
    db: Session = Depends(get_db),
) -> list[AttendanceResponse]:
    return list_employee_attendance(db, employee_id)
