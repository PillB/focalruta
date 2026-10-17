"""Scene light and exposure arithmetic for the photo planner.

One place defines how bright a planned scene is expected to be and how a
camera setting relates to it, so the plan data, the diagrams and the tests
agree on what "correctly exposed" means.

Exposure value at ISO 100: EV100 = log2(N^2 / t) - log2(ISO / 100).
A setting exposes a scene correctly when its EV100 plus the density of any
neutral-density filter (in stops) equals the scene's EV100. Scene values come
from the standard table of typical exposure values published with ANSI
PH2.7-1986 and reproduced in the Wikipedia article "Exposure value"; the two
rows marked ``estimate`` are not in that table and say so on the page.
"""
from __future__ import annotations

import math
import re

# key: (low EV100, high EV100, Spanish label, provenance)
SCENE_LIGHT: dict[str, tuple[float, float, str, str]] = {
    "sol_pleno": (15, 15, "sol pleno o levemente velado", "ANSI PH2.7 · escena típica a pleno sol"),
    "sol_velado": (14, 14, "sol velado", "ANSI PH2.7 · sol con bruma"),
    "nublado_claro": (13, 13, "nublado claro (garúa sin sombras)", "ANSI PH2.7 · nublado brillante"),
    "sombra_abierta": (12, 12, "sombra abierta o nublado denso", "ANSI PH2.7 · sombra abierta con cielo despejado"),
    "antes_ocaso": (12, 14, "sol bajo, antes del ocaso", "ANSI PH2.7 · justo antes del ocaso"),
    "tras_ocaso": (9, 11, "hora azul, justo después del ocaso", "ANSI PH2.7 · justo después del ocaso"),
    "galeria": (8, 11, "interior muy iluminado", "ANSI PH2.7 · galerías"),
    "calle_noche": (7, 8, "calle iluminada de noche", "ANSI PH2.7 · escenas de calle nocturnas"),
    "oficina": (7, 8, "interior con luz de ventana", "ANSI PH2.7 · oficinas y áreas de trabajo"),
    "interior_casa": (5, 7, "interior de casa con lámparas", "ANSI PH2.7 · interiores de vivienda"),
    "trafico_noche": (5, 5, "tráfico de noche", "ANSI PH2.7 · tráfico vehicular nocturno"),
    "iluminado_focos": (3, 5, "parque o monumento con faroles", "ANSI PH2.7 · edificios y monumentos iluminados"),
    "luces_lejanas": (2, 2, "sólo luces lejanas", "ANSI PH2.7 · vistas lejanas de edificios iluminados"),
    "oscuridad": (-3, -1, "oscuridad sin faroles cercanos", "estimate · sin fila en la tabla ANSI; equivale a paisaje con luna"),
}

# How much a planned setting may differ from the scene before it stops being a
# useful starting point. One stop is what a single test frame and the
# histogram can recover without changing the technique.
TOLERANCE_STOPS = 1.0

# Light painting wants the ambient light to stay at least this far under the
# exposure, so only the moving light source draws.
LIGHTPAINTING_AMBIENT_MARGIN_STOPS = 3.0

THIRD_STOP_SHUTTERS = (
    "1/4000", "1/3200", "1/2500", "1/2000", "1/1600", "1/1250", "1/1000", "1/800", "1/640",
    "1/500", "1/400", "1/320", "1/250", "1/200", "1/160", "1/125", "1/100", "1/80", "1/60",
    "1/50", "1/40", "1/30", "1/25", "1/20", "1/15", "1/13", "1/10", "1/8", "1/6", "1/5",
    "1/4", "0.3", "0.4", "0.5", "0.6", "0.8", "1", "1.3", "1.6", "2", "2.5", "3.2", "4", "5",
    "6", "8", "10", "13", "15", "20", "25", "30",
)
THIRD_STOP_ISOS = (100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000,
                   2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000, 20000, 25600)


def f_number(aperture: str | float) -> float:
    """'f/5.6' -> 5.6."""
    if isinstance(aperture, (int, float)):
        return float(aperture)
    match = re.search(r"(\d+(?:\.\d+)?)", aperture)
    if not match:
        raise ValueError(f"no f-number in {aperture!r}")
    return float(match.group(1))


def shutter_seconds(shutter: str | float) -> float:
    """'1/250' -> 0.004, '2"' -> 2, 'Bulb 20"' -> 20, '10 s' -> 10."""
    if isinstance(shutter, (int, float)):
        return float(shutter)
    text = shutter.replace("Bulb", "").replace('"', "").replace("s", "").strip()
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return float(numerator) / float(denominator)
    return float(text.replace(",", "."))


def settings_ev100(aperture, shutter, iso) -> float:
    """EV at ISO 100 that a camera setting is calibrated for."""
    n = f_number(aperture)
    return math.log2(n * n / shutter_seconds(shutter)) - math.log2(float(iso) / 100.0)


def scene_range(scene: str) -> tuple[float, float]:
    low, high, _label, _source = SCENE_LIGHT[scene]
    return low, high


def exposure_error_stops(setting: dict) -> float:
    """Signed stops by which a setting misses its scene; 0 inside the scene range.

    Positive means the frame would come out too bright (overexposed).
    """
    low, high = scene_range(setting["scene"])
    effective = settings_ev100(setting["aperture"], setting["shutter"], setting["iso"]) + setting.get("nd_stops", 0)
    if effective < low:
        return low - effective
    if effective > high:
        return high - effective
    return 0.0


def nd_name(stops: int) -> str:
    """Factor naming used on filter rings: 3 stops -> ND8, 10 stops -> ND1000."""
    if stops <= 0:
        return ""
    factor = 2 ** stops
    return "ND1000" if stops == 10 else f"ND{factor}"


def nd_label(stops: int) -> str:
    """'ND de 6 pasos (ND64 · 1.8)'."""
    if stops <= 0:
        return ""
    density = round(0.301 * stops, 1)
    return f"ND de {stops} pasos ({nd_name(stops)} · {density:.1f})"
