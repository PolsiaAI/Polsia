"""Test GET/POST /api/v1/tasks endpoints."""
import pytest


@pytest.mark.asyncio
async def test_list_tasks_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_task(api_client, auth_headers):
    resp = await api_client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Research competitors",
            "agent_type": "competitor_research",
            "priority": 2,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Research competitors"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_task_by_id(api_client, auth_headers):
    create = await api_client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "My task", "agent_type": "finance"},
    )
    task_id = create.json()["id"]

    resp = await api_client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(api_client, auth_headers):
    resp = await api_client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert resp.status_code == 404
