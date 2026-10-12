from fastapi.testclient import TestClient

from app.main import app
from app.routes import cafes as cafes_route
from app.services import nomad_store
from app.services.google_places import _parse_place
from tests.conftest import nomad_item
from tests.test_enrich import google_place


def test_recommend_returns_enriched_cafes(temp_db, stations, monkeypatch):
    nomad_store.save([nomad_item()])
    monkeypatch.setattr(
        cafes_route, "search_places",
        lambda city, keyword, limit: [_parse_place(google_place(), city, keyword)],
    )
    res = TestClient(app).get("/api/cafes/recommend", params={"city": "taipei"})
    assert res.status_code == 200
    cafe = res.json()["recommendations"][0]["cafe"]
    assert cafe["work"]["wifi"] == 4
    assert cafe["open_now"] is True
    assert cafe["mrt_walk_minutes"] == 0


def test_status(temp_db, stations):
    nomad_store.save([nomad_item()])
    body = TestClient(app).get("/api/status").json()
    assert body["nomad_cafes"] == 1 and body["mrt_stations"] == 3
