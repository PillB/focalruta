"""Other cameras and lenses get settings equivalent to the plan (V13 to V15).

Step 3 of the plan Pablo approved, public half: the gear becomes configurable,
with the Canon 6D kit as the default. Until now every setting assumed the 6D
and its four lenses, so a reader with an APS-C body or a kit zoom had to work
out the crop factor, the equivalent aperture and the exposure by hand.

Requirements:
- V13 assets/gear.js adapts each planned setting to the reader's gear and the
  result is physically equivalent: the same framing (field width at the
  subject), the same depth of field in proportion to the subject distance
  (thin lens, circle of confusion scaled to the sensor), the same exposure,
  and the plan's creative variable unchanged (the shutter for motion, the
  aperture's depth of field for depth-of-field shots). Where the gear cannot
  do it (a lens that does not open enough, not enough light, no zoom for a
  zoom burst) the result says so.
- V14 the Canon 6D kit is the default and changes nothing.
- V15 the home page offers the gear picker, and the home page, the plan pages
  and the field card all carry the same gear.js.

Every physical check uses scripts/optics_physics.py and the exposure-value
equation, not the arithmetic inside gear.js.
"""
from __future__ import annotations

import itertools
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import exposure_model as em  # noqa: E402
import optics_physics as op  # noqa: E402

GEAR_JS = ROOT / "assets" / "gear.js"
DATA = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
REF_W, REF_COC = 35.8, 0.03
MOTION = {"congelado", "barrido", "fantasma", "lightpainting", "larga_exp", "zooming"}
# A zoom that covers every focal at f/1: only the physics can limit the result.
IDEAL = [{"name": "ideal", "min": 5, "max": 300, "wide": 1, "tele": 1}]
REAL_KITS = {
    "apsc_canon": ({"body": "apsc_canon", "iso": 6400, "lenses": [
        {"name": "18-55", "min": 18, "max": 55, "wide": 3.5, "tele": 5.6}, {"name": "50", "min": 50, "max": 50, "wide": 1.8, "tele": 1.8}]}),
    "m43": ({"body": "m43", "iso": 6400, "lenses": [
        {"name": "14-42", "min": 14, "max": 42, "wide": 3.5, "tele": 5.6}, {"name": "25", "min": 25, "max": 25, "wide": 1.7, "tele": 1.7}]}),
    "full_frame_one_zoom": ({"body": "full_frame", "iso": 12800, "lenses": [
        {"name": "24-105", "min": 24, "max": 105, "wide": 4, "tele": 4}]}),
    "one_inch": ({"body": "one_inch", "iso": 3200, "lenses": [
        {"name": "9-37", "min": 9, "max": 37, "wide": 1.8, "tele": 2.8}]}),
    "apsc_primes_only": ({"body": "apsc", "iso": 12800, "lenses": [
        {"name": "23", "min": 23, "max": 23, "wide": 2, "tele": 2}, {"name": "56", "min": 56, "max": 56, "wide": 1.2, "tele": 1.2}]}),
}
BODY_W = {"canon_6d": 35.8, "full_frame": 36, "apsc_canon": 22.3, "apsc": 23.5, "m43": 17.3, "one_inch": 13.2}


def slot_inputs():
    for plan in DATA["plans"]:
        for shot in plan["shots"]:
            for slot, s in shot["settings_by_time"].items():
                yield {"key": f"{shot['id']}/{slot}", "technique": shot["technique"], "lens": s["lens"], "aperture": s["aperture"],
                       "shutter": s["shutter"], "iso": s["iso"], "nd_stops": s.get("nd_stops", 0), "distance": shot["subject_distance_m"],
                       "viable": s.get("viable", True)}


SLOTS = list(slot_inputs())


def adapt_all(gears: dict) -> dict:
    script = (f"const G=require({json.dumps(str(GEAR_JS))});const slots={json.dumps(SLOTS)};const gears={json.dumps(gears)};"
              "const out={};for(const [name,g] of Object.entries(gears)){out[name]=slots.map(s=>G.adapt(s,g));}"
              "process.stdout.write(JSON.stringify(out));")
    return json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)


def ideal_gears() -> dict:
    return {body: {"body": body, "iso": 51200, "lenses": IDEAL} for body in BODY_W}


@pytest.fixture(scope="module")
def results():
    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    gears = {**ideal_gears(), **REAL_KITS,
             "reference": json.loads(subprocess.run(["node", "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(str(GEAR_JS))}).reference()))"],
                                                     check=True, capture_output=True, text=True).stdout)}
    return gears, adapt_all(gears)


def plan_focal(lens: str) -> float:
    text = lens.replace("–", "-")
    if "@" in text:
        return float(text.split("@")[1])
    head = text.split("mm")[0]
    return float(head.split("-")[1] if "-" in head else head)


def exposure_q(aperture: float, seconds: float, iso: float, nd: float) -> float:
    """log2(N²/t) − log2(ISO/100) + ND: equal values give equally bright pictures of the same scene."""
    return math.log2(aperture * aperture / seconds) - math.log2(iso / 100) + nd


def plan_q(slot: dict) -> float:
    return exposure_q(em.f_number(slot["aperture"]), em.shutter_seconds(slot["shutter"]), slot["iso"], slot["nd_stops"])


def viable(pairs):
    return [(s, r) for s, r in pairs if s["viable"] is not False and r["ok"]]


def framing_errors(slot, r, sensor_w):
    planned = slot["distance"] * REF_W / plan_focal(slot["lens"])
    if "girando" in r["lens"]:  # a zoom burst ends at its tele focal
        return []
    got = r["distance_m"] * sensor_w / r["focal"]
    return [] if abs(math.log(got / planned)) < 0.02 else [f"{slot['key']}: field width {got:.2f} m vs {planned:.2f} m"]


def dof_errors(slot, r, sensor_w):
    """Same sharp zone in proportion to the distance: near and far limits scale by d'/d."""
    if r["flags"]["apertureLimited"] or r["flags"]["stoppedDown"] or r["flags"]["opened"]:
        return []
    f0, n0, d0 = plan_focal(slot["lens"]), em.f_number(slot["aperture"]), slot["distance"]
    planned = op.depth_of_field(f0, n0, d0, REF_COC)
    got = op.depth_of_field(r["focal"], r["f_number"], r["distance_m"], REF_COC * sensor_w / REF_W)
    scale = r["distance_m"] / d0
    errors = []
    # Apertures come in third stops, so the hyperfocal distance can land up to a sixth of a stop away.
    if abs(math.log(got["hyperfocal"] / (planned["hyperfocal"] * scale))) > math.log(2 ** (1 / 6)) * 1.05:
        errors.append(f"{slot['key']}: hyperfocal {got['hyperfocal']:.1f} m vs {planned['hyperfocal'] * scale:.1f} m")
    if abs(math.log(got["near"] / (planned["near"] * scale))) > 0.15:
        errors.append(f"{slot['key']}: near {got['near']:.2f} m vs {planned['near'] * scale:.2f} m")
    if math.isinf(planned["far"]) and not math.isinf(got["far"]):
        errors.append(f"{slot['key']}: sharp to {got['far']:.0f} m, the plan is sharp to infinity")
    return errors


@pytest.mark.parametrize("body", list(BODY_W))
def test_v13_an_unlimited_lens_reproduces_framing_depth_and_exposure(results, body):
    gears, out = results
    pairs = viable(zip(SLOTS, out[body]))
    assert len(pairs) >= 140
    errors = []
    for slot, r in pairs:
        errors += framing_errors(slot, r, BODY_W[body])
        errors += dof_errors(slot, r, BODY_W[body])
        q = exposure_q(r["f_number"], r["seconds"], r["iso"], r["nd_stops"])
        if abs(q - plan_q(slot) - r["flags"]["short"]) > 1 / 3 + 1e-9:
            errors.append(f"{slot['key']}: exposure off by {q - plan_q(slot):+.2f} EV")
    assert errors == []


def test_v13_exposure_holds_beyond_the_plans_on_a_grid_of_settings():
    """The plans rarely make the gear add or drop an ND filter, so the exposure is also checked on a grid of
    settings, techniques, filters and ISO limits that forces every branch: more light, less light, ND on, ND off."""
    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    grid = [{"key": f"{tech} {ap} {sh} ISO {iso} ND {nd}", "technique": tech, "lens": "50mm", "aperture": ap, "shutter": sh,
             "iso": iso, "nd_stops": nd, "distance": 4, "viable": True}
            for tech, ap, sh, iso, nd in itertools.product(("poca_pdc", "mucha_pdc", "fantasma", "barrido", "congelado"),
                                                           ("f/2", "f/4", "f/8", "f/16"), ("1/2000", "1/250", "1/30", '1"', '8"'),
                                                           (100, 400, 1600, 6400), (0, 3, 6))]
    gears = {f"{body} ISO {limit}": {"body": body, "iso": limit, "lenses": IDEAL} for body in BODY_W for limit in (1600, 51200)}
    script = (f"const G=require({json.dumps(str(GEAR_JS))});const slots={json.dumps(grid)};const gears={json.dumps(gears)};"
              "const out={};for(const [name,g] of Object.entries(gears)){out[name]=slots.map(s=>G.adapt(s,g));}"
              "process.stdout.write(JSON.stringify(out));")
    out = json.loads(subprocess.run(["node", "-"], input=script, check=True, capture_output=True, text=True).stdout)
    errors = []
    for name, rows in out.items():
        for slot, r in zip(grid, rows):
            q = exposure_q(r["f_number"], r["seconds"], r["iso"], r["nd_stops"])
            if abs(q - plan_q(slot) - r["flags"]["short"]) > 1 / 3 + 1e-9:
                errors.append(f"{name} · {slot['key']}: off by {q - plan_q(slot):+.2f} EV")
    assert sum(len(rows) for rows in out.values()) == 14400 and errors == []


@pytest.mark.parametrize("kit", list(REAL_KITS))
def test_v13_real_kits_stay_within_their_limits_and_say_what_they_lose(results, kit):
    gears, out = results
    gear = gears[kit]
    errors = []
    for slot, r in viable(zip(SLOTS, out[kit])):
        lens = next((l for l in gear["lenses"] if l["name"] == r["lens_name"]), None)
        if lens is None or not lens["min"] - 0.01 <= r["focal"] <= lens["max"] + 0.01:
            errors.append(f"{slot['key']}: {r['focal']} mm is not on {r['lens_name']}")
            continue
        share = 0 if lens["max"] == lens["min"] else (r["focal"] - lens["min"]) / (lens["max"] - lens["min"])
        if r["f_number"] < lens["wide"] + share * (lens["tele"] - lens["wide"]) - 0.06 or r["f_number"] > 22:
            errors.append(f"{slot['key']}: f/{r['f_number']} outside the lens")
        if not 100 <= r["iso"] <= gear["iso"]:
            errors.append(f"{slot['key']}: ISO {r['iso']} outside 100-{gear['iso']}")
        if r["seconds"] < 1 / 4000 - 1e-9:
            errors.append(f"{slot['key']}: {r['shutter']} faster than the body")
        errors += framing_errors(slot, r, BODY_W[gear["body"]])
        q = exposure_q(r["f_number"], r["seconds"], r["iso"], r["nd_stops"])
        if abs(q - plan_q(slot) - r["flags"]["short"]) > 1 / 3 + 1e-9:
            errors.append(f"{slot['key']}: exposure off by {q - plan_q(slot):+.2f} EV")
        if r["flags"]["apertureLimited"] and not any("no abre tanto" in n for n in r["notes"]):
            errors.append(f"{slot['key']}: lens limit not explained")
        if r["flags"]["short"] and not any("Faltan" in n for n in r["notes"]):
            errors.append(f"{slot['key']}: missing light not explained")
    assert errors == []


@pytest.mark.parametrize("kit", ["apsc_canon", "m43", "one_inch", "full_frame_one_zoom", "apsc_primes_only"])
def test_v13_motion_shots_keep_the_planned_shutter(results, kit):
    gears, out = results
    changed = [f"{s['key']}: {s['shutter']} -> {r['shutter']}" for s, r in viable(zip(SLOTS, out[kit]))
               if s["technique"] in MOTION and em.shutter_seconds(r["shutter"]) != pytest.approx(em.shutter_seconds(s["shutter"]), rel=0.01)]
    assert changed == []


def test_v13_depth_of_field_shots_keep_their_depth_of_field_when_the_lens_allows(results):
    gears, out = results
    errors = []
    for kit in REAL_KITS:
        for slot, r in viable(zip(SLOTS, out[kit])):
            if slot["technique"] in ("mucha_pdc", "poca_pdc"):
                errors += dof_errors(slot, r, BODY_W[gears[kit]["body"]])
    assert errors == []


def test_v13_a_zoom_burst_without_a_zoom_says_so(results):
    gears, out = results
    zooming = [r for s, r in zip(SLOTS, out["apsc_primes_only"]) if s["technique"] == "zooming" and s["viable"] is not False]
    assert zooming and all(not r["ok"] and "zoom" in r["reason"] for r in zooming)


def test_v14_the_canon_6d_kit_changes_nothing(results):
    gears, out = results
    changed = []
    for slot, r in zip(SLOTS, out["reference"]):
        if not r["ok"]:
            changed.append(f"{slot['key']}: {r['reason']}")
            continue
        same = (r["aperture"] == slot["aperture"] and em.shutter_seconds(r["shutter"]) == pytest.approx(em.shutter_seconds(slot["shutter"]), rel=0.01)
                and r["iso"] == slot["iso"] and r["nd_stops"] == slot["nd_stops"] and abs(r["distance_m"] - slot["distance"]) < 1e-9 and not r["notes"])
        if not same:
            changed.append(f"{slot['key']}: {r['lens']} {r['aperture']} {r['shutter']} ISO {r['iso']} {r['notes']}")
    assert changed == []


def test_v14_the_default_gear_shows_no_extra_line():
    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    script = (f"const G=require({json.dumps(str(GEAR_JS))});const s={json.dumps(SLOTS[0])};"
              "process.stdout.write(JSON.stringify([G.lineHtml(s,G.reference()),G.lineHtml(s,{body:'m43',iso:6400,lenses:G.reference().lenses})]));")
    default_line, other_line = json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)
    assert default_line == "" and "Con tu equipo" in other_line


def inline_script(page: Path, script_id: str) -> str:
    text = page.read_text(encoding="utf-8")
    start = text.index(f'<script id="{script_id}">') + len(f'<script id="{script_id}">')
    return text[start:text.index("</script>", start)].strip()


@pytest.mark.parametrize("page", [ROOT / "index.html", ROOT / "field_card.html", *sorted((ROOT / "plans").glob("plan_*.html"))], ids=lambda p: p.name)
def test_v15_every_page_carries_the_same_gear_script(page):
    assert inline_script(page, "gear-js") == GEAR_JS.read_text(encoding="utf-8").strip()


def test_v15_home_page_offers_the_gear_picker_with_every_body():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'id="gear-config"' in page and 'id="gear-body"' in page and 'id="gear-reset"' in page
    assert "lineFor(shot" in page, "shot cards must show the adapted line"


def test_v15_a_stored_lens_cannot_put_markup_on_the_page():
    """The gear is read back from localStorage and drawn with innerHTML, so a damaged or crafted entry must not inject markup."""
    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    stored = {"body": "apsc_canon", "iso": "6400", "lenses": [
        {"name": '<img src=x onerror="alert(1)">50', "min": 50, "max": 50, "wide": 1.8, "tele": 1.8},
        {"name": "zoom", "min": "18<b>", "max": 55, "wide": 3.5, "tele": 5.6},
        None,
    ]}
    script = (f"global.localStorage={{getItem:()=>{json.dumps(json.dumps(stored))}}};const G=require({json.dumps(str(GEAR_JS))});"
              f"const g=G.load();process.stdout.write(JSON.stringify([g,G.lineHtml({json.dumps(SLOTS[0])},g)]));")
    gear, line = json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)
    assert gear["iso"] == 6400 and [lens["min"] for lens in gear["lenses"]] == [50]
    assert "<" not in gear["lenses"][0]["name"] and '"' not in gear["lenses"][0]["name"]
    assert "<img" not in line and "Con tu equipo" in line
