import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = ROOT / "architectural_photography" / "research" / "bonilla" / "snapshots"


def load_snapshots():
    return [
        json.loads((SNAPSHOT_DIR / f"W{number:02d}_snapshot.json").read_text(encoding="utf-8"))
        for number in range(1, 21)
    ]


def test_all_twenty_bonilla_sources_have_immutable_snapshot_schema():
    snapshots = load_snapshots()
    required = {
        "source_id", "title", "url", "status", "lesson", "claim_ids",
        "candidate_added", "candidate_merged", "candidate_removed_or_quarantined",
        "canonical_count_after", "ranking_model_version", "ranking_run_id",
        "top5", "delta_vs_previous", "confidence", "open_questions",
        "retrieved_at", "source_access", "evidentiary_role", "expert_rejection",
    }
    assert [item["source_id"] for item in snapshots] == [f"W{number:02d}" for number in range(1, 21)]
    assert all(required <= item.keys() for item in snapshots)
    assert all(item["status"] in {"VERIFIED", "REFERENCE", "PARTIAL", "BROKEN"} for item in snapshots)
    assert all(item["ranking_model_version"] is None for item in snapshots)
    assert all(item["ranking_run_id"] is None for item in snapshots)
    assert all(item["top5"] == [] for item in snapshots)


def test_bonilla_sources_cannot_promote_historical_candidates_or_smuggle_callao():
    snapshots = load_snapshots()
    assert all(item["candidate_added"] == [] for item in snapshots)
    assert all(item["canonical_count_after"] == 81 for item in snapshots)
    assert all(item["evidentiary_role"] != "RANKING_AUTHORITY" for item in snapshots)
    assert "Callao" in snapshots[0]["expert_rejection"]
    assert snapshots[11]["candidate_removed_or_quarantined"] == [
        {
            "candidate": "Cantagallo · comunidad Shipibo-Konibo",
            "reason": "ETHICS_CONSENT_COLLABORATION_GATE",
        }
    ]
    assert snapshots[11]["geographic_scope"] == "IN_SCOPE_RIMAC_DISTRICT"


def test_cantagallo_and_start_from_one_hard_gates_are_explicit():
    w12 = load_snapshots()[11]
    assert w12["ethical_gate"] == {
        "consent_or_collaboration_required": True,
        "hidden_telephoto_workaround_prohibited": True,
        "exotic_texture_extraction_prohibited": True,
        "vulnerability_as_opportunity_prohibited": True,
    }
    w18 = load_snapshots()[17]
    assert w18["field_test"] == (
        "What existed before the intervention, and where does that prior condition still control the image?"
    )


def test_source_access_does_not_claim_current_scene_truth():
    snapshots = load_snapshots()
    assert all(item["source_access"] in {"DIRECT_CURRENT", "INDEX_ONLY", "UNRESOLVED"} for item in snapshots)
    assert all("current scene" in item["expert_rejection"].lower() for item in snapshots)
    assert all(item["confidence"] <= 0.9 for item in snapshots)
