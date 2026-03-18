"""Test POST /api/v1/agents/{type}/trigger and GET /api/v1/agents/status."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_trigger_valid_agent(api_client, auth_headers):
    with patch("celery_app.tasks.agent_tasks.run_agent_task.delay"):
        resp = await api_client.post(
            "/api/v1/agents/social_media/trigger",
            headers=auth_headers,
            json={"task_title": "Post about new feature"},
        )
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "queued"
    assert data["task_id"] is not None


@pytest.mark.asyncio
async def test_trigger_invalid_agent(api_client, auth_headers):
    resp = await api_client.post(
        "/api/v1/agents/nonexistent/trigger",
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_trigger_requires_auth(api_client):
    resp = await api_client.post("/api/v1/agents/social_media/trigger")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_agent_status(api_client, auth_headers):
    resp = await api_client.get("/api/v1/agents/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 9  # All 9 agent types
    agent_types = [a["agent_type"] for a in data]
    assert "social_media" in agent_types
    assert "finance" in agent_types
