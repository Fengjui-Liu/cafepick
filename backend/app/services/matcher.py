"""
Decide whether a Google Places cafe and a Cafe Nomad cafe are the same shop.

Rule (see docs/DESIGN_v2.md §5): similar name AND within 80 m. Names are
compared as bags of tokens because the two sources order and decorate them
differently, e.g.

    Google: "路易莎咖啡 Louisa Coffee 忠孝復興門市"
    Nomad:  "Louisa Coffee 路易莎 (忠孝復興店)"
"""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import List, Optional, Set, Tuple

from app.services import nomad_store
from app.services.google_places import CITY_DISTRICTS
from app.services.mrt_builder import station_lines

MATCH_RADIUS_KM = 0.08
VERY_CLOSE_KM = 0.02
MIN_SIMILARITY = 0.6
MIN_SIMILARITY_VERY_CLOSE = 0.3

# Words that say "this is a cafe/branch" rather than which cafe it is.
_GENERIC = [
    "咖啡館", "咖啡廳", "咖啡店", "咖啡屋", "咖啡", "珈琲", "自家烘焙", "烘焙坊",
    "門市", "分店", "旗艦店", "總店", "本店", "工作室",
    "coffee roasters", "roasters", "roastery", "coffee", "café", "cafe",
    "caffè", "caffe", "kaffe", "espresso bar", "studio",
]
_TRAILING_STORE = re.compile(r"店$")
_TOKEN = re.compile(r"[㐀-鿿]+|[a-z0-9]+")
_CJK = re.compile(r"[㐀-鿿]")

# Place words (stations, districts) say where a branch is, not which shop it
# is: "Fika 信義" and "Gear 信義" must not match on 信義 alone.
_LOCATION_WORDS = set(station_lines()) | {
    d.rstrip("區") for city in ("taipei", "newtaipei") for d in CITY_DISTRICTS.get(city, [])
}


def _normalize(name: str) -> str:
    return unicodedata.normalize("NFKC", name or "").lower()


def tokens(name: str) -> Set[str]:
    text = _normalize(name)
    for word in _GENERIC:
        text = text.replace(word, " ")
    result = set()
    for tok in _TOKEN.findall(text):
        tok = _TRAILING_STORE.sub("", tok)
        if len(tok) >= 2 or tok.isdigit():
            result.add(tok)
    return result


def _token_overlap(a: Set[str], b: Set[str]) -> float:
    """Share of the smaller token set found in the other (substring-tolerant)."""
    if not a or not b:
        return 0.0
    small, large = (a, b) if len(a) <= len(b) else (b, a)
    hits = sum(1 for s in small if any(s in l or l in s for l in large))
    return hits / len(small)


def _is_location(tok: str) -> bool:
    return any(tok in word for word in _LOCATION_WORDS)


def _same_script_overlap(a: Set[str], b: Set[str]) -> float:
    """
    Bilingual names often share only one script: "好丘 Good Cho's" vs
    "Mellow Fields 好丘". Compare Chinese tokens and Latin tokens separately,
    but only count it when a shared token is a name, not a place.
    """
    best = 0.0
    for is_cjk in (True, False):
        sa = {t for t in a if bool(_CJK.match(t)) == is_cjk}
        sb = {t for t in b if bool(_CJK.match(t)) == is_cjk}
        shared = {s for s in sa if any(s in t or t in s for t in sb)}
        if any(not _is_location(t) for t in shared):
            best = max(best, 0.9 * _token_overlap(sa, sb))
    return best


def similarity(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    overlap = max(_token_overlap(ta, tb), _same_script_overlap(ta, tb))
    joined_a, joined_b = "".join(sorted(ta)), "".join(sorted(tb))
    ratio = SequenceMatcher(None, joined_a, joined_b).ratio() if joined_a and joined_b else 0.0
    return max(overlap, ratio)


def best_match(
    name: str, candidates: List[Tuple[float, dict]]
) -> Optional[Tuple[dict, float]]:
    """Pick the best (cafe, similarity) among (distance_km, cafe) candidates."""
    best = None
    best_score = -1.0
    for km, cafe in candidates:
        if km > MATCH_RADIUS_KM:
            continue
        sim = similarity(name, cafe.get("name", ""))
        threshold = MIN_SIMILARITY_VERY_CLOSE if km <= VERY_CLOSE_KM else MIN_SIMILARITY
        if sim < threshold:
            continue
        score = sim - 0.2 * (km / MATCH_RADIUS_KM)
        if score > best_score:
            best, best_score = (cafe, sim), score
    return best


def match_nomad(name: str, lat: float, lng: float) -> Optional[Tuple[dict, float]]:
    return best_match(name, nomad_store.nearby(lat, lng, MATCH_RADIUS_KM))
