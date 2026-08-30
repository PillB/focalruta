import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / "data/architecture/routes.json"
RUNS = ROOT / "architectural_photography/routes/route_runs"


def load_routes():
    return json.loads(ROUTES.read_text(encoding="utf-8"))


def test_route_dataset_has_evidence_contract_and_six_iterations():
    routes = load_routes()
    assert routes["schema_version"] == "architecture-routes-v1"
    assert routes["road_source"]["mode"] == "pedestrian"
    assert routes["road_source"]["geometry_kind"] != "geodesic"
    assert routes["district_boundary_source"]["url"]
    assert routes["generated_at"]
    runs = sorted(RUNS.glob("iteration-*.json"))
    assert len(runs) == 6
    assert [json.loads(path.read_text())["iteration"] for path in runs] == list(range(1, 7))


def test_every_layer_is_district_pure_and_every_stop_is_contained():
    routes = load_routes()
    for layer in routes["district_layers"]:
        assert layer["district"]
        assert layer["containment_status"] == "VERIFIED"
        assert layer["stops"]
        for stop in layer["stops"]:
            assert stop["district"] == layer["district"]
            assert stop["point_in_district"] is True
            assert -12.6 < stop["latitude"] < -11.5
            assert -77.3 < stop["longitude"] < -76.5


def test_iphone_links_use_google_walking_contract_without_truncation():
    routes = load_routes()
    for layer in routes["district_layers"]:
        for stage in layer["stages"]:
            parsed = urlparse(stage["google_maps_url"])
            query = parse_qs(parsed.query)
            assert parsed.netloc == "www.google.com"
            assert parsed.path == "/maps/dir/"
            assert query["api"] == ["1"]
            assert query["travelmode"] == ["walking"]
            assert len(stage["stop_ids"]) <= 5
            assert len(query.get("waypoints", [""])[0].split("|")) <= 3
            assert len(stage["google_maps_url"]) <= 2048


def test_each_road_leg_has_source_geometry_and_no_fake_live_eta():
    routes = load_routes()
    for layer in routes["district_layers"]:
        for leg in layer["legs"]:
            assert leg["road_distance_m"] > 0
            assert leg["road_duration_s"] > 0
            assert len(leg["geometry"]["coordinates"]) >= 2
            assert leg["source_retrieved_at"]
            assert leg["eta_label"] == "snapshot estimate"
            assert leg["road_distance_m"] <= 2500


def test_small_tours_are_checked_by_exact_permutation():
    routes = load_routes()
    for layer in routes["district_layers"]:
        if len(layer["stops"]) <= 9:
            optimization = layer["optimization"]
            assert optimization["method"] == "exact_permutation"
            assert optimization["permutations_evaluated"] >= 1
            assert optimization["selected_distance_m"] == optimization["exact_minimum_distance_m"]


def test_downloads_and_eli5_iphone_help_exist():
    routes = load_routes()
    help_text = (ROOT / "challenges/arquitectura-en-foco/iphone-maps.html").read_text(encoding="utf-8")
    assert "iPhone 13 Pro" in help_text
    assert "You" in help_text and "Maps" in help_text
    for layer in routes["district_layers"]:
        assert (ROOT / layer["kml_path"]).exists()
        assert (ROOT / layer["geojson_path"]).exists()


def test_hosted_offline_shell_precaches_route_ui_and_help():
    build = (ROOT / "scripts/build_dual_release.py").read_text(encoding="utf-8")
    assert "./challenges/arquitectura-en-foco/iphone-maps.html" in build
    assert "./data/architecture/routes.json" in build
