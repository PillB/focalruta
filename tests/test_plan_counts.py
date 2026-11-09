"""W08: a new plan needs only its data and its diagrams.

The copy counted six plans by hand, and every browser suite carried the letters "abcdef".
These tests count from the data, and build the site once with a seventh plan to show it
reaches every page, the field card, the offline pack, the sitemap and the checks.
"""
from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import plan_counts  # noqa: E402

DATA = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
DIST = ROOT / "dist" / "canon6d_sota_hosted"
SEVEN = {"plans": 7, "shots": 70, "diagrams": 140, "all_diagrams": 151}


def test_w08_every_total_follows_the_data_and_nothing_else_moves():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    seven = plan_counts.fill(page, SEVEN)
    for phrase in ("Siete rutas por Lima", "📷 7 planes", "🎯 70 tomas", "🎨 140 diagramas", "Ver los 7 planes",
                   "7 opciones:", "7 planes alternativos", "= 140 diagramas", "7 planes de sesión",
                   "70 tomas planificadas", "70 tomas en siete rutas", "los siete planes con sus 151 diagramas"):
        assert phrase in seven, phrase
    for gone in ("Seis rutas", "6 planes", "60 tomas", "120 diagramas", "131 diagramas", "seis planes"):
        assert gone not in seven, gone
    # One plan's own size and every other number stay as written.
    for kept in ("Planifica 10 tomas", "× 10 tomas × 2 sujetos", "EV 7 a 8", "rosca de 67 mm"):
        assert page.count(kept) == seven.count(kept), kept
    assert plan_counts.fill(seven, SEVEN) == seven
    assert plan_counts.fill(seven, plan_counts.counts(DATA)) == page


@pytest.mark.parametrize("name", ["index.html", "field_card.html", "manifest.webmanifest"])
def test_w08_the_shipped_pages_count_what_the_data_holds(name):
    c = plan_counts.counts(DATA)
    shipped = (DIST / name).read_text(encoding="utf-8")
    assert plan_counts.fill(shipped, c) == shipped
    word = plan_counts.number_word(c["plans"])
    assert f"{word} rutas" in shipped.lower() or f"{word} planes" in shipped.lower(), name


def test_w08_counts_are_written_in_words_up_to_twenty():
    assert [plan_counts.number_word(n) for n in (2, 6, 7, 16, 20)] == ["dos", "seis", "siete", "dieciséis", "veinte"]
    assert plan_counts.number_word(21) == "21" and plan_counts.number_word(7, capital=True) == "Siete"


# --- one build with a seventh plan -------------------------------------------------------

IGNORE = shutil.ignore_patterns(".git", "node_modules", "dist", "__pycache__", ".pytest_cache")
PLAN_G = '''
import copy as _copy
PLAN_G = _copy.deepcopy(PLAN_A)
PLAN_G["id"] = "plan_g"
PLAN_G["name"] = "Plan de prueba G"
for _shot in PLAN_G["shots"]:
    _shot["id"] = "G" + _shot["id"][1:]
PLANS.append(PLAN_G)
'''


@pytest.fixture(scope="module")
def seventh(tmp_path_factory):
    """The repository with a plan G (plan A's shots under new ids), built from scratch."""
    sandbox = tmp_path_factory.mktemp("seventh") / "repo"
    shutil.copytree(ROOT, sandbox, ignore=IGNORE)
    shutil.copytree(DIST, sandbox / "dist" / "canon6d_sota_hosted", ignore=shutil.ignore_patterns("__pycache__"))
    data = sandbox / "scripts" / "plans_data.py"
    text = data.read_text(encoding="utf-8")
    anchor = "\nPLANS = [PLAN_A, PLAN_B, PLAN_C, PLAN_D, PLAN_E, PLAN_F]\n"
    assert anchor in text
    data.write_text(text.replace(anchor, anchor + PLAN_G, 1), encoding="utf-8")
    for png in (sandbox / "diagrams").glob("plan_a_*.png"):
        shutil.copy(png, png.with_name(png.name.replace("plan_a_A", "plan_g_G")))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    run = subprocess.run([sys.executable, "scripts/regenerate_all.py"], cwd=sandbox, env=env,
                         capture_output=True, text=True, timeout=1500)
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-3000:]
    return sandbox


@pytest.mark.timeout(1800)
def test_w08_a_seventh_plan_reaches_every_page_and_check(seventh):
    dist = seventh / "dist" / "canon6d_sota_hosted"
    assert (seventh / "plans" / "plan_g.html").is_file() and (dist / "plans" / "plan_g.html").is_file()
    home = (dist / "index.html").read_text(encoding="utf-8")
    for phrase in ("Siete rutas por Lima", "📷 7 planes", "🎯 70 tomas", "🎨 140 diagramas", "Ver los 7 planes"):
        assert phrase in home, phrase
    assert not re.search(r"\b6 planes\b|Seis rutas|\b60 tomas\b|\b120 diagramas\b", home)
    card = (dist / "field_card.html").read_text(encoding="utf-8")
    assert 'value="plan_g"' in card and "los siete planes" in card
    assert "plans/plan_g.html" in card  # the offline pack keeps the new plan
    assert "plan_g.html" in (dist / "sitemap.xml").read_text(encoding="utf-8")
    assert '"plan_g"' in (dist / "data" / "plans_embedded.js").read_text(encoding="utf-8")
    assert "Siete rutas" in (dist / "manifest.webmanifest").read_text(encoding="utf-8")
    letters = subprocess.run([sys.executable, "-c", "import qa_matrix;print(''.join(qa_matrix.PLAN_LETTERS))"],
                             cwd=seventh / "scripts", capture_output=True, text=True, check=True).stdout.strip()
    assert letters == "abcdefg"
