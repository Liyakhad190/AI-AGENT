"""Pytest fixtures: async HTTP client against the FastAPI app with a clean DB."""
from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_dev.db")
os.environ.setdefault("APPLICATION_ENV", "testing")
os.environ.setdefault("APP_SECRET_KEY", "test-secret")

from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrate_test_db():
    os.remove("test_dev.db") if os.path.exists("test_dev.db") else None
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    command.upgrade(alembic_cfg, "head")
    yield
    try:
        os.remove("test_dev.db")
    except OSError:
        pass


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_client(client):
    """Register and log in a test user, return (client, token, user_id)."""
    unique = uuid.uuid4().hex[:8]
    email = f"test-{unique}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Test User"},
    )
    r = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "secret123"}
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    me = await client.get("/api/v1/auth/me")
    user_id = me.json()["id"]
    return client, token, user_id
