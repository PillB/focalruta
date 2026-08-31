import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BONILLA_ROOT = ROOT / "architectural_photography" / "research" / "bonilla"
GLOBAL_CLAIMS = ROOT / "architectural_photography" / "state" / "CLAIM_GRAPH.jsonl"


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_twenty_bonilla_source_records_resolve_with_independence_clusters():
    sources = json.loads((BONILLA_ROOT / "source_records.json").read_text(encoding="utf-8"))
    assert len(sources) == 20
    assert [item["source_id"] for item in sources] == [f"SRC-BONILLA-W{number:02d}" for number in range(1, 21)]
    assert all(item["type"] in {"PRIMARY", "ACADEMIC", "PROFESSIONAL", "JOURNALISM"} for item in sources)
    assert all(item["privacy_class"] in {"PUBLIC_PRIMARY", "PUBLIC_SECONDARY"} for item in sources)
    assert all(item["status"] in {"ACTIVE", "HISTORICAL", "BROKEN"} for item in sources)
    assert all(item["independence_cluster"] for item in sources)


def test_bonilla_claims_are_framework_only_and_resolve_sources():
    sources = json.loads((BONILLA_ROOT / "source_records.json").read_text(encoding="utf-8"))
    source_ids = {item["source_id"] for item in sources}
    claims = read_jsonl(BONILLA_ROOT / "claim_records.jsonl")
    assert len(claims) == 20
    assert all(set(item["source_ids"]) <= source_ids for item in claims)
    assert all(item["evidence_status"] in {"VERIFIED", "PARTIAL"} for item in claims)
    assert all(item["ranking_impacts"] == ["FRAMEWORK_ONLY_NO_SCORE_OR_PROMOTION"] for item in claims)
    assert all(item["route_impacts"] == ["CURRENT_PLACE_AND_ACCESS_SOURCE_REQUIRED"] for item in claims)
    assert all(item["confidence"] <= 0.9 for item in claims)


def test_global_claim_graph_contains_each_bonilla_claim_once():
    claims = read_jsonl(GLOBAL_CLAIMS)
    ids = [item["claim_id"] for item in claims]
    expected = [f"CLM-BONILLA-{number:02d}-FRAMEWORK" for number in range(1, 21)]
    assert all(ids.count(claim_id) == 1 for claim_id in expected)


def test_cantagallo_claim_preserves_geography_and_ethics_without_route_promotion():
    claims = {item["claim_id"]: item for item in read_jsonl(BONILLA_ROOT / "claim_records.jsonl")}
    claim = claims["CLM-BONILLA-12-FRAMEWORK"]
    assert "Rímac" in claim["claim"]
    assert "consent" in claim["claim"].lower()
    assert claim["route_impacts"] == ["CURRENT_PLACE_AND_ACCESS_SOURCE_REQUIRED"]
