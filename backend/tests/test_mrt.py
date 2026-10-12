from app.services import mrt


def test_nearest_station(stations):
    near = mrt.nearest_station(25.0420, 121.5440)
    assert near["name"] == "忠孝復興"
    assert near["walk_minutes"] <= 1
    assert "板南線" in near["lines"]


def test_far_away_returns_none(stations):
    assert mrt.nearest_station(24.0, 121.0) is None


def test_missing_table_is_harmless(tmp_path, monkeypatch):
    monkeypatch.setattr(mrt, "STATIONS_PATH", str(tmp_path / "nope.json"))
    mrt.reload_stations()
    assert mrt.nearest_station(25.04, 121.54) is None
    assert not mrt.has_station_table()
    mrt.reload_stations()


def test_find_stations(stations):
    assert {s["name"] for s in mrt.find_stations("捷運忠孝站")} == {"忠孝復興", "忠孝敦化"}
