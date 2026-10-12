"""
Nearest MRT / light-rail station lookup from a local table.

The table lives in backend/data/mrt_stations.json and is generated once by
scripts/build_mrt_stations.py. Looking stations up locally replaces the old
per-cafe Google Places call.
"""

import json
import os
from typing import Dict, List, Optional

from app.services.geo import haversine_km, walk_minutes

STATIONS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "mrt_stations.json"
)

# Beyond this, "nearest MRT" isn't useful information for the user.
MAX_DISTANCE_KM = 3.0

_stations: Optional[List[Dict]] = None


def load_stations() -> List[Dict]:
    global _stations
    if _stations is None:
        try:
            with open(STATIONS_PATH, encoding="utf-8") as f:
                _stations = json.load(f)
        except FileNotFoundError:
            _stations = []
    return _stations


def reload_stations() -> None:
    global _stations
    _stations = None


def has_station_table() -> bool:
    return os.path.exists(STATIONS_PATH)


def nearest_station(lat: float, lng: float) -> Optional[Dict]:
    """Return {name, lines, distance_km, walk_minutes} or None."""
    best = None
    best_km = MAX_DISTANCE_KM
    for station in load_stations():
        km = haversine_km(lat, lng, station["latitude"], station["longitude"])
        if km <= best_km:
            best, best_km = station, km
    if best is None:
        return None
    return {
        "name": best["name"],
        "lines": best.get("lines", []),
        "distance_km": round(best_km, 2),
        "walk_minutes": walk_minutes(best_km),
    }


def find_stations(query: str) -> List[Dict]:
    """Stations whose name contains the query (e.g. '忠孝' → 忠孝復興, 忠孝新生…)."""
    q = query.replace("捷運", "").replace("站", "").strip()
    if not q:
        return []
    return [s for s in load_stations() if q in s["name"]]
