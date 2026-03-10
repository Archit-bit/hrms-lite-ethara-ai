from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Attendance, AttendanceStatus, Employee


def count_records(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Attendance)) or 0


def count_by_date_and_status(db: Session, *, attendance_date: date, status: AttendanceStatus) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Attendance)
        .where(Attendance.date == attendance_date, Attendance.status == status)
    ) or 0


def get_by_employee_and_date(db: Session, *, employee_ref: int, attendance_date: date) -> Attendance | None:
    return db.execute(
        select(Attendance).where(
            Attendance.employee_ref == employee_ref,
            Attendance.date == attendance_date,
        )
    ).scalar_one_or_none()


def list_by_employee(db: Session, *, employee_ref: int) -> list[Attendance]:
    return db.execute(
        select(Attendance)
        .options(joinedload(Attendance.employee))
        .where(Attendance.employee_ref == employee_ref)
        .order_by(Attendance.date.desc(), Attendance.created_at.desc())
    ).scalars().all()


def list_records(
    db: Session,
    *,
    employee_id: str | None = None,
    attendance_date: date | None = None,
    status_filter: AttendanceStatus | None = None,
) -> list[Attendance]:
    query = (
        select(Attendance)
        .options(joinedload(Attendance.employee))
        .join(Employee)
        .order_by(Attendance.date.desc(), Employee.full_name.asc())
    )

    if employee_id:
        query = query.where(Employee.employee_id == employee_id)
    if attendance_date:
        query = query.where(Attendance.date == attendance_date)
    if status_filter:
        query = query.where(Attendance.status == status_filter)

    return db.execute(query).scalars().all()


def create(db: Session, *, employee_ref: int, attendance_date: date, status: AttendanceStatus) -> Attendance:
    record = Attendance(employee_ref=employee_ref, date=attendance_date, status=status)
    db.add(record)
    db.flush()
    return record
