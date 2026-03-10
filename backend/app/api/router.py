from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.attendance import router as attendance_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.employees import router as employees_router
from app.api.routes.health import router as health_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(dashboard_router)
api_router.include_router(employees_router)
api_router.include_router(attendance_router)
