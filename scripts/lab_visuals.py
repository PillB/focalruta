#!/usr/bin/env python3
"""Geometry for every interactive lab and every technique diagram.

Each lab ships a table of precomputed states: the browser only applies
attributes that Python already calculated with `optics_physics`, so the values
pytest checks are the values the page draws.

Table entry shape: {"a": [[element_id, attribute, value], ...], "t": readout}.
The key of a state is the joined value of its controls, in declaration order.
"""
from __future__ import annotations

import math
import re
from html import escape

import optics_physics as op

ACCENT = "#b84c32"
GREEN = "#176b55"
STONE = "#80958d"
INK = "#10211d"
SUN = "#f2cf45"

# ---------------------------------------------------------------------------
# helpers


def _fmt(value: float, digits: int = 1) -> str:
    text = f"{value:.{digits}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


def _round(value: float, digits: int = 2) -> float:
    return round(value, digits)


def _with_text_scale(svg: str, divisor: float) -> str:
    """Size SVG text in user units so it renders at a constant on-screen size."""
    width = float(re.search(r'viewBox="0 0 ([\d.]+)', svg).group(1))
    return svg.replace("<svg ", f'<svg font-size="{_round(width / divisor)}" ', 1)


def _ramp(luminance: float) -> str:
    """Map a normalized diffuse response to a warm stone tone."""
    level = max(0.0, min(1.0, luminance))
    red = int(56 + 199 * level)
    green = int(70 + 143 * level)
    blue = int(66 + 91 * level)
    return f"#{red:02x}{green:02x}{blue:02x}"


def _grey(level: float) -> str:
    value = int(max(0.0, min(1.0, level)) * 255)
    return f"#{value:02x}{value:02x}{value:02x}"


# ---------------------------------------------------------------------------
# Lab 1 · position before focal

PERSPECTIVE_FOCALS = (35, 50, 85)
PERSPECTIVE_POSITIONS = tuple(range(2, 8))
PERSPECTIVE_HEIGHT_M = 1.8
PERSPECTIVE_FRAME_PX = 136.0
PLAN_ORIGIN = (18.0, 80.0)
PLAN_PX_PER_M = 15.0
FRAME_BASE_Y = 148.0


def _perspective_state(focal: int, position: int) -> dict:
    """The right-hand panel is the frame itself: the subject may overflow it."""
    near = op.projected_height(PERSPECTIVE_HEIGHT_M, position, focal, op.FULL_FRAME_HEIGHT_MM, PERSPECTIVE_FRAME_PX)
    far = op.projected_height(PERSPECTIVE_HEIGHT_M, position + 4, focal, op.FULL_FRAME_HEIGHT_MM, PERSPECTIVE_FRAME_PX)
    half = op.half_angle_of_view_deg(focal, op.FULL_FRAME_WIDTH_MM)
    ox, oy = PLAN_ORIGIN
    # keep the cone inside its panel: 70 px of vertical room, 188 px of horizontal room
    radius = min(70.0 / math.sin(math.radians(half)), 188.0 / math.cos(math.radians(half)))
    edge_x = ox + radius * math.cos(math.radians(half))
    edge_y = radius * math.sin(math.radians(half))
    cone = f"M{ox} {oy}L{_round(edge_x)} {_round(oy - edge_y)}M{ox} {oy}L{_round(edge_x)} {_round(oy + edge_y)}"
    near_x = ox + position * PLAN_PX_PER_M
    far_x = ox + (position + 4) * PLAN_PX_PER_M
    attrs = [
        ["perspective-fov", "d", cone],
        ["perspective-plan-near", "x1", _round(near_x)],
        ["perspective-plan-near", "x2", _round(near_x)],
        ["perspective-plan-far", "x1", _round(far_x)],
        ["perspective-plan-far", "x2", _round(far_x)],
        ["perspective-near", "height", _round(near)],
        ["perspective-near", "y", _round(FRAME_BASE_Y - near)],
        ["perspective-near", "width", _round(near * 0.5)],
        ["perspective-near", "x", _round(292 - near * 0.25)],
        ["perspective-far", "height", _round(far)],
        ["perspective-far", "y", _round(FRAME_BASE_Y - far)],
        ["perspective-far", "width", _round(far * 0.5)],
        ["perspective-far", "x", _round(392 - far * 0.25)],
    ]
    readout = (
        f"{position} m · {focal} mm. Semiángulo de visión {_fmt(half)}°: alargar la focal cierra el campo. "
        f"La puerta cercana ocupa el {_fmt(near / PERSPECTIVE_FRAME_PX * 100, 0)} % del alto del encuadre y se proyecta "
        f"{_fmt(near / far, 2)}× más alta que la de atrás. Esa relación sólo cambia si mueves los pies."
    )
    if near > PERSPECTIVE_FRAME_PX:
        readout += " No cabe: desde aquí, con esta focal, tendrías que retroceder."
    return {"a": attrs, "t": readout}


def perspective_table() -> dict:
    return {
        f"{focal}|{position}": _perspective_state(focal, position)
        for focal in PERSPECTIVE_FOCALS
        for position in PERSPECTIVE_POSITIONS
    }


def perspective_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="pinhole-projection" role="img" '
        'aria-label="Planta con el cono de visión real y, al lado, el encuadre con las dos puertas proyectadas" '
        'viewBox="0 0 440 160">'
        '<rect class="comparison-pane" x="4" y="4" width="212" height="152"/>'
        '<rect class="comparison-pane" x="226" y="8" width="210" height="140"/>'
        '<text x="14" y="20">PLANTA</text><text x="236" y="24">ENCUADRE COMPLETO</text>'
        f'<path id="perspective-fov" d="M18 80L154 10M18 80L154 150" fill="none" stroke="{GREEN}" stroke-width="2"/>'
        f'<line x1="18" y1="80" x2="206" y2="80" stroke="{INK}" stroke-dasharray="4 4"/>'
        f'<circle cx="18" cy="80" r="5" fill="{ACCENT}"/><text x="10" y="100">cámara</text>'
        f'<line id="perspective-plan-near" x1="78" y1="56" x2="78" y2="104" stroke="{ACCENT}" stroke-width="5"/>'
        f'<line id="perspective-plan-far" x1="138" y1="62" x2="138" y2="98" stroke="{STONE}" stroke-width="5"/>'
        '<clipPath id="perspective-frame-clip"><rect x="226" y="8" width="210" height="140"/></clipPath>'
        '<g clip-path="url(#perspective-frame-clip)">'
        f'<rect id="perspective-far" x="386" y="88" width="12" height="60" fill="{STONE}"/>'
        f'<rect id="perspective-near" x="278" y="60" width="28" height="88" fill="{ACCENT}" opacity=".92"/></g>'
        f'<line x1="230" y1="148" x2="432" y2="148" stroke="{INK}"/>'
        '<text x="266" y="158">cerca</text><text x="378" y="158">lejos</text>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 2 · levelling and convergence

VERTICAL_TILTS = tuple(range(0, 21))
VERTICAL_FOCAL = 35.0
VERTICAL_DISTANCE_M = 26.0
VERTICAL_WIDTH_M = 10.0
VERTICAL_HEIGHT_M = 12.0
VERTICAL_FRAME_PX = 120.0


def _vertical_state(tilt: int) -> dict:
    corners = op.keystone_corners(
        float(tilt), VERTICAL_WIDTH_M, VERTICAL_HEIGHT_M, VERTICAL_DISTANCE_M,
        VERTICAL_FOCAL, op.FULL_FRAME_HEIGHT_MM, VERTICAL_FRAME_PX,
    )
    bottom_w, top_w = corners["bottom_width"], corners["top_width"]
    height = corners["top_y"] - corners["bottom_y"]
    base_y, centre_x = 112.0, 110.0
    top_y = base_y - height
    points = (
        f"{_round(centre_x - top_w / 2)},{_round(top_y)} {_round(centre_x + top_w / 2)},{_round(top_y)} "
        f"{_round(centre_x + bottom_w / 2)},{_round(base_y)} {_round(centre_x - bottom_w / 2)},{_round(base_y)}"
    )
    convergence = (bottom_w - top_w) / bottom_w * 100.0
    vanishing = op.vertical_vanishing_point(float(tilt), VERTICAL_FOCAL, op.FULL_FRAME_HEIGHT_MM, VERTICAL_FRAME_PX)
    slope_x = (top_w - bottom_w) / 2.0
    guide = (
        f"M{_round(centre_x - bottom_w / 2)} {base_y}L{_round(centre_x - bottom_w / 2 - slope_x * 2.4)} {_round(base_y - height * 3.4)}"
        f"M{_round(centre_x + bottom_w / 2)} {base_y}L{_round(centre_x + bottom_w / 2 + slope_x * 2.4)} {_round(base_y - height * 3.4)}"
    )
    if vanishing is None:
        readout = (
            "Cámara nivelada: las verticales del edificio quedan paralelas al sensor y no convergen. "
            "Su punto de fuga está en el infinito."
        )
        guide_opacity = 0.0
    else:
        frames = vanishing / VERTICAL_FRAME_PX
        readout = (
            f"Inclinación {tilt}°: las verticales convergen un {_fmt(convergence)} % y su punto de fuga cae a "
            f"{_fmt(frames)} alturas de encuadre por encima del centro. Cuanto más inclinas, más cerca lo traes."
        )
        guide_opacity = 0.85
    return {
        "a": [
            ["vertical-building", "points", points],
            ["vertical-guides", "d", guide],
            ["vertical-guides", "opacity", _round(guide_opacity)],
        ],
        "t": readout,
    }


def vertical_table() -> dict:
    return {str(tilt): _vertical_state(tilt) for tilt in VERTICAL_TILTS}


def vertical_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="vanishing-point" role="img" '
        'aria-label="Fachada proyectada bajo inclinación, con horizonte y líneas que convergen hacia el punto de fuga" '
        'viewBox="0 0 220 120">'
        f'<line id="vertical-horizon" x1="8" y1="64" x2="212" y2="64" stroke="{ACCENT}" stroke-dasharray="5 4"/>'
        '<text x="8" y="60">horizonte</text>'
        f'<path id="vertical-guides" d="" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="3 3" opacity="0"/>'
        f'<polygon id="vertical-building" points="63,42 157,42 157,112 63,112" fill="{STONE}" stroke="{INK}" stroke-width="3"/>'
        f'<line x1="8" y1="112" x2="212" y2="112" stroke="{INK}"/>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 3 · reading order and edges

HIERARCHY_MODES = ("clean", "clutter", "human")
HIERARCHY_READING = {
    "clean": (((88, 40), "umbral"), ((150, 52), "eje"), ((110, 96), "suelo")),
    "clutter": (((186, 32), "señal"), ((88, 40), "umbral"), ((150, 52), "eje")),
    "human": (((110, 86), "gesto"), ((88, 40), "umbral"), ((165, 50), "fondo")),
}
HIERARCHY_COPY = {
    "clean": "Primera lectura: umbral y eje. Los bordes permanecen en silencio y la mirada se queda dentro.",
    "clutter": "La señal brillante del borde gana la primera lectura y el umbral pasa a segundo lugar: es competencia de borde, no ruido inevitable.",
    "human": "El gesto humano toma la primera lectura. Apruébalo sólo si su verbo cambia el significado del umbral.",
}


def _hierarchy_state(mode: str) -> dict:
    attrs = [
        ["hierarchy-clutter", "opacity", 1 if mode == "clutter" else 0.12],
        ["hierarchy-person", "opacity", 1 if mode == "human" else 0.14],
    ]
    for index, ((cx, cy), label) in enumerate(HIERARCHY_READING[mode], 1):
        attrs.append([f"hierarchy-order-{index}", "transform", f"translate({cx - 110},{cy - 60})"])
        attrs.append([f"hierarchy-order-{index}-label", "textContent", label])
    return {"a": attrs, "t": HIERARCHY_COPY[mode]}


def hierarchy_table() -> dict:
    return {mode: _hierarchy_state(mode) for mode in HIERARCHY_MODES}


def _hierarchy_marker(index: int, fill: str) -> str:
    return (
        f'<g id="hierarchy-order-{index}" transform="translate(0,0)">'
        f'<circle cx="110" cy="60" r="11" fill="{fill}"/>'
        f'<text x="110" y="64" fill="#ffffff" text-anchor="middle">{index}</text>'
        f'<text id="hierarchy-order-{index}-label" x="110" y="84" text-anchor="middle">·</text></g>'
    )


def hierarchy_svg() -> str:
    markers = "".join(_hierarchy_marker(index, fill) for index, fill in ((1, GREEN), (2, STONE), (3, ACCENT)))
    return (
        '<svg class="lab-frame" data-physics-model="layered-attention" role="img" '
        'aria-label="Orden de lectura numerado que se reordena según la variante elegida" viewBox="0 0 220 120">'
        f'<path d="M25 112V28H195V112M70 112V58H150V112" fill="none" stroke="{INK}" stroke-width="8"/>'
        f'<g id="hierarchy-clutter" opacity=".12"><rect x="176" y="18" width="34" height="22" fill="{SUN}"/>'
        f'<rect x="8" y="92" width="26" height="20" fill="{SUN}"/></g>'
        f'<g id="hierarchy-person" opacity=".14"><circle cx="110" cy="82" r="7" fill="{ACCENT}"/>'
        f'<path d="M110 90v16m0-10l-9 7m9-7l9 7" stroke="{ACCENT}" stroke-width="4"/></g>'
        f'<g id="hierarchy-reading-order">{markers}</g></svg>'
    )


# ---------------------------------------------------------------------------
# Lab 4 · direction, size and colour of the source

LIGHT_AZIMUTHS = (-70, -35, 0, 35, 70)
LIGHT_ALTITUDES = (10, 25, 45, 70)
LIGHT_SOURCES = {
    "sol": ("sol directo", op.SUN_ANGULAR_DIAMETER_DEG),
    "velado": ("sol velado", 10.0),
    "garua": ("garúa cerrada", op.OVERCAST_ANGULAR_DIAMETER_DEG),
}
LIGHT_HEIGHT_M = 8.0
LIGHT_PX_PER_M = 9.0
LIGHT_FRONT_NORMAL = 0.0
LIGHT_SIDE_NORMAL = 62.0


def _light_faces(azimuth: int, altitude: int) -> tuple[float, float]:
    irradiance = math.cos(math.radians(altitude))
    front = op.lambert_luminance(LIGHT_FRONT_NORMAL, azimuth, 0.62, 0.18, irradiance)
    side = op.lambert_luminance(LIGHT_SIDE_NORMAL, azimuth, 0.62, 0.18, irradiance)
    return front, side


def _light_shadow(azimuth: int, altitude: int, source_deg: float) -> tuple[str, str, float, float, float]:
    length_m = op.shadow_length(LIGHT_HEIGHT_M, altitude)
    length_px = min(130.0, length_m * LIGHT_PX_PER_M)
    radians = math.radians(azimuth)
    dx = -math.sin(radians) * length_px
    dy = 0.13 * math.cos(radians) * length_px
    penumbra_m = op.penumbra_width(source_deg, LIGHT_HEIGHT_M)
    penumbra_px = penumbra_m * LIGHT_PX_PER_M
    umbra = max(0.0, (length_px - penumbra_px) / length_px) if length_px else 0.0
    shadow = (
        f"78,148 146,148 {_round(146 + dx)},{_round(148 + dy)} {_round(78 + dx)},{_round(148 + dy)}"
    )
    umbra_points = (
        f"84,148 140,148 {_round(140 + dx * umbra)},{_round(148 + dy * umbra)} "
        f"{_round(84 + dx * umbra)},{_round(148 + dy * umbra)}"
    )
    return shadow, umbra_points, penumbra_m, length_m, umbra


DIFFUSE_THRESHOLD_DEG = 20.0


def _length_text(metres: float) -> str:
    return f"{_fmt(metres * 100, 0)} cm" if metres < 1.0 else f"{_fmt(metres)} m"


def _diffuse_readout(label: str, penumbra_m: float, front: float, side: float) -> str:
    return (
        f"{label}: la fuente cubre {_fmt(op.OVERCAST_ANGULAR_DIAMETER_DEG, 0)}° de cielo, así que deja de haber una "
        f"dirección única. La umbra desaparece —la penumbra sola mediría {_length_text(penumbra_m)}— y bajo el volumen "
        f"queda una oclusión suave. Las caras se igualan ({_fmt(front, 2)} y {_fmt(side, 2)}): "
        "el color y la microtextura separan materiales, no el relieve."
    )


def _light_state(azimuth: int, altitude: int, source_key: str) -> dict:
    label, source_deg = LIGHT_SOURCES[source_key]
    front, side = _light_faces(azimuth, altitude)
    shadow, umbra_points, penumbra_m, length_m, umbra = _light_shadow(azimuth, altitude, source_deg)
    diffuse = source_deg >= DIFFUSE_THRESHOLD_DEG
    if diffuse:
        ambient = 0.52
        front = side = ambient + 0.06 * math.cos(math.radians(altitude))
        shadow = "72,148 152,148 162,158 62,158"
        umbra = 0.0
        blur = 6.5
    else:
        blur = max(0.3, min(9.0, penumbra_m * LIGHT_PX_PER_M / 3.0))
    sun_x = 118 + 96 * math.sin(math.radians(azimuth))
    sun_y = 56 - 42 * math.sin(math.radians(altitude))
    brighter = "la fachada frontal" if front > side else "el lateral"
    if diffuse:
        readout = _diffuse_readout(label, penumbra_m, front, side)
    else:
        readout = (
            f"{label}, {altitude}° sobre el horizonte. La sombra mide {_length_text(length_m)} para 8 m de altura "
            f"(h/tan {altitude}°) y su borde se abre {_length_text(penumbra_m)} de penumbra. "
            f"Lambert reparte cos θ y gana {brighter}: fachada frontal {_fmt(front, 2)}, "
            f"lateral {_fmt(side, 2)}."
        )
        if umbra <= 0.05:
            readout += " La penumbra ya se come casi toda la sombra: el borde deja de ser duro."
    return {
        "a": [
            ["light-shadow", "points", shadow],
            ["light-umbra", "points", umbra_points],
            ["light-umbra", "opacity", _round(0.72 * umbra)],
            ["light-front", "fill", _ramp(front)],
            ["light-side", "fill", _ramp(side)],
            ["light-penumbra-blur", "stdDeviation", _round(blur)],
            ["light-sun", "cx", _round(sun_x)],
            ["light-sun", "cy", _round(sun_y)],
            ["light-sun", "r", _round(4 + min(source_deg, 24.0) / 3)],
            ["light-direction", "x1", _round(sun_x)],
            ["light-direction", "y1", _round(sun_y)],
            ["light-direction", "x2", _round(112 + (sun_x - 112) * 0.28)],
            ["light-direction", "y2", _round(84 + (sun_y - 84) * 0.06)],
        ],
        "t": readout,
    }


def light_table() -> dict:
    return {
        f"{azimuth}|{altitude}|{source}": _light_state(azimuth, altitude, source)
        for azimuth in LIGHT_AZIMUTHS
        for altitude in LIGHT_ALTITUDES
        for source in LIGHT_SOURCES
    }


def light_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="lambert-shadow" role="img" '
        'aria-label="Cielo con la posición del sol, volumen sombreado por la ley del coseno y sombra con umbra y penumbra" '
        'viewBox="0 0 240 180">'
        '<defs><filter id="light-penumbra" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur id="light-penumbra-blur" stdDeviation="1.2"/></filter></defs>'
        '<rect x="0" y="0" width="240" height="64" fill="#eef3f4"/>'
        '<text x="6" y="12">izquierda</text><text x="196" y="12">derecha</text>'
        f'<line x1="0" y1="64" x2="240" y2="64" stroke="{INK}" stroke-dasharray="3 3" opacity=".35"/>'
        f'<line id="light-direction" x1="60" y1="30" x2="112" y2="80" stroke="{SUN}" stroke-width="3" stroke-dasharray="6 4"/>'
        f'<circle id="light-sun" cx="60" cy="30" r="6" fill="{SUN}"/>'
        f'<line x1="8" y1="148" x2="232" y2="148" stroke="{INK}"/>'
        f'<polygon id="light-shadow" points="78,148 146,148 190,160 122,160" fill="#2b3a35" filter="url(#light-penumbra)"/>'
        f'<polygon id="light-umbra" points="84,148 140,148 178,158 122,158" fill="#16211e" opacity=".72"/>'
        f'<polygon id="light-side" points="146,148 178,138 178,72 146,80" fill="#6f4230"/>'
        f'<rect id="light-front" x="78" y="80" width="68" height="68" fill="#c66b3d"/>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 6 · negative space and edge discipline

NEGATIVE_MARGINS = tuple(range(0, 45, 5))
NEGATIVE_TANGENCY_PX = 4.0


def _negative_state(margin: int) -> dict:
    width = 168.0 - margin * 2.6
    height = 96.0 - margin * 1.7
    left = 110.0 - width / 2
    top = 62.0 - height / 2
    gap_left = left - 8.0
    gap_right = 196.0 - (left + width)
    tangent = gap_left < NEGATIVE_TANGENCY_PX or gap_right < NEGATIVE_TANGENCY_PX
    readout = (
        f"Margen {margin} px. El sujeto deja {_fmt(gap_left, 0)} px al borde izquierdo y "
        f"{_fmt(gap_right, 0)} px al objeto que compite en el borde derecho."
    )
    readout += (
        " Tangencia: dos contornos casi se tocan y la mirada se escapa por ahí. Entra entero o sal entero."
        if tangent
        else " Sin tangencias: el vacío sostiene la figura en lugar de decorarla."
    )
    return {
        "a": [
            ["negative-subject", "x", _round(left)],
            ["negative-subject", "y", _round(top)],
            ["negative-subject", "width", _round(width)],
            ["negative-subject", "height", _round(height)],
            ["negative-warning", "opacity", 1 if tangent else 0],
            ["negative-subject", "stroke", ACCENT if tangent else INK],
        ],
        "t": readout,
    }


def negative_table() -> dict:
    return {str(margin): _negative_state(margin) for margin in NEGATIVE_MARGINS}


def negative_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="edge-competition" role="img" '
        'aria-label="Sujeto dentro del encuadre con aviso de tangencia cuando roza un borde" viewBox="0 0 220 120">'
        f'<rect x="8" y="8" width="204" height="104" fill="none" stroke="{INK}" stroke-dasharray="4 4"/>'
        f'<rect x="196" y="30" width="16" height="60" fill="{SUN}"/><text x="150" y="24">compite</text>'
        f'<rect id="negative-subject" x="26" y="14" width="168" height="96" fill="{STONE}" stroke="{INK}" stroke-width="3"/>'
        f'<g id="negative-warning" opacity="0"><rect x="8" y="8" width="204" height="104" fill="none" '
        f'stroke="{ACCENT}" stroke-width="4"/><text x="14" y="106" fill="{ACCENT}">tangencia</text></g>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 7 · layers, depth and aerial perspective

DEPTH_HAZE = (0, 15, 30, 45, 60, 75, 90)
DEPTH_PLANES = ((8.0, "primer plano"), (60.0, "dispositivo"), (400.0, "fondo"))


def _depth_state(haze: int) -> dict:
    attrs = []
    contrasts = []
    for index, (distance, _label) in enumerate(DEPTH_PLANES, 1):
        contrast = op.aerial_contrast(distance, haze / 100.0)
        contrasts.append(contrast)
        attrs.append([f"depth-plane-{index}", "fill", _grey(0.92 - 0.62 * contrast)])
        attrs.append([f"depth-plane-{index}", "opacity", _round(0.35 + 0.65 * contrast)])
    separation = contrasts[0] - contrasts[-1]
    readout = (
        f"Bruma {haze} %. El contraste que sobrevive cae de {_fmt(contrasts[0], 2)} a 8 m hasta "
        f"{_fmt(contrasts[-1], 2)} a 400 m: exp(−bruma·d/200 m). "
    )
    readout += (
        "La separación entre planos es suficiente para leer profundidad."
        if separation > 0.25
        else "Los planos se están igualando: sin solape no habrá profundidad, así que busca una posición que superponga capas."
    )
    return {"a": attrs, "t": readout}


def depth_table() -> dict:
    return {str(haze): _depth_state(haze) for haze in DEPTH_HAZE}


def depth_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="aerial-perspective" role="img" '
        'aria-label="Tres planos superpuestos cuyo contraste decae con la distancia" viewBox="0 0 220 120">'
        '<defs><linearGradient id="depth-haze-gradient" x1="0" y1="1" x2="0" y2="0">'
        '<stop offset="0" stop-color="#eef1ee" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#eef1ee" stop-opacity=".8"/></linearGradient></defs>'
        f'<rect id="depth-plane-3" x="18" y="18" width="184" height="66" fill="#9aa6a2"/>'
        f'<polygon id="depth-plane-2" points="46,112 46,44 138,32 138,112" fill="#7d8d87"/>'
        f'<polygon id="depth-plane-1" points="8,112 8,74 92,60 92,112" fill="#41524d"/>'
        '<rect x="18" y="18" width="184" height="94" fill="url(#depth-haze-gradient)"/>'
        f'<line x1="8" y1="112" x2="212" y2="112" stroke="{INK}"/>'
        '<text x="12" y="108">8 m</text><text x="100" y="46">60 m</text><text x="168" y="30">400 m</text>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 5 · one scene, five decisions

COMPOSITION_VARIANTS = (
    ("default-postcard", "Postal: eje central y edificio completo. Es legible, pero la relación urbana sigue siendo genérica."),
    ("changed-position", "Posición: el desplazamiento lateral abre el umbral y aparecen solapes nuevos entre planos."),
    ("fixed-position-focal", "Focal desde la misma posición: cambia el recorte, no la relación entre los planos. Compáralo con la variante anterior."),
    ("human-presence", "Presencia: el gesto suma sólo si demuestra cómo se usa el espacio. Compara también la versión vacía."),
    ("light-weather", "Luz y clima: otra dirección o la garúa separan material y volumen sin mover la geometría."),
)
COMPOSITION_GLASS_ANGLE_DEG = 75.0
COMPOSITION_EXPOSURE_EV = -0.5


def composition_reflectance() -> float:
    return op.schlick_reflectance(COMPOSITION_GLASS_ANGLE_DEG)


def composition_halo_px() -> float:
    return op.halo_radius(1.0, COMPOSITION_EXPOSURE_EV, 26.0)


def _composition_state(variant: str, copy: str) -> dict:
    attrs = [[f"composition-state-{item}", "display", "inline" if item == variant else "none"] for item, _ in COMPOSITION_VARIANTS]
    attrs.append(["composition-fixed-position", "opacity", 1 if variant == "fixed-position-focal" else 0])
    return {"a": attrs, "t": copy}


def composition_table() -> dict:
    return {variant: _composition_state(variant, copy) for variant, copy in COMPOSITION_VARIANTS}


def composition_svg() -> str:
    reflect = _round(composition_reflectance(), 3)
    halo = _round(composition_halo_px())
    return (
        '<svg id="composition-frame" class="lab-frame" role="img" '
        'aria-label="Comparación antes y después de cinco decisiones aisladas" viewBox="0 0 440 180">'
        '<rect class="comparison-pane" x="5" y="5" width="205" height="170"/>'
        '<rect class="comparison-pane" x="230" y="5" width="205" height="170"/>'
        '<text x="18" y="25">ANTES</text><text x="243" y="25">DESPUÉS</text>'
        f'<g id="composition-before"><path d="M35 155V55H180V155M85 155V105H130V155" fill="{STONE}" stroke="{INK}" stroke-width="4"/>'
        f'<circle cx="108" cy="116" r="8" fill="{SUN}"/></g><g id="composition-after">'
        f'<g id="composition-state-default-postcard" class="state-layer"><path d="M260 155V55H405V155M310 155V105H355V155" fill="{STONE}" stroke="{INK}" stroke-width="4"/>'
        f'<circle cx="333" cy="116" r="8" fill="{SUN}"/></g>'
        f'<g id="composition-state-changed-position" class="state-layer" display="none"><path d="M245 155L278 48H408V155M325 155V98H370V155" fill="{STONE}" stroke="{INK}" stroke-width="4"/>'
        f'<path d="M278 48L245 155" stroke="{ACCENT}" stroke-width="6"/></g>'
        f'<g id="composition-state-fixed-position-focal" class="state-layer" display="none"><path d="M235 165V35H430V165M300 165V88H365V165" fill="{STONE}" stroke="{INK}" stroke-width="5"/>'
        f'<rect x="260" y="46" width="145" height="105" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="7 5"/></g>'
        f'<g id="composition-state-human-presence" class="state-layer" display="none"><path d="M260 155V55H405V155M310 155V105H355V155" fill="{STONE}" stroke="{INK}" stroke-width="4"/>'
        f'<circle cx="333" cy="105" r="10" fill="{ACCENT}"/><path d="M333 115v32m0-20l-18 12m18-12l18 12" stroke="{ACCENT}" stroke-width="6"/></g>'
        '<g id="composition-state-light-weather" class="state-layer" display="none">'
        '<defs><radialGradient id="composition-glare-gradient"><stop offset="0" stop-color="#fff7c2" stop-opacity=".95"/>'
        '<stop offset="1" stop-color="#fff7c2" stop-opacity="0"/></radialGradient>'
        '<filter id="composition-halo-filter"><feGaussianBlur stdDeviation="5"/></filter></defs>'
        f'<path d="M260 155V55H405V155M310 155V105H355V155" fill="#7891a0" stroke="{INK}" stroke-width="4"/>'
        '<path d="M235 35l75 35M248 28l75 35M365 55l60 60" stroke="#5d7f91" stroke-width="4"/>'
        '<polygon points="355,155 425,120 425,155" fill="#2b3a35"/>'
        f'<path id="composition-reflection" d="M280 62L382 150M296 55L398 143" stroke="#d8edf0" stroke-width="5" opacity="{reflect}"/>'
        f'<circle id="composition-halo" cx="382" cy="58" r="{halo}" fill="url(#composition-glare-gradient)" filter="url(#composition-halo-filter)"/>'
        '<circle id="composition-glare" cx="382" cy="58" r="8" fill="#fff7c2"/></g></g>'
        f'<g id="composition-fixed-position" opacity="0"><path d="M205 145h30" stroke="{GREEN}" stroke-width="4"/>'
        f'<circle cx="220" cy="145" r="8" fill="{GREEN}"/><text x="170" y="168">cámara fija</text></g>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 8 · shutter, aperture, ISO and sharpness

EXPOSURE_SHUTTERS = (15, 30, 60, 125, 250, 500)
EXPOSURE_APERTURES = (1.8, 2.8, 4.0, 5.6, 8.0, 11.0)
EXPOSURE_SCENE_EV = 12.0
EXPOSURE_SUBJECT_M = 6.0
EXPOSURE_FOCAL_MM = 50.0
EXPOSURE_WALK_MPS = 1.4
DEPTH_BAR_NEAR_M = 0.5
DEPTH_BAR_FAR_M = 20.0


def _depth_bar_x(metres: float) -> float:
    ratio = math.log(max(DEPTH_BAR_NEAR_M, min(DEPTH_BAR_FAR_M, metres)) / DEPTH_BAR_NEAR_M)
    span = math.log(DEPTH_BAR_FAR_M / DEPTH_BAR_NEAR_M)
    return 20.0 + 200.0 * ratio / span


def _required_iso(aperture: float, shutter: int) -> tuple[float, float]:
    raw = 100.0 * (aperture * aperture) * shutter / (2.0 ** EXPOSURE_SCENE_EV)
    clamped = float(op.nearest_iso(max(100.0, min(12800.0, raw))))
    stops_over = math.log2(clamped / raw) if raw > 0 else 0.0
    return clamped, max(0.0, stops_over)


def _exposure_state(shutter: int, aperture: float) -> dict:
    seconds = 1.0 / shutter
    iso, stops_over = _required_iso(aperture, shutter)
    blur = op.motion_blur_px(EXPOSURE_WALK_MPS, seconds, EXPOSURE_SUBJECT_M, EXPOSURE_FOCAL_MM, op.FULL_FRAME_WIDTH_MM, 200.0)
    zone = op.depth_of_field(EXPOSURE_FOCAL_MM, aperture, EXPOSURE_SUBJECT_M)
    noise = op.iso_noise_sigma(iso)
    near_x, far_x = _depth_bar_x(zone["near"]), _depth_bar_x(zone["far"])
    far_text = "∞" if zone["far"] == math.inf else f"{_fmt(zone['far'])} m"
    readout = (
        f"1/{shutter} s · f/{_fmt(aperture)} · ISO {int(round(iso))}. Un peatón a 6 m deja una estela de "
        f"{_fmt(blur)} px; la zona nítida va de {_fmt(zone['near'])} m a {far_text}. "
        f"El ruido crece con la raíz del ISO (σ≈{_fmt(noise * 100, 2)} %)."
    )
    if stops_over > 0.15:
        readout += f" A ISO 100 esta pareja aún sobreexpone {_fmt(stops_over)} pasos: cierra o acorta el tiempo."
    return {
        "a": [
            ["exposure-streak", "width", _round(min(96.0, blur * 8.0))],
            ["exposure-streak", "opacity", _round(min(0.85, 0.12 + blur * 0.5))],
            ["exposure-sharp", "x", _round(near_x)],
            ["exposure-sharp", "width", _round(max(3.0, far_x - near_x))],
            ["exposure-grain", "opacity", _round(min(0.55, noise * 26.0))],
        ],
        "t": readout,
    }


def exposure_table() -> dict:
    return {
        f"{shutter}|{_fmt(aperture)}": _exposure_state(shutter, aperture)
        for shutter in EXPOSURE_SHUTTERS
        for aperture in EXPOSURE_APERTURES
    }


def exposure_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="exposure-triangle" role="img" '
        'aria-label="Estela de movimiento, zona nítida y grano, calculados a partir del triángulo de exposición" '
        'viewBox="0 0 240 130">'
        f'<rect x="8" y="8" width="224" height="72" fill="#e8e2d5" stroke="{INK}"/>'
        f'<rect id="exposure-streak" x="60" y="34" width="20" height="30" fill="{ACCENT}" opacity=".3"/>'
        f'<circle cx="60" cy="28" r="7" fill="{ACCENT}"/><rect x="54" y="36" width="12" height="30" fill="{ACCENT}"/>'
        f'<rect id="exposure-grain" x="8" y="8" width="224" height="72" fill="url(#exposure-grain-pattern)" opacity=".1"/>'
        '<defs><pattern id="exposure-grain-pattern" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#10211d"/><circle cx="3" cy="3" r="0.8" fill="#5e6d67"/></pattern></defs>'
        f'<line x1="20" y1="104" x2="220" y2="104" stroke="{INK}" stroke-width="3"/>'
        f'<rect id="exposure-sharp" x="60" y="98" width="60" height="12" fill="{GREEN}" opacity=".75"/>'
        '<text x="16" y="124">0,5 m</text><text x="196" y="124">20 m</text><text x="96" y="94">zona nítida</text>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab 9 · reflection, glare and halo

REFLECTION_ANGLES = (0, 15, 30, 45, 60, 75, 85)
REFLECTION_EXPOSURES = (-3, -2, -1, 0, 1)


def _stops_text(stops: int) -> str:
    if stops == 0:
        return "sin compensar la exposición"
    unit = "paso" if abs(stops) == 1 else "pasos"
    return f"con {stops:+d} {unit} de exposición"


def _reflection_state(angle: int, exposure_ev: int) -> dict:
    reflectance = op.schlick_reflectance(float(angle))
    visible = op.specular_visibility(reflectance)
    halo = op.halo_radius(1.0, float(exposure_ev), 26.0)
    core = min(1.0, 0.3 * (2.0 ** exposure_ev))
    readout = (
        f"A {angle}° de la perpendicular el vidrio devuelve el {_fmt(reflectance * 100)} % de la luz "
        f"(Schlick, n≈1,5). Pero lo que ves depende del contraste: con un cielo 40 veces más brillante que el "
        f"interior, el reflejo aporta el {_fmt(visible * 100, 0)} % de lo que registra el sensor. "
    )
    if visible > 0.85:
        readout += "El vidrio se lee como espejo: sólo lo abre un interior más iluminado, un cielo más apagado o un polarizador."
    elif visible > 0.5:
        readout += "El reflejo ya domina, pero el interior todavía asoma: gira hacia una posición más frontal y vuelve a mirar."
    else:
        readout += "El interior gana la lectura desde aquí: conserva este ángulo."
    readout += f" El halo {_stops_text(exposure_ev)} mide {_fmt(halo)} px de radio."
    return {
        "a": [
            ["reflection-mirror", "opacity", _round(visible, 3)],
            ["reflection-interior", "opacity", _round(max(0.05, 1.0 - visible), 3)],
            ["reflection-halo", "r", _round(halo)],
            ["reflection-core", "opacity", _round(core, 3)],
        ],
        "t": readout,
    }


def reflection_table() -> dict:
    return {
        f"{angle}|{exposure}": _reflection_state(angle, exposure)
        for angle in REFLECTION_ANGLES
        for exposure in REFLECTION_EXPOSURES
    }


def reflection_svg() -> str:
    return (
        '<svg class="lab-frame" data-physics-model="fresnel-schlick" role="img" '
        'aria-label="Fachada de vidrio donde el reflejo del cielo y el interior se reparten según el ángulo de incidencia" '
        'viewBox="0 0 240 130">'
        '<defs><radialGradient id="reflection-glow"><stop offset="0" stop-color="#fff7c2" stop-opacity=".9"/>'
        '<stop offset="1" stop-color="#fff7c2" stop-opacity="0"/></radialGradient>'
        '<clipPath id="reflection-pane"><rect x="40" y="18" width="160" height="94"/></clipPath></defs>'
        '<rect x="40" y="18" width="160" height="94" fill="#16241f"/>'
        '<g id="reflection-interior" opacity=".9" clip-path="url(#reflection-pane)">'
        '<rect x="40" y="18" width="160" height="94" fill="#1d3029"/>'
        '<rect x="54" y="30" width="14" height="70" fill="#4d6b62"/><rect x="96" y="30" width="14" height="70" fill="#4d6b62"/>'
        '<rect x="138" y="30" width="14" height="70" fill="#4d6b62"/>'
        f'<rect x="46" y="88" width="148" height="12" fill="{GREEN}" opacity=".75"/>'
        '<text x="50" y="30" fill="#dcebe5">interior</text></g>'
        '<g id="reflection-mirror" opacity=".2" clip-path="url(#reflection-pane)">'
        '<rect x="40" y="18" width="160" height="94" fill="#bcd6e2"/>'
        '<path d="M40 112V86h18V64h20v30h22V52h24v42h20V70h18v42Z" fill="#8fb0c2"/>'
        '<path d="M46 112L96 40M74 112l50-72" stroke="#ffffff" stroke-width="3" opacity=".7"/>'
        '<text x="140" y="108" fill="#22343d">reflejo del cielo</text></g>'
        f'<rect x="40" y="18" width="160" height="94" fill="none" stroke="{INK}" stroke-width="3"/>'
        '<circle id="reflection-halo" cx="176" cy="40" r="18" fill="url(#reflection-glow)"/>'
        '<circle id="reflection-core" cx="176" cy="40" r="7" fill="#fff7c2" opacity=".3"/>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Lab registry


def _range_control(control_id: str, label: str, low: int, high: int, step: int, default: int) -> str:
    return (
        f'<label for="{control_id}">{escape(label)}</label>'
        f'<input id="{control_id}" data-lab-control type="range" min="{low}" max="{high}" step="{step}" '
        f'value="{default}" data-default="{default}">'
    )


def _select_control(control_id: str, label: str, options: tuple, default: str) -> str:
    items = "".join(
        f'<option value="{escape(str(value))}"{" selected" if str(value) == default else ""}>{escape(text)}</option>'
        for value, text in options
    )
    return (
        f'<label for="{control_id}">{escape(label)}</label>'
        f'<select id="{control_id}" data-lab-control data-default="{escape(default)}">{items}</select>'
    )


def _perspective_controls() -> str:
    focals = tuple((focal, f"{focal} mm") for focal in PERSPECTIVE_FOCALS)
    return _select_control("perspective-focal", "Focal montada", focals, "35") + _range_control(
        "perspective-position", "Distancia de cámara · m", 2, 7, 1, 4
    )


def _light_controls() -> str:
    azimuths = ((-70, "muy a la izquierda"), (-35, "a la izquierda"), (0, "de frente"), (35, "a la derecha"), (70, "muy a la derecha"))
    altitudes = ((10, "10° · rasante"), (25, "25° · media mañana"), (45, "45° · alta"), (70, "70° · casi cenital"))
    sources = tuple((key, label) for key, (label, _size) in LIGHT_SOURCES.items())
    return (
        _select_control("light-azimuth", "Dirección de la luz", azimuths, "-35")
        + _select_control("light-altitude", "Altura sobre el horizonte", altitudes, "25")
        + _select_control("light-source", "Tamaño de la fuente", sources, "sol")
    )


def _exposure_controls() -> str:
    shutters = tuple((shutter, f"1/{shutter} s") for shutter in EXPOSURE_SHUTTERS)
    apertures = tuple((_fmt(aperture), f"f/{_fmt(aperture)}") for aperture in EXPOSURE_APERTURES)
    return _select_control("exposure-shutter", "Obturación", shutters, "125") + _select_control(
        "exposure-aperture", "Diafragma", apertures, "5,6"
    )


def _reflection_controls() -> str:
    angles = tuple((angle, f"{angle}° de la perpendicular") for angle in REFLECTION_ANGLES)
    exposures = ((-3, "−3 pasos"), (-2, "−2 pasos"), (-1, "−1 paso"), (0, "sin compensar"), (1, "+1 paso"))
    return _select_control("reflection-angle", "Ángulo con el vidrio", angles, "45") + _select_control(
        "reflection-exposure", "Exposición", exposures, "0"
    )


LAB_SPECS = {
    "perspective-position": {
        "slug": "perspective", "eyebrow": "LAB 1 · POSICIÓN Y FOCAL",
        "controls": _perspective_controls, "svg": perspective_svg, "table": perspective_table,
        "caption": "Izquierda, la planta: la cámara, su cono de visión real y las dos fachadas. Derecha, lo que cabe en el encuadre.",
    },
    "vertical-convergence": {
        "slug": "vertical", "eyebrow": "LAB 2 · VERTICALES",
        "controls": lambda: _range_control("vertical-tilt", "Inclinación hacia arriba · grados", 0, 20, 1, 0),
        "svg": vertical_svg, "table": vertical_table,
        "caption": "La línea roja es el horizonte. Las punteadas prolongan las verticales hacia su punto de fuga.",
    },
    "hierarchy-edges": {
        "slug": "hierarchy", "eyebrow": "LAB 3 · JERARQUÍA",
        "controls": lambda: _select_control(
            "hierarchy-mode", "Variante",
            (("clean", "Eje limpio"), ("clutter", "Bordes con competencia"), ("human", "Acción humana")), "clean",
        ),
        "svg": hierarchy_svg, "table": hierarchy_table,
        "caption": "Los círculos 1, 2 y 3 marcan el orden de lectura y se reordenan con cada variante.",
    },
    "negative-space-edges": {
        "slug": "negative", "eyebrow": "LAB 4 · VACÍO Y BORDES",
        "controls": lambda: _range_control("negative-margin", "Margen alrededor del sujeto · px", 0, 40, 5, 20),
        "svg": negative_svg, "table": negative_table,
        "caption": "El rectángulo punteado es el encuadre; el bloque amarillo compite desde el borde derecho.",
    },
    "depth-layers": {
        "slug": "depth", "eyebrow": "LAB 5 · CAPAS Y PROFUNDIDAD",
        "controls": lambda: _range_control("depth-haze", "Bruma atmosférica · %", 0, 90, 15, 30),
        "svg": depth_svg, "table": depth_table,
        "caption": "Tres planos a 8, 60 y 400 m. Su contraste cae con la distancia según la dispersión atmosférica.",
    },
    "composition-sequence": {
        "slug": "composition", "eyebrow": "LAB 6 · SECUENCIA",
        "controls": lambda: _select_control(
            "composition-mode", "Decisión aislada",
            tuple((variant, label) for variant, label in (
                ("default-postcard", "Postal por defecto"), ("changed-position", "Cambia posición"),
                ("fixed-position-focal", "Focal, posición fija"), ("human-presence", "Presencia / ausencia"),
                ("light-weather", "Luz / clima"))), "default-postcard",
        ),
        "svg": composition_svg, "table": composition_table,
        "caption": "ANTES conserva la referencia; DESPUÉS muestra qué relación cambia. «Cámara fija» significa que sólo se recortó con la focal.",
    },
    "light-material": {
        "slug": "light", "eyebrow": "LAB 7 · LUZ Y MATERIAL",
        "controls": _light_controls, "svg": light_svg, "table": light_table,
        "caption": "El tono de cada cara sale de cos θ; la sombra mide h/tan(altura solar) y su borde se abre con el tamaño de la fuente.",
    },
    "exposure-triangle": {
        "slug": "exposure", "eyebrow": "LAB 8 · EXPOSICIÓN Y NITIDEZ",
        "controls": _exposure_controls, "svg": exposure_svg, "table": exposure_table,
        "caption": "Arriba, la estela de un peatón a 6 m. Abajo, la zona nítida sobre una escala de 0,5 a 20 m.",
    },
    "reflection-glare": {
        "slug": "reflection", "eyebrow": "LAB 9 · REFLEJOS Y HALO",
        "controls": _reflection_controls, "svg": reflection_svg, "table": reflection_table,
        "caption": "La capa clara es el reflejo del cielo; debajo está el interior. El halo rodea la fuente brillante.",
    },
}

LAB_CYCLE = (
    '<div class="lab-cycle"><span>Predicción</span><span>Acción</span><span>Observación</span>'
    '<span>Transferencia al campo</span></div>'
)
LAB_LEGEND = (
    '<div class="lab-legend"><span>Terracota: atención o acción</span><span>Verde: referencia y medida</span>'
    '<span>Gris: arquitectura y sombra</span></div>'
)


def _source_links(sources: list[str]) -> str:
    return " · ".join(f'<a href="{escape(url)}">Fuente {index}</a>' for index, url in enumerate(sources, 1))


def _lab_article(lab: dict, spec: dict) -> str:
    slug = spec["slug"]
    return (
        f'<article class="learning-lab" id="lab-{escape(lab["simulation_id"])}" data-lab="{slug}">'
        f'<p class="eyebrow">{escape(spec["eyebrow"])}</p><h3>{escape(lab["title"])}</h3>'
        f'<p>{escape(lab["prediction_prompt"])}</p>'
        f'<div class="lab-controls">{spec["controls"]()}</div>{_with_text_scale(spec["svg"](), 56.0)}'
        f'<p class="viz-caption">{escape(spec["caption"])}</p>'
        f'<p id="{slug}-feedback" class="lab-readout" role="status"></p>'
        f'<p><strong>Qué observar:</strong> {escape(lab["observable_feedback"])}</p>'
        f'<p><strong>Campo:</strong> {escape(lab["field_drill"])}</p>'
        f'<p class="reject"><strong>Cuidado:</strong> {escape(lab["misconception_warning"])}</p>'
        f'<p class="route-note">Límite del modelo: {escape(lab["model_limit"])}</p>'
        f'<p class="source-links">{_source_links(lab["sources"])}</p>'
        f'{LAB_CYCLE}{LAB_LEGEND}'
        f'<button type="button" class="lab-reset" data-lab="{slug}">Restablecer ejemplo</button></article>'
    )


def render_labs(learning: dict) -> str:
    return "".join(_lab_article(lab, LAB_SPECS[lab["simulation_id"]]) for lab in learning["simulations"])


def physics_tables() -> dict:
    return {spec["slug"]: spec["table"]() for spec in LAB_SPECS.values()}


# ---------------------------------------------------------------------------
# Technique diagrams for the wiki: one drawing per family, no shared template


def _diagram(technique_id: str, title: str, body: str, view_box: str = "0 0 360 150") -> str:
    svg = (
        f'<svg class="wiki-diagram" data-technique="{escape(technique_id)}" role="img" '
        f'aria-label="{escape(title)}" viewBox="{view_box}">{body}</svg>'
    )
    return _with_text_scale(svg, 34.0)


def _viewpoint_diagram() -> str:
    near = _round(op.projected_height(1.8, 4.0, 35.0, op.FULL_FRAME_HEIGHT_MM, 90.0))
    far = _round(op.projected_height(1.8, 8.0, 35.0, op.FULL_FRAME_HEIGHT_MM, 90.0))
    half = op.half_angle_of_view_deg(35.0, op.FULL_FRAME_WIDTH_MM)
    reach = 128.0
    dy = _round(reach * math.tan(math.radians(half)))
    body = (
        f'<line x1="12" y1="130" x2="348" y2="130" stroke="{INK}"/>'
        f'<circle cx="34" cy="96" r="6" fill="{ACCENT}"/><text x="12" y="146">posición A</text>'
        f'<path d="M34 96L162 {_round(96 - dy)}M34 96L162 {_round(96 + dy)}" fill="none" stroke="{GREEN}" stroke-width="2"/>'
        f'<circle cx="34" cy="40" r="6" fill="{GREEN}"/><text x="12" y="26">posición B</text>'
        f'<rect x="186" y="{_round(130 - near)}" width="34" height="{near}" fill="{ACCENT}"/>'
        f'<rect x="252" y="{_round(130 - far)}" width="26" height="{far}" fill="{STONE}"/>'
        f'<text x="182" y="146">cerca</text><text x="248" y="146">lejos</text>'
        f'<text x="292" y="60">solape</text><path d="M300 68v40" stroke="{ACCENT}" stroke-width="3"/>'
    )
    return _diagram("viewpoint-before-focal", "Dos posiciones de cámara y cómo cambia el solape entre planos", body)


def _tilt_diagram() -> str:
    level = op.keystone_corners(0.0, 10.0, 12.0, 26.0, 35.0, op.FULL_FRAME_HEIGHT_MM, 120.0)
    tilted = op.keystone_corners(16.0, 10.0, 12.0, 26.0, 35.0, op.FULL_FRAME_HEIGHT_MM, 120.0)

    def facade(cx: float, corners: dict) -> str:
        height = corners["top_y"] - corners["bottom_y"]
        top = 128.0 - height
        return (
            f'{_round(cx - corners["top_width"] / 2)},{_round(top)} {_round(cx + corners["top_width"] / 2)},{_round(top)} '
            f'{_round(cx + corners["bottom_width"] / 2)},128 {_round(cx - corners["bottom_width"] / 2)},128'
        )

    body = (
        f'<polygon points="{facade(96, level)}" fill="{STONE}" stroke="{INK}" stroke-width="3"/>'
        f'<polygon points="{facade(262, tilted)}" fill="{STONE}" stroke="{ACCENT}" stroke-width="3"/>'
        f'<line x1="12" y1="128" x2="348" y2="128" stroke="{INK}"/>'
        '<text x="58" y="146">nivelada</text><text x="212" y="146">inclinada 16°</text>'
        f'<path d="M262 26v-14" stroke="{ACCENT}" stroke-dasharray="3 3"/><text x="216" y="18">al punto de fuga</text>'
    )
    return _diagram("perspective-shift-tilt", "Fachada nivelada frente a fachada inclinada 16 grados", body)


def _hierarchy_diagram() -> str:
    body = (
        f'<path d="M40 128V40H210V128M96 128V78H154V128" fill="none" stroke="{INK}" stroke-width="7"/>'
        f'<circle cx="120" cy="56" r="12" fill="{GREEN}"/><text x="120" y="61" fill="#ffffff" text-anchor="middle">1</text>'
        f'<circle cx="196" cy="70" r="12" fill="{STONE}"/><text x="196" y="75" fill="#ffffff" text-anchor="middle">2</text>'
        f'<circle cx="126" cy="112" r="12" fill="{ACCENT}"/><text x="126" y="117" fill="#ffffff" text-anchor="middle">3</text>'
        f'<path d="M132 60L184 68M190 80L134 104" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="4 3"/>'
        f'<rect x="300" y="34" width="42" height="30" fill="{SUN}"/><text x="252" y="26">compite</text>'
    )
    return _diagram("lines-symmetry-hierarchy", "Recorrido de lectura numerado sobre una fachada", body)


def _negative_diagram() -> str:
    body = (
        f'<rect x="18" y="18" width="324" height="112" fill="none" stroke="{INK}" stroke-dasharray="5 4"/>'
        f'<rect x="60" y="40" width="150" height="88" fill="{STONE}" stroke="{ACCENT}" stroke-width="3"/>'
        f'<text x="62" y="34" fill="{ACCENT}">toca el borde</text>'
        f'<rect x="238" y="46" width="86" height="60" fill="{STONE}" stroke="{GREEN}" stroke-width="3"/>'
        f'<text x="238" y="126" fill="{GREEN}">con margen</text>'
        f'<path d="M238 18v28M324 18v28" stroke="{GREEN}" stroke-width="2"/>'
    )
    return _diagram("negative-space-edge-control", "Sujeto tangente al borde frente a sujeto con margen", body)


def _depth_diagram() -> str:
    tones = [op.aerial_contrast(distance, 0.45) for distance in (8.0, 60.0, 400.0)]
    body = (
        f'<rect x="30" y="26" width="300" height="60" fill="{_grey(0.92 - 0.62 * tones[2])}"/>'
        f'<polygon points="78,128 78,54 214,42 214,128" fill="{_grey(0.92 - 0.62 * tones[1])}"/>'
        f'<polygon points="18,128 18,86 150,70 150,128" fill="{_grey(0.92 - 0.62 * tones[0])}"/>'
        f'<line x1="12" y1="128" x2="348" y2="128" stroke="{INK}"/>'
        f'<text x="22" y="146">8 m</text><text x="160" y="146">60 m</text><text x="286" y="20">400 m</text>'
    )
    return _diagram("depth-figure-ground", "Tres planos con contraste decreciente por distancia", body)


def _gesture_diagram() -> str:
    body = (
        f'<path d="M28 128V44H160V128M74 128V86H118V128" fill="none" stroke="{INK}" stroke-width="6"/>'
        f'<circle cx="96" cy="98" r="8" fill="{ACCENT}"/><path d="M96 106v20m0-13l-11 9m11-9l11 9" stroke="{ACCENT}" stroke-width="4"/>'
        f'<text x="52" y="34">con verbo</text>'
        f'<path d="M204 128V44H336V128M250 128V86H294V128" fill="none" stroke="{INK}" stroke-width="6"/>'
        f'<path d="M246 122h56" stroke="{GREEN}" stroke-width="4" stroke-dasharray="6 4"/>'
        f'<text x="216" y="34">con residuo de uso</text>'
    )
    return _diagram("gesture-absence", "Mismo umbral con gesto humano y con ausencia significativa", body)


def _light_diagram() -> str:
    front, side = _light_faces(-35, 25)
    length = min(150.0, op.shadow_length(8.0, 25.0) * 6.0)
    body = (
        f'<line x1="12" y1="122" x2="348" y2="122" stroke="{INK}"/>'
        f'<circle cx="44" cy="30" r="9" fill="{SUN}"/>'
        f'<line x1="44" y1="30" x2="128" y2="52" stroke="{SUN}" stroke-width="3" stroke-dasharray="6 4"/>'
        f'<polygon points="128,122 206,122 {_round(206 + length)},136 {_round(128 + length)},136" fill="#2b3a35" opacity=".55"/>'
        f'<polygon points="134,122 200,122 {_round(200 + length * 0.9)},133 {_round(134 + length * 0.9)},133" fill="#16211e"/>'
        f'<polygon points="206,122 244,110 244,40 206,52" fill="{_ramp(side)}"/>'
        f'<rect x="128" y="52" width="78" height="70" fill="{_ramp(front)}"/>'
        f'<text x="122" y="46">cos θ = {_fmt(front / max(front, side), 2)}</text><text x="196" y="146">penumbra</text>'
    )
    return _diagram("light-material-weather", "Volumen con caras según la ley del coseno y sombra con umbra y penumbra", body)


def _exposure_diagram() -> str:
    slow = op.motion_blur_px(1.4, 1 / 15, 6.0, 50.0, op.FULL_FRAME_WIDTH_MM, 200.0)
    fast = op.motion_blur_px(1.4, 1 / 250, 6.0, 50.0, op.FULL_FRAME_WIDTH_MM, 200.0)
    wide = op.depth_of_field(50.0, 1.8, 6.0)
    stopped = op.depth_of_field(50.0, 11.0, 6.0)
    body = (
        f'<text x="18" y="24">1/15 s</text><circle cx="46" cy="46" r="7" fill="{ACCENT}"/>'
        f'<rect x="46" y="40" width="{_round(min(120.0, slow * 9))}" height="14" fill="{ACCENT}" opacity=".45"/>'
        f'<text x="18" y="84">1/250 s</text><circle cx="46" cy="104" r="7" fill="{ACCENT}"/>'
        f'<rect x="46" y="98" width="{_round(max(3.0, fast * 9))}" height="14" fill="{ACCENT}" opacity=".8"/>'
        f'<line x1="212" y1="60" x2="344" y2="60" stroke="{INK}" stroke-width="3"/>'
        f'<rect x="252" y="54" width="{_round(max(4.0, (stopped["far"] - stopped["near"]) * 2.6))}" height="12" fill="{GREEN}" opacity=".8"/>'
        f'<line x1="212" y1="112" x2="344" y2="112" stroke="{INK}" stroke-width="3"/>'
        f'<rect x="266" y="106" width="{_round(max(4.0, (wide["far"] - wide["near"]) * 2.6))}" height="12" fill="{GREEN}" opacity=".8"/>'
        f'<text x="210" y="46">f/11</text><text x="210" y="100">f/1,8</text>'
    )
    return _diagram("exposure-focus-iso-motion", "Estela de movimiento por obturación y zona nítida por diafragma", body)


def _editing_diagram() -> str:
    body = (
        f'<rect x="16" y="30" width="150" height="90" rx="10" fill="none" stroke="{GREEN}" stroke-width="3"/>'
        f'<text x="26" y="52">CAPTURA</text><text x="26" y="74">REVELADO</text>'
        f'<text x="26" y="98" fill="{GREEN}">normalmente permitido</text>'
        f'<rect x="194" y="30" width="150" height="90" rx="10" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="6 4"/>'
        f'<text x="204" y="52">COMPOSICIÓN</text><text x="204" y="74">GENERACIÓN</text>'
        f'<text x="204" y="98" fill="{ACCENT}">consulta el encargo</text>'
        f'<path d="M170 74h20" stroke="{INK}" stroke-width="3"/><text x="150" y="22">frontera</text>'
    )
    return _diagram("contest-safe-editing", "Cuatro categorías de edición separadas por la frontera del encargo", body)


TECHNIQUE_DIAGRAMS = {
    "viewpoint-before-focal": _viewpoint_diagram,
    "perspective-shift-tilt": _tilt_diagram,
    "lines-symmetry-hierarchy": _hierarchy_diagram,
    "negative-space-edge-control": _negative_diagram,
    "depth-figure-ground": _depth_diagram,
    "gesture-absence": _gesture_diagram,
    "light-material-weather": _light_diagram,
    "exposure-focus-iso-motion": _exposure_diagram,
    "contest-safe-editing": _editing_diagram,
}

TECHNIQUE_CAPTIONS = {
    "viewpoint-before-focal": "Cómo leerlo: desde A y desde B el cono de visión es el mismo, pero cambia qué tapa qué. El solape sólo se mueve con los pies.",
    "perspective-shift-tilt": "Cómo leerlo: la fachada de la izquierda está nivelada; la de la derecha, inclinada 16°. Su borde superior se estrecha porque queda más lejos del sensor.",
    "lines-symmetry-hierarchy": "Cómo leerlo: los círculos 1, 2 y 3 marcan el recorrido de la mirada. El rectángulo amarillo es un borde que compite por la primera lectura.",
    "negative-space-edge-control": "Cómo leerlo: a la izquierda el sujeto toca el borde inferior y la mirada se escapa; a la derecha conserva margen en los cuatro lados.",
    "depth-figure-ground": "Cómo leerlo: los tres planos están a 8, 60 y 400 m. Su tono se aclara con la distancia porque el aire dispersa el contraste.",
    "gesture-absence": "Cómo leerlo: el mismo umbral con una figura que actúa y con el residuo de uso que deja cuando no hay nadie.",
    "light-material-weather": "Cómo leerlo: cada cara tiene el tono que le da cos θ. La zona oscura del suelo es la umbra; su contorno difuso, la penumbra.",
    "exposure-focus-iso-motion": "Cómo leerlo: arriba, la estela que deja un peatón según la obturación. Abajo, la zona nítida que abre cada diafragma.",
    "contest-safe-editing": "Cómo leerlo: a la izquierda, lo que casi todo encargo admite. A la derecha, lo que hay que confirmar en las bases antes de tocarlo.",
}

TECHNIQUE_LABS = {
    "viewpoint-before-focal": "perspective-position",
    "perspective-shift-tilt": "vertical-convergence",
    "lines-symmetry-hierarchy": "hierarchy-edges",
    "negative-space-edge-control": "negative-space-edges",
    "depth-figure-ground": "depth-layers",
    "gesture-absence": "composition-sequence",
    "light-material-weather": "light-material",
    "exposure-focus-iso-motion": "exposure-triangle",
    "contest-safe-editing": None,
}

SYMPTOM_INDEX = (
    ("El edificio sale torcido o se cae hacia atrás", "perspective-shift-tilt"),
    ("La foto sale plana, sin profundidad", "depth-figure-ground"),
    ("Algo en el borde me roba la mirada", "negative-space-edge-control"),
    ("Cambié de objetivo y la escena no mejoró", "viewpoint-before-focal"),
    ("No sé qué se mira primero", "lines-symmetry-hierarchy"),
    ("La fachada se ve dura o apagada", "light-material-weather"),
    ("Salió movida o con poco nítido", "exposure-focus-iso-motion"),
    ("El vidrio sólo devuelve reflejos", "light-material-weather"),
    ("La persona no aporta nada", "gesture-absence"),
    ("No sé si puedo borrar algo al editar", "contest-safe-editing"),
)


def technique_diagram(technique_id: str) -> str:
    return TECHNIQUE_DIAGRAMS[technique_id]()
