"""Test GET /api/v1/finance/* endpoints."""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_finance_summary_empty(api_client, auth_headers):
    """Returns zero values when no snapshot exists."""
    resp = await api_client.get("/api/v1/finance/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mrr_cents"] == 0
    assert data["arr_cents"] == 0
    assert data["active_subscribers"] == 0
    assert data["last_snapshot_date"] is None


@pytest.mark.asyncio
async def test_finance_summary_with_snapshot(api_client, auth_headers, async_db_session):
    """Returns values from the latest revenue snapshot."""
    from app.models.finance import RevenueSnapshot

    snap = RevenueSnapshot(
        snapshot_date=date.today(),
        mrr_cents=500000,
        arr_cents=6000000,
        active_subscribers=42,
        stripe_balance_cents=150000,
    )
    async_db_session.add(snap)
    await async_db_session.commit()

    resp = await api_client.get("/api/v1/finance/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mrr_cents"] == 500000
    assert data["arr_cents"] == 6000000
    assert data["active_subscribers"] == 42


@pytest.mark.asyncio
async def test_finance_summary_requires_auth(api_client):
    resp = await api_client.get("/api/v1/finance/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_finance_revenue_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/finance/revenue", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_finance_revenue_returns_snapshots(api_client, auth_headers, async_db_session):
    from app.models.finance import RevenueSnapshot
    from datetime import timedelta

    for i in range(3):
        snap = RevenueSnapshot(
            snapshot_date=date.today() - timedelta(days=i),
            mrr_cents=100000 * (3 - i),   # today=300k, yesterday=200k, 2 days ago=100k
            arr_cents=1200000 * (3 - i),
        )
        async_db_session.add(snap)
    await async_db_session.commit()

    resp = await api_client.get("/api/v1/finance/revenue?limit=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # Most recent first
    assert data[0]["mrr_cents"] >= data[1]["mrr_cents"]


@pytest.mark.asyncio
async def test_finance_expenses_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/finance/expenses", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_finance_expenses_filter_by_category(api_client, auth_headers, async_db_session):
    from app.models.finance import ExpenseRecord

    async_db_session.add(ExpenseRecord(category="ads", vendor="Google", amount_cents=5000, currency="usd", date=date.today()))
    async_db_session.add(ExpenseRecord(category="software", vendor="GitHub", amount_cents=1000, currency="usd", date=date.today()))
    await async_db_session.commit()

    resp = await api_client.get("/api/v1/finance/expenses?category=ads", headers=auth_headers)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category"] == "ads"


@pytest.mark.asyncio
async def test_finance_stripe_events_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/finance/events", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_stripe_webhook_missing_secret(api_client):
    """Returns 500 when webhook secret is not configured."""
    from app.config import settings
    original = settings.stripe_webhook_secret
    settings.stripe_webhook_secret = ""
    try:
        resp = await api_client.post(
            "/api/v1/finance/stripe/webhook",
            content=b'{"id":"evt_test"}',
            headers={"stripe-signature": "t=1,v1=abc"},
        )
        assert resp.status_code == 500
    finally:
        settings.stripe_webhook_secret = original


@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(api_client):
    """Returns 400 on bad Stripe signature."""
    from app.config import settings
    settings.stripe_webhook_secret = "whsec_test"
    try:
        resp = await api_client.post(
            "/api/v1/finance/stripe/webhook",
            content=b'{"id":"evt_test","type":"payment_intent.succeeded"}',
            headers={"stripe-signature": "t=1,v1=badsig"},
        )
        assert resp.status_code == 400
    finally:
        settings.stripe_webhook_secret = ""
