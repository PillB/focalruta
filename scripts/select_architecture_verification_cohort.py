#!/usr/bin/env python3
"""Select an unordered, evidence-gated research cohort without historical rank."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCATION_ROOT = ROOT / "architectural_photography" / "research" / "locations"
POOL_PATH = LOCATION_ROOT / "verification_pool.json"
OUTPUT_PATH = LOCATION_ROOT / "verification_cohort.json"
CANONICAL_PATH = ROOT / "architectural_photography" / "ranking" / "canonical_candidates.json"
MAX_COHORT = 6
BLOCKED_FIELDS = {"masterRank", "robustIndex", "fieldRank", "R0", "R1", "R2", "R3"}


def canonical_ids():
    records = json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))
    return {item["canonical_id"] for item in records}


def eligible(item, known_ids):
    return all((
        item.get("identity_resolved") is True,
        item.get("geography_eligible") is True,
        item.get("canonical_id") in known_ids,
        bool(item.get("current_primary_sources")),
        bool(item.get("source_last_verified_at")),
        item.get("access_status") != "CLOSED",
        bool(item.get("primary_scene_mechanism")),
    ))


def public_record(item):
    record = {key: value for key, value in item.items() if key not in BLOCKED_FIELDS}
    record.update({
        "evidence_status": "RESEARCH_QUEUE",
        "ranking_eligible": False,
        "route_eligible": False,
        "requires_ten_pass_dossier": True,
        "requires_visual_forensics": True,
    })
    return record


def select_cohort(pool):
    known_ids = canonical_ids()
    eligible_records = [item for item in pool if eligible(item, known_ids)]
    by_mechanism = {}
    for item in sorted(eligible_records, key=lambda record: record["canonical_id"]):
        by_mechanism.setdefault(item["primary_scene_mechanism"], item)
    if len(by_mechanism) > MAX_COHORT:
        raise ValueError("More than six distinct mechanisms qualify; record an explicit displacement decision")
    return [public_record(item) for item in by_mechanism.values()]


def main():
    pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    candidates = select_cohort(pool)
    output = {
        "cohort_id": "VERIFY-2026-08-27-A",
        "selection_type": "UNORDERED_RESEARCH_QUEUE",
        "selection_rule": "Resolved canonical identity + eligible Lima geography + current primary source + non-closed access + unique scene mechanism.",
        "historical_rank_fields_prohibited": sorted(BLOCKED_FIELDS),
        "ranking_model_version": None,
        "ranking_run_id": None,
        "route_run_id": None,
        "candidates": candidates,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cohort_id": output["cohort_id"], "count": len(candidates), "ranked": False}))


if __name__ == "__main__":
    main()
