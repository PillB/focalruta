from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "index.html"
CHALLENGE = ROOT / "challenges/arquitectura-en-foco/index.html"
BUILD = ROOT / "scripts/build_dual_release.py"
CANDIDATES = ROOT / "data/architecture/candidates.json"
VERIFICATION = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
MODULE_INVENTORY = ROOT / "architectural_photography/ARCHITECTURE_MODULE_INVENTORY.json"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_home_discovers_architecture_challenge():
    home = text(HOME)
    assert 'href="challenges/arquitectura-en-foco/"' in home
    assert "Fotografía arquitectónica" in home


def test_home_explains_architecture_challenge_in_a_content_landmark():
    home = text(HOME)
    assert 'id="architecture-challenge"' in home
    challenge = home.split('id="architecture-challenge"', 1)[1].split("</section>", 1)[0]
    assert 'aria-labelledby="architecture-challenge-title"' in challenge
    assert "87 lugares y escenas" in challenge
    assert "rutas peatonales" in challenge.lower()
    assert 'href="challenges/arquitectura-en-foco/"' in challenge
    assert "Abrir fotografía arquitectónica" in challenge


def test_architecture_module_inventory_maps_every_public_module_to_evidence():
    import json

    inventory = json.loads(text(MODULE_INVENTORY))
    required = {
        "today", "ranking", "field-priorities", "route", "style-radar", "scenes",
        "learn", "field-run", "ai-firewall", "rules", "iphone-maps", "offline-shell",
    }
    modules = {item["module_id"]: item for item in inventory["modules"]}
    assert required <= modules.keys()
    assert all(item["public_surface"] and item["verification"] for item in modules.values())
    assert inventory["main_site_entry"] == "#architecture-challenge"
    assert inventory["return_navigation"] == "../../index.html"


def test_challenge_has_task_navigation_and_truthful_queue_language():
    page = text(CHALLENGE)
    for anchor in ("#today", "#scenes", "#learn", "#field-run", "#rules"):
        assert f'href="{anchor}"' in page
    assert "87 lugares y escenas" in page
    assert "scroll-margin-top:70px" in page
    assert "Top 3" not in page
    assert "probabilidad de ganar" not in page.lower()


def test_user_can_choose_scene_count_or_all_without_implying_rank():
    page = text(CHALLENGE)
    assert 'id="scene-limit"' in page
    assert 'value="all"' in page
    assert "Mostrar N escenas" in page
    assert "applySceneLimit" in page
    assert "sceneLimit" in page
    assert "Top 3" not in page
    assert page.count('class="scene"') >= 81
    assert "Torres de Limatambo" in page
    assert "Residencial San Felipe" in page
    assert "PREVI Lima" in page


def test_public_candidate_universe_contains_all_87_without_rank_fields():
    candidates = __import__("json").loads(text(CANDIDATES))
    assert len(candidates) == 87
    assert len({item["canonical_id"] for item in candidates}) == 87
    prohibited = {"R0", "R1", "R2", "R3", "masterRank", "fieldRank", "robustIndex"}
    assert all(prohibited.isdisjoint(item) for item in candidates)
    assert sum(item["ranking_eligible"] for item in candidates) == 6


def test_generated_progress_matches_equal_depth_ledger_without_promotion():
    import json

    candidates = json.loads(text(CANDIDATES))
    verification = json.loads(text(VERIFICATION))["records"]
    expected = {
        item["canonical_id"]: len(item["visual_reference_families"])
        for item in verification
    }
    expected_started = sum(count > 0 for count in expected.values())
    expected_complete = sum(item["verification_complete"] for item in verification)
    assert {item["canonical_id"]: item["visual_reference_count"] for item in candidates} == expected
    assert sum(item["visual_reference_count"] > 0 for item in candidates) == expected_started
    assert sum(item["ranking_eligible"] for item in candidates) == 6
    assert sum(item["verification_complete"] for item in candidates) == expected_complete
    page = text(CHALLENGE)
    assert f"{expected_started} tienen forénsica visual" in page
    assert f"{expected_complete} dossier de escritorio verificado" in page
    assert "seis tienen verificación iniciada" not in page


def test_field_run_is_local_persistent_and_portable():
    page = text(CHALLENGE)
    assert "focalruta.architecture.field.v1" in page
    assert "localStorage" in page
    assert 'id="export-field"' in page
    assert 'id="import-field"' in page
    assert "STAY" in page and "MOVE" in page and "RETURN_OTHER_LIGHT" in page


def test_no_js_fallback_contains_queue_protocol_and_rules():
    page = text(CHALLENGE)
    noscript = page.split("<noscript>", 1)[1].split("</noscript>", 1)[0]
    assert "Matriz sin JavaScript" in noscript
    assert "87 tarjetas" in noscript
    assert "los filtros requieren JavaScript" in noscript
    assert "CONTRATO vs USO" in noscript
    assert "elegibilidad, tema, archivos, fechas, permisos" in noscript


def test_hosted_build_copies_and_precaches_architecture_core():
    build = text(BUILD)
    assert "challenges/arquitectura-en-foco" in build
    assert "data/architecture" in build
    assert "./challenges/arquitectura-en-foco/index.html" in build


def test_architecture_page_excludes_irrelevant_pose_and_dog_flows():
    page = text(CHALLENGE).lower()
    assert "pose coach" not in page
    assert "flujo de perro" not in page
