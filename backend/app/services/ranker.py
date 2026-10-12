"""
Score cafes for a scenario and explain why (docs/DESIGN_v2.md §3, §6).

Every factor is a number in 0–1, or None when we don't know. Unknown factors
count as 0.5 so a shop missing from Cafe Nomad isn't buried, but they never
show up as a reason.
"""

from typing import Callable, Dict, List, Optional, Tuple

MODES = ("work", "date", "quick")

WEIGHTS: Dict[str, Dict[str, float]] = {
    # 💻 工作／讀書: can I sit here for hours with a laptop?
    "work": {
        "socket": 0.25, "wifi": 0.20, "limited_time": 0.20, "quiet": 0.15,
        "seat": 0.05, "distance": 0.10, "rating": 0.05,
    },
    # 💬 約會／聊天: is it a nice place?
    "date": {
        "rating": 0.35, "distance": 0.15, "tasty": 0.10, "reservable": 0.10,
        "quiet": 0.10, "dessert": 0.05, "outdoor": 0.05, "music": 0.05,
        "cheap": 0.05,
    },
    # ☕ 喝一杯就走: closest decent cafe that's open.
    "quick": {"distance": 0.55, "rating": 0.30, "open_now": 0.15},
}

NEUTRAL = 0.5
# Shops only on Cafe Nomad aren't confirmed by Google to still exist or be open.
UNVERIFIED_PENALTY = 8
REASON_MIN = 0.7  # a factor has to be clearly good to be called out
MAX_WALK_FOR_SCORE = 20  # minutes; beyond this distance scores 0

_PRICE_LEVEL = {
    "PRICE_LEVEL_FREE": 1.0,
    "PRICE_LEVEL_INEXPENSIVE": 0.9,
    "PRICE_LEVEL_MODERATE": 0.6,
    "PRICE_LEVEL_EXPENSIVE": 0.3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 0.1,
}


def _nomad(cafe: Dict, field: str) -> Optional[float]:
    value = (cafe.get("work") or {}).get(field)
    return value / 5 if value else None


def _bool(value) -> Optional[float]:
    return None if value is None else (1.0 if value else 0.0)


def _rating(cafe: Dict) -> Optional[float]:
    """Google rating shrunk toward 4.0 by review count, mapped 3.5–4.8 → 0–1."""
    rating, count = cafe.get("rating"), cafe.get("user_ratings_total") or 0
    if rating is None:
        return None
    adjusted = (rating * count + 4.0 * 20) / (count + 20)
    return min(1.0, max(0.0, (adjusted - 3.5) / 1.3))


def _limited_time(cafe: Dict) -> Optional[float]:
    value = (cafe.get("work") or {}).get("limited_time")
    return {"no": 1.0, "maybe": 0.5, "yes": 0.0}.get(value)


def _cheap(cafe: Dict) -> Optional[float]:
    nomad = _nomad(cafe, "cheap")
    if nomad is not None:
        return nomad
    return _PRICE_LEVEL.get(cafe.get("price_level"))


def _distance(cafe: Dict) -> Optional[float]:
    minutes = cafe.get("walk_minutes")
    if minutes is None:
        return None
    return max(0.0, 1 - minutes / MAX_WALK_FOR_SCORE)


FACTORS: Dict[str, Callable[[Dict], Optional[float]]] = {
    "socket": lambda c: _nomad(c, "socket"),
    "wifi": lambda c: _nomad(c, "wifi"),
    "quiet": lambda c: _nomad(c, "quiet"),
    "seat": lambda c: _nomad(c, "seat"),
    "tasty": lambda c: _nomad(c, "tasty"),
    "music": lambda c: _nomad(c, "music"),
    "limited_time": _limited_time,
    "cheap": _cheap,
    "rating": _rating,
    "distance": _distance,
    "open_now": lambda c: _bool(c.get("open_now")),
    "reservable": lambda c: _bool(c.get("reservable")),
    "dessert": lambda c: _bool(c.get("serves_dessert")),
    "outdoor": lambda c: _bool(c.get("outdoor_seating")),
}

_REASON_TEXT: Dict[str, Callable[[Dict], str]] = {
    "socket": lambda c: "插座多",
    "wifi": lambda c: "WiFi 穩",
    "limited_time": lambda c: "不限時",
    "quiet": lambda c: "安靜",
    "seat": lambda c: "座位多",
    "tasty": lambda c: "咖啡好喝",
    "music": lambda c: "音樂好",
    "cheap": lambda c: "價格親民",
    "rating": lambda c: f"評價 {c['rating']:.1f}",
    "open_now": lambda c: "營業中",
    "reservable": lambda c: "可訂位",
    "dessert": lambda c: "有甜點",
    "outdoor": lambda c: "戶外座位",
}


def factor_values(cafe: Dict) -> Dict[str, Optional[float]]:
    return {name: fn(cafe) for name, fn in FACTORS.items()}


def score(cafe: Dict, mode: str) -> Tuple[int, Dict[str, Optional[float]]]:
    weights = WEIGHTS[mode]
    values = factor_values(cafe)
    total = sum(
        w * (values[f] if values[f] is not None else NEUTRAL) for f, w in weights.items()
    )
    return round(100 * total / sum(weights.values())), values


def reasons(cafe: Dict, mode: str, values: Dict[str, Optional[float]], limit: int = 3) -> List[str]:
    """Short phrases like ["走路 4 分", "插座多", "不限時"]."""
    result = []
    if cafe.get("walk_minutes") is not None:
        result.append(f"走路 {cafe['walk_minutes']} 分")
    weights = WEIGHTS[mode]
    good = sorted(
        (f for f in weights if f != "distance" and values.get(f) is not None and values[f] >= REASON_MIN),
        key=lambda f: weights[f] * values[f],
        reverse=True,
    )
    for f in good:
        if len(result) >= limit:
            break
        result.append(_REASON_TEXT[f](cafe))
    if mode == "work" and cafe.get("work") is None:
        result.append("工作條件未知")
    return result


def pet_status(cafe: Dict) -> str:
    """'yes' | 'no' | 'unknown' — from Google's allowsDogs."""
    value = cafe.get("pet_friendly")
    return "unknown" if value is None else ("yes" if value else "no")


def rank(
    cafes: List[Dict],
    mode: str,
    pet: bool = False,
    max_walk_minutes: Optional[int] = None,
    exclude: Optional[set] = None,
) -> List[Dict]:
    """Filter hard constraints, score, and sort. Returns recommendation dicts."""
    if mode not in WEIGHTS:
        raise ValueError(f"unknown mode: {mode}")
    exclude = exclude or set()
    results = []
    for cafe in cafes:
        if cafe.get("id") in exclude:
            continue
        if cafe.get("open_now") is False:
            continue
        minutes = cafe.get("walk_minutes")
        if max_walk_minutes is not None and minutes is not None and minutes > max_walk_minutes:
            continue
        pets = pet_status(cafe)
        if pet and pets == "no":
            continue
        points, values = score(cafe, mode)
        if cafe.get("source") == "nomad":
            points -= UNVERIFIED_PENALTY
        results.append(
            {
                "cafe": cafe,
                "score": points,
                "reasons": reasons(cafe, mode, values),
                "pet_status": pets,
                "walk_minutes": minutes,
                "distance_km": cafe.get("distance_km"),
            }
        )
    # With 帶毛孩 on, confirmed pet-friendly shops come before 未確認 ones.
    results.sort(key=lambda r: (pet and r["pet_status"] != "yes", -r["score"]))
    return results
