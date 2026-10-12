from fastapi.testclient import TestClient

from app.main import app
from app.services import nomad_store
from app.services import recommend as recommend_service
from app.services.google_places import _parse_place
from tests.conftest import nomad_item
from tests.test_enrich import google_place

client = TestClient(app)


def _fake_nearby(places):
    calls = []

    def fake(lat, lng, radius_m, rank_by="DISTANCE", limit=20):
        calls.append((lat, lng, radius_m, rank_by))
        return [_parse_place(p, "taipei", None) for p in places]

    return fake, calls


def test_recommend_by_station_work_mode(temp_db, stations, monkeypatch):
    nomad_store.save([
        nomad_item(),  # matches the Google Louisa
        nomad_item(id="n9", name="安靜讀書咖啡", latitude="25.0430", longitude="121.5450",
                   socket=5, wifi=5, quiet=5, limited_time="no"),
    ])
    fake, calls = _fake_nearby([google_place()])
    monkeypatch.setattr(recommend_service, "search_nearby_cafes", fake)

    body = client.get("/api/recommend", params={"mode": "work", "station": "忠孝復興站"}).json()

    assert body["origin"]["label"] == "捷運忠孝復興站"
    assert calls[0][2] == 1500.0
    ids = [r["cafe"]["id"] for r in body["recommendations"]]
    assert set(ids) == {"g1", "nomad:n9"}  # Nomad-only shop added, Louisa not duplicated
    top = body["recommendations"][0]
    assert top["reasons"][0].startswith("走路")
    assert 0 <= top["score"] <= 100


def test_recommend_gps_quick_mode_with_pet_and_exclude(temp_db, stations, monkeypatch):
    dog = google_place(id="dog", displayName={"text": "狗狗咖啡"}, allowsDogs=True,
                       location={"latitude": 25.0425, "longitude": 121.5445})
    nodog = google_place(id="nodog", displayName={"text": "禁狗咖啡"}, allowsDogs=False)
    fake, calls = _fake_nearby([dog, nodog, google_place()])
    monkeypatch.setattr(recommend_service, "search_nearby_cafes", fake)

    body = client.get("/api/recommend", params={
        "mode": "quick", "lat": 25.0416, "lng": 121.5437, "pet": "true", "exclude": "g1"}).json()

    assert [r["cafe"]["id"] for r in body["recommendations"]] == ["dog"]
    assert body["recommendations"][0]["pet_status"] == "yes"
    assert calls[0][2] == 700.0


def test_recommend_needs_an_origin():
    assert client.get("/api/recommend").status_code == 422
    assert client.get("/api/recommend", params={"station": "不存在"}).status_code == 404


def test_stations_autocomplete(stations):
    names = [s["name"] for s in client.get("/api/stations", params={"q": "忠孝"}).json()["stations"]]
    assert set(names) == {"忠孝復興", "忠孝敦化"}
