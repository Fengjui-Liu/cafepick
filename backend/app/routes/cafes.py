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
    area: Optional[str] = None,
    wifi: Optional[float] = Query(None, ge=0, le=5),
    socket: Optional[float] = Query(None, ge=0, le=5),
    quiet: Optional[float] = Query(None, ge=0, le=5),
    limited_time: Optional[str] = None,
    cheap: Optional[float] = Query(None, ge=0, le=5),
    mrt: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Cafe)

    if city:
        query = query.filter(Cafe.city == city)
    if mrt:
        query = query.filter(Cafe.mrt.contains(mrt))
    if wifi is not None:
        query = query.filter(Cafe.wifi >= wifi)
    if socket is not None:
        query = query.filter(Cafe.socket >= socket)
    if quiet is not None:
        query = query.filter(Cafe.quiet >= quiet)
    if cheap is not None:
        query = query.filter(Cafe.cheap >= cheap)
    if limited_time:
        query = query.filter(Cafe.limited_time == limited_time)

    total = query.count()
    cafes = query.offset(offset).limit(limit).all()

    return {"total": total, "cafes": cafes}


@router.get("/cafes/recommend")
def get_recommendations(
    city: str = "taipei",
    wifi: Optional[float] = Query(None, ge=0, le=5),
    socket: Optional[float] = Query(None, ge=0, le=5),
    quiet: Optional[float] = Query(None, ge=0, le=5),
    limited_time: Optional[str] = None,
    cheap: Optional[float] = Query(None, ge=0, le=5),
    mrt: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    top_n: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    filters = {
        "city": city,
        "wifi": wifi,
        "socket": socket,
        "quiet": quiet,
        "limited_time": limited_time,
        "cheap": cheap,
        "mrt": mrt,
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
