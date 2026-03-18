"""Test Celery agent task dispatch (without real broker)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_crew_factory_returns_result():
    """Test that crew_factory.run_agent_for_task dispatches correctly."""
    from app.agents.crew_factory import run_agent_for_task

    with patch("app.agents.social_media.agent.SocialMediaAgent.run") as mock_run:
        mock_run.return_value = {"summary": "Mocked result", "tweets": []}
        result = run_agent_for_task(
            "social_media",
            {"title": "Post tweets", "description": None},
            {"company": {"name": "Test Co"}},
        )
    assert result["summary"] == "Mocked result"


def test_crew_factory_raises_on_unknown_agent():
    from app.agents.crew_factory import run_agent_for_task
    with pytest.raises(ValueError, match="Unknown agent"):
        run_agent_for_task("nonexistent_agent", {}, {})
