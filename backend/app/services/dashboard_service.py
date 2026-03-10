from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models import AttendanceStatus
from app.repositories import attendance_repository, employee_repository
from app.schemas import DashboardSummary


def get_dashboard_summary(db: Session) -> DashboardSummary:
    today = date.today()
    return DashboardSummary(
        total_employees=employee_repository.count_employees(db),
        total_attendance_records=attendance_repository.count_records(db),
        present_today=attendance_repository.count_by_date_and_status(
            db,
            attendance_date=today,
            status=AttendanceStatus.PRESENT,
        ),
        absent_today=attendance_repository.count_by_date_and_status(
            db,
            attendance_date=today,
            status=AttendanceStatus.ABSENT,
        ),
    )
