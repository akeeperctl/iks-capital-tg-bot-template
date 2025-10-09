#!/bin/bash

set -e

sleep 15
source /app/.venv/bin/activate
uv sync --dev

alembic upgrade head
pytest tests/ -v --tb=short
