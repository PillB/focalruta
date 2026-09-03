"""QA evidence must name the artefacts it audited, and still match them.

Requirements: M02, M04, M05, O03, Q03. The three reports gating verify_release
were last committed 2026-08-09 while the site they audit changed 2026-09-02.
Nothing could notice, because none of them records what it looked at.
"""
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ("CURRENT_BROWSER_QA.json", "OPTICS_ACCESSIBILITY_QA.json", "VISUAL_RESOURCE_QA.json")


def _report(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", REPORTS)
def test_report_records_what_it_audited(name):
    report = _report(name)
    assert report.get("audited_at"), f"{name} does not say when it ran"
    audited = report.get("audited_artifacts")
    assert isinstance(audited, dict) and audited, f"{name} does not say what it inspected"
    for path in audited:
        assert (ROOT / path).is_file(), f"{name} audited {path}, which no longer exists"


@pytest.mark.parametrize("name", REPORTS)
def test_report_still_matches_the_files_it_audited(name):
    report = _report(name)
    drifted = []
    for path, recorded in report["audited_artifacts"].items():
        current = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if current != recorded:
            drifted.append(path)
    assert not drifted, (
        f"{name} was produced against a different build; re-run its generator. Changed since: {drifted}"
    )


@pytest.mark.parametrize("name", REPORTS)
def test_report_still_passes(name):
    report = _report(name)
    assert report.get("passed") is True
    assert report.get("checks", 0) > 0
