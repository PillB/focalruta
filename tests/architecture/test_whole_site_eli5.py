"""Whole-site editorial contract: every public entry point explains itself before asking for action."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def _text(path: Path) -> str:
    return re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", path.read_text(encoding="utf-8"), flags=re.S | re.I)


def test_master_has_plain_language_orientation_panel():
    html = _text(ROOT / "index.html")
    assert 'id="eli5-orientation"' in html
    assert "Qué vas a hacer" in html
    assert "Qué significa" in html
    assert "Si algo falla" in html


def test_plan_pages_explain_controls_before_the_first_toggle():
    pages = sorted((ROOT / "plans").glob("plan_*.html"))
    assert pages
    for page in pages:
        html = _text(page)
        intro = html.find('id="plan-orientation"')
        first_control = min(x for x in (html.find('id="toggle-human"'), html.find('id="toggle-day"')) if x >= 0)
        assert 0 <= intro < first_control, page.name
        assert "Qué cambia" in html and "Cómo comprobarlo" in html and "Si no funciona" in html


def test_public_visualizations_have_a_caption_or_nearby_explanation():
    paths = [ROOT / "index.html", ROOT / "field_card.html", *sorted((ROOT / "challenges").rglob("*.html"))]
    for path in paths:
        html = _text(path)
        for match in re.finditer(r"<svg\b[^>]*role=\"img\"[^>]*>", html, flags=re.I):
            end = html.find("</svg>", match.end())
            window = html[match.start() : end + 6 if end >= 0 else match.end() + 600]
            following = html[end + 6 : end + 500] if end >= 0 else ""
            assert "aria-label" in match.group(0) or "aria-labelledby" in match.group(0), f"missing label: {path}"
            assert ("<title>" in window or "<figcaption" in window or "Diagrama" in following
                    or "Visualización" in following or "Síntesis causal" in following or "geometría" in following
                    or "Geometría peatonal" in html), path


def test_glossary_defines_operational_terms_in_master():
    html = _text(ROOT / "index.html")
    for term in ("PDC", "ISO", "KML", "GeoJSON", "histograma"):
        assert term in html, term
    assert "profundidad de campo" in html.lower()
