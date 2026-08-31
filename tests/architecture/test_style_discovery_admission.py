import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "utec-campus-barranco", "torre-interbank", "casa-fernandini-1913",
    "estacion-desamparados", "edificio-petroperu", "torre-begonias",
}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_six_desk_verified_scenes_enter_current_universe_without_rewriting_history():
    current = load("architectural_photography/ranking/canonical_candidates.json")
    historical = load("architectural_photography/ranking/reconciliation_report.json")
    assert len(current) == 87
    assert EXPECTED <= {item["canonical_id"] for item in current}
    assert historical["canonical_count"] == 81
    additions = [item for item in current if item["canonical_id"] in EXPECTED]
    assert all(item["source_runs"] == ["NEW_2026_STYLE_DISCOVERY"] for item in additions)
    assert all(item["historical_ids"] == [] for item in additions)


def test_new_scenes_use_explicit_evidence_assessments_not_legacy_scores():
    matrix = load("architectural_photography/ranking/performance_matrix.json")
    rows = {item["canonical_id"]: item for item in matrix["rows"]}
    assert matrix["candidate_count"] == 87
    assert EXPECTED <= rows.keys()
    for canonical_id in EXPECTED:
        assert rows[canonical_id]["assessment_basis"] == "2026_STYLE_DOSSIER_EXPLICIT_EVIDENCE_ASSESSMENT"
        assert rows[canonical_id]["evidence_source_ids"]


def test_new_scenes_are_ranked_and_only_evidence_routed():
    ranking = load("data/architecture/ranking.json")
    results = {item["canonical_id"]: item for item in ranking["results"]}
    assert ranking["candidate_count"] == 87
    assert EXPECTED <= results.keys()
    assert all(results[item]["ranking_eligible"] for item in EXPECTED)
    assert all(results[item]["route_eligible"] for item in EXPECTED)
