#!/usr/bin/env python3
"""Independently re-verify that every published route leg stays in its district.

The route builder already refuses to publish a leg that leaves its boundary.
This audit does not trust that: it re-fetches each administrative polygon and
re-tests every vertex, so the containment claim has evidence separate from the
code that made it.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from build_architecture_routes import OUTPUT, atomic_json, boundary_url, geometry_contains, get_json

AUDIT = Path(__file__).resolve().parents[1] / "architectural_photography/routes/geometry_containment_audit.json"


def boundary_for(district: str) -> dict:
    """Pick the administrative polygon the builder would have used."""
    results = get_json(boundary_url(district))
    for result in results:
        if result.get("geojson", {}).get("type") in {"Polygon", "MultiPolygon"}:
            return result
    raise ValueError(f"no polygon boundary for {district}")


def audit_layer(layer: dict, boundary: dict, index: int) -> dict:
    checked = 0
    outside = 0
    for leg in layer["legs"]:
        for longitude, latitude in leg["geometry"]["coordinates"]:
            checked += 1
            if not geometry_contains(boundary["geojson"], {"longitude": longitude, "latitude": latitude}):
                outside += 1
    return {
        "district": layer["district"],
        "layer_index": index,
        "stops": len(layer["stops"]),
        "checked_vertices": checked,
        "outside_vertices": outside,
        "boundary_osm_id": boundary.get("osm_id"),
    }


def audit_layers(routes: dict) -> list[dict]:
    boundaries: dict[str, dict] = {}
    counts: dict[str, int] = {}
    rows = []
    for layer in routes["district_layers"]:
        district = layer["district"]
        counts[district] = counts.get(district, 0) + 1
        if district not in boundaries:
            boundaries[district] = boundary_for(district)
        rows.append(audit_layer(layer, boundaries[district], counts[district]))
    return rows


def main() -> None:
    routes = json.loads(OUTPUT.read_text(encoding="utf-8"))
    rows = audit_layers(routes)
    atomic_json(AUDIT, {
        "schema_version": "route-geometry-containment-v2",
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "audited_route_run": routes["generated_at"],
        "method": "INDEPENDENT_REFETCH_OF_ADMINISTRATIVE_POLYGONS_AND_PER_VERTEX_POINT_IN_POLYGON",
        "boundary_source": routes["district_boundary_source"],
        "road_source": routes["road_source"],
        "layers": rows,
    })
    outside = sum(row["outside_vertices"] for row in rows)
    checked = sum(row["checked_vertices"] for row in rows)
    print(f"audited {len(rows)} layers, {checked} vertices, {outside} outside their district")


if __name__ == "__main__":
    main()
