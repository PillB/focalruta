import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "architectural_photography/research/locations"
LEDGER = EVIDENCE_DIR / "equal_depth_verification.json"

def batches():
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(EVIDENCE_DIR.glob("visual_reference_evidence*.json"))]

def test_visual_references_have_forensic_limits_and_link_only_policy():
    required = {"reference_id", "page_url", "image_url", "publisher", "viewpoint_family", "likely_camera_height", "fov_class", "light_weather", "people_activity", "edge_background", "cliche_cluster", "proves", "cannot_prove", "redistribution"}
    references = [reference for batch in batches() for update in batch["candidate_updates"] for reference in update["reference_families"]]
    assert references
    assert len({reference["reference_id"] for reference in references}) == len(references)
    for reference in references:
        assert required <= reference.keys()
        assert all(reference[field] for field in required)
        assert reference["page_url"].startswith("https://")
        assert reference["image_url"].startswith("https://")
        assert reference["redistribution"] == "LINK_ONLY"

def test_visual_intake_updates_ledger_without_promoting_candidates_by_itself():
    ledger = {item["canonical_id"]: item for item in json.loads(LEDGER.read_text(encoding="utf-8"))["records"]}
    updates = [update for batch in batches() for update in batch["candidate_updates"]]
    for update in updates:
        item = ledger[update["canonical_id"]]
        ledger_references = {
            reference["reference_id"]: reference
            for reference in item["visual_reference_families"]
        }
        assert all(
            ledger_references[reference["reference_id"]] == reference
            for reference in update["reference_families"]
        )
        if item["verification_complete"]:
            assert all(
                check["status"] in {"CORROBORATED", "VERIFIED"}
                for check in item["passes"].values()
            )
            assert all(
                proof["status"] == "READY_FOR_FIELD"
                for proof in item["proofs"].values()
            )
        assert item["ranking_eligible"] is False
        assert item["route_eligible"] is False
