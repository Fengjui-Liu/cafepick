import logging
import os
import threading
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.models import cafe as _cafe_model, sync_state as _sync_state_model  # noqa: F401  register tables
from app.routes import cafes, areas
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

app.include_router(cafes.router, prefix="/api")
app.include_router(areas.router, prefix="/api")


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
