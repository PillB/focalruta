import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / "architectural_photography" / "research" / "locations" / "user_discovery_intake_2026-08-27.json"


def test_user_places_are_preserved_without_automatic_promotion():
    data = json.loads(INTAKE.read_text(encoding="utf-8"))
    assert data["intake_id"] == "USER-PLACES-2026-08-27-A"
    assert [item["user_label"] for item in data["hypotheses"]] == [
        "Parque americas",
        "El queirolo",
        "Iglesia santo domingo",
        "Iglesia de la soledad",
        "Huaca de breña",
    ]
    assert all(item["ranking_eligible"] is False for item in data["hypotheses"])
    assert all(item["route_eligible"] is False for item in data["hypotheses"])
    assert all(item["expert_rejection"] for item in data["hypotheses"])


def test_known_candidates_merge_by_identity_and_new_places_remain_discovery_edges():
    hypotheses = {
        item["user_label"]: item
        for item in json.loads(INTAKE.read_text(encoding="utf-8"))["hypotheses"]
    }
    assert hypotheses["Parque americas"]["disposition"] == "MERGE_EXISTING_CANONICAL_IDENTITY"
    assert hypotheses["El queirolo"]["disposition"] == "MERGE_EXISTING_CANONICAL_IDENTITY"
    assert hypotheses["Iglesia santo domingo"]["disposition"] == "NEW_DISCOVERY_EDGE"
    assert hypotheses["Iglesia de la soledad"]["disposition"] == "NEW_DISCOVERY_EDGE"


def test_huaca_de_brena_identity_is_not_silently_assumed():
    item = next(
        item
        for item in json.loads(INTAKE.read_text(encoding="utf-8"))["hypotheses"]
        if item["user_label"] == "Huaca de breña"
    )
    assert item["disposition"] == "IDENTITY_UNRESOLVED"
    assert {candidate["canonical_name"] for candidate in item["identity_hypotheses"]} == {
        "Complejo Arqueológico Mateo Salado",
        "Huaca Independencia",
    }
    assert all(candidate["district"] in {"Lima", "Breña"} for candidate in item["identity_hypotheses"])
