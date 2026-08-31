import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "architecture"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_official_rules_exact_compliance_contract():
    rules = load("competition_rules.json")
    assert rules["submission"]["photo_count"] == 1
    assert rules["eligibility"] == {"minimum_age": 18, "residency": ["Chile", "Peru", "Colombia"]}
    assert rules["file"]["extensions"] == [".jpg", ".jpeg"]
    assert rules["file"]["minimum_bytes"] == 5_000_000
    assert rules["file"]["maximum_bytes"] == 25_000_000
    assert rules["capture"]["minimum_year"] == 2020
    assert rules["submission"]["filename_pattern"] == "nombre-apellido"


def test_adjustments_and_prohibitions_are_exact_and_distinct():
    rules = load("competition_rules.json")
    assert rules["editing"]["allowed_basic_adjustments"] == [
        "composition_crop",
        "white_balance",
        "black_and_white_conversion",
        "brightness",
        "contrast",
        "sharpness",
        "color_correction",
    ]
    assert set(rules["editing"]["prohibited"]) == {
        "fundamental_element_retouch",
        "ai_generated_intervened_or_edited",
        "collage_montage_or_reality_altering_composition",
    }


def test_dates_jurors_criteria_and_source_discrepancies():
    rules = load("competition_rules.json")
    assert rules["dates"] == {
        "opens": "2026-07-30",
        "closes_local": "2026-08-30T23:59:00",
        "queries_through": "2026-08-29",
        "results": "2026-10-22",
    }
    assert rules["jurors"] == ["Cristián Aninat", "Hans Stoll", "Camilo Monzón"]
    assert rules["official_criteria"] == ["Propuesta creativa y estética", "Coherencia con la temática"]
    discrepancy_ids = {item["discrepancy_id"] for item in rules["source_discrepancies"]}
    assert discrepancy_ids == {"DISC-FILE-MINIMUM", "DISC-JUROR-NAMES"}


def test_ai_firewall_is_single_and_candidate_image_safe():
    rules = load("competition_rules.json")
    firewall = rules["ai_firewall"]
    assert firewall["ui_instance_limit"] == 1
    assert firewall["planning_allowed"] is True
    assert firewall["candidate_image_ai_workflow"] == "PROHIBITED_UNLESS_EXACT_ORGANIZER_AUTHORIZATION_STORED"


def test_every_material_rule_has_primary_source_and_status():
    rules = load("competition_rules.json")
    assert rules["source_ids"]
    assert rules["evidence_status"] == "VERIFIED"
    sources = load("sources.json")
    known = {source["source_id"] for source in sources}
    assert set(rules["source_ids"]) <= known
    assert all(source["url_or_path"] for source in sources)
