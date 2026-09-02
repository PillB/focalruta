import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOSSIERS = ROOT / "architectural_photography/research/locations/style_discovery_dossiers.json"
EXPECTED_IDS = {
    "utec-campus-barranco",
    "torre-interbank",
    "casa-fernandini-1913",
    "estacion-desamparados",
    "edificio-petroperu",
    "torre-begonias",
}
PASSES = {
    "source_truth", "original_spatial_contract", "current_life",
    "human_verbs_or_meaningful_absence", "architectural_causality",
    "visual_forensic_saturation", "light_material_geometry",
    "position_then_optics", "moment_logistics_ethics", "one_frame_contest_test",
}
PROOFS = {"A_STRUCTURE", "B_HABITAR", "C_ANTI_POSTAL", "D_LIGHT_MATERIAL", "E_ONE_FRAME_STORY"}


def records():
    return json.loads(DOSSIERS.read_text(encoding="utf-8"))["records"]


def test_all_six_style_discoveries_have_equal_depth_dossiers():
    items = records()
    assert {item["canonical_id"] for item in items} == EXPECTED_IDS
    for item in items:
        assert item["status"] == "DESK_VERIFIED_RANKED_ROUTED"
        assert set(item["passes"]) == PASSES
        assert all(check["answer"] and check["source_ids"] for check in item["passes"].values())
        assert set(item["proofs"]) == PROOFS
        assert len(item["composition_questions"]) == 3
        assert len(item["visual_reference_families"]) >= 3
        assert item["ranking_eligible"] is True
        assert item["route_eligible"] is True


def test_style_dossier_proofs_are_field_ready_and_source_backed():
    required = {
        "position", "camera_height", "orientation", "lens", "exposure_intent",
        "expected_action", "light", "edge_guards", "wait_trigger", "kill_trigger",
        "access_ethics", "fallback",
    }
    for item in records():
        assert item["latitude"] and item["longitude"]
        assert len(item["sources"]) >= 3
        assert all(source["url"].startswith("https://") for source in item["sources"])
        for proof in item["proofs"].values():
            assert proof["status"] == "READY_FOR_FIELD"
            assert proof["source_ids"]
            assert required <= proof.keys()
            assert all(proof[field] for field in required)
        for reference in item["visual_reference_families"]:
            assert reference["page_url"].startswith("https://")
            assert reference["redistribution"] == "LINK_ONLY"


def test_style_dossiers_enter_canonical_ranking_and_verified_routes():
    candidate_ids = {
        item["canonical_id"]
        for item in json.loads((ROOT / "data/architecture/candidates.json").read_text(encoding="utf-8"))
    }
    ranking_ids = {
        item["canonical_id"]
        for item in json.loads((ROOT / "data/architecture/ranking.json").read_text(encoding="utf-8"))["results"]
    }
    assert EXPECTED_IDS <= candidate_ids
    assert EXPECTED_IDS <= ranking_ids
    assert all(item["route_eligible"] for item in json.loads((ROOT / "data/architecture/ranking.json").read_text(encoding="utf-8"))["results"] if item["canonical_id"] in EXPECTED_IDS)


def test_generated_site_reports_completed_promoted_dossiers():
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    assert "6/6 dossiers incorporados al ranking" in page
    assert "¿Puedes mostrar en una sola imagen cómo se usa hoy este espacio?" in page
    assert "incorporados al ranking" in page
