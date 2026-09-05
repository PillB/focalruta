"""Publishing the hosted build must never leave a half-written tree on disk.

Requirements: L06, M05, O03.

`build_dual_release.py` used to `shutil.rmtree(dist/…)` and then repopulate it
over several seconds. Anything reading the directory in that window — a QA
script, CI, or a `git add -A` — saw an empty or partial tree. That is exactly
how a commit in this project once staged 176 spurious deletions.

The repository already had the right pattern in
`build_architecture_routes.publish_downloads`: stage elsewhere, then swap.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOSTED = ROOT / "dist/canon6d_sota_hosted"
BUILD = ROOT / "scripts/build_dual_release.py"


@pytest.fixture()
def perturbed():
    """Damage a tracked input for one test, then restore it from git.

    These tests must break the build to prove it fails safely, which means
    touching real files. Restoring from git rather than from a copy means the
    file comes back byte-exact even if the copy step itself went wrong, and the
    fixture also sweeps any staging directory a failed build left behind.
    """
    touched: list[Path] = []

    def damage(relative: str, content: Optional[str]) -> Path:
        path = ROOT / relative
        touched.append(path)
        if content is None:
            path.unlink()
        else:
            path.write_text(content, encoding="utf-8")
        return path

    yield damage

    for path in touched:
        subprocess.run(
            ["git", "checkout", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, timeout=60, check=False,
        )
        assert path.is_file(), f"{path.name} was not restored; run: git checkout -- {path.name}"
    for staging in (ROOT / "dist").glob(".canon6d_sota_hosted.*"):
        shutil.rmtree(staging, ignore_errors=True)


def test_the_published_tree_is_populated():
    assert HOSTED.is_dir()
    assert len(list(HOSTED.rglob("*"))) > 100, "the hosted build looks truncated"
    for required in ("index.html", "FocalRuta_STANDALONE.html", "sw.js", "BUILD_METRICS.json"):
        assert (HOSTED / required).is_file(), f"{required} missing from the published build"


def test_a_failed_build_leaves_the_previous_publication_intact(perturbed):
    """Interrupt the build partway and the live directory must be untouched."""
    before = sorted(path.relative_to(HOSTED).as_posix() for path in HOSTED.rglob("*") if path.is_file())
    assert before, "precondition: something must already be published"

    # field_card.html is copied well after the tree has started filling, so its
    # absence interrupts a build that is already partway through writing.
    perturbed("field_card.html", None)
    completed = subprocess.run(
        [sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True, timeout=900
    )
    assert completed.returncode != 0, "the build should have failed on a missing input"

    after = sorted(path.relative_to(HOSTED).as_posix() for path in HOSTED.rglob("*") if path.is_file())
    assert after == before, (
        "a failed build damaged the published tree; publication must be atomic.\n"
        f"lost: {sorted(set(before) - set(after))[:10]}"
    )


def test_macos_folder_metadata_is_not_published():
    """.DS_Store was being copied into the published tree by copytree."""
    strays = [path.relative_to(ROOT).as_posix() for path in HOSTED.rglob(".DS_Store")]
    assert not strays, f"macOS metadata published to the site: {strays}"


def test_the_build_refuses_to_publish_unparseable_canonical_data(perturbed):
    """A corrupt plans.json once shipped to the site and the build reported success."""
    perturbed("data/plans.json", "{ not valid json")
    completed = subprocess.run(
        [sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True, timeout=900
    )
    assert completed.returncode != 0, "the build published invalid canonical data"
    assert "not valid JSON" in completed.stderr
    published = (HOSTED / "data/plans.json").read_text(encoding="utf-8")
    assert json.loads(published), "the published copy must remain the last good one"
