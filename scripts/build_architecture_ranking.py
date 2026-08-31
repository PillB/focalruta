#!/usr/bin/env python3
"""Build the transparent, deterministic architecture scene ranking."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "architectural_photography/ranking/scoring_model.json"
CANONICAL_PATH = ROOT / "architectural_photography/ranking/canonical_candidates.json"
VERIFICATION_PATH = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
LEGACY_PATH = ROOT / "architectural_photography/FocalRuta_Bonilla_Master82_Ranking.json"
MATRIX_PATH = ROOT / "architectural_photography/ranking/performance_matrix.json"
RUNS_DIR = ROOT / "architectural_photography/ranking/ranking_runs"
HISTORY_PATH = ROOT / "architectural_photography/ranking/ranking_history.json"
PUBLIC_PATH = ROOT / "data/architecture/ranking.json"
ROUTES_PATH = ROOT / "data/architecture/routes.json"
NEW_ASSESSMENTS_PATH = ROOT / "architectural_photography/ranking/new_candidate_assessments.json"
RUN_ID = "2026-08-31-r4-v7"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_immutable_json(path: Path, value) -> None:
    serialized = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != serialized:
        raise RuntimeError(f"immutable ranking run changed: {path.stem}")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized, encoding="utf-8")


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def status_score(status: str) -> float:
    return {"VERIFIED": 100.0, "CORROBORATED": 78.0}[status]


def validate_model(model: dict) -> None:
    if set(model["scenarios"]) != {"R0", "R1", "R2", "R3"}:
        raise ValueError("ranking model must define exactly R0, R1, R2 and R3")
    for key, scenario in model["scenarios"].items():
        if abs(sum(scenario["weights"].values()) - 1.0) >= 1e-9:
            raise ValueError(f"{key} weights must sum to one")
    if "fame" in model["criteria"]:
        raise ValueError("fame cannot be a ranking criterion")


def legacy_by_canonical(candidates: list[dict], legacy: list[dict]) -> dict[str, dict]:
    by_id = {item["id"]: item for item in legacy}
    result = {}
    for candidate in candidates:
        rows = [by_id[item] for item in candidate["historical_ids"] if item in by_id]
        result[candidate["canonical_id"]] = {
            key: mean([float(row[key]) for row in rows])
            for key in ("brief", "story", "novelty", "saturation", "lived", "formal", "feasibility", "judge", "ephemeris", "travel")
        }
    return result


def access_score(item: dict, base: dict) -> float:
    text = " ".join(item["contradictions"] + [item["passes"]["moment_logistics_ethics"]["answer"]]).lower()
    score = base["feasibility"] * 10 - base["travel"] * 2
    if any(token in text for token in ("closed", "cerrad", "closure", "permission", "authorization", "autorización")):
        score -= 18
    if any(token in text for token in ("same-day", "verify", "verif", "unresolved", "stale")):
        score -= 10
    if item["canonical_id"] == "cantagallo-comunidad-shipibo-konibo":
        return 0.0
    return max(0.0, min(100.0, score))


def matrix_row(candidate: dict, verified: dict, base: dict) -> dict:
    passes = verified["passes"]
    evidence = mean([status_score(check["status"]) for check in passes.values()])
    criteria = {
        "creative_aesthetic_proxy": mean([base["story"], base["formal"], base["novelty"]]) * 10,
        "theme_coherence_proxy": mean([base["brief"], base["story"], base["lived"], base["ephemeris"]]) * 10,
        "architecture_causality": status_score(passes["architectural_causality"]["status"]),
        "first_read_clarity": base["formal"] * 10,
        "anti_postal_originality": mean([base["novelty"], 10 - base["saturation"]]) * 10,
        "inhabitation_strength": base["lived"] * 10,
        "temporal_transformation": base["ephemeris"] * 10,
        "light_material_geometry": mean([base["formal"] * 10, status_score(passes["light_material_geometry"]["status"])]),
        "decisive_moment": mean([base["story"], base["lived"]]) * 10,
        "technical_feasibility": base["feasibility"] * 10,
        "access_permission": access_score(verified, base),
        "evidence_confidence": evidence,
        "juror_public_work_intersection": base["judge"] * 10,
    }
    return {
        "canonical_id": candidate["canonical_id"], "name": candidate["name"],
        "district": candidate["district"],
        "criteria": {key: round(value, 3) for key, value in criteria.items()},
        "evidence_source_ids": verified["current_source_ids"],
        "assessment_basis": "CANONICALIZED_MASTER82_ATTRIBUTES_PLUS_2026_EQUAL_DEPTH_EVIDENCE",
        "contradiction_count": len(verified["contradictions"]),
    }


def assessed_matrix_row(candidate: dict, verified: dict, assessment: dict) -> dict:
    return {
        "canonical_id": candidate["canonical_id"], "name": candidate["name"],
        "district": candidate["district"], "criteria": assessment["criteria"],
        "evidence_source_ids": verified["current_source_ids"],
        "assessment_basis": "2026_STYLE_DOSSIER_EXPLICIT_EVIDENCE_ASSESSMENT",
        "contradiction_count": len(verified["contradictions"]),
    }


def weighted_score(criteria: dict, weights: dict) -> float:
    return sum(criteria[key] * weight for key, weight in weights.items())


def ranked(rows: list[dict], weights: dict) -> list[dict]:
    scored = [(weighted_score(row["criteria"], weights), row["canonical_id"]) for row in rows]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [{"rank": index, "canonical_id": canonical_id, "score": round(score, 3)} for index, (score, canonical_id) in enumerate(scored, 1)]


def perturb(weights: dict, rng: random.Random, low: float, high: float) -> dict:
    values = {key: value * rng.uniform(low, high) for key, value in weights.items()}
    total = sum(values.values())
    return {key: value / total for key, value in values.items()}


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def pareto_ids(rows: list[dict], objectives: list[str]) -> set[str]:
    front = set()
    for row in rows:
        dominated = any(
            all(other["criteria"][key] >= row["criteria"][key] for key in objectives)
            and any(other["criteria"][key] > row["criteria"][key] for key in objectives)
            for other in rows if other is not row
        )
        if not dominated:
            front.add(row["canonical_id"])
    return front


def build_run(model: dict, rows: list[dict], verification: dict, route_ids: set[str] | None = None) -> dict:
    route_ids = route_ids or set()
    scenario_rankings = {key: ranked(rows, value["weights"]) for key, value in model["scenarios"].items()}
    rank_samples = {row["canonical_id"]: [] for row in rows}
    rng = random.Random(model["sensitivity"]["seed"])
    for scenario in model["scenarios"].values():
        for _ in range(model["sensitivity"]["samples"]):
            weights = perturb(scenario["weights"], rng, model["sensitivity"]["weight_multiplier_min"], model["sensitivity"]["weight_multiplier_max"])
            for item in ranked(rows, weights):
                rank_samples[item["canonical_id"]].append(item["rank"])
    field = ranked(rows, model["field_weights"])
    field_ranks = {item["canonical_id"]: item["rank"] for item in field}
    scenario_ranks = {
        key: {item["canonical_id"]: item["rank"] for item in ranking}
        for key, ranking in scenario_rankings.items()
    }
    front = pareto_ids(rows, model["pareto_objectives"])
    verified_by_id = {item["canonical_id"]: item for item in verification["records"]}
    results = []
    for row in rows:
        canonical_id = row["canonical_id"]
        samples = rank_samples[canonical_id]
        distribution = {"min": min(samples), "p10": percentile(samples, 0.10), "p50": percentile(samples, 0.50), "p90": percentile(samples, 0.90), "max": max(samples)}
        results.append({
            "canonical_id": canonical_id,
            "name": row["name"],
            "district": row["district"],
            "scenario_ranks": {key: ranks[canonical_id] for key, ranks in scenario_ranks.items()},
            "scenario_scores": {key: next(item["score"] for item in ranking if item["canonical_id"] == canonical_id) for key, ranking in scenario_rankings.items()},
            "rank_distribution": distribution,
            "rank_spread": distribution["max"] - distribution["min"],
            "pareto_front": canonical_id in front,
            "evidence_confidence": round(row["criteria"]["evidence_confidence"] / 100, 3),
            "field_rank": field_ranks[canonical_id],
            "ranking_eligible": verified_by_id[canonical_id]["verification_complete"],
            "route_eligible": canonical_id in route_ids,
            "why_survives": verified_by_id[canonical_id]["passes"]["one_frame_contest_test"]["answer"],
            "strongest_counterargument": verified_by_id[canonical_id]["contradictions"][0] if verified_by_id[canonical_id]["contradictions"] else "Field evidence may overturn the desk hypothesis.",
            "field_failure": verified_by_id[canonical_id]["proofs"]["E_ONE_FRAME_STORY"]["kill_trigger"],
            "required_scene": verified_by_id[canonical_id]["proofs"]["E_ONE_FRAME_STORY"]["expected_action"],
            "exact_view": verified_by_id[canonical_id]["proofs"]["E_ONE_FRAME_STORY"]["position"],
            "exact_light": verified_by_id[canonical_id]["proofs"]["E_ONE_FRAME_STORY"]["light"],
            "fallback": verified_by_id[canonical_id]["proofs"]["E_ONE_FRAME_STORY"]["fallback"],
            "evidence_that_moves_rank": "Field proof that confirms or contradicts the E one-frame story, access and decisive-moment assumptions.",
        })
    results.sort(key=lambda item: (item["rank_distribution"]["p50"], max(item["scenario_ranks"].values()), mean(list(item["scenario_ranks"].values())), item["canonical_id"]))
    for index, item in enumerate(results, 1):
        item["robust_rank"] = index
    top_five_field = sorted(results, key=lambda item: item["field_rank"])[:5]
    return {
        "run_id": RUN_ID,
        "model_version": model["model_version"],
        "generated_at": "2026-08-30T12:00:00-05:00",
        "candidate_count": len(rows),
        "seed": model["sensitivity"]["seed"],
        "samples_per_scenario": model["sensitivity"]["samples"],
        "official_proxy_label": model["official_proxy_label"],
        "calibrated_winning_probability": False,
        "scenario_rankings": scenario_rankings,
        "field_ranking": field,
        "top_15_robust_ids": [item["canonical_id"] for item in results[:15]],
        "top_5_field": [
            {
                "canonical_id": item["canonical_id"],
                "name": item["name"],
                "district": item["district"],
                "field_rank": item["field_rank"],
                "robust_rank": item["robust_rank"],
                "why_go_now": f"Combina valor de campo #{item['field_rank']} con potencial robusto #{item['robust_rank']} bajo la evidencia actual.",
                "field_confidence": item["evidence_confidence"],
                "route_fit": "VERIFIED_WALKING_LAYER" if item["route_eligible"] else "NO_VERIFIED_WALKING_LAYER",
                "required_scene": item["required_scene"],
                "fallback": item["fallback"],
            }
            for item in top_five_field
        ],
        "results": results,
    }


def public_run(run: dict) -> dict:
    return {key: run[key] for key in ("run_id", "model_version", "candidate_count", "official_proxy_label", "calibrated_winning_probability", "scenario_rankings", "top_15_robust_ids", "top_5_field", "results")}


def update_history(run: dict, run_path: Path) -> None:
    digest = hashlib.sha256(run_path.read_bytes()).hexdigest()
    history = read_json(HISTORY_PATH) if HISTORY_PATH.exists() else {"runs": []}
    entry = {"run_id": run["run_id"], "model_version": run["model_version"], "file": run_path.name, "sha256": digest}
    existing = {item["run_id"]: item for item in history["runs"]}
    if run["run_id"] in existing and existing[run["run_id"]] != entry:
        raise RuntimeError(f"immutable ranking run changed: {run['run_id']}")
    existing[run["run_id"]] = entry
    history["runs"] = [existing[key] for key in sorted(existing)]
    write_json(HISTORY_PATH, history)


def main() -> None:
    model = read_json(MODEL_PATH)
    validate_model(model)
    candidates = read_json(CANONICAL_PATH)
    verification = read_json(VERIFICATION_PATH)
    historical = [item for item in candidates if item["historical_ids"]]
    legacy = legacy_by_canonical(historical, read_json(LEGACY_PATH))
    assessments = {item["canonical_id"]: item for item in read_json(NEW_ASSESSMENTS_PATH)["records"]}
    verified = {item["canonical_id"]: item for item in verification["records"]}
    rows = [
        matrix_row(candidate, verified[candidate["canonical_id"]], legacy[candidate["canonical_id"]])
        if candidate["canonical_id"] in legacy else
        assessed_matrix_row(candidate, verified[candidate["canonical_id"]], assessments[candidate["canonical_id"]])
        for candidate in candidates
    ]
    matrix = {"model_version": model["model_version"], "candidate_count": len(rows), "rows": rows}
    write_json(MATRIX_PATH, matrix)
    routes = read_json(ROUTES_PATH)
    route_ids = {stop["canonical_id"] for layer in routes["district_layers"] for stop in layer["stops"]}
    run = build_run(model, rows, verification, route_ids)
    run_path = RUNS_DIR / f"{RUN_ID}.json"
    write_immutable_json(run_path, run)
    update_history(run, run_path)
    write_json(PUBLIC_PATH, public_run(run))
    print(json.dumps({"run_id": RUN_ID, "candidates": len(rows), "pareto": sum(item["pareto_front"] for item in run["results"])}))


if __name__ == "__main__":
    main()
