"""Physical invariants for the sixty planned shots.

Requirements: P01 (exposure matches scene light), P02 (ND filters are stock
densities and named where needed), P03 (camera and lens limits), P04
(technique envelopes), P05 (optical claims in the explanations agree with the
shared optics module), P06 (the published JSON is the canonical data).

Every assertion compares the data against an independent calculation: the
exposure-value equation, the thin-lens depth-of-field model in
optics_physics.py, or the sensor geometry published by Canon. None of them
re-reads the value it is checking.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import exposure_model as em  # noqa: E402
import optics_physics as op  # noqa: E402

PLANS_JSON = ROOT / "data" / "plans.json"
SENSOR_W_MM, SENSOR_H_MM = 35.8, 23.9  # Canon EOS 6D, global.canon camera museum
STOCK_ND_STOPS = {2, 3, 6, 10}
TIMES = ("day", "afternoon", "night")


def load_plans(path: Path = PLANS_JSON) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def all_shots(data: dict):
    for plan in data["plans"]:
        for shot in plan["shots"]:
            yield plan, shot


def slots(data: dict):
    for _plan, shot in all_shots(data):
        for time in TIMES:
            yield shot, time, shot["settings_by_time"][time]


def viable_slots(data: dict):
    return [(shot, time, s) for shot, time, s in slots(data) if s.get("viable", True)]


def number(text: str) -> float:
    return float(text.replace(",", "."))


def headline_focal_mm(shot: dict) -> float:
    value = str(shot["lens_focal"])
    match = re.search(r"@(\d+)", value)
    return float(match.group(1) if match else re.match(r"\d+", value).group(0))


def max_aperture(lens: str) -> float:
    """Widest f-number each lens in the kit can reach at the stated focal length."""
    if "35-80" in lens:
        at = re.search(r"@(\d+)", lens)
        if not at:
            return 5.6  # zooming through 80 mm
        focal = int(at.group(1))
        return 4.0 if focal <= 35 else 4.5 if focal <= 50 else 5.6
    return {"35": 2.0, "50": 1.8, "85": 1.8}[re.match(r"\d+", lens).group(0)]


# --------------------------------------------------------------------------- P01


def exposure_violations(data: dict) -> list[str]:
    bad = []
    for shot, time, s in viable_slots(data):
        if "scene" not in s:
            bad.append(f"{shot['id']} {time}: no scene light declared")
            continue
        if shot["technique"] == "lightpainting":
            continue
        error = em.exposure_error_stops(s)
        if abs(error) > em.TOLERANCE_STOPS:
            bad.append(f"{shot['id']} {time}: {error:+.1f} stops against {s['scene']}")
    return bad


def test_every_planned_exposure_matches_its_scene_light():
    assert exposure_violations(load_plans()) == []


def test_light_painting_keeps_the_ambient_light_well_under_the_exposure():
    for shot, time, s in viable_slots(load_plans()):
        if shot["technique"] != "lightpainting":
            continue
        ev = em.settings_ev100(s["aperture"], s["shutter"], s["iso"])
        ambient_high = em.scene_range(s["scene"])[1]
        assert ev - ambient_high >= em.LIGHTPAINTING_AMBIENT_MARGIN_STOPS, (shot["id"], time)


def test_scene_table_follows_the_published_ev_values():
    # ANSI PH2.7-1986 as reproduced in Wikipedia "Exposure value", table 2.
    assert em.scene_range("sol_pleno") == (15, 15)
    assert em.scene_range("sombra_abierta") == (12, 12)
    assert em.scene_range("antes_ocaso") == (12, 14)
    assert em.scene_range("tras_ocaso") == (9, 11)
    assert em.scene_range("interior_casa") == (5, 7)
    assert em.scene_range("iluminado_focos") == (3, 5)


def test_exposure_error_has_the_photographic_sign():
    # f/16 1/125 ISO 100 is the classic full-sun exposure (EV 15). On a lit
    # street (EV 7-8) it is seven stops too dark; opened to f/5.6 in full sun
    # it is three stops too bright.
    sunny = {"aperture": "f/16", "shutter": "1/125", "iso": 100, "scene": "sol_pleno"}
    assert em.exposure_error_stops(sunny) == pytest.approx(0, abs=0.05)
    assert em.exposure_error_stops({**sunny, "scene": "calle_noche"}) < -6
    assert em.exposure_error_stops({**sunny, "aperture": "f/5.6"}) == pytest.approx(3, abs=0.1)


# --------------------------------------------------------------------------- P02


def test_nd_filters_are_stock_densities_and_the_notes_name_them():
    for shot, time, s in viable_slots(load_plans()):
        stops = s.get("nd_stops", 0)
        if not stops:
            assert not re.search(r"\bsin (filtro|ND)\b.*\bND de \d+ pasos\b", s["notes"]), (shot["id"], time)
            continue
        assert stops in STOCK_ND_STOPS, (shot["id"], time, stops)
        assert f"ND de {stops} pasos" in s["notes"], (shot["id"], time, s["notes"])
        assert not re.search(r"\bsin (filtro|ND)\b", s["notes"]), (shot["id"], time, s["notes"])


def test_nd_names_follow_the_filter_factor_convention():
    assert [em.nd_name(n) for n in (2, 3, 6, 10)] == ["ND4", "ND8", "ND64", "ND1000"]
    assert em.nd_label(6) == "ND de 6 pasos (ND64 · 1.8)"


def test_unviable_slots_tell_the_reader_to_move_the_shot():
    data = load_plans()
    unviable = [(shot, time, s) for shot, time, s in slots(data) if not s.get("viable", True)]
    assert unviable, "the night jumps and daylight light painting cannot be exposed as planned"
    for shot, time, s in unviable:
        assert re.search(r"no viable|pospón", s["notes"], re.I), (shot["id"], time, s["notes"])


# --------------------------------------------------------------------------- P03


def test_settings_stay_inside_camera_and_lens_limits():
    for shot, time, s in viable_slots(load_plans()):
        n = em.f_number(s["aperture"])
        assert max_aperture(s["lens"]) - 1e-9 <= n <= 22, (shot["id"], time, s["lens"], s["aperture"])
        t = em.shutter_seconds(s["shutter"])
        assert 1 / 4000 - 1e-12 <= t, (shot["id"], time)
        assert t <= 30 or "Bulb" in s["shutter"], (shot["id"], time)
        assert 100 <= s["iso"] <= 25600, (shot["id"], time)


SHUTTER_DISPLAY = re.compile(r'^(1/\d+|\d+(\.\d)?"|Bulb \d+")$')


def test_shutter_speeds_are_written_the_way_the_camera_shows_them():
    # The 6D shows fractions as 1/250 and whole seconds with a seconds mark
    # (2", 30"); a bare "10" reads as 1/10 on the top LCD.
    for shot, time, s in slots(load_plans()):
        assert SHUTTER_DISPLAY.match(s["shutter"]), (shot["id"], time, s["shutter"])


def test_headline_settings_are_one_of_the_time_slots():
    for _plan, shot in all_shots(load_plans()):
        headline = (shot["aperture"], shot["shutter"], shot["iso"])
        options = [(s["aperture"], s["shutter"], s["iso"]) for s in shot["settings_by_time"].values() if s.get("viable", True)]
        assert headline in options, shot["id"]


# --------------------------------------------------------------------------- P04

ENVELOPES = {
    "congelado": lambda n, t: t <= 1 / 1000,
    "barrido": lambda n, t: 1 / 160 <= t <= 1 / 15,
    "fantasma": lambda n, t: 0.5 <= t <= 8,
    "larga_exp": lambda n, t: t >= 5,
    "zooming": lambda n, t: 1 <= t <= 4,
    "lightpainting": lambda n, t: t >= 5,
    "poca_pdc": lambda n, t: n <= 2.8,
    "mucha_pdc": lambda n, t: n >= 8,
}


def test_every_setting_keeps_the_variable_that_defines_its_technique():
    for shot, time, s in viable_slots(load_plans()):
        n, t = em.f_number(s["aperture"]), em.shutter_seconds(s["shutter"])
        assert ENVELOPES[shot["technique"]](n, t), (shot["id"], time, s["aperture"], s["shutter"])


# --------------------------------------------------------------------------- P05

DOF_CM = re.compile(r"(?:PDC|profundidad de campo)(?: total)?(?: es de| de)?\s*[≈~]\s*(\d+(?:[.,]\d+)?)\s*cm"
                    r"|[≈~]\s*(\d+(?:[.,]\d+)?)\s*cm de (?:PDC|profundidad de campo)", re.I)
HYPERFOCAL = re.compile(r"hiperfocal[^.\d]{0,25}?[≈~]\s*(\d+(?:[.,]\d+)?)\s*m", re.I)
NEAR_TO_INF = re.compile(r"desde\s*[≈~]\s*(\d+(?:[.,]\d+)?)\s*m (?:hasta el|a) infinito", re.I)
COVERS = re.compile(r"cubre (?:sólo )?[≈~]\s*(\d+(?:[.,]\d+)?)(?:\s*×\s*(\d+(?:[.,]\d+)?))?\s*m", re.I)


def claim_aperture(shot: dict) -> float:
    match = re.search(r"f/(\d+(?:\.\d+)?)", shot["reasoning"])
    return float(match.group(1)) if match else em.f_number(shot["aperture"])


def optical_claim_violations(data: dict) -> list[str]:
    bad = []
    for _plan, shot in all_shots(data):
        text, focal, n = shot["reasoning"], headline_focal_mm(shot), claim_aperture(shot)
        dof = op.depth_of_field(focal, n, shot["subject_distance_m"])
        for match in DOF_CM.finditer(text):
            claimed = number(match.group(1) or match.group(2)) / 100
            if abs(claimed - dof["total"]) > 0.15 * dof["total"]:
                bad.append(f"{shot['id']}: claims DoF {claimed*100:.0f} cm, model {dof['total']*100:.0f} cm")
        for match in HYPERFOCAL.finditer(text):
            claimed = number(match.group(1))
            if abs(claimed - dof["hyperfocal"]) > 0.1 * dof["hyperfocal"]:
                bad.append(f"{shot['id']}: claims hyperfocal {claimed} m, model {dof['hyperfocal']:.2f} m")
        for match in NEAR_TO_INF.finditer(text):
            claimed = number(match.group(1))
            if not math.isinf(dof["far"]) or abs(claimed - dof["near"]) > 0.1 * dof["near"]:
                bad.append(f"{shot['id']}: claims {claimed} m to infinity, model {dof['near']:.2f}–{dof['far']} m")
        for match in COVERS.finditer(text):
            width = shot["subject_distance_m"] * SENSOR_W_MM / focal
            if abs(number(match.group(1)) - width) > 0.05 * width:
                bad.append(f"{shot['id']}: claims {match.group(1)} m wide, sensor gives {width:.1f} m")
            if match.group(2):
                height = shot["subject_distance_m"] * SENSOR_H_MM / focal
                if abs(number(match.group(2)) - height) > 0.05 * height:
                    bad.append(f"{shot['id']}: claims {match.group(2)} m high, sensor gives {height:.1f} m")
    return bad


def test_optical_claims_in_the_explanations_match_the_physics():
    assert optical_claim_violations(load_plans()) == []


def test_the_claim_checker_sees_the_claims_it_is_meant_to_check():
    # Guard against a regex that silently matches nothing.
    data = load_plans()
    texts = " ".join(shot["reasoning"] for _plan, shot in all_shots(data))
    assert len(DOF_CM.findall(texts)) >= 6
    assert len(HYPERFOCAL.findall(texts)) >= 2
    assert len(COVERS.findall(texts)) >= 5


def test_explanations_do_not_teach_the_compression_or_zoom_burst_myths():
    # Perspective depends on camera position only (Wikipedia, "Perspective
    # distortion"); a zoom burst scales the image about its centre, so streak
    # length grows with distance from the frame centre, not from the camera.
    myths = (
        re.compile(r"\d+ ?mm comprime", re.I),
        re.compile(r"lejan[oa] se estira más", re.I),
        re.compile(r"diferentes distancias[^.]*estallidos de diferente longitud", re.I),
    )
    for _plan, shot in all_shots(load_plans()):
        for myth in myths:
            assert not myth.search(shot["reasoning"]), (shot["id"], myth.pattern)


# --------------------------------------------------------------------------- P06


def test_published_json_is_the_canonical_plan_data():
    import plans_data

    canonical = json.loads(json.dumps(plans_data.to_dict(), ensure_ascii=False))
    assert load_plans() == canonical
