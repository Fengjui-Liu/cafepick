from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query

from app.services import mrt
from app.services.recommend import recommend

router = APIRouter(tags=["recommend"])


@router.get("/recommend")
def get_recommend(
    mode: Literal["work", "date", "quick"] = "quick",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    station: Optional[str] = Query(None, description="捷運站名，例如 忠孝復興"),
    city: str = "taipei",
    district: Optional[str] = None,
    pet: bool = False,
    max_walk_minutes: Optional[int] = Query(None, ge=1, le=60),
    exclude: Optional[str] = Query(None, description="已看過的店 id，逗號分隔（換 3 間用）"),
    top_n: int = Query(3, ge=1, le=10),
):
    """
    推薦咖啡廳。起點三選一：GPS（lat/lng）、捷運站（station）、行政區（district）。
    """
    origin = None
    if lat is not None and lng is not None:
        origin = {"latitude": lat, "longitude": lng, "label": "目前位置"}
    elif station:
        matches = mrt.find_stations(station)
        exact = [s for s in matches if s["name"] == station.replace("站", "")]
        chosen = (exact or matches or [None])[0]
        if chosen is None:
            raise HTTPException(status_code=404, detail=f"找不到捷運站：{station}")
        origin = {
            "latitude": chosen["latitude"],
            "longitude": chosen["longitude"],
            "label": f"捷運{chosen['name']}站",
        }
    elif not district:
        raise HTTPException(status_code=422, detail="請提供 lat/lng、station 或 district")

    result = recommend(
        mode=mode,
        lat=origin["latitude"] if origin else None,
        lng=origin["longitude"] if origin else None,
        city=city,
        district=district,
        pet=pet,
        max_walk_minutes=max_walk_minutes,
        exclude=set(exclude.split(",")) if exclude else None,
        top_n=top_n,
    )
    result["origin"] = origin or {"label": district}
    return result


@router.get("/stations")
def get_stations(q: str = ""):
    """捷運站名自動完成（本地資料，不呼叫 Google）。"""
    stations = mrt.find_stations(q) if q else mrt.load_stations()
    return {"stations": [{"name": s["name"], "lines": s.get("lines", [])} for s in stations]}
