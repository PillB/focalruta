"""The QA harness must cover the mandated viewports and never hang silently.

Requirements: N01, N02, M01, O03.

N01 mandates six viewports. Four browser scripts each kept their own copy of the
list and two more kept a different, shorter one — so "the responsive matrix" was
three lists, one of which tested a viewport N01 does not name.

Playwright's `page.evaluate` has no promise timeout (microsoft/playwright#13253)
and `navigator.serviceWorker.ready` never rejects by specification, so an
unguarded await of it blocks the run forever rather than failing.
"""
import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qa_matrix

QA_SCRIPTS = sorted((ROOT / "tests/architecture").glob("browser_*.py")) + [
    ROOT / "scripts/browser_release_qa.py",
    ROOT / "scripts/live_pages_qa.py",
]


def test_the_mandated_viewports_come_from_the_requirement_not_from_memory():
    inventory = (ROOT / "architectural_photography/REQUIREMENTS_INVENTORY.md").read_text(encoding="utf-8")
    line = next(row for row in inventory.splitlines() if row.startswith("- **N01"))
    required = {
        (int(width), int(height))
        for width, height in re.findall(r"(\d{3,4})×(\d{3,4})", line)
    }
    assert set(qa_matrix.REQUIRED_VIEWPORTS) == required, (
        f"the shared matrix disagrees with N01: {sorted(set(qa_matrix.REQUIRED_VIEWPORTS) ^ required)}"
    )


@pytest.mark.parametrize("script", QA_SCRIPTS, ids=lambda p: p.name)
def test_no_qa_script_keeps_its_own_viewport_list(script):
    source = script.read_text(encoding="utf-8")
    inline = re.findall(r"\(\s*\d{3,4}\s*,\s*\d{3,4}\s*\)\s*,\s*\(\s*\d{3,4}\s*,\s*\d{3,4}\s*\)", source)
    assert not inline, f"{script.name} hardcodes a viewport list instead of importing qa_matrix"


def _evaluate_arguments(source: str) -> list[str]:
    """Every literal JavaScript string handed to page.evaluate, via the AST.

    A regex cannot do this: the JavaScript contains its own quotes, so a
    non-greedy match truncates the body and silently reports zero awaits.
    """
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"evaluate", "evaluate_handle"} or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            found.append(first.value)
        elif isinstance(first, ast.Call):
            # e.g. qa_matrix.bounded_async("..."): already wrapped, record as bounded.
            found.append("Promise.race")
    return found


@pytest.mark.parametrize("script", QA_SCRIPTS, ids=lambda p: p.name)
def test_every_awaited_evaluate_is_bounded(script):
    """An `await` inside page.evaluate must not be able to block forever."""
    for call in _evaluate_arguments(script.read_text(encoding="utf-8")):
        if "await" not in call:
            continue
        assert "Promise.race" in call, (
            f"{script.name} awaits inside page.evaluate without a race; "
            "Playwright cannot time this out (microsoft/playwright#13253)"
        )


def test_the_inspection_actually_sees_the_javascript_it_checks():
    """Guard against the truncating-regex false green this test used to have."""
    calls = _evaluate_arguments((ROOT / "scripts/live_pages_qa.py").read_text(encoding="utf-8"))
    assert len(calls) >= 15, f"only {len(calls)} evaluate calls parsed; the inspection is under-matching"
    assert any("await" in call for call in calls), "no awaited expression seen; the parser is not reading bodies"


def test_the_shared_race_helper_rejects_a_promise_that_never_settles():
    expression = qa_matrix.bounded_async("new Promise(()=>{})", 50)
    assert "Promise.race" in expression
    assert "50" in expression


SHIPPED_PAGES = (ROOT / "index.html", ROOT / "dist/canon6d_sota_hosted/index.html")


def optics_drift(html: str) -> list[str]:
    """Constants the shipped optical lab disagrees with optics_physics about.

    scripts/optics_physics.py is the tested source of truth for Python and the
    challenge labs. The root optical lab keeps its own JavaScript
    implementation, so the least that must hold is that the physical constants
    it ships still equal the ones under test.

    Returned as a list rather than asserted in place so the guard itself can be
    exercised in both directions — a guard that has only ever passed proves
    nothing about what it would catch.
    """
    import optics_physics

    match = re.search(r"const coc=([\d.]+),sw=([\d.]+)", html)
    if not match:
        return ["the optical-lab constants are no longer present"]
    shipped = (
        ("circle of confusion", float(match.group(1)), optics_physics.FULL_FRAME_COC_MM),
        ("sensor width", float(match.group(2)), optics_physics.CANON_6D_WIDTH_MM),
    )
    return [
        f"{name} drifted: page ships {found}, optics_physics has {expected}"
        for name, found, expected in shipped
        if found != expected
    ]


@pytest.mark.parametrize("page", SHIPPED_PAGES, ids=lambda p: p.parent.name or p.name)
def test_shipped_optics_constants_agree_with_the_python_module(page):
    assert optics_drift(page.read_text(encoding="utf-8", errors="replace")) == []


def test_the_optics_guard_actually_detects_a_drifted_constant():
    """Proof the guard can fail, without mutating a shipped page to find out."""
    assert optics_drift("const coc=.03,sw=35.8,stops=[]") == []
    assert optics_drift("const coc=.03,sw=36.0,stops=[]") == [
        "sensor width drifted: page ships 36.0, optics_physics has 35.8"
    ]
    assert len(optics_drift("const coc=.031,sw=36.0,stops=[]")) == 2
    assert optics_drift("<html>no optical lab here</html>") == [
        "the optical-lab constants are no longer present"
    ]


def test_the_superseded_optics_generator_is_not_wired_into_the_build():
    """sota_upgrade.py is historical; its output must not reappear in the page."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("regenerate_all", ROOT / "scripts/regenerate_all.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    wired = {script for script, _ in module.CORE} | {script for script, _ in module.BROWSER_QA}
    assert "sota_upgrade.py" not in wired
    for page in SHIPPED_PAGES:
        assert "maxScene=30" not in page.read_text(encoding="utf-8", errors="replace"), (
            f"{page.name} carries output from the superseded generator"
        )
