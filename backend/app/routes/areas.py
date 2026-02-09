from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cafe import Cafe

router = APIRouter(tags=["areas"])


@router.get("/areas")
def get_areas(db: Session = Depends(get_db)):
    """Get available cities, districts, and MRT stations."""
    cities = db.query(Cafe.city, func.count(Cafe.id)).group_by(Cafe.city).all()

    result = []
    for city, count in cities:
        mrts = (
            db.query(func.coalesce(func.nullif(Cafe.mrt_station, ""), Cafe.mrt))
            .filter(
                Cafe.city == city,
                func.coalesce(func.nullif(Cafe.mrt_station, ""), Cafe.mrt).isnot(None),
                func.coalesce(func.nullif(Cafe.mrt_station, ""), Cafe.mrt) != "",
            )
            .distinct()
            .all()
        )
        mrt_list = sorted(set(m[0] for m in mrts if m[0]))

        districts = (
            db.query(Cafe.district)
            .filter(Cafe.city == city, Cafe.district.isnot(None), Cafe.district != "")
            .distinct()
            .all()
        )
        district_list = sorted(set(d[0] for d in districts if d[0]))

        result.append(
            {
                "city": city,
                "cafe_count": count,
                "districts": district_list,
                "mrt_stations": mrt_list,
            }
        )

    return {"areas": result}
