"""Test report_service — daily report lifecycle."""
import pytest
from datetime import date

from app.services.report_service import (
    get_daily_report,
    get_or_create_daily_report,
    save_evening_summary,
    save_morning_plan,
)


@pytest.mark.asyncio
async def test_get_or_create_creates_new(async_db_session):
    today = date.today()
    report = await get_or_create_daily_report(async_db_session, today)
    assert report.id is not None
    assert report.report_date == today
    assert report.morning_plan is None


@pytest.mark.asyncio
async def test_get_or_create_is_idempotent(async_db_session):
    today = date.today()
    r1 = await get_or_create_daily_report(async_db_session, today)
    await async_db_session.commit()
    r2 = await get_or_create_daily_report(async_db_session, today)
    assert r1.id == r2.id


@pytest.mark.asyncio
async def test_save_morning_plan(async_db_session):
    today = date.today()
    report = await save_morning_plan(async_db_session, today, "Focus on outreach", tasks_planned=5)
    await async_db_session.commit()

    assert report.morning_plan == "Focus on outreach"
    assert report.tasks_planned == 5


@pytest.mark.asyncio
async def test_save_evening_summary(async_db_session):
    today = date.today()
    report = await save_evening_summary(
        async_db_session,
        today,
        summary="Good day overall",
        insights=["Referral traffic up 20%", "Support load low"],
        tasks_completed=4,
        tasks_failed=1,
        metrics_snapshot={"mrr": 5000},
    )
    await async_db_session.commit()

    assert report.evening_summary == "Good day overall"
    assert report.tasks_completed == 4
    assert report.tasks_failed == 1
    assert report.insights == ["Referral traffic up 20%", "Support load low"]
    assert report.metrics_snapshot["mrr"] == 5000


@pytest.mark.asyncio
async def test_get_daily_report_none_when_missing(async_db_session):
    from datetime import timedelta
    future = date.today().replace(year=2099)
    result = await get_daily_report(async_db_session, future)
    assert result is None


@pytest.mark.asyncio
async def test_get_daily_report_returns_existing(async_db_session):
    today = date.today()
    await save_morning_plan(async_db_session, today, "Plan for today", tasks_planned=3)
    await async_db_session.commit()

    result = await get_daily_report(async_db_session, today)
    assert result is not None
    assert result.morning_plan == "Plan for today"
