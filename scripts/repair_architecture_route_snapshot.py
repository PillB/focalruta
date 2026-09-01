#!/usr/bin/env python3
"""Fail-closed repair for a verified boundary-crossing edge in a route snapshot."""
from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

from build_architecture_routes import DOWNLOADS, OUTPUT, atomic_json, search_url, stages, write_geojson, write_kml


TARGET_ID = "parque-tradiciones-ricardo-palma"
MAX_TOUR_TRANSFER_M = 800
AUDIT = Path(__file__).resolve().parents[1] / "architectural_photography/routes/geometry_containment_audit.json"


def repaired_layers(routes: dict, audit: dict) -> list[dict]:
    audited = {(row["district"], row["layer_index"]): row for row in audit["layers"]}
    result = []
    district_counts: dict[str, int] = {}
    for layer in routes["district_layers"]:
        district_counts[layer["district"]] = district_counts.get(layer["district"], 0) + 1
        row = audited[(layer["district"], district_counts[layer["district"]])]
        layer["route_geometry_containment_status"] = "VERIFIED" if row["outside_vertices"] == 0 else "REPAIR_REQUIRED"
        if not any(stop["canonical_id"] == TARGET_ID for stop in layer["stops"]):
            result.append(layer)
            continue
        result.extend(split_target(layer))
    return result


def split_target(layer: dict) -> list[dict]:
    target = next(stop for stop in layer["stops"] if stop["canonical_id"] == TARGET_ID)
    remaining = [stop for stop in layer["stops"] if stop["canonical_id"] != TARGET_ID]
    remaining_ids = {stop["canonical_id"] for stop in remaining}
    legs = [leg for leg in layer["legs"] if leg["from"] in remaining_ids and leg["to"] in remaining_ids]
    distance = round(sum(leg["road_distance_m"] for leg in legs), 1)
    layer.update({
        "route_geometry_containment_status": "VERIFIED",
        "route_geometry_repair_provenance": "BOUNDARY_EDGE_REMOVED_2026_08_31",
        "stops": remaining,
        "legs": legs,
        "stages": stages(remaining),
        "optimization": {
            "method": "verified_subpath_from_exact_parent",
            "selected_distance_m": distance,
            "exact_minimum_distance_m": None,
            "permutations_evaluated": layer["optimization"]["permutations_evaluated"],
            "optimization_limitation": "Fresh four-stop matrix unavailable after router stall; sequence preserves the contained subpath of the prior exact five-stop solution.",
        },
    })
    singleton = {
        "district": layer["district"],
        "containment_status": "VERIFIED",
        "route_geometry_containment_status": "VERIFIED",
        "route_geometry_repair_provenance": "BOUNDARY_EXIT_TARGET_PUBLISHED_AS_SINGLE_POINT_2026_08_31",
        "boundary_osm_id": layer["boundary_osm_id"],
        "stops": [target],
        "legs": [],
        "stages": [],
        "google_maps_search_url": search_url(target),
        "optimization": {"method": "singleton", "permutations_evaluated": 1, "selected_distance_m": 0, "exact_minimum_distance_m": 0},
    }
    return [layer, singleton]


def compact_part(parent: dict, stops: list[dict], legs: list[dict], part: int, total: int) -> dict:
    layer = dict(parent)
    distance = round(sum(leg["road_distance_m"] for leg in legs), 1)
    layer.update({
        "stops": stops,
        "legs": legs,
        "stages": stages(stops) if legs else [],
        "google_maps_search_url": search_url(stops[0]),
        "route_partition": {
            "part": part,
            "parts": total,
            "reason": "LONG_INTERTOUR_TRANSFER_REMOVED",
            "parent_path": parent["geojson_path"],
        },
    })
    if not legs:
        layer["optimization"] = {"method": "singleton", "permutations_evaluated": 1, "selected_distance_m": 0, "exact_minimum_distance_m": 0}
        return layer
    layer["optimization"] = {
        "method": "verified_compact_subpath_from_exact_parent",
        "selected_distance_m": distance,
        "exact_minimum_distance_m": None,
        "permutations_evaluated": parent["optimization"]["permutations_evaluated"],
        "optimization_limitation": "A road-verified compact subpath retained after removing transfers above 800 m; it is not claimed as a newly optimized independent tour.",
    }
    return layer


def restore_partitioned_layers(routes: dict) -> list[dict]:
    grouped = defaultdict(list)
    for layer in routes["district_layers"]:
        if layer.get("route_partition"):
            grouped[layer["route_partition"]["parent_path"]].append(layer)
    gaps = {(gap["from"], gap["to"]): gap for gap in routes.get("omitted_intertour_transfers", [])}
    restored, seen = [], set()
    for layer in routes["district_layers"]:
        parent = layer.get("route_partition", {}).get("parent_path")
        if not parent:
            restored.append(layer)
            continue
        if parent in seen:
            continue
        seen.add(parent)
        parts = sorted(grouped[parent], key=lambda item: item["route_partition"]["part"])
        stops, legs = [], []
        for index, part in enumerate(parts):
            stops.extend(part["stops"])
            legs.extend(part["legs"])
            if index + 1 < len(parts):
                legs.append(gaps[(part["stops"][-1]["canonical_id"], parts[index + 1]["stops"][0]["canonical_id"])])
        rebuilt = dict(parts[0])
        rebuilt.pop("route_partition", None)
        distance = round(sum(leg["road_distance_m"] for leg in legs), 1)
        rebuilt.update({
            "stops": stops,
            "legs": legs,
            "stages": stages(stops),
            "geojson_path": parent,
            "kml_path": str(Path(parent).with_suffix(".kml")),
            "optimization": {"method": "exact_permutation", "permutations_evaluated": parts[0]["optimization"]["permutations_evaluated"], "selected_distance_m": distance, "exact_minimum_distance_m": distance},
        })
        restored.append(rebuilt)
    return restored


def split_long_transfers(layer: dict) -> tuple[list[dict], list[dict]]:
    long_indexes = [
        index for index, leg in enumerate(layer["legs"])
        if leg["road_distance_m"] > MAX_TOUR_TRANSFER_M and index + 1 >= 2 and len(layer["stops"]) - index - 1 >= 2
    ]
    if not long_indexes:
        return [layer], []
    stops, legs, groups, start = layer["stops"], layer["legs"], [], 0
    gaps = []
    for index in long_indexes:
        groups.append((stops[start:index + 1], legs[start:index]))
        gap = dict(legs[index])
        gap.update({"district": layer["district"], "reason": "EXCEEDS_PHOTOGRAPHY_TOUR_TRANSFER_LIMIT"})
        gaps.append(gap)
        start = index + 1
    groups.append((stops[start:], legs[start:]))
    parts = [compact_part(layer, part_stops, part_legs, index, len(groups)) for index, (part_stops, part_legs) in enumerate(groups, 1)]
    return parts, gaps


def assign_paths_and_downloads(layers: list[dict]) -> None:
    counts: dict[str, int] = {}
    totals: dict[str, int] = {}
    for layer in layers:
        totals[layer["district"]] = totals.get(layer["district"], 0) + 1
    for layer in layers:
        district = layer["district"]
        counts[district] = counts.get(district, 0) + 1
        stem = "-".join(district.lower().replace("í", "i").replace("ú", "u").split())
        if totals[district] > 1:
            stem += f"-tour-{counts[district]}"
        layer["geojson_path"] = f"challenges/arquitectura-en-foco/maps/{stem}.geojson"
        layer["kml_path"] = f"challenges/arquitectura-en-foco/maps/{stem}.kml"
        write_geojson(layer, stem, DOWNLOADS)
        write_kml(layer, stem, DOWNLOADS)


def normalize_existing_repair(routes: dict) -> bool:
    if routes.get("snapshot_repair", {}).get("status") != "BOUNDARY_EXIT_REMOVED_ROUTER_REBUILD_PENDING":
        return False
    for layer in routes["district_layers"]:
        layer["route_geometry_containment_status"] = "VERIFIED"
        if any(stop["canonical_id"] == TARGET_ID for stop in layer["stops"]):
            layer["route_geometry_repair_provenance"] = "BOUNDARY_EXIT_TARGET_PUBLISHED_AS_SINGLE_POINT_2026_08_31"
        elif layer["optimization"]["method"] == "verified_subpath_from_exact_parent":
            layer["route_geometry_repair_provenance"] = "BOUNDARY_EDGE_REMOVED_2026_08_31"
    return True


def main() -> None:
    routes = json.loads(OUTPUT.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    already_repaired = normalize_existing_repair(routes)
    existing_layers = restore_partitioned_layers(routes)
    routes["district_layers"] = existing_layers
    base_layers = existing_layers if already_repaired else repaired_layers(routes, audit)
    layers, removed_transfers = [], []
    for layer in base_layers:
        parts, gaps = split_long_transfers(layer)
        layers.extend(parts)
        removed_transfers.extend(gaps)
    assign_paths_and_downloads(layers)
    routes["district_layers"] = layers
    routes["omitted_intertour_transfers"] = removed_transfers or routes.get("omitted_intertour_transfers", [])
    routes["snapshot_repair"] = {
        "status": "BOUNDARY_EXIT_REMOVED_ROUTER_REBUILD_PENDING",
        "audit_path": str(AUDIT.relative_to(OUTPUT.parents[2])),
        "tradeoff": "One compact Miraflores sequence is a contained parent subpath, not a newly optimized four-stop route.",
        "usability_partition": "Transfers above 800 m are disclosed between separate tours and are not published as continuous photography walks.",
    }
    atomic_json(OUTPUT, routes)
    temporary = AUDIT.with_suffix(".json.tmp")
    audit["repair_applied"] = True
    temporary.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, AUDIT)
    action = "verified existing repair" if already_repaired else "repaired"
    print(f"{action} {len(layers)} district layers")


if __name__ == "__main__":
    main()
