from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import create_engine_and_session, initialize_database


def create_app(database_url: str | None = None) -> FastAPI:
    settings = get_settings(database_url)
    engine, session_factory = create_engine_and_session(settings.database_url, settings.db_schema)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        initialize_database(engine, settings.db_schema)
        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(
        title="HRMS Lite API",
        version="1.0.0",
        description="Employee and attendance management API for HRMS Lite.",
        lifespan=lifespan,
    )
    app.state.engine = engine
    app.state.session_factory = session_factory

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
