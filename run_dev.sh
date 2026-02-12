#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_LOG="$ROOT_DIR/backend/.uvicorn.log"
BACKEND_PID=""

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

if [[ ! -f "$BACKEND_DIR/.env" ]]; then
  echo "Missing $BACKEND_DIR/.env"
  echo "Please add GOOGLE_MAPS_API_KEY in backend/.env first."
  exit 1
fi

if [[ ! -f "$FRONTEND_DIR/.env" ]]; then
  echo "Missing $FRONTEND_DIR/.env"
  echo "Please add VITE_GOOGLE_MAPS_API_KEY and VITE_API_URL in frontend/.env first."
  exit 1
fi

cd "$BACKEND_DIR"
if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi
python3 -m uvicorn app.main:app --reload --port 8000 >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
sleep 2

if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "Backend failed to start. Log:"
  tail -n 80 "$BACKEND_LOG" || true
  exit 1
fi

echo "Backend running: http://127.0.0.1:8000"
echo "Frontend starting..."

cd "$FRONTEND_DIR"
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run dev
