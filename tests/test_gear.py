"""Other cameras and lenses get settings equivalent to the plan (V13 to V15).

Step 3 of the plan Pablo approved, public half: the gear becomes configurable,
with the Canon 6D kit as the default. Until now every setting assumed the 6D
and its four lenses, so a reader with an APS-C body or a kit zoom had to work
out the crop factor, the equivalent aperture and the exposure by hand.

Requirements:
- V13 assets/gear.js adapts each planned setting to the reader's gear and the
  result is physically equivalent: the same framing (field width at the
  subject; a zoom burst runs over the plan's angles of view and ends on its
  framing), the same depth of field in proportion to the subject distance
  (thin lens, circle of confusion scaled to the sensor), the same exposure,
  and the plan's creative variable unchanged (the shutter for motion, the
  aperture's depth of field for depth-of-field shots). Where the gear cannot
  do it (a lens that does not open or close enough, not enough light, no zoom
  that covers the zoom burst, a shutter too slow to hold by hand at the
  reader's equivalent focal) the result says so.
- V14 the Canon 6D kit is the default and changes nothing.
- V15 the home page offers the gear picker, and the home page, the plan pages
  and the field card all carry the same gear.js. What is stored is read back
  within the picker's own options, once per change.

Every physical check uses scripts/optics_physics.py, scripts/exposure_model.py
and the exposure-value equation, not the arithmetic inside gear.js. A result
may fall short of the plan only where the physics forces it, never because
gear.js says it does.
"""
from __future__ import annotations

import itertools
import json
import math
import re
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
# Most lenses stop at f/22; gear.js assumes it for every lens.
NARROWEST = 22
THIRD = 2 ** (1 / 3)
SIXTH = 2 ** (1 / 6)
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
    # The zoom bursts go 35 -> 80 mm: this zoom stops at 70, so the burst has to end closer.
    "full_frame_24_70": ({"body": "full_frame", "iso": 12800, "lenses": [
        {"name": "24-70", "min": 24, "max": 70, "wide": 2.8, "tele": 2.8}]}),
    # Only a long zoom: it misses the 35 -> 80 mm burst and needs more than f/22 for the plans' depth.
    "full_frame_tele": ({"body": "full_frame", "iso": 25600, "lenses": [
        {"name": "100-400", "min": 100, "max": 400, "wide": 4.5, "tele": 5.6}]}),
    # The beginner's kit: a 50 mm on APS-C frames like 80 mm, and a plan at 35 mm f/22 needs more than f/22 with it.
    "apsc_nifty_fifty": ({"body": "apsc_canon", "iso": 6400, "lenses": [
        {"name": "50", "min": 50, "max": 50, "wide": 1.8, "tele": 1.8}]}),
    # The plans' own EF lenses on a Canon APS-C body: the 35 mm frames like 56 mm, so a shutter the plan
    # holds by hand at 35 mm (1/40) is past the reciprocal rule on the crop body.
    "apsc_canon_6d_lenses": ({"body": "apsc_canon", "iso": 12800, "lenses": [
        {"name": "EF 35mm f/2 IS USM", "min": 35, "max": 35, "wide": 2, "tele": 2},
        {"name": "EF 50mm f/1.8 STM", "min": 50, "max": 50, "wide": 1.8, "tele": 1.8},
        {"name": "EF 85mm f/1.8 USM", "min": 85, "max": 85, "wide": 1.8, "tele": 1.8},
        {"name": "EF 35–80mm f/4–5.6 III", "min": 35, "max": 80, "wide": 4, "tele": 5.6}]}),
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


def run_node(script: str) -> object:
    return json.loads(subprocess.run(["node", "-"], input=script, check=True, capture_output=True, text=True).stdout)


def adapt_all(gears: dict, slots: list | None = None) -> dict:
    return run_node(f"const G=require({json.dumps(str(GEAR_JS))});const slots={json.dumps(SLOTS if slots is None else slots)};"
                    f"const gears={json.dumps(gears)};"
                    "const out={};for(const [name,g] of Object.entries(gears)){out[name]=slots.map(s=>G.adapt(s,g));}"
                    "process.stdout.write(JSON.stringify(out));")


def ideal_gears() -> dict:
    """Keyed apart from REAL_KITS: three kits are named after their bodies, and a shared key would replace the ideal lens."""
    return {f"ideal {body}": {"body": body, "iso": 51200, "lenses": IDEAL} for body in BODY_W}


def need_node():
    if shutil.which("node") is None:
        pytest.skip("node is not installed")


@pytest.fixture(scope="module")
def results():
    need_node()
    gears = {**ideal_gears(), **REAL_KITS,
             "reference": run_node(f"process.stdout.write(JSON.stringify(require({json.dumps(str(GEAR_JS))}).reference()))")}
    assert len(gears) == len(BODY_W) + len(REAL_KITS) + 1, "a kit replaced another one"
    return gears, adapt_all(gears)


def plan_focal(lens: str) -> float:
    """The plan's focal; a zoom burst is framed where it ends, at the long end."""
    text = lens.replace("–", "-")
    if "@" in text:
        return float(text.split("@")[1])
    head = text.split("mm")[0]
    return float(head.split("-")[1] if "-" in head else head)


def plan_zoom(lens: str) -> tuple[float, float] | None:
    """'35-80mm' (zooming during the exposure) -> (35, 80); a fixed focal, or a zoom set at one focal, -> None."""
    match = re.match(r"^(\d+)-(\d+)mm\s*$", lens.replace("–", "-"))
    return (float(match[1]), float(match[2])) if match else None


def exposure_q(aperture: float, seconds: float, iso: float, nd: float) -> float:
    """log2(N²/t) − log2(ISO/100) + ND: equal values give equally bright pictures of the same scene; higher is darker."""
    return op.exposure_value(aperture, seconds, iso) + nd


def plan_q(slot: dict) -> float:
    return exposure_q(em.f_number(slot["aperture"]), em.shutter_seconds(slot["shutter"]), slot["iso"], slot["nd_stops"])


def viable(pairs):
    return [(s, r) for s, r in pairs if s["viable"] is not False and r["ok"]]


def lens_of(gear: dict, r: dict) -> dict | None:
    return next((lens for lens in gear["lenses"] if lens["name"] == r["lens_name"]), None)


def widest(lens: dict, focal: float) -> float:
    """A zoom's widest aperture narrows from the wide end to the tele end."""
    if lens["max"] == lens["min"]:
        return lens["wide"]
    share = min(1.0, max(0.0, (focal - lens["min"]) / (lens["max"] - lens["min"])))
    return lens["wide"] + share * (lens["tele"] - lens["wide"])


# The third-stop f-numbers a camera shows (nominally 2^(i/6), rounded as engraved).
MARKS = (1, 1.1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.5, 2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1, 8, 9, 10, 11, 13, 14, 16, 18, 20, 22)


def dial_open(w: float) -> float:
    """The widest mark a lens whose widest aperture is w can be set to."""
    return next(mark for mark in MARKS if mark >= w - 0.05)


def coc_of(sensor_w: float) -> float:
    return REF_COC * sensor_w / REF_W


def ideal_aperture(slot: dict, r: dict, sensor_w: float) -> float:
    """The f-number that gives the plan's hyperfocal distance scaled by d'/d, with the reader's focal and circle of confusion."""
    target = op.hyperfocal_mm(plan_focal(slot["lens"]), em.f_number(slot["aperture"]), REF_COC) * r["distance_m"] / slot["distance"]
    focal = r["focal"]
    return math.inf if target <= focal else focal * focal / (coc_of(sensor_w) * (target - focal))


def plan_sharp_to_infinity(slot: dict) -> bool:
    return math.isinf(op.depth_of_field(plan_focal(slot["lens"]), em.f_number(slot["aperture"]), slot["distance"], REF_COC)["far"])


def equivalent_focal(focal_on_6d: float, sensor_w: float) -> float:
    """The focal that gives a sensor sensor_w wide the angle of view focal_on_6d gives the 6D."""
    return sensor_w / (2 * math.tan(math.radians(op.half_angle_of_view_deg(focal_on_6d, REF_W))))


def framing_errors(slot, r, sensor_w):
    """Same field width at the subject. A zoom burst is compared where it ends, at its long end."""
    planned = slot["distance"] * REF_W / plan_focal(slot["lens"])
    got = r["distance_m"] * sensor_w / r["focal"]
    return [] if abs(math.log(got / planned)) < 0.02 else [f"{slot['key']}: field width {got:.2f} m vs {planned:.2f} m"]


def zoom_errors(slot, r, lens, sensor_w):
    """A zoom burst runs over the plan's angles of view, clipped to the reader's zoom, from short to long."""
    zoom = plan_zoom(slot["lens"])
    if zoom is None:
        return []
    shown = re.match(r"^(\d+)–(\d+) mm, girando", r["lens"])
    start = max(lens["min"], equivalent_focal(zoom[0], sensor_w))
    end = min(lens["max"], equivalent_focal(zoom[1], sensor_w))
    if shown and int(shown[1]) < int(shown[2]) and abs(int(shown[1]) - start) <= 0.5 + 1e-9 and abs(int(shown[2]) - end) <= 0.5 + 1e-9:
        return []
    return [f"{slot['key']}: burst shown as {r['lens']!r}, the physics gives {start:.1f}–{end:.1f} mm"]


def forced_shortfall(slot, r, lens, iso_limit):
    """Stops of light the gear cannot give without breaking the plan's creative variable.

    A depth-of-field shot can always lengthen its shutter, so it never falls short. A motion shot keeps its
    shutter: at most it gets the lens wide open, the ISO at the reader's limit and no ND filter."""
    if slot["technique"] not in MOTION:
        return 0.0
    brightest = exposure_q(dial_open(widest(lens, r["focal"])), em.shutter_seconds(slot["shutter"]), iso_limit, 0)
    return max(0.0, brightest - plan_q(slot))


def exposure_errors(slot, r, lens, iso_limit):
    """The plan's exposure from the EV equation, darker only by what the physics forces (third-stop dials: 1/3 EV)."""
    forced = forced_shortfall(slot, r, lens, iso_limit)
    off = exposure_q(r["f_number"], r["seconds"], r["iso"], r["nd_stops"]) - plan_q(slot)
    return [] if abs(off - forced) <= 1 / 3 + 1e-9 else [f"{slot['key']}: exposure {off:+.2f} EV from the plan, the gear forces only {forced:+.2f}"]


def dof_mismatch(slot, r, sensor_w):
    """Same sharp zone in proportion to the distance: near and far limits scale by d'/d."""
    f0, n0, d0 = plan_focal(slot["lens"]), em.f_number(slot["aperture"]), slot["distance"]
    planned = op.depth_of_field(f0, n0, d0, REF_COC)
    got = op.depth_of_field(r["focal"], r["f_number"], r["distance_m"], coc_of(sensor_w))
    scale = r["distance_m"] / d0
    errors = []
    # Apertures come in third stops, so the hyperfocal distance can land up to a sixth of a stop away; a plan
    # sharp to infinity may round one more third toward more depth to stay sharp to infinity.
    off = math.log(got["hyperfocal"] / (planned["hyperfocal"] * scale))
    deeper = math.log(SIXTH * (THIRD if math.isinf(planned["far"]) else 1))
    if not -deeper * 1.05 <= off <= math.log(SIXTH) * 1.05:
        errors.append(f"{slot['key']}: hyperfocal {got['hyperfocal']:.1f} m vs {planned['hyperfocal'] * scale:.1f} m")
    if abs(math.log(got["near"] / (planned["near"] * scale))) > 0.15:
        errors.append(f"{slot['key']}: near {got['near']:.2f} m vs {planned['near'] * scale:.2f} m")
    if math.isinf(planned["far"]) and not math.isinf(got["far"]):
        errors.append(f"{slot['key']}: sharp to {got['far']:.0f} m, the plan is sharp to infinity")
    return errors


def light_limits(slot, r, start, iso_limit):
    """For a motion shot the aperture may leave the depth-of-field match only for the light: closed when even
    ISO 100 is too bright at the matched aperture, opened when the ISO limit without ND is too dark. The
    matched aperture is rounded to a mark, so the light is judged with a third of a stop to spare."""
    t, q0 = em.shutter_seconds(slot["shutter"]), plan_q(slot)
    limits = set()
    if r["f_number"] > start and exposure_q(start, t, 100, slot["nd_stops"]) < q0 + 1 / 3:
        limits.add("too much light")
    if r["f_number"] < start and exposure_q(start, t, iso_limit, 0) > q0 - 1 / 3:
        limits.add("too little light")
    return limits


def dof_limits(slot, r, lens, iso_limit, sensor_w):
    """The reasons the physics gives for a depth of field that differs from the plan, each checked on the result."""
    n, w = ideal_aperture(slot, r, sensor_w), widest(lens, r["focal"])
    limits = set()
    if n < w - 0.05 and r["f_number"] <= dial_open(w) + 1e-9:
        limits.add("the lens does not open that far")
    if n > NARROWEST and r["f_number"] == NARROWEST:
        limits.add("the lens does not close that far")
    if slot["technique"] in MOTION:
        limits |= light_limits(slot, r, max(min(n, NARROWEST), w), iso_limit)
    return limits


def dof_errors(slot, r, lens, iso_limit, sensor_w):
    errors = dof_mismatch(slot, r, sensor_w)
    return [] if errors and dof_limits(slot, r, lens, iso_limit, sensor_w) else errors


@pytest.mark.parametrize("body", list(BODY_W))
def test_v13_an_unlimited_lens_reproduces_framing_depth_and_exposure(results, body):
    gears, out = results
    pairs = viable(zip(SLOTS, out[f"ideal {body}"]))
    assert len(pairs) >= 140
    errors = []
    for slot, r in pairs:
        errors += framing_errors(slot, r, BODY_W[body]) + zoom_errors(slot, r, IDEAL[0], BODY_W[body])
        errors += dof_errors(slot, r, IDEAL[0], 51200, BODY_W[body])
        errors += exposure_errors(slot, r, IDEAL[0], 51200)
    assert errors == []


def grid_slots():
    return [{"key": f"{tech} {ap} {sh} ISO {iso} ND {nd}", "technique": tech, "lens": "50mm", "aperture": ap, "shutter": sh,
             "iso": iso, "nd_stops": nd, "distance": 4, "viable": True}
            for tech, ap, sh, iso, nd in itertools.product(("poca_pdc", "mucha_pdc", "fantasma", "barrido", "congelado"),
                                                           ("f/2", "f/4", "f/8", "f/16"), ("1/2000", "1/250", "1/30", '1"', '8"'),
                                                           (100, 400, 1600, 6400), (0, 3, 6))]


def test_v13_exposure_and_depth_hold_beyond_the_plans_on_a_grid_of_settings():
    """The plans rarely make the gear add or drop an ND filter, so the exposure and the creative variable are also
    checked on a grid of settings, techniques, filters and ISO limits that forces every branch: more light, less
    light, ND on, ND off. Darker than the plan only where the physics forces it; a depth-of-field shot keeps its
    depth of field and pays for the light with the shutter; a motion shot leaves its depth only for the light."""
    need_node()
    grid = grid_slots()
    gears = {f"{body} ISO {limit}": {"body": body, "iso": limit, "lenses": IDEAL} for body in BODY_W for limit in (1600, 51200)}
    out = adapt_all(gears, grid)
    errors = []
    for name, rows in out.items():
        gear = gears[name]
        for slot, r in zip(grid, rows):
            errors += [f"{name} · {e}" for e in exposure_errors(slot, r, IDEAL[0], gear["iso"])]
            errors += [f"{name} · {e}" for e in dof_errors(slot, r, IDEAL[0], gear["iso"], BODY_W[gear["body"]])]
    assert sum(len(rows) for rows in out.values()) == 14400 and errors == []


def said_number(pattern: str, said: str) -> float | None:
    match = re.search(pattern, said)
    return float(match[1].replace(",", ".")) if match else None


def light_note_errors(slot, r, lens, sensor_w):
    """The lens limits and the missing light are said, with the numbers the physics gives."""
    said, errors = " ".join(r["notes"]), []
    n, w = ideal_aperture(slot, r, sensor_w), widest(lens, r["focal"])
    if n < w - 0.05 and r["f_number"] <= dial_open(w) + 1e-9 and "no abre tanto" not in said:
        errors.append(f"{slot['key']}: the lens cannot open to f/{n:.1f} and the line does not say so")
    dark = exposure_q(r["f_number"], r["seconds"], r["iso"], r["nd_stops"]) - plan_q(slot)
    missing = said_number(r"Faltan (\d+,\d) pasos", said)
    # The planner holds the exposure to a third of a stop (the 6D's dial step), so a shortfall is said from a third up.
    if (dark > 1 / 3 + 0.02 and (missing is None or abs(missing - dark) > 0.1)) or (dark < 1 / 3 - 0.02 and missing is not None):
        errors.append(f"{slot['key']}: {dark:+.2f} EV darker than the plan, the line says {missing} stops missing")
    return errors


def test_v13_a_shortfall_is_said_only_from_a_third_of_a_stop():
    """Real kits on the grid of settings: the lens limits and the missing light are said with the numbers the
    physics gives, and nothing is said missing under a third of a stop (red team, second pass on PR #20:
    "Faltan 0,2 pasos" at 0.17 EV), which the 6D's dial cannot even show."""
    need_node()
    grid = grid_slots()
    gears = {f"{kit} ISO {limit}": {**gear, "iso": limit} for kit, gear in REAL_KITS.items() for limit in (1600, 6400)}
    out = adapt_all(gears, grid)
    errors = []
    for name, rows in out.items():
        gear = gears[name]
        for slot, r in viable(zip(grid, rows)):
            errors += [f"{name} · {e}" for e in light_note_errors(slot, r, lens_of(gear, r), BODY_W[gear["body"]])]
    assert errors == [], errors[:8]


def depth_note_errors(slot, r, sensor_w):
    """At f/22 a long lens can lose the plan's sharp zone; the line says so, and where the zone now ends."""
    if r["f_number"] != NARROWEST or not dof_mismatch(slot, r, sensor_w):
        return []
    said = " ".join(r["notes"])
    far = op.depth_of_field(r["focal"], r["f_number"], r["distance_m"], coc_of(sensor_w))["far"]
    if plan_sharp_to_infinity(slot) and not math.isinf(far):
        shown = said_number(r"hasta (\d+,\d) m", said)
        return [] if shown is not None and abs(shown - far) <= 0.051 else [f"{slot['key']}: sharp only to {far:.1f} m at f/22, the line says {shown}"]
    return [] if "menos zona nítida" in said else [f"{slot['key']}: depth of field lost at f/22 without a note"]


def tripod_errors(slot, r, sensor_w):
    """Reciprocal rule on the equivalent focal (focal × crop factor, Photography Life "What is the reciprocal
    rule"): support past 1/(equivalent focal) whenever the reader passes it at a shutter the plan could hold, or
    at a shutter slower than the plan's; never at a shutter the reader can hold. Panning moves the camera on purpose."""
    if slot["technique"] == "barrido":
        return []
    limit = 1 / (r["focal"] * REF_W / sensor_w)
    plan_t = em.shutter_seconds(slot["shutter"])
    plan_holds = plan_t <= 1.05 / plan_focal(slot["lens"])
    tripod = "trípode" in " ".join(r["notes"])
    if r["seconds"] > limit * 1.05 and (plan_holds or r["seconds"] > plan_t * 1.05) and not tripod:
        return [f"{slot['key']}: {r['shutter']} on {r['focal']:.0f} mm ({1 / limit:.0f} mm equivalent) needs support, no note"]
    if r["seconds"] <= limit and tripod:
        return [f"{slot['key']}: tripod asked at {r['shutter']} on {1 / limit:.0f} mm equivalent"]
    return []


def distance_note_errors(slot, r):
    """A changed camera distance is said, with the distance."""
    if abs(r["distance_m"] / slot["distance"] - 1) <= 0.05:
        return []
    shown = said_number(r"(?:Acércate|Retrocede) a (\d+,\d) m", " ".join(r["notes"]))
    return [] if shown is not None and abs(shown - r["distance_m"]) <= 0.051 else [f"{slot['key']}: camera at {r['distance_m']:.1f} m, the line says {shown}"]


def limit_errors(slot, r, lens, gear):
    errors = []
    if not 100 <= r["iso"] <= gear["iso"]:
        errors.append(f"{slot['key']}: ISO {r['iso']} outside 100-{gear['iso']}")
    if r["seconds"] < 1 / 4000 - 1e-9:
        errors.append(f"{slot['key']}: {r['shutter']} faster than the body")
    if r["f_number"] < widest(lens, r["focal"]) - 0.06 or r["f_number"] > NARROWEST:
        errors.append(f"{slot['key']}: f/{r['f_number']} outside the lens")
    return errors


def kit_errors(slot, r, gear):
    lens, sensor_w = lens_of(gear, r), BODY_W[gear["body"]]
    if lens is None or not lens["min"] - 0.01 <= r["focal"] <= lens["max"] + 0.01:
        return [f"{slot['key']}: {r['focal']} mm is not on {r['lens_name']}"]
    errors = limit_errors(slot, r, lens, gear) + framing_errors(slot, r, sensor_w) + zoom_errors(slot, r, lens, sensor_w)
    errors += exposure_errors(slot, r, lens, gear["iso"]) + dof_errors(slot, r, lens, gear["iso"], sensor_w)
    errors += light_note_errors(slot, r, lens, sensor_w) + depth_note_errors(slot, r, sensor_w)
    return errors + tripod_errors(slot, r, sensor_w) + distance_note_errors(slot, r)


@pytest.mark.parametrize("kit", list(REAL_KITS))
def test_v13_real_kits_stay_within_their_limits_and_say_what_they_lose(results, kit):
    gears, out = results
    errors = []
    for slot, r in viable(zip(SLOTS, out[kit])):
        errors += kit_errors(slot, r, gears[kit])
    assert errors == []


@pytest.mark.parametrize("kit", list(REAL_KITS))
def test_v13_motion_shots_keep_the_planned_shutter(results, kit):
    gears, out = results
    changed = [f"{s['key']}: {s['shutter']} -> {r['shutter']}" for s, r in viable(zip(SLOTS, out[kit]))
               if s["technique"] in MOTION and em.shutter_seconds(r["shutter"]) != pytest.approx(em.shutter_seconds(s["shutter"]), rel=0.01)]
    assert changed == []


def test_v13_depth_of_field_shots_keep_their_depth_of_field_when_the_lens_allows(results):
    """A depth-of-field shot changes its aperture only at the lens's own limits, never for the light."""
    gears, out = results
    errors = []
    for kit, gear in {**ideal_gears(), **REAL_KITS}.items():
        for slot, r in viable(zip(SLOTS, out[kit])):
            if slot["technique"] in ("mucha_pdc", "poca_pdc"):
                errors += dof_errors(slot, r, lens_of(gear, r), gear["iso"], BODY_W[gear["body"]])
    assert errors == []


@pytest.mark.parametrize("kit", ["apsc_primes_only", "apsc_nifty_fifty", "full_frame_tele"])
def test_v13_a_zoom_burst_without_a_zoom_that_covers_it_says_so(results, kit):
    """Primes cannot zoom, and a 100-400 cannot run a 35 -> 80 mm burst: there is no burst to offer."""
    gears, out = results
    zooming = [r for s, r in zip(SLOTS, out[kit]) if s["technique"] == "zooming" and s["viable"] is not False]
    assert zooming and all(not r["ok"] and "zoom" in r["reason"] for r in zooming), [r.get("lens") for r in zooming]
    # A reader who owns a zoom is told it misses the range, not asked to add a zoom.
    owns_zoom = any(lens["max"] / lens["min"] >= 1.5 for lens in gears[kit]["lenses"])
    assert all(("llega" in r["reason"] and " mm con tu cámara" in r["reason"]) == owns_zoom for r in zooming), {r["reason"] for r in zooming}


def test_v13_a_plan_sharp_to_infinity_stays_sharp_to_infinity_after_rounding():
    """Rounding the f-number to the nearest mark can push the hyperfocal distance past the subject. A01 day
    (35 mm f/11 at 4 m) on a 38 mm prime on the 6D: f/11 at 4.3 m is sharp only to 176 m, f/13 to infinity."""
    need_node()
    slots = [s for s in SLOTS if s["viable"] is not False and plan_zoom(s["lens"]) is None and plan_sharp_to_infinity(s)]
    gears = {f"{body} {f} mm": {"body": body, "iso": 51200, "lenses": [{"name": "prime", "min": f, "max": f, "wide": 1.4, "tele": 1.4}]}
             for body in BODY_W for f in range(8, 201)}
    rows = run_node(f"const G=require({json.dumps(str(GEAR_JS))});const slots={json.dumps(slots)};const gears={json.dumps(gears)};"
                    "const out={};for(const [k,g] of Object.entries(gears)){out[k]=slots.map(s=>{const r=G.adapt(s,g);return [r.focal,r.f_number,r.distance_m];});}"
                    "process.stdout.write(JSON.stringify(out));")
    errors = []
    for name, results_for_gear in rows.items():
        sensor_w = BODY_W[gears[name]["body"]]
        for slot, (focal, n, distance) in zip(slots, results_for_gear):
            far = op.depth_of_field(focal, n, distance, coc_of(sensor_w))["far"]
            if n < NARROWEST and not math.isinf(far):
                errors.append(f"{name} · {slot['key']}: f/{n} sharp only to {far:.0f} m")
    assert len(slots) >= 50 and errors == []


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
    need_node()
    script = (f"const G=require({json.dumps(str(GEAR_JS))});const s={json.dumps(SLOTS[0])};"
              "process.stdout.write(JSON.stringify([G.lineHtml(s,G.reference()),G.lineHtml(s,{body:'m43',iso:6400,lenses:G.reference().lenses})]));")
    default_line, other_line = run_node(script)
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
    need_node()
    stored = {"body": "apsc_canon", "iso": "6400", "lenses": [
        {"name": '<img src=x onerror="alert(1)">50', "min": 50, "max": 50, "wide": 1.8, "tele": 1.8},
        {"name": "zoom", "min": "18<b>", "max": 55, "wide": 3.5, "tele": 5.6},
        None,
    ]}
    script = (f"global.localStorage={{getItem:()=>{json.dumps(json.dumps(stored))}}};const G=require({json.dumps(str(GEAR_JS))});"
              f"const g=G.load();process.stdout.write(JSON.stringify([g,G.lineHtml({json.dumps(SLOTS[0])},g)]));")
    gear, line = run_node(script)
    assert gear["iso"] == 6400 and [lens["min"] for lens in gear["lenses"]] == [50]
    assert "<" not in gear["lenses"][0]["name"] and '"' not in gear["lenses"][0]["name"]
    assert "<img" not in line and "Con tu equipo" in line


# The home page's picker, run on a stand-in DOM: every element is a plain object, so the picker's own options
# can be read back, and a <select> whose value is not one of its options shows blank.
PICKER = """
const vm=require('vm'),fs=require('fs');
const els={};const el=()=>({innerHTML:'',value:'',textContent:'',hidden:true,addEventListener(){}});
const ctx={document:{getElementById:id=>els[id]||(els[id]=el()),dispatchEvent(){}},CustomEvent:function(){},
  localStorage:{getItem:()=>RAW,setItem(){},removeItem(){}}};
ctx.window=ctx;vm.createContext(ctx);vm.runInContext(fs.readFileSync(PATH,'utf8'),ctx);
const options=[...els['gear-iso'].innerHTML.matchAll(/value="([^"]*)"/g)].map(m=>m[1]);
const line=ctx.FocalRutaEquipo.lineFor({technique:'mucha_pdc',subject_distance_m:4},{lens:'35mm',aperture:'f/11',shutter:'1/125',iso:400});
process.stdout.write(JSON.stringify({shown:els['gear-iso'].value,options,line}));
"""


# Too low comes back as the lowest option, too high as the highest, not a number as the body's own limit (APS-C: 12800).
@pytest.mark.parametrize(("stored_iso", "shown"), [("50", "1600"), ("1e309", "51200"), ("-3", "12800")])
def test_v15_a_stored_iso_limit_out_of_range_comes_back_as_one_the_picker_offers(stored_iso, shown):
    """ISO 50 used to draw "ISO undefined", and 1e309 (Infinity once parsed) left the picker blank."""
    need_node()
    raw = '{"body":"apsc_canon","iso":' + stored_iso + ',"lenses":[{"name":"50","min":50,"max":50,"wide":1.8,"tele":1.8}]}'
    got = run_node(f"const RAW={json.dumps(raw)},PATH={json.dumps(str(GEAR_JS))};" + PICKER)
    iso = re.search(r"ISO (\S+?)[ <]", got["line"])
    assert got["options"] and got["shown"] in got["options"] and got["shown"] == shown, got
    assert iso and iso[1] in {str(x) for x in em.THIRD_STOP_ISOS} | {"32000", "40000", "51200"}, got["line"]


def test_v15_the_stored_gear_is_parsed_once_per_change_not_once_per_shot():
    """The home page draws 175 shot lines at once; each used to parse localStorage again. A change still shows."""
    need_node()
    first = {"body": "apsc_canon", "iso": 6400, "lenses": [{"name": "50", "min": 50, "max": 50, "wide": 1.8, "tele": 1.8}]}
    second = {"body": "m43", "iso": 6400, "lenses": [{"name": "25", "min": 25, "max": 25, "wide": 1.7, "tele": 1.7}]}
    script = (f"let raw={json.dumps(json.dumps(first))};const second={json.dumps(json.dumps(second))};"
              "global.localStorage={getItem:()=>raw,setItem(){},removeItem(){}};"
              "const parse=JSON.parse;let parsed=0;JSON.parse=function(s){if(s===raw||s===second)parsed++;return parse.apply(JSON,arguments);};"
              f"const G=require({json.dumps(str(GEAR_JS))});const shot={{technique:'mucha_pdc',subject_distance_m:4}};"
              "const setting={lens:'35mm',aperture:'f/11',shutter:'1/125',iso:400};"
              "const lines=[];for(let i=0;i<175;i++)lines.push(G.lineFor(shot,setting));const once=parsed;"
              "raw=second;const after=G.lineFor(shot,setting);"
              "process.stdout.write(JSON.stringify({once,total:parsed,same:new Set(lines).size,first:lines[0],after}));")
    got = run_node(script)
    assert got["once"] == 1 and got["same"] == 1, got
    assert got["total"] == 2 and got["after"] != got["first"] and "25 mm" in got["after"], got


@pytest.mark.parametrize("slowest", [22, 25, 32])
def test_v13_the_slowest_lens_the_picker_accepts_still_gets_an_aperture(slowest):
    """The form took a maximum aperture up to f/32, beyond the f/22 the conversion closes to:
    such a lens drew "f/undefined". A lens the picker accepts must get a real f-number on every slot."""
    need_node()
    lens = {"name": "lento", "min": 50, "max": 50, "wide": slowest, "tele": slowest}
    raw = json.dumps({"body": "full_frame", "iso": 51200, "lenses": [lens]})
    got = run_node(f"global.localStorage={{getItem:()=>{json.dumps(raw)},setItem(){{}},removeItem(){{}}}};"
                   f"const G=require({json.dumps(str(GEAR_JS))});const g=G.load();const slots={json.dumps(SLOTS)};"
                   "process.stdout.write(JSON.stringify({kept:g.lenses.length,apertures:[...new Set(slots.map(s=>G.adapt(s,g)).filter(r=>r.ok).map(r=>r.aperture))]}));")
    if got["kept"]:
        assert got["apertures"] and all(re.fullmatch(r"f/\d+(\.\d)?", a) for a in got["apertures"]), got
    assert got["kept"] == (1 if slowest <= 22 else 0), got
