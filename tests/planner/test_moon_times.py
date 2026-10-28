"""W09: the light panel says when the moon rises and sets, where, and how much of it is lit.

Night shots (light painting, long exposures, the blue hour after sunset) change with the
moon: a full moon adds light to the scene and can stand in the frame, a new moon adds none.
No part of the site said so. The references are the US Naval Observatory's own tables for
San Isidro (tests/fixtures/usno_moon_lima.json: its rise/set service and, at each rise and
set minute, its altitude/azimuth service), fetched once and stored, so the test needs no
network. Both twins, scripts/moon_times.py and the moon half of assets/sun_times.js, are held
to them, and the panel's words are held to the Python twin.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import moon_times as mt  # noqa: E402

USNO = json.loads((ROOT / "tests/fixtures/usno_moon_lima.json").read_text(encoding="utf-8"))
JS = ROOT / "assets" / "sun_times.js"
RISE_SET_MIN = 2.0
BEARING_DEG = 0.25
LIT_POINTS = 2


def minutes(hhmm: str) -> int:
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


@pytest.mark.parametrize("row", USNO["days"], ids=lambda row: row["date"])
def test_w09_moonrise_and_moonset_match_the_naval_observatory(row):
    ours = mt.moon_day(date.fromisoformat(row["date"]))
    for event in ("rise", "set"):
        if event not in row:
            assert ours[event] is None, (row["date"], event, ours[event])
            continue
        assert ours[event] == pytest.approx(minutes(row[event]["time"]), abs=RISE_SET_MIN), (row["date"], event)
        assert abs((ours[f"{event}_azimuth"] - row[event]["zn"] + 180) % 360 - 180) < BEARING_DEG, (row["date"], event)


@pytest.mark.parametrize("row", USNO["days"], ids=lambda row: row["date"])
def test_w09_the_lit_fraction_and_its_direction_match_the_naval_observatory(row):
    noon = mt.moon_at(date.fromisoformat(row["date"]), 12 * 60)
    assert abs(round(100 * noon["fraction"]) - row["fracillum_percent"]) <= LIT_POINTS, (row["date"], noon)
    if row["curphase"].startswith(("Waxing", "Waning")):
        assert noon["waxing"] == row["curphase"].startswith("Waxing"), (row["date"], noon)


def test_w09_phase_names_follow_the_lit_fraction():
    assert [mt.phase_name(f, w) for f, w in ((0.01, True), (0.3, True), (0.5, True), (0.8, True), (0.99, False),
                                              (0.8, False), (0.5, False), (0.2, False))] == [
        "luna nueva", "luna creciente", "cuarto creciente", "gibosa creciente", "luna llena",
        "gibosa menguante", "cuarto menguante", "luna menguante"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_w09_the_browser_twin_gives_the_python_numbers():
    days = [row["date"] for row in USNO["days"]]
    script = (f"const S=require({json.dumps(str(JS))});const out={{}};"
              f"for (const d of {json.dumps(days)}) out[d]={{day:S.moonDay(d),noon:S.moonAt(d,720)}};"
              "process.stdout.write(JSON.stringify(out));")
    shown = json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)
    for day, js in shown.items():
        py_day, py_noon = mt.moon_day(date.fromisoformat(day)), mt.moon_at(date.fromisoformat(day), 720)
        for key, value in py_day.items():
            assert (js["day"][key] is None) == (value is None) and (value is None or js["day"][key] == pytest.approx(value, abs=0.01)), (day, key)
        assert js["noon"]["fraction"] == pytest.approx(py_noon["fraction"], abs=1e-6) and js["noon"]["phase"] == py_noon["phase"]


PANEL = (ROOT / "index.html").read_text(encoding="utf-8")
PANEL = PANEL[PANEL.index("<!-- LIMA_SUN_PANEL_START -->"):PANEL.index("<!-- LIMA_SUN_PANEL_END -->")]


def test_w09_the_light_panel_shows_the_moon_without_javascript_too():
    script = PANEL[PANEL.rindex("<script>"):]
    assert "S.moonDay(" in script and "S.moonAt(" in script and 'id="moon-read"' in PANEL
    noscript = re.search(r'<noscript><p id="sun-noscript".*?</noscript>', PANEL, re.S).group(0)
    assert "luna" in noscript.lower()
