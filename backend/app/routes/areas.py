from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cafe import Cafe
from app.services.normalize import normalize_mrt

router = APIRouter(tags=["areas"])

CITY_NAMES = {
    "taipei": "台北",
    "keelung": "基隆",
    "taoyuan": "桃園",
    "hsinchu": "新竹",
    "miaoli": "苗栗",
    "taichung": "台中",
    "changhua": "彰化",
    "nantou": "南投",
    "yunlin": "雲林",
    "chiayi": "嘉義",
    "tainan": "台南",
    "kaohsiung": "高雄",
    "pingtung": "屏東",
    "yilan": "宜蘭",
    "hualien": "花蓮",
    "taitung": "台東",
}


@router.get("/areas")
def get_areas(db: Session = Depends(get_db)):
    """Get available cities with their districts and MRT stations (hierarchical)."""
    cities = db.query(Cafe.city, func.count(Cafe.id)).group_by(Cafe.city).all()

    result = []
    for city, count in cities:
        # Get all cafes in this city to build district → MRT mapping
        cafes = db.query(Cafe.district, Cafe.mrt).filter(Cafe.city == city).all()

        district_mrts = defaultdict(set)
        all_mrts = set()

        for district, mrt in cafes:
            normalized = normalize_mrt(mrt) if mrt else ""
            if normalized:
                all_mrts.add(normalized)
                if district:
                    district_mrts[district].add(normalized)

        districts = []
        for d_name in sorted(district_mrts.keys()):
            districts.append({
                "name": d_name,
                "mrt_stations": sorted(district_mrts[d_name]),
            })

        result.append({
            "city": city,
            "city_name": CITY_NAMES.get(city, city),
            "cafe_count": count,
            "districts": districts,
            "mrt_stations": sorted(all_mrts),
        })

    return {"areas": result}
