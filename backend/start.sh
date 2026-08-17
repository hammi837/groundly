#!/bin/sh
set -e
# Hardcode 8000 to match Railway public domain target port.
PORT="${PORT:-8000}"
echo "Groundly starting… PORT=${PORT}"
alembic upgrade head
echo "Migrations OK — starting uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
