#!/usr/bin/env python3
"""Canonicalize historical architecture candidates without importing old scores."""

from __future__ import annotations

import re
import unicodedata
import json
import zipfile
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
PRIVATE_INPUT_ROOT = ROOT / "architectural_photography"
MASTER68_SUFFIX = "/artifacts/generated/FocalRuta_Expanded_Master_Ranking_68.json"
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
    blocked = HISTORICAL_SCORE_FIELDS | {"id", "name", "district", "_run_id"}
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


def record_key(record: dict) -> tuple[str, str]:
    return normalize_identity(record["name"]), canonical_district(record["district"])


def eligible_keys(records: list[dict]) -> set[tuple[str, str]]:
    return {
        record_key(record)
        for record in records
        if classify_candidate(canonical_district(record.get("district", ""))).startswith("ELIGIBLE")
    }


def canonicalize_runs(runs: dict[str, list[dict]]) -> dict:
    tagged = [dict(record, _run_id=run_id) for run_id, records in runs.items() for record in records]
    result = canonicalize_records(tagged)
    provenance = defaultdict(list)
    for record in tagged:
        provenance[record_key(record)].append({
            "run_id": record["_run_id"],
            "historical_id": record["id"],
        })
    for candidate in result["candidates"]:
        key = (normalize_identity(candidate["name"]), canonical_district(candidate["district"]))
        refs = sorted(provenance[key], key=lambda item: (item["run_id"], item["historical_id"]))
        candidate["historical_refs"] = refs
        candidate["historical_ids"] = sorted({item["historical_id"] for item in refs})
        candidate["source_runs"] = sorted({item["run_id"] for item in refs})
    same_run_groups = defaultdict(list)
    for record in tagged:
        same_run_groups[(record["_run_id"], record_key(record))].append(record)
    result["merges"] = [
        {
            "run_id": run_id,
            "canonical_id": canonical_id(group[0]["name"]),
            "historical_ids": sorted({item["id"] for item in group}),
            "reason": "SEMANTIC_IDENTITY_MATCH",
            "count_effect": 1 - len(group),
        }
        for (run_id, _key), group in same_run_groups.items()
        if len({item["id"] for item in group}) > 1
    ]
    run_deltas = {}
    run_items = list(runs.items())
    for (old_id, old_records), (new_id, new_records) in zip(run_items, run_items[1:]):
        old_keys, new_keys = eligible_keys(old_records), eligible_keys(new_records)
        run_deltas[f"{old_id}_to_{new_id}"] = {
            "retained": len(old_keys & new_keys),
            "added": len(new_keys - old_keys),
            "removed": len(old_keys - new_keys),
        }
    result["run_deltas"] = run_deltas
    return result


def load_master68() -> list[dict]:
    matches = []
    for archive_path in PRIVATE_INPUT_ROOT.glob("*.zip"):
        with zipfile.ZipFile(archive_path) as archive:
            matches.extend(
                (archive_path, member)
                for member in archive.namelist()
                if member.endswith(MASTER68_SUFFIX)
            )
    if len(matches) != 1:
        raise ValueError(f"Expected one private Master68 artifact, found {len(matches)}")
    archive_path, member = matches[0]
    with zipfile.ZipFile(archive_path) as archive:
        return json.loads(archive.read(member))


def write_historical_derivatives(input_path: Path = DEFAULT_INPUT) -> dict:
    runs = {
        "Master68": load_master68(),
        "Master82": json.loads(input_path.read_text(encoding="utf-8")),
    }
    result = canonicalize_runs(runs)
    historical_dir = RANKING_ROOT / "historical"
    historical_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        RANKING_ROOT / "canonical_candidates.json": result["candidates"],
        RANKING_ROOT / "candidate_aliases.json": result["merges"],
        RANKING_ROOT / "reconciliation_report.json": {
            "source_runs": {run_id: len(records) for run_id, records in runs.items()},
            "canonical_count": len(result["candidates"]),
            "merge_count": len(result["merges"]),
            "quarantined_count": len(result["quarantined"]),
            "run_deltas": result["run_deltas"],
            "merges": result["merges"],
            "quarantined": result["quarantined"],
        },
    }
    for run_id, records in runs.items():
        outputs[historical_dir / f"{run_id.casefold()}_sanitized.json"] = [
            {"historical_id": item.get("id"), "name": item["name"],
             "district": item["district"], "source_run": run_id}
            for item in records
        ]
    for path, payload in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs[RANKING_ROOT / "reconciliation_report.json"]


if __name__ == "__main__":
    print(json.dumps(write_historical_derivatives(), ensure_ascii=False, indent=2))
