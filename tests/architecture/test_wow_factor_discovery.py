import json
from pathlib import Path

from scripts.architecture_geography import classify_candidate


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = (
    ROOT
    / "architectural_photography"
    / "research"
    / "locations"
    / "wow_factor_discovery_2026-08-28.json"
)


def load_hypotheses():
    return json.loads(DISCOVERY.read_text(encoding="utf-8"))["hypotheses"]


def test_wow_discoveries_are_authoritatively_sourced_and_in_scope():
    hypotheses = load_hypotheses()
    assert len(hypotheses) >= 8
    assert all(classify_candidate(item["district"]).startswith("ELIGIBLE_") for item in hypotheses)
    assert all(len(item["sources"]) >= 2 for item in hypotheses)
    assert all(
        {source["source_type"] for source in item["sources"]}
        & {"OFFICIAL", "PRIMARY", "ACADEMIC", "PROFESSIONAL"}
        for item in hypotheses
    )


def test_wow_is_a_scene_mechanism_not_a_fame_or_award_bonus():
    for item in load_hypotheses():
        assert item["distinct_scene_mechanism"]
        assert item["one_frame_hypothesis"]
        assert item["expert_rejection"]
        assert item["kill_condition"]
        assert item["fame_bonus"] is False
        assert item["award_bonus"] is False


def test_discovery_does_not_bypass_equal_depth_or_current_access_gates():
    allowed = {"ADMIT_PENDING_EQUAL_DEPTH", "DISCOVERY_ONLY", "QUARANTINE_CURRENTITY"}
    for item in load_hypotheses():
        assert item["disposition"] in allowed
        assert item["ranking_eligible"] is False
        assert item["route_eligible"] is False
        assert item["equal_depth_required"] is True
        assert item["current_access_status"] in {
            "PARTIAL",
            "UNRESOLVED",
            "VERIFY_BEFORE_ROUTE",
        }


def test_admitted_discoveries_identify_what_they_add_to_the_existing_mix():
    admitted = [
        item for item in load_hypotheses()
        if item["disposition"] == "ADMIT_PENDING_EQUAL_DEPTH"
    ]
    assert len(admitted) >= 4
    assert all(item["distinct_from_existing"] for item in admitted)
