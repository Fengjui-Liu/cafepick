"""
Local copy of Cafe Nomad data.

Cafe Nomad's "taipei" dataset covers both Taipei and New Taipei. We sync it
into SQLite at most once a day and keep an in-memory grid index so matching a
Google result against it is a dictionary lookup, not a scan.
"""

import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import httpx

from app.database import SessionLocal
from app.models.cafe import Cafe
from app.models.sync_state import SyncState
from app.services.cafenomad import CAFENOMAD_API, _map_fields
from app.services.geo import haversine_km

log = logging.getLogger(__name__)

NOMAD_CITY = "taipei"
SOURCE_KEY = f"cafenomad:{NOMAD_CITY}"
MAX_AGE = timedelta(hours=24)

# ~1.1 km × 1.0 km grid cells at Taipei's latitude.
_CELL = 0.01
_index: Optional[Dict[Tuple[int, int], List[dict]]] = None

_CAFE_COLUMNS = {c.name for c in Cafe.__table__.columns}


def _cell(lat: float, lng: float) -> Tuple[int, int]:
    return (math.floor(lat / _CELL), math.floor(lng / _CELL))


def last_synced(db) -> Optional[datetime]:
    state = db.get(SyncState, SOURCE_KEY)
    return state.synced_at if state else None


def is_stale() -> bool:
    db = SessionLocal()
    try:
        synced = last_synced(db)
    finally:
        db.close()
    return synced is None or datetime.utcnow() - synced > MAX_AGE


def fetch_raw() -> List[dict]:
    resp = httpx.get(f"{CAFENOMAD_API}/{NOMAD_CITY}", timeout=60)
    resp.raise_for_status()
    return resp.json()


def save(items: List[dict]) -> int:
    """Upsert Cafe Nomad API items into the DB. Returns the number saved."""
    db = SessionLocal()
    try:
        count = 0
        for item in items:
            fields = _map_fields(item, NOMAD_CITY)
            if not fields.get("id"):
                continue
            fields = {k: v for k, v in fields.items() if k in _CAFE_COLUMNS}
            db.merge(Cafe(**fields))
            count += 1
        db.merge(SyncState(source=SOURCE_KEY, synced_at=datetime.utcnow(), row_count=count))
        db.commit()
    finally:
        db.close()
    invalidate_index()
    return count


def sync(force: bool = False) -> Optional[int]:
    """Refresh from the Cafe Nomad API if stale. Returns rows saved, or None if skipped."""
    if not force and not is_stale():
        return None
    count = save(fetch_raw())
    log.info("Synced %d cafes from Cafe Nomad", count)
    return count


def invalidate_index() -> None:
    global _index
    _index = None


def _load_index() -> Dict[Tuple[int, int], List[dict]]:
    global _index
    if _index is None:
        db = SessionLocal()
        try:
            rows = (
                db.query(Cafe)
                .filter(Cafe.city == NOMAD_CITY, ~Cafe.id.startswith("demo-"))
                .all()
            )
            index: Dict[Tuple[int, int], List[dict]] = defaultdict(list)
            for row in rows:
                if not row.latitude or not row.longitude:
                    continue
                cafe = {c: getattr(row, c) for c in _CAFE_COLUMNS}
                index[_cell(row.latitude, row.longitude)].append(cafe)
            _index = dict(index)
        finally:
            db.close()
    return _index


def nearby(lat: float, lng: float, radius_km: float) -> List[Tuple[float, dict]]:
    """Nomad cafes within radius_km, as (distance_km, cafe), closest first."""
    index = _load_index()
    ci, cj = _cell(lat, lng)
    span = math.ceil(radius_km)  # a cell is ≥1 km on each side at Taipei's latitude
    found = []
    for di in range(-span, span + 1):
        for dj in range(-span, span + 1):
            for cafe in index.get((ci + di, cj + dj), []):
                km = haversine_km(lat, lng, cafe["latitude"], cafe["longitude"])
                if km <= radius_km:
                    found.append((km, cafe))
    found.sort(key=lambda pair: pair[0])
    return found


def count() -> int:
    return sum(len(v) for v in _load_index().values())
