#!/usr/bin/env python3
"""Turn the supplied Bonilla ledger into fail-closed, source-level snapshots."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_LEDGER = ROOT / "architectural_photography" / "FocalRuta_Bonilla_Source_Snapshots.json"
OUTPUT_DIR = ROOT / "architectural_photography" / "research" / "bonilla" / "snapshots"
RETRIEVED_AT = "2026-08-27T17:30:00-05:00"
CANONICAL_COUNT = 81

DIRECT_CURRENT = {
    "W01", "W02", "W04", "W06", "W07", "W08", "W09", "W10", "W11",
    "W13", "W14", "W17", "W18", "W19", "W20",
}
INDEX_ONLY = {"W03", "W12", "W15"}


def source_access(source_id):
    if source_id in DIRECT_CURRENT:
        return "DIRECT_CURRENT"
    if source_id in INDEX_ONLY:
        return "INDEX_ONLY"
    return "UNRESOLVED"


def source_status(record, access):
    if access == "DIRECT_CURRENT":
        return "VERIFIED"
    if access == "INDEX_ONLY":
        return "REFERENCE"
    return "PARTIAL"


def expert_rejection(record):
    common = (
        "A published source can support a conceptual lens, but it cannot verify current scene conditions, "
        "access, safety, consent, light, activity, or one-frame strength."
    )
    if record["id"] == "W01":
        return f"{common} Its Callao coverage is outside the 43-district Lima boundary and cannot seed candidates."
    if record["id"] == "W12":
        return f"{common} Cantagallo cannot become an extractive photo opportunity without collaboration and consent."
    return common


def removed_or_quarantined(record):
    if record["id"] != "W12":
        return []
    return [{
        "candidate": "Cantagallo · comunidad Shipibo-Konibo",
        "reason": "ETHICS_CONSENT_COLLABORATION_GATE",
    }]


def source_role(record):
    if record["id"] in {"W01", "W02", "W03", "W04", "W05"}:
        return "CONTEXTUAL_FRAMEWORK"
    return "AUTHOR_ARGUMENT_FRAMEWORK"


def make_snapshot(record, previous_count):
    access = source_access(record["id"])
    snapshot = {
        "source_id": record["id"],
        "title": record["title"],
        "url": record["url"],
        "status": source_status(record, access),
        "lesson": record["lesson"],
        "claim_ids": [f"CLM-BONILLA-{record['id'][1:]}-FRAMEWORK"],
        "candidate_added": [],
        "candidate_merged": [],
        "candidate_removed_or_quarantined": removed_or_quarantined(record),
        "canonical_count_after": CANONICAL_COUNT,
        "ranking_model_version": None,
        "ranking_run_id": None,
        "top5": [],
        "delta_vs_previous": (
            "No canonical change; historical additions remain provenance-only."
            if previous_count == CANONICAL_COUNT
            else "Canonical baseline established without promotion."
        ),
        "confidence": 0.9 if access == "DIRECT_CURRENT" else 0.65 if access == "INDEX_ONLY" else 0.45,
        "open_questions": [
            "Which current, primary place source verifies any derived Lima scene?",
            "What field evidence would make the relationship legible in one frame?",
        ],
        "retrieved_at": RETRIEVED_AT,
        "source_access": access,
        "evidentiary_role": source_role(record),
        "expert_rejection": expert_rejection(record),
        "historical_candidate_suggestions": record.get("added", []),
        "historical_count_after": record.get("count"),
        "historical_top5": record.get("top5", []),
    }
    if record["id"] == "W12":
        snapshot["geographic_scope"] = "IN_SCOPE_RIMAC_DISTRICT"
        snapshot["ethical_gate"] = {
            "consent_or_collaboration_required": True,
            "hidden_telephoto_workaround_prohibited": True,
            "exotic_texture_extraction_prohibited": True,
            "vulnerability_as_opportunity_prohibited": True,
        }
    if record["id"] == "W18":
        snapshot["field_test"] = (
            "What existed before the intervention, and where does that prior condition still control the image?"
        )
    return snapshot


def main():
    records = json.loads(SOURCE_LEDGER.read_text(encoding="utf-8"))
    expected_ids = [f"W{number:02d}" for number in range(1, 21)]
    actual_ids = [record["id"] for record in records]
    if actual_ids != expected_ids:
        raise ValueError(f"Bonilla source sequence mismatch: {actual_ids}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    previous_count = None
    for record in records:
        snapshot = make_snapshot(record, previous_count)
        output = OUTPUT_DIR / f"{record['id']}_snapshot.json"
        output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        previous_count = CANONICAL_COUNT
    print(json.dumps({"snapshots": len(records), "canonical_promotions": 0, "canonical_count": CANONICAL_COUNT}))


if __name__ == "__main__":
    main()
