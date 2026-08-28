#!/usr/bin/env python3
"""Build the fail-closed equal-depth verification ledger for every candidate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/architecture/candidates.json"
OUTPUT = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
EVIDENCE = ROOT / "architectural_photography/research/locations/equal_depth_evidence.json"
PASSES = [
    "source_truth", "original_spatial_contract", "current_life",
    "human_verbs_or_meaningful_absence", "architectural_causality",
    "visual_forensic_saturation", "light_material_geometry",
    "position_then_optics", "moment_logistics_ethics", "one_frame_contest_test",
]
PROOFS = ["A_STRUCTURE", "B_HABITAR", "C_ANTI_POSTAL", "D_LIGHT_MATERIAL", "E_ONE_FRAME_STORY"]

def empty_checklist(names):
    return {name: {"status": "NOT_STARTED", "source_ids": []} for name in names}

def record(candidate):
    return {
        "canonical_id": candidate["canonical_id"], "name": candidate["name"],
        "district": candidate["district"], "verification_status": "NOT_STARTED",
        "passes": empty_checklist(PASSES), "proofs": empty_checklist(PROOFS),
        "visual_reference_families": [], "composition_questions": [],
        "current_source_ids": [], "contradictions": [],
        "verification_complete": False, "ranking_eligible": False, "route_eligible": False,
    }

def apply_evidence(records):
    if not EVIDENCE.exists():
        return
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    by_id = {item["canonical_id"]: item for item in records}
    for update in evidence["candidate_updates"]:
        target = by_id[update["canonical_id"]]
        target["verification_status"] = "IN_PROGRESS"
        target["current_source_ids"] = update["current_source_ids"]
        target["contradictions"] = update.get("contradictions", [])
        for pass_name, pass_update in update["passes"].items():
            target["passes"][pass_name] = pass_update

def main():
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    records = [record(candidate) for candidate in candidates]
    apply_evidence(records)
    payload = {
        "ledger_id": "EQUAL-DEPTH-81-2026-08-28", "candidate_count": len(candidates),
        "completion_rule": "All ten passes, five proofs, current sources, visual families and composition questions must be VERIFIED or CORROBORATED.",
        "records": records,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(payload["records"]), "complete": 0}))

if __name__ == "__main__":
    main()
