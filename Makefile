.PHONY: up down build logs shell-backend migrate seed test lint

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

shell-backend:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec backend python scripts/seed_company.py

init-db: migrate seed

test-unit:
	docker-compose exec backend pytest tests/unit/ -v --cov=app --cov-report=term-missing

test-integration:
	docker-compose exec backend pytest tests/integration/ -v -m integration

test: test-unit test-integration

lint-backend:
	docker-compose exec backend ruff check app/
	docker-compose exec backend mypy app/

lint-frontend:
	docker-compose exec frontend npm run lint

lint: lint-backend lint-frontend

e2e:
	cd e2e && npx playwright test

reset-db:
	docker-compose exec backend alembic downgrade base
	docker-compose exec backend alembic upgrade head
	$(MAKE) seed
