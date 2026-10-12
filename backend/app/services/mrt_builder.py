"""
Builds backend/data/mrt_stations.json: every Greater Taipei MRT / light-rail
station with coordinates, geocoded once through the Google Places API.

The backend runs this automatically on first start when the file is missing.
To run it by hand (e.g. after a new line opens):

    cd backend && python -m scripts.build_mrt_stations

Station names below are the source of truth; edit them here, not in the JSON.
"""

import json
import os
from typing import Dict, List, Optional

from app.services.google_places import PLACES_TEXT_ENDPOINT, _post_places
from app.services import mrt

LINES: Dict[str, List[str]] = {
    "文湖線": [
        "動物園", "木柵", "萬芳社區", "萬芳醫院", "辛亥", "麟光", "六張犁",
        "科技大樓", "大安", "忠孝復興", "南京復興", "中山國中", "松山機場",
        "大直", "劍南路", "西湖", "港墘", "文德", "內湖", "大湖公園", "葫洲",
        "東湖", "南港軟體園區", "南港展覽館",
    ],
    "淡水信義線": [
        "象山", "台北101/世貿", "信義安和", "大安", "大安森林公園", "東門",
        "中正紀念堂", "台大醫院", "台北車站", "中山", "雙連", "民權西路",
        "圓山", "劍潭", "士林", "芝山", "明德", "石牌", "唭哩岸", "奇岩",
        "北投", "新北投", "復興崗", "忠義", "關渡", "竹圍", "紅樹林", "淡水",
    ],
    "松山新店線": [
        "新店", "新店區公所", "七張", "小碧潭", "大坪林", "景美", "萬隆",
        "公館", "台電大樓", "古亭", "中正紀念堂", "小南門", "西門", "北門",
        "中山", "松江南京", "南京復興", "台北小巨蛋", "南京三民", "松山",
    ],
    "中和新蘆線": [
        "南勢角", "景安", "永安市場", "頂溪", "古亭", "東門", "忠孝新生",
        "松江南京", "行天宮", "中山國小", "民權西路", "大橋頭", "台北橋",
        "菜寮", "三重", "先嗇宮", "頭前庄", "新莊", "輔大", "丹鳳", "迴龍",
        "三重國小", "三和國中", "徐匯中學", "三民高中", "蘆洲",
    ],
    "板南線": [
        "頂埔", "永寧", "土城", "海山", "亞東醫院", "府中", "板橋", "新埔",
        "江子翠", "龍山寺", "西門", "台北車站", "善導寺", "忠孝新生",
        "忠孝復興", "忠孝敦化", "國父紀念館", "市政府", "永春", "後山埤",
        "昆陽", "南港", "南港展覽館",
    ],
    "環狀線": [
        "大坪林", "十四張", "秀朗橋", "景平", "景安", "中和", "橋和", "中原",
        "板新", "板橋", "新埔民生", "頭前庄", "幸福", "新北產業園區",
    ],
    "機場捷運": [
        "台北車站", "三重", "新北產業園區", "新莊副都心", "泰山", "泰山貴和",
        "體育大學", "長庚醫院", "林口",
    ],
    "淡海輕軌": [
        "紅樹林", "竿蓁林", "淡金鄧公", "淡江大學", "淡金北新", "新市一路",
        "淡水行政中心", "濱海義山", "濱海沙崙", "淡海新市鎮", "崁頂",
        "台北海洋大學", "沙崙", "淡水漁人碼頭",
    ],
    "安坑輕軌": [
        "雙城", "玫瑰中國城", "台北小城", "耕莘安康院區", "景文科大", "安康",
        "陽光運動公園", "新和國小", "十四張",
    ],
}

LIGHT_RAIL = {"淡海輕軌", "安坑輕軌"}

# Rough bounding box of Taipei + New Taipei (incl. Linkou); rejects bad geocodes.
BBOX = (24.67, 25.31, 121.28, 122.01)  # lat_min, lat_max, lng_min, lng_max


def station_lines() -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for line, names in LINES.items():
        for name in names:
            result.setdefault(name, []).append(line)
    return result


def _query(name: str, lines: List[str]) -> str:
    if all(line in LIGHT_RAIL for line in lines):
        return f"輕軌{name}站"
    if lines == ["機場捷運"]:
        return f"機場捷運{name}站"
    return f"捷運{name}站"


def _in_bbox(lat: float, lng: float) -> bool:
    return BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lng <= BBOX[3]


def geocode(name: str, lines: List[str]) -> Optional[Dict]:
    payload = {
        "textQuery": _query(name, lines),
        "locationBias": {
            "circle": {
                "center": {"latitude": 25.04, "longitude": 121.53},
                "radius": 30000.0,
            }
        },
        "maxResultCount": 3,
        "languageCode": "zh-TW",
        "regionCode": "TW",
    }
    data = _post_places(
        PLACES_TEXT_ENDPOINT, payload, "places.displayName,places.location,places.types"
    )
    core = name.split("/")[0]
    for place in data.get("places", []):
        loc = place.get("location") or {}
        lat, lng = loc.get("latitude"), loc.get("longitude")
        label = (place.get("displayName") or {}).get("text", "")
        if lat is None or lng is None or not _in_bbox(lat, lng):
            continue
        if core in label:
            return {"latitude": lat, "longitude": lng}
    return None


def build() -> List[str]:
    """Geocode every station and write the table. Returns names that failed."""
    stations = []
    failed = []
    for name, lines in station_lines().items():
        loc = geocode(name, lines)
        if loc is None:
            failed.append(name)
            continue
        stations.append({"name": name, "lines": lines, **loc})

    path = mrt.STATIONS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False, indent=1)
    mrt.reload_stations()
    return failed

