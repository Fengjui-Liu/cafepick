import math
import re


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


def recommend_cafes_from_list(cafes: list, filters: dict, top_n: int = 5) -> list:
    """Recommend cafes from a list of dicts (Café Nomad live data)."""
    if not cafes:
        return []

    filtered = []
    for cafe in cafes:
        if filters.get("district") and cafe.get("district") != filters["district"]:
            continue
        if filters.get("mrt_station"):
            if filters["mrt_station"] not in (cafe.get("mrt_station") or ""):
                continue
        if filters.get("mrt"):
            normalized = _normalize_mrt_station(filters["mrt"])
            if normalized and normalized not in (cafe.get("mrt_station") or ""):
                continue
        if filters.get("bus_stop"):
            needle = filters["bus_stop"]
            haystack = " ".join(
                [
                    cafe.get("bus_stop") or "",
                    cafe.get("address") or "",
                    cafe.get("name") or "",
                    cafe.get("mrt_station") or "",
                ]
            )
            if needle not in haystack:
                continue
        if filters.get("has_wifi") is True and not cafe.get("has_wifi"):
            continue
        if filters.get("has_socket") is True and not cafe.get("has_socket"):
            continue
        if filters.get("reservable") is True and not cafe.get("reservable"):
            continue
        if filters.get("quiet_level") and cafe.get("quiet_level") != filters["quiet_level"]:
            continue
        if filters.get("max_price") is not None:
            if cafe.get("price") is None or cafe.get("price") > filters["max_price"]:
                continue
        if filters.get("limited_time") and cafe.get("limited_time") != filters["limited_time"]:
            continue
        filtered.append(cafe)

    scored = []
    for cafe in filtered:
        score = 0.0
        max_score = 0.0

        if filters.get("has_wifi"):
            max_score += 2.0
            if cafe.get("has_wifi"):
                score += 2.0
            elif cafe.get("wifi", 0) >= 1:
                score += 0.5

        if filters.get("has_socket"):
            max_score += 2.0
            if cafe.get("has_socket"):
                score += 2.0
            elif cafe.get("socket", 0) >= 1:
                score += 0.5

        quiet_level = filters.get("quiet_level")
        if quiet_level:
            max_score += 2.0
            cafe_level = cafe.get("quiet_level") or _quiet_level(cafe.get("quiet", 0))
            if cafe_level == quiet_level:
                score += 2.0
            elif quiet_level == "quiet" and cafe.get("quiet", 0) >= 2.5:
                score += 1.0
            elif quiet_level == "normal" and 2.0 <= cafe.get("quiet", 0) < 4.0:
                score += 1.0
            elif quiet_level == "loud" and cafe.get("quiet", 0) < 3.0:
                score += 1.0

        if filters.get("max_price") is not None:
            max_score += 2.0
            if cafe.get("price") and cafe.get("price") <= filters["max_price"]:
                score += 2.0

        if cafe.get("seat", 0) > 3:
            score += 0.5
            max_score += 0.5

        distance = None
        if (
            filters.get("latitude")
            and filters.get("longitude")
            and cafe.get("latitude")
            and cafe.get("longitude")
        ):
            distance = _haversine(
                filters["latitude"],
                filters["longitude"],
                cafe["latitude"],
                cafe["longitude"],
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
                cafe.get(k, 0)
                for k in ["wifi", "socket", "quiet", "cheap", "seat"]
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
