from app.services import nomad_store
from app.services.enrich import enrich
from app.services.google_places import _parse_place
from tests.conftest import nomad_item


def google_place(**overrides):
    place = {
        "id": "g1",
        "displayName": {"text": "路易莎咖啡 Louisa Coffee 忠孝復興門市"},
        "formattedAddress": "106台灣台北市大安區忠孝東路三段217號",
        "location": {"latitude": 25.04165, "longitude": 121.54362},
        "rating": 4.2,
        "currentOpeningHours": {"openNow": True},
        "allowsDogs": False,
    }
    place.update(overrides)
    return place


def test_parse_place_keeps_unknown_distinct_from_no():
    assert _parse_place(google_place(), "taipei", None)["pet_friendly"] is False
    unknown = google_place()
    del unknown["allowsDogs"]
    assert _parse_place(unknown, "taipei", None)["pet_friendly"] is None
    assert _parse_place(google_place(), "taipei", None)["district"] == "大安區"
    assert _parse_place(google_place(formattedAddress="新北市板橋區文化路一段"), "newtaipei", None)["district"] == "板橋區"


def test_enrich_merges_nomad_and_mrt(temp_db, stations):
    nomad_store.save([nomad_item(music=0)])
    cafe = enrich(_parse_place(google_place(), "taipei", None))

    assert cafe["nomad"]["id"] == "n1"
    assert cafe["work"]["socket"] == 4.5
    assert cafe["work"]["limited_time"] == "no"
    assert cafe["work"]["music"] is None  # 0 = unrated
    assert cafe["nearest_mrt"]["name"] == "忠孝復興"
    assert cafe["mrt_station"] == "忠孝復興"


def test_enrich_without_nomad_match_marks_work_unknown(temp_db, stations):
    cafe = enrich(_parse_place(google_place(displayName={"text": "某間新開的店"}), "taipei", None))
    assert cafe["work"] is None and cafe["nomad"] is None
    assert cafe["nearest_mrt"]["name"] == "忠孝復興"
