"""What CI runs on every pull request, and what it checks after every deploy.

Requirements X01 and X03. Until step 4 the browser suites ran only on the
owner's Mac: CI checked regeneration, tests and the committed reports, so a
change could pass CI with a report from an older run. These tests read the
workflows as YAML and fail when a browser suite exists that no CI job runs, or
when the live site goes unchecked after a deploy.
"""
from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
# Suites that load axe-core or Lighthouse from node_modules.
NEEDS_NPM = {"axe_accessibility_qa.py", "field_card_qa.py", "perf_budget_qa.py"}
ARCHITECTURE_SUITES = sorted(path.name for path in (ROOT / "tests/architecture").glob("browser_*.py"))


def workflow(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def triggers(document: dict) -> dict:
    # YAML 1.1 reads a bare `on` key as the boolean True.
    return document.get("on", document.get(True)) or {}


def run_lines(job: dict) -> str:
    return "\n".join(step.get("run", "") for step in job.get("steps", []))


def browser_suites() -> set[str]:
    spec = importlib.util.spec_from_file_location("regenerate_all", ROOT / "scripts/regenerate_all.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {script for script, _purpose in module.BROWSER_QA}


def browser_jobs(document: dict) -> list[dict]:
    return [job for job in document["jobs"].values() if "playwright install" in run_lines(job)]


def suites_run_by(job: dict) -> set[str]:
    """Scripts a job runs: its matrix entries plus scripts named in its steps."""
    named = set(re.findall(r"[\w/]*?(\w+\.py)", run_lines(job)))
    matrix = job.get("strategy", {}).get("matrix", {}).get("suite", [])
    return named | set(matrix)


def test_x01_every_browser_suite_runs_on_every_pull_request():
    quality = workflow("quality.yml")
    assert "pull_request" in triggers(quality)
    jobs = browser_jobs(quality)
    assert jobs, "no CI job installs a browser"
    covered = set().union(*(suites_run_by(job) for job in jobs))
    missing = (browser_suites() | set(ARCHITECTURE_SUITES)) - covered
    assert not missing, f"browser suites no CI job runs: {sorted(missing)}"


def test_x01_browser_jobs_install_pinned_tools_and_fail_on_a_red_suite():
    jobs = browser_jobs(workflow("quality.yml"))
    assert jobs, "no CI job installs a browser"
    for job in jobs:
        commands = run_lines(job)
        assert "pip install -r requirements-qa.txt" in commands
        if suites_run_by(job) & NEEDS_NPM:
            assert "npm ci" in commands, "axe-core and Lighthouse must come from package-lock.json"
        assert "continue-on-error" not in job and all("continue-on-error" not in step for step in job["steps"])
    pins = (ROOT / "requirements-qa.txt").read_text(encoding="utf-8")
    assert re.search(r"^playwright==\d+\.\d+\.\d+$", pins, re.M)
    lock = (ROOT / "package-lock.json").read_text(encoding="utf-8")
    assert '"node_modules/axe-core"' in lock and '"version": "4.10.3"' in lock
    assert '"node_modules/lighthouse"' in lock


def test_x01_suites_find_the_browser_without_a_mac_path():
    hard_coded = [path.relative_to(ROOT).as_posix()
                  for path in [*(ROOT / "scripts").glob("*.py"), *(ROOT / "tests/architecture").glob("browser_*.py")]
                  if "/Applications/Google Chrome.app" in path.read_text(encoding="utf-8")
                  and path.name != "qa_matrix.py"]
    assert not hard_coded, f"suites that only run on the owner's Mac: {hard_coded}"


def launches_ignoring_the_configured_browser(path: Path) -> list[int]:
    """Lines where a suite starts Chromium without qa_matrix.browser_options()."""
    lines = []
    for call in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr in ("launch", "launch_persistent_context"):
            expanded = [k.value for k in call.keywords if k.arg is None]
            if not any(isinstance(v, ast.Call) and ast.unparse(v.func) == "qa_matrix.browser_options" for v in expanded):
                lines.append(call.lineno)
    return lines


def test_x01_every_suite_starts_the_browser_ci_names():
    """Red team on PR #21, F3: three architecture suites started Playwright's own Chromium
    and ignored FOCALRUTA_CHROME, so CI and the owner's Mac could run them on different
    browsers than the other suites."""
    suites = [*(ROOT / "scripts").glob("*.py"), *(ROOT / "tests/architecture").glob("browser_*.py")]
    ignoring = {path.relative_to(ROOT).as_posix(): lines for path in suites if (lines := launches_ignoring_the_configured_browser(path))}
    assert not ignoring, f"suites that ignore FOCALRUTA_CHROME: {ignoring}"


def test_x03_only_the_deploy_job_can_write_to_pages():
    """Red team on PR #21, F4: Pages' write and token permissions were granted to the whole
    workflow, so the live-check it calls held them too. Least privilege: read at the top,
    and only the job that deploys may write."""
    writers = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        document = workflow(path.name)
        assert set((document.get("permissions") or {}).values()) <= {"read"}, f"{path.name} grants writes to every job"
        for name, job in document["jobs"].items():
            if any(level == "write" for level in (job.get("permissions") or {}).values()):
                writers[f"{path.name}:{name}"] = job["permissions"]
    assert writers == {"pages.yml:deploy": {"contents": "read", "pages": "write", "id-token": "write"}}, writers


def test_x03_the_live_site_is_checked_after_every_deploy_and_daily():
    pages = workflow("pages.yml")
    callers = [job for job in pages["jobs"].values() if job.get("uses") == "./.github/workflows/live-check.yml"]
    assert callers, "pages.yml does not run the live check"
    assert all(job.get("needs") == "deploy" or "deploy" in job.get("needs", []) for job in callers)
    live = workflow("live-check.yml")
    on = triggers(live)
    assert "workflow_call" in on and "workflow_dispatch" in on
    assert on.get("schedule"), "the live site must also be checked on a schedule"
    commands = "\n".join(run_lines(job) for job in live["jobs"].values())
    assert "scripts/live_pages_qa.py" in commands
    assert "scripts/perf_budget_qa.py --base-url" in commands


def uses_lines() -> list[tuple[str, str]]:
    """Every `uses:` of every workflow step, with the workflow it is in."""
    found = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(?:-\s*)?uses:\s*(\S+)(.*)$", line)
            if m:
                found.append((path.name, line.strip()))
    return found


def test_x09_every_outside_action_is_pinned_to_a_commit_with_its_tag_named():
    """Sign-off note on PR #21: the actions were pinned to tags, which their owner can move.
    A full commit SHA cannot be moved (GitHub's security hardening guide for Actions), and the
    comment after it names the release, so Dependabot and a reader can tell what it is."""
    lines = uses_lines()
    outside = [(name, line) for name, line in lines if "uses: ./" not in line]
    assert len(outside) >= 10, f"read only {len(outside)} outside actions: the scan reads nothing"
    loose = [f"{name}: {line}" for name, line in outside
             if not re.search(r"@[0-9a-f]{40}\s+#\s*v\d+(?:\.\d+){0,2}\s*$", line)]
    assert loose == [], "actions not pinned to a commit SHA with its tag:\n" + "\n".join(loose)


def test_x09_one_action_is_pinned_to_one_commit_everywhere():
    """The same action at two commits would run two versions in one pipeline."""
    pins: dict[str, set[str]] = {}
    for _name, line in uses_lines():
        m = re.search(r"uses:\s*([\w./-]+)@(\S+)", line)
        if m and not m.group(1).startswith("."):
            pins.setdefault(m.group(1), set()).add(m.group(2))
    assert pins, "no outside action found"
    assert {action: refs for action, refs in pins.items() if len(refs) > 1} == {}
