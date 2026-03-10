from __future__ import annotations

import re
from sqlite3 import Connection as SQLiteConnection

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


SCHEMA_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def create_engine_and_session(database_url: str, db_schema: str | None = None) -> tuple[Engine, sessionmaker[Session]]:
    connect_args = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    elif database_url.startswith("postgresql") and db_schema:
        if not SCHEMA_NAME_PATTERN.fullmatch(db_schema):
            raise ValueError("POSTGRES_SCHEMA must contain only letters, numbers, and underscores.")
        connect_args["options"] = f"-csearch_path={db_schema}"

    engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

    if database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection: SQLiteConnection, _connection_record: object) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return engine, session_factory


def initialize_database(engine: Engine, db_schema: str | None = None) -> None:
    if engine.dialect.name == "postgresql" and db_schema and db_schema != "public":
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{db_schema}"'))
