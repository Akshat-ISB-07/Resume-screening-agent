#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"
exec "$ROOT/.venv/bin/uvicorn" main:app --reload --port 8000
