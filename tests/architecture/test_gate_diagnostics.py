"""Inducing a one-byte regression must produce a message that locates it.

Requirements: M01, M04, O03. Detection without localization is what made every
parity failure in this project cost a manual investigation.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "challenges/arquitectura-en-foco/index.html"
VERIFIER = ROOT / "scripts/verify_architecture.py"


def _run_verifier() -> dict:
    completed = subprocess.run(
        [sys.executable, str(VERIFIER)], capture_output=True, text=True, cwd=ROOT, timeout=180
    )
    return json.loads(completed.stdout)


def test_clean_tree_passes():
    assert _run_verifier()["passed"] is True


def test_one_byte_regression_is_located_not_merely_detected(tmp_path):
    backup = tmp_path / "index.html"
    shutil.copy2(PAGE, backup)
    original = PAGE.read_text(encoding="utf-8")
    marker = 'id="perspective-fov"'
    assert marker in original
    mutated = original.replace(marker, 'id="perspective-fov_"', 1)
    # Derive the true first-differing index independently of the code under test.
    offset = next(i for i in range(min(len(original), len(mutated))) if original[i] != mutated[i])
    try:
        PAGE.write_text(mutated, encoding="utf-8")
        report = _run_verifier()
        assert report["passed"] is False
        blob = " ".join(report["checks_failed"])
        assert str(offset) in blob, f"the failure must carry the offset; got: {blob[:400]}"
        assert "perspective-fov" in blob, "the failure must show the surrounding content"
        assert len(blob) < 20000, "the failure must stay readable, not dump the artifact"
    finally:
        shutil.copy2(backup, PAGE)
    assert _run_verifier()["passed"] is True
