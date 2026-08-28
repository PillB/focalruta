import json
from pathlib import Path

from scripts.architecture_geography import classify_candidate


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "data" / "architecture" / "geography.json"


def test_lima_metropolitana_is_exactly_the_43_district_province_scope():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert policy["jurisdiction"] == "Lima Metropolitana (Provincia de Lima)"
    assert len(policy["eligible_districts"]) == 43
    assert len(set(policy["eligible_districts"])) == 43
    assert "Callao" not in policy["eligible_districts"]
    assert policy["outside_scope_action"] == "QUARANTINE_OUT_OF_SCOPE"


def test_user_named_districts_are_priority_field_territory():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert {
        "Lima", "San Isidro", "Miraflores", "San Borja", "Barranco",
        "Pueblo Libre", "Magdalena del Mar", "Surquillo", "Lince",
    } <= set(policy["priority_districts"])


def test_candidate_admission_fails_closed_outside_lima_province():
    assert classify_candidate("San Isidro") == "ELIGIBLE_PRIORITY"
    assert classify_candidate("Rímac") == "ELIGIBLE_METROPOLITAN"
    assert classify_candidate("Callao") == "QUARANTINE_OUT_OF_SCOPE"
    assert classify_candidate("Cusco") == "QUARANTINE_OUT_OF_SCOPE"
    assert classify_candidate("") == "QUARANTINE_UNRESOLVED_DISTRICT"
