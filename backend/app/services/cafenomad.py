import time
from collections import defaultdict
from typing import Dict, List
import httpx
from app.services.normalize import normalize_mrt, extract_district

CAFENOMAD_API = "https://cafenomad.tw/api/v1.2/cafes"

CITIES = [
    "taipei",
    "keelung",
    "taoyuan",
    "hsinchu",
    "miaoli",
    "taichung",
    "changhua",
    "nantou",
    "yunlin",
    "chiayi",
    "tainan",
    "kaohsiung",
    "pingtung",
    "yilan",
    "hualien",
    "taitung",
    "penghu",
    "kinmen",
    "lienchiang",
]

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
    "penghu": "澎湖",
    "kinmen": "金門",
    "lienchiang": "連江",
}

_CACHE: Dict[str, Dict[str, object]] = {}
_CACHE_TTL_SECONDS = 300


def _to_float(val) -> float:
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def _quiet_level(score: float) -> str:
    if score >= 4.0:
        return "quiet"
    if score >= 2.5:
        return "normal"
    return "loud"


def _price_from_cheap(score: float) -> float:
    if score <= 0:
        return 0.0
    min_price = 80.0
    max_price = 300.0
    return round(max_price - (max_price - min_price) * (score / 5.0), 0)


def _map_fields(item: dict, city: str) -> dict:
    wifi_score = _to_float(item.get("wifi"))
    socket_score = _to_float(item.get("socket"))
    quiet_score = _to_float(item.get("quiet"))
    cheap_score = _to_float(item.get("cheap"))
    address = item.get("address", "")
    mrt_raw = item.get("mrt", "")

    return {
        "id": item.get("id", ""),
        "name": item.get("name", ""),
        "city": city,
        "address": address,
        "district": extract_district(address),
        "latitude": _to_float(item.get("latitude")),
        "longitude": _to_float(item.get("longitude")),
        "url": item.get("url", ""),
        "mrt": mrt_raw,
        "mrt_station": normalize_mrt(mrt_raw),
        "open_time": item.get("open_time", ""),
        "wifi": wifi_score,
        "socket": socket_score,
        "quiet": quiet_score,
        "tasty": _to_float(item.get("tasty")),
        "cheap": cheap_score,
        "music": _to_float(item.get("music")),
        "seat": _to_float(item.get("seat")),
        "price": _price_from_cheap(cheap_score),
        "quiet_level": _quiet_level(quiet_score),
        "has_wifi": wifi_score > 0,
        "has_socket": socket_score > 0,
        "reservable": None,
        "bus_stop": None,
        "limited_time": item.get("limited_time", ""),
        "standing_desk": item.get("standing_desk", ""),
    }


def fetch_cafes(city: str) -> List[dict]:
    if not city:
        return []

    now = time.time()
    cached = _CACHE.get(city)
    if cached and (now - cached["ts"]) < _CACHE_TTL_SECONDS:
        return cached["data"]  # type: ignore[return-value]

    url = f"{CAFENOMAD_API}/{city}"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    cafes = [_map_fields(item, city) for item in data]
    _CACHE[city] = {"ts": now, "data": cafes}
    return cafes


def filter_cafes(cafes: List[dict], filters: dict) -> List[dict]:
    result = []
    for cafe in cafes:
        if filters.get("district") and cafe.get("district") != filters["district"]:
            continue
        if filters.get("mrt_station"):
            if filters["mrt_station"] not in (cafe.get("mrt_station") or ""):
                continue
        if filters.get("mrt"):
            normalized = normalize_mrt(filters["mrt"])
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
        if filters.get("limited_time"):
            if cafe.get("limited_time") != filters["limited_time"]:
                continue
        result.append(cafe)
    return result


def build_area(city: str) -> dict:
    cafes = fetch_cafes(city)
    district_mrts = defaultdict(set)
    all_mrts = set()

    for cafe in cafes:
        mrt_name = (cafe.get("mrt_station") or "").strip()
        district = cafe.get("district") or ""
        if mrt_name:
            all_mrts.add(mrt_name)
            if district:
                district_mrts[district].add(mrt_name)

    districts = [
        {"name": d_name, "mrt_stations": sorted(district_mrts[d_name])}
        for d_name in sorted(district_mrts.keys())
    ]

    return {
        "city": city,
        "city_name": CITY_NAMES.get(city, city),
        "cafe_count": len(cafes),
        "districts": districts,
        "mrt_stations": sorted(all_mrts),
    }
