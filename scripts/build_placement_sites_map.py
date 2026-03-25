#!/usr/bin/env python3
"""Folium map: hypothetical new-pharmacy sites only (OSM villages/hamlets from placement run).

Reads data/placement_hypothetical_sites.csv produced by notebooks/04-weighted.ipynb
after the OSRM placement loop completes. Each point is colored by
person_minutes_saved_one_way (gradient scale).

Writes data/placement_hypothetical_sites_map.html
"""

from __future__ import annotations

import sys
from pathlib import Path

import branca.colormap as cm
import folium
import numpy as np
import pandas as pd


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data = root / "data"
    csv_path = data / "placement_hypothetical_sites.csv"
    out_html = data / "placement_hypothetical_sites_map.html"

    if not csv_path.is_file():
        print(
            "Missing placement CSV. Run the OSRM placement section in "
            "notebooks/04-weighted.ipynb (with OSRM up) so it writes "
            f"{csv_path.name}",
            file=sys.stderr,
        )
        sys.exit(1)

    df = pd.read_csv(csv_path)
    required = {"lon", "lat", "person_minutes_saved_one_way", "village"}
    missing = required - set(df.columns)
    if missing:
        print(f"CSV missing columns: {sorted(missing)}", file=sys.stderr)
        sys.exit(1)
    if df.empty:
        print("placement CSV has no rows", file=sys.stderr)
        sys.exit(1)

    saved = df["person_minutes_saved_one_way"].to_numpy(dtype=float)
    p95 = float(max(1e-6, np.percentile(saved, 95)))

    colors = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"]
    colormap = cm.LinearColormap(
        colors=colors,
        vmin=0.0,
        vmax=p95,
        caption=(
            "Person·minutes saved (one-way) if a pharmacy opened at this OSM point "
            f"(color scale 0–95th pct ≈ {p95:,.0f}; tooltip shows exact value)"
        ),
    )

    center_lat = float(df["lat"].mean())
    center_lon = float(df["lon"].mean())
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="cartodbpositron")

    for _, row in df.iterrows():
        v = float(row["person_minutes_saved_one_way"])
        folium.CircleMarker(
            location=[float(row["lat"]), float(row["lon"])],
            radius=8,
            stroke=True,
            color="#222222",
            weight=1,
            fill=True,
            fill_color=colormap(min(v, p95)),
            fill_opacity=0.85,
            tooltip=(
                f"<b>{row['village']}</b> ({row.get('place', '')})<br>"
                f"{v:,.0f} person·min saved (one-way)"
            ),
        ).add_to(m)

    colormap.add_to(m)
    m.save(str(out_html))
    print(f"Wrote {out_html} ({len(df)} placement points)")


if __name__ == "__main__":
    main()
