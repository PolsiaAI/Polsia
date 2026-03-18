"""Integration test conftest — real Postgres + Redis via testcontainers."""
import json
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


@pytest.fixture(autouse=True)
def mock_claude_cli(monkeypatch):
    monkeypatch.setenv("CLAUDE_CLI_MOCK", "true")
    monkeypatch.setenv("CLAUDE_CLI_MOCK_RESPONSE", json.dumps({"result": "integration mock"}))


@pytest.fixture(scope="session")
def postgres_url():
    """Spin up a real Postgres container for the test session."""
    try:
        from testcontainers.postgres import PostgresContainer
        with PostgresContainer("postgres:16-alpine") as pg:
            url = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://")
            yield url
    except ImportError:
        pytest.skip("testcontainers not installed")


@pytest.fixture(scope="session")
def redis_url():
    """Spin up a real Redis container for the test session."""
    try:
        from testcontainers.redis import RedisContainer
        with RedisContainer("redis:7-alpine") as redis:
            yield f"redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}/0"
    except ImportError:
        pytest.skip("testcontainers not installed")


@pytest_asyncio.fixture(scope="session")
async def integration_db(postgres_url):
    """Create all tables and return async session factory."""
    from app.core.database import Base
    import app.models  # noqa — ensure all models registered

    engine = create_async_engine(postgres_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield Session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(integration_db):
    async with integration_db() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def int_client(db, redis_url, monkeypatch):
    """FastAPI client connected to real Postgres + Redis."""
    from app.main import app
    from app.core.database import get_db
    from app.config import settings

    monkeypatch.setattr(settings, "redis_url", redis_url)
    monkeypatch.setattr(settings, "api_key", "int-test-key")

    app.dependency_overrides[get_db] = lambda: db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
