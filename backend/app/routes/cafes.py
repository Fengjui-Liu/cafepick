from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.enrich import enrich
from app.services.geo import haversine_km, walk_minutes
from app.services.google_places import (
    search_places,
    search_places_near,
    search_transit_points,
    has_cafes_near_transit,
)

router = APIRouter(tags=["cafes"])


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
    cafes = [enrich(c) for c in cafes[offset : offset + limit]]

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
        cafe = enrich(cafe)
        if cafe.get("latitude") and cafe.get("longitude"):
            if transit_lat is not None and transit_lng is not None and transit_name:
                dist = haversine_km(
                    cafe["latitude"], cafe["longitude"], transit_lat, transit_lng
                )
                minutes = walk_minutes(dist)
                if max_walk_minutes is not None and minutes > max_walk_minutes:
                    continue
                cafe["transit_name"] = transit_name
                cafe["transit_distance_km"] = round(dist, 2)
                cafe["transit_walk_minutes"] = minutes
            elif max_walk_minutes is not None:
                station = cafe.get("nearest_mrt")
                if station and station["walk_minutes"] > max_walk_minutes:
                    continue
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
