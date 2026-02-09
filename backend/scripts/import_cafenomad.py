"""
Import cafe data from Cafe Nomad API into local SQLite database.

Usage:
    python -m scripts.import_cafenomad
    python -m scripts.import_cafenomad --city taipei
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
import re
from app.database import engine, Base, SessionLocal
from app.models.cafe import Cafe

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


def fetch_cafes(city: str) -> list:
    """Fetch cafes for a city from Cafe Nomad API."""
    url = f"{CAFENOMAD_API}/{city}"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def import_city(db, city: str) -> int:
    """Import cafes for a single city. Returns count of imported cafes."""
    print(f"Fetching {city}...")
    try:
        data = fetch_cafes(city)
    except Exception as e:
        print(f"  Failed to fetch {city}: {e}")
        return 0

    count = 0
    for item in data:
        cafe_id = item.get("id")
        if not cafe_id:
            continue

        existing = db.query(Cafe).filter(Cafe.id == cafe_id).first()
        if existing:
            # Update existing record
            for key, val in _map_fields(item, city).items():
                setattr(existing, key, val)
        else:
            cafe = Cafe(id=cafe_id, **_map_fields(item, city))
            db.add(cafe)
        count += 1

    db.commit()
    print(f"  Imported {count} cafes from {city}")
    return count


def _map_fields(item: dict, city: str) -> dict:
    """Map Cafe Nomad API fields to our Cafe model."""
    wifi_score = _to_float(item.get("wifi"))
    socket_score = _to_float(item.get("socket"))
    quiet_score = _to_float(item.get("quiet"))
    mrt_raw = item.get("mrt", "")
    address = item.get("address", "")
    return {
        "name": item.get("name", ""),
        "city": city,
        "address": address,
        "district": _parse_district(address),
        "latitude": _to_float(item.get("latitude")),
        "longitude": _to_float(item.get("longitude")),
        "url": item.get("url", ""),
        "mrt": mrt_raw,
        "mrt_station": _normalize_mrt_station(mrt_raw),
        "open_time": item.get("open_time", ""),
        "wifi": wifi_score,
        "socket": socket_score,
        "quiet": quiet_score,
        "tasty": _to_float(item.get("tasty")),
        "cheap": _to_float(item.get("cheap")),
        "music": _to_float(item.get("music")),
        "seat": _to_float(item.get("seat")),
        "price": _price_from_cheap(_to_float(item.get("cheap"))),
        "quiet_level": _quiet_level(quiet_score),
        "has_wifi": wifi_score > 0,
        "has_socket": socket_score > 0,
        "reservable": None,
        "bus_stop": None,
        "limited_time": item.get("limited_time", ""),
        "standing_desk": item.get("standing_desk", ""),
    }


def _to_float(val) -> float:
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def _normalize_mrt_station(mrt: str) -> str:
    if not mrt:
        return ""
    value = re.sub(r"\(.*?\)", "", mrt)
    value = re.split(r"(出口|Exit)", value)[0]
    value = re.sub(r"\d+號?", "", value)
    value = re.split(r"[#／/、,;；]", value)[0]
    return value.strip()


def _parse_district(address: str) -> str:
    if not address:
        return ""
    match = re.search(r"([\u4e00-\u9fff]{1,3}區)", address)
    if match:
        return match.group(1)
    return _map_english_district(address)


def _map_english_district(address: str) -> str:
    normalized = address.lower()
    district_map = {
        "zhongzheng district": "中正區",
        "datong district": "大同區",
        "zhongshan district": "中山區",
        "songshan district": "松山區",
        "daan district": "大安區",
        "wanhua district": "萬華區",
        "xinyi district": "信義區",
        "shilin district": "士林區",
        "beitou district": "北投區",
        "neihu district": "內湖區",
        "nangang district": "南港區",
        "wenshan district": "文山區",
        "banqiao district": "板橋區",
        "sanchong district": "三重區",
        "zhonghe district": "中和區",
        "yonghe district": "永和區",
        "xinzhuang district": "新莊區",
        "xindian district": "新店區",
        "tucheng district": "土城區",
        "luzhou district": "蘆洲區",
        "shulin district": "樹林區",
        "yingge district": "鶯歌區",
        "sanxia district": "三峽區",
        "ruifang district": "瑞芳區",
        "tamsui district": "淡水區",
        "xizhi district": "汐止區",
        "shenkeng district": "深坑區",
        "shiding district": "石碇區",
        "pinglin district": "坪林區",
        "sanzhi district": "三芝區",
        "shimen district": "石門區",
        "bali district": "八里區",
        "pingxi district": "平溪區",
        "shuangxi district": "雙溪區",
        "gongliao district": "貢寮區",
        "jinshan district": "金山區",
        "wanli district": "萬里區",
        "wulai district": "烏來區",
        "taishan district": "泰山區",
    }
    for key, value in district_map.items():
        if key in normalized:
            return value
    return ""


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


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if specific city was requested
    cities = CITIES
    if len(sys.argv) > 2 and sys.argv[1] == "--city":
        cities = [sys.argv[2]]

    total = 0
    for city in cities:
        total += import_city(db, city)

    db.close()
    print(f"\nDone! Total: {total} cafes imported.")


if __name__ == "__main__":
    main()
