from __future__ import annotations

from fastapi import APIRouter

from app.schemas import ApiMessage


router = APIRouter(tags=["system"])


@router.get("/health", response_model=ApiMessage)
async def healthcheck() -> ApiMessage:
    return ApiMessage(message="ok")
