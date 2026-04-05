import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_all_roles_can_list_records_according_to_permissions(client, seeded_data):
    for role in ("viewer", "analyst", "admin"):
        response = await client.get("/api/records", headers=auth_headers(role))
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_records_are_sorted_by_created_at_ascending(client, seeded_data):
    response = await client.get("/api/records", headers=auth_headers("viewer"))

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["data"]]
    assert ids == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_records_support_filters_and_pagination(client, seeded_data):
    response = await client.get(
        "/api/records?page=1&page_size=1&category=Rent&type=expense&start_date=2026-02-01&end_date=2026-02-28",
        headers=auth_headers("viewer"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"] == {"total": 1, "page": 1, "page_size": 1}
    assert payload["data"][0]["category"] == "Rent"


@pytest.mark.asyncio
async def test_viewer_cannot_create_record(client, seeded_data):
    response = await client.post(
        "/api/records",
        headers=auth_headers("viewer"),
        json={
            "amount": 90,
            "type": "expense",
            "category": "Coffee",
            "entry_date": "2026-04-01",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_create_record(client, seeded_data):
    response = await client.post(
        "/api/records",
        headers=auth_headers("admin"),
        json={
            "amount": 90,
            "type": "expense",
            "category": "Coffee",
            "entry_date": "2026-04-01",
            "notes": "Team coffee",
            "created_by_user_id": 1,
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "Coffee"


@pytest.mark.asyncio
async def test_admin_can_update_record(client, seeded_data):
    response = await client.patch(
        "/api/records/1",
        headers=auth_headers("admin"),
        json={"amount": 5500, "notes": "Updated salary"},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "5500.00"
    assert response.json()["notes"] == "Updated salary"


@pytest.mark.asyncio
async def test_updating_missing_record_returns_404(client, seeded_data):
    response = await client.patch(
        "/api/records/999",
        headers=auth_headers("admin"),
        json={"amount": 10},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Financial record not found."


@pytest.mark.asyncio
async def test_admin_can_delete_record(client, seeded_data):
    response = await client.delete("/api/records/1", headers=auth_headers("admin"))

    assert response.status_code == 200
    assert response.json()["message"] == "Financial record deleted successfully."


@pytest.mark.asyncio
async def test_deleting_missing_record_returns_404(client, seeded_data):
    response = await client.delete("/api/records/999", headers=auth_headers("admin"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Financial record not found."
