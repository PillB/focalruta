import json
from pathlib import Path

from scripts.canonicalize_architecture_candidates import (
    HISTORICAL_SCORE_FIELDS,
    canonicalize_runs,
    canonicalize_records,
    normalize_identity,
)


ROOT = Path(__file__).resolve().parents[2]


def test_uv3_punctuation_and_abbreviation_variants_share_identity():
    variants = ["Unidad Vecinal Nº3", "Unidad Vecinal N.º 3", "Unidad Vecinal No. 3"]
    assert len({normalize_identity(value) for value in variants}) == 1


def test_semantic_duplicate_merges_history_without_leaking_old_rank():
    records = [
        {"id": "uv3-bonilla", "name": "Unidad Vecinal Nº3", "district": "Cercado de Lima", "masterRank": 10},
        {"id": "uv3", "name": "Unidad Vecinal N.º 3", "district": "Lima", "masterRank": 18},
    ]
    result = canonicalize_records(records)
    assert len(result["candidates"]) == 1
    candidate = result["candidates"][0]
    assert candidate["canonical_id"] == "unidad-vecinal-3"
    assert candidate["historical_ids"] == ["uv3", "uv3-bonilla"]
    assert "masterRank" not in candidate
    assert result["merges"][0]["count_effect"] == -1


def test_out_of_scope_historical_record_is_quarantined_not_ranked():
    result = canonicalize_records([
        {"id": "callao-test", "name": "Fortaleza del Real Felipe", "district": "Callao"},
    ])
    assert result["candidates"] == []
    assert result["quarantined"][0]["reason"] == "QUARANTINE_OUT_OF_SCOPE"


def test_historical_lima_neighborhood_and_cross_district_labels_are_resolved():
    records = [
        {"id": "heeren", "name": "Quinta Heeren", "district": "Barrios Altos"},
        {"id": "damero", "name": "Damero de Lima", "district": "Centro Histórico"},
        {"id": "armendariz", "name": "Puente de la Paz", "district": "Miraflores–Barranco"},
        {"id": "transect", "name": "Transecto compacto", "district": "Lima media"},
    ]
    result = canonicalize_records(records)
    assert len(result["candidates"]) == 4
    assert result["quarantined"] == []


def test_generated_historical_union_is_provenanced_and_score_isolated():
    candidates = json.loads(
        (ROOT / "architectural_photography" / "ranking" / "canonical_candidates.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (ROOT / "architectural_photography" / "ranking" / "reconciliation_report.json").read_text(encoding="utf-8")
    )
    assert report["source_runs"] == {"Master68": 68, "Master82": 82}
    assert report["canonical_count"] == 81
    assert report["run_deltas"]["Master68_to_Master82"] == {
        "retained": 68, "added": 13, "removed": 0,
    }
    assert len({item["canonical_id"] for item in candidates}) == 81
    assert all(item["evidence_status"] == "HISTORICAL_ONLY" for item in candidates)
    assert all(item["ranking_eligible"] is False for item in candidates)
    assert all(not (HISTORICAL_SCORE_FIELDS & item.keys()) for item in candidates)
    assert sum("Master68" in item["source_runs"] for item in candidates) == 68
    assert sum("Master82" in item["source_runs"] for item in candidates) == 81


def test_multiple_runs_preserve_run_provenance_without_inflating_identity():
    shared = {"id": "shared", "name": "Parque de prueba", "district": "Lince"}
    newer = {"id": "new", "name": "Edificio nuevo", "district": "Surquillo"}
    result = canonicalize_runs({"Master68": [shared], "Master82": [shared, newer]})
    assert len(result["candidates"]) == 2
    park = next(item for item in result["candidates"] if item["canonical_id"] == "parque-de-prueba")
    assert park["source_runs"] == ["Master68", "Master82"]
    assert park["historical_refs"] == [
        {"run_id": "Master68", "historical_id": "shared"},
        {"run_id": "Master82", "historical_id": "shared"},
    ]
    assert result["run_deltas"]["Master68_to_Master82"] == {
        "retained": 1, "added": 1, "removed": 0,
    }
