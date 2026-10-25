"""Health check routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter(tags=["observability"])


@router.get("/healthz")
async def liveness():
    return {"status": "ok", "env": settings.application_env}


@router.get("/readyz")
async def readiness():
    return {"status": "ready"}
