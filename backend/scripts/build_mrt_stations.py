"""
Rebuild backend/data/mrt_stations.json (Greater Taipei MRT station coordinates).

Usage:
    cd backend && python -m scripts.build_mrt_stations
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.mrt import STATIONS_PATH
from app.services.mrt_builder import build, station_lines


def main():
    failed = build()
    total = len(station_lines())
    print(f"Wrote {total - len(failed)}/{total} stations to {os.path.abspath(STATIONS_PATH)}")
    if failed:
        print("Could not geocode (add them by hand):", "、".join(failed))


if __name__ == "__main__":
    main()
