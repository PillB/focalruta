"""Y05-Y18: what the plans tell a reader in the field agrees with Lima, the camera and the plans' own numbers.

The red team on PR #24 (research audit, F1-F22) found advice that the arithmetic under it
contradicts: a sunny sky planned all year in a city under cloud from June to October, a
frame that cannot hold the jump it promises, fill flash at 1/4000 s on a body that syncs at
1/180 s, a handheld rule stated three ways, a zoom burst both "never 1 s" and "1 to 4 s",
a sunset "into the sea" that falls behind San Lorenzo island half the year, and a golden
hour that ends before the hour the plan sends the reader out.

Every check holds the text to something it does not say itself: the exposure equation, the
sensor's size, Canon's specifications for the EOS 6D (flash sync 1/180 s, a 7-frame RAW+JPEG
buffer against 14 in RAW) and the EF 35 mm f/2 IS (4 stops of stabilisation), the site's own
sun model (scripts/sun_times.py) and the outline of San Lorenzo island in OpenStreetMap.
"""
from __future__ import annotations

import math
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exposure_model as em  # noqa: E402
import optics_physics as op  # noqa: E402
import sun_times  # noqa: E402
from test_shot_physics import (  # noqa: E402
    ENVELOPES, HANDHELD, SENSOR_H_MM, SENSOR_W_MM, SUPPORTED, THIRD_STOP_APERTURES, all_shots, load_plans,
    max_aperture, slot_focal_mm, slots, viable_slots,
)

SUNNY = {"sol_pleno", "sol_velado"}
GARUA_EV = em.scene_range("nublado_claro")[0]


def ev(s: dict) -> float:
    n, t = em.f_number(s["aperture"]), em.shutter_seconds(s["shutter"])
    return math.log2(n * n / t) - math.log2(s["iso"] / 100) + s.get("nd_stops", 0)


def garua_sentence(notes: str) -> str:
    return notes[notes.find("Con garúa"):] if "Con garúa" in notes else ""


def own_notes(notes: str) -> str:
    return notes[:notes.find("Con garúa")] if "Con garúa" in notes else notes


# --------------------------------------------------------------------------- Y05


def garua_limits(shot: dict, s: dict, g: dict) -> list[str]:
    """What the camera, the lens and the technique allow the garúa setting."""
    n, t = em.f_number(g["aperture"]), em.shutter_seconds(g["shutter"])
    problems = []
    if g["scene"] != "nublado_claro" or abs(ev(g) - GARUA_EV) > 1 / 3 + 1e-9:
        problems.append(f"EV {ev(g):.2f} for {g['scene']}")
    if not ENVELOPES[shot["technique"]](n, t):
        problems.append("leaves the technique's envelope")
    if g["shutter"] not in em.THIRD_STOP_SHUTTERS or g["iso"] not in em.THIRD_STOP_ISOS or n not in THIRD_STOP_APERTURES:
        problems.append("not on the dials")
    if not max_aperture(s["lens"]) - 1e-9 <= n <= 16:
        problems.append("outside the lens or past f/16")
    if g.get("nd_stops", 0) not in {0, 2, 3, 6, 10}:
        problems.append("not a stock ND")
    if shot["technique"] in HANDHELD and t > nearest_dial(hand_limit(s["lens"])) * 1.01:
        problems.append("slower than the hand holds")
    return problems


def garua_wording(shot: dict, s: dict, g: dict) -> list[str]:
    """The setting keeps what makes the effect, and the note gives every value it changes."""
    problems = []
    effect = {"mucha_pdc": "aperture", "poca_pdc": "aperture"}.get(shot["technique"], "shutter")
    if shot["technique"] != "congelado" and g[effect] != s[effect]:
        problems.append(f"changes the {effect} that makes the effect")
    said = garua_sentence(s["notes"])
    for key, shown in (("aperture", g["aperture"]), ("shutter", g["shutter"]), ("iso", f"ISO {g['iso']}")):
        if g[key] != s[key] and shown not in said:
            problems.append(f"the note does not give the {key} {shown}")
    return problems


def test_y05_every_sunny_day_slot_also_says_how_to_shoot_it_under_the_garua():
    # Jorge Chávez gets 28-60 h of sun a month from June to October against 185 h in January
    # (DWD 1991-2020 normals): a sunny morning is the exception for half the year.
    missing, wrong = [], []
    for shot, time, s in viable_slots(load_plans()):
        if time != "day" or s["scene"] not in SUNNY:
            continue
        g = s.get("garua")
        if not g:
            missing.append(shot["id"])
        elif garua_limits(shot, s, g) + garua_wording(shot, s, g):
            wrong.append((shot["id"], garua_limits(shot, s, g) + garua_wording(shot, s, g)))
    assert not missing and not wrong, {"missing": missing, "wrong": wrong}


def test_y05_the_garua_months_are_the_ones_the_sunshine_record_gives():
    for shot, time, s in viable_slots(load_plans()):
        said = garua_sentence(s["notes"])
        if said:
            assert "de junio a octubre" in said, (shot["id"], said)


# --------------------------------------------------------------------------- Y06

CLEAR_SKY = re.compile(r"cielo (azul|despejado)|despejad|sol fuerte|sombras duras", re.I)
DUSK = {"antes_ocaso", "tras_ocaso"}


def test_y06_no_note_describes_a_brighter_sky_than_the_light_its_settings_are_for():
    bad = []
    for shot, time, s in slots(load_plans()):
        if CLEAR_SKY.search(own_notes(s["notes"])) and s["scene"] != "sol_pleno":
            bad.append((shot["id"], time, s["scene"], s["notes"][:60]))
    for _plan, shot in all_shots(load_plans()):
        day = shot["settings_by_time"]["day"]
        if CLEAR_SKY.search(shot["scene_notes"]) and day["scene"] != "sol_pleno":
            bad.append((shot["id"], "scene_notes", day["scene"], shot["scene_notes"][:60]))
    assert not bad, bad


def test_y06_morning_slots_are_never_scored_against_the_light_before_or_after_sunset():
    bad = [(shot["id"], s["scene"]) for shot, time, s in slots(load_plans())
           if (time == "day" or s["notes"].startswith("Mañana")) and s["scene"] in DUSK]
    assert not bad, bad


# --------------------------------------------------------------------------- Y08

PERSON_M, JUMP_ARMS_UP_M, AIR = 1.7, 2.6, 1.1
COVERS = re.compile(r"cubre (?:sólo )?[≈~]\s*(\d+(?:[.,]\d+)?)\s*×\s*(\d+(?:[.,]\d+)?)\s*m")


def fit_claim_errors(shot: dict):
    focal = slot_focal_mm(shot["settings_by_time"]["afternoon"]["lens"])
    long_side = shot["subject_distance_m"] * SENSOR_W_MM / focal
    short_side = shot["subject_distance_m"] * SENSOR_H_MM / focal
    for sentence in re.split(r"(?<=\.)\s", shot["reasoning"]):
        if not COVERS.search(sentence) or not re.search(r"cuerpo entero|brazos arriba|en el aire", sentence):
            continue
        tall = JUMP_ARMS_UP_M if re.search(r"brazos arriba|salto|en el aire", sentence) else PERSON_M
        for orientation, height in (("horizontal", short_side), ("vertical", long_side)):
            claims = re.search(rf"en {orientation}[^.;:]*?(entra|sobra|con margen|con aire)", sentence)
            if re.search(rf"en {orientation}[^.;:]*?\bno (entra|cabe)", sentence):
                claims = None
            unnamed = orientation == "horizontal" and not re.search(r"en (horizontal|vertical)", sentence)
            if (claims or unnamed) and height < tall * AIR:
                yield f"{shot['id']}: {orientation} frame {height:.2f} m tall for {tall} m"


def test_y08_a_frame_said_to_hold_the_body_is_tall_enough_for_it():
    # 23.9 x 35.8 mm sensor: frame size = distance x sensor / focal.
    bad = [error for _plan, shot in all_shots(load_plans()) for error in fit_claim_errors(shot)]
    assert not bad, bad


def test_y08_the_fit_checker_sees_the_sentence_the_red_team_found():
    shot = {"reasoning": "A 6 m el 85 mm cubre ≈2.5 × 1.7 m: en horizontal entra el cuerpo entero con poco aire.",
            "subject_distance_m": 6.0, "id": "A05", "settings_by_time": {"afternoon": {"lens": "85mm"}}}
    assert list(fit_claim_errors(shot))


# --------------------------------------------------------------------------- Y09

X_SYNC_S = 1 / 180  # Canon EOS 6D specifications: X-sync 1/180 s, no built-in flash
FLASH = re.compile(r"flash", re.I)
NO_FLASH = re.compile(r"sin flash|flash directo|no uses flash", re.I)


def shot_texts(shot: dict):
    yield "reasoning", shot["reasoning"]
    for key in ("dos", "donts"):
        for text in shot[key]:
            yield key, text
    for time, s in shot["settings_by_time"].items():
        yield time, s["notes"]


def test_y09_flash_is_only_suggested_with_the_sync_speed_or_high_speed_sync():
    bad = []
    for _plan, shot in all_shots(load_plans()):
        fastest = min(em.shutter_seconds(s["shutter"]) for s in shot["settings_by_time"].values())
        for where, text in shot_texts(shot):
            if FLASH.search(text) and not NO_FLASH.search(text) and fastest < X_SYNC_S:
                if not re.search(r"1/180|HSS", text):
                    bad.append((shot["id"], where, text[:80]))
    assert not bad, bad


# --------------------------------------------------------------------------- Y10


def test_y10_street_lamp_white_balance_is_measured_not_a_fixed_kelvin():
    # High-pressure sodium burns at about 2000-2100 K with a CRI near 22, Lima's LED at
    # 3000-4000 K: one Kelvin number cannot neutralise both.
    bad = []
    for _plan, shot in all_shots(load_plans()):
        for where, text in shot_texts(shot):
            for kelvin in re.findall(r"(\d{4})\s*K\b", text):
                if re.search(r"farol|sodio|calle|noche", text, re.I) and not (
                        "RAW" in text and "personalizado" in text and re.search(r"sodio[^.]*2[01]00", text)):
                    bad.append((shot["id"], where, kelvin, text[:80]))
    assert not bad, bad


# --------------------------------------------------------------------------- Y11

IS_STOPS = {"35": 3}  # EF 35 mm f/2 IS USM: 4 stops (Canon), 3 counted to keep a margin


def hand_limit(lens: str) -> float:
    """Slowest handheld time that passes the 100 % check: 1/(2 x focal), stretched by IS."""
    focal = slot_focal_mm(lens)
    stabilised = re.match(r"(\d+)", lens).group(1) if "35-80" not in lens else ""
    return 2 ** IS_STOPS.get(stabilised, 0) / (2 * focal)


def nearest_dial(seconds: float) -> float:
    return min((em.shutter_seconds(x) for x in em.THIRD_STOP_SHUTTERS), key=lambda t: abs(math.log2(t / seconds)))


def test_y11_handheld_slots_pass_the_100_percent_check_or_say_how_to_support_the_camera():
    bad = []
    for shot, time, s in viable_slots(load_plans()):
        if shot["technique"] not in HANDHELD:
            continue
        if em.shutter_seconds(s["shutter"]) > nearest_dial(hand_limit(s["lens"])) * 1.01 and not SUPPORTED.search(s["notes"]):
            bad.append((shot["id"], time, s["lens"], s["shutter"]))
    assert not bad, bad


def test_y11_no_text_warns_of_camera_shake_at_a_speed_the_lens_holds():
    bad = []
    for _plan, shot in all_shots(load_plans()):
        lens = shot["settings_by_time"]["afternoon"]["lens"]
        for where, text in shot_texts(shot):
            for denominator in re.findall(r"1/(\d+)[^.]*trepid|trepid[^.]*1/(\d+)", text):
                speed = 1 / float(next(d for d in denominator if d))
                if speed <= hand_limit(lens):
                    bad.append((shot["id"], where, text[:80]))
    assert not bad, bad


# --------------------------------------------------------------------------- Y12


def test_y12_zoom_burst_times_agree_with_the_one_to_four_seconds_the_plans_use():
    bad = []
    for _plan, shot in all_shots(load_plans()):
        if shot["technique"] != "zooming":
            continue
        for where, text in shot_texts(shot):
            for value in re.findall(r"No uses (\d+) s", text):
                if 1 <= float(value) <= 4:
                    bad.append((shot["id"], where, text))
            for value in re.findall(r"más de (\d+) s", text):
                if float(value) != 4:
                    bad.append((shot["id"], where, text))
    assert not bad, bad


# --------------------------------------------------------------------------- Y13

PIXEL_UM = 35.8 / 5472 * 1000  # 6.54 µm


def test_y13_no_slot_is_planned_where_diffraction_spreads_a_point_over_four_pixels():
    # Airy disk diameter 2.44 x 0.55 µm x N: at f/16 it is 3.3 pixels, at f/22 4.5.
    bad = [(shot["id"], time, s["aperture"]) for shot, time, s in viable_slots(load_plans())
           if 2.44 * 0.55 * em.f_number(s["aperture"]) / PIXEL_UM > 4]
    assert not bad, bad


def test_y13_infinity_is_only_promised_sharp_for_the_print_the_blur_circle_assumes():
    # 0.030 mm suits a normal print; the 100 % check on the camera needs about half.
    bad = []
    for _plan, shot in all_shots(load_plans()):
        if not re.search(r"hasta el infinito", shot["reasoning"]):
            continue
        focal = slot_focal_mm(shot["settings_by_time"]["afternoon"]["lens"])
        n = em.f_number(shot["aperture"])
        strict = op.depth_of_field(focal, n, shot["subject_distance_m"], coc_mm=0.015)
        if not math.isinf(strict["far"]) and not re.search(r"copia", shot["reasoning"]):
            bad.append(shot["id"])
    assert not bad, bad


# --------------------------------------------------------------------------- Y15


def test_y15_action_bursts_are_not_told_to_shoot_raw_and_jpeg():
    # The 6D buffers about 7 RAW+JPEG frames against 14 RAW (Canon specifications): at
    # 4.5 fps the buffer fills in under two seconds, and the file type does not help focus.
    bad = [(shot["id"], text) for _plan, shot in all_shots(load_plans()) if shot["technique"] == "congelado"
           for _where, text in shot_texts(shot) if re.search(r"(Dispara|usa) en (JPG\s*\+\s*RAW|RAW\s*\+\s*JPE?G)", text, re.I)]
    assert not bad, bad


# --------------------------------------------------------------------------- Y16

MALECON = (-12.1267, -77.0365)  # Malecón Cisneros, Miraflores
# San Lorenzo island seen from there, from its OpenStreetMap outline (relation 3285474).
SAN_LORENZO_BEARINGS = (274.6, 288.4)
MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
          "octubre", "noviembre", "diciembre")


def test_y16_plan_b_says_when_the_sun_sets_behind_san_lorenzo_and_not_into_the_sea():
    year = [date(2026, 1, 1) + timedelta(days=i) for i in range(365)]
    behind = [d for d in year if sun_times.sunset_azimuth(d) >= SAN_LORENZO_BEARINGS[0]]
    first, last = MONTHS[behind[0].month - 1], MONTHS[behind[-1].month - 1]
    why = next(p for p in load_plans()["plans"] if p["id"] == "plan_b")["why"]
    assert "San Lorenzo" in why and first in why and last in why, (first, last, why)


def test_y16_every_plan_says_who_lets_you_shoot_there_and_when_that_was_checked():
    for plan in load_plans()["plans"]:
        access = plan.get("access", "")
        assert re.search(r"Revisado el \d{1,2} de [a-z]+ de 20\d\d\.$", access), (plan["id"], access)


def test_y16_the_plaza_san_martin_symmetry_names_the_facing_portales():
    # Hotel Bolívar and Club Nacional both stand on the west side (OpenStreetMap); the
    # near-identical pair facing each other are the Portal de Zela and the Portal de Pumacahua.
    d02 = next(shot for _plan, shot in all_shots(load_plans()) if shot["id"] == "D02")
    assert "Zela" in d02["scene_notes"] and "Pumacahua" in d02["scene_notes"], d02["scene_notes"]
    assert not re.search(r"Club Nacional y Hotel Bolívar\) a ambos lados", d02["scene_notes"])


def test_y16_no_shot_asks_anyone_to_scare_birds_into_the_frame():
    bad = [(shot["id"], text) for _plan, shot in all_shots(load_plans())
           for _where, text in shot_texts(shot) if re.search(r"asust", text, re.I)]
    assert not bad, bad


def test_y16_the_clifftop_warning_is_about_the_edge_not_the_spray():
    # The Malecón stands on 50 m cliffs: spray does not reach it, the railing does.
    texts = [text for _plan, shot in all_shots(load_plans()) if shot["id"].startswith("B")
             for _where, text in shot_texts(shot)]
    assert not any("spray" in text for text in texts)
    assert any(re.search(r"baranda", text) and re.search(r"no (la )?pases|no te subas", text, re.I) for text in texts)


# --------------------------------------------------------------------------- Y17


def golden_end_minutes_after_sunrise() -> list[float]:
    out = []
    for month in range(1, 13):
        plan = sun_times.day_plan(date(2026, month, 21))
        out.append(plan["golden_am_end"] - plan["sunrise"])
    return out


def test_y17_golden_hour_lengths_in_the_text_are_the_sun_models():
    spans = golden_end_minutes_after_sunrise()
    for plan in load_plans()["plans"]:
        for claimed in re.findall(r"luz dorada ≈(\d+) min tras salir el sol", plan["best_window"]):
            assert min(spans) - 5 <= float(claimed) <= max(spans) + 5, (plan["id"], claimed, spans)


def test_y17_no_note_promises_warm_morning_light_after_the_golden_hour_has_ended():
    latest_end = max(sun_times.day_plan(date(2026, 1, 1) + timedelta(days=i))["golden_am_end"] for i in range(365))
    bad = []
    for shot, time, s in slots(load_plans()):
        # The middle of the promised window comes after the golden hour on every day of the year.
        for start, end in re.findall(r"(\d{1,2})[-–](\d{1,2})\s*am[^.]*(?:cálida|dorada)", s["notes"]):
            if (float(start) + float(end)) * 30 >= latest_end:
                bad.append((shot["id"], time, s["notes"]))
    assert not bad, bad


# --------------------------------------------------------------------------- Y18


def test_y18_no_text_blames_the_focal_length_for_converging_or_stretched_lines():
    # Converging verticals come from tilting the camera, edge stretch from where you stand
    # with a rectilinear lens (Wikipedia, "Perspective distortion"); none of the kit is 24 mm.
    bad = [(shot["id"], text) for _plan, shot in all_shots(load_plans())
           for _where, text in shot_texts(shot) if re.search(r"\d+ ?mm\)? — distorsiona|angular[^.]*distorsiona", text)]
    assert not bad, bad
