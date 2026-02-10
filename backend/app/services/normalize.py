"""
Utilities for normalizing Cafe Nomad data:
- MRT station name cleanup (strip exit numbers, walking directions)
- District extraction from addresses
"""

import re

# Pattern to strip MRT exit numbers, walking directions, etc.
# Examples:
#   "忠孝復興站2號出口" → "忠孝復興"
#   "捷運松江南京站1號出口步行3分鐘" → "松江南京"
#   "南京復興站 3號出口" → "南京復興"
#   "台北101/世貿" → "台北101/世貿"
_MRT_CLEANUP_PATTERNS = [
    r"捷運",           # Remove "捷運" prefix
    r"站\s*\d*號?出口.*",  # "站2號出口步行3分鐘" etc.
    r"站$",            # Trailing "站"
    r"\s*\d+號出口.*",    # Standalone exit number
    r"\s*步行.*",        # Walking directions
    r"\s*走路.*",        # Walking directions variant
    r"\s*約.*分鐘",      # "約5分鐘"
]


def normalize_mrt(raw_mrt: str) -> str:
    """Normalize a messy MRT station name to just the core station name."""
    if not raw_mrt:
        return ""

    name = raw_mrt.strip()

    for pattern in _MRT_CLEANUP_PATTERNS:
        name = re.sub(pattern, "", name)

    return name.strip()


# Taipei districts mapping (行政區)
TAIPEI_DISTRICTS = [
    "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區",
    "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區",
]

NEW_TAIPEI_DISTRICTS = [
    "板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區",
    "土城區", "蘆洲區", "汐止區", "樹林區", "鶯歌區", "三峽區",
    "淡水區", "瑞芳區", "五股區", "泰山區", "林口區", "深坑區",
    "石碇區", "坪林區", "三芝區", "石門區", "八里區", "平溪區",
    "雙溪區", "貢寮區", "金山區", "萬里區", "烏來區",
]


def extract_district(address: str) -> str:
    """Extract the district (行政區) from a Taiwanese address.

    Example: "台北市大安區忠孝東路三段217號" → "大安區"
    """
    if not address:
        return ""

    # Try to match district pattern: X市/縣 + YY區
    match = re.search(r"[市縣](\w{2,3}區)", address)
    if match:
        return match.group(1)

    # Fallback: search for known district names
    all_districts = TAIPEI_DISTRICTS + NEW_TAIPEI_DISTRICTS
    for d in all_districts:
        if d in address:
            return d

    return ""


# Mapping for quiet score to human-readable labels
QUIET_LABELS = {
    "lively": {"label": "熱鬧", "min": 0, "max": 2},
    "moderate": {"label": "普通", "min": 2, "max": 3.5},
    "quiet": {"label": "安靜", "min": 3.5, "max": 5.1},
}

# Mapping for price (cheap score) to price range
PRICE_RANGES = {
    "budget": {"label": "平價 (< $100)", "min_cheap": 4, "max_cheap": 5.1},
    "moderate": {"label": "中等 ($100-200)", "min_cheap": 2.5, "max_cheap": 4},
    "pricey": {"label": "較貴 (> $200)", "min_cheap": 0, "max_cheap": 2.5},
}
