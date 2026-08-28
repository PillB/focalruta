from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "index.html"
CHALLENGE = ROOT / "challenges/arquitectura-en-foco/index.html"
BUILD = ROOT / "scripts/build_dual_release.py"
CANDIDATES = ROOT / "data/architecture/candidates.json"
VERIFICATION = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_home_discovers_architecture_challenge():
    home = text(HOME)
    assert 'href="challenges/arquitectura-en-foco/"' in home
    assert "Arquitectura en Foco" in home


def test_challenge_has_task_navigation_and_truthful_queue_language():
    page = text(CHALLENGE)
    for anchor in ("#today", "#scenes", "#learn", "#field-run", "#rules"):
        assert f'href="{anchor}"' in page
    assert "81 lugares y escenas" in page
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


def test_public_candidate_universe_contains_all_81_without_rank_fields():
    candidates = __import__("json").loads(text(CANDIDATES))
    assert len(candidates) == 81
    assert len({item["canonical_id"] for item in candidates}) == 81
    prohibited = {"R0", "R1", "R2", "R3", "masterRank", "fieldRank", "robustIndex"}
    assert all(prohibited.isdisjoint(item) for item in candidates)
    assert all(item["ranking_eligible"] is False for item in candidates)


def test_generated_progress_matches_equal_depth_ledger_without_promotion():
    import json

    candidates = json.loads(text(CANDIDATES))
    verification = json.loads(text(VERIFICATION))["records"]
    expected = {
        item["canonical_id"]: len(item["visual_reference_families"])
        for item in verification
    }
    expected_started = sum(count > 0 for count in expected.values())
    assert {item["canonical_id"]: item["visual_reference_count"] for item in candidates} == expected
    assert sum(item["visual_reference_count"] > 0 for item in candidates) == expected_started
    assert all(item["ranking_eligible"] is False for item in candidates)
    page = text(CHALLENGE)
    assert f"{expected_started} tienen forénsica visual iniciada" in page
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
    assert "Escenas en verificación" in noscript
    assert "CONTRATO vs USO" in noscript
    assert "5–25 MB" in noscript


def test_hosted_build_copies_and_precaches_architecture_core():
    build = text(BUILD)
    assert "challenges/arquitectura-en-foco" in build
    assert "data/architecture" in build
    assert "./challenges/arquitectura-en-foco/index.html" in build


def test_architecture_page_excludes_irrelevant_pose_and_dog_flows():
    page = text(CHALLENGE).lower()
    assert "pose coach" not in page
    assert "flujo de perro" not in page
