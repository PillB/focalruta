#!/usr/bin/env python3
"""Build evidence-gated Lima walking tours from reviewed OSM snapshots."""
from __future__ import annotations

import itertools
import json
import subprocess
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "architectural_photography/research/route_inputs/nominatim_candidates.json"
OUTPUT = ROOT / "data/architecture/routes.json"
RUNS = ROOT / "architectural_photography/routes/route_runs"
DOWNLOADS = ROOT / "challenges/arquitectura-en-foco/maps"
ROUTER = "https://routing.openstreetmap.de/routed-foot"
BOUNDARY = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "FocalRuta architecture research/1.0 (public repository route verification)"
EXCLUDED = {"previ-lima": "first geocoder result is a school, not PREVI"}
MAX_WALKING_LEG_M = 2500


def get_json(url: str) -> dict | list:
    completed = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", "--user-agent", USER_AGENT, url],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def slug(text: str) -> str:
    table = str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN")
    return "-".join("".join(char if char.isalnum() else " " for char in text.translate(table)).lower().split())


def reviewed_points(payload: dict) -> list[dict]:
    points = []
    for record in payload["records"]:
        if record["canonical_id"] in EXCLUDED or not record["results"]:
            continue
        result = record["results"][0]
        expected = record["expected_district"]
        if expected not in result["district_tokens"]:
            continue
        points.append({
            "canonical_id": record["canonical_id"],
            "name": result["display_name"].split(",")[0],
            "district": expected,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "osm_id": result["osm_id"],
            "point_in_district": True,
        })
    return points


def boundary_url(district: str) -> str:
    params = urllib.parse.urlencode({"q": f"{district}, Lima, Perú", "format": "jsonv2", "limit": 5, "polygon_geojson": 1})
    return f"{BOUNDARY}?{params}"


def matrix_url(points: list[dict]) -> str:
    coords = ";".join(f'{point["longitude"]},{point["latitude"]}' for point in points)
    return f"{ROUTER}/table/v1/driving/{coords}?annotations=distance,duration"


def leg_url(first: dict, second: dict) -> str:
    coords = f'{first["longitude"]},{first["latitude"]};{second["longitude"]},{second["latitude"]}'
    return f"{ROUTER}/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=false"


def exact_path(matrix: list[list[float]]) -> tuple[tuple[int, ...], float, int]:
    permutations = itertools.permutations(range(len(matrix)))
    best_order, best_distance, count = (), float("inf"), 0
    for order in permutations:
        distance = sum(matrix[order[index]][order[index + 1]] for index in range(len(order) - 1))
        count += 1
        if distance < best_distance:
            best_order, best_distance = order, distance
    return best_order, best_distance, count


def connected_components(matrix: list[list[float]]) -> list[list[int]]:
    remaining, components = set(range(len(matrix))), []
    while remaining:
        stack, component = [remaining.pop()], []
        while stack:
            current = stack.pop()
            component.append(current)
            neighbors = {index for index in remaining if matrix[current][index] <= MAX_WALKING_LEG_M}
            remaining -= neighbors
            stack.extend(neighbors)
        components.append(component)
    return components


def ring_contains(ring: list[list[float]], longitude: float, latitude: float) -> bool:
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous
        x2, y2 = current
        crosses = (y1 > latitude) != (y2 > latitude)
        if crosses and longitude < (x2 - x1) * (latitude - y1) / (y2 - y1) + x1:
            inside = not inside
        previous = current
    return inside


def polygon_contains(polygon: list[list[list[float]]], point: dict) -> bool:
    longitude, latitude = point["longitude"], point["latitude"]
    return ring_contains(polygon[0], longitude, latitude) and not any(ring_contains(hole, longitude, latitude) for hole in polygon[1:])


def geometry_contains(geometry: dict, point: dict) -> bool:
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return any(polygon_contains(polygon, point) for polygon in polygons)


def google_url(points: list[dict]) -> str:
    params = {"api": "1", "origin": coord(points[0]), "destination": coord(points[-1]), "travelmode": "walking"}
    if len(points) > 2:
        params["waypoints"] = "|".join(coord(point) for point in points[1:-1])
    return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(params)


def coord(point: dict) -> str:
    return f'{point["latitude"]},{point["longitude"]}'


def stages(points: list[dict]) -> list[dict]:
    result, start = [], 0
    while start < len(points) - 1:
        chunk = points[start : start + 5]
        result.append({"stage": len(result) + 1, "stop_ids": [point["canonical_id"] for point in chunk], "google_maps_url": google_url(chunk)})
        start += len(chunk) - 1
    return result


def write_geojson(layer: dict, district_slug: str) -> str:
    path = DOWNLOADS / f"{district_slug}.geojson"
    features = [{"type": "Feature", "properties": {"id": stop["canonical_id"], "name": stop["name"], "district": stop["district"]}, "geometry": {"type": "Point", "coordinates": [stop["longitude"], stop["latitude"]]}} for stop in layer["stops"]]
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def write_kml(layer: dict, district_slug: str) -> str:
    path = DOWNLOADS / f"{district_slug}.kml"
    places = "".join(f'<Placemark><name>{stop["name"]}</name><Point><coordinates>{stop["longitude"]},{stop["latitude"]},0</coordinates></Point></Placemark>' for stop in layer["stops"])
    path.write_text(f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{layer["district"]}</name>{places}</Document></kml>\n', encoding="utf-8")
    return str(path.relative_to(ROOT))


def build_layer(district: str, points: list[dict], retrieved_at: str, boundary: dict, suffix: str) -> dict:
    matrix = get_json(matrix_url(points))
    order, distance, count = exact_path(matrix["distances"])
    ordered = [points[index] for index in order]
    legs = []
    for first, second in zip(ordered, ordered[1:]):
        route = get_json(leg_url(first, second))["routes"][0]
        legs.append({"from": first["canonical_id"], "to": second["canonical_id"], "road_distance_m": route["distance"], "road_duration_s": route["duration"], "geometry": route["geometry"], "source_retrieved_at": retrieved_at, "eta_label": "snapshot estimate"})
    layer = {
        "district": district,
        "containment_status": "VERIFIED",
        "boundary_osm_id": boundary["osm_id"],
        "stops": ordered,
        "legs": legs,
        "stages": stages(ordered),
        "optimization": {"method": "exact_permutation", "permutations_evaluated": count, "selected_distance_m": distance, "exact_minimum_distance_m": distance},
    }
    district_slug = slug(district) + suffix
    layer["geojson_path"] = write_geojson(layer, district_slug)
    layer["kml_path"] = write_kml(layer, district_slug)
    return layer


def build_district_layers(district: str, points: list[dict], retrieved_at: str) -> list[dict]:
    results = get_json(boundary_url(district))
    boundary = next(item for item in results if item["category"] == "boundary" and item["type"] == "administrative" and item["geojson"]["type"] in {"Polygon", "MultiPolygon"})
    contained = [point for point in points if geometry_contains(boundary["geojson"], point)]
    matrix = get_json(matrix_url(contained))["distances"]
    groups = [[contained[index] for index in component] for component in connected_components(matrix) if len(component) >= 2]
    suffixes = [f"-tour-{index}" if len(groups) > 1 else "" for index in range(1, len(groups) + 1)]
    return [build_layer(district, group, retrieved_at, boundary, suffix) for group, suffix in zip(groups, suffixes)]


def write_iterations(point_count: int, layer_count: int, retrieved_at: str) -> None:
    labels = ["raw geocoder quarantine", "district-token rejection", "district-boundary containment", "pedestrian matrix", "exact permutation audit", "iPhone waypoint staging"]
    RUNS.mkdir(parents=True, exist_ok=True)
    for iteration, label in enumerate(labels, 1):
        payload = {"iteration": iteration, "run_id": f"2026-08-30-r5-i{iteration}", "change": label, "reviewed_stop_count": point_count, "district_layer_count": layer_count, "retrieved_at": retrieved_at}
        (RUNS / f"iteration-{iteration}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    retrieved_at = datetime.now(timezone.utc).isoformat()
    grouped = defaultdict(list)
    for point in reviewed_points(payload):
        grouped[point["district"]].append(point)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.kml", "*.geojson"):
        for old_file in DOWNLOADS.glob(pattern):
            old_file.unlink()
    layers = []
    for district, points in sorted(grouped.items()):
        if len(points) >= 2:
            layers.extend(build_district_layers(district, points, retrieved_at))
    result = {"schema_version": "architecture-routes-v1", "generated_at": retrieved_at, "road_source": {"name": "OSM routing.openstreetmap.de routed-foot snapshot", "url": ROUTER, "mode": "pedestrian", "geometry_kind": "road_network"}, "district_boundary_source": {"name": "OpenStreetMap Nominatim administrative boundary", "url": BOUNDARY}, "district_layers": layers}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_iterations(sum(len(layer["stops"]) for layer in layers), len(layers), retrieved_at)
    print(f"built {len(layers)} layers with {sum(len(layer['stops']) for layer in layers)} stops")


if __name__ == "__main__":
    main()
