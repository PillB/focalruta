import json
from pathlib import Path

import pytest

from scripts.select_architecture_verification_cohort import select_cohort


ROOT = Path(__file__).resolve().parents[2]
LOCATION_ROOT = ROOT / "architectural_photography" / "research" / "locations"


def load_json(name):
    return json.loads((LOCATION_ROOT / name).read_text(encoding="utf-8"))


def test_cohort_is_bounded_unranked_and_current_source_gated():
    cohort = load_json("verification_cohort.json")
    assert cohort["selection_type"] == "UNORDERED_RESEARCH_QUEUE"
    assert cohort["ranking_model_version"] is None
    assert cohort["ranking_run_id"] is None
    assert cohort["route_run_id"] is None
    assert len(cohort["candidates"]) == 6
    assert all(item["ranking_eligible"] is False for item in cohort["candidates"])
    assert all(item["route_eligible"] is False for item in cohort["candidates"])
    assert all(item["current_primary_sources"] for item in cohort["candidates"])
    assert all(item["access_status"] != "CLOSED" for item in cohort["candidates"])


def test_selector_is_invariant_to_historical_rank_and_input_order():
    pool = load_json("verification_pool.json")
    baseline = select_cohort(pool)
    contaminated = []
    for rank, item in enumerate(reversed(pool), start=1):
        item = dict(item)
        item.update({"masterRank": rank, "robustIndex": 999 - rank, "fieldRank": rank})
        contaminated.append(item)
    assert select_cohort(contaminated) == baseline


def test_cohort_uses_unique_identities_and_scene_mechanisms():
    candidates = load_json("verification_cohort.json")["candidates"]
    assert len({item["canonical_id"] for item in candidates}) == len(candidates)
    assert len({item["primary_scene_mechanism"] for item in candidates}) == len(candidates)
    assert all(item["evidence_status"] == "RESEARCH_QUEUE" for item in candidates)


def test_user_suggested_existing_identities_are_in_research_queue_not_promoted():
    candidates = {item["canonical_id"]: item for item in load_json("verification_cohort.json")["candidates"]}
    assert "parque-de-las-americas" in candidates
    assert "antigua-taberna-queirolo" in candidates
    assert candidates["parque-de-las-americas"]["selection_reasons"][-1] == "USER_DISCOVERY_IDEA"
    assert candidates["antigua-taberna-queirolo"]["selection_reasons"][-1] == "USER_DISCOVERY_IDEA"


def test_unresolved_or_new_discovery_edges_cannot_enter_canonical_cohort():
    pool = load_json("verification_pool.json") + [{
        "canonical_id": None,
        "name": "Huaca de Breña",
        "district": "Breña",
        "identity_resolved": False,
        "geography_eligible": True,
        "source_last_verified_at": "2026-08-27",
        "current_primary_sources": ["https://example.invalid"],
        "access_status": "UNKNOWN",
        "primary_scene_mechanism": "ARCHAEOLOGICAL_EDGE",
    }]
    assert all(item["name"] != "Huaca de Breña" for item in select_cohort(pool))


def test_selector_fails_closed_instead_of_alphabetically_dropping_seventh_candidate():
    pool = load_json("verification_pool.json") + [{
        "canonical_id": "biblioteca-nacional-del-peru",
        "name": "Biblioteca Nacional del Perú",
        "district": "San Borja",
        "identity_resolved": True,
        "geography_eligible": True,
        "source_last_verified_at": "2026-08-27",
        "current_primary_sources": ["https://www.bnp.gob.pe/"],
        "access_status": "MANAGED_PUBLIC",
        "permission": "VERIFY_INTERIOR_PHOTOGRAPHY",
        "primary_scene_mechanism": "INSTITUTIONAL_ORDER_AND_MEANINGFUL_ABSENCE",
        "selection_reasons": ["CURRENT_INSTITUTIONAL_SOURCE"],
        "expert_rejection": "Access does not prove scene strength.",
    }]
    with pytest.raises(ValueError, match="explicit displacement decision"):
        select_cohort(pool)
