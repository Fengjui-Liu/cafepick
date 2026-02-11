from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.google_places import (
    search_places,
    search_places_near,
    find_nearest_mrt,
    search_transit_points,
    has_cafes_near_transit,
)

router = APIRouter(tags=["cafes"])


def _walk_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    # Keep this route independent from private service helpers.
    from math import radians, sin, cos, atan2, sqrt

    earth_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return earth_km * 2 * atan2(sqrt(a), sqrt(1 - a))


@router.get("/cafes")
def get_cafes(
    city: Optional[str] = None,
    district: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    if not city:
        return {"total": 0, "cafes": []}

    keyword = query or district
    cafes = search_places(city, keyword, limit=limit + offset)
    total = len(cafes)
    cafes = cafes[offset : offset + limit]

    return {"total": total, "cafes": cafes}


@router.get("/cafes/recommend")
def get_recommendations(
    city: str = "taipei",
    district: Optional[str] = None,
    query: Optional[str] = None,
    transit_lat: Optional[float] = None,
    transit_lng: Optional[float] = None,
    transit_name: Optional[str] = None,
    max_walk_minutes: Optional[int] = Query(None, ge=1, le=60),
    top_n: int = Query(5, ge=1, le=10),
):
    keyword = query or district
    if transit_lat is not None and transit_lng is not None:
        cafes = search_places_near(
            city=city,
            latitude=transit_lat,
            longitude=transit_lng,
            district=keyword,
            limit=min(max(top_n * 3, top_n), 20),
        )
    else:
        cafes = search_places(city, keyword, limit=top_n)

    if query:
        q = query.strip().lower()
        cafes.sort(
            key=lambda c: 0 if q and q in (c.get("name") or "").lower() else 1
        )
    enriched = []
    for cafe in cafes:
        if cafe.get("latitude") and cafe.get("longitude"):
            if transit_lat is not None and transit_lng is not None and transit_name:
                dist = _walk_distance_km(
                    cafe["latitude"], cafe["longitude"], transit_lat, transit_lng
                )
                walk_minutes = int(round((dist / 5) * 60))
                if max_walk_minutes is not None and walk_minutes > max_walk_minutes:
                    continue
                cafe = dict(cafe)
                cafe["transit_name"] = transit_name
                cafe["transit_distance_km"] = round(dist, 2)
                cafe["transit_walk_minutes"] = walk_minutes
            else:
                mrt = find_nearest_mrt(cafe["latitude"], cafe["longitude"])
                if mrt:
                    if max_walk_minutes is not None and mrt["walk_minutes"] > max_walk_minutes:
                        continue
                    cafe = dict(cafe)
                    cafe["mrt_station"] = mrt["name"]
                    cafe["mrt_distance_km"] = mrt["distance_km"]
                    cafe["mrt_walk_minutes"] = mrt["walk_minutes"]
        enriched.append({"cafe": cafe, "score": None, "distance_km": None})
        if len(enriched) >= top_n:
            break
    return {"recommendations": enriched}


@router.get("/transit")
def get_transit_points(
    city: str = "taipei",
    district: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    only_with_cafes: bool = True,
    max_walk_minutes: int = Query(10, ge=1, le=60),
):
    points = search_transit_points(city, district, query=query, limit=limit)
    if only_with_cafes:
        filtered = []
        for point in points:
            lat = point.get("latitude")
            lng = point.get("longitude")
            if lat is None or lng is None:
                continue
            if has_cafes_near_transit(
                city=city,
                district=district,
                transit_lat=lat,
                transit_lng=lng,
                max_walk_minutes=max_walk_minutes,
            ):
                filtered.append(point)
        points = filtered
    return {"transit_points": points}


@router.get("/cafes/{cafe_id}")
def get_cafe(cafe_id: str):
    raise HTTPException(status_code=404, detail="Cafe not found")
