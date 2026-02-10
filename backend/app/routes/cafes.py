from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.cafe import Cafe
from app.services.recommend import recommend_cafes

router = APIRouter(tags=["cafes"])


@router.get("/cafes")
def get_cafes(
    city: Optional[str] = None,
    district: Optional[str] = None,
    mrt: Optional[str] = None,
    name: Optional[str] = None,
    has_wifi: Optional[bool] = None,
    has_socket: Optional[bool] = None,
    quiet_level: Optional[str] = None,  # "quiet", "moderate", "lively"
    price_range: Optional[str] = None,  # "budget", "moderate", "pricey"
    limited_time: Optional[str] = None,
    has_reservation: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Cafe)

    if name:
        query = query.filter(Cafe.name.contains(name))
    if city:
        query = query.filter(Cafe.city == city)
    if district:
        query = query.filter(Cafe.district == district)
    if mrt:
        query = query.filter(Cafe.mrt.contains(mrt))
    if has_wifi:
        query = query.filter(Cafe.wifi >= 3)
    if has_socket:
        query = query.filter(Cafe.socket >= 3)
    if quiet_level == "quiet":
        query = query.filter(Cafe.quiet >= 3.5)
    elif quiet_level == "moderate":
        query = query.filter(Cafe.quiet >= 2, Cafe.quiet < 3.5)
    elif quiet_level == "lively":
        query = query.filter(Cafe.quiet < 2)
    if price_range == "budget":
        query = query.filter(Cafe.cheap >= 4)
    elif price_range == "moderate":
        query = query.filter(Cafe.cheap >= 2.5, Cafe.cheap < 4)
    elif price_range == "pricey":
        query = query.filter(Cafe.cheap < 2.5)
    if limited_time:
        query = query.filter(Cafe.limited_time == limited_time)
    if has_reservation:
        query = query.filter(Cafe.has_reservation == "yes")

    total = query.count()
    cafes = query.offset(offset).limit(limit).all()

    return {"total": total, "cafes": cafes}


@router.get("/cafes/recommend")
def get_recommendations(
    city: str = "taipei",
    district: Optional[str] = None,
    mrt: Optional[str] = None,
    name: Optional[str] = None,
    has_wifi: Optional[bool] = None,
    has_socket: Optional[bool] = None,
    quiet_level: Optional[str] = None,
    price_range: Optional[str] = None,
    limited_time: Optional[str] = None,
    has_reservation: Optional[bool] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    top_n: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    filters = {
        "city": city,
        "district": district,
        "mrt": mrt,
        "name": name,
        "has_wifi": has_wifi,
        "has_socket": has_socket,
        "quiet_level": quiet_level,
        "price_range": price_range,
        "limited_time": limited_time,
        "has_reservation": has_reservation,
        "latitude": latitude,
        "longitude": longitude,
    }
    results = recommend_cafes(db, filters, top_n)
    return {"recommendations": results}


@router.get("/cafes/{cafe_id}")
def get_cafe(cafe_id: str, db: Session = Depends(get_db)):
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if not cafe:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Cafe not found")
    return cafe
