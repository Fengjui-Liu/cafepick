import math
import re
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.cafe import Cafe


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two coordinates."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _normalize_mrt_station(mrt: str) -> str:
    if not mrt:
        return ""
    value = re.sub(r"\(.*?\)", "", mrt)
    value = re.split(r"(出口|Exit)", value)[0]
    value = re.sub(r"\d+號?", "", value)
    value = re.split(r"[#／/、,;；]", value)[0]
    return value.strip()


def _quiet_level(score: float) -> str:
    if score >= 4.0:
        return "quiet"
    if score >= 2.5:
        return "normal"
    return "loud"


def _walk_minutes_to_km(minutes: float) -> float:
    return minutes * 0.08


def recommend_cafes(db: Session, filters: dict, top_n: int = 5) -> list:
    """
    Recommendation algorithm: improved scoring with boolean/categorical filters.

    Scoring factors:
    - WiFi match bonus (if requested and available)
    - Socket match bonus (if requested and available)
    - Quiet level match bonus
    - Price cap bonus
    - Seat availability bonus
    - Distance bonus (if user location provided)
    """
    query = db.query(Cafe)

    # Hard filters
    if filters.get("city"):
        query = query.filter(Cafe.city == filters["city"])
    if filters.get("district"):
        query = query.filter(Cafe.district == filters["district"])
    if filters.get("mrt_station"):
        query = query.filter(
            or_(
                Cafe.mrt_station.contains(filters["mrt_station"]),
                Cafe.mrt.contains(filters["mrt_station"]),
            )
        )
    if filters.get("mrt"):
        normalized = _normalize_mrt_station(filters["mrt"])
        if normalized:
            query = query.filter(
                or_(Cafe.mrt_station.contains(normalized), Cafe.mrt.contains(normalized))
            )
    if filters.get("limited_time") == "no":
        query = query.filter(Cafe.limited_time == "no")
    if filters.get("has_wifi") is True:
        query = query.filter(Cafe.has_wifi.is_(True))
    if filters.get("has_socket") is True:
        query = query.filter(Cafe.has_socket.is_(True))
    if filters.get("reservable") is True:
        query = query.filter(Cafe.reservable.is_(True))
    if filters.get("quiet_level"):
        query = query.filter(Cafe.quiet_level == filters["quiet_level"])
    if filters.get("max_price") is not None:
        query = query.filter(Cafe.price.isnot(None), Cafe.price <= filters["max_price"])
    if filters.get("bus_stop"):
        query = query.filter(Cafe.bus_stop.contains(filters["bus_stop"]))

    cafes = query.all()
    if not cafes:
        return []

    scored = []
    for cafe in cafes:
        score = 0.0
        max_score = 0.0

        if filters.get("has_wifi"):
            max_score += 2.0
            has_wifi = cafe.has_wifi if cafe.has_wifi is not None else (cafe.wifi or 0) >= 3
            if has_wifi:
                score += 2.0
            elif cafe.wifi and cafe.wifi >= 1:
                score += 0.5

        if filters.get("has_socket"):
            max_score += 2.0
            has_socket = (
                cafe.has_socket if cafe.has_socket is not None else (cafe.socket or 0) >= 3
            )
            if has_socket:
                score += 2.0
            elif cafe.socket and cafe.socket >= 1:
                score += 0.5

        quiet_level = filters.get("quiet_level")
        if quiet_level:
            max_score += 2.0
            q = cafe.quiet or 0
            cafe_level = cafe.quiet_level or _quiet_level(q)
            if cafe_level == quiet_level:
                score += 2.0
            elif quiet_level == "quiet" and q >= 2.5:
                score += 1.0
            elif quiet_level == "normal" and 2.0 <= q < 4.0:
                score += 1.0
            elif quiet_level == "loud" and q < 3.0:
                score += 1.0

        if filters.get("max_price") is not None:
            max_score += 2.0
            if cafe.price and cafe.price <= filters["max_price"]:
                score += 2.0

        if cafe.seat and cafe.seat > 3:
            score += 0.5
            max_score += 0.5

        distance = None
        if (
            filters.get("latitude")
            and filters.get("longitude")
            and cafe.latitude
            and cafe.longitude
        ):
            distance = _haversine(
                filters["latitude"],
                filters["longitude"],
                cafe.latitude,
                cafe.longitude,
            )
            if filters.get("max_walk_minutes") is not None:
                max_distance_km = _walk_minutes_to_km(filters["max_walk_minutes"])
                if distance > max_distance_km:
                    continue
            max_score += 2.0
            if distance < 0.5:
                score += 2.0
            elif distance < 1.0:
                score += 1.5
            elif distance < 2.0:
                score += 1.0
            elif distance < 5.0:
                score += 0.5

        if max_score > 0:
            final_score = round((score / max_score) * 100)
        else:
            overall = sum(
                v or 0 for v in [cafe.wifi, cafe.socket, cafe.quiet, cafe.cheap, cafe.seat]
            )
            final_score = round((overall / 25) * 100)

        scored.append(
            {
                "cafe": cafe,
                "score": final_score,
                "distance_km": round(distance, 2) if distance else None,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
