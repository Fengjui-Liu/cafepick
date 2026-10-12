"""
Merge a Google Places cafe with what we know locally: the nearest MRT station
and, when the shop is also on Cafe Nomad, its work-friendliness ratings.
"""

from typing import Dict, Optional

from app.services import matcher, mrt

# Cafe Nomad rates these 0–5; 0 means "nobody rated it", not "terrible".
_RATED_FIELDS = ["wifi", "socket", "quiet", "seat", "tasty", "cheap", "music"]


def _rating(value) -> Optional[float]:
    return value if value else None


def _yes_no(value) -> Optional[str]:
    return value if value in ("yes", "no", "maybe") else None


def work_info(nomad: dict) -> Dict:
    info = {field: _rating(nomad.get(field)) for field in _RATED_FIELDS}
    info["limited_time"] = _yes_no(nomad.get("limited_time"))
    info["standing_desk"] = _yes_no(nomad.get("standing_desk"))
    info["open_time"] = nomad.get("open_time") or None
    return info


def enrich(cafe: Dict) -> Dict:
    cafe = dict(cafe)
    lat, lng = cafe.get("latitude"), cafe.get("longitude")
    cafe["work"] = None
    cafe["nomad"] = None
    if lat is None or lng is None:
        return cafe

    station = mrt.nearest_station(lat, lng)
    if station:
        cafe["nearest_mrt"] = station
        # Flat fields kept for the current frontend.
        cafe["mrt_station"] = station["name"]
        cafe["mrt_distance_km"] = station["distance_km"]
        cafe["mrt_walk_minutes"] = station["walk_minutes"]

    found = matcher.match_nomad(cafe.get("name", ""), lat, lng)
    if found:
        nomad, sim = found
        cafe["work"] = work_info(nomad)
        cafe["nomad"] = {
            "id": nomad["id"],
            "name": nomad["name"],
            "match_confidence": round(sim, 2),
        }
    return cafe
