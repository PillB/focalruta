import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
EVIDENCE = ROOT / "architectural_photography/research/locations/equal_depth_evidence.json"

def records():
    return json.loads(LEDGER.read_text(encoding="utf-8"))["records"]

def test_all_81_candidates_have_identical_verification_shape():
    items = records()
    assert len(items) == 81
    assert len({item["canonical_id"] for item in items}) == 81
    shapes = {(tuple(item["passes"]), tuple(item["proofs"])) for item in items}
    assert len(shapes) == 1
    passes, proofs = next(iter(shapes))
    assert len(passes) == 10
    assert proofs == ("A_STRUCTURE", "B_HABITAR", "C_ANTI_POSTAL", "D_LIGHT_MATERIAL", "E_ONE_FRAME_STORY")

def test_no_candidate_is_complete_or_rankable_from_historical_detail_alone():
    for item in records():
        assert item["verification_complete"] is False
        assert item["ranking_eligible"] is False
        assert item["route_eligible"] is False
        assert all(check["status"] in {"NOT_STARTED", "PARTIAL", "CORROBORATED", "VERIFIED"} for check in item["passes"].values())
        assert all(check["status"] == "NOT_STARTED" for check in item["proofs"].values())

def test_partial_evidence_updates_are_source_linked_without_promotion():
    items = {item["canonical_id"]: item for item in records()}
    updates = json.loads(EVIDENCE.read_text(encoding="utf-8"))["candidate_updates"]
    assert sum(item["verification_status"] == "IN_PROGRESS" for item in items.values()) == len(updates)
    for item in items.values():
        for check in item["passes"].values():
            if check["status"] != "NOT_STARTED":
                assert check["source_ids"]
        assert item["verification_complete"] is False
