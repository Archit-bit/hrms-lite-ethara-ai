from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.repositories import employee_repository
from app.schemas import ApiMessage, EmployeeCreate, EmployeeResponse
from app.services.mappers import to_employee_response


def list_employees(db: Session) -> list[EmployeeResponse]:
    rows = employee_repository.list_employees_with_present_days(db)
    return [to_employee_response(employee, total_present_days) for employee, total_present_days in rows]


def create_employee(db: Session, payload: EmployeeCreate) -> EmployeeResponse:
    duplicate_employee = employee_repository.get_by_employee_id_or_email(
        db,
        payload.employee_id,
        payload.email_address,
    )
    if duplicate_employee:
        if duplicate_employee.employee_id == payload.employee_id:
            raise ConflictError("Employee ID already exists.")
        raise ConflictError("Email address already exists.")

    employee = employee_repository.create(
        db,
        employee_id=payload.employee_id,
        full_name=payload.full_name,
        email_address=payload.email_address,
        department=payload.department,
    )
    db.commit()
    db.refresh(employee)
    return to_employee_response(employee, 0)


def get_employee_or_raise(db: Session, employee_id: str):
    employee = employee_repository.get_by_employee_id(db, employee_id)
    if not employee:
        raise NotFoundError("Employee not found.")
    return employee


def delete_employee(db: Session, employee_id: str) -> ApiMessage:
    employee = get_employee_or_raise(db, employee_id)
    employee_repository.delete(db, employee)
    db.commit()
    return ApiMessage(message="Employee deleted successfully.")
