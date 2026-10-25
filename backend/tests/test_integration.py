"""Integration tests for API endpoints using mock telephony and voice providers."""
import pytest


@pytest.mark.asyncio
async def test_register_login_me_flow(auth_client):
    client, token, user_id = auth_client
    assert token
    assert user_id
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["email"].endswith("@example.com")


@pytest.mark.asyncio
async def test_unauthenticated_endpoints_rejected(client):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401
    r = await client.get("/api/v1/tasks/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_call_initiate_status_terminate(auth_client):
    client, token, user_id = auth_client
    r = await client.post(
        "/api/v1/calls/initiate",
        json={"to_number": "+919876543210"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "ringing"
    assert data["provider_call_id"].startswith("mock-call-")
    call_id = data["call_id"]

    r = await client.get(f"/api/v1/calls/{call_id}/status")
    assert r.status_code == 200
    assert r.json()["status"] in ("ringing", "connected", "completed")

    r = await client.post(f"/api/v1/calls/{call_id}/terminate")
    assert r.status_code == 200
    assert r.json()["terminated"] is True


@pytest.mark.asyncio
async def test_call_initiate_requires_destination(auth_client):
    client, token, user_id = auth_client
    # No to_number and no VERIFIED_DESTINATION_NUMBER configured -> 400
    r = await client.post("/api/v1/calls/initiate", json={})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_task_create_and_list(auth_client):
    client, token, user_id = auth_client
    r = await client.post("/api/v1/tasks/", json={"goal": "Check my email"})
    assert r.status_code == 200, r.text
    task = r.json()
    assert task["goal"] == "Check my email"
    assert task["status"] == "PENDING"

    r = await client.get("/api/v1/tasks/")
    assert r.status_code == 200
    assert any(t["id"] == task["id"] for t in r.json())


@pytest.mark.asyncio
async def test_task_get_not_found(auth_client):
    client, token, user_id = auth_client
    r = await client.get(f"/api/v1/tasks/{uuid_nonexistent()}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_task_cancel_and_approve(auth_client):
    client, token, user_id = auth_client
    r = await client.post("/api/v1/tasks/", json={"goal": "Send an email"})
    assert r.status_code == 200
    task_id = r.json()["id"]

    r = await client.post(f"/api/v1/tasks/{task_id}/cancel")
    assert r.status_code == 200
    assert r.json()["status"] == "CANCELLED"


def uuid_nonexistent():
    import uuid
    return str(uuid.uuid4())
