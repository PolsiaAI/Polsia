"""Test GET /api/v1/dashboard/* endpoints."""
import pytest

from app.models.company import CompanyConfig


@pytest.mark.asyncio
async def test_get_summary(api_client, auth_headers, async_db_session):
    company = CompanyConfig(name="Test Co", kpis={"mrr_usd": 5000}, timezone="UTC", daily_cycle_hour=6)
    async_db_session.add(company)
    await async_db_session.commit()

    resp = await api_client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "tasks_today_total" in data
    assert data["kpis"]["mrr_usd"] == 5000


@pytest.mark.asyncio
async def test_get_activity_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/dashboard/activity", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_daily_report_none(api_client, auth_headers):
    resp = await api_client.get("/api/v1/dashboard/reports/daily", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() is None


@pytest.mark.asyncio
async def test_health_endpoint(api_client):
    resp = await api_client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
