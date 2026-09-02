"""RED/GREEN contracts for navigation coherence and per-technique visuals.

Requirements: G04, G05, G06, L10, M03, N03, N04.

The visual assertions compare rendered geometry against itself rather than
against a literal, so a shared placeholder diagram cannot satisfy them.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "challenges/arquitectura-en-foco/index.html"
WIKI = ROOT / "challenges/arquitectura-en-foco/wiki-tecnicas.html"
LEARNING = ROOT / "data/architecture/learning.json"

SECTION_RE = re.compile(r'<section id="([^"]+)"', re.DOTALL)
SVG_RE = re.compile(r"<svg.*?</svg>", re.DOTALL)


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def _wiki() -> str:
    return WIKI.read_text(encoding="utf-8")


def _nav_targets(html: str) -> list[str]:
    nav = re.search(r"<nav[^>]*>(.*?)</nav>", html, re.DOTALL)
    assert nav, "the challenge page must expose a navigation landmark"
    return re.findall(r'href="#([^"]+)"', nav.group(1))


def _fingerprint(svg: str) -> str:
    """Hash the drawing only, so labels alone cannot make two diagrams differ."""
    geometry = re.sub(r'\s(aria-label|role|id|class)="[^"]*"', "", svg)
    geometry = re.sub(r">[^<]*<", "><", geometry)
    return hashlib.sha256(geometry.encode("utf-8")).hexdigest()


def test_navigation_order_follows_the_order_a_reader_actually_scrolls():
    html = _page()
    positions = {match.group(1): match.start() for match in SECTION_RE.finditer(html)}
    targets = [target for target in _nav_targets(html) if target in positions]
    scrolled = [positions[target] for target in targets]
    assert scrolled == sorted(scrolled), (
        "navigation order contradicts document order: "
        f"{targets} vs {sorted(targets, key=positions.get)}"
    )


def test_every_visible_section_is_reachable_from_the_navigation():
    html = _page()
    sections = {match.group(1) for match in SECTION_RE.finditer(html)}
    reachable = set(_nav_targets(html))
    assert sections <= reachable, f"unreachable sections: {sorted(sections - reachable)}"


def test_each_technique_family_has_its_own_diagram():
    wiki = _wiki()
    learning = json.loads(LEARNING.read_text(encoding="utf-8"))
    articles = re.findall(r'<article class="wiki-technique".*?</article>', wiki, re.DOTALL)
    assert len(articles) == len(learning["technique_cards"])
    prints = []
    for article in articles:
        svgs = SVG_RE.findall(article)
        assert svgs, "every technique family needs a diagram"
        prints.append(_fingerprint(svgs[0]))
    assert len(set(prints)) == len(prints), "technique diagrams repeat the same drawing"


def test_each_technique_family_is_directly_linkable():
    wiki = _wiki()
    learning = json.loads(LEARNING.read_text(encoding="utf-8"))
    anchors = re.findall(r'<article class="wiki-technique" id="([^"]+)"', wiki)
    assert len(anchors) == len(learning["technique_cards"])
    assert len(set(anchors)) == len(anchors)
    for anchor in anchors:
        assert f'href="#{anchor}"' in wiki, f"{anchor} has no link pointing at it"


def test_wiki_offers_a_symptom_entry_point_into_the_techniques():
    wiki = _wiki()
    index = re.search(r'<(?:nav|section)[^>]*id="sintomas".*?</(?:nav|section)>', wiki, re.DOTALL)
    assert index, "the wiki needs a symptom-first entry point"
    targets = re.findall(r'href="#([^"]+)"', index.group(0))
    anchors = set(re.findall(r'<article class="wiki-technique" id="([^"]+)"', wiki))
    assert len(targets) >= 5
    assert set(targets) <= anchors


def test_every_interactive_lab_draws_something_of_its_own():
    html = _page()
    labs = re.findall(r'<article class="learning-lab".*?</article>', html, re.DOTALL)
    learning = json.loads(LEARNING.read_text(encoding="utf-8"))
    assert len(labs) == len(learning["simulations"])
    prints = [_fingerprint(SVG_RE.findall(lab)[0]) for lab in labs]
    assert len(set(prints)) == len(prints), "two labs render the same drawing"


def test_learning_path_shown_to_readers_comes_from_the_data():
    html = _page()
    learning = json.loads(LEARNING.read_text(encoding="utf-8"))
    eyebrow = re.search(r'<p class="eyebrow">([A-ZÁÉÍÓÚÑ ]+(?: → [A-ZÁÉÍÓÚÑ ]+)+)</p>', html)
    assert eyebrow, "the learning path must be visible above the labs"
    steps = [step.strip() for step in eyebrow.group(1).split("→")]
    assert len(steps) == len(learning["learning_path"])


def test_no_orphaned_offline_map_files_are_published():
    """Every published map must still belong to a live route layer."""
    maps = ROOT / "challenges/arquitectura-en-foco/maps"
    routes = json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))
    referenced: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and "maps/" in node:
            referenced.add(node.rsplit("maps/", 1)[-1])

    walk(routes)
    linked = " ".join(
        (ROOT / name).read_text(encoding="utf-8", errors="ignore")
        for name in ("challenges/arquitectura-en-foco/index.html", "sw.js")
    )
    orphans = sorted(
        path.name for path in maps.iterdir() if path.name not in referenced and path.name not in linked
    )
    assert not orphans, f"published map files no route points at: {orphans}"


def test_published_pages_have_no_duplicate_element_ids():
    """Duplicated ids silently break getElementById and assistive technology."""
    pages = [PAGE, WIKI, ROOT / "challenges/arquitectura-en-foco/field-card.html",
             ROOT / "challenges/arquitectura-en-foco/iphone-maps.html"]
    for path in pages:
        found = re.findall(r'\sid="([^"]+)"', path.read_text(encoding="utf-8"))
        duplicates = sorted({name for name in found if found.count(name) > 1})
        assert not duplicates, f"{path.name} repeats ids: {duplicates}"
