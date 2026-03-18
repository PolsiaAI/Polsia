# Acceptance Testing Plan — Polsia AI Business Agent

## How to run all tests

```bash
# Backend unit (41+ tests, no Docker needed)
cd backend && CLAUDE_CLI_MOCK=true python -m pytest tests/unit/ -v

# Backend with coverage report
cd backend && CLAUDE_CLI_MOCK=true python -m pytest tests/unit/ --cov=app --cov-report=term-missing

# Frontend unit
cd frontend && npm test -- --watchAll=false --coverage

# Integration (testcontainers, no Docker Compose needed)
cd backend && CLAUDE_CLI_MOCK=true python -m pytest tests/integration/ -v -m integration

# E2E (requires running Docker stack)
docker-compose up -d && npx playwright test e2e/ --reporter=html
```

---

## Test coverage map

### Backend unit tests

| File | Tests | What's covered |
|---|---|---|
| `test_base_agent.py` | 4 | `call_claude()` mock, session continuity, subprocess not called when mock active |
| `test_company_service.py` | 4 | `get_full_context()`, `build_context_prompt()`, missing config returns None |
| `test_task_service.py` | 5 | Create task, get task, list tasks, update status, create/finish agent run |
| `test_activity_service.py` | 3 | Log activity → DB write, Redis publish, ordering desc by id+timestamp |
| `test_memory_service.py` | 4 | `store_memory()` PG+Chroma dual-write, `search_memory()`, `list_memories()` filter |
| `test_report_service.py` | 6 | `get_or_create()` idempotent, `save_morning_plan()`, `save_evening_summary()`, `get_daily_report()` |
| `api/test_dashboard.py` | 4 | `GET /summary`, `GET /activity`, `GET /reports/daily`, `/health` |
| `api/test_agents.py` | 4 | Trigger valid agent → 202, invalid agent → 422, no auth → 403, `GET /status` |
| `api/test_tasks.py` | 4 | List empty, create, get by id, 404 not found |
| `api/test_config.py` | 4 | Get 404 when missing, get existing, update, auth required |
| `api/test_memory.py` | 3 | List memories, semantic search, create memory |
| `api/test_finance.py` | 9 | Summary empty/with data, revenue list, expense filter, stripe events, webhook error paths |
| `api/test_social.py` | 4 | List empty, list all, filter by status, auth required |
| `celery/test_agent_tasks.py` | 2 | Celery task dispatches correct agent from AGENT_MAP |

**Total: 60 backend unit tests**

### Frontend unit tests

| File | Tests | What's covered |
|---|---|---|
| `MetricsCard.test.tsx` | 5 | Renders title/value, subtitle, loading skeleton, trend colours |
| `ActivityFeed.test.tsx` | ~5 | WS connect, events render, reconnect badge, level colours |
| `Sidebar.test.tsx` | ~3 | Nav items render, active route highlight |
| `AgentStatusGrid.test.tsx` | 7 | Loading skeleton, agent cards, task count, status badges, status colours |
| `useActivityFeed.test.ts` | 5 | Connect, events, disconnect, malformed message no-crash |
| `useAgentStatus.test.ts` | 5 | Loading state, fetch on mount, poll interval, error handling, cleanup on unmount |

### Integration tests

| File | What's covered |
|---|---|
| `test_api_db_roundtrip.py` | Full HTTP request → PostgreSQL write → read back (real Postgres via testcontainers) |

### E2E tests (Playwright)

| File | What's covered |
|---|---|
| `dashboard.spec.ts` | Dashboard loads, metrics visible, activity feed present |
| `agents.spec.ts` | Trigger agent button → task appears in list |
| `settings.spec.ts` | Update company config, verify saved |

---

## Feature acceptance criteria

### Core infrastructure

| Feature | Acceptance criteria | Test type |
|---|---|---|
| Docker stack starts | All 7 services healthy after `make up` | Manual / `docker-build.yml` CI |
| Database migrations | `make init-db` succeeds, all 16 tables present | Manual |
| Health endpoint | `GET /api/v1/health` → `{"status":"ok"}` | E2E |
| Authentication | Requests without `X-API-Key` return 403 | Unit (all API tests) |
| WebSocket | Connect to `WS /ws/activity`, receive events from agent runs | Unit + E2E |

### Agent framework

| Feature | Acceptance criteria | Test type |
|---|---|---|
| Claude CLI mock | `CLAUDE_CLI_MOCK=true` → no subprocess spawned, returns stub | Unit: `test_base_agent.py` |
| Agent dispatch | `run_agent_task(task_id)` routes to correct agent class | Unit: `test_agent_tasks.py` |
| Task lifecycle | Create → pending → in_progress → completed/failed | Unit: `test_task_service.py` |
| Activity broadcast | `log_activity()` writes to DB + publishes to Redis channel | Unit: `test_activity_service.py` |
| Morning cycle | 06:00 Beat job enqueues 5-8 tasks for the day | Integration |
| Evening cycle | 20:00 Beat job saves evening summary to `daily_reports` | Integration |

### Individual agents (all sandbox-safe)

| Agent | Acceptance criteria | Test type |
|---|---|---|
| Orchestrator | Returns valid JSON `{summary, tasks[], key_focus}` | Unit (mocked CLI) |
| Business Planning | Reads company context, returns recommendations | Unit (mocked CLI) |
| Competitor Research | Calls Tavily (mocked), returns competitor profiles | Unit (mocked CLI) |
| Social Media | Returns draft tweet content | Unit (mocked CLI) |
| Email Outreach | Returns personalized email draft | Unit (mocked CLI) |
| Customer Support | Returns reply draft for inbox item | Unit (mocked CLI) |
| Ads Management | Returns campaign recommendation | Unit (mocked CLI) |
| Code Generation | Calls PyGitHub (mocked), returns commit summary | Unit (mocked CLI) |
| Finance | Calls Stripe (mocked), returns MRR/ARR values | Unit (mocked CLI) |
| Deployment | Calls Render API (mocked), logs to `deployments` table | Unit (mocked HTTP) |

### REST API endpoints

| Endpoint | Acceptance criteria |
|---|---|
| `GET /api/v1/config` | Returns 404 if no config, 200 with company data if seeded |
| `PUT /api/v1/config` | Updates fields, returns updated object with refreshed `updated_at` |
| `POST /api/v1/agents/{type}/trigger` | Returns 202 with `task_id`, task visible in `GET /tasks` |
| `GET /api/v1/agents/status` | Returns list of all 10 agent types with last-run info |
| `GET /api/v1/tasks` | Returns paginated task list |
| `POST /api/v1/tasks` | Creates task, returns 201 |
| `GET /api/v1/memory?q=<query>` | Returns semantic search results from ChromaDB |
| `POST /api/v1/memory` | Stores to PostgreSQL + ChromaDB |
| `GET /api/v1/finance/summary` | Returns MRR, ARR, subscribers, ad spend, expenses |
| `POST /api/v1/finance/stripe/webhook` | Validates Stripe signature, logs event, returns `{"received":true}` |
| `GET /api/v1/social/posts` | Returns list of posts, filterable by status |
| `GET /api/v1/deployments` | Returns deploy history |
| `POST /api/v1/deployments/trigger` | Triggers Render deploy, returns deploy record |
| `GET /api/v1/deployments/latest` | Returns most recent deploy per service |

### Finance agent (Stripe)

| Feature | Acceptance criteria | Test type |
|---|---|---|
| Revenue snapshot | Fetches Stripe balance + subscriber count, writes `revenue_snapshots` row | Unit |
| Expense logging | Writes `expense_records` row with correct category | Unit |
| Webhook signature | Invalid signature → 400, missing secret → 500 | Unit: `test_finance.py` |
| Sandbox gate | `SANDBOX_MODE=true` prevents real Stripe refunds | Unit (env check) |

### Deployment agent (Render)

| Feature | Acceptance criteria | Test type |
|---|---|---|
| Trigger deploy | `POST /v1/services/{id}/deploys` called with correct headers | Unit (mock httpx) |
| Poll status | Polls until `live` or `failed`, updates `deployments.status` | Unit |
| Health check | `GET {health_check_url}` after deploy; marks `health_check_passed` | Unit |
| Rollback | On health check failure, calls `POST /v1/deploys/{id}/rollback` | Unit |
| Sandbox mode | No real HTTP calls when `SANDBOX_MODE=true` | Unit |
| DB record | Every deploy attempt logged to `deployments` table | Unit |

### Frontend dashboard

| Feature | Acceptance criteria | Test type |
|---|---|---|
| Metrics cards | Show MRR, ARR, tasks today, active agents | E2E: `dashboard.spec.ts` |
| Activity feed | WebSocket events appear in real-time, level-colour coded | Unit + E2E |
| Agent status grid | All 10 agents shown with last-run status badge | Unit: `AgentStatusGrid.test.tsx` |
| Agent trigger | Button click → 202 → task appears in task list | E2E: `agents.spec.ts` |
| Settings save | Update company name → `PUT /config` → success toast | E2E: `settings.spec.ts` |
| Deploy page | Deploy history table, trigger button per service | E2E (to be added) |
| Memory search | Type query → semantic results appear | E2E (to be added) |

---

## Coverage targets

| Scope | Current | Target |
|---|---|---|
| `backend/app/services/` | ~85% | 85% |
| `backend/app/agents/` | ~75% | 75% |
| `backend/app/api/` | ~80% | 80% |
| `frontend/src/components/` | ~70% | 70% |
| `frontend/src/hooks/` | ~80% | 80% |

---

## Gaps to address before production

### Missing unit tests (to write when agents are implemented)
- `tests/unit/test_deployment_agent.py` — mock Render HTTP calls with `respx` or `httpx`
- `tests/unit/api/test_deployments.py` — GET/POST deployment endpoints
- `tests/unit/test_social_media_agent.py` — mock Tweepy
- `tests/unit/test_finance_agent.py` — mock Stripe SDK

### Missing E2E specs
- `e2e/finance.spec.ts` — Finance page loads MRR/ARR, expense table visible
- `e2e/deployments.spec.ts` — Deploy page shows history, trigger button works
- `e2e/memory.spec.ts` — Search returns results, add memory entry

### Manual acceptance checklist (run before first real deployment)

- [ ] `SANDBOX_MODE=false` + real Stripe keys → Stripe balance loads in Finance page
- [ ] `SANDBOX_MODE=false` + real Render keys → trigger deploy from dashboard → Render dashboard shows active deploy
- [ ] Morning cycle runs at 06:00 UTC → tasks visible in dashboard
- [ ] Agent trigger → Celery worker picks up task → activity feed updates via WebSocket
- [ ] Claude CLI authenticated (`claude login` on host) → agent runs real inference
- [ ] Stripe webhook received → event appears in `/finance/events`
