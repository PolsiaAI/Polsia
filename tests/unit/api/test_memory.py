"""Test GET/POST /api/v1/memory endpoints."""
import pytest


@pytest.mark.asyncio
async def test_create_memory(api_client, auth_headers, mock_chroma):
    resp = await api_client.post(
        "/api/v1/memory",
        headers=auth_headers,
        json={
            "category": "strategy",
            "title": "Key insight",
            "content": "Referrals convert 3x better than paid",
            "tags": ["referral", "conversion"],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Key insight"
    assert data["category"] == "strategy"


@pytest.mark.asyncio
async def test_search_memory(api_client, auth_headers, mock_chroma):
    resp = await api_client.get(
        "/api/v1/memory?q=referral+conversion",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_memory_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/memory", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
