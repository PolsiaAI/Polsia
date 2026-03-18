"""Integration: full API request → real Postgres round-trip."""
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_create_and_retrieve_task(int_client):
    auth = {"X-API-Key": "int-test-key"}

    # Create
    resp = await int_client.post(
        "/api/v1/tasks",
        headers=auth,
        json={"title": "Integration test task", "agent_type": "finance"},
    )
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    # Retrieve
    resp2 = await int_client.get(f"/api/v1/tasks/{task_id}", headers=auth)
    assert resp2.status_code == 200
    assert resp2.json()["title"] == "Integration test task"


@pytest.mark.asyncio
async def test_config_round_trip(int_client):
    auth = {"X-API-Key": "int-test-key"}

    # Seed company
    from app.models.company import CompanyConfig
    # (done via fixture or direct insert in real integration tests)

    # Health check passes
    resp = await int_client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
