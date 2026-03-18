# CLAUDE.md — Polsia AI Business Agent

## What this project is

Polsia is a self-hosted, autonomous AI platform that runs a company's operations 24/7. Ten specialized agents (Orchestrator, Business Planning, Competitor Research, Social Media, Ads, Email Outreach, Customer Support, Code Generation, Finance, Deployment) run on a Celery + Redis task queue with a FastAPI backend and Next.js dashboard. Agents call the Claude Code CLI as a subprocess — no Anthropic API key is used.

## Running tests

**Unit tests** (no Docker, no Claude credentials needed):
```bash
cd backend
CLAUDE_CLI_MOCK=true python -m pytest tests/unit/ -v
```

**With coverage:**
```bash
CLAUDE_CLI_MOCK=true python -m pytest tests/unit/ --cov=app --cov-report=term-missing
```

**Frontend unit tests:**
```bash
cd frontend
npm test -- --watchAll=false
```

**Integration tests** (testcontainers spins up Postgres + Redis automatically):
```bash
cd backend
CLAUDE_CLI_MOCK=true python -m pytest tests/integration/ -v -m integration
```

## Key development commands

```bash
make up          # Start all Docker services
make down        # Stop
make migrate     # Run Alembic migrations
make seed        # Seed company config
make init-db     # migrate + seed
make lint        # ruff + mypy + eslint
make test        # unit + integration (via Docker)
```

## Architecture in one paragraph

FastAPI (async, Python 3.11) serves the REST API and WebSocket. Celery workers pull tasks from Redis and run agents. Each agent inherits `BasePolsiaAgent` and calls `claude -p "..." --output-format json` as a subprocess. Results are written to PostgreSQL (SQLAlchemy async ORM, 16 tables) and semantic insights are dual-written to ChromaDB. Redis pub/sub broadcasts activity events to the WebSocket, which the Next.js dashboard consumes in real-time. `CLAUDE_CLI_MOCK=true` makes all agents return a stub response — used in all tests and CI.

## Critical env vars for development

```bash
CLAUDE_CLI_MOCK=true         # Always set this in tests — skips real CLI subprocess
SANDBOX_MODE=true            # Prevents real API calls (Twitter, Stripe, Render, etc.)
API_KEY=dev-key              # X-API-Key header for dashboard API
DATABASE_URL=sqlite+aiosqlite:///:memory:  # Unit tests use SQLite; integration tests use testcontainers
```

## Test fixtures (backend/tests/conftest.py)

| Fixture | What it does |
|---|---|
| `mock_claude_cli` (autouse) | Sets `CLAUDE_CLI_MOCK=true` — no real CLI calls ever in tests |
| `async_db_session` | SQLite in-memory DB with full schema; no Postgres needed |
| `mock_redis` | Patches `get_redis` with AsyncMock; prevents real Redis connections |
| `mock_chroma` | Patches `get_collection` in both `chroma_client` and `memory_service` namespaces |
| `api_client` | HTTPX AsyncClient wired to FastAPI with DB + auth overrides |
| `auth_headers` | `{"X-API-Key": "test-key"}` |

## SQLite compatibility notes

All ORM models use `JSON` instead of `JSONB` or `ARRAY(String)` — this makes them work with SQLite in unit tests and PostgreSQL in production. Do not use PostgreSQL-specific dialect types in models.

## Model imports

`backend/app/models/__init__.py` imports all models so Alembic can discover them. If you add a new model, import it there and in the `0001_initial_schema.py` migration (or create a new migration).

## Adding a new agent

1. Create `backend/app/agents/<name>/agent.py` with a class inheriting `BasePolsiaAgent`
2. Add `"<name>": ("app.agents.<name>.agent", "<ClassName>")` to `AGENT_MAP` in `crew_factory.py`
3. Add the agent type string to `VALID_AGENT_TYPES` in `task_service.py`
4. Add a Beat schedule entry in `celery_app/beat_schedule.py` if it needs periodic runs
5. Write unit tests in `tests/unit/test_<name>_agent.py`

## Adding a new API endpoint

1. Create `backend/app/api/v1/<name>.py`
2. Register the router in `backend/app/main.py`
3. Write tests in `tests/unit/api/test_<name>.py` using the `api_client` fixture

## Database migrations

```bash
# Create a new migration (inside the backend container or with the right DATABASE_URL):
alembic revision --autogenerate -m "add deployments table"
alembic upgrade head
```

Always add the new model to `models/__init__.py` before generating the migration.

## What CLAUDE_CLI_MOCK does

In `base_agent.py`, if `os.getenv("CLAUDE_CLI_MOCK")` is truthy, `call_claude()` returns the value of `CLAUDE_CLI_MOCK_RESPONSE` (defaults to `{"result": "Mock Claude response for testing"}`) instead of spawning a subprocess. This is set via `autouse` fixture in all tests and via env var in CI.

## CI environment

Three GitHub Actions workflows:
- `ci.yml` — lint + unit tests on every PR (no Docker, `CLAUDE_CLI_MOCK=true`)
- `integration.yml` — integration + E2E tests on push to main (testcontainers + full Docker stack)
- `docker-build.yml` — build all images + health-check smoke test on push to main

No Claude credentials are needed in CI. The `CLAUDE_CLI_MOCK=true` env var is set in `docker-compose.ci.yml` and in the workflow env blocks.

## Common pitfalls

- **Don't use `JSONB` or `ARRAY` in models** — use `JSON` for SQLite compatibility
- **Don't import `chromadb` or `asyncpg` at module level** — both are lazy-imported inside functions so unit tests can import models without these packages installed
- **Don't call `await db.commit()` in API handlers** — `get_db()` auto-commits on successful yield; call `await db.flush()` + `await db.refresh(obj)` if you need the server-generated `updated_at` before returning
- **Always patch where the name is used, not where it's defined** — e.g. patch `app.services.memory_service.get_collection`, not `app.core.chroma_client.get_collection`
