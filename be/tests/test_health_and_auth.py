import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_missing_role_header_returns_422(client):
    response = await client.get("/api/records")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_role_header_returns_400(client):
    response = await client.get("/api/records", headers=auth_headers("superadmin"))

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid x-user-role header. Use viewer, analyst, or admin."
