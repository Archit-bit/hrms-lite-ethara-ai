from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


@dataclass(slots=True)
class Settings:
    database_url: str
    cors_origins: list[str]
    db_schema: str | None


def _get_required_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


def _build_postgres_database_url() -> tuple[str, str]:
    server_name = os.getenv("POSTGRES_SERVER", os.getenv("POSTGRES_HOST", "")).strip()
    if not server_name:
        raise ValueError("Missing required environment variable: POSTGRES_SERVER")

    port = os.getenv("POSTGRES_PORT", "5432").strip() or "5432"
    database_name = _get_required_env("POSTGRES_DB")
    username = _get_required_env("POSTGRES_USER")
    password = _get_required_env("POSTGRES_PASSWORD")
    schema_name = os.getenv("POSTGRES_SCHEMA", "public").strip() or "public"

    database_url = (
        f"postgresql+psycopg://{quote_plus(username)}:{quote_plus(password)}"
        f"@{server_name}:{port}/{database_name}"
    )
    return database_url, schema_name


@lru_cache(maxsize=8)
def get_settings(database_url: str | None = None) -> Settings:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    default_database_url = f"sqlite:///{(DATA_DIR / 'hrms.db').as_posix()}"
    raw_cors_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    selected_database_url = database_url
    db_schema: str | None = None

    if not selected_database_url:
        explicit_database_url = os.getenv("DATABASE_URL", "").strip()
        if explicit_database_url:
            selected_database_url = explicit_database_url
            db_schema = os.getenv("POSTGRES_SCHEMA", "").strip() or None
        else:
            db_engine = os.getenv("DB_ENGINE", "sqlite").strip().lower()
            if db_engine == "postgresql":
                selected_database_url, db_schema = _build_postgres_database_url()
            else:
                sqlite_path = os.getenv("SQLITE_PATH", (DATA_DIR / "hrms.db").as_posix()).strip()
                if not Path(sqlite_path).is_absolute():
                    sqlite_path = (BASE_DIR / sqlite_path).resolve().as_posix()
                selected_database_url = f"sqlite:///{sqlite_path}"

    return Settings(
        database_url=selected_database_url or default_database_url,
        cors_origins=[origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()],
        db_schema=db_schema,
    )
