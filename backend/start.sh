#!/bin/sh
set -e
echo "Groundly starting… PORT=${PORT:-8000}"
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
