"""
Lightweight migration to add new columns to the cafes table and backfill basics.
Usage:
    cd backend && python3 -m scripts.migrate_add_columns
"""

import os
import re
import sqlite3
from app.database import DB_PATH


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


def main() -> None:
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run import/seed first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(cafes)")
    existing = {row[1] for row in cur.fetchall()}

    columns = [
        ("district", "TEXT"),
        ("mrt_station", "TEXT"),
        ("bus_stop", "TEXT"),
        ("price", "REAL"),
        ("quiet_level", "TEXT"),
        ("has_wifi", "INTEGER"),
        ("has_socket", "INTEGER"),
        ("reservable", "INTEGER"),
    ]

    added = 0
    for name, col_type in columns:
        if name in existing:
            continue
        cur.execute(f"ALTER TABLE cafes ADD COLUMN {name} {col_type}")
        added += 1

    if added:
        print(f"Added {added} columns.")
    else:
        print("No new columns added.")

    # Backfill basic derived fields for existing rows
    cur.execute(
        "SELECT id, address, mrt, wifi, socket, quiet, cheap, has_wifi, has_socket, quiet_level, price, district, mrt_station FROM cafes"
    )
    rows = cur.fetchall()
    for (
        cafe_id,
        address,
        mrt,
        wifi,
        socket,
        quiet,
        cheap,
        has_wifi,
        has_socket,
        quiet_level,
        price,
        district,
        mrt_station,
    ) in rows:
        updates = {}
        if has_wifi is None:
            updates["has_wifi"] = 1 if (wifi or 0) > 0 else 0
        if has_socket is None:
            updates["has_socket"] = 1 if (socket or 0) > 0 else 0
        if quiet_level is None:
            updates["quiet_level"] = _quiet_level(float(quiet or 0))
        if price is None:
            updates["price"] = _price_from_cheap(float(cheap or 0))
        if district is None:
            updates["district"] = _parse_district(address or "")
        if mrt_station is None:
            updates["mrt_station"] = _normalize_mrt_station(mrt or "")

        if updates:
            sets = ", ".join(f"{k} = ?" for k in updates.keys())
            params = list(updates.values()) + [cafe_id]
            cur.execute(f"UPDATE cafes SET {sets} WHERE id = ?", params)

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    main()
