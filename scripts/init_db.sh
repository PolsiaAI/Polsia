#!/usr/bin/env bash
set -euo pipefail

echo "Running Alembic migrations..."
cd /app
alembic upgrade head

echo "Seeding default company config..."
python scripts/seed_company.py

echo "Database initialized successfully."
