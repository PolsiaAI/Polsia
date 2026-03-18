"""Root conftest — shared fixtures for all unit tests."""
import json
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from unittest.mock import AsyncMock, MagicMock


# ─── Claude CLI mock (autouse — always active in unit tests) ──────────────────

@pytest.fixture(autouse=True)
def mock_claude_cli(monkeypatch):
    """Prevent any real claude CLI calls in unit tests."""
    monkeypatch.setenv("CLAUDE_CLI_MOCK", "true")
    monkeypatch.setenv(
        "CLAUDE_CLI_MOCK_RESPONSE",
        json.dumps({"result": "Mock Claude response for testing"}),
    )


# ─── In-memory SQLite database ────────────────────────────────────────────────

@pytest_asyncio.fixture
async def async_db_session():
    """SQLite in-memory async session — no Postgres required for unit tests."""
    from app.core.database import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        # SQLite doesn't support ARRAY — create tables via raw SQL for models that use it
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    await engine.dispose()


# ─── Mock Redis ───────────────────────────────────────────────────────────────

@pytest.fixture
def mock_redis(mocker):
    mock = AsyncMock()
    mock.publish = AsyncMock(return_value=1)
    mocker.patch("app.core.redis_client.get_redis", return_value=mock)
    mocker.patch("app.core.events.get_redis", return_value=mock)
    return mock


# ─── Mock ChromaDB ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_chroma(mocker):
    collection = MagicMock()
    collection.add = MagicMock()
    collection.query = MagicMock(return_value={
        "documents": [["Mock memory content"]],
        "metadatas": [[{"category": "strategy", "title": "Test", "source": "test"}]],
        "ids": [["mock-id-1"]],
        "distances": [[0.1]],
    })
    mocker.patch("app.core.chroma_client.get_collection", return_value=collection)
    mocker.patch("app.services.memory_service.get_collection", return_value=collection)
    return collection


# ─── FastAPI test client ──────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def api_client(async_db_session, mock_redis):
    from app.main import app
    from app.core.database import get_db
    from app.config import settings

    # Override DB dependency
    app.dependency_overrides[get_db] = lambda: async_db_session
    # Override API key check
    settings.api_key = "test-key"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ─── Auth header helper ───────────────────────────────────────────────────────

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}
