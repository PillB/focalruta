"""Every page a reader opens speaks Spanish, and says so where it does not (V12).

The red team found English on the contest pages that the word list in
`reading_floor.ENGLISH_UI` could not see: six scene subtitles printed from an English
identifier ("Decisive Motion In Designed Ramp"), six claims on the techniques guide copied
from English notes, and English video titles a screen reader would read with a Spanish
voice. These tests read every published page for English prose outside `lang="en"`, and
check that each scene mechanism has a Spanish name.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_architecture_pages  # noqa: E402
import reading_floor  # noqa: E402

DIST = ROOT / "dist" / "canon6d_sota_hosted"
CHALLENGE = ROOT / "challenges" / "arquitectura-en-foco"
PAGES = sorted(p for p in DIST.rglob("*.html") if p.name != "FocalRuta_STANDALONE.html") + [
    ROOT / "index.html", ROOT / "field_card.html", *sorted((ROOT / "plans").glob("plan_*.html")), *sorted(CHALLENGE.rglob("*.html"))]
LOCATIONS = ROOT / "architectural_photography" / "research" / "locations"


def test_v12_english_prose_is_told_from_spanish():
    english = ["Background luminance, distance, edges and clutter change figure-ground separation and perceived depth.",
               "How to use metering the RIGHT WAY.", "Why some photos look 3D (and yours don’t)."]
    spanish = ["La luminancia, la distancia, los bordes y el desorden del fondo cambian la separación figura-fondo.",
               "Funciona sin conexión una vez cargada.", "Guarda la tarjeta offline y usa el zoom de 35 a 80 mm.",
               "Canon Camera Museum · EF 35mm f/2 IS USM"]
    assert [reading_floor.english_prose(text) for text in english] == [True] * 3
    assert [reading_floor.english_prose(text) for text in spanish] == [False] * 4


def test_v12_an_element_marked_english_and_everything_inside_it_is_left_alone():
    html = ('<html lang="es"><body><h3 lang="en">How to use metering the <b>RIGHT</b> WAY.</h3>'
            '<p>Mira <cite lang="en">The definitive Architectural Photography TUTORIAL</cite>.</p>'
            '<p>Read the existing direction of the light before adding equipment.</p><br></body></html>')
    assert reading_floor.english_outside_lang_en(html) == ["Read the existing direction of the light before adding equipment."]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_v12_no_english_prose_outside_lang_en(page):
    assert reading_floor.english_outside_lang_en(page.read_text(encoding="utf-8")) == []


def test_v12_every_scene_mechanism_has_a_spanish_name():
    files = [json.loads((LOCATIONS / name).read_text(encoding="utf-8")) for name in ("verification_cohort.json", "verification_pool.json")]
    mechanisms = {candidate["primary_scene_mechanism"] for data in files
                  for candidate in (data["candidates"] if isinstance(data, dict) else data) if candidate.get("primary_scene_mechanism")}
    assert len(mechanisms) == 6
    assert mechanisms <= generate_architecture_pages.SCENE_MECHANISMS.keys()
    html = (CHALLENGE / "index.html").read_text(encoding="utf-8")
    for mechanism in mechanisms:
        assert mechanism.replace("_", " ").title() not in html
        assert generate_architecture_pages.SCENE_MECHANISMS[mechanism] in html
