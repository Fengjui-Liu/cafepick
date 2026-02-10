"""
Import cafe data from Cafe Nomad API into local SQLite database.

Usage:
    python -m scripts.import_cafenomad
    python -m scripts.import_cafenomad --city taipei
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from app.database import engine, Base, SessionLocal
from app.models.cafe import Cafe
from app.services.normalize import normalize_mrt, extract_district

CAFENOMAD_API = "https://cafenomad.tw/api/v1.2/cafes"

CITIES = [
    "taipei",
    "keelung",
    "taoyuan",
    "hsinchu",
    "miaoli",
    "taichung",
    "changhua",
    "nantou",
    "yunlin",
    "chiayi",
    "tainan",
    "kaohsiung",
    "pingtung",
    "yilan",
    "hualien",
    "taitung",
    "penghu",
    "kinmen",
    "lienchiang",
]


def fetch_cafes(city: str) -> list:
    """Fetch cafes for a city from Cafe Nomad API."""
    url = f"{CAFENOMAD_API}/{city}"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def import_city(db, city: str) -> int:
    """Import cafes for a single city. Returns count of imported cafes."""
    print(f"Fetching {city}...")
    try:
        data = fetch_cafes(city)
    except Exception as e:
        print(f"  Failed to fetch {city}: {e}")
        return 0

    count = 0
    for item in data:
        cafe_id = item.get("id")
        if not cafe_id:
            continue

        existing = db.query(Cafe).filter(Cafe.id == cafe_id).first()
        if existing:
            # Update existing record
            for key, val in _map_fields(item, city).items():
                setattr(existing, key, val)
        else:
            cafe = Cafe(id=cafe_id, **_map_fields(item, city))
            db.add(cafe)
        count += 1

    db.commit()
    print(f"  Imported {count} cafes from {city}")
    return count


def _map_fields(item: dict, city: str) -> dict:
    """Map Cafe Nomad API fields to our Cafe model."""
    address = item.get("address", "")
    return {
        "name": item.get("name", ""),
        "city": city,
        "district": extract_district(address),
        "address": address,
        "latitude": _to_float(item.get("latitude")),
        "longitude": _to_float(item.get("longitude")),
        "url": item.get("url", ""),
        "mrt": normalize_mrt(item.get("mrt", "")),
        "open_time": item.get("open_time", ""),
        "wifi": _to_float(item.get("wifi")),
        "socket": _to_float(item.get("socket")),
        "quiet": _to_float(item.get("quiet")),
        "tasty": _to_float(item.get("tasty")),
        "cheap": _to_float(item.get("cheap")),
        "music": _to_float(item.get("music")),
        "seat": _to_float(item.get("seat")),
        "limited_time": item.get("limited_time", ""),
        "standing_desk": item.get("standing_desk", ""),
        "has_reservation": "",
    }


def _to_float(val) -> float:
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if specific city was requested
    cities = CITIES
    if len(sys.argv) > 2 and sys.argv[1] == "--city":
        cities = [sys.argv[2]]

    total = 0
    for city in cities:
        total += import_city(db, city)

    db.close()
    print(f"\nDone! Total: {total} cafes imported.")


if __name__ == "__main__":
    main()
