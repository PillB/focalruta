"""The containment audit must describe the routes that are actually published.

Requirements: K04, M01, O03. The audit was previously a hand-written artifact
keyed positionally to one snapshot, so a rebuild silently invalidated it.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / "data/architecture/routes.json"
AUDIT = ROOT / "architectural_photography/routes/geometry_containment_audit.json"


def _layer_keys(routes: dict) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    keys = []
    for layer in routes["district_layers"]:
        counts[layer["district"]] = counts.get(layer["district"], 0) + 1
        keys.append((layer["district"], counts[layer["district"]]))
    return keys


def test_audit_covers_exactly_the_published_layers():
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audited = [(row["district"], row["layer_index"]) for row in audit["layers"]]
    assert sorted(audited) == sorted(_layer_keys(routes)), (
        "the containment audit describes a different set of layers than the ones published"
    )


def test_audit_records_the_snapshot_it_verified():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    assert audit["audited_route_run"] == routes["generated_at"], (
        "the audit does not name the route snapshot it checked"
    )
    assert audit["method"].startswith("INDEPENDENT")


def test_every_published_leg_vertex_stays_inside_its_district():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    offenders = [(row["district"], row["layer_index"], row["outside_vertices"])
                 for row in audit["layers"] if row["outside_vertices"]]
    assert not offenders, f"published route geometry leaves its district: {offenders}"
    assert sum(row["checked_vertices"] for row in audit["layers"]) > 0


def test_no_published_layer_is_empty():
    """A layer with no stops is not a tour; it must never reach routes.json."""
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    empty = [(index, layer["district"]) for index, layer in enumerate(routes["district_layers"])
             if not layer.get("stops")]
    assert not empty, f"layers published with zero stops: {empty}"


def test_every_layer_has_one_fewer_leg_than_stops():
    """A walking tour of n stops has exactly n-1 legs; anything else is malformed."""
    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    broken = [
        (layer.get("layer_id"), layer["district"], len(layer["stops"]), len(layer["legs"]))
        for layer in routes["district_layers"]
        if len(layer["legs"]) != max(0, len(layer["stops"]) - 1)
    ]
    assert not broken, f"stop/leg counts disagree: {broken}"


def test_snapshot_repair_survives_an_audit_from_a_different_run():
    """A stale positional audit must not be able to crash the publication step."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    import repair_architecture_route_snapshot as repair

    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    stale_audit = {"audited_route_run": "1999-01-01T00:00:00+00:00", "layers": []}
    layers = repair.repaired_layers(json.loads(json.dumps(routes)), stale_audit)
    assert len(layers) >= len(routes["district_layers"])
    assert all(layer["route_geometry_containment_status"] == "VERIFIED" for layer in layers)


def test_boundary_repair_is_a_no_op_when_the_builder_already_isolated_the_target():
    """Repairing an already-isolated singleton must not leave an empty layer behind."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    import repair_architecture_route_snapshot as repair

    already_isolated = {
        "district": "Miraflores",
        "route_geometry_containment_status": "VERIFIED",
        "stops": [{"canonical_id": repair.TARGET_ID, "name": "Parque", "longitude": -77.0, "latitude": -12.1}],
        "legs": [],
        "optimization": {"permutations_evaluated": 1},
        "geojson_path": "challenges/arquitectura-en-foco/maps/x.geojson",
        "boundary_osm_id": 1,
    }
    layers = repair.repaired_layers({"district_layers": [already_isolated]}, {"layers": []})
    assert len(layers) == 1
    assert all(layer["stops"] for layer in layers)
