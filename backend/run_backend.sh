#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if [ -z "${GOOGLE_MAPS_API_KEY:-}" ]; then
  echo "ERROR: GOOGLE_MAPS_API_KEY is not set."
  echo "Please set it in backend/.env:"
  echo "GOOGLE_MAPS_API_KEY=your_api_key"
  exit 1
fi
GOOGLE_MAPS_API_KEY=AIzaSyAj7IAlnzOAyjc33C4c-cOSvQYAh0Vc4Ww
python3 -m uvicorn app.main:app --reload --port 8000
