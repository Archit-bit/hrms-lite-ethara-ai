from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Attendance, AttendanceStatus, Employee


def _employee_present_days_query():
    return func.coalesce(
        func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)),
        0,
    ).label("total_present_days")


def list_employees_with_present_days(db: Session) -> list[tuple[Employee, int]]:
    present_days = _employee_present_days_query()
    rows = db.execute(
        select(Employee, present_days)
        .outerjoin(Attendance, Attendance.employee_ref == Employee.id)
        .group_by(Employee.id)
        .order_by(Employee.created_at.desc())
    ).all()
    return [(employee, total_present_days) for employee, total_present_days in rows]


def get_by_employee_id(db: Session, employee_id: str) -> Employee | None:
    return db.execute(select(Employee).where(Employee.employee_id == employee_id)).scalar_one_or_none()


def get_by_employee_id_or_email(db: Session, employee_id: str, email_address: str) -> Employee | None:
    return db.execute(
        select(Employee).where(
            (Employee.employee_id == employee_id) | (Employee.email_address == email_address)
        )
    ).scalar_one_or_none()


def count_employees(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Employee)) or 0


def create(db: Session, *, employee_id: str, full_name: str, email_address: str, department: str) -> Employee:
    employee = Employee(
        employee_id=employee_id,
        full_name=full_name,
        email_address=email_address,
        department=department,
    )
    db.add(employee)
    db.flush()
    return employee


def delete(db: Session, employee: Employee) -> None:
    db.delete(employee)
