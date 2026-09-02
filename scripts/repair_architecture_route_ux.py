#!/usr/bin/env python3
"""Enrich route output without re-querying unstable routing services."""
from __future__ import annotations

import json
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "data/architecture/routes.json"
GEOCODES = ROOT / "architectural_photography/research/route_inputs/nominatim_candidates.json"
ANCHORS = ROOT / "architectural_photography/research/route_inputs/manual_anchors.json"
MAPS = ROOT / "challenges/arquitectura-en-foco/maps"
SENSITIVITY = ROOT / "architectural_photography/research/route_inputs/threshold_sensitivity.json"


def address_index() -> dict[str, str]:
    payload = json.loads(GEOCODES.read_text(encoding="utf-8"))
    result = {row["canonical_id"]: row["results"][0]["display_name"] for row in payload["records"] if row["results"]}
    result.update({row["canonical_id"]: row["address"] for row in json.loads(ANCHORS.read_text(encoding="utf-8"))["anchors"]})
    return result


def map_html(layer: dict, filename: str) -> None:
    points = layer["stops"]
    west, east = min(float(p["longitude"]) for p in points), max(float(p["longitude"]) for p in points)
    south, north = min(float(p["latitude"]) for p in points), max(float(p["latitude"]) for p in points)
    span_x, span_y = max(east - west, 0.001), max(north - south, 0.001)
    def xy(point: dict) -> tuple[float, float]:
        return (24 + 752 * (float(point["longitude"]) - west) / span_x, 360 - 320 * (float(point["latitude"]) - south) / span_y)
    lines = "".join('<polyline points="' + " ".join(f'{xy(p)[0]:.1f},{xy(p)[1]:.1f}' for p in [points[next(i for i, x in enumerate(points) if x["canonical_id"] == leg["from"])] , points[next(i for i, x in enumerate(points) if x["canonical_id"] == leg["to"])]]) + '"/>' for leg in layer["legs"])
    markers = "".join(f'<circle cx="{xy(point)[0]:.1f}" cy="{xy(point)[1]:.1f}" r="10"/><text x="{xy(point)[0]:.1f}" y="{xy(point)[1]:.1f}">{i}</text>' for i, point in enumerate(points, 1))
    rows = "".join(f'<li><strong>{i}. {escape(point["name"])}</strong><br>{escape(point["address"])}<br><code>{point["latitude"]}, {point["longitude"]}</code></li>' for i, point in enumerate(points, 1))
    content = f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mapa offline · {escape(layer["district"])}</title><style>body{{font:16px/1.5 system-ui;max-width:900px;margin:auto;padding:1rem;color:#10211d}}svg{{width:100%;background:#eef0e9;border:1px solid #cbc2b2}}polyline{{fill:none;stroke:#b84c32;stroke-width:7}}circle{{fill:#10211d;stroke:#fff;stroke-width:3}}text{{fill:#fff;font:bold 12px system-ui;text-anchor:middle;dominant-baseline:central}}li{{margin:.8rem 0}}</style><h1>{escape(layer["district"])} · mapa offline</h1><p>Geometría peatonal capturada; confirma cruces y cierres en campo. Google Maps puede recalcular otra ruta.</p><svg viewBox="0 0 800 400" role="img" aria-label="Ruta peatonal con paradas numeradas">{lines}{markers}</svg><ol>{rows}</ol>'
    (MAPS / filename).write_text(content, encoding="utf-8")


def main() -> None:
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    addresses = address_index()
    by_district: dict[str, list[dict]] = {}
    all_points: list[dict] = []
    for index, layer in enumerate(routes["district_layers"], 1):
        layer["layer_id"] = f'route-{index:02d}'
        for stop in layer["stops"]:
            stop["address"] = addresses.get(stop["canonical_id"], f'{stop["name"]}, {layer["district"]}, Lima')
            stop["address_source"] = "NOMINATIM_OR_MANUAL_ANCHOR"
            all_points.append({**stop, "district": layer["district"], "layer_id": layer["layer_id"], "is_singleton": len(layer["stops"]) == 1})
        filename = f'{Path(layer["kml_path"]).stem}.html'
        map_html(layer, filename)
        layer["offline_map_path"] = str((MAPS / filename).relative_to(ROOT))
        by_district.setdefault(layer["district"], []).append(layer)
    collections = []
    for district, layers in sorted(by_district.items()):
        collections.append({
            "collection_id": "collection-" + district.lower().replace(" ", "-"), "title": f"{district} · colección de ruta",
            "district": district, "layer_ids": [layer["layer_id"] for layer in layers],
            "segments": [layer["layer_id"] for layer in layers if len(layer["stops"]) >= 2],
            "independent_points": [layer["layer_id"] for layer in layers if len(layer["stops"]) == 1],
            "routing_note": "Camina cada segmento; los puntos independientes requieren traslado aparte.",
        })
    routes["route_collections"] = collections
    routes["threshold_sensitivity"] = threshold_sensitivity(all_points)
    routes["ux_version"] = "2.0.0"
    ROUTES.write_text(json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def haversine_m(first: dict, second: dict) -> float:
    radius = 6371000
    lat1, lat2 = math.radians(float(first["latitude"])), math.radians(float(second["latitude"]))
    dlat = lat2 - lat1
    dlon = math.radians(float(second["longitude"]) - float(first["longitude"]))
    return 2 * radius * math.asin(math.sqrt(math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2))


def threshold_sensitivity(points: list[dict]) -> dict:
    singles = [point for point in points if point["is_singleton"]]
    candidates = []
    for first_index, first in enumerate(singles):
        for second in singles[first_index + 1:]:
            if first["district"] == second["district"]:
                distance = round(haversine_m(first, second), 1)
                candidates.append({"from": first["canonical_id"], "to": second["canonical_id"], "district": first["district"], "straight_distance_m": distance, "road_distance_status": "NOT_CAPTURED_NO_MERGE"})
    return {
        "baseline_m": 1000, "tested_thresholds_m": [500, 1000, 1500],
        "method": "straight-line sensitivity screen only; road network evidence remains authoritative",
        "candidate_pairs_under_1500m": [item for item in candidates if item["straight_distance_m"] <= 1500],
        "candidate_pairs": candidates,
        "decision": "Do not merge on straight distance alone. A 1500 m screen identifies field/router checks; only captured road legs may join a walking segment.",
    }


if __name__ == "__main__":
    main()
