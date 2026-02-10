from typing import Optional
from fastapi import APIRouter, Query
from app.services.google_places import CITY_NAMES, CITY_COORDS, get_city_districts

router = APIRouter(tags=["areas"])


@router.get("/areas")
def get_areas(city: Optional[str] = Query(None)):
    """Get cities list for Places API usage (no districts/mrt from Places)."""
    if city:
        if city not in CITY_COORDS:
            return {"areas": []}
        districts = [
            {"name": d, "mrt_stations": []} for d in get_city_districts(city)
        ]
        return {
            "areas": [
                {
                    "city": city,
                    "city_name": CITY_NAMES.get(city, city),
                    "cafe_count": None,
                    "districts": districts,
                    "mrt_stations": [],
                }
            ]
        }

    result = [
        {
            "city": c,
            "city_name": CITY_NAMES.get(c, c),
            "cafe_count": None,
            "districts": [],
            "mrt_stations": [],
        }
        for c in CITY_COORDS.keys()
    ]
    return {"areas": result}
