#!/usr/bin/env python3
"""Build the field card: each plan's exact settings for the light you are in.

Requirements V01-V06 (tests/test_field_card.py). The card is generated from
data/plans.json, so it can never disagree with the plans: for every plan, shot
and light slot it prints the lens, aperture, shutter, ISO and ND filter the
plan computed, and marks the slots that cannot be shot.

Everything a reader switches (plan, light, subject, section) is a radio
button, and CSS :has() shows the matching cards, so the card works with
JavaScript off and printed. assets/field_card.js adds what needs a clock or
memory: the slot for the time in Lima, each shot's time window, saved
progress, the next pending shot and keeping the screen awake.

Outputs field_card.html (its own page) and the three parts the home page
embeds in its dialog: data/field_card_fragment.html, data/field_card.css and
data/field_card.js (integrate_field_card.py puts them in index.html).
"""
from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import exposure_model as em  # noqa: E402
import optics_physics as op  # noqa: E402

DATA = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
OUT = ROOT / "field_card.html"
SLOTS = (("day", "Día", "☀"), ("afternoon", "Tarde", "🌇"), ("night", "Noche", "🌙"))
SUBJECTS = (("human", "Persona"), ("dog", "Perro"))
TABS = (("shots", "Tomas", "📷"), ("techniques", "Técnicas", "🎯"), ("rescue", "Rescate", "🛟"),
        ("framing", "Encuadre", "▦"), ("gear", "Equipo", "🎒"))
esc = html.escape

RESCUE = [
    ("🎯", "El foco falla", "Retrato quieto: cierra de f/1.8 a f/2.2–2.8. Acción: punto central, AF AI SERVO y sigue al sujeto antes de disparar. No bajes la velocidad que crea el efecto. Si el 85 mm falla siempre por delante o por detrás, la 6D tiene microajuste del AF en el menú."),
    ("🌫", "El fondo no se desenfoca", "Primero aleja al sujeto del fondo; después abre el diafragma o usa el 85 mm. Abrir un tercio de paso no compensa un fondo pegado."),
    ("💨", "El barrido sale congelado", "Baja de 1/60 a 1/40 y luego a 1/30. Mantén la trayectoria lateral y sigue girando después del disparo."),
    ("🫨", "El barrido sale todo movido", "Sube a 1/60, gira desde la cintura y apunta a un detalle estable del sujeto."),
    ("👻", "El fantasma queda muy tenue", "Pide a la persona que cruce más despacio o que se detenga un instante. Si sale sólida, que se mueva más."),
    ("🌟", "Las luces se queman", "Baja a ISO 100 primero. Después cambia lo que no hace el efecto: con poca profundidad, acorta hasta 1/4000 s y luego pon un ND de 2–3 pasos o busca sombra; para congelar, cierra el diafragma; en tomas de segundos, cierra hasta f/11 y pon un ND más fuerte, porque más allá la difracción ablanda."),
    ("🔭", "El efecto zoom no traza rayos", "Busca luces o patrones con contraste, expón de 1\" a 4\" y gira el anillo de 35 a 80 mm durante toda la exposición, sin mover el trípode."),
    ("▰", "De noche la foto vibra", "Trípode firme, retardo de 2 s o disparador remoto, y no toques la cámara. Revisa la nitidez al 100 % antes de seguir."),
    ("⬛", "Con el ND la foto falla", "Compón, enfoca y pasa a MF antes de enroscar el filtro: con un ND de 10 pasos el visor queda negro y el AF no ve. Pon la tapa del ocular que va en la correa: la luz que entra por el visor altera la exposición."),
]
COMPOSITION = [
    ("▦", "Tercios", "Ojos o sujeto cerca de una intersección; deja aire hacia donde mira o se mueve."),
    ("↗", "Perspectiva", "Las líneas llevan al sujeto. Cambia de posición antes de cambiar de objetivo."),
    ("↔", "Simetría", "Eje central exacto; nivela la cámara antes de disparar."),
    ("▣", "Enmarcado", "Una rama, puerta o arco rodea al sujeto sin tapar ojos ni articulaciones."),
    ("□", "Espacio negativo", "Aire útil alrededor del sujeto, no vacío por accidente."),
    ("◎", "Punto de interés", "Un solo elemento gana la atención en menos de un segundo."),
    ("•", "Minimalismo", "Quita elementos hasta que nada compita con el sujeto."),
    ("▤", "Capas", "Primer plano, sujeto y fondo separados de verdad en distancia."),
]
ANGLES = [
    ("↔", "A la altura de los ojos", "Objetivo a la altura de sus ojos: perro a 30–50 cm del suelo; persona, según su estatura."),
    ("↘", "Picado", "Cámara arriba mirando abajo; resta presencia al sujeto."),
    ("↗", "Contrapicado", "Cámara abajo mirando arriba; da presencia y hace converger las verticales."),
    ("↑", "Nadir", "A 90° hacia arriba: copas y edificios. Vigila los bordes con el 35 mm."),
    ("↓", "Cenital", "A 90° hacia abajo: patrones y lectura gráfica."),
    ("◇", "Holandés", "Inclina 10–15° sólo si quieres tensión."),
]
BEFORE_LEAVING = [
    ("RAW", "Archivo", "RAW, tarjeta con espacio, batería cargada y objetivo limpio."),
    ("AF", "Enfoque", "Sujeto quieto: AF ONE SHOT. Acción: AF AI SERVO y punto central."),
    ("▰", "Soporte", "A pulso: 1 entre el doble de la focal (1/100 s con el 50 mm, 1/160 s con el 85 mm); el estabilizador del 35 mm permite ≈3 pasos más lento si nada se mueve. Desde 0\"5: trípode y retardo de 2 s o remoto."),
    ("100 %", "Revisión", "Acción: ojos y patas. Profundidad: primer plano y fondo. Noche: altas luces."),
    ("🐶", "Perro", "Correa y trayectoria segura; nunca junto a una calzada con tráfico."),
    ("▟", "Exposición", "Histograma RGB y altas luces en la primera foto de cada luz nueva y después de cada serie. Salen de la vista previa JPEG: con estilo Neutro se acercan al RAW, que guarda ≈⅓–⅔ de paso más."),
    ("🌙", "De noche", "Ve acompañado, con una bolsa pequeña y el teléfono aparte; elige puntos iluminados con gente y no dejes el trípode solo."),
]
TECHNIQUE_ICONS = {"mucha_pdc": "▤", "poca_pdc": "◎", "congelado": "❄", "barrido": "→", "fantasma": "◌",
                   "lightpainting": "✦", "larga_exp": "≈", "zooming": "⇆"}


def number(value: float) -> str:
    return f"{value:g}"


def lens_label(lens: str) -> str:
    """'35-80mm @50' → '35–80 mm a 50 mm'."""
    match = re.fullmatch(r"(\d+)(?:-(\d+))?mm(?: @(\d+))?", lens)
    if not match:
        raise ValueError(f"unknown lens {lens!r}")
    short, long_, at = match.groups()
    label = f"{short}–{long_} mm" if long_ else f"{short} mm"
    return label + (f" a {at} mm" if at else "")


def lens_key(lens: str) -> str:
    return lens.split()[0].replace("mm", "").replace("-", "–")


def nd_name(stops: int) -> str:
    # Sold as ND4, ND8, ND64; ten stops (×1024) is sold as ND1000.
    return "ND1000" if stops == 10 else f"ND{2 ** stops}"


def needs_support(shutter: str) -> bool:
    return '"' in shutter or shutter.startswith("Bulb")


def scene_text(scene: str) -> str:
    light = DATA["scene_light"][scene]
    ev = f"EV {light['ev_low']}" if light["ev_low"] == light["ev_high"] else f"EV {light['ev_low']} a {light['ev_high']}"
    return f"{light['label'][0].upper()}{light['label'][1:]} · {ev}"


def chips(setting: dict) -> str:
    out = []
    if setting.get("nd_stops"):
        out.append(f'<span class="fc-chip fc-chip-nd"><span class="fc-v-nd">{nd_name(setting["nd_stops"])} · {setting["nd_stops"]} pasos</span></span>')
    if needs_support(setting["shutter"]):
        out.append('<span class="fc-chip">Trípode · retardo de 2 s</span>')
    if setting.get("viable") is False:
        out.append('<span class="fc-chip fc-chip-off">No viable con esta luz</span>')
    return f'<p class="fc-chips">{"".join(out)}</p>' if out else ""


def slot_block(plan: dict, shot: dict, slot: str, slot_name: str) -> str:
    setting = shot["settings_by_time"][slot]
    key = f"{plan['id']}/{shot['id']}/{slot}"
    off = " fc-off" if setting.get("viable") is False else ""
    return (
        f'<div class="fc-slot{off}" data-plan="{plan["id"]}" data-shot="{shot["id"]}" data-slot="{slot}">'
        f'<label class="fc-check-wrap"><input class="fc-check" type="checkbox" data-key="{key}"><span class="fc-box" aria-hidden="true"></span>'
        f'<span class="fc-sr">{shot["id"]} hecha ({slot_name.lower()})</span></label>'
        # The space keeps the two apart when the line is copied or read aloud; on screen the flex gap does.
        f'<p class="fc-settings"><span class="fc-v-lens">{lens_label(setting["lens"])}</span> '
        f'<span class="fc-v-exposure">{esc(setting["aperture"])} · {esc(setting["shutter"])} · ISO {setting["iso"]}</span></p>'
        f'{chips(setting)}'
        f'<p class="fc-light">{esc(scene_text(setting["scene"]))} <span class="fc-when" data-scene="{setting["scene"]}" data-slot="{slot}"></span></p>'
        f'<p class="fc-v-note">{esc(setting["notes"])}</p>{gear_slot(shot, setting)}</div>'
    )


def gear_slot(shot: dict, setting: dict) -> str:
    """V15: room for the setting adapted to the reader's gear; assets/gear.js fills it."""
    data = {"technique": shot["technique"], "lens": setting["lens"], "aperture": setting["aperture"], "shutter": setting["shutter"],
            "iso": setting["iso"], "nd_stops": setting.get("nd_stops", 0), "distance": shot["subject_distance_m"],
            "viable": setting.get("viable", True)}
    # Single-quoted, so the JSON's double quotes need no escaping: 180 slots, about 20 KB less.
    value = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")
    return f"<div class=\"fc-gear\" hidden data-gear='{value}'></div>"


def geometry(shot: dict) -> str:
    parts = [f"Sujeto a {number(shot['subject_distance_m'])} m", f"fondo a {number(shot['background_distance_m'])} m",
             f"cámara a {number(shot['camera_height_m'])} m de altura"]
    if shot["angle"] != "central":
        parts.append(shot["angle_label"].lower())
    return " · ".join(parts)


def shot_card(plan: dict, shot: dict) -> str:
    slots = "".join(slot_block(plan, shot, slot, name) for slot, name, _icon in SLOTS)
    who = "".join(f'<p class="fc-who fc-who-{key}"><b>{name}:</b> {esc(shot["subjects"][key]["action"])}</p>' for key, name in SUBJECTS)
    dos = "".join(f"<li>{esc(item)}</li>" for item in shot["dos"])
    donts = "".join(f"<li>{esc(item)}</li>" for item in shot["donts"])
    return (
        f'<li class="fc-shot" data-plan="{plan["id"]}" data-shot="{shot["id"]}">'
        f'<h3 class="fc-name"><span class="fc-id" aria-hidden="true">{TECHNIQUE_ICONS[shot["technique"]]}</span>'
        f'{shot["id"]} · {esc(shot["technique_label"])} · {esc(shot["composition_label"])}</h3>'
        f'{slots}<p class="fc-geo">{esc(geometry(shot))}</p>{who}'
        f'<details class="fc-more"><summary>Qué hacer y qué evitar</summary><ul class="fc-do">{dos}</ul><ul class="fc-dont">{donts}</ul></details></li>'
    )


def radio_group(name: str, legend: str, options, extra_class: str = "", checked_first: bool = True) -> str:
    """options: (value, visible label HTML, extra words for screen readers or '')."""
    inputs = "".join(
        f'<label class="fc-option"><input type="radio" name="{name}" value="{value}"{" checked" if checked_first and i == 0 else ""}>'
        f'<span>{label}{f"<span class=fc-sr> · {esc(spoken)}</span>" if spoken else ""}</span></label>'
        for i, (value, label, spoken) in enumerate(options))
    return f'<fieldset class="fc-group {extra_class}"><legend>{legend}</legend><div class="fc-options">{inputs}</div></fieldset>'


def plan_letter(plan: dict) -> str:
    return plan["id"].split("_")[1].upper()


def plans_settings(plan: dict) -> list[dict]:
    return [s for shot in plan["shots"] for s in shot["settings_by_time"].values() if s.get("viable") is not False]


def nd_items(plan: dict, threads: dict) -> list[str]:
    by_stops: dict[int, set[str]] = {}
    for setting in plans_settings(plan):
        if setting.get("nd_stops"):
            by_stops.setdefault(setting["nd_stops"], set()).add(lens_key(setting["lens"]))
    items = []
    for stops in sorted(by_stops):
        lenses = sorted(by_stops[stops], key=lambda k: threads[k])
        sizes = " y ".join(f"{threads[k]} mm para el {k} mm" for k in lenses)
        items.append(f"<li><b>{nd_name(stops)}</b> ({stops} pasos): rosca de {sizes}.</li>")
    sizes = {threads[k] for lenses in by_stops.values() for k in lenses}
    if len(sizes) > 1:
        items.append(f"<li>Un juego de filtros de {max(sizes)} mm con aros adaptadores "
                     f"{', '.join(f'{s}→{max(sizes)}' for s in sorted(sizes - {max(sizes)}))} sirve para todos.</li>")
    return items


def packing_list(plan: dict) -> str:
    threads = {str(lens["focal"]).replace("-", "–"): lens["filter_mm"] for lens in DATA["gear"]["lenses"]}
    settings = plans_settings(plan)
    lenses = sorted({lens_key(s["lens"]) for s in settings}, key=lambda k: int(k.split("–")[0]) * 10 + len(k))
    items = ["<li><b>Objetivos:</b> " + ", ".join(f"{k} mm (rosca de {threads[k]} mm)" for k in lenses) + ".</li>"]
    items += nd_items(plan, threads)
    if any(needs_support(s["shutter"]) for s in settings):
        items.append("<li><b>Trípode</b> y disparador remoto, o retardo de 2 s.</li>")
    if any(shot["technique"] == "lightpainting" for shot in plan["shots"]):
        items.append("<li><b>Linterna</b> o tira de luz para pintar.</li>")
    items.append("<li><b>Para el perro:</b> correa, premios y agua.</li>")
    items.append("<li>Batería de repuesto y tarjeta vacía.</li>")
    return f'<ul class="fc-pack" data-plan="{plan["id"]}">{"".join(items)}</ul>'


def mini_cards(rows, extra: str = "") -> str:
    return "".join(f'<li class="fc-mini{extra}"><span aria-hidden="true">{esc(icon)}</span><div><b>{esc(title)}</b><p>{esc(tip)}</p></div></li>'
                   for icon, title, tip in rows)


# W10: the two numbers a long exposure and a landscape need on site, printed so they work
# with no signal. A filter of n stops multiplies the time by 2^n; past the 6D's 30 s the
# time is counted in Bulb. The hyperfocal distance uses the site's normal-print 0.030 mm.
ND_METERED = ("1/1000", "1/500", "1/250", "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "1/2", '1"')
HYPERFOCAL_APERTURES = (5.6, 8, 11, 16)
HYPERFOCAL_FOCALS = (35, 50, 85)


def kit_nd_stops() -> list[int]:
    return sorted({s["nd_stops"] for plan in DATA["plans"] for s in plans_settings(plan) if s.get("nd_stops")})


def dial_seconds(label: str) -> float:
    """The time a dial label stands for: the labels round powers of 2^(1/3), "1/60" is 1/64 s."""
    return 2 ** (round(3 * math.log2(em.shutter_seconds(label))) / 3)


def nd_time(metered: str, stops: int) -> str:
    want = dial_seconds(metered) * 2 ** stops
    if want <= dial_seconds(em.THIRD_STOP_SHUTTERS[-1]) + 1e-9:
        return min(em.THIRD_STOP_SHUTTERS, key=lambda s: abs(math.log2(dial_seconds(s) / want)))
    total = round(want)
    return f"B · {total // 60} min {total % 60} s" if total >= 60 else f"B · {total} s"


def nd_table() -> str:
    stops = kit_nd_stops()
    head = "".join(f'<th scope="col">{nd_name(n)}<br><small>{n} pasos</small></th>' for n in stops)
    rows = "".join(f'<tr><th scope="row">{esc(t)}</th>' + "".join(f"<td>{esc(nd_time(t, n))}</td>" for n in stops) + "</tr>"
                   for t in ND_METERED)
    return ('<div class="fc-tablewrap"><table class="fc-table"><caption>Con el ND puesto: tu velocidad sin filtro, convertida</caption>'
            f'<thead><tr><th scope="col">Sin<br>filtro</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
            '<p class="fc-table-note">Mide sin el filtro, busca tu velocidad en la primera columna y usa la de la columna de tu ND. '
            'Más allá de 30 s pasa a Bulb (B) y cuenta el tiempo con el disparador remoto. Un ND real se aparta hasta un tercio de paso '
            'de su etiqueta: revisa el histograma de la primera toma y corrige.</p>')


def hyperfocal_table() -> str:
    head = "".join(f'<th scope="col">{f} mm</th>' for f in HYPERFOCAL_FOCALS)
    rows = ""
    for n in HYPERFOCAL_APERTURES:
        cells = []
        for focal in HYPERFOCAL_FOCALS:
            far = op.hyperfocal_mm(focal, n) / 1000
            cells.append(f"<td>{far:.1f} m<br><small>desde {far / 2:.1f} m</small></td>")
        rows += f'<tr><th scope="row">f/{n:g}</th>{"".join(cells)}</tr>'
    return ('<div class="fc-tablewrap"><table class="fc-table"><caption>Hiperfocal: enfoca a esta distancia y queda nítido desde la mitad hasta el infinito</caption>'
            f'<thead><tr><th scope="col">Diafragma</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
            '<p class="fc-table-note">Para una copia normal (círculo de confusión de 0.03 mm). Si vas a revisar al 100 % o a recortar, '
            'enfoca al doble de la distancia de la tabla. f/16 ya ablanda por difracción en la 6D: úsalo sólo si necesitas esa profundidad. '
            'El zoom 35–80 mm a 35 o 50 mm usa la columna de esa focal.</p>')


def technique_rows() -> str:
    labels = {key: value["es"] for key, value in DATA["techniques"].items()}
    rows = []
    for key, base in DATA["field_baselines"].items():
        technique = re.sub(r"_\d$", "", key)
        rows.append(f'<li class="fc-mini"><span aria-hidden="true">{TECHNIQUE_ICONS[technique]}</span><div><b>{esc(labels[technique])}</b>'
                    f'<p class="fc-base">{esc(lens_text(base["lens"]))} · {esc(base["aperture"])} · {esc(base["shutter"])} · ISO {esc(base["iso"])}</p>'
                    f'<p>{esc(base["af"])}</p><p>{esc(base["geometry"])}</p></div></li>')
    return "".join(rows)


def lens_text(text: str) -> str:
    return re.sub(r"(\d)mm", r"\1 mm", text).replace(" @", " a ")


# W11: where each setting the plans use lives on the 6D, read in Canon's EOS 6D instruction
# manual (pp. 24, 45-46, 92, 98, 106, 128, 148, 154, 165).
CONTROLS = [
    ("M", "Modo manual", "Pon el dial de modo en M (mantén pulsado su botón central para girarlo). La velocidad va en el dial "
     "principal, detrás del disparador; el diafragma, en el dial de control rápido, la rueda grande de atrás. Si un dial no "
     "responde, pasa a la izquierda el interruptor de bloqueo."),
    ("ISO", "ISO", "Pulsa el botón ISO de arriba y gira un dial mirando el panel superior: va de {iso_low} a {iso_high} en "
     "tercios de paso. En M no uses ISO Auto: cambiaría la exposición que da el plan."),
    ("AF", "Enfoque", "Pon el interruptor del objetivo en AF. Pulsa el botón AF de arriba y gira un dial: ONE SHOT para lo "
     "quieto, AI SERVO para seguir al perro que corre (la 6D los muestra así, en mayúsculas)."),
    ("⏱", "Disparo y retardo", "Pulsa el botón DRIVE y gira un dial: foto a foto, continuo (≈{fps} fotos/s), silencioso, y los "
     "temporizadores de 10 s y 2 s, que también arrancan con el control remoto."),
    ("B", "B (Bulb) para más de {longest} s", "Pon el dial de modo en B. El diafragma va en un dial; el obturador queda abierto "
     "mientras pulses el disparador y el panel superior cuenta los segundos. Para no tocar la cámara, Canon indica el "
     "disparador RS-80N3 o el temporizador TC-80N3."),
    ("🪞", "Bloqueo del espejo", "Menú de disparo 2 → bloqueo del espejo → Activar. El primer disparo sube el espejo y el "
     "segundo hace la foto: así su golpe no mueve las tomas largas en trípode."),
    ("NR", "Ruido en exposiciones largas", "Menú de disparo 4 → reducción de ruido en largas exposiciones → Auto: actúa en las "
     "fotos de 1 s o más cuando detecta ruido."),
]


def camera_controls() -> str:
    camera = DATA["gear"]["camera"]
    iso_low, iso_high = re.match(r"(\d+)–(\d+)", camera["iso"]).groups()
    values = {"iso_low": iso_low, "iso_high": iso_high, "fps": f"{camera['fps']:g}",
              "longest": em.THIRD_STOP_SHUTTERS[-1].rstrip('"')}
    rows = [(icon, title.format(**values), text.format(**values)) for icon, title, text in CONTROLS]
    return ('<h3 class="fc-h3" id="fc-h-controls">Cómo se pone en tu 6D</h3>'
            f'<ul class="fc-grid">{mini_cards(rows)}</ul>'
            '<p class="fc-table-note">Según el manual de instrucciones de la EOS 6D (Canon), págs. 24, 45–46, 92, 98, 106, 128, '
            '148, 154 y 165. Los nombres del menú cambian un poco con el idioma de la cámara.</p>')


def gear_list() -> str:
    camera = DATA["gear"]["camera"]
    lenses = "".join(f'<li class="fc-mini"><span aria-hidden="true">{esc(str(lens["focal"]).replace("-", "–"))}</span><div><b>{esc(lens["name"])}</b>'
                     f'<p>Apertura máxima f/{esc(str(lens["max_ap"]).replace("-", "–"))} · enfoca desde {number(lens["min_focus_m"])} m · rosca de {lens["filter_mm"]} mm</p></div></li>'
                     for lens in DATA["gear"]["lenses"])
    return (f'<p class="fc-body-text"><b>{esc(camera["name"])}</b>: {esc(camera["sensor"])}, ISO {esc(camera["iso"])}, '
            f'hasta 1/4000 s, {camera["af_points"]} puntos de enfoque.</p><ul class="fc-grid">{lenses}</ul>')


def offline_pack() -> str:
    """Plan pages and every diagram, for the service worker to keep (V07)."""
    pages = [f"plans/{plan['id']}.html" for plan in DATA["plans"]]
    diagrams = [f"diagrams-webp/{png.stem}.webp" for png in sorted((ROOT / "diagrams").glob("*.png"))]
    urls = json.dumps(pages + diagrams, separators=(",", ":"))
    return ('<section class="fc-offline" id="fc-offline" hidden aria-labelledby="fc-h-offline"><h3 class="fc-h3" id="fc-h-offline">Sin conexión</h3>'
            '<p class="fc-body-text">Esta tarjeta ya funciona sin conexión. Guarda también los seis planes con sus '
            f'{len(diagrams)} diagramas para consultarlos donde no hay señal; ocupa unos 11 MB.</p>'
            f"<button type=\"button\" id=\"fc-pack\" class=\"fc-reset fc-pack-button\" data-urls='{urls}'>Guardar planes y diagramas</button>"
            '<p id="fc-pack-status" class="fc-body-text" role="status"></p></section>')


def sun_strip() -> str:
    chips_html = "".join(f'<li><span aria-hidden="true">{icon}</span> {name} <b data-slot-window="{slot}">—</b></li>' for slot, name, icon in SLOTS)
    return (
        '<section class="fc-sun" aria-labelledby="fc-sun-title"><h2 id="fc-sun-title">Luz en Lima</h2>'
        f'<ul class="fc-sun-slots">{chips_html}</ul>'
        '<p id="fc-now" class="fc-now" aria-live="polite">Con JavaScript verás la hora de cada luz para hoy. '
        'Día: del amanecer a una hora antes de la puesta. Tarde: la última hora de sol y la hora azul. Noche: desde que termina la hora azul.</p>'
        '<div class="fc-tools"><label class="fc-date" hidden>Otro día <input id="fc-date" type="date"></label>'
        '<label class="fc-toggle"><input id="fc-night" type="checkbox"> Pantalla de noche</label>'
        '<label class="fc-toggle" hidden><input id="fc-awake" type="checkbox"> No apagar la pantalla</label>'
        '<button type="button" id="fc-ics" class="fc-toggle fc-ics" hidden><span aria-hidden="true">📅</span> Añadir al calendario</button></div></section>'
    )


def controls() -> str:
    plans = DATA["plans"]
    plan_options = [(p["id"], f'<b>{plan_letter(p)}</b>', p["name"]) for p in plans]
    names = "".join(f'<p class="fc-plan-name" data-plan="{p["id"]}" data-name="Plan {plan_letter(p)} · {esc(p["name"])}" '
                    f'data-location="{esc(p["location"])}"><b>Plan {plan_letter(p)}</b> · {esc(p["name"])}<br><small>{esc(p["location"])}</small>'
                    f'<br><small>Acceso: {esc(p["access"])}</small></p>' for p in plans)
    slot_options = [(slot, f'<span aria-hidden="true">{icon}</span> {name}', "") for slot, name, icon in SLOTS]
    subject_options = [(key, name, "") for key, name in SUBJECTS]
    return (radio_group("fc-plan", "Plan", plan_options, "fc-plans") + names +
            radio_group("fc-slot", "Luz", slot_options, "fc-slots") +
            radio_group("fc-subject", "Con quién", subject_options, "fc-subjects"))


def panel(tab: str, title: str, intro: str, body: str) -> str:
    return (f'<section class="fc-panel fc-panel-{tab}" aria-labelledby="fc-h-{tab}"><h2 id="fc-h-{tab}">{title}</h2>'
            f'<p class="fc-intro">{intro}</p>{body}</section>')


def shots_panel() -> str:
    cards = "".join(shot_card(plan, shot) for plan in DATA["plans"] for shot in plan["shots"])
    head = ('<div class="fc-listhead"><p class="fc-intro">Marca cada toma sólo después de revisarla al 100 %. '
            'Los valores son los del plan para esa luz.</p><button type="button" id="fc-reset" class="fc-reset">Reiniciar esta lista</button></div>'
            '<p id="fc-status" class="fc-sr" role="status"></p>')
    return (f'<section class="fc-panel fc-panel-shots" aria-labelledby="fc-h-shots"><h2 id="fc-h-shots">Tomas</h2>'
            f'{controls()}{head}<ol class="fc-shots">{cards}</ol>'
            '<p class="fc-note"><b>Regla maestra:</b> poca profundidad de campo depende de la apertura, la focal, la distancia al sujeto '
            'y la del sujeto al fondo. Alejar el fondo suele cambiar la foto más que abrir un tercio de paso.</p></section>')


def tab_bar() -> str:
    options = "".join(
        f'<label class="fc-tab"><input type="radio" name="fc-tab" value="{tab}"{" checked" if i == 0 else ""}>'
        f'<span aria-hidden="true">{icon}</span><span>{name}</span></label>'
        for i, (tab, name, icon) in enumerate(TABS))
    return f'<fieldset class="fc-tabs"><legend class="fc-sr">Sección</legend>{options}</fieldset>'


def app(title_tag: str) -> str:
    gear = "".join(packing_list(plan) for plan in DATA["plans"])
    return (
        f'<div id="field-card-app" class="fc-app">'
        f'<header class="fc-hero"><div class="fc-headrow"><{title_tag} class="fc-title">Tarjeta de campo</{title_tag}>'
        '<p class="fc-progress" aria-live="polite"><b id="fc-count">0/10</b> hechas</p></div>'
        '<p class="fc-sub">Canon 6D · los ajustes exactos de cada toma para la luz en la que estás</p>'
        f'{sun_strip()}</header>'
        f'{tab_bar()}{shots_panel()}'
        + panel("techniques", "Técnicas · valores de partida", "Para improvisar fuera de un plan: el punto de partida de cada técnica.",
                f'<ul class="fc-grid">{technique_rows()}</ul><h3 class="fc-h3">Filtro ND</h3>{nd_table()}'
                f'<h3 class="fc-h3">Hiperfocal</h3>{hyperfocal_table()}')
        + panel("rescue", "Cuando la foto no sale", "Cambia una sola variable cada vez y conserva la que crea el efecto.",
                f'<ul class="fc-grid">{mini_cards(RESCUE, " fc-rescue")}</ul>'
                '<p class="fc-note fc-danger"><b>No negociable:</b> para congelar no sacrifiques 1/2000; para barrer no subas de 1/40 a 1/250; '
                'para fantasma, larga exposición o efecto zoom no muevas la cámara.</p>')
        + panel("framing", "Composición y ángulo", "Una intención dominante; no colecciones reglas.",
                f'<ul class="fc-grid">{mini_cards(COMPOSITION)}{mini_cards(ANGLES)}</ul>')
        + panel("gear", "Qué llevar", "Calculado a partir de las tomas viables del plan elegido.",
                f'{gear}<h3 class="fc-h3">Antes de salir</h3><ul class="fc-grid">{mini_cards(BEFORE_LEAVING)}</ul>'
                f'{offline_pack()}<h3 class="fc-h3">Tu equipo</h3>{gear_list()}{camera_controls()}')
        + '<button type="button" id="fc-next" class="fc-next" hidden>Siguiente toma ↓</button></div>'
    )


def visibility_rules() -> str:
    """Show the cards of the chosen plan, light, subject and section; :has() needs no script."""
    rules = []
    for plan in DATA["plans"]:
        pid = plan["id"]
        rules.append(f'.fc-app:has(input[name=fc-plan][value={pid}]:checked) :is(.fc-shot,.fc-plan-name,.fc-pack)[data-plan={pid}]{{display:block}}')
    for slot, _name, _icon in SLOTS:
        chosen = f'.fc-app:has(input[name=fc-slot][value={slot}]:checked)'
        rules.append(f'{chosen} .fc-slot[data-slot={slot}]{{display:block}}')
        rules.append(f'{chosen} .fc-shot:has(.fc-slot[data-slot={slot}] .fc-check:checked){{border-color:var(--fc-ok);background:var(--fc-ok-bg)}}')
    for key, _name in SUBJECTS:
        rules.append(f'.fc-app:has(input[name=fc-subject][value={key}]:checked) .fc-who-{key}{{display:block}}')
    for tab, _name, _icon in TABS:
        rules.append(f'.fc-app:has(input[name=fc-tab][value={tab}]:checked) .fc-panel-{tab}{{display:block}}')
    return "\n".join(rules)


CSS_FILE = ROOT / "assets" / "field_card.css"


def card_css() -> str:
    return CSS_FILE.read_text(encoding="utf-8").replace("/* VISIBILITY_RULES */", visibility_rules())


PAGE_CSS = """html{-webkit-text-size-adjust:100%}body{margin:0;background:#f4f1e9}body:has(#fc-night:checked){background:#000}body:has(#fc-night:checked) .fc-page-top a{color:#ff6b5e}
.fc-page-top{max-width:760px;margin:0 auto;padding:12px 12px 0}.fc-page-top a{display:inline-flex;align-items:center;min-height:44px;padding:0 4px;font:600 15px/1.2 system-ui,sans-serif;color:#0b1724}
@media(prefers-color-scheme:dark){body{background:#0b1220}.fc-page-top a{color:#f1f5f9}}"""


def page(app_html: str, css: str, js: str, sun_js: str, gear_js: str, diagnostics_js: str) -> str:
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#061827"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="assets/app-icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="assets/icon-192.png">
<meta name="description" content="Tarjeta de campo de FocalRuta: los ajustes exactos de cada toma de los seis planes para la luz de día, tarde o noche, la hora de cada luz en Lima y qué llevar. Funciona sin conexión.">
<meta name="apple-mobile-web-app-capable" content="yes"><script id="diagnostics-js">\n{diagnostics_js}</script><title>Tarjeta de campo · FocalRuta</title>
<style>{PAGE_CSS}
{css}</style></head>
<body><nav class="fc-page-top" aria-label="Sitio"><a href="index.html">← Volver a FocalRuta</a></nav>
<main>{app_html}</main>
<script>{sun_js}</script><script id="gear-js">\n{gear_js}</script><script>{js}</script>
<script>if(('serviceWorker' in navigator)&&(location.protocol==='http:'||location.protocol==='https:')){{window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(e=>FocalRutaDiagnostico.record('trabajador',e&&e.message||String(e),'sw.js')));}}</script>
</body></html>
"""


def main() -> None:
    css = card_css()
    js = (ROOT / "assets" / "field_card.js").read_text(encoding="utf-8")
    sun_js = (ROOT / "assets" / "sun_times.js").read_text(encoding="utf-8")
    gear_js = (ROOT / "assets" / "gear.js").read_text(encoding="utf-8")
    diagnostics_js = (ROOT / "assets" / "diagnostics.js").read_text(encoding="utf-8")
    OUT.write_text(page(app("h1"), css, js, sun_js, gear_js, diagnostics_js), encoding="utf-8")
    # The home page shows the card in a dialog next to its own h1.
    (ROOT / "data" / "field_card_fragment.html").write_text(app("p"), encoding="utf-8")
    (ROOT / "data" / "field_card.css").write_text(css, encoding="utf-8")
    (ROOT / "data" / "field_card.js").write_text(js, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
