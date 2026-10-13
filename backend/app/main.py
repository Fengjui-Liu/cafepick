import logging
import os
import threading
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.models import cafe as _cafe_model, sync_state as _sync_state_model  # noqa: F401  register tables
from app.routes import cafes, areas, recommend as recommend_route
from app.services import mrt, nomad_store

log = logging.getLogger("cafepick")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CaféPick API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_PLACES_HINTS = {
    "API_KEY_HTTP_REFERRER_BLOCKED": "後端用的金鑰被設了「網站（HTTP 參照網址）限制」，伺服器呼叫會被擋。backend/.env 請用沒有網站限制的金鑰。",
    "API_KEY_INVALID": "GOOGLE_MAPS_API_KEY 無效，請確認 backend/.env 的金鑰沒有貼錯。",
    "SERVICE_DISABLED": "這個 Google 專案還沒啟用 Places API (New)。",
    "BILLING_DISABLED": "這個 Google 專案還沒綁定帳單帳戶。",
    "API_KEY_SERVICE_BLOCKED": "金鑰的「API 限制」沒有勾選 Places API (New)。",
}


@app.exception_handler(RuntimeError)
def places_error(_request: Request, exc: RuntimeError):
    """Turn Google Places failures into a message the UI can show."""
    message = str(exc)
    hint = next((h for code, h in _PLACES_HINTS.items() if code in message), None)
    if "GOOGLE_MAPS_API_KEY is not set" in message:
        hint = "後端讀不到 GOOGLE_MAPS_API_KEY，請確認 backend/.env 存在且有填金鑰。"
    log.warning("Request failed: %s", message)
    detail = f"{hint}（{message[:300]}）" if hint else message[:500]
    return JSONResponse(status_code=502, content={"detail": detail})


app.include_router(cafes.router, prefix="/api")
app.include_router(areas.router, prefix="/api")
app.include_router(recommend_route.router, prefix="/api")


def _refresh_local_data() -> None:
    """Bring the local data up to date without blocking requests."""
    try:
        nomad_store.sync()
    except Exception as exc:  # network down, API changed, …: keep serving
        log.warning("Cafe Nomad sync failed: %s", exc)

    if not mrt.has_station_table() and os.getenv("GOOGLE_MAPS_API_KEY"):
        try:
            from app.services.mrt_builder import build

            failed = build()
            if failed:
                log.warning("MRT stations not geocoded: %s", "、".join(failed))
        except Exception as exc:
            log.warning("Building MRT station table failed: %s", exc)


@app.on_event("startup")
def start_background_refresh() -> None:
    if os.getenv("CAFEPICK_SKIP_REFRESH"):
        return
    threading.Thread(target=_refresh_local_data, daemon=True).start()


@app.get("/")
def root():
    return {"message": "CaféPick API is running"}


@app.get("/api/status")
def status():
    """What local data the recommender currently has."""
    db = SessionLocal()
    try:
        synced = nomad_store.last_synced(db)
    finally:
        db.close()
    return {
        "nomad_cafes": nomad_store.count(),
        "nomad_synced_at": synced.isoformat() if isinstance(synced, datetime) else None,
        "mrt_stations": len(mrt.load_stations()),
    }
