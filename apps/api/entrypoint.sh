#!/bin/sh
set -e

echo "=== Aplicando migrations (alembic upgrade head) ==="
alembic upgrade head

echo "=== Iniciando API (uvicorn) ==="
exec uvicorn metaway_api.main:app --host 0.0.0.0 --port 8000
