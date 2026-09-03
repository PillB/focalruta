"""Editorial invariants that survive a rewrite but still catch regressions.

Requirements: G06, L10, M03, N03, N04, O03. Around sixty assertions pinned exact
Spanish sentences, so any rewording broke tests that had nothing to do with the
change — and a rewrite that quietly dropped a safety caveat could still pass by
keeping the sentence elsewhere. These contracts check the property instead.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHALLENGE = ROOT / "challenges/arquitectura-en-foco/index.html"
WIKI = ROOT / "challenges/arquitectura-en-foco/wiki-tecnicas.html"
LEARNING = ROOT / "data/architecture/learning.json"
PUBLIC_PAGES = [
    ROOT / "index.html", ROOT / "field_card.html",
    *sorted((ROOT / "challenges").rglob("*.html")),
    *sorted((ROOT / "plans").glob("plan_*.html")),
]


def _text(path: Path) -> str:
    return re.sub(r"<[^>]+>", " ", path.read_text(encoding="utf-8", errors="replace"))


def test_no_public_page_promises_a_chance_of_winning():
    """The internal model is a practice lens, never a forecast (A03, J02)."""
    forbidden = ("probabilidad de ganar", "probability of winning", "vas a ganar")
    for path in PUBLIC_PAGES:
        lowered = _text(path).lower()
        for phrase in forbidden:
            assert phrase not in lowered, f"{path.name} promises an outcome: {phrase!r}"


def test_every_lab_declares_the_limit_of_its_model():
    """A computed diagram must say what it does not predict."""
    html = CHALLENGE.read_text(encoding="utf-8")
    labs = re.findall(r'<article class="learning-lab".*?</article>', html, re.DOTALL)
    learning = json.loads(LEARNING.read_text(encoding="utf-8"))
    assert len(labs) == len(learning["simulations"])
    for lab in labs:
        assert 'class="route-note"' in lab, "a lab published without its declared limit"
        assert re.search(r"Límite del modelo", lab), "the limit must be labelled, not implied"


def test_every_lab_offers_recovery_and_a_starting_state():
    html = CHALLENGE.read_text(encoding="utf-8")
    labs = re.findall(r'<article class="learning-lab".*?</article>', html, re.DOTALL)
    for lab in labs:
        assert 'class="lab-reset"' in lab, "no way back to a known state"
        controls = re.findall(r"data-lab-control[^>]*", lab)
        assert controls, "a lab with no control is not interactive"
        assert all("data-default" in control for control in controls), "a control with no initial state"


def test_every_interactive_control_is_labelled_for_assistive_technology():
    html = CHALLENGE.read_text(encoding="utf-8")
    for control_id in re.findall(r'id="([^"]+)"[^>]*data-lab-control', html):
        assert f'for="{control_id}"' in html, f"{control_id} has no <label>"


def test_the_no_javascript_fallback_covers_every_lab():
    html = CHALLENGE.read_text(encoding="utf-8")
    fallback = html.split("<noscript>", 1)[1].split("</noscript>", 1)[0]
    numbered = re.findall(r"<p><strong>(\d+)\.", fallback)
    assert [int(item) for item in numbered] == list(range(1, html.count('class="learning-lab"') + 1))


def test_every_technique_family_reaches_a_place_to_practise_it():
    wiki = WIKI.read_text(encoding="utf-8")
    articles = re.findall(r'<article class="wiki-technique".*?</article>', wiki, re.DOTALL)
    assert articles
    for article in articles:
        assert re.search(r'href="index\.html#(lab-[\w-]+|rules)"', article), (
            "a technique that leads nowhere the reader can try it"
        )


JARGON = (
    (ROOT / "index.html", "pdc", "profundidad de campo"),
    (ROOT / "challenges/arquitectura-en-foco/index.html", "kml", "google"),
    (ROOT / "challenges/arquitectura-en-foco/index.html", "geojson", "mapa"),
    (ROOT / "challenges/arquitectura-en-foco/wiki-tecnicas.html", "schlick", "vidrio"),
)


@pytest.mark.parametrize("path,term,definition", JARGON)
def test_jargon_is_explained_on_the_page_that_uses_it(path, term, definition):
    """An operational term must carry its explanation where the reader meets it (G06, L10)."""
    html = _text(path).lower()
    if term not in html:
        pytest.skip(f"{path.name} does not use {term}")
    assert definition in html, f"{path.name} uses {term!r} with no nearby explanation"


@pytest.mark.parametrize("path", [p for p in PUBLIC_PAGES if p.name.endswith(".html")])
def test_no_page_ships_an_unresolved_template_placeholder(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    # "TODO" alone is a common Spanish word ("todo el encuadre"), so only the
    # marker forms count as an unresolved placeholder.
    for placeholder in ("{{", "TODO:", "FIXME", "XXX:", "lorem ipsum", ">undefined<", ">NaN<", ">null<"):
        assert placeholder not in raw, f"{path.name} ships {placeholder!r}"
