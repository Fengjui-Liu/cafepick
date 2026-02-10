from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.google_places import search_places, find_nearest_mrt, search_transit_points

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

    keyword = district or query
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
    keyword = district or query
    cafes = search_places(city, keyword, limit=top_n)
    enriched = []
    for cafe in cafes:
        if cafe.get("latitude") and cafe.get("longitude"):
            if transit_lat is not None and transit_lng is not None and transit_name:
                from app.services.google_places import _haversine_km
                dist = _haversine_km(
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
    return {"recommendations": enriched}


@router.get("/transit")
def get_transit_points(
    city: str = "taipei",
    district: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
):
    points = search_transit_points(city, district, query=query, limit=limit)
    return {"transit_points": points}


@router.get("/cafes/{cafe_id}")
def get_cafe(cafe_id: str):
    raise HTTPException(status_code=404, detail="Cafe not found")
