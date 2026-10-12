from app.services.matcher import best_match, similarity, tokens


def test_tokens_strip_generic_words_and_branch_suffix():
    assert tokens("路易莎咖啡 Louisa Coffee 忠孝復興門市") == {"路易莎", "louisa", "忠孝復興"}
    assert tokens("Louisa Coffee 路易莎 (忠孝復興店)") == {"louisa", "路易莎", "忠孝復興"}


def test_same_shop_with_different_decoration_is_similar():
    assert similarity("路易莎咖啡 Louisa Coffee 忠孝復興門市", "Louisa Coffee 路易莎 (忠孝復興店)") >= 0.9
    assert similarity("好丘 Good Cho's 信義店", "Mellow Fields 好丘 (信義店)") >= 0.6
    assert similarity("ＣＡＭＡ ＣＯＦＦＥＥ 南京復興", "cama café (南京復興店)") >= 0.6


def test_different_shops_are_not_similar():
    assert similarity("星巴克 忠孝復興門市", "Louisa Coffee 路易莎 (忠孝復興店)") < 0.6
    assert similarity("Fika Fika Cafe", "Cafe de Gear") < 0.6


def test_best_match_respects_distance_and_threshold():
    louisa = {"id": "n1", "name": "Louisa Coffee 路易莎 (忠孝復興店)"}
    other = {"id": "n2", "name": "Cafe de Gear"}
    name = "路易莎咖啡 Louisa Coffee 忠孝復興門市"

    assert best_match(name, [(0.03, other), (0.05, louisa)])[0] is louisa
    assert best_match(name, [(0.09, louisa)]) is None  # beyond 80 m
    assert best_match(name, [(0.01, other)]) is None  # right next door but unrelated


def test_very_close_allows_looser_name():
    shop = {"id": "n3", "name": "Coffee Lab 實驗室"}
    assert best_match("實驗室咖啡", [(0.01, shop)]) is not None


def test_shared_place_word_alone_is_not_a_match():
    assert similarity("Fika 信義", "Gear 信義") < 0.6
    assert similarity("木木咖啡 東門", "Simple Kaffa 東門") < 0.6
