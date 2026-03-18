"""Test GET /api/v1/social/posts endpoint."""
import pytest


@pytest.mark.asyncio
async def test_get_posts_empty(api_client, auth_headers):
    resp = await api_client.get("/api/v1/social/posts", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_posts_returns_list(api_client, auth_headers, async_db_session):
    from app.models.social import SocialPost

    async_db_session.add(SocialPost(platform="twitter", content="Hello world!", status="published"))
    async_db_session.add(SocialPost(platform="twitter", content="Draft post", status="draft"))
    await async_db_session.commit()

    resp = await api_client.get("/api/v1/social/posts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_posts_filter_by_status(api_client, auth_headers, async_db_session):
    from app.models.social import SocialPost

    async_db_session.add(SocialPost(platform="twitter", content="Published!", status="published"))
    async_db_session.add(SocialPost(platform="twitter", content="Still drafting", status="draft"))
    await async_db_session.commit()

    resp = await api_client.get("/api/v1/social/posts?status=published", headers=auth_headers)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "published"
    assert data[0]["content"] == "Published!"


@pytest.mark.asyncio
async def test_get_posts_requires_auth(api_client):
    resp = await api_client.get("/api/v1/social/posts")
    assert resp.status_code == 401
