"""The session mode's shot review: checks, fixes, saved state and the summary.

Requirements W05 (each shot is checked on the camera's screen for sharpness where its
technique needs it, exposure and the plan's own pass criterion), W06 (a failed check names
what to change, the same advice the field card gives for that problem; the review survives
a reload and a damaged store, and the old "✓ Marcar" ticks count as passed) and W07 (the
summary counts passed shots, lists the ones to repeat with their fixes, and names the check
that failed most).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "assets" / "shot_review.js"
PLANS = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))["plans"]
TECHNIQUES = sorted({shot["technique"] for plan in PLANS for shot in plan["shots"]})

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")


def node(expression: str):
    script = f"const R=require({json.dumps(str(JS))});process.stdout.write(JSON.stringify({expression}));"
    return json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)


class Rescue(HTMLParser):
    """The field card's «Cuando la foto no sale» panel: problem title → advice."""

    def __init__(self):
        super().__init__()
        self.inside, self.tag, self.title, self.items = False, None, "", {}

    def handle_starttag(self, tag, attrs):
        if tag == "section" and "fc-panel-rescue" in (dict(attrs).get("class") or ""):
            self.inside = True
        self.tag = tag

    def handle_endtag(self, tag):
        if tag == "section":
            self.inside = False

    def handle_data(self, data):
        if not self.inside or not data.strip():
            return
        if self.tag == "b":
            self.title = data.strip()
        elif self.tag == "p" and self.title:
            self.items[self.title] = data.strip()
            self.title = ""


def rescue_panel() -> dict:
    parser = Rescue()
    parser.feed((ROOT / "field_card.html").read_text(encoding="utf-8"))
    return parser.items


def test_w05_every_technique_in_the_plans_has_its_own_checks_and_fixes():
    """No shot of any plan falls back to the generic question or fix."""
    got = node(f"{json.dumps(TECHNIQUES)}.map(t=>[R.checks(t,'x')[0].question,"
               "R.fixes(t,{s:'no',e:'ok',i:'ok'})[0],R.fixes(t,{s:'ok',e:'ok',i:'no'})[0]])")
    for technique, (question, sharp_fix, intent_fix) in zip(TECHNIQUES, got):
        assert "lo importante está nítido" not in question, technique
        assert sharp_fix != "Revisa el foco y la estabilidad, una sola variable cada vez.", technique
        assert intent_fix != "Cambia una sola variable y repite.", technique
    assert node("R.checks('barrido','✓ sujeto reconocible')[2].question") == "Aprueba si: ✓ sujeto reconocible"


@pytest.mark.parametrize("technique,review,problem", [
    ("poca_pdc", {"s": "ok", "e": "ok", "i": "no"}, "El fondo no se desenfoca"),
    ("barrido", {"s": "ok", "e": "ok", "i": "no"}, "El barrido sale congelado"),
    ("barrido", {"s": "no", "e": "ok", "i": "ok"}, "El barrido sale todo movido"),
    ("lightpainting", {"s": "no", "e": "ok", "i": "ok"}, "De noche la foto vibra"),
    ("larga_exp", {"s": "ok", "e": "over", "i": "ok"}, "Las luces se queman"),
    ("zooming", {"s": "ok", "e": "ok", "i": "no"}, "El efecto zoom no traza rayos"),
])
def test_w06_a_failed_check_gives_the_field_cards_own_advice(technique, review, problem):
    """The review and the field card's rescue panel must not tell the reader two things."""
    advice = rescue_panel()[problem]
    fixes = node(f"R.fixes({json.dumps(technique)},{json.dumps(review)})")
    # The panel opens a problem with its first sentence; the fix carries the same instruction.
    first = re.split(r"(?<=\.)\s", advice)[0]
    assert any(first in fix or fix in advice for fix in fixes), (problem, advice, fixes)


def test_w06_verdicts_follow_the_three_checks():
    cases = node("[R.verdict({s:'ok',e:'ok',i:'ok'}),R.verdict({s:'ok',e:'under',i:'ok'}),R.verdict({s:'no',e:'ok',i:'ok'}),"
                 "R.verdict({s:'ok',e:'ok'}),R.verdict(null),R.verdict({legacy:true}),R.verdict({s:'ok',e:'quemada',i:'ok'})]")
    assert cases == ["ok", "retry", "retry", None, None, "ok", None]
    # one fix per failed check, exposure over and under each with its own
    assert len(node("R.fixes('congelado',{s:'no',e:'over',i:'no'})")) == 3
    assert node("R.fixes('congelado',{s:'ok',e:'over',i:'ok'})") != node("R.fixes('congelado',{s:'ok',e:'under',i:'ok'})")


@pytest.mark.parametrize("stored", ["", "{", "null", "42", '"x"', '{"0":true}', "[1,2,3]", '[{"s":5}]',
                                    '[{"s":"ok","e":"ok","i":"ok","x":"<img src=x onerror=alert(1)>"}]'])
def test_w06_a_damaged_store_never_stops_the_review(stored):
    states = node(f"R.readState({json.dumps(stored)},10)")
    assert len(states) == 10
    for state in states:
        assert state is None or set(state) <= {"s", "e", "i", "legacy"}


def test_w06_old_ticks_count_as_passed_and_new_reviews_are_kept():
    states = node('R.readState(JSON.stringify([true,false,{s:"ok",e:"over",i:"ok"},{s:"no"}]),10)')
    assert states[0] == {"legacy": True}
    assert states[1] is None
    assert states[2] == {"s": "ok", "e": "over", "i": "ok"}
    assert states[3] == {"s": "no"}  # half answered: kept, not yet a verdict
    assert node('R.verdict(R.readState(JSON.stringify([{s:"no"}]),1)[0])') is None


def test_w07_the_summary_counts_lists_and_names_the_weakest_check():
    techniques = [shot["technique"] for shot in PLANS[0]["shots"]]
    states = [{"s": "ok", "e": "ok", "i": "ok"}, {"legacy": True}, {"s": "no", "e": "ok", "i": "ok"},
              {"s": "no", "e": "under", "i": "ok"}, {"s": "ok", "e": "ok", "i": "no"}, None, {"s": "ok"}, None, None, None]
    got = node(f"R.summary({json.dumps(states)},{json.dumps(techniques)})")
    assert got["approved"] == 2
    assert [item["n"] for item in got["retry"]] == [2, 3, 4]
    assert got["pending"] == [5, 6, 7, 8, 9]
    assert got["weakest"] == "s" and got["label"] == "nitidez" and "100 %" in got["advice"]
    # a review saved again keeps the old tick's flag
    assert node('R.readState(JSON.stringify([{legacy:true}]),1)[0]') == {"legacy": True}
    assert [len(item["fixes"]) for item in got["retry"]] == [1, 2, 1]
    empty = node(f"R.summary([],{json.dumps(techniques)})")
    assert empty["approved"] == 0 and empty["weakest"] is None and len(empty["pending"]) == 10
