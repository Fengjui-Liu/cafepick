"""
End-to-end recommendation: gather candidates around an origin, enrich them
with local data, and rank them for the chosen scenario.
"""

from typing import Dict, List, Optional

from app.services import nomad_store
from app.services.enrich import enrich, work_info
from app.services.geo import haversine_km, walk_minutes
from app.services.google_places import search_nearby_cafes, search_places
from app.services.ranker import rank

# How far to look, by scenario. "Just a coffee" should be really close.
SEARCH_RADIUS_M = {"quick": 700.0, "work": 1500.0, "date": 1500.0}
RANK_BY = {"quick": "DISTANCE", "work": "DISTANCE", "date": "POPULARITY"}


def _with_distance(cafe: Dict, lat: float, lng: float) -> Dict:
    if cafe.get("latitude") is None or cafe.get("longitude") is None:
        return cafe
    km = haversine_km(lat, lng, cafe["latitude"], cafe["longitude"])
    cafe["distance_km"] = round(km, 2)
    cafe["walk_minutes"] = walk_minutes(km)
    return cafe


def _nomad_only(radius_m: float, lat: float, lng: float, seen: set) -> List[Dict]:
    """
    Work-friendly shops on Cafe Nomad that Google's 20 results missed.
    Google caps a search at 20 places, which in 大安區 is a few blocks.
    """
    extra = []
    for _, nomad in nomad_store.nearby(lat, lng, radius_m / 1000):
        if nomad["id"] in seen:
            continue
        extra.append(enrich_nomad_only(nomad))
    return extra


def enrich_nomad_only(nomad: Dict) -> Dict:
    cafe = enrich(
        {
            "id": f"nomad:{nomad['id']}",
            "name": nomad["name"],
            "address": nomad.get("address") or "",
            "latitude": nomad["latitude"],
            "longitude": nomad["longitude"],
            "url": nomad.get("url") or None,
            "district": nomad.get("district") or "",
            "city": "newtaipei" if "新北" in (nomad.get("address") or "") else "taipei",
            "source": "nomad",
        },
        match_nomad=False,
    )
    cafe["work"] = work_info(nomad)
    cafe["nomad"] = {"id": nomad["id"], "name": nomad["name"], "match_confidence": 1.0}
    return cafe


def recommend(
    mode: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: str = "taipei",
    district: Optional[str] = None,
    pet: bool = False,
    max_walk_minutes: Optional[int] = None,
    exclude: Optional[set] = None,
    top_n: int = 3,
) -> Dict:
    if lat is not None and lng is not None:
        radius = SEARCH_RADIUS_M[mode]
        if max_walk_minutes:
            radius = max(radius, max_walk_minutes / 60 * 5000)
        candidates = [
            _with_distance(enrich(c), lat, lng)
            for c in search_nearby_cafes(lat, lng, radius, RANK_BY[mode])
        ]
        if mode == "work":
            seen = {c["nomad"]["id"] for c in candidates if c.get("nomad")}
            candidates += [
                _with_distance(c, lat, lng) for c in _nomad_only(radius, lat, lng, seen)
            ]
    else:
        # No origin point (only a district): text search, no walking distance.
        candidates = [enrich(c) for c in search_places(city, district, limit=20)]

    ranked = rank(candidates, mode, pet=pet, max_walk_minutes=max_walk_minutes, exclude=exclude)
    return {
        "mode": mode,
        "pool_size": len(ranked),
        "recommendations": ranked[:top_n],
        "has_more": len(ranked) > top_n,
    }
