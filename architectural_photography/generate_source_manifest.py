#!/usr/bin/env python3
"""Inventory architecture workbench inputs with stable privacy classifications."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "SOURCE_MANIFEST.json"


def privacy_class(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix().lower()
    name = path.name.lower()
    if relative.startswith("inputs_private/"):
        return "PRIVATE_LOCAL"
    if name.endswith(".zip") or "architectura" in name or "strategy.json" in name:
        return "PRIVATE_LOCAL"
    if "reference_copies/architectura_historical_log" in relative:
        return "PRIVATE_LOCAL"
    if name.endswith(".pdf") and "bases" in name:
        return "PUBLIC_PRIMARY"
    if name in {"source_manifest.json", "generate_source_manifest.py"}:
        return "GENERATED_LOCAL"
    if "execution_kit" in relative:
        return "GENERATED_LOCAL"
    if name.endswith((".html", "_qa.json", "_ranking.json", "_snapshots.json")):
        return "HISTORICAL_ARTIFACT"
    return "GENERATED_LOCAL"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path != OUTPUT)
    records = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "privacy_class": privacy_class(path),
        }
        for path in files
    ]
    payload = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": "architectural_photography",
        "entry_count": len(records),
        "entries": records,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
