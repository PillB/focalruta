#!/usr/bin/env python3
"""Bind a QA report to the artefacts it audited.

A report that says only `{"passed": true, "checks": 234}` cannot go stale
loudly: the three reports gating `verify_release.py` were produced on
2026-08-09 and kept passing against a site last regenerated on 2026-09-02.
Recording a fingerprint of every inspected file turns a month of silent drift
into a named failure.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(paths) -> dict[str, str]:
    """sha256 per audited file, keyed by repository-relative path."""
    prints: dict[str, str] = {}
    for path in paths:
        resolved = Path(path)
        if not resolved.is_absolute():
            resolved = ROOT / resolved
        if resolved.is_file():
            prints[str(resolved.relative_to(ROOT))] = hashlib.sha256(resolved.read_bytes()).hexdigest()
    return dict(sorted(prints.items()))


def stamp(report: dict, audited_paths) -> dict:
    """Add provenance to a QA report without disturbing its existing shape."""
    report["audited_at"] = datetime.now(timezone.utc).isoformat()
    report["audited_commit"] = os.environ.get("GITHUB_SHA", "")
    report["audited_artifacts"] = fingerprint(audited_paths)
    return report


def write_report(path: Path, report: dict, audited_paths) -> dict:
    """Stamp and write a QA report atomically."""
    stamped = stamp(report, audited_paths)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(stamped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return stamped
