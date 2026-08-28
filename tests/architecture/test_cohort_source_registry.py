import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COHORT = ROOT / "architectural_photography/research/locations/verification_cohort.json"
SOURCES = ROOT / "data/architecture/sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_cohort_primary_url_has_one_public_source_record():
    cohort = load(COHORT)["candidates"]
    sources = load(SOURCES)
    urls = [source["url_or_path"] for source in sources]
    for candidate in cohort:
        for url in candidate["current_primary_sources"]:
            assert urls.count(url) == 1, (candidate["canonical_id"], url)


def test_location_source_ids_are_unique_active_and_public():
    location_sources = [source for source in load(SOURCES) if source["source_id"].startswith("SRC-LOC-")]
    ids = [source["source_id"] for source in location_sources]
    assert len(ids) == len(set(ids))
    assert len(location_sources) >= 9
    for source in location_sources:
        assert source["status"] == "ACTIVE"
        assert source["privacy_class"] == "PUBLIC_PRIMARY"
        assert source["retrieved_at"] == "2026-08-27"


def test_cohort_sources_do_not_promote_candidates_or_encode_historical_rank():
    prohibited = {"ranking_eligible", "route_eligible", "historical_rank", "masterRank", "robustIndex"}
    for source in load(SOURCES):
        if source["source_id"].startswith("SRC-LOC-"):
            assert prohibited.isdisjoint(source)
