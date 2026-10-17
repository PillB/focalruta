"""Every element a page's script looks up is on the page (V05).

Rebuilding the field card replaced the home page's card block wholesale, and
the session-run dialog («Modo sesión») had been inserted inside that block, so
it disappeared: the button still called openSessionRun(), which found no
dialog and silently did nothing. No test noticed, because every lookup in the
page is guarded with `if (!d) return`.

This holds the wiring statically, on every shipped page: an id the script
fetches with getElementById('…') must exist in the markup or be created by
the script, and a function the markup calls (onclick="openFieldCard()") is
defined once, so the one that runs is not decided by load order (the red
team found two openFieldCard definitions). It also holds the card
integration to replacing only the card.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import integrate_field_card  # noqa: E402

HOSTED = ROOT / "dist" / "canon6d_sota_hosted"
PAGES = [ROOT / "index.html", ROOT / "field_card.html", *sorted((ROOT / "plans").glob("plan_*.html")),
         HOSTED / "index.html", HOSTED / "field_card.html", *sorted((HOSTED / "plans").glob("plan_*.html"))]
# assets/gear.js runs on every page but draws its picker only where the home page offers one;
# assets/diagnostics.js records on every scripted page but shows its log only in the home page's footer.
OPTIONAL = {"gear-config", "diag-list", "diag-empty", "diag-report", "diag-count", "diag-copy", "diag-clear"}
INLINE_DATA = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=]+")
LOOKUP = re.compile(r"getElementById\(\s*['\"]([\w-]+)['\"]\s*\)")
DECLARED = re.compile(r"\bid=[\"']([\w-]+)[\"']|\.id\s*=\s*['\"]([\w-]+)['\"]")
HANDLER = re.compile(r"\son[a-z]+=\"([A-Za-z_$][\w$]*)\(")
DEFINITION = r"(?:\bfunction\s+{0}\s*\(|\bwindow\.{0}\s*=)"


def missing_ids(text: str) -> list[str]:
    text = INLINE_DATA.sub("data:", text)
    declared = {a or b for a, b in DECLARED.findall(text)}
    return sorted(set(LOOKUP.findall(text)) - declared - OPTIONAL)


def handlers_not_defined_once(text: str) -> dict[str, int]:
    text = INLINE_DATA.sub("data:", text)
    counts = {name: len(re.findall(DEFINITION.format(re.escape(name)), text)) for name in set(HANDLER.findall(text))}
    return {name: count for name, count in sorted(counts.items()) if count != 1}


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_v05_every_function_the_markup_calls_is_defined_once(page):
    assert handlers_not_defined_once(page.read_text(encoding="utf-8")) == {}


def test_v05_the_handler_scan_sees_a_duplicate_and_a_missing_function():
    sample = '<button onclick="a()"></button><button onclick="b(1)"></button><script>function a(){}window.a=function(){}</script>'
    assert handlers_not_defined_once(sample) == {"a": 2, "b": 0}


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_v05_every_element_the_script_looks_up_is_on_the_page(page):
    assert missing_ids(page.read_text(encoding="utf-8")) == []


def test_v05_the_wiring_scan_sees_a_missing_element():
    assert missing_ids("<div id='a'></div><script>getElementById('a');getElementById('b')</script>") == ["b"]
    assert missing_ids("<script>const d=document.createElement('dialog');d.id='c';getElementById('c')</script>") == []


def test_v05_card_integration_refuses_to_drop_other_markup():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    start = page.index("<!-- FIELD CARD INTEGRATED -->") + len("<!-- FIELD CARD INTEGRATED -->")
    crowded = page[:start] + '\n<dialog id="other-dialog"></dialog>' + page[start:]
    with pytest.raises(RuntimeError, match="other-dialog"):
        integrate_field_card.patch(crowded)
    assert integrate_field_card.patch(page) == page
