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


def recommend_cafes(db: Session, filters: dict, top_n: int = 3) -> list:
    """
    Recommendation algorithm v1: score-based matching.

    Each cafe gets a score based on how well it matches the user's criteria.
    Higher score = better match.
    """
    query = db.query(Cafe)

    # Apply hard filters
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
        weight_sum = 0.0

        # Score based on requested criteria (weighted matching)
        quiet_pref = filters.get("quiet") or filters.get("quiet_level")
        if isinstance(quiet_pref, (int, float)):
            requested = quiet_pref
            if requested > 0:
                match_ratio = min(cafe.quiet / requested, 1.0)
                score += match_ratio * requested
                weight_sum += requested
        elif isinstance(quiet_pref, str):
            requested_score = {"quiet": 4.0, "normal": 2.5, "loud": 1.0}.get(
                quiet_pref
            )
            if requested_score:
                match_ratio = min(cafe.quiet / requested_score, 1.0)
                score += match_ratio * 1.5
                weight_sum += 1.5

        if filters.get("cheap") is not None and filters.get("max_price") is None:
            requested = filters["cheap"]
            if requested > 0:
                match_ratio = min(cafe.cheap / requested, 1.0)
                score += match_ratio * requested
                weight_sum += requested

        # Bonus for seat availability
        if cafe.seat and cafe.seat > 3:
            score += 0.5

        # Distance bonus (if user location provided)
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
            # Closer = higher bonus (max 2 points within 500m)
            if distance < 0.5:
                score += 2.0
            elif distance < 1.0:
                score += 1.5
            elif distance < 2.0:
                score += 1.0
            elif distance < 5.0:
                score += 0.5

        # Normalize score
        final_score = score / weight_sum if weight_sum > 0 else score

        scored.append(
            {
                "cafe": cafe,
                "score": round(final_score, 2),
                "distance_km": round(distance, 2) if distance else None,
            }
        )

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
