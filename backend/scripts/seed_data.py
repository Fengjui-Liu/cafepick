"""
Seed the database with sample cafe data for development and testing.

Usage:
    cd backend && python -m scripts.seed_data
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine, Base, SessionLocal
from app.models.cafe import Cafe

SAMPLE_CAFES = [
    # === 大安區 ===
    {
        "id": "demo-001",
        "name": "Louisa Coffee 路易莎 (忠孝復興店)",
        "city": "taipei",
        "district": "大安區",
        "address": "台北市大安區忠孝東路三段217號",
        "latitude": 25.0416,
        "longitude": 121.5436,
        "mrt": "忠孝復興",
        "open_time": "07:00-22:00",
        "wifi": 4.0, "socket": 4.5, "quiet": 3.0, "tasty": 3.5,
        "cheap": 4.5, "music": 3.0, "seat": 3.5,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-010",
        "name": "Notch 咖啡 (永康店)",
        "city": "taipei",
        "district": "大安區",
        "address": "台北市大安區永康街75號",
        "latitude": 25.0315,
        "longitude": 121.5295,
        "mrt": "東門",
        "open_time": "08:00-22:00",
        "wifi": 4.5, "socket": 4.5, "quiet": 3.5, "tasty": 4.0,
        "cheap": 3.5, "music": 3.5, "seat": 4.0,
        "limited_time": "no", "standing_desk": "yes",
        "has_reservation": "yes", "url": "",
    },
    {
        "id": "demo-011",
        "name": "cafe MUJI 無印良品 (統一時代店)",
        "city": "taipei",
        "district": "大安區",
        "address": "台北市大安區忠孝東路四段280號B1",
        "latitude": 25.0412,
        "longitude": 121.5485,
        "mrt": "忠孝敦化",
        "open_time": "11:00-21:30",
        "wifi": 3.5, "socket": 1.0, "quiet": 3.0, "tasty": 3.5,
        "cheap": 3.0, "music": 4.0, "seat": 3.0,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-012",
        "name": "All Day Roasting Company",
        "city": "taipei",
        "district": "大安區",
        "address": "台北市大安區仁愛路四段27巷6號",
        "latitude": 25.0387,
        "longitude": 121.5445,
        "mrt": "忠孝敦化",
        "open_time": "08:00-18:00",
        "wifi": 4.0, "socket": 3.5, "quiet": 4.0, "tasty": 4.5,
        "cheap": 2.0, "music": 4.5, "seat": 2.5,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    # === 中山區 ===
    {
        "id": "demo-002",
        "name": "Cafe de Gear",
        "city": "taipei",
        "district": "中山區",
        "address": "台北市中山區伊通街35號",
        "latitude": 25.0522,
        "longitude": 121.5334,
        "mrt": "松江南京",
        "open_time": "12:00-22:00",
        "wifi": 4.5, "socket": 4.0, "quiet": 4.5, "tasty": 4.0,
        "cheap": 2.5, "music": 4.5, "seat": 3.0,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "yes", "url": "",
    },
    {
        "id": "demo-006",
        "name": "Ruins Coffee Roasters",
        "city": "taipei",
        "district": "中山區",
        "address": "台北市中山區民生東路二段38號",
        "latitude": 25.0574,
        "longitude": 121.5283,
        "mrt": "中山國小",
        "open_time": "10:00-20:00",
        "wifi": 3.0, "socket": 2.5, "quiet": 4.5, "tasty": 4.5,
        "cheap": 2.5, "music": 5.0, "seat": 2.0,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-013",
        "name": "星巴克 Starbucks (南京門市)",
        "city": "taipei",
        "district": "中山區",
        "address": "台北市中山區南京東路二段1號",
        "latitude": 25.0523,
        "longitude": 121.5283,
        "mrt": "中山",
        "open_time": "07:00-22:00",
        "wifi": 4.0, "socket": 3.0, "quiet": 2.5, "tasty": 3.5,
        "cheap": 2.5, "music": 3.5, "seat": 3.5,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    # === 松山區 ===
    {
        "id": "demo-003",
        "name": "Fika Fika Cafe",
        "city": "taipei",
        "district": "松山區",
        "address": "台北市松山區伊通街33號",
        "latitude": 25.0518,
        "longitude": 121.5330,
        "mrt": "松江南京",
        "open_time": "10:00-18:00",
        "wifi": 3.5, "socket": 2.0, "quiet": 4.0, "tasty": 5.0,
        "cheap": 2.0, "music": 4.5, "seat": 2.5,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-007",
        "name": "cama café (南京復興店)",
        "city": "taipei",
        "district": "松山區",
        "address": "台北市松山區南京東路三段261號",
        "latitude": 25.0520,
        "longitude": 121.5445,
        "mrt": "南京復興",
        "open_time": "07:30-21:00",
        "wifi": 3.0, "socket": 3.5, "quiet": 2.5, "tasty": 3.5,
        "cheap": 4.5, "music": 2.5, "seat": 2.5,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-014",
        "name": "Pergamin Cafe",
        "city": "taipei",
        "district": "松山區",
        "address": "台北市松山區民生東路五段36巷8弄62號",
        "latitude": 25.0585,
        "longitude": 121.5620,
        "mrt": "南京三民",
        "open_time": "09:00-18:00",
        "wifi": 4.0, "socket": 3.0, "quiet": 4.5, "tasty": 4.5,
        "cheap": 2.5, "music": 4.0, "seat": 2.0,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "yes", "url": "",
    },
    # === 信義區 ===
    {
        "id": "demo-004",
        "name": "WOOLLOOMOOLOO (信義店)",
        "city": "taipei",
        "district": "信義區",
        "address": "台北市信義區信義路四段379號",
        "latitude": 25.0330,
        "longitude": 121.5565,
        "mrt": "市政府",
        "open_time": "08:00-21:00",
        "wifi": 4.0, "socket": 3.0, "quiet": 3.5, "tasty": 4.5,
        "cheap": 2.0, "music": 4.5, "seat": 3.5,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "yes", "url": "",
    },
    {
        "id": "demo-008",
        "name": "Mellow Fields 好丘 (信義店)",
        "city": "taipei",
        "district": "信義區",
        "address": "台北市信義區松勤街54號",
        "latitude": 25.0315,
        "longitude": 121.5582,
        "mrt": "台北101/世貿",
        "open_time": "09:00-18:00",
        "wifi": 3.5, "socket": 1.5, "quiet": 3.0, "tasty": 4.0,
        "cheap": 2.0, "music": 5.0, "seat": 3.0,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "yes", "url": "",
    },
    # === 中正區 ===
    {
        "id": "demo-005",
        "name": "伯朗咖啡館 (站前店)",
        "city": "taipei",
        "district": "中正區",
        "address": "台北市中正區館前路8號",
        "latitude": 25.0460,
        "longitude": 121.5150,
        "mrt": "台北車站",
        "open_time": "07:00-22:00",
        "wifi": 3.5, "socket": 4.0, "quiet": 2.5, "tasty": 3.0,
        "cheap": 4.0, "music": 2.5, "seat": 4.0,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-015",
        "name": "Percent Arabica (南昌門市)",
        "city": "taipei",
        "district": "中正區",
        "address": "台北市中正區南昌路一段1號",
        "latitude": 25.0350,
        "longitude": 121.5170,
        "mrt": "中正紀念堂",
        "open_time": "10:00-19:00",
        "wifi": 2.0, "socket": 1.0, "quiet": 3.5, "tasty": 4.5,
        "cheap": 1.5, "music": 4.0, "seat": 2.0,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    # === 大同區 ===
    {
        "id": "demo-009",
        "name": "Starbucks 星巴克 (典藏大稻埕門市)",
        "city": "taipei",
        "district": "大同區",
        "address": "台北市大同區保安街11號",
        "latitude": 25.0570,
        "longitude": 121.5100,
        "mrt": "大橋頭",
        "open_time": "07:00-21:30",
        "wifi": 4.0, "socket": 3.5, "quiet": 3.0, "tasty": 3.5,
        "cheap": 2.5, "music": 4.0, "seat": 3.5,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    {
        "id": "demo-016",
        "name": "保安捌肆 Boan 84",
        "city": "taipei",
        "district": "大同區",
        "address": "台北市大同區保安街84號",
        "latitude": 25.0560,
        "longitude": 121.5105,
        "mrt": "大橋頭",
        "open_time": "11:00-19:00",
        "wifi": 3.0, "socket": 1.0, "quiet": 4.5, "tasty": 4.0,
        "cheap": 2.5, "music": 5.0, "seat": 2.0,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    # === 萬華區 ===
    {
        "id": "demo-017",
        "name": "Cafe Flâneur 浪人咖啡",
        "city": "taipei",
        "district": "萬華區",
        "address": "台北市萬華區康定路25巷12號",
        "latitude": 25.0395,
        "longitude": 121.5033,
        "mrt": "龍山寺",
        "open_time": "13:00-22:00",
        "wifi": 4.0, "socket": 3.5, "quiet": 4.0, "tasty": 4.0,
        "cheap": 3.0, "music": 4.5, "seat": 2.5,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    # === 內湖區 ===
    {
        "id": "demo-018",
        "name": "Louisa Coffee 路易莎 (內湖成功店)",
        "city": "taipei",
        "district": "內湖區",
        "address": "台北市內湖區成功路四段182巷6號",
        "latitude": 25.0780,
        "longitude": 121.5880,
        "mrt": "內湖",
        "open_time": "07:00-22:00",
        "wifi": 4.0, "socket": 4.5, "quiet": 3.0, "tasty": 3.0,
        "cheap": 4.5, "music": 2.5, "seat": 4.0,
        "limited_time": "no", "standing_desk": "no",
        "has_reservation": "no", "url": "",
    },
    # === 文山區 ===
    {
        "id": "demo-019",
        "name": "Café Latte Art 拉花咖啡 (政大店)",
        "city": "taipei",
        "district": "文山區",
        "address": "台北市文山區指南路二段64號",
        "latitude": 24.9870,
        "longitude": 121.5760,
        "mrt": "動物園",
        "open_time": "09:00-21:00",
        "wifi": 4.5, "socket": 4.0, "quiet": 4.0, "tasty": 3.5,
        "cheap": 4.0, "music": 3.0, "seat": 3.5,
        "limited_time": "no", "standing_desk": "yes",
        "has_reservation": "yes", "url": "",
    },
    # === 士林區 ===
    {
        "id": "demo-020",
        "name": "mojocoffee (天母店)",
        "city": "taipei",
        "district": "士林區",
        "address": "台北市士林區天母東路8巷38號",
        "latitude": 25.1135,
        "longitude": 121.5295,
        "mrt": "芝山",
        "open_time": "08:00-18:00",
        "wifi": 3.5, "socket": 2.0, "quiet": 4.0, "tasty": 4.5,
        "cheap": 2.0, "music": 4.0, "seat": 2.5,
        "limited_time": "yes", "standing_desk": "no",
        "has_reservation": "yes", "url": "",
    },
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    count = 0
    for item in SAMPLE_CAFES:
        existing = db.query(Cafe).filter(Cafe.id == item["id"]).first()
        if existing:
            for key, val in item.items():
                if key != "id":
                    setattr(existing, key, val)
        else:
            db.add(Cafe(**item))
        count += 1

    db.commit()
    db.close()
    print(f"Seeded {count} sample cafes.")


if __name__ == "__main__":
    main()
