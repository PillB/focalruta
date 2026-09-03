import json
import hashlib
from pathlib import Path
import subprocess
import sys
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / "data/architecture/routes.json"
RUNS = ROOT / "architectural_photography/routes/route_runs"
GEOCODES = ROOT / "architectural_photography/research/route_inputs/nominatim_candidates.json"
DISCOVERIES = ROOT / "data/architecture/style_discoveries.json"
MANUAL_ANCHORS = ROOT / "architectural_photography/research/route_inputs/manual_anchors.json"


def load_routes():
    return json.loads(ROUTES.read_text(encoding="utf-8"))


def test_manual_anchors_require_address_and_coordinate_provenance():
    payload = json.loads(MANUAL_ANCHORS.read_text(encoding="utf-8"))
    assert payload["publication_gate"] == "source-backed address plus independent coordinate and district containment"
    assert len(payload["anchors"]) >= 3
    routed_ids = {stop["canonical_id"] for layer in load_routes()["district_layers"] for stop in layer["stops"]}
    for anchor in payload["anchors"]:
        assert anchor["canonical_id"] in routed_ids
        assert anchor["address_source_url"].startswith("https://")
        assert anchor["coordinate_source_url"].startswith("https://")
        assert anchor["address_source_url"] != anchor["coordinate_source_url"]
        assert anchor["confidence"] >= 0.8
        assert anchor["status"] == "CORROBORATED_ADDRESS_COORDINATE"


def test_anchor_research_resolves_most_canonical_scenes_for_review():
    payload = json.loads(GEOCODES.read_text(encoding="utf-8"))
    resolved = [record for record in payload["records"] if record["results"]]
    assert len(resolved) >= 50
    previ = next(record for record in payload["records"] if record["canonical_id"] == "previ-lima")
    assert previ["status"] == "REVIEW_REQUIRED"
    assert all(stop["canonical_id"] != "previ-lima" for layer in load_routes()["district_layers"] for stop in layer["stops"])


def test_style_discoveries_are_source_backed_ranked_and_route_closed():
    discoveries = json.loads(DISCOVERIES.read_text(encoding="utf-8"))["discoveries"]
    ranking = json.loads((ROOT / "data/architecture/ranking.json").read_text(encoding="utf-8"))
    ranked_ids = {item["canonical_id"] for item in ranking["results"]}
    assert len(discoveries) >= 6
    style_text = " ".join(item["style_signal"] for item in discoveries)
    assert all(term in style_text for term in ("contemporary", "Art Nouveau", "brutalism"))
    assert all(item["source_url"].startswith("https://") and item["status"].startswith("ADMISSION_PENDING") for item in discoveries)
    discovery_ids = {item["discovery_id"] for item in discoveries}
    assert discovery_ids <= ranked_ids
    assert all(item["route_eligible"] for item in ranking["results"] if item["canonical_id"] in discovery_ids)


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
    assert sum(len(layer["stops"]) for layer in routes["district_layers"]) >= 50


def test_route_builder_stages_outputs_before_atomic_publish():
    source = (ROOT / "scripts/build_architecture_routes.py").read_text(encoding="utf-8")
    assert "TemporaryDirectory" in source
    assert "os.replace" in source
    assert '"--retry-all-errors"' in source
    assert source.index("build_district_layers") < source.index("publish_downloads(staging)")


def test_every_layer_is_district_pure_and_every_stop_is_contained():
    routes = load_routes()
    for layer in routes["district_layers"]:
        assert layer["district"]
        assert layer["containment_status"] == "VERIFIED"
        assert layer["route_geometry_containment_status"] == "VERIFIED"
        assert layer["stops"]
        for stop in layer["stops"]:
            assert stop["district"] == layer["district"]
            assert stop["point_in_district"] is True
            assert -12.6 < stop["latitude"] < -11.5
            assert -77.3 < stop["longitude"] < -76.5


def test_known_miraflores_boundary_exit_is_split_not_published():
    routes = load_routes()
    traditions = [
        layer
        for layer in routes["district_layers"]
        if any(stop["canonical_id"] == "parque-tradiciones-ricardo-palma" for stop in layer["stops"])
    ]
    assert len(traditions) == 1
    assert len(traditions[0]["stops"]) == 1
    assert not traditions[0]["legs"]


def test_snapshot_boundary_repair_is_idempotent():
    command = [sys.executable, str(ROOT / "scripts/repair_architecture_route_snapshot.py")]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    first = hashlib.sha256(ROUTES.read_bytes()).hexdigest()
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    second = hashlib.sha256(ROUTES.read_bytes()).hexdigest()
    assert first == second


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
            assert leg["eta_label"] in {"snapshot estimate", "estimación recta · validar en campo"}
            assert leg["road_distance_m"] <= 1500
            if leg["road_distance_m"] > 1000:
                assert leg.get("evidence_status") == "STRAIGHT_LINE_THRESHOLD_SCREEN_NOT_ROAD_ROUTING"


def test_long_intertour_transfers_are_removed_and_disclosed_not_hidden():
    routes = load_routes()
    gaps = routes["omitted_intertour_transfers"]
    assert gaps
    routed_ids = {stop["canonical_id"] for layer in routes["district_layers"] for stop in layer["stops"]}
    for gap in gaps:
        assert gap["from"] in routed_ids and gap["to"] in routed_ids
        assert gap["road_distance_m"] > 800
        assert gap["reason"] == "EXCEEDS_PHOTOGRAPHY_TOUR_TRANSFER_LIMIT"
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    assert "traslados omitidos" in page
    assert "no se presentan como caminata continua" in page


def test_compact_partition_never_creates_new_singleton_layers():
    routes = load_routes()
    partitioned = [layer for layer in routes["district_layers"] if layer.get("route_partition")]
    assert partitioned
    assert all(len(layer["stops"]) >= 2 for layer in partitioned)
    for layer in routes["district_layers"]:
        for index, leg in enumerate(layer["legs"]):
            if leg["road_distance_m"] > 800:
                assert index == 0 or index == len(layer["legs"]) - 1


def test_short_network_detour_is_not_mislabeled_as_a_long_transfer():
    from tests.architecture.browser_round5_route_qa import route_assessment

    assessment = route_assessment({"road_distance_m": 406}, 1.87)
    assert assessment == "short road-conforming detour; barrier pattern disclosed"


def test_generated_page_separates_long_transfers_instead_of_recommending_them():
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    assert "Transferencia larga:" not in page
    assert "Tour separado" in page
    assert "no se presentan como caminata continua" in page
    assert page.count("Traslado terminal conservado:") == 7
    assert "Separarlo aislaría una escena" in page


def test_route_builder_does_not_use_preferred_transfer_as_connectivity_ceiling():
    source = (ROOT / "scripts/build_architecture_routes.py").read_text(encoding="utf-8")
    assert "MAX_WALKING_LEG_M = 1000" in source


def test_repaired_subpath_is_not_presented_as_a_new_exact_minimum():
    """A subpath kept from a parent solution may never claim its own optimum.

    The count is not fixed: a router rebuild can remove the need for a repair
    entirely. What must hold is that any surviving subpath is disclosed as one
    and declares no exact minimum.
    """
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    routes = load_routes()
    subpaths = [layer for layer in routes["district_layers"] if "subpath" in layer["optimization"]["method"]]
    for layer in subpaths:
        assert layer["optimization"]["exact_minimum_distance_m"] is None, layer.get("layer_id")
        assert layer["optimization"]["optimization_limitation"]
    disclosed = "no se presenta como un nuevo mínimo exacto" in page
    assert disclosed == bool(subpaths), (
        "the subpath disclaimer must appear exactly when a subpath is published"
    )
    exact = [layer for layer in routes["district_layers"] if layer["optimization"]["method"] == "exact_permutation"]
    assert all(layer["optimization"]["exact_minimum_distance_m"] is not None for layer in exact)


def test_small_tours_are_checked_by_exact_permutation():
    routes = load_routes()
    for layer in routes["district_layers"]:
        if len(layer["stops"]) <= 9:
            optimization = layer["optimization"]
            if optimization["method"] == "exact_permutation":
                assert optimization["permutations_evaluated"] >= 1
                assert optimization["selected_distance_m"] == optimization["exact_minimum_distance_m"]
            elif optimization["method"] == "singleton":
                assert optimization["selected_distance_m"] == 0
            else:
                assert optimization["method"] in {"verified_subpath_from_exact_parent", "verified_compact_subpath_from_exact_parent", "threshold_sensitivity_merge"}
                assert optimization["exact_minimum_distance_m"] is None
                assert optimization["optimization_limitation"]


def test_downloads_and_eli5_iphone_help_exist():
    routes = load_routes()
    help_text = (ROOT / "challenges/arquitectura-en-foco/iphone-maps.html").read_text(encoding="utf-8")
    assert "iPhone 13 Pro" in help_text
    assert "You" in help_text and "Maps" in help_text
    assert "Arquitectura en Foco" not in help_text
    field_card = ROOT / "challenges/arquitectura-en-foco/field-card.html"
    assert field_card.exists() and "TARJETA DESCARGABLE" in field_card.read_text(encoding="utf-8")
    for layer in routes["district_layers"]:
        assert (ROOT / layer["kml_path"]).exists()
        assert (ROOT / layer["geojson_path"]).exists()
        assert all(stop.get("address") and stop.get("latitude") is not None and stop.get("longitude") is not None for stop in layer["stops"])
        assert layer.get("offline_map_path") and (ROOT / layer["offline_map_path"]).exists()


def test_route_collections_never_call_single_points_tours_and_group_all_layers():
    routes = load_routes()
    collections = routes["route_collections"]
    assert collections
    assert all(collection["segments"] or collection["independent_points"] for collection in collections)
    assert all("singleton" not in collection["title"].lower() for collection in collections)
    layer_ids = {layer_id for collection in collections for layer_id in collection["layer_ids"]}
    assert layer_ids == {layer["layer_id"] for layer in routes["district_layers"]}
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    assert "Colecciones de ruta" in page
    assert "Punto independiente" in page


def test_beginner_guide_explains_every_major_surface_in_plain_spanish():
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    for phrase in ("Matriz de preparación", "Tarjeta de lugar", "Laboratorio", "Ruta y colección", "Brief", "SIN CONOCIMIENTOS PREVIOS"):
        assert phrase in page
    assert "no una nota ni una predicción" in page


def test_public_copy_removes_known_english_prose_and_keeps_readable_gutters():
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    for phrase in ("The frame passes", "Natural light before lighting complexity", "A cliff-like teaching section", "Caption must", "<strong>Kill:</strong>", "RETURN OTHER LIGHT", ">STAY<", ">MOVE<"):
        assert phrase not in page
    assert "padding-inline:clamp(24px,6vw,72px)" in page


def test_iphone_help_explains_direct_link_and_kml_failure_recovery():
    help_text = (ROOT / "challenges/arquitectura-en-foco/iphone-maps.html").read_text(encoding="utf-8")
    assert "Si el enlace no abre" in help_text
    assert "mantén pulsado" in help_text
    assert "Archivos" in help_text
    assert "no se importa directamente" in help_text


def test_download_layers_include_road_conforming_lines_not_only_pins():
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    for layer in load_routes()["district_layers"]:
        geojson = json.loads((ROOT / layer["geojson_path"]).read_text(encoding="utf-8"))
        line_features = [feature for feature in geojson["features"] if feature["geometry"]["type"] == "LineString"]
        assert len(line_features) == len(layer["legs"])
        for feature, leg in zip(line_features, layer["legs"]):
            assert feature["geometry"] == leg["geometry"]
            assert feature["properties"]["road_distance_m"] == leg["road_distance_m"]
        kml_root = ElementTree.parse(ROOT / layer["kml_path"]).getroot()
        assert len(kml_root.findall(".//kml:LineString", namespace)) == len(layer["legs"])


def test_each_multistop_route_card_has_accessible_road_shape_preview():
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    expected = sum(bool(layer["legs"]) for layer in load_routes()["district_layers"])
    assert page.count('class="route-preview"') == expected
    assert page.count('role="img" aria-label="Trazado peatonal') == expected
    assert "La línea sigue la geometría peatonal OSM capturada" in page


def test_route_ui_exposes_district_filter_and_singleton_map_links():
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    assert 'id="route-district"' in page
    assert 'id="route-cards"' in page
    assert "applyRouteFilter" in page
    routes = load_routes()
    assert all(layer["stages"] or layer["google_maps_search_url"] for layer in routes["district_layers"])


def test_hosted_offline_shell_precaches_route_ui_and_help():
    build = (ROOT / "scripts/build_dual_release.py").read_text(encoding="utf-8")
    assert "./challenges/arquitectura-en-foco/iphone-maps.html" in build
    assert "./data/architecture/routes.json" in build
    assert "u.pathname.endsWith('/')?u.pathname+'index.html'" in build
