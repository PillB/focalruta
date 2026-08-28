#!/usr/bin/env python3
"""Canonicalize historical architecture candidates without importing old scores."""

from __future__ import annotations

import re
import unicodedata
import json
from collections import defaultdict
from pathlib import Path

try:
    from scripts.architecture_geography import classify_candidate, normalize_district
except ModuleNotFoundError:  # Direct `python3 scripts/...` execution.
    from architecture_geography import classify_candidate, normalize_district


HISTORICAL_SCORE_FIELDS = {
    "brief", "story", "novelty", "saturation", "lived", "formal", "feasibility",
    "judge", "ephemeris", "travel", "R0", "R1", "R2", "R3", "R0Rank",
    "R1Rank", "R2Rank", "R3Rank", "rankSpread", "worstRank", "rankMean",
    "robustIndex", "masterRank", "fieldIndex", "fieldRank", "oldRobustRank",
}
DISTRICT_ALIASES = {
    "cercado de lima": "lima",
    "cercado": "lima",
    "barrios altos": "lima",
    "centro historico": "lima",
    "miraflores–barranco": "miraflores",
    "miraflores-barranco": "miraflores",
    "lima media": "lima",
}
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "architectural_photography" / "FocalRuta_Bonilla_Master82_Ranking.json"
RANKING_ROOT = ROOT / "architectural_photography" / "ranking"


def normalize_identity(value: str) -> str:
    text = unicodedata.normalize("NFKD", value)
    text = "".join(char for char in text if not unicodedata.combining(char)).casefold()
    text = re.sub(r"\bn\s*[.º°o]*\s*(?=\d)", "", text)
    text = re.sub(r"\bno\s*[.]?\s*(?=\d)", "", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def canonical_district(value: str) -> str:
    district = normalize_district(value)
    return DISTRICT_ALIASES.get(district, district)


def canonical_id(name: str) -> str:
    return normalize_identity(name).replace(" ", "-")


def public_candidate(record: dict) -> dict:
    blocked = HISTORICAL_SCORE_FIELDS | {"id", "name", "district"}
    candidate = {key: value for key, value in record.items() if key not in blocked}
    candidate.update({
        "canonical_id": canonical_id(record["name"]),
        "name": record["name"],
        "district": "Lima" if canonical_district(record["district"]) == "lima" else record["district"],
        "evidence_status": "HISTORICAL_ONLY",
        "ranking_eligible": False,
        "requires_current_verification": True,
    })
    return candidate


def canonicalize_records(records: list[dict]) -> dict:
    groups = defaultdict(list)
    quarantined = []
    for record in records:
        status = classify_candidate(canonical_district(record.get("district", "")))
        if not status.startswith("ELIGIBLE"):
            quarantined.append({"historical_id": record.get("id"), "reason": status})
            continue
        groups[(normalize_identity(record["name"]), canonical_district(record["district"]))].append(record)

    candidates, merges = [], []
    for grouped_records in groups.values():
        representative = max(grouped_records, key=lambda item: len(item.keys() - HISTORICAL_SCORE_FIELDS))
        candidate = public_candidate(representative)
        candidate["historical_ids"] = sorted(item["id"] for item in grouped_records)
        candidates.append(candidate)
        if len(grouped_records) > 1:
            merges.append({
                "canonical_id": candidate["canonical_id"],
                "historical_ids": candidate["historical_ids"],
                "reason": "SEMANTIC_IDENTITY_MATCH",
                "count_effect": 1 - len(grouped_records),
            })
    return {"candidates": candidates, "merges": merges, "quarantined": quarantined}


def write_master82_derivatives(input_path: Path = DEFAULT_INPUT) -> dict:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    result = canonicalize_records(records)
    historical_dir = RANKING_ROOT / "historical"
    historical_dir.mkdir(parents=True, exist_ok=True)
    sanitized_history = [
        {"historical_id": item.get("id"), "name": item["name"], "district": item["district"], "source_run": "Master82"}
        for item in records
    ]
    outputs = {
        historical_dir / "master82_sanitized.json": sanitized_history,
        RANKING_ROOT / "canonical_candidates.json": result["candidates"],
        RANKING_ROOT / "candidate_aliases.json": result["merges"],
        RANKING_ROOT / "reconciliation_report.json": {
            "source_run": "Master82",
            "historical_count": len(records),
            "canonical_count": len(result["candidates"]),
            "merge_count": len(result["merges"]),
            "quarantined_count": len(result["quarantined"]),
            "merges": result["merges"],
            "quarantined": result["quarantined"],
        },
    }
    for path, payload in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs[RANKING_ROOT / "reconciliation_report.json"]


if __name__ == "__main__":
    print(json.dumps(write_master82_derivatives(), ensure_ascii=False, indent=2))
