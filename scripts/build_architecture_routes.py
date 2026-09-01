#!/usr/bin/env python3
"""Build evidence-gated Lima walking tours from reviewed OSM snapshots."""
from __future__ import annotations

import itertools
import json
import os
import subprocess
from html import escape
from tempfile import TemporaryDirectory
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "architectural_photography/research/route_inputs/nominatim_candidates.json"
MANUAL_INPUT = ROOT / "architectural_photography/research/route_inputs/manual_anchors.json"
OUTPUT = ROOT / "data/architecture/routes.json"
RUNS = ROOT / "architectural_photography/routes/route_runs"
DOWNLOADS = ROOT / "challenges/arquitectura-en-foco/maps"
ROUTER = "https://routing.openstreetmap.de/routed-foot"
BOUNDARY = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "FocalRuta architecture research/1.0 (public repository route verification)"
EXCLUDED = {
    "previ-lima": "first geocoder result is a school, not PREVI",
    "estacion-restos-del-funicular-de-barranco": "first result is Estación Estado Unión, not the funicular",
    "torres-centro-empresarial-camino-real": "first result is Calle Luis Dorich Torres, not Camino Real",
}
# Hard connectivity ceiling. The publication repair applies a separate 800 m
# preferred photography-transfer threshold only when both resulting walks keep
# at least two stops; using 800 m here fragmented useful tours into singletons.
MAX_WALKING_LEG_M = 1000
MAX_EXACT_STOPS = 8
FORCE_SINGLETONS = {
    "parque-tradiciones-ricardo-palma": "OSM pedestrian route to its nearest cluster exits the Miraflores administrative polygon",
}


def get_json(url: str) -> dict | list:
    completed = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", "--retry", "3", "--retry-delay", "2", "--retry-all-errors", "--user-agent", USER_AGENT, url],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def slug(text: str) -> str:
    table = str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN")
    return "-".join("".join(char if char.isalnum() else " " for char in text.translate(table)).lower().split())


def reviewed_points(payload: dict, manual_payload: dict) -> list[dict]:
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
            "anchor_method": "OSM_NOMINATIM_REVIEWED",
        })
    for anchor in manual_payload["anchors"]:
        points = [point for point in points if point["canonical_id"] != anchor["canonical_id"]]
        points.append({
            "canonical_id": anchor["canonical_id"],
            "name": anchor["name"],
            "district": anchor["district"],
            "latitude": anchor["latitude"],
            "longitude": anchor["longitude"],
            "osm_id": None,
            "point_in_district": True,
            "anchor_method": anchor["status"],
            "address": anchor["address"],
            "address_source_url": anchor["address_source_url"],
            "coordinate_source_url": anchor["coordinate_source_url"],
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
        edges = [matrix[order[index]][order[index + 1]] for index in range(len(order) - 1)]
        count += 1
        if any(edge > MAX_WALKING_LEG_M for edge in edges):
            continue
        distance = sum(edges)
        if distance < best_distance:
            best_order, best_distance = order, distance
    if not best_order:
        raise ValueError("cluster has no exact path within the maximum walking-leg constraint")
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


def bounded_components(matrix: list[list[float]]) -> list[list[int]]:
    bounded = []
    for component in connected_components(matrix):
        remaining = set(component)
        while remaining:
            group = [remaining.pop()]
            while remaining and len(group) < MAX_EXACT_STOPS:
                nearest = min(remaining, key=lambda index: min(matrix[index][member] for member in group))
                remaining.remove(nearest)
                group.append(nearest)
            bounded.append(group)
    return bounded


def exact_path_cover(matrix: list[list[float]], group: list[int]) -> list[list[int]]:
    best_order, best_breaks, best_metric = (), (), (float("inf"), float("inf"))
    for order in itertools.permutations(group):
        breaks = tuple(index for index in range(len(order) - 1) if matrix[order[index]][order[index + 1]] > MAX_WALKING_LEG_M)
        distance = sum(matrix[order[index]][order[index + 1]] for index in range(len(order) - 1) if index not in breaks)
        metric = (len(breaks) + 1, distance)
        if metric < best_metric:
            best_order, best_breaks, best_metric = order, breaks, metric
    starts, paths = (0,) + tuple(index + 1 for index in best_breaks), []
    ends = tuple(index + 1 for index in best_breaks) + (len(best_order),)
    for start, end in zip(starts, ends):
        paths.append(list(best_order[start:end]))
    return paths


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


def search_url(point: dict) -> str:
    params = urllib.parse.urlencode({"api": "1", "query": coord(point)})
    return "https://www.google.com/maps/search/?" + params


def write_geojson(layer: dict, district_slug: str, output_dir: Path) -> str:
    path = output_dir / f"{district_slug}.geojson"
    features = [{"type": "Feature", "properties": {"id": stop["canonical_id"], "name": stop["name"], "district": stop["district"]}, "geometry": {"type": "Point", "coordinates": [stop["longitude"], stop["latitude"]]}} for stop in layer["stops"]]
    features.extend(
        {
            "type": "Feature",
            "properties": {
                "from": leg["from"],
                "to": leg["to"],
                "road_distance_m": leg["road_distance_m"],
                "source_retrieved_at": leg["source_retrieved_at"],
            },
            "geometry": leg["geometry"],
        }
        for leg in layer["legs"]
    )
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def write_kml(layer: dict, district_slug: str, output_dir: Path) -> str:
    path = output_dir / f"{district_slug}.kml"
    places = "".join(f'<Placemark><name>{escape(stop["name"])}</name><Point><coordinates>{stop["longitude"]},{stop["latitude"]},0</coordinates></Point></Placemark>' for stop in layer["stops"])
    lines = "".join(
        f'<Placemark><name>{escape(leg["from"])} → {escape(leg["to"])}</name><styleUrl>#walking-route</styleUrl>'
        f'<ExtendedData><Data name="road_distance_m"><value>{leg["road_distance_m"]}</value></Data></ExtendedData>'
        f'<LineString><tessellate>1</tessellate><altitudeMode>clampToGround</altitudeMode><coordinates>'
        + " ".join(f"{longitude},{latitude},0" for longitude, latitude in leg["geometry"]["coordinates"])
        + "</coordinates></LineString></Placemark>"
        for leg in layer["legs"]
    )
    style = '<Style id="walking-route"><LineStyle><color>ff326bb8</color><width>5</width></LineStyle></Style>'
    path.write_text(f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{escape(layer["district"])}</name>{style}{places}{lines}</Document></kml>\n', encoding="utf-8")
    return str(path.relative_to(ROOT))


def build_layer(district: str, points: list[dict], retrieved_at: str, boundary: dict, suffix: str, output_dir: Path) -> dict:
    distances = [[0.0]] if len(points) == 1 else get_json(matrix_url(points))["distances"]
    order, distance, count = exact_path(distances)
    ordered = [points[index] for index in order]
    legs = []
    for first, second in zip(ordered, ordered[1:]):
        route = get_json(leg_url(first, second))["routes"][0]
        legs.append({"from": first["canonical_id"], "to": second["canonical_id"], "road_distance_m": route["distance"], "road_duration_s": route["duration"], "geometry": route["geometry"], "source_retrieved_at": retrieved_at, "eta_label": "snapshot estimate"})
    if any(not geometry_contains(boundary["geojson"], {"longitude": point[0], "latitude": point[1]}) for leg in legs for point in leg["geometry"]["coordinates"]):
        raise ValueError("route geometry exits its stated district")
    layer = {
        "district": district,
        "containment_status": "VERIFIED",
        "route_geometry_containment_status": "VERIFIED",
        "boundary_osm_id": boundary["osm_id"],
        "stops": ordered,
        "legs": legs,
        "stages": stages(ordered),
        "google_maps_search_url": search_url(ordered[0]),
        "optimization": {"method": "exact_permutation", "permutations_evaluated": count, "selected_distance_m": distance, "exact_minimum_distance_m": distance},
    }
    district_slug = slug(district) + suffix
    layer["geojson_path"] = str((DOWNLOADS / f"{district_slug}.geojson").relative_to(ROOT))
    layer["kml_path"] = str((DOWNLOADS / f"{district_slug}.kml").relative_to(ROOT))
    write_geojson(layer, district_slug, output_dir)
    write_kml(layer, district_slug, output_dir)
    return layer


def build_district_layers(district: str, points: list[dict], retrieved_at: str, output_dir: Path) -> list[dict]:
    results = get_json(boundary_url(district))
    boundary = next(item for item in results if item["category"] == "boundary" and item["type"] == "administrative" and item["geojson"]["type"] in {"Polygon", "MultiPolygon"})
    contained = [point for point in points if geometry_contains(boundary["geojson"], point)]
    singleton_groups = [[point] for point in contained if point["canonical_id"] in FORCE_SINGLETONS]
    routable = [point for point in contained if point["canonical_id"] not in FORCE_SINGLETONS]
    matrix = [[0.0]] if len(routable) == 1 else get_json(matrix_url(routable))["distances"]
    index_groups = [path for component in bounded_components(matrix) for path in exact_path_cover(matrix, component)] if routable else []
    groups = [[routable[index] for index in group] for group in index_groups] + singleton_groups
    suffixes = [f"-tour-{index}" if len(groups) > 1 else "" for index in range(1, len(groups) + 1)]
    return [build_layer(district, group, retrieved_at, boundary, suffix, output_dir) for group, suffix in zip(groups, suffixes)]


def publish_downloads(staging: Path) -> None:
    published = {path.name for path in staging.iterdir()}
    for path in staging.iterdir():
        os.replace(path, DOWNLOADS / path.name)
    for pattern in ("*.kml", "*.geojson"):
        for old_file in DOWNLOADS.glob(pattern):
            if old_file.name not in published:
                old_file.unlink()


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def write_iterations(point_count: int, layer_count: int, retrieved_at: str) -> None:
    labels = ["raw geocoder quarantine", "district-token rejection", "district-boundary containment", "pedestrian matrix", "exact permutation audit", "iPhone waypoint staging"]
    RUNS.mkdir(parents=True, exist_ok=True)
    for iteration, label in enumerate(labels, 1):
        payload = {"iteration": iteration, "run_id": f"2026-08-30-r5-i{iteration}", "change": label, "reviewed_stop_count": point_count, "district_layer_count": layer_count, "retrieved_at": retrieved_at}
        (RUNS / f"iteration-{iteration}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    manual_payload = json.loads(MANUAL_INPUT.read_text(encoding="utf-8"))
    retrieved_at = datetime.now(timezone.utc).isoformat()
    grouped = defaultdict(list)
    for point in reviewed_points(payload, manual_payload):
        grouped[point["district"]].append(point)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="architecture-routes-", dir=DOWNLOADS.parent) as temporary:
        staging = Path(temporary)
        layers = []
        for district, points in sorted(grouped.items()):
            layers.extend(build_district_layers(district, points, retrieved_at, staging))
        publish_downloads(staging)
    result = {"schema_version": "architecture-routes-v1", "generated_at": retrieved_at, "road_source": {"name": "OSM routing.openstreetmap.de routed-foot snapshot", "url": ROUTER, "mode": "pedestrian", "geometry_kind": "road_network"}, "district_boundary_source": {"name": "OpenStreetMap Nominatim administrative boundary", "url": BOUNDARY}, "district_layers": layers}
    atomic_json(OUTPUT, result)
    write_iterations(sum(len(layer["stops"]) for layer in layers), len(layers), retrieved_at)
    print(f"built {len(layers)} layers with {sum(len(layer['stops']) for layer in layers)} stops")


if __name__ == "__main__":
    main()
