import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_viewer_cannot_list_users(client, seeded_data):
    response = await client.get("/api/users", headers=auth_headers("viewer"))

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_analyst_can_list_users_sorted_by_created_at(client, seeded_data):
    response = await client.get("/api/users", headers=auth_headers("analyst"))

    assert response.status_code == 200
    emails = [item["email"] for item in response.json()]
    assert emails == ["admin@example.com", "analyst@example.com", "viewer@example.com"]


@pytest.mark.asyncio
async def test_admin_can_create_user(client, seeded_data):
    payload = {
        "name": "New Admin",
        "email": "new-admin@example.com",
        "role": "admin",
        "status": "active",
    }

    response = await client.post("/api/users", headers=auth_headers("admin"), json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]


@pytest.mark.asyncio
async def test_admin_cannot_create_duplicate_user(client, seeded_data):
    payload = {
        "name": "Duplicate",
        "email": "admin@example.com",
        "role": "viewer",
        "status": "active",
    }

    response = await client.post("/api/users", headers=auth_headers("admin"), json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "A user with this email already exists."


@pytest.mark.asyncio
async def test_admin_can_update_user(client, seeded_data):
    response = await client.patch(
        "/api/users/2",
        headers=auth_headers("admin"),
        json={"name": "Updated Analyst", "status": "inactive"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Analyst"
    assert response.json()["status"] == "inactive"


@pytest.mark.asyncio
async def test_admin_cannot_update_user_to_duplicate_email(client, seeded_data):
    response = await client.patch(
        "/api/users/2",
        headers=auth_headers("admin"),
        json={"email": "admin@example.com"},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_updating_missing_user_returns_404(client, seeded_data):
    response = await client.patch(
        "/api/users/999",
        headers=auth_headers("admin"),
        json={"name": "Nobody"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
