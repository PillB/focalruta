"""QA evidence must name the artefacts it audited, and still match them.

Requirements: M02, M04, M05, O03, Q03. The three reports gating verify_release
were last committed 2026-08-09 while the site they audit changed 2026-09-02.
Nothing could notice, because none of them records what it looked at.
"""
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
# The same names scripts/evidence.py exempts when it decides a tree is dirty.
REPORTS = (
    "CURRENT_BROWSER_QA.json",
    "OPTICS_ACCESSIBILITY_QA.json",
    "VISUAL_RESOURCE_QA.json",
    "AXE_ACCESSIBILITY_QA.json",
    "FIELD_CARD_QA.json",
)


def _report(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", REPORTS)
def test_report_records_what_it_audited(name):
    report = _report(name)
    assert report.get("audited_at"), f"{name} does not say when it ran"
    assert re.fullmatch(r"[0-9a-f]{40}(\+dirty)?", report.get("audited_commit", "")), f"{name} does not say which commit it audited"
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


def test_no_unbound_qa_report_sits_beside_the_current_evidence():
    # Six August reports with no fingerprints lived at the root next to these.
    assert sorted(path.name for path in ROOT.glob("*QA*.json")) == sorted(REPORTS)


@pytest.mark.parametrize("name", REPORTS)
def test_report_was_produced_on_a_committed_tree(name):
    """Evidence names a commit a reviewer can check out, not "+dirty" (red-team second pass on PR #19)."""
    assert not _report(name)["audited_commit"].endswith("+dirty"), f"{name} was produced on an uncommitted tree"


def test_a_report_written_by_an_earlier_suite_does_not_make_the_tree_dirty(tmp_path):
    import shutil
    import subprocess
    import sys

    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    sys.path.insert(0, str(ROOT / "scripts"))
    import evidence

    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "index.html").write_text("a", encoding="utf-8")
    (tmp_path / "VISUAL_RESOURCE_QA.json").write_text("{}", encoding="utf-8")
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "c")
    (tmp_path / "VISUAL_RESOURCE_QA.json").write_text('{"checks": 1}', encoding="utf-8")
    assert not evidence.current_commit(tmp_path).endswith("+dirty")
    # Only the suites' own reports are exempt, by name: another evidence-looking file still counts.
    (tmp_path / "OLD_BROWSER_QA.json").write_text("{}", encoding="utf-8")
    git("add", "OLD_BROWSER_QA.json")
    assert evidence.current_commit(tmp_path).endswith("+dirty")
    git("reset", "-q", "OLD_BROWSER_QA.json")
    (tmp_path / "OLD_BROWSER_QA.json").unlink()
    (tmp_path / "index.html").write_text("b", encoding="utf-8")
    assert evidence.current_commit(tmp_path).endswith("+dirty")


def test_the_dirty_check_exempts_exactly_the_reports_this_file_holds_to_account():
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    import evidence

    assert evidence.QA_REPORTS == set(REPORTS)
