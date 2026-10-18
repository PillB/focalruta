"""The field card shows each plan's exact settings for the light you are in.

Step 3 of the plan Pablo approved: field use first. The old card listed ten
generic starting values per technique, in 8-11 px type, half in English
("Field Card", "Eye-level", "shutter", "FG/BG"), with 21 px checkboxes, so in
the field the reader still had to open a plan page to know what to dial in.

Requirements:
- V01 every word a reader sees on the card is Spanish; camera labels stay as
  the 6D prints them (ONE SHOT, AI SERVO, Tv, Av, MF).
- V02 for every plan, shot and light slot the card shows that slot's lens,
  aperture, shutter, ISO and ND filter, and marks slots that cannot be shot.
- V03 no text smaller than 12 px, on the card or in the home page's copy of it.
- V04 a packing list per plan names every lens, ND filter (with its thread)
  and support the plan's shots need.
- V05 the home page embeds exactly the card that generate_field_card.py
  builds, through the regeneration entrypoint.
- V06 the light slots and each shot's time window follow the ephemeris.
"""
from __future__ import annotations

import html as html_text
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CARD = ROOT / "field_card.html"
# The copy that ships: a build step could break it alone.
CARDS = (CARD, ROOT / "dist" / "canon6d_sota_hosted" / "field_card.html")
FRAGMENT = ROOT / "data" / "field_card_fragment.html"
CARD_CSS = ROOT / "data" / "field_card.css"
CARD_JS = ROOT / "data" / "field_card.js"
DATA = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
SLOTS = ("day", "afternoon", "night")

# English a reader could meet on the old card. Matched without case.
ENGLISH = re.compile(
    r"\b(?:field card|eye-level|pre-?flight|shutter|dof|burst|streak|blue hour|light ?painting|zooming"
    r"|background|foreground|panning|reset|home|building lab|session|tips?)\b",
    re.I,
)
# Mixed-case camera modes are a translation slip: the 6D prints them in capitals.
MIXED_CASE_CAMERA = re.compile(r"\b(?:One Shot|AI Servo|AI Focus)\b")
INITIALS = re.compile(r"\b(?:FG|BG)\b")


class Blocks(HTMLParser):
    """Collect the text of every element carrying data-slot, keyed by plan/shot/slot."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict]] = []
        self.blocks: dict[tuple[str, str, str], dict] = {}
        self.current = None
        self.text_by_class: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("data-slot") and attrs.get("data-shot"):
            key = (attrs["data-plan"], attrs["data-shot"], attrs["data-slot"])
            self.current = self.blocks.setdefault(key, {"classes": attrs.get("class", ""), "parts": {}})
            self.stack.append((tag, {"block": True}))
            return
        css = (attrs.get("class") or "").split()
        self.stack.append((tag, {"field": next((c for c in css if c.startswith("fc-v-")), None)}))

    def handle_endtag(self, tag):
        while self.stack:
            open_tag, info = self.stack.pop()
            if info.get("block"):
                self.current = None
            if open_tag == tag:
                break

    def handle_data(self, data):
        if self.current is None:
            return
        for _tag, info in reversed(self.stack):
            if info.get("field"):
                parts = self.current["parts"]
                parts[info["field"]] = parts.get(info["field"], "") + data
                break


def slot_blocks(html: str) -> dict:
    parser = Blocks()
    parser.feed(html)
    return parser.blocks


def visible_text(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def nd_name(stops: int) -> str:
    return "ND1000" if stops == 10 else f"ND{2 ** stops}"


def test_v01_card_text_is_spanish():
    for page in (*CARDS, FRAGMENT):
        text = visible_text(page.read_text(encoding="utf-8"))
        hits = sorted({m.group(0) for pattern in (ENGLISH, MIXED_CASE_CAMERA, INITIALS) for m in pattern.finditer(text)})
        assert not hits, f"{page.name}: {hits}"


@pytest.mark.parametrize("card", CARDS, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_v02_every_slot_shows_its_exact_settings(card):
    blocks = slot_blocks(card.read_text(encoding="utf-8"))
    wrong = []
    for plan in DATA["plans"]:
        for shot in plan["shots"]:
            for slot in SLOTS:
                setting = shot["settings_by_time"][slot]
                block = blocks.get((plan["id"], shot["id"], slot))
                if block is None:
                    wrong.append(f"{shot['id']} {slot}: missing")
                    continue
                parts = {k: " ".join(v.split()) for k, v in block["parts"].items()}
                expected = f"{setting['aperture']} · {setting['shutter']} · ISO {setting['iso']}"
                if parts.get("fc-v-exposure") != expected:
                    wrong.append(f"{shot['id']} {slot}: {parts.get('fc-v-exposure')!r} != {expected!r}")
                lens = setting["lens"].replace("-", "–").replace("mm", " mm").replace(" @", " a ") + (" mm" if "@" in setting["lens"] else "")
                if parts.get("fc-v-lens") != lens:
                    wrong.append(f"{shot['id']} {slot}: lens {parts.get('fc-v-lens')!r}")
                nd = parts.get("fc-v-nd")
                if setting.get("nd_stops") and nd != f"{nd_name(setting['nd_stops'])} · {setting['nd_stops']} pasos":
                    wrong.append(f"{shot['id']} {slot}: ND {nd!r}")
                if not setting.get("nd_stops") and nd:
                    wrong.append(f"{shot['id']} {slot}: unexpected ND {nd!r}")
    assert len(blocks) == 180 and not wrong, (len(blocks), wrong[:10])


@pytest.mark.parametrize("card", (*CARDS, ROOT / "index.html", ROOT / "dist" / "canon6d_sota_hosted" / "index.html"),
                         ids=lambda p: p.relative_to(ROOT).as_posix())
def test_v02_the_lens_and_the_exposure_read_as_two_words(card):
    """Live check of 56a6e97: the lens and exposure spans touched, so copied or spoken the line
    read "50 mmf/13". The flex layout hid it on screen."""
    html = card.read_text(encoding="utf-8")
    lines = [" ".join(html_text.unescape(re.sub(r"<[^>]+>", "", m)).split()) for m in re.findall(r'<p class="fc-settings">(.*?)</p>', html, flags=re.S)]
    expected = []
    for plan in DATA["plans"]:
        for shot in plan["shots"]:
            for slot in SLOTS:
                s = shot["settings_by_time"][slot]
                lens = s["lens"].replace("-", "–").replace("mm", " mm").replace(" @", " a ") + (" mm" if "@" in s["lens"] else "")
                expected.append(f"{lens} {s['aperture']} · {s['shutter']} · ISO {s['iso']}")
    assert len(lines) == 180 and sorted(lines) == sorted(expected), [line for line in lines if line not in expected][:5]


@pytest.mark.parametrize("card", CARDS, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_v02_slots_that_cannot_be_shot_say_so(card):
    blocks = slot_blocks(card.read_text(encoding="utf-8"))
    for plan in DATA["plans"]:
        for shot in plan["shots"]:
            for slot in SLOTS:
                setting = shot["settings_by_time"][slot]
                block = blocks[(plan["id"], shot["id"], slot)]
                assert ("fc-off" in block["classes"].split()) == (setting.get("viable") is False), (shot["id"], slot)
                assert " ".join(block["parts"].get("fc-v-note", "").split()) == setting["notes"], (shot["id"], slot)


def font_sizes_px(css: str) -> list[tuple[float, str]]:
    """Every font size a rule can resolve to, in CSS px (1rem = 16px)."""
    sizes = []
    for match in re.finditer(r"font(?:-size)?\s*:\s*([^;}]+)", css):
        value = match.group(1)
        if match.group(0).startswith("font:") and not re.search(r"\d", value):
            continue
        lengths = [float(n) * (16 if unit in ("rem", "em") else 1)
                   for n, unit in re.findall(r"(\d*\.?\d+)(px|rem|em)\b", value)]
        if not lengths:
            continue
        resolved = max(lengths) if value.strip().startswith(("max(", "clamp(")) else min(lengths)
        sizes.append((resolved, match.group(0)[:60]))
    return sizes


def test_v03_no_card_text_below_12px():
    css = CARD_CSS.read_text(encoding="utf-8")
    # Print sizes are physical (A4); screens are what the field reader holds.
    screen = re.sub(r"@media print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    small = [rule for size, rule in font_sizes_px(screen) if size < 12]
    assert font_sizes_px(screen) and not small, small


@pytest.mark.parametrize("card", CARDS, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_v03_the_card_pages_style_no_text_below_12px(card):
    css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", card.read_text(encoding="utf-8"), re.S))
    screen = re.sub(r"@media print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    small = [rule for size, rule in font_sizes_px(screen) if size < 12]
    assert font_sizes_px(screen) and not small, small


def test_v03_home_page_copy_of_the_card_has_no_text_below_12px():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    block = index.split("<!-- FIELD CARD CSS START -->", 1)[1].split("<!-- FIELD CARD CSS END -->", 1)[0]
    block = re.sub(r"@media print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", block)
    small = [rule for size, rule in font_sizes_px(block) if size < 12]
    assert not small, small


def packing(html: str) -> dict[str, str]:
    lists = {}
    for match in re.finditer(r'<ul class="fc-pack" data-plan="([^"]+)"[^>]*>(.*?)</ul>', html, re.S):
        lists[match.group(1)] = " ".join(visible_text(match.group(2)).split())
    return lists


def test_v04_packing_list_names_every_filter_lens_and_support_the_plan_needs():
    lists = packing(CARD.read_text(encoding="utf-8"))
    threads = {str(lens["focal"]).replace("-", "–"): lens["filter_mm"] for lens in DATA["gear"]["lenses"]}
    for plan in DATA["plans"]:
        text = lists.get(plan["id"], "")
        settings = [s for shot in plan["shots"] for s in shot["settings_by_time"].values() if s.get("viable") is not False]
        for stops in {s["nd_stops"] for s in settings if s.get("nd_stops")}:
            assert nd_name(stops) in text, (plan["id"], nd_name(stops), text)
        for lens in {s["lens"].split()[0].replace("mm", "").replace("-", "–") for s in settings}:
            assert f"{lens} mm" in text and f"{threads[lens]} mm" in text, (plan["id"], lens, text)
        needs_support = any(re.search(r'"|Bulb', s["shutter"]) for s in settings)
        assert ("Trípode" in text) == needs_support, (plan["id"], text)


def test_v05_home_page_embeds_the_generated_card():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    for source in (FRAGMENT, CARD_CSS, CARD_JS):
        assert source.read_text(encoding="utf-8").strip() in index, f"index.html is out of step with {source.name}"


def test_v05_regeneration_runs_the_card_integration():
    import regenerate_all
    steps = [script for script, _purpose in regenerate_all.CORE]
    assert steps.index("generate_field_card.py") < steps.index("integrate_field_card.py") < steps.index("build_dual_release.py")


# 2026-10-17 in Lima, from the astral 3.2 reference in tests/planner/test_sun_times.py.
SUNRISE, GOLDEN_PM, SUNSET, BLUE_END = 5 * 60 + 42.1, 17 * 60 + 37.3, 18 * 60 + 4.9, 18 * 60 + 26.8
JS_CARD = ROOT / "assets" / "field_card.js"
JS_SUN = ROOT / "assets" / "sun_times.js"


def run_node(expression: str):
    script = (f"global.LimaSun=require({json.dumps(str(JS_SUN))});"
              f"const F=require({json.dumps(str(JS_CARD))});"
              f"const P=LimaSun.dayPlan('2026-10-17');process.stdout.write(JSON.stringify({expression}));")
    return json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_v06_light_slot_follows_the_clock_in_lima():
    times = [4 * 60, SUNRISE + 1, 12 * 60, GOLDEN_PM + 1, SUNSET + 5, BLUE_END + 1, 23 * 60]
    assert run_node(f"{json.dumps(times)}.map(m=>F.slotAt(m,P))") == [
        "night", "day", "day", "afternoon", "afternoon", "night", "night"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_v06_each_scene_gets_the_window_its_light_occurs_in():
    windows = run_node("{golden:F.sceneWindow('antes_ocaso','afternoon',P),blue:F.sceneWindow('tras_ocaso','afternoon',P),"
                       "street:F.sceneWindow('calle_noche','night',P),sun:F.sceneWindow('sol_velado','day',P),"
                       "lamps:F.sceneWindow('interior_casa','night',P)}")
    approx = lambda pair, start, end: abs(pair[0] - start) < 2 and (end is None and pair[1] is None or abs(pair[1] - end) < 2)
    assert approx(windows["golden"], GOLDEN_PM, SUNSET)
    assert approx(windows["blue"], SUNSET, BLUE_END)
    assert approx(windows["street"], BLUE_END, None)
    assert approx(windows["sun"], SUNRISE, GOLDEN_PM)
    assert windows["lamps"] is None  # lamp-lit interiors do not wait for the sun


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_v06_lima_clock_reads_the_same_from_any_time_zone():
    script = (f"const F=require({json.dumps(str(JS_CARD))});"
              "process.stdout.write(JSON.stringify(F.limaMinutes(Date.parse('2026-10-17T22:50:00Z'))));")
    for zone in ("Europe/Madrid", "Asia/Tokyo", "America/Lima"):
        env = {"PATH": __import__("os").environ["PATH"], "TZ": zone}
        out = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True, env=env).stdout
        assert json.loads(out) == 17 * 60 + 50, zone
