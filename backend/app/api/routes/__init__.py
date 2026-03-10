from app.api.routes.attendance import router as attendance_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.employees import router as employees_router
from app.api.routes.health import router as health_router

__all__ = ["attendance_router", "dashboard_router", "employees_router", "health_router"]
