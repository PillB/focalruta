"""Y05: the setting for a sunny day slot when Lima's winter sky is grey instead.

From late May to mid November a stratocumulus deck covers Lima most mornings: Jorge Chávez
records 28-60 hours of sun a month from June to October against 185 in January (DWD
1991-2020 normals, in the Wikipedia article "Lima"), and the cloud is thickest early in the
day (Garreaud et al. 2001, BAMS, EPIC Stratocumulus). A day slot planned for sun is then one
or two stops too dark. The garúa's bright, even grey is the model's `nublado_claro` row,
EV 13 at ISO 100.

garua_setting() picks, among the settings the camera and lens can take, the one that
exposes that sky and changes least from the planned slot. What makes the technique's effect
is held: the aperture for depth of field, the time for motion and long exposure; freezing
may slow only to 1/2000 s and open only to f/2.8, the plans' own limits for it. Handheld
times stay at 1/(2 x focal) or faster, the rule the 100 % check needs, with the 35 mm's
stabiliser counted at 3 of its 4 stops.
"""
from __future__ import annotations

import math
import re

import exposure_model as em

GARUA_SCENE = "nublado_claro"
SUNNY_SCENES = ("sol_pleno", "sol_velado")
APERTURES = (1.8, 2, 2.2, 2.5, 2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1, 8, 9, 10, 11, 13, 14, 16)
STOCK_ND = (0, 2, 3, 6, 10)
TIME_HELD = {"barrido", "fantasma", "larga_exp", "zooming", "lightpainting"}
# What a stop of change costs each technique; a variable not listed is held. Each variable
# changed costs CHANGE more, so one turn of one dial beats two small ones in the field.
CHANGE = 0.5
COSTS = {
    "mucha_pdc": {"shutter": 1.0, "iso": 1.1},
    "poca_pdc": {"shutter": 1.0, "iso": 1.1},
    "congelado": {"shutter": 1.0, "aperture": 1.05, "iso": 1.2},
}
LONG_COSTS = {"aperture": 1.0, "nd": 1.5, "iso": 1.3}
STABILISED_STOPS = {35: 3}  # EF 35 mm f/2 IS USM: 4 stops (Canon), 3 counted


def lens_widest(lens: str) -> float:
    """Widest f-number of the kit's lens at the slot's focal length."""
    if "35-80" in lens:
        at = re.search(r"@(\d+)", lens)
        focal = int(at.group(1)) if at else 80
        return 4.0 if focal <= 35 else 4.5 if focal <= 50 else 5.6
    return {"35": 2.0, "50": 1.8, "85": 1.8}[re.match(r"\d+", lens).group(0)]


def lens_focal(lens: str) -> int:
    at = re.search(r"@(\d+)", lens)
    if at:
        return int(at.group(1))
    return 80 if "35-80" in lens else int(re.match(r"\d+", lens).group(0))


def hand_limit(lens: str) -> float:
    """Slowest handheld time on the dial that passes the 100 % check."""
    focal = lens_focal(lens)
    stops = 0 if "35-80" in lens else STABILISED_STOPS.get(focal, 0)
    target = 2 ** stops / (2 * focal)
    return min((em.shutter_seconds(s) for s in em.THIRD_STOP_SHUTTERS), key=lambda t: abs(math.log2(t / target)))


def _stops(a: float, b: float) -> float:
    return abs(math.log2(a / b))


def _shutters(technique: str, slot: dict) -> list[str]:
    planned = em.shutter_seconds(slot["shutter"])
    if technique in TIME_HELD:
        return [slot["shutter"]]
    if technique == "congelado":
        top = 1 / 2000
    else:
        top = max(planned, hand_limit(slot["lens"]))
    return [s for s in em.THIRD_STOP_SHUTTERS if em.shutter_seconds(s) <= top + 1e-12]


def _apertures(technique: str, slot: dict) -> list[float]:
    planned = em.f_number(slot["aperture"])
    if technique in ("mucha_pdc", "poca_pdc"):
        return [planned]
    widest = lens_widest(slot["lens"])
    if technique == "congelado":
        widest = max(widest, 2.8)
    return [n for n in APERTURES if n >= widest - 1e-9]


def _isos(technique: str) -> tuple[int, ...]:
    top = 400 if technique in TIME_HELD else 6400
    return tuple(i for i in em.THIRD_STOP_ISOS if i <= top)


def _cost(technique: str, slot: dict, n: float, shutter: str, iso: int, nd: int) -> float:
    weights = COSTS.get(technique, LONG_COSTS)
    planned_nd = slot.get("nd_stops", 0)
    moved = {
        "aperture": _stops(n, em.f_number(slot["aperture"])),
        "shutter": _stops(em.shutter_seconds(shutter), em.shutter_seconds(slot["shutter"])),
        "iso": max(0.0, math.log2(iso / slot["iso"])) if iso >= slot["iso"] else math.inf,
    }
    cost = sum(weights.get(key, 0) * stops + (CHANGE if stops > 1e-9 else 0) for key, stops in moved.items())
    return cost + (weights.get("nd", 0) + CHANGE if nd != planned_nd else 0)


def garua_setting(technique: str, slot: dict) -> dict:
    """The planned slot's setting for EV 13 under the garúa, changing what matters least."""
    target = em.scene_range(GARUA_SCENE)[0]
    best = None
    for n in _apertures(technique, slot):
        for shutter in _shutters(technique, slot):
            for iso in _isos(technique):
                for nd in (x for x in STOCK_ND if x <= slot.get("nd_stops", 0)):
                    miss = abs(em.settings_ev100(n, shutter, iso) + nd - target)
                    if miss > 1 / 6 + 1e-9:
                        continue
                    key = (_cost(technique, slot, n, shutter, iso, nd) + 3 * miss, n, iso)
                    if best is None or key < best[0]:
                        best = (key, n, shutter, iso, nd)
    if best is None:
        raise ValueError(f"no setting exposes the garúa for {technique} {slot}")
    _key, n, shutter, iso, nd = best
    out = {"aperture": f"f/{n:g}", "shutter": shutter, "iso": iso, "scene": GARUA_SCENE}
    if nd:
        out["nd_stops"] = nd
    return out


def _change(key: str, planned: dict, garua: dict) -> str | None:
    if key == "nd_stops":
        before, after = planned.get("nd_stops", 0), garua.get("nd_stops", 0)
        if before == after:
            return None
        return "quita el ND" if not after else f"cambia al {em.nd_label(after)}"
    if planned[key] == garua[key]:
        return None
    if key == "aperture":
        return f"abre a {garua['aperture']}"
    if key == "shutter":
        return f"baja la velocidad a {garua['shutter']} s"
    return f"sube a ISO {garua['iso']}"


STOPS_IN_WORDS = {1: "un paso", 2: "dos pasos", 3: "tres pasos"}


def garua_note(planned: dict, garua: dict) -> str:
    """'Con garúa (cielo gris parejo, de junio a octubre) llega un paso menos de luz: …'."""
    stops = round(em.scene_range(planned["scene"])[0] - em.scene_range(GARUA_SCENE)[0])
    changes = [c for c in (_change(k, planned, garua) for k in ("aperture", "shutter", "iso", "nd_stops")) if c]
    listed = changes[0] if len(changes) == 1 else f"{', '.join(changes[:-1])} y {changes[-1]}"
    return (f"Con garúa (cielo gris parejo, de junio a octubre) llega {STOPS_IN_WORDS[stops]} menos de luz: "
            f"{listed}; lo demás igual.")


def add_garua(technique: str, day: dict) -> None:
    """Give a sunny, viable day slot its garúa setting and say it in the slot's note."""
    if day.get("scene") not in SUNNY_SCENES or day.get("viable", True) is False:
        return
    day["garua"] = garua_setting(technique, day)
    day["notes"] = f"{day['notes']} {garua_note(day, day['garua'])}"
