#!/usr/bin/env python3
"""Build typed Bonilla source and claim records without promoting candidates."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BONILLA_ROOT = ROOT / "architectural_photography" / "research" / "bonilla"
SNAPSHOT_ROOT = BONILLA_ROOT / "snapshots"
SOURCE_OUTPUT = BONILLA_ROOT / "source_records.json"
CLAIM_OUTPUT = BONILLA_ROOT / "claim_records.jsonl"
GLOBAL_CLAIMS = ROOT / "architectural_photography" / "state" / "CLAIM_GRAPH.jsonl"


def source_type(source_id):
    number = int(source_id[1:])
    if number == 1:
        return "PRIMARY"
    if 2 <= number <= 5:
        return "ACADEMIC"
    return "JOURNALISM"


def publisher(url):
    if "juntadeandalucia" in url:
        return "Junta de Andalucía"
    if "usmp.edu.pe" in url:
        return "Universidad de San Martín de Porres"
    if "dialnet.unirioja.es" in url:
        return "Dialnet / Universidad de La Rioja"
    if "ulima.edu.pe" in url:
        return "Universidad de Lima"
    if "scielo.org.ar" in url:
        return "SciELO Argentina"
    if "rpp.pe" in url:
        return "RPP"
    return "El Comercio"


def privacy_class(record_type):
    return "PUBLIC_PRIMARY" if record_type in {"PRIMARY", "ACADEMIC"} else "PUBLIC_SECONDARY"


def make_source(snapshot):
    record_type = source_type(snapshot["source_id"])
    return {
        "source_id": f"SRC-BONILLA-{snapshot['source_id']}",
        "type": record_type,
        "url_or_path": snapshot["url"],
        "publisher": publisher(snapshot["url"]),
        "publication_date": None,
        "event_date": None,
        "retrieved_at": snapshot["retrieved_at"],
        "independence_cluster": f"bonilla_{snapshot['source_id'].casefold()}",
        "privacy_class": privacy_class(record_type),
        "status": "ACTIVE" if snapshot["source_access"] == "DIRECT_CURRENT" else "HISTORICAL",
    }


def claim_text(snapshot):
    if snapshot["source_id"] == "W12":
        return (
            "Cantagallo is geographically within Rímac, Lima, but any photographic hypothesis involving the "
            "Shipibo-Konibo community requires collaboration or consent and cannot use hidden telephoto capture."
        )
    return f"Bonilla framework lesson: {snapshot['lesson']}"


def make_claim(snapshot):
    verified = snapshot["source_access"] == "DIRECT_CURRENT"
    return {
        "claim_id": snapshot["claim_ids"][0],
        "entity": f"bonilla_{snapshot['source_id'].casefold()}",
        "claim": claim_text(snapshot),
        "source_ids": [f"SRC-BONILLA-{snapshot['source_id']}"],
        "evidence_status": "VERIFIED" if verified else "PARTIAL",
        "as_of": snapshot["retrieved_at"][:10],
        "confidence": snapshot["confidence"],
        "contradictions": [snapshot["expert_rejection"]],
        "ranking_impacts": ["FRAMEWORK_ONLY_NO_SCORE_OR_PROMOTION"],
        "route_impacts": ["CURRENT_PLACE_AND_ACCESS_SOURCE_REQUIRED"],
    }


def write_jsonl(path, records):
    path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8")


def main():
    snapshots = [
        json.loads((SNAPSHOT_ROOT / f"W{number:02d}_snapshot.json").read_text(encoding="utf-8"))
        for number in range(1, 21)
    ]
    sources = [make_source(snapshot) for snapshot in snapshots]
    claims = [make_claim(snapshot) for snapshot in snapshots]
    SOURCE_OUTPUT.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_jsonl(CLAIM_OUTPUT, claims)
    existing = [
        json.loads(line)
        for line in GLOBAL_CLAIMS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not json.loads(line)["claim_id"].startswith("CLM-BONILLA-")
    ]
    write_jsonl(GLOBAL_CLAIMS, existing + claims)
    print(json.dumps({"sources": len(sources), "claims": len(claims), "candidate_promotions": 0}))


if __name__ == "__main__":
    main()
