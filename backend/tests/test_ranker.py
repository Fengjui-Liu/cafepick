import pytest

from app.services.ranker import WEIGHTS, rank, reasons, score


def cafe(id, **kw):
    base = {"id": id, "name": id, "walk_minutes": 5, "rating": 4.3,
            "user_ratings_total": 300, "open_now": True, "work": None}
    base.update(kw)
    return base


def work(**kw):
    w = {"wifi": None, "socket": None, "quiet": None, "seat": None, "tasty": None,
         "cheap": None, "music": None, "limited_time": None, "standing_desk": None,
         "open_time": None}
    w.update(kw)
    return w


def test_weights_sum_to_one():
    for mode, weights in WEIGHTS.items():
        assert sum(weights.values()) == pytest.approx(1.0), mode


def test_work_mode_prefers_laptop_friendly_shop():
    laptop = cafe("laptop", rating=4.0, work=work(socket=5, wifi=5, quiet=4, limited_time="no"))
    pretty = cafe("pretty", rating=4.8, user_ratings_total=2000,
                  work=work(socket=1, wifi=2, limited_time="yes"))
    assert [r["cafe"]["id"] for r in rank([pretty, laptop], "work")] == ["laptop", "pretty"]
    assert [r["cafe"]["id"] for r in rank([pretty, laptop], "date")] == ["pretty", "laptop"]


def test_quick_mode_prefers_nearest():
    near = cafe("near", walk_minutes=1, rating=4.0)
    far = cafe("far", walk_minutes=12, rating=4.7)
    assert rank([far, near], "quick")[0]["cafe"]["id"] == "near"


def test_unknown_data_is_neutral_not_zero():
    unknown = cafe("unknown")
    bad = cafe("bad", work=work(socket=1, wifi=1, quiet=1, seat=1, limited_time="yes"))
    assert score(unknown, "work")[0] > score(bad, "work")[0]


def test_closed_and_too_far_are_filtered():
    ids = [r["cafe"]["id"] for r in rank(
        [cafe("closed", open_now=False), cafe("far", walk_minutes=25), cafe("ok"), cafe("unsure", open_now=None)],
        "quick", max_walk_minutes=15)]
    assert set(ids) == {"ok", "unsure"}


def test_pet_toggle_excludes_no_and_puts_unknown_last():
    shops = [cafe("unknown", walk_minutes=1),
             cafe("no", pet_friendly=False, walk_minutes=1),
             cafe("yes", pet_friendly=True, walk_minutes=10)]
    ranked = rank(shops, "quick", pet=True)
    assert [r["cafe"]["id"] for r in ranked] == ["yes", "unknown"]
    assert [r["pet_status"] for r in ranked] == ["yes", "unknown"]
    assert len(rank(shops, "quick", pet=False)) == 3


def test_exclude_for_show_more():
    ids = [r["cafe"]["id"] for r in rank([cafe("a"), cafe("b"), cafe("c")], "quick", exclude={"a", "b"})]
    assert ids == ["c"]


def test_reasons_lead_with_walk_and_name_strong_factors():
    shop = cafe("s", walk_minutes=4, work=work(socket=5, wifi=4.5, limited_time="no", quiet=2))
    _, values = score(shop, "work")
    assert reasons(shop, "work", values) == ["走路 4 分", "插座多", "不限時"]
    assert reasons(shop, "work", values, limit=4)[-1] == "WiFi 穩"


def test_reasons_flag_unknown_work_info():
    shop = cafe("s")
    _, values = score(shop, "work")
    assert reasons(shop, "work", values)[-1] == "工作條件未知"


def test_nomad_only_shops_rank_slightly_lower():
    google = cafe("g", work=work(socket=4))
    nomad = cafe("n", work=work(socket=4), source="nomad")
    assert rank([nomad, google], "work")[0]["cafe"]["id"] == "g"


def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        rank([], "party")
