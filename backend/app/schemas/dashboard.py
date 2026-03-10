from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_employees: int
    total_attendance_records: int
    present_today: int
    absent_today: int
