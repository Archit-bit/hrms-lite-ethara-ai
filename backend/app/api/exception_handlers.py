from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import AppError
from app.schemas import ValidationErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: object, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"message": exc.message})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: object, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: object, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            location = " -> ".join(str(part) for part in error["loc"] if part != "body")
            errors.append(f"{location or 'request'}: {error['msg']}")
        payload = ValidationErrorResponse(message="Validation failed.", errors=errors)
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload.model_dump())

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(_request: object, _exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Database operation failed."},
        )
