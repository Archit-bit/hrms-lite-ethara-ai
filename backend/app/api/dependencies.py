from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.orm import Session


async def get_db(request: Request) -> AsyncGenerator[Session, None]:
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()
