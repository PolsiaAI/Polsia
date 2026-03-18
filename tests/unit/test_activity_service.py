"""Test activity_service — logging and Redis broadcast."""
import pytest

from app.services.activity_service import get_recent_activity, log_activity


@pytest.mark.asyncio
async def test_log_activity_creates_record(async_db_session, mock_redis):
    entry = await log_activity(
        async_db_session,
        agent_type="social_media",
        action="post_tweet",
        summary="Posted a tweet about our product",
        level="success",
    )
    await async_db_session.commit()

    assert entry.id is not None
    assert entry.agent_type == "social_media"
    assert entry.level == "success"


@pytest.mark.asyncio
async def test_log_activity_publishes_to_redis(async_db_session, mock_redis):
    await log_activity(
        async_db_session,
        agent_type="finance",
        action="revenue_snapshot",
        summary="Saved daily revenue snapshot",
    )
    mock_redis.publish.assert_called_once()
    call_args = mock_redis.publish.call_args
    assert "polsia:activity" in call_args[0]


@pytest.mark.asyncio
async def test_get_recent_activity_returns_ordered(async_db_session, mock_redis):
    await log_activity(async_db_session, agent_type="a", action="x", summary="First")
    await log_activity(async_db_session, agent_type="b", action="y", summary="Second")
    await async_db_session.commit()

    results = await get_recent_activity(async_db_session, limit=10)
    assert len(results) == 2
    # Most recent first
    assert results[0].summary == "Second"
