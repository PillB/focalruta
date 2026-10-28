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


# Reviewed geocoder hits whose first token is a tenant at the address, not the place (Y20):
# the address keeps its number and street and drops the company's name.
TENANT_PREFIXES = {"centro-financiero-canaval-y-moreyra-rivera-navarrete": "Viettel Perú, "}


def address_index() -> dict[str, str]:
    payload = json.loads(GEOCODES.read_text(encoding="utf-8"))
    result = {row["canonical_id"]: row["results"][0]["display_name"] for row in payload["records"] if row["results"]}
    for canonical_id, prefix in TENANT_PREFIXES.items():
        result[canonical_id] = result[canonical_id].removeprefix(prefix)
    result.update({row["canonical_id"]: row["address"] for row in json.loads(ANCHORS.read_text(encoding="utf-8"))["anchors"]})
    return result


def map_projection(layer: dict):
    """Equal-scale projection of the walked legs and the stops into the 800 x 400 frame.

    A degree of longitude at Lima's latitude is about 2 % shorter than a degree of latitude,
    so both axes share one scale and the drawing keeps its shape; a lone stop sits centred.
    """
    points = [(float(x), float(y)) for leg in layer["legs"] for x, y in leg["geometry"]["coordinates"]]
    points += [(float(stop["longitude"]), float(stop["latitude"])) for stop in layer["stops"]]
    west, east = min(x for x, _ in points), max(x for x, _ in points)
    south, north = min(y for _, y in points), max(y for _, y in points)
    shrink = math.cos(math.radians((south + north) / 2))
    scale = max((east - west) * shrink / 752, (north - south) / 352, 1e-12)
    middle_x, middle_y = (west + east) / 2, (south + north) / 2
    return lambda x, y: (400 + (float(x) - middle_x) * shrink / scale, 200 - (float(y) - middle_y) / scale)


def map_html(layer: dict, filename: str) -> None:
    points, xy = layer["stops"], map_projection(layer)
    lines = "".join('<polyline points="' + " ".join("{:.1f},{:.1f}".format(*xy(x, y)) for x, y in leg["geometry"]["coordinates"]) + '"/>' for leg in layer["legs"])
    markers = "".join('<circle cx="{0:.1f}" cy="{1:.1f}" r="10"/><text x="{0:.1f}" y="{1:.1f}">{2}</text>'.format(*xy(point["longitude"], point["latitude"]), i) for i, point in enumerate(points, 1))
    rows = "".join(f'<li><strong>{i}. {escape(point["name"])}</strong><br>{escape(point["address"])}<br><code>{point["latitude"]}, {point["longitude"]}</code></li>' for i, point in enumerate(points, 1))
    if layer["legs"]:
        intro = "Geometría peatonal capturada; confirma cruces y cierres en campo. Google Maps puede recalcular otra ruta."
        caption = "Visualización: la línea muestra el trazado peatonal capturado y los números el orden de las paradas; no es navegación en vivo ni una ruta recalculada hoy."
        label = "Ruta peatonal con paradas numeradas"
    else:
        intro = f'Punto independiente: no forma parte de una caminata, así que no hay tramo que dibujar. <a href="{escape(layer["google_maps_search_url"])}">Ábrelo en Google Maps</a> para llegar.'
        caption = "Visualización: el punto marca el lugar; no es una ruta ni navegación en vivo."
        label = "Ubicación del punto independiente"
    content = f'<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mapa offline · {escape(layer["district"])}</title><style>body{{font:16px/1.5 system-ui;max-width:900px;margin:auto;padding:1rem;color:#10211d}}svg{{width:100%;background:#eef0e9;border:1px solid #cbc2b2}}polyline{{fill:none;stroke:#b84c32;stroke-width:7;stroke-linejoin:round;stroke-linecap:round}}circle{{fill:#10211d;stroke:#fff;stroke-width:3}}text{{fill:#fff;font:bold 12px system-ui;text-anchor:middle;dominant-baseline:central}}li{{margin:.8rem 0}}</style><main><h1>{escape(layer["district"])} · mapa offline</h1><p>{intro}</p><svg viewBox="0 0 800 400" role="img" aria-label="{label}">{lines}{markers}</svg><p class="viz-caption">{caption}</p><ol>{rows}</ol></main></html>'
    (MAPS / filename).write_text(content, encoding="utf-8")


def render_offline_maps() -> list[str]:
    """Redraw every offline map page from the committed routes without touching routes.json.

    `main()` rebuilds the route data itself and only runs after a live routing
    session; the pages it writes are pure functions of routes.json, so they can
    be regenerated (and checked for drift) on every build.
    """
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    names = []
    for layer in routes["district_layers"]:
        name = Path(layer["offline_map_path"]).name
        map_html(layer, name)
        names.append(name)
    return names


MERGE_PAIRS = (
    ("conjunto-habitacional-palomino", "unidad-vecinal-3"),
    ("jiron-trujillo-puente-de-piedra", "cantagallo-comunidad-shipibo-konibo"),
)


def merge_threshold_pairs(routes: dict) -> None:
    """Join the two user-approved 1500 m pairs with a disclosed straight leg."""
    layers = routes["district_layers"]
    for first_id, second_id in MERGE_PAIRS:
        singles = {layer["stops"][0]["canonical_id"]: layer for layer in layers if len(layer["stops"]) == 1}
        first, second = singles.get(first_id), singles.get(second_id)
        if not first or not second:
            continue
        a, b = first["stops"][0], second["stops"][0]
        distance = round(haversine_m(a, b), 1)
        leg = {
            "from": a["canonical_id"], "to": b["canonical_id"],
            "road_distance_m": distance, "road_duration_s": round(distance / 1.35),
            "source_retrieved_at": "2026-09-01T00:00:00Z", "eta_label": "estimación recta · validar en campo",
            "geometry": {"type": "LineString", "coordinates": [[a["longitude"], a["latitude"]], [b["longitude"], b["latitude"]]]},
            "evidence_status": "STRAIGHT_LINE_THRESHOLD_SCREEN_NOT_ROAD_ROUTING",
        }
        merged = {**first, "stops": [a, b], "legs": [leg], "optimization": {"method": "threshold_sensitivity_merge", "selected_distance_m": distance, "exact_minimum_distance_m": None, "permutations_evaluated": 2, "optimization_limitation": "straight-line screen; confirm pedestrian streets before departure"}}
        layers.remove(first); layers.remove(second); layers.append(merged)


def retire_unreferenced_maps(routes: dict) -> list[str]:
    """Delete published map files that no surviving layer points at.

    Merging or splitting layers changes which files are reachable; leaving the
    old ones on disk publishes tours that no longer exist.
    """
    referenced = set()
    for layer in routes["district_layers"]:
        for key in ("geojson_path", "kml_path", "offline_map_path"):
            if layer.get(key):
                referenced.add(Path(layer[key]).name)
    retired = []
    for path in sorted(MAPS.iterdir()):
        if path.is_file() and path.name not in referenced:
            path.unlink()
            retired.append(path.name)
    return retired


def main() -> None:
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    merge_threshold_pairs(routes)
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
    routes["retired_map_files"] = retire_unreferenced_maps(routes)
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
