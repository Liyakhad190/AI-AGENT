"""FastAPI application entry point."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import calls, health, integrations, tasks, schedule, auth as auth_router
from app.config.settings import settings
from app.observability.logging import configure_logging, get_logger, set_correlation_id
from app.scheduler.worker import run_scheduler_loop

configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background scheduler loop
    scheduler_task = asyncio.create_task(run_scheduler_loop())
    yield
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI Voice Agent",
    description="Production-grade autonomous AI voice agent for outbound/inbound calls.",
    version="0.1.0",
    docs_url="/docs" if settings.application_env != "production" else None,
    redoc_url=None if settings.application_env == "production" else "/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    cid = request.headers.get("x-correlation-id") or str(__import__("uuid").uuid4())
    set_correlation_id(cid)
    response = await call_next(request)
    response.headers["x-correlation-id"] = cid
    return response


API_V1_PREFIX = "/api/v1"
app.include_router(auth_router.router, prefix="/api/v1/auth")
app.include_router(calls.router, prefix=API_V1_PREFIX)
app.include_router(tasks.router, prefix=API_V1_PREFIX)
app.include_router(schedule.router, prefix=API_V1_PREFIX)
app.include_router(integrations.router, prefix=API_V1_PREFIX)
app.include_router(health.router, prefix=API_V1_PREFIX)


@app.get("/healthz", tags=["observability"])
async def liveness():
    return {"status": "ok"}


@app.get("/readyz", tags=["observability"])
async def readiness():
    return {"status": "ready"}


@app.get("/", tags=["root"])
async def root():
    return {
        "service": "ai-voice-agent",
        "version": "0.1.0",
        "env": settings.application_env,
    }
