from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary


router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    return get_dashboard_summary(db)
