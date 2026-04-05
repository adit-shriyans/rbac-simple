import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_viewer_cannot_access_dashboard(client, seeded_data):
    response = await client.get("/api/dashboard/summary", headers=auth_headers("viewer"))

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_analyst_can_access_dashboard_summary(client, seeded_data):
    response = await client.get("/api/dashboard/summary", headers=auth_headers("analyst"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_income"] == "5800.00"
    assert payload["total_expenses"] == "1500.00"
    assert payload["net_balance"] == "4300.00"
    assert [item["period"] for item in payload["monthly_trends"]] == ["2026-01", "2026-02"]
    assert [item["id"] for item in payload["recent_activity"]] == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_dashboard_summary_supports_date_filters(client, seeded_data):
    response = await client.get(
        "/api/dashboard/summary?start_date=2026-02-01&end_date=2026-02-28",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_income"] == "800.00"
    assert payload["total_expenses"] == "1200.00"
    assert payload["net_balance"] == "-400.00"
    assert [item["category"] for item in payload["category_breakdown"]] == ["Rent", "Freelance"]
