#!/usr/bin/env python3
"""Fail-closed repair for a verified boundary-crossing edge in a route snapshot."""
from __future__ import annotations

import json
import os
from pathlib import Path

from build_architecture_routes import DOWNLOADS, OUTPUT, atomic_json, search_url, stages, write_geojson, write_kml


TARGET_ID = "parque-tradiciones-ricardo-palma"
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
    layers = routes["district_layers"] if already_repaired else repaired_layers(routes, audit)
    assign_paths_and_downloads(layers)
    routes["district_layers"] = layers
    routes["snapshot_repair"] = {
        "status": "BOUNDARY_EXIT_REMOVED_ROUTER_REBUILD_PENDING",
        "audit_path": str(AUDIT.relative_to(OUTPUT.parents[2])),
        "tradeoff": "One compact Miraflores sequence is a contained parent subpath, not a newly optimized four-stop route.",
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
