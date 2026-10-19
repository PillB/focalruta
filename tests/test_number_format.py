"""V20: numbers are written the way Peru reads them, on every page the site ships.

es-PE in CLDR, like the RAE's Ortografía (2010), takes the point as the decimal
mark, and a unit symbol stands one space from its number. The pages mixed both:
gear.js and the plan notes wrote "0,3 pasos" and "2,5 m" beside the optics lab's
"0.24 m" and the plan pages' "Distancia: 2.5m" (red team spot check on PR #20).

These tests read the text of the published pages; the browser QA reads the same
check on the text JavaScript writes, in every state (reading_floor.numbers_in).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from reading_floor import numbers_in  # noqa: E402
from test_home_page import ShownText  # noqa: E402

DIST = ROOT / "dist" / "canon6d_sota_hosted"
# The standalone copy is the home page with its images inside; index.html stands for it.
PAGES = sorted(path for path in DIST.rglob("*.html") if path.name != "FocalRuta_STANDALONE.html")


def text_of(path: Path) -> str:
    parser = ShownText()
    parser.feed(path.read_text(encoding="utf-8"))
    return " ".join(parser.parts)


def test_v20_the_scan_sees_a_decimal_comma_and_a_glued_unit_and_nothing_else():
    """Guard against a scan that passes because it reads nothing, or flags what is right."""
    sample = "a 1,5 m · Distancia: 2.5m · ≈0,03 mm · 1,234 lectores · EF 35mm f/1.8 · 2.5 m · 12:30 · 1/2000 s"
    assert numbers_in(sample) == ["1,5", "0,03", "2.5m"]


def test_v20_the_scan_sees_seconds_millimetres_and_long_decimals_but_not_lens_names():
    """Red team on PR #21, F5: the scan missed "0,125", "2.5s" and "5mm", and the site had
    "0,030 mm", "1/2000s", "(24mm)" and "23.9mm". A lens keeps its name: the maker's
    "EF 35mm f/2", "XF 35mmF2", and the kit's 35mm, 50mm, 85mm and 35–80mm."""
    sample = ("c = 0,030 mm · 0,125 · 1/2000s congelado · 5–15s · 2.5s · (24mm) · 35.8 × 23.9mm · "
              "Canon EF 35mm f/2 IS USM · EF 35–80mm f/4–5.6 · XF 35mmF2 · el 85mm a f/8 · 35-80mm @50 · 1/2000 s · 24 mm")
    assert numbers_in(sample) == ["0,030", "0,125", "2000s", "15s", "2.5s", "24mm", "23.9mm"]


@pytest.mark.parametrize("page", PAGES, ids=lambda path: path.relative_to(DIST).as_posix())
def test_v20_every_published_page_writes_numbers_the_peruvian_way(page):
    assert numbers_in(text_of(page)) == []


def test_v20_the_diagrams_write_numbers_the_peruvian_way(tmp_path, monkeypatch):
    """Every label drawn on a plan's diagrams, both subjects. The diagrams are redrawn by
    hand (matplotlib is not in CI), so this runs where they are drawn."""
    pytest.importorskip("matplotlib")
    import matplotlib.axes
    import generate_diagrams
    from plans_data import PLANS

    drawn = []
    real_text = matplotlib.axes.Axes.text
    monkeypatch.setattr(matplotlib.axes.Axes, "text", lambda ax, x, y, s, *a, **k: drawn.append(str(s)) or real_text(ax, x, y, s, *a, **k))
    plan = PLANS[0]
    for shot in plan["shots"][:3]:
        for variant in ("dog", "human"):
            generate_diagrams.render_diagram(shot, plan, variant, str(tmp_path / f"{shot['id']}_{variant}.png"))
    assert any("zona nítida" in label for label in drawn), "the sharp zone label was not drawn"
    assert numbers_in(" · ".join(drawn)) == []
