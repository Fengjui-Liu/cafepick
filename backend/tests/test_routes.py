from fastapi.testclient import TestClient

from app.main import app
from app.services import recommend as recommend_service
from app.services import nomad_store
from tests.conftest import nomad_item


def test_status(temp_db, stations):
    nomad_store.save([nomad_item()])
    body = TestClient(app).get("/api/status").json()
    assert body["nomad_cafes"] == 1 and body["mrt_stations"] == 3


def test_places_error_is_explained(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError('Places API error 403: {"error": {"status": "PERMISSION_DENIED", "details": [{"reason": "API_KEY_HTTP_REFERRER_BLOCKED"}]}}')

    monkeypatch.setattr(recommend_service, "search_nearby_cafes", boom)
    res = TestClient(app).get("/api/recommend", params={"lat": 25.04, "lng": 121.54})
    assert res.status_code == 502
    assert "網站（HTTP 參照網址）限制" in res.json()["detail"]
