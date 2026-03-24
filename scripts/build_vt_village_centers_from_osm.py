#!/usr/bin/env python3
"""Fetch OSM village/hamlet (etc.) centers in the five-county study area and write vt_village_centers.csv.

Requires network. Uses Overpass API + counties_five_vt.geojson for clipping.
Run from repo root:  uv run python scripts/build_vt_village_centers_from_osm.py
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.request
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

REPO = Path(__file__).resolve().parents[1]
COUNTIES_GEOJSON = REPO / "data" / "counties_five_vt.geojson"
OUT_CSV = REPO / "data" / "vt_village_centers.csv"

# South, West, North, East — generous bbox around five counties
BBOX = (44.05, -73.05, 45.08, -71.40)

# village + hamlet only (exclude locality — not distinct villages in this project)
PLACE_REGEX = "^(village|hamlet)$"


def overpass_places() -> list[dict]:
    south, west, north, east = BBOX
    query = f"""
[out:json][timeout:300];
(
  node["place"~"{PLACE_REGEX}"]({south},{west},{north},{east});
  way["place"~"{PLACE_REGEX}"]({south},{west},{north},{east});
);
out center tags;
"""
    url = "https://overpass-api.de/api/interpreter"
    req = urllib.request.Request(
        url,
        data=query.encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=320) as resp:
        data = json.loads(resp.read().decode())
    return data.get("elements", [])


def element_lonlat(el: dict) -> tuple[float, float] | None:
    if el["type"] == "node":
        return float(el["lon"]), float(el["lat"])
    if el["type"] == "way":
        c = el.get("center")
        if not c:
            return None
        return float(c["lon"]), float(c["lat"])
    return None


def main() -> None:
    if not COUNTIES_GEOJSON.is_file():
        print(f"Missing {COUNTIES_GEOJSON}", file=sys.stderr)
        sys.exit(1)

    counties = gpd.read_file(COUNTIES_GEOJSON)
    union = counties.geometry.union_all()

    elements = overpass_places()
    rows: list[dict] = []
    for el in elements:
        tags = el.get("tags") or {}
        name = tags.get("name")
        if not name or not str(name).strip():
            continue
        place = tags.get("place", "")
        ll = element_lonlat(el)
        if ll is None:
            continue
        lon, lat = ll
        if not union.covers(Point(lon, lat)):
            continue
        rows.append(
            {
                "name": str(name).strip(),
                "lon": lon,
                "lat": lat,
                "place": place,
                "osm_type": el["type"],
                "osm_id": int(el["id"]),
            }
        )

    # Dedupe: same name + coords within ~25 m (4 decimal degrees ~ 11m lat)
    rows.sort(key=lambda r: (r["name"].lower(), r["lat"], r["lon"]))
    deduped: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for r in rows:
        key = (r["name"].lower(), f"{r['lon']:.4f}", f"{r['lat']:.4f}")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    deduped.sort(key=lambda r: (r["name"].lower(), r["lon"], r["lat"]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["name", "lon", "lat", "place", "osm_type", "osm_id", "source"],
        )
        w.writeheader()
        for r in deduped:
            w.writerow({**r, "source": "osm_overpass"})

    print(f"Wrote {len(deduped)} places to {OUT_CSV} (from {len(rows)} in-county before dedupe)")


if __name__ == "__main__":
    main()
