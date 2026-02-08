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
    {
        "id": "demo-001",
        "name": "Louisa Coffee 路易莎 (忠孝復興店)",
        "city": "taipei",
        "address": "台北市大安區忠孝東路三段217號",
        "latitude": 25.0416,
        "longitude": 121.5436,
        "mrt": "忠孝復興",
        "open_time": "07:00-22:00",
        "wifi": 4.0,
        "socket": 4.5,
        "quiet": 3.0,
        "tasty": 3.5,
        "cheap": 4.5,
        "music": 3.0,
        "seat": 3.5,
        "limited_time": "no",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-002",
        "name": "Cafe de Gear",
        "city": "taipei",
        "address": "台北市中山區伊通街35號",
        "latitude": 25.0522,
        "longitude": 121.5334,
        "mrt": "松江南京",
        "open_time": "12:00-22:00",
        "wifi": 4.5,
        "socket": 4.0,
        "quiet": 4.5,
        "tasty": 4.0,
        "cheap": 2.5,
        "music": 4.5,
        "seat": 3.0,
        "limited_time": "no",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-003",
        "name": "Fika Fika Cafe",
        "city": "taipei",
        "address": "台北市松山區伊通街33號",
        "latitude": 25.0518,
        "longitude": 121.5330,
        "mrt": "松江南京",
        "open_time": "10:00-18:00",
        "wifi": 3.5,
        "socket": 2.0,
        "quiet": 4.0,
        "tasty": 5.0,
        "cheap": 2.0,
        "music": 4.5,
        "seat": 2.5,
        "limited_time": "yes",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-004",
        "name": "WOOLLOOMOOLOO (信義店)",
        "city": "taipei",
        "address": "台北市信義區信義路四段379號",
        "latitude": 25.0330,
        "longitude": 121.5565,
        "mrt": "市政府",
        "open_time": "08:00-21:00",
        "wifi": 4.0,
        "socket": 3.0,
        "quiet": 3.5,
        "tasty": 4.5,
        "cheap": 2.0,
        "music": 4.5,
        "seat": 3.5,
        "limited_time": "no",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-005",
        "name": "伯朗咖啡館 (站前店)",
        "city": "taipei",
        "address": "台北市中正區館前路8號",
        "latitude": 25.0460,
        "longitude": 121.5150,
        "mrt": "台北車站",
        "open_time": "07:00-22:00",
        "wifi": 3.5,
        "socket": 4.0,
        "quiet": 2.5,
        "tasty": 3.0,
        "cheap": 4.0,
        "music": 2.5,
        "seat": 4.0,
        "limited_time": "no",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-006",
        "name": "Ruins Coffee Roasters",
        "city": "taipei",
        "address": "台北市中山區民生東路二段38號",
        "latitude": 25.0574,
        "longitude": 121.5283,
        "mrt": "中山國小",
        "open_time": "10:00-20:00",
        "wifi": 3.0,
        "socket": 2.5,
        "quiet": 4.5,
        "tasty": 4.5,
        "cheap": 2.5,
        "music": 5.0,
        "seat": 2.0,
        "limited_time": "yes",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-007",
        "name": "cama café (南京復興店)",
        "city": "taipei",
        "address": "台北市松山區南京東路三段261號",
        "latitude": 25.0520,
        "longitude": 121.5445,
        "mrt": "南京復興",
        "open_time": "07:30-21:00",
        "wifi": 3.0,
        "socket": 3.5,
        "quiet": 2.5,
        "tasty": 3.5,
        "cheap": 4.5,
        "music": 2.5,
        "seat": 2.5,
        "limited_time": "no",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-008",
        "name": "Mellow Fields 好丘 (信義店)",
        "city": "taipei",
        "address": "台北市信義區松勤街54號",
        "latitude": 25.0315,
        "longitude": 121.5582,
        "mrt": "台北101/世貿",
        "open_time": "09:00-18:00",
        "wifi": 3.5,
        "socket": 1.5,
        "quiet": 3.0,
        "tasty": 4.0,
        "cheap": 2.0,
        "music": 5.0,
        "seat": 3.0,
        "limited_time": "yes",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-009",
        "name": "Starbucks 星巴克 (典藏大稻埕門市)",
        "city": "taipei",
        "address": "台北市大同區保安街11號",
        "latitude": 25.0570,
        "longitude": 121.5100,
        "mrt": "大橋頭",
        "open_time": "07:00-21:30",
        "wifi": 4.0,
        "socket": 3.5,
        "quiet": 3.0,
        "tasty": 3.5,
        "cheap": 2.5,
        "music": 4.0,
        "seat": 3.5,
        "limited_time": "no",
        "standing_desk": "no",
        "url": "",
    },
    {
        "id": "demo-010",
        "name": "Notch 咖啡 (永康店)",
        "city": "taipei",
        "address": "台北市大安區永康街75號",
        "latitude": 25.0315,
        "longitude": 121.5295,
        "mrt": "東門",
        "open_time": "08:00-22:00",
        "wifi": 4.5,
        "socket": 4.5,
        "quiet": 3.5,
        "tasty": 4.0,
        "cheap": 3.5,
        "music": 3.5,
        "seat": 4.0,
        "limited_time": "no",
        "standing_desk": "yes",
        "url": "",
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
