import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def pinned(workflow: str, action: str, major: int) -> bool:
    """`action` is pinned to a commit of release `major` (X09 pins to a SHA, its tag in a comment)."""
    return re.search(rf"{re.escape(action)}@[0-9a-f]{{40}} # v{major}(?:\.\d+)*\s*$", workflow, re.M) is not None


def test_quality_workflow_enforces_cyclomatic_complexity_ceiling():
    workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    assert pinned(workflow, "actions/checkout", 5)
    assert pinned(workflow, "actions/setup-python", 6)
    # One pin list for CI and contributors: a different local Pillow re-encodes
    # 132 images and dirties the tree (red team, PR #19).
    assert "pip install -r requirements-dev.txt" in workflow
    pins = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").split()
    assert "ruff==0.12.11" in pins
    assert "Pillow==11.3.0" in pins
    assert "--select C901" in workflow
    assert "lint.mccabe.max-complexity=10" in workflow
    assert "python3 scripts/verify_release.py" in workflow
    assert "python3 scripts/verify_architecture.py" in workflow


def test_pages_workflow_uses_node24_action_generations():
    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert pinned(workflow, "actions/checkout", 5)
    assert pinned(workflow, "actions/configure-pages", 6)
    assert pinned(workflow, "actions/upload-pages-artifact", 5)
    assert pinned(workflow, "actions/deploy-pages", 5)
    assert "# v4" not in workflow and "@v4" not in workflow
    assert not pinned(workflow, "actions/upload-pages-artifact", 3)


def test_agent_contract_requires_expert_rejection_and_fail_fast_evidence():
    contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required = (
        "Expert-rejection gate",
        "methodological and scientific correctness",
        "Tautological tests are prohibited",
        "stop the run and surface the issue",
        "⌘⌥Q",
        "Every trade-off",
    )
    assert all(phrase in contract for phrase in required)
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "`AGENTS.md`" in claude
    assert "/Users/pabloillescas/Documents/GitHub/focalruta/AGENTS.md" in claude
