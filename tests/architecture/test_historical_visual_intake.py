import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "architectural_photography/research/visual_forensics/historical_visual_intake.json"

def payload():
    return json.loads(LEDGER.read_text(encoding="utf-8"))

def test_historical_visual_intake_covers_canonical_universe_without_promotion():
    data = payload()
    assert data["candidate_count"] == 81
    assert len(data["records"]) == 81
    assert len({record["canonical_id"] for record in data["records"]}) == 81
    assert data["status"] == "DISCOVERY_ONLY_NOT_VERIFICATION_EVIDENCE"
    for reference in (item for record in data["records"] for item in record["references"]):
        assert reference["visual_evidence_eligible"] is False
        assert reference["rights_status"] == "UNRESOLVED"
        assert reference["provenance_status"] in {"PROXY_UNRESOLVED", "DIRECT_HOST_UNVERIFIED"}

def test_proxy_images_never_count_as_direct_source_evidence():
    references = [item for record in payload()["records"] for item in record["references"]]
    proxy = [item for item in references if item["host"] == "pplx-res.cloudinary.com"]
    assert proxy
    assert all(item["provenance_status"] == "PROXY_UNRESOLVED" for item in proxy)
    assert not any(item["visual_evidence_eligible"] for item in proxy)
