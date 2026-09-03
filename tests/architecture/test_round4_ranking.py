import json
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "architectural_photography/ranking/scoring_model.json"
MATRIX = ROOT / "architectural_photography/ranking/performance_matrix.json"
HISTORY = ROOT / "architectural_photography/ranking/ranking_history.json"
RUNS = ROOT / "architectural_photography/ranking/ranking_runs"
PUBLIC = ROOT / "data/architecture/ranking.json"
PAGE = ROOT / "challenges/arquitectura-en-foco/index.html"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_model_is_internal_transparent_and_has_four_scenarios():
    model = load(MODEL)
    assert model["official_proxy_label"] == "INTERNAL_PROXY"
    assert model["calibrated_winning_probability"] is False
    assert model["method"] == "LINEAR_ADDITIVE_VALUE_MODEL_WITH_SENSITIVITY"
    assert set(model["scenarios"]) == {"R0", "R1", "R2", "R3"}
    assert all(abs(sum(item["weights"].values()) - 1) < 1e-9 for item in model["scenarios"].values())
    assert "fame" not in model["criteria"]
    assert "historical_rank" in model["prohibited_features"]
    assert model["sensitivity"]["seed"] == 20260830
    assert model["sensitivity"]["samples"] >= 1000
    assert abs(sum(model["field_weights"].values()) - 1) < 1e-9
    assert {"creative_aesthetic_proxy", "theme_coherence_proxy", "architecture_causality"}.issubset(model["field_weights"])


def test_performance_matrix_covers_all_scenes_without_historical_rank_leakage():
    matrix = load(MATRIX)
    rows = matrix["rows"]
    assert len(rows) == 87
    assert len({row["canonical_id"] for row in rows}) == 87
    prohibited = {"historical_rank", "masterRank", "R0Rank", "R1Rank", "R2Rank", "R3Rank", "robustIndex"}
    assert all(prohibited.isdisjoint(row) for row in rows)
    assert all(row["evidence_source_ids"] for row in rows)
    assert all(0 <= value <= 100 for row in rows for value in row["criteria"].values())


def test_latest_run_has_deterministic_sensitivity_pareto_and_separate_field_rank():
    history = load(HISTORY)
    latest = load(RUNS / history["runs"][-1]["file"])
    assert latest["candidate_count"] == 87
    assert latest["seed"] == 20260830
    assert set(latest["scenario_rankings"]) == {"R0", "R1", "R2", "R3"}
    assert all(len(ranking) == 87 for ranking in latest["scenario_rankings"].values())
    assert len(latest["results"]) == 87
    for item in latest["results"]:
        distribution = item["rank_distribution"]
        assert distribution["min"] <= distribution["p10"] <= distribution["p50"] <= distribution["p90"] <= distribution["max"]
        assert item["rank_spread"] == distribution["max"] - distribution["min"]
        assert isinstance(item["pareto_front"], bool)
        assert 0 <= item["evidence_confidence"] <= 1
        assert item["field_rank"] >= 1
        assert isinstance(item["route_eligible"], bool)
    assert sorted(item["field_rank"] for item in latest["results"]) == list(range(1, 88))


def test_public_ranking_supports_top_n_or_all_and_avoids_probability_language():
    public = load(PUBLIC)
    assert public["candidate_count"] == 87
    assert len(public["results"]) == 87
    assert len(public["top_15_robust_ids"]) == 15
    assert len(public["top_5_field"]) == 5
    assert all(item["route_fit"] in {"VERIFIED_WALKING_LAYER", "NO_VERIFIED_WALKING_LAYER"} for item in public["top_5_field"])
    assert all(item["fallback"] for item in public["top_5_field"])
    assert public["official_proxy_label"] == "INTERNAL_PROXY"
    page = PAGE.read_text(encoding="utf-8")
    assert 'id="ranking-scenario"' in page
    assert 'id="ranking-limit"' in page
    assert 'value="all"' in page
    assert "applyRankingView" in page
    assert "Pareto" in page


def test_ranking_history_is_append_only_and_points_to_immutable_runs():
    history = load(HISTORY)
    run_ids = [item["run_id"] for item in history["runs"]]
    assert run_ids == sorted(run_ids)
    assert len(run_ids) == len(set(run_ids))
    for entry in history["runs"]:
        run = load(RUNS / entry["file"])
        assert run["run_id"] == entry["run_id"]
        assert run["model_version"] == entry["model_version"]


def test_ranking_is_precached_and_route_status_comes_from_verified_layers():
    build = (ROOT / "scripts/build_dual_release.py").read_text(encoding="utf-8")
    assert "./data/architecture/ranking.json" in build
    public = load(PUBLIC)
    assert all(item["ranking_eligible"] for item in public["results"])
    routes = load(ROOT / "data/architecture/routes.json")
    route_ids = {stop["canonical_id"] for layer in routes["district_layers"] for stop in layer["stops"]}
    assert {item["canonical_id"] for item in public["results"] if item["route_eligible"]} == route_ids


def test_generator_is_repeatable_and_does_not_read_historical_rank_fields():
    history = load(HISTORY)
    latest_path = RUNS / history["runs"][-1]["file"]
    before = hashlib.sha256(latest_path.read_bytes()).hexdigest()
    subprocess.run([sys.executable, "-B", "scripts/build_architecture_ranking.py"], cwd=ROOT, check=True, capture_output=True, text=True)
    after = hashlib.sha256(latest_path.read_bytes()).hexdigest()
    assert before == after == history["runs"][-1]["sha256"]
    source = (ROOT / "scripts/build_architecture_ranking.py").read_text(encoding="utf-8")
    assert "FocalRuta_Bonilla_Master82_Ranking.json" not in source
    for field in ("masterRank", "R0Rank", "R1Rank", "R2Rank", "R3Rank", "robustIndex"):
        assert f'["{field}"]' not in source


def test_public_ranking_build_has_all_sanitized_declared_inputs():
    assessments = load(ROOT / "architectural_photography/ranking/legacy_attribute_assessments.json")
    assert assessments["privacy"] == "GENERATED_PUBLIC_NO_RAW_CONVERSATION_NO_HISTORICAL_RANKS"
    assert len(assessments["records"]) == 81
    assert all(set(item) == {"canonical_id", "attributes"} for item in assessments["records"])


def test_immutable_writer_rejects_changed_content(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_architecture_ranking import write_immutable_json

    target = tmp_path / "run.json"
    write_immutable_json(target, {"run_id": "stable"})
    write_immutable_json(target, {"run_id": "stable"})
    with pytest.raises(RuntimeError, match="immutable ranking run changed"):
        write_immutable_json(target, {"run_id": "changed"})
