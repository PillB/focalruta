from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_quality_workflow_enforces_cyclomatic_complexity_ceiling():
    workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    assert "actions/checkout@v5" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "--select C901" in workflow
    assert "lint.mccabe.max-complexity=10" in workflow
    assert "python3 scripts/verify_release.py" in workflow
    assert "python3 scripts/verify_architecture.py" in workflow


def test_ci_and_contributors_install_the_same_dependency_set():
    """The dependency list must live in one file, not be retyped in the workflow."""
    workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    assert "-r requirements-dev.txt" in workflow, (
        "the workflow must install from requirements-dev.txt so CI and local runs agree"
    )
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    for pinned in ("ruff==0.12.11", "Pillow==11.3.0"):
        assert pinned in requirements, f"{pinned} must stay pinned for reproducibility"
    # pytest.ini declares a timeout; without this plugin pytest silently ignores it.
    assert "pytest-timeout" in requirements
    assert "timeout" in (ROOT / "pytest.ini").read_text(encoding="utf-8")


def test_pages_workflow_uses_node24_action_generations():
    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "actions/checkout@v5" in workflow
    assert "actions/configure-pages@v6" in workflow
    assert "actions/upload-pages-artifact@v5" in workflow
    assert "actions/deploy-pages@v5" in workflow
    assert "@v4" not in workflow
    assert "upload-pages-artifact@v3" not in workflow


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
