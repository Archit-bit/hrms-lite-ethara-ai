from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path

import httpx

from app.core.config import get_settings
from app.db.base import Base
from app.main import create_app


def build_test_app(tmp_path: Path, filename: str):
    database_url = f"sqlite:///{(tmp_path / filename).as_posix()}"
    app = create_app(database_url)
    Base.metadata.create_all(bind=app.state.engine)
    return app


def api_request(app, method: str, path: str, **kwargs) -> httpx.Response:
    async def _request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_request())


def test_employee_and_attendance_flow(tmp_path: Path) -> None:
    app = build_test_app(tmp_path, "test.db")

    create_employee = api_request(
        app,
        "POST",
        "/api/employees",
        json={
            "employee_id": "EMP-1001",
            "full_name": "Ava Carter",
            "email_address": "ava@example.com",
            "department": "Operations",
        },
    )
    assert create_employee.status_code == 201
    assert create_employee.json()["employee_id"] == "EMP-1001"

    duplicate_employee = api_request(
        app,
        "POST",
        "/api/employees",
        json={
            "employee_id": "EMP-1001",
            "full_name": "Duplicate User",
            "email_address": "duplicate@example.com",
            "department": "Operations",
        },
    )
    assert duplicate_employee.status_code == 409

    attendance = api_request(
        app,
        "POST",
        "/api/attendance",
        json={
            "employee_id": "EMP-1001",
            "date": date.today().isoformat(),
            "status": "PRESENT",
        },
    )
    assert attendance.status_code == 201
    assert attendance.json()["status"] == "PRESENT"

    filtered_attendance = api_request(app, "GET", "/api/attendance", params={"employee_id": "EMP-1001"})
    assert filtered_attendance.status_code == 200
    assert len(filtered_attendance.json()) == 1

    dashboard = api_request(app, "GET", "/api/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["total_employees"] == 1
    assert dashboard.json()["present_today"] == 1


def test_validation_errors_return_meaningful_messages(tmp_path: Path) -> None:
    app = build_test_app(tmp_path, "validation.db")

    response = api_request(
        app,
        "POST",
        "/api/employees",
        json={
            "employee_id": "E1",
            "full_name": "",
            "email_address": "not-an-email",
            "department": "",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["message"] == "Validation failed."
    assert len(body["errors"]) >= 2


def test_database_url_is_normalized_for_railway_postgres(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("DATABASE_URL", "postgresql://demo:secret@db.railway.internal:5432/hrms_lite")

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://demo:secret@db.railway.internal:5432/hrms_lite"

    get_settings.cache_clear()
