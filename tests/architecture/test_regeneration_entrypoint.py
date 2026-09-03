"""One entrypoint must regenerate every derived artefact, idempotently.

Requirements: L05, M04, M05, O03. `git diff --exit-code` after regeneration is
only a valid staleness gate if the generators are deterministic and the
entrypoint covers them.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/regenerate_all.py"


def _tracked_state() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, timeout=120
    ).stdout


def test_entrypoint_exists_and_documents_the_excluded_generator():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "build_architecture_routes.py" in source, "the excluded generator must be named and justified"
    assert "OSM" in source


def test_entrypoint_covers_every_deterministic_generator():
    import importlib.util

    spec = importlib.util.spec_from_file_location("regenerate_all", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    covered = {script for script, _ in module.CORE} | {script for script, _ in module.BROWSER_QA}
    for required in (
        "build_architecture_learning_v2.py", "generate_architecture_pages.py",
        "build_master.py", "build_dual_release.py",
        "visual_resource_audit.py", "optics_accessibility_qa.py", "browser_release_qa.py",
    ):
        assert required in covered, f"{required} is not reachable from the regeneration entrypoint"
    assert all((ROOT / "scripts" / script).is_file() for script in covered)


def test_regenerating_leaves_the_tree_unchanged():
    """Deterministic generators must not dirty a clean tree."""
    before = _tracked_state()
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, timeout=1800
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    after = _tracked_state()
    assert after == before, (
        "regeneration changed the working tree; committed output was stale or a generator is "
        f"non-deterministic.\nbefore:\n{before}\nafter:\n{after}"
    )
