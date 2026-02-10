import math
from sqlalchemy.orm import Session
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


def recommend_cafes(db: Session, filters: dict, top_n: int = 5) -> list:
    """
    Recommendation algorithm v2: improved scoring with boolean/categorical filters.

    Scoring factors:
    - WiFi match bonus (if requested and available)
    - Socket match bonus (if requested and available)
    - Quiet level match bonus
    - Price range match bonus
    - Seat availability bonus
    - Distance bonus (if user location provided)
    """
    query = db.query(Cafe)

    # Hard filters (location)
    if filters.get("city"):
        query = query.filter(Cafe.city == filters["city"])
    if filters.get("district"):
        query = query.filter(Cafe.district == filters["district"])
    if filters.get("mrt"):
        query = query.filter(Cafe.mrt.contains(filters["mrt"]))
    if filters.get("limited_time") == "no":
        query = query.filter(Cafe.limited_time == "no")
    if filters.get("has_reservation"):
        query = query.filter(Cafe.has_reservation == "yes")

    cafes = query.all()
    if not cafes:
        return []

    scored = []
    for cafe in cafes:
        score = 0.0
        max_score = 0.0

        # WiFi: bonus if cafe has good wifi (score >= 3)
        if filters.get("has_wifi"):
            max_score += 2.0
            if cafe.wifi and cafe.wifi >= 3:
                score += 2.0
            elif cafe.wifi and cafe.wifi >= 1:
                score += 0.5

        # Socket: bonus if cafe has sockets (score >= 3)
        if filters.get("has_socket"):
            max_score += 2.0
            if cafe.socket and cafe.socket >= 3:
                score += 2.0
            elif cafe.socket and cafe.socket >= 1:
                score += 0.5

        # Quiet level matching
        quiet_level = filters.get("quiet_level")
        if quiet_level:
            max_score += 2.0
            q = cafe.quiet or 0
            if quiet_level == "quiet" and q >= 3.5:
                score += 2.0
            elif quiet_level == "quiet" and q >= 2.5:
                score += 1.0
            elif quiet_level == "moderate" and 2 <= q < 3.5:
                score += 2.0
            elif quiet_level == "moderate":
                score += 0.5
            elif quiet_level == "lively" and q < 2:
                score += 2.0
            elif quiet_level == "lively" and q < 3:
                score += 1.0

        # Price range matching
        price_range = filters.get("price_range")
        if price_range:
            max_score += 2.0
            c = cafe.cheap or 0
            if price_range == "budget" and c >= 4:
                score += 2.0
            elif price_range == "budget" and c >= 3:
                score += 1.0
            elif price_range == "moderate" and 2.5 <= c < 4:
                score += 2.0
            elif price_range == "moderate":
                score += 0.5
            elif price_range == "pricey" and c < 2.5:
                score += 2.0
            elif price_range == "pricey" and c < 3.5:
                score += 1.0

        # Seat availability bonus
        if cafe.seat and cafe.seat > 3:
            score += 0.5
            max_score += 0.5

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
            max_score += 2.0
            if distance < 0.5:
                score += 2.0
            elif distance < 1.0:
                score += 1.5
            elif distance < 2.0:
                score += 1.0
            elif distance < 5.0:
                score += 0.5

        # Normalize to 0-100 scale
        if max_score > 0:
            final_score = round((score / max_score) * 100)
        else:
            # No specific preferences → score based on overall quality
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
