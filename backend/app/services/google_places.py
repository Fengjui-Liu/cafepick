import os
import re
import math
import httpx
from typing import List, Dict, Optional, Tuple

PLACES_TEXT_ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
PLACES_NEARBY_ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"

CITY_COORDS = {
    "taipei": (25.0330, 121.5654),
    "newtaipei": (25.0124, 121.4657),
    "keelung": (25.1283, 121.7419),
    "taoyuan": (24.9937, 121.3000),
    "hsinchu": (24.8066, 120.9686),
    "miaoli": (24.5602, 120.8214),
    "taichung": (24.1477, 120.6736),
    "changhua": (24.0717, 120.5420),
    "nantou": (23.9609, 120.9719),
    "yunlin": (23.7092, 120.4313),
    "chiayi": (23.4801, 120.4491),
    "tainan": (22.9999, 120.2270),
    "kaohsiung": (22.6273, 120.3014),
    "pingtung": (22.5519, 120.5489),
    "yilan": (24.7570, 121.7544),
    "hualien": (23.9872, 121.6015),
    "taitung": (22.7583, 121.1444),
    "penghu": (23.5712, 119.5794),
    "kinmen": (24.4321, 118.3171),
    "lienchiang": (26.1600, 119.9500),
}

CITY_NAMES = {
    "taipei": "台北",
    "newtaipei": "新北",
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

CITY_DISTRICTS = {
    "taipei": [
        "中正區",
        "大同區",
        "中山區",
        "松山區",
        "大安區",
        "萬華區",
        "信義區",
        "士林區",
        "北投區",
        "內湖區",
        "南港區",
        "文山區",
    ],
    "newtaipei": [
        "板橋區",
        "三重區",
        "中和區",
        "永和區",
        "新莊區",
        "新店區",
        "土城區",
        "蘆洲區",
        "汐止區",
        "樹林區",
        "鶯歌區",
        "三峽區",
        "淡水區",
        "瑞芳區",
        "五股區",
        "泰山區",
        "林口區",
        "深坑區",
        "石碇區",
        "坪林區",
        "三芝區",
        "石門區",
        "八里區",
        "平溪區",
        "雙溪區",
        "貢寮區",
        "金山區",
        "萬里區",
        "烏來區",
    ],
    "taoyuan": [
        "桃園區",
        "中壢區",
        "平鎮區",
        "八德區",
        "楊梅區",
        "蘆竹區",
        "大溪區",
        "大園區",
        "龜山區",
        "龍潭區",
        "新屋區",
        "觀音區",
        "復興區",
    ],
    "taichung": [
        "中區",
        "東區",
        "南區",
        "西區",
        "北區",
        "北屯區",
        "西屯區",
        "南屯區",
        "太平區",
        "大里區",
        "霧峰區",
        "烏日區",
        "豐原區",
        "后里區",
        "石岡區",
        "東勢區",
        "和平區",
        "新社區",
        "潭子區",
        "大雅區",
        "神岡區",
        "大肚區",
        "沙鹿區",
        "龍井區",
        "梧棲區",
        "清水區",
        "大甲區",
        "外埔區",
        "大安區",
    ],
    "kaohsiung": [
        "楠梓區",
        "左營區",
        "鼓山區",
        "三民區",
        "鹽埕區",
        "前金區",
        "新興區",
        "苓雅區",
        "前鎮區",
        "旗津區",
        "小港區",
        "鳳山區",
        "大寮區",
        "林園區",
        "鳥松區",
        "大樹區",
        "大社區",
        "仁武區",
        "岡山區",
        "橋頭區",
        "燕巢區",
        "田寮區",
        "阿蓮區",
        "路竹區",
        "湖內區",
        "茄萣區",
        "永安區",
        "彌陀區",
        "梓官區",
        "旗山區",
        "美濃區",
        "六龜區",
        "甲仙區",
        "杉林區",
        "內門區",
        "茂林區",
        "桃源區",
        "那瑪夏區",
    ],
}

_MRT_CACHE: Dict[Tuple[float, float], Dict[str, object]] = {}


def _api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not set")
    return key


def _text_query(city: str, district: Optional[str] = None) -> str:
    city_name = CITY_NAMES.get(city, city)
    if district:
        return f"{district} {city_name} 咖啡"
    return f"{city_name} 咖啡"


def _extract_district(address: str) -> str:
    if not address:
        return ""
    match = re.search(r"([\u4e00-\u9fff]{1,3}區)", address)
    return match.group(1) if match else ""


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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


def get_city_districts(city: str) -> List[str]:
    return CITY_DISTRICTS.get(city, [])


def _post_places(url: str, payload: dict, field_mask: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": _api_key(),
        "X-Goog-FieldMask": field_mask,
    }
    resp = httpx.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"Places API error {resp.status_code}: {resp.text}")
    return resp.json()


def search_places(city: str, district: Optional[str] = None, limit: int = 20) -> List[Dict]:
    if city not in CITY_COORDS:
        return []
    lat, lng = CITY_COORDS[city]

    payload = {
        "textQuery": _text_query(city, district),
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 8000.0,
            }
        },
        "includedType": "cafe",
        "maxResultCount": min(max(limit, 1), 20),
        "languageCode": "zh-TW",
        "regionCode": "TW",
    }

    data = _post_places(
        PLACES_TEXT_ENDPOINT,
        payload,
        "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.priceLevel,places.websiteUri",
    )

    places = data.get("places", [])
    results = []
    for p in places:
        loc = p.get("location") or {}
        address = p.get("formattedAddress", "")
        inferred_district = _extract_district(address)
        results.append(
            {
                "id": p.get("id", ""),
                "name": (p.get("displayName") or {}).get("text", ""),
                "address": address,
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
                "rating": p.get("rating"),
                "user_ratings_total": p.get("userRatingCount"),
                "price_level": p.get("priceLevel"),
                "url": p.get("websiteUri"),
                "city": city,
                "district": district or inferred_district or "",
            }
        )
    return results


def search_places_near(
    city: str,
    latitude: float,
    longitude: float,
    district: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    if city not in CITY_COORDS:
        return []

    payload = {
        "textQuery": _text_query(city, district),
        "locationBias": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": 2500.0,
            }
        },
        "includedType": "cafe",
        "maxResultCount": min(max(limit, 1), 20),
        "languageCode": "zh-TW",
        "regionCode": "TW",
    }

    data = _post_places(
        PLACES_TEXT_ENDPOINT,
        payload,
        "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.priceLevel,places.websiteUri",
    )

    places = data.get("places", [])
    results = []
    for p in places:
        loc = p.get("location") or {}
        address = p.get("formattedAddress", "")
        inferred_district = _extract_district(address)
        results.append(
            {
                "id": p.get("id", ""),
                "name": (p.get("displayName") or {}).get("text", ""),
                "address": address,
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
                "rating": p.get("rating"),
                "user_ratings_total": p.get("userRatingCount"),
                "price_level": p.get("priceLevel"),
                "url": p.get("websiteUri"),
                "city": city,
                "district": district or inferred_district or "",
            }
        )
    return results


def has_cafes_near_transit(
    city: str,
    transit_lat: float,
    transit_lng: float,
    district: Optional[str] = None,
    max_walk_minutes: int = 10,
) -> bool:
    cafes = search_places_near(
        city=city,
        latitude=transit_lat,
        longitude=transit_lng,
        district=district,
        limit=5,
    )
    max_km = (max_walk_minutes / 60.0) * 5.0
    for cafe in cafes:
        lat = cafe.get("latitude")
        lng = cafe.get("longitude")
        if lat is None or lng is None:
            continue
        if _haversine_km(lat, lng, transit_lat, transit_lng) <= max_km:
            return True
    return False


def search_transit_points(
    city: str,
    district: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    if city not in CITY_COORDS:
        return []
    lat, lng = CITY_COORDS[city]

    payload_base = {
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 12000.0,
            }
        },
        "maxResultCount": min(max(limit, 1), 20),
        "languageCode": "zh-TW",
        "regionCode": "TW",
    }

    def to_points(data: dict) -> List[Dict]:
        points: List[Dict] = []
        for p in data.get("places", []):
            loc = p.get("location") or {}
            if loc.get("latitude") is None or loc.get("longitude") is None:
                continue
            points.append(
                {
                    "id": p.get("id", ""),
                    "name": (p.get("displayName") or {}).get("text", ""),
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                }
            )
        return points

    if query:
        payload = {**payload_base, "textQuery": query}
        data = _post_places(
            PLACES_TEXT_ENDPOINT,
            payload,
            "places.id,places.displayName,places.location",
        )
        points = to_points(data)
        deduped: Dict[str, Dict] = {}
        for point in points:
            name = (point.get("name") or "").strip()
            if not name:
                continue
            deduped.setdefault(name, point)
        return list(deduped.values())

    if district:
        text_query = f"{district} 交通站"
    else:
        text_query = "交通站"

    results: Dict[str, Dict] = {}
    for place_type in ["transit_station", "bus_stop"]:
        payload = {**payload_base, "textQuery": text_query, "includedType": place_type}
        data = _post_places(
            PLACES_TEXT_ENDPOINT,
            payload,
            "places.id,places.displayName,places.location",
        )
        for p in to_points(data):
            results[p["id"]] = p

    by_name: Dict[str, Dict] = {}
    for point in results.values():
        name = (point.get("name") or "").strip()
        if not name:
            continue
        by_name.setdefault(name, point)
    return list(by_name.values())


def _nearby_transit(lat: float, lng: float) -> Optional[Dict[str, object]]:
    payload = {
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 8000.0,
            }
        },
        "includedTypes": [
            "subway_station",
            "light_rail_station",
            "train_station",
            "transit_station",
        ],
        "maxResultCount": 1,
        "rankPreference": "DISTANCE",
        "languageCode": "zh-TW",
        "regionCode": "TW",
    }

    data = _post_places(
        PLACES_NEARBY_ENDPOINT,
        payload,
        "places.displayName,places.location",
    )
    places = data.get("places", [])
    if not places:
        return None

    place = places[0]
    loc = place.get("location") or {}
    name = (place.get("displayName") or {}).get("text", "")
    if not (loc.get("latitude") and loc.get("longitude")):
        return None

    distance_km = _haversine_km(lat, lng, loc["latitude"], loc["longitude"])
    return {
        "name": name,
        "distance_km": round(distance_km, 2),
        "walk_minutes": int(round((distance_km / 5) * 60)),
    }


def _text_transit(lat: float, lng: float) -> Optional[Dict[str, object]]:
    payload = {
        "textQuery": "捷運站",
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 8000.0,
            }
        },
        "maxResultCount": 1,
        "languageCode": "zh-TW",
        "regionCode": "TW",
    }

    data = _post_places(
        PLACES_TEXT_ENDPOINT,
        payload,
        "places.displayName,places.location",
    )
    places = data.get("places", [])
    if not places:
        return None

    place = places[0]
    loc = place.get("location") or {}
    name = (place.get("displayName") or {}).get("text", "")
    if not (loc.get("latitude") and loc.get("longitude")):
        return None

    distance_km = _haversine_km(lat, lng, loc["latitude"], loc["longitude"])
    return {
        "name": name,
        "distance_km": round(distance_km, 2),
        "walk_minutes": int(round((distance_km / 5) * 60)),
    }


def find_nearest_mrt(lat: float, lng: float) -> Optional[Dict[str, object]]:
    key = (round(lat, 4), round(lng, 4))
    cached = _MRT_CACHE.get(key)
    if cached:
        return cached

    result = _nearby_transit(lat, lng)
    if not result:
        result = _text_transit(lat, lng)
    if result:
        _MRT_CACHE[key] = result
    return result
