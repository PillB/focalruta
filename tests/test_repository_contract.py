from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_quality_workflow_enforces_cyclomatic_complexity_ceiling():
    workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    assert "ruff==0.12.11" in workflow
    assert "--select C901" in workflow
    assert "lint.mccabe.max-complexity=10" in workflow
    assert "python3 scripts/verify_release.py" in workflow
    assert "python3 scripts/verify_architecture.py" in workflow
