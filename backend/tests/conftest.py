import json
import os

os.environ.setdefault("CAFEPICK_SKIP_REFRESH", "1")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import cafe as _cafe, sync_state as _sync  # noqa: F401
from app.services import mrt, nomad_store

STATIONS = [
    {"name": "忠孝復興", "lines": ["文湖線", "板南線"], "latitude": 25.0416, "longitude": 121.5438},
    {"name": "忠孝敦化", "lines": ["板南線"], "latitude": 25.0414, "longitude": 121.5509},
    {"name": "東門", "lines": ["淡水信義線", "中和新蘆線"], "latitude": 25.0339, "longitude": 121.5288},
]


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)
    monkeypatch.setattr(nomad_store, "SessionLocal", session)
    nomad_store.invalidate_index()
    yield session
    nomad_store.invalidate_index()


@pytest.fixture
def stations(tmp_path, monkeypatch):
    path = tmp_path / "mrt_stations.json"
    path.write_text(json.dumps(STATIONS, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(mrt, "STATIONS_PATH", str(path))
    mrt.reload_stations()
    yield STATIONS
    mrt.reload_stations()


def nomad_item(**overrides):
    item = {
        "id": "n1", "name": "Louisa Coffee 路易莎 (忠孝復興店)",
        "address": "台北市大安區忠孝東路三段217號",
        "latitude": "25.0416", "longitude": "121.5436",
        "wifi": 4, "socket": 4.5, "quiet": 3, "tasty": 3.5, "cheap": 4.5,
        "music": 3, "seat": 3.5, "limited_time": "no", "standing_desk": "no",
        "mrt": "忠孝復興站2號出口", "url": "", "open_time": "07:00-22:00",
    }
    item.update(overrides)
    return item
