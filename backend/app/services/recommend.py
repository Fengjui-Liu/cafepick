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
    if filters.get("mrt"):
        query = query.filter(Cafe.mrt.contains(filters["mrt"]))
    if filters.get("limited_time") == "no":
        query = query.filter(Cafe.limited_time == "no")

    cafes = query.all()
    if not cafes:
        return []

    scored = []
    for cafe in cafes:
        score = 0.0
        weight_sum = 0.0

        # Score based on requested criteria (weighted matching)
        criteria = [
            ("wifi", cafe.wifi),
            ("socket", cafe.socket),
            ("quiet", cafe.quiet),
            ("cheap", cafe.cheap),
        ]

        for key, cafe_val in criteria:
            requested = filters.get(key)
            if requested is not None and requested > 0:
                # How well does this cafe meet the requirement? (0-1)
                match_ratio = min(cafe_val / requested, 1.0) if requested else 1.0
                weight = requested  # Higher requirement = higher weight
                score += match_ratio * weight
                weight_sum += weight

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
