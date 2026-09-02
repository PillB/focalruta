#!/usr/bin/env python3
"""Generate the dependency-free Arquitectura en Foco challenge."""
from __future__ import annotations
import json
import re
from html import escape
from pathlib import Path

import lab_visuals

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data/architecture/competition_rules.json"
LEARNING_PATH = ROOT / "data/architecture/learning.json"
PHOTOGRAPHERS_PATH = ROOT / "data/architecture/photographers.json"
COHORT_PATH = ROOT / "architectural_photography/research/locations/verification_cohort.json"
CANONICAL_PATH = ROOT / "architectural_photography/ranking/canonical_candidates.json"
PUBLIC_CANDIDATES_PATH = ROOT / "data/architecture/candidates.json"
VERIFICATION_PATH = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
RANKING_PATH = ROOT / "data/architecture/ranking.json"
ROUTES_PATH = ROOT / "data/architecture/routes.json"
DISCOVERIES_PATH = ROOT / "data/architecture/style_discoveries.json"
DISCOVERY_DOSSIERS_PATH = ROOT / "architectural_photography/research/locations/style_discovery_dossiers.json"
OUTPUT = ROOT / "challenges/arquitectura-en-foco/index.html"
IPHONE_HELP = ROOT / "challenges/arquitectura-en-foco/iphone-maps.html"
FIELD_CARD = ROOT / "challenges/arquitectura-en-foco/field-card.html"
VIDEO_LEDGER_PATH = ROOT / "architectural_photography/research/videos/VIDEO_LEDGER.json"
TECHNIQUE_WIKI = ROOT / "challenges/arquitectura-en-foco/wiki-tecnicas.html"
PHYSICS_GUIDE = ('<aside class="beginner-guide"><h3>De dónde salen estos dibujos</h3><p>Los nueve laboratorios no dibujan formas a ojo: calculan la física y aplican el resultado. El campo de visión sale de <strong>atan(sensor / 2·focal)</strong>, así que la posición controla la perspectiva y la focal controla el encuadre desde una posición fija. El tono de una fachada mate sigue la ley de Lambert, es decir cae con <strong>cos(θ)</strong>, donde θ es el ángulo entre la luz y la perpendicular de esa cara. La sombra mide <strong>altura / tan(altura del sol)</strong> y su borde se abre según el tamaño angular de la fuente: el sol mide medio grado y deja un borde duro; un cielo de garúa cubre decenas de grados y borra la umbra. El reflejo del vidrio usa la aproximación de Schlick y el halo crece con el brillo de la fuente.</p><p><strong>Y aquí está el límite:</strong> cada laboratorio predice la dirección y el orden de magnitud de una relación. No es una simulación calibrada ni una predicción de píxeles: no anticipa tu exposición, tu clima ni el comportamiento de un objetivo concreto. Sirve para reconocer la relación en la calle, no para sustituir la prueba. Puedes consultar cada fórmula con su fuente en la <a href="wiki-tecnicas.html#fisica">wiki de técnicas</a>.</p></aside>')

CSS = """:root{--ink:#10211d;--muted:#5e6d67;--paper:#f4f0e7;--card:#fffdf8;--accent:#b84c32;--green:#176b55;--line:#cbc2b2}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}a{color:inherit}header,main,footer{max-width:1040px;margin:auto;padding-inline:clamp(18px,4vw,48px)}header{padding-top:34px;padding-bottom:28px}h1{font-size:clamp(2.5rem,10vw,6rem);line-height:.88;margin:.3em 0}h2{font-size:clamp(1.7rem,5vw,3rem);line-height:1.05}.eyebrow,.status{font-size:.75rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:var(--green)}nav{position:sticky;top:0;z-index:5;display:flex;gap:6px;overflow:auto;padding:8px max(12px,env(safe-area-inset-left));background:rgba(244,240,231,.96);border-block:1px solid var(--line)}nav a{min-height:44px;display:grid;place-items:center;padding:0 13px;border-radius:999px;text-decoration:none;font-weight:750;white-space:nowrap}nav a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid var(--accent);outline-offset:2px}section{padding:34px 0;border-top:1px solid var(--line)}.command,.callout{padding:18px;border-radius:16px;background:var(--ink);color:white}.command-grid,.scenes{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}.command-grid article,.scene{padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--card)}.command-grid article{color:var(--ink)}.scene .reject{color:var(--muted);font-size:.92rem}.ranking-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px;margin-bottom:16px}.rank-number{font-size:2rem;font-weight:900;line-height:1}.rank-meta{display:flex;flex-wrap:wrap;gap:6px}.rank-meta span{padding:3px 8px;border:1px solid var(--line);border-radius:999px;font-size:.78rem}.route-preview{display:block;width:100%;height:auto;margin:12px 0;border:1px solid var(--line);border-radius:10px;background:#e9eee9}.route-preview polyline{fill:none;stroke:var(--accent);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}.route-preview circle{fill:var(--ink);stroke:white;stroke-width:2}.route-preview text{fill:white;font:bold 8px system-ui;text-anchor:middle;dominant-baseline:central}.route-note{font-size:.82rem;color:var(--muted)}.modes{columns:2;gap:30px}label{display:block;font-weight:750;margin-top:13px}input,textarea,select,button{width:100%;min-height:44px;font:inherit}textarea{min-height:82px}button{margin-top:10px;padding:9px 14px;border:0;border-radius:10px;background:var(--ink);color:white;font-weight:800}.actions{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.actions button{background:var(--green)}.secondary{background:white!important;color:var(--ink)!important;border:1px solid var(--line)!important}.rule{font-weight:800}.warning{border-left:5px solid var(--accent);padding-left:16px}footer{padding-block:30px 70px;color:var(--muted)}@media(max-width:560px){.modes{columns:1}.actions{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}"""

CSS += ":root{--sticky-nav-offset:84px}html{scroll-padding-top:var(--sticky-nav-offset)}section{scroll-margin-top:var(--sticky-nav-offset)}"
CSS += ".learning-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:14px}.lesson-card,.learning-lab,.video-transfer{padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--card)}.lesson-card details{margin-top:8px}.lesson-card summary{min-height:44px;display:flex;align-items:center;font-weight:800;cursor:pointer}.learning-lab{grid-column:span 1}.lab-frame{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#eef0e9;margin:12px 0}.lab-readout{min-height:52px;padding:10px;border-radius:10px;background:#eef6f2}.source-links{font-size:.82rem;color:var(--muted)}@media(min-width:800px){.learning-lab{grid-column:span 2}}"
CSS += "header,main,footer{max-width:1160px;padding-inline:clamp(24px,6vw,72px)}section{padding-block:42px}.beginner-guide{background:#fffaf0;border:1px solid var(--line);border-radius:18px;padding:clamp(22px,4vw,42px);margin-block:20px}.beginner-guide dl{display:grid;grid-template-columns:minmax(10rem, .35fr) 1fr;gap:12px 24px}.beginner-guide dt{font-weight:850;color:var(--green)}.beginner-guide dd{margin:0;max-width:70ch}.scene,.lesson-card,.learning-lab,.video-transfer{min-width:0;overflow-wrap:anywhere}.scene p{max-width:72ch}@media(max-width:620px){.beginner-guide dl{grid-template-columns:1fr;gap:4px}.beginner-guide dd{margin-bottom:14px}}"
CSS += ".lab-frame text,.wiki-diagram text{font-family:system-ui,sans-serif;fill:var(--ink)}.lab-frame,.wiki-diagram{overflow:hidden}.lab-controls{display:grid;gap:4px;margin-bottom:10px}"
CSS += ".lab-cycle{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:10px 0}.lab-cycle span,.lab-legend span{padding:6px 8px;border-radius:8px;background:#eef6f2;font-size:.78rem;font-weight:750}.lab-legend{display:flex;flex-wrap:wrap;gap:6px}.lab-reset{width:auto;min-height:44px;background:var(--card);color:var(--ink);border:2px solid var(--green)}.learning-lab:focus-within{border-color:var(--green);box-shadow:0 0 0 3px rgba(23,107,85,.16)}.lab-frame{min-height:260px}.comparison-pane{stroke:#cbc2b2;stroke-width:2;fill:#fffdf8}.state-layer{transition:opacity .18s ease}.state-layer[hidden]{display:none}@media(max-width:700px){.learning-grid{display:block}.learning-lab{margin-bottom:14px;padding:14px}.lab-frame{min-height:220px}.lab-cycle{grid-template-columns:1fr 1fr}}@media(min-width:701px) and (max-width:1000px){.learning-grid{grid-template-columns:1fr 1fr}.learning-lab{grid-column:span 2}}@media(prefers-reduced-motion:reduce){.state-layer{transition:none}}"

SCRIPT = r"""const KEY='focalruta.architecture.field.v1',form=document.querySelector('#field-form'),status=document.querySelector('#save-status'),sceneLimit=document.querySelector('#scene-limit');
const state=()=>({...Object.fromEntries(new FormData(form).entries()),sceneLimit:sceneLimit.value});function applySceneLimit(){const cards=[...document.querySelectorAll('#scene-cards .scene')],limit=sceneLimit.value==='all'?cards.length:Number(sceneLimit.value);cards.forEach((card,index)=>card.hidden=index>=limit);document.querySelector('#scene-count-status').textContent=`Mostrando ${Math.min(limit,cards.length)} de ${cards.length} escenas.`}function applyRankingView(){const scenario=document.querySelector('#ranking-scenario').value,control=document.querySelector('#ranking-limit'),cards=[...document.querySelectorAll('#ranking-cards .scene')],limit=control.value==='all'?cards.length:Number(control.value);cards.sort((a,b)=>Number(a.dataset[scenario])-Number(b.dataset[scenario])||a.dataset.name.localeCompare(b.dataset.name,'es')).forEach((card,index)=>{card.hidden=index>=limit;card.querySelector('.rank-number').textContent=`#${card.dataset[scenario]}`;card.parentNode.appendChild(card)});document.querySelector('#ranking-count-status').textContent=`Mostrando ${Math.min(limit,cards.length)} de ${cards.length} según ${scenario.toUpperCase()}.`}function applyRouteFilter(){const district=document.querySelector('#route-district').value,cards=[...document.querySelectorAll('#route-cards .scene')];cards.forEach(card=>card.hidden=district!=='all'&&card.dataset.district!==district);const visible=cards.filter(card=>!card.hidden).length;document.querySelector('#route-count-status').textContent=`Mostrando ${visible} de ${cards.length} capas.`}function save(extra={}){localStorage.setItem(KEY,JSON.stringify({...state(),...extra,updatedAt:new Date().toISOString()}));status.textContent='Notas guardadas en este dispositivo.'}function restore(data){for(const [key,value] of Object.entries(data||{})){const control=key==='sceneLimit'?sceneLimit:form.elements.namedItem(key);if(control)control.value=value}status.textContent='Notas restauradas.'}try{restore(JSON.parse(localStorage.getItem(KEY)||'{}'))}catch(error){status.textContent='No se pudieron restaurar las notas.'}applySceneLimit();applyRankingView();applyRouteFilter();sceneLimit.addEventListener('change',()=>{applySceneLimit();save()});document.querySelector('#ranking-scenario').addEventListener('change',applyRankingView);document.querySelector('#ranking-limit').addEventListener('change',applyRankingView);document.querySelector('#route-district').addEventListener('change',applyRouteFilter);form.addEventListener('input',()=>save());document.querySelectorAll('[data-decision]').forEach(button=>button.addEventListener('click',()=>save({decision:button.dataset.decision})));
document.querySelector('#export-field').addEventListener('click',()=>{const blob=new Blob([localStorage.getItem(KEY)||JSON.stringify(state())],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='focalruta-arquitectura-campo.json';a.click();URL.revokeObjectURL(a.href)});document.querySelector('#import-field').addEventListener('click',()=>document.querySelector('#import-file').click());document.querySelector('#import-file').addEventListener('change',event=>{const file=event.target.files[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{try{const data=JSON.parse(reader.result);restore(data);save(data)}catch(error){status.textContent='El archivo no contiene notas válidas.'}};reader.readAsText(file)});document.querySelector('#clear-field').addEventListener('click',()=>{localStorage.removeItem(KEY);form.reset();status.textContent='Notas borradas.'});
function labKey(article){return [...article.querySelectorAll('[data-lab-control]')].map(control=>control.value).join('|')}
function applyLab(article){const table=PHYSICS[article.dataset.lab];if(!table)return;const entry=table[labKey(article)];if(!entry)return;for(const [target,attribute,value] of entry.a){const node=document.getElementById(target);if(!node)continue;if(attribute==='textContent'){node.textContent=value}else{node.setAttribute(attribute,String(value))}}const readout=article.querySelector('.lab-readout');if(readout)readout.textContent=entry.t}
function resetLab(article){article.querySelectorAll('[data-lab-control]').forEach(control=>{control.value=control.dataset.default});applyLab(article);const first=article.querySelector('[data-lab-control]');if(first)first.focus()}
document.querySelectorAll('.learning-lab').forEach(article=>{article.querySelectorAll('[data-lab-control]').forEach(control=>{control.addEventListener('input',()=>applyLab(article));control.addEventListener('change',()=>applyLab(article))});const reset=article.querySelector('.lab-reset');if(reset)reset.addEventListener('click',()=>resetLab(article));applyLab(article)});

document.querySelector('#route-district').addEventListener('change',()=>{const district=document.querySelector('#route-district').value;document.querySelectorAll('#route-collections .scene').forEach(card=>{card.hidden=district!=='all'&&!card.querySelector('.eyebrow').textContent.startsWith(district+' ·')})});
"""

NAV_ITEMS = (
    ("today", "Inicio"),
    ("how-to-read", "Cómo usar"),
    ("learn", "Aprender"),
    ("style-radar", "Nuevos hallazgos"),
    ("scenes", "Lugares"),
    ("ranking", "Comparar"),
    ("field-priorities", "Prioridades"),
    ("route", "Rutas"),
    ("field-run", "En campo"),
    ("ai-firewall", "Revelado"),
    ("rules", "Bases"),
)
STORY_ORDER = tuple(anchor for anchor, _label in NAV_ITEMS if anchor not in {"today", "how-to-read"})


def navigation() -> str:
    links = "".join(f'<a href="#{anchor}">{escape(label)}</a>' for anchor, label in NAV_ITEMS)
    return f'<nav aria-label="Secciones de la guía"><a href="../../index.html">FocalRuta</a>{links}</nav>'


def scene_cards(candidates: list[dict], cohort: dict, verification: dict) -> str:
    active = {item["canonical_id"]: item for item in cohort["candidates"]}
    progress = {item["canonical_id"]: item for item in verification["records"]}
    cards = []
    for candidate in candidates:
        verified = active.get(candidate["canonical_id"])
        mechanism = verified["primary_scene_mechanism"].replace("_", " ").title() if verified else "Mecanismo visual por investigar"
        rejection = "La hipótesis todavía necesita fuentes actuales, comprobación en campo y una prueba A/B/C/D/E; no la tomes como un hecho terminado."
        visual_count = len(progress[candidate["canonical_id"]]["visual_reference_families"])
        desk_verified = progress[candidate["canonical_id"]]["verification_complete"]
        status = f"Dossier de escritorio verificado · {visual_count} referencias · campo pendiente" if desk_verified else f"Forénsica visual: {visual_count} referencias · sin ranking"
        cards.append(
            f'<article class="scene"><p class="eyebrow">{escape(candidate["district"])}</p><h3>{escape(candidate["name"])}</h3>'
            f'<p>{escape(mechanism)}</p><p class="reject"><strong>Puede fallar:</strong> {escape(rejection)}</p>'
            f'<span class="status">{escape(status)}</span></article>'
        )
    return "".join(cards)

def public_candidates(candidates: list[dict], verification: dict) -> list[dict]:
    fields = ("canonical_id", "name", "district", "evidence_status", "ranking_eligible", "requires_current_verification")
    progress = {item["canonical_id"]: item for item in verification["records"]}
    return [
        {
            **{field: candidate[field] for field in fields},
            "visual_reference_count": len(progress[candidate["canonical_id"]]["visual_reference_families"]),
            "verification_complete": progress[candidate["canonical_id"]]["verification_complete"],
        }
        for candidate in candidates
    ]

def ranking_cards(ranking: dict) -> str:
    cards = []
    for item in ranking["results"]:
        ranks = item["scenario_ranks"]
        pareto = " · Pareto" if item["pareto_front"] else ""
        cards.append(
            f'<article class="scene" data-name="{escape(item["name"])}" data-r0="{ranks["R0"]}" data-r1="{ranks["R1"]}" data-r2="{ranks["R2"]}" data-r3="{ranks["R3"]}">'
            f'<div class="rank-number">#{item["robust_rank"]}</div><p class="eyebrow">{escape(item["district"])}{pareto}</p><h3>{escape(item["name"])}</h3>'
            f'<div class="rank-meta"><span>R0 #{ranks["R0"]}</span><span>R1 #{ranks["R1"]}</span><span>R2 #{ranks["R2"]}</span><span>R3 #{ranks["R3"]}</span><span>Campo #{item["field_rank"]}</span></div>'
            f'<p><strong>Por qué entra:</strong> Esta escena tiene una hipótesis visual que conecta espacio, luz y uso actual; el rango muestra prioridad de práctica, no calidad absoluta.</p><p><strong>Qué debes comprobar:</strong> Busca una posición concreta, una acción o ausencia significativa y una condición de luz que hagan visible la relación sin depender del texto.</p><p class="reject"><strong>Qué podría refutarla:</strong> Si solo funciona como postal, necesita un pie de foto para explicar la idea o no puedes confirmar acceso y actividad, baja su prioridad.</p><p class="reject"><strong>Se descarta si:</strong> La relación arquitectónica no se entiende en una sola imagen o exige inventar elementos.</p>'
            f'<p class="status">p50 {item["rank_distribution"]["p50"]} · p10–p90 {item["rank_distribution"]["p10"]}–{item["rank_distribution"]["p90"]} · confianza {round(item["evidence_confidence"] * 100)}%</p></article>'
        )
    return "".join(cards)

def field_priority_cards(ranking: dict) -> str:
    return "".join(
        f'<article class="scene"><div class="rank-number">#{item["field_rank"]}</div><p class="eyebrow">CAMPO · {escape(item["district"])}</p><h3>{escape(item["name"])}</h3><p>Este lugar merece una visita porque ofrece una relación comprobable entre forma construida y vida cotidiana. Confirma primero que puedes entrar, detenerte y fotografiar.</p><p><strong>Prueba:</strong> Haz una toma de estructura, otra con uso humano y una tercera desde una posición distinta; compara qué lectura permanece.</p><p><strong>Plan B:</strong> Si no hay acceso o actividad, vuelve con otra luz o cambia a una escena del mismo distrito.</p><p class="status">confianza de escritorio {round(item["field_confidence"] * 100)}% · ruta por confirmar</p></article>'
        for item in ranking["top_5_field"]
    )


def route_projection(layer: dict) -> tuple[dict[tuple[float, float], tuple[float, float]], list[list[tuple[float, float]]]]:
    lines = [leg["geometry"]["coordinates"] for leg in layer["legs"]]
    coordinates = [tuple(point) for line in lines for point in line]
    coordinates.extend((stop["longitude"], stop["latitude"]) for stop in layer["stops"])
    longitudes, latitudes = [point[0] for point in coordinates], [point[1] for point in coordinates]
    west, east, south, north = min(longitudes), max(longitudes), min(latitudes), max(latitudes)
    width, height = max(east - west, 1e-9), max(north - south, 1e-9)
    project = lambda point: (8 + 204 * (point[0] - west) / width, 112 - 104 * (point[1] - south) / height)
    projected = {point: project(point) for point in coordinates}
    return projected, [[projected[tuple(point)] for point in line] for line in lines]


def route_preview_svg(layer: dict) -> str:
    if not layer["legs"]:
        return ""
    projected, lines = route_projection(layer)
    polylines = "".join('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in line) + '"/>' for line in lines)
    markers = []
    for index, stop in enumerate(layer["stops"], 1):
        x, y = projected.get((stop["longitude"], stop["latitude"]), (8.0, 112.0))
        markers.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7"/><text x="{x:.1f}" y="{y:.1f}">{index}</text>')
    label = escape(f'Trazado peatonal {layer["district"]}: {len(layer["stops"])} paradas')
    return f'<svg class="route-preview" role="img" aria-label="{label}" viewBox="0 0 220 120">{polylines}{"".join(markers)}</svg><p class="route-note">La línea sigue la geometría peatonal OSM capturada; confirma cruces y cierres al salir.</p>'


def optimization_copy(layer: dict) -> str:
    optimization = layer["optimization"]
    if optimization["method"] == "exact_permutation":
        return f'Orden mínimo comprobado entre {optimization["permutations_evaluated"]} permutaciones.'
    if optimization["method"] == "singleton":
        return "Punto aislado verificado; no se presenta como tour."
    if optimization["method"] == "verified_compact_subpath_from_exact_parent":
        return "Subruta peatonal compacta conservada de un orden exacto anterior; no se presenta como un nuevo mínimo independiente."
    return "Subruta contenida de una solución exacta anterior; falta recalcular su matriz y no se presenta como un nuevo mínimo exacto."


def retained_transfer_copy(layer: dict) -> str:
    retained = [leg for leg in layer["legs"] if leg["road_distance_m"] > 800]
    if not retained:
        return ""
    longest = max(leg["road_distance_m"] for leg in retained)
    return (
        '<p class="warning"><strong>Traslado terminal conservado:</strong> '
        f'{longest / 1000:.1f} km. Separarlo aislaría una escena, así que decide en campo '
        'si lo caminas o lo tratas como una salida aparte.</p>'
    )

def route_cards(routes: dict) -> str:
    cards = []
    for layer in routes["district_layers"]:
        stages_html = "".join(
            f'<li><a href="{escape(stage["google_maps_url"])}">Abrir tramo {stage["stage"]} caminando</a> · {len(stage["stop_ids"])} paradas</li>'
            for stage in layer["stages"]
        )
        if not stages_html:
            stages_html = f'<li><a href="{escape(layer["google_maps_search_url"])}">Abrir punto en Google Maps</a> · sin ruta inventada</li>'
        distance = round(layer["optimization"]["selected_distance_m"] / 1000, 1)
        stop_details = "".join(f'<li><strong>{index}. {escape(stop["name"])}</strong><br>{escape(stop["address"])}<br><code>{stop["latitude"]}, {stop["longitude"]}</code></li>' for index, stop in enumerate(layer["stops"], 1))
        partition = ""
        if layer.get("route_partition"):
            info = layer["route_partition"]
            partition = f'<p class="warning"><strong>Tour separado {info["part"]}/{info["parts"]}:</strong> un traslado mayor de 800 m se retiró de esta caminata fotográfica.</p>'
        cards.append(
            f'<article class="scene" data-district="{escape(layer["district"])}"><p class="eyebrow">{escape(layer["district"])} · RED PEATONAL</p><h3>{len(layer["stops"])} paradas · {distance} km</h3>'
            f'<p>{optimization_copy(layer)} El tiempo es una captura, no tráfico en vivo.</p>{route_preview_svg(layer)}{partition}{retained_transfer_copy(layer)}<ol>{stages_html}</ol>'
            f'<details><summary>Direcciones y coordenadas</summary><ol>{stop_details}</ol></details><p><a href="maps/{escape(Path(layer["kml_path"]).name)}" download>Descargar KML</a> · <a href="maps/{escape(Path(layer["geojson_path"]).name)}" download>GeoJSON</a> · <a href="maps/{escape(Path(layer["offline_map_path"]).name)}" download>Mapa HTML offline</a></p></article>'
        )
    return "".join(cards)


def route_collection_cards(routes: dict) -> str:
    layers = {layer["layer_id"]: layer for layer in routes["district_layers"]}
    cards = []
    for collection in routes.get("route_collections", []):
        segment_text = "".join(f'<li>{len(layers[item]["stops"])} paradas · {round(layers[item]["optimization"]["selected_distance_m"] / 1000, 1)} km · <a href="maps/{escape(Path(layers[item]["offline_map_path"]).name)}" download>mapa offline</a></li>' for item in collection["segments"])
        point_text = "".join(f'<li>{escape(layers[item]["stops"][0]["name"])} · Punto independiente · <a href="{escape(layers[item]["google_maps_search_url"])}">Google Maps</a></li>' for item in collection["independent_points"])
        cards.append(f'<article class="scene"><p class="eyebrow">{escape(collection["district"])}</p><h3>{escape(collection["title"])}</h3><p>{escape(collection["routing_note"])}</p><h4>Segmentos caminables</h4><ul>{segment_text or "<li>No hay segmento caminable en esta colección.</li>"}</ul><h4>Puntos independientes</h4><ul>{point_text or "<li>Ninguno.</li>"}</ul></article>')
    return "".join(cards)

def route_district_options(routes: dict) -> str:
    districts = sorted({layer["district"] for layer in routes["district_layers"]})
    return "".join(f'<option value="{escape(district)}">{escape(district)}</option>' for district in districts)

def discovery_cards(discoveries: dict, dossiers: dict) -> str:
    evidence = {item["canonical_id"]: item for item in dossiers["records"]}
    cards = []
    for item in discoveries["discoveries"]:
        dossier = evidence[item["discovery_id"]]
        question = "¿Puedes mostrar en una sola imagen cómo se usa hoy este espacio?"
        cards.append(
            f'<article class="scene"><p class="eyebrow">{escape(item["district"])} · RADAR</p>'
            f'<h3>{escape(item["name"])}</h3><p><strong>Qué observar:</strong> Compara volumen, material, luz y actividad actual; el estilo es una pista, no una conclusión.</p>'
            f'<p>Busca una relación visible entre el edificio y las personas que lo atraviesan. No dependas del pie de foto para explicar la idea.</p><p><strong>Pregunta de campo:</strong> {escape(question)}</p>'
            f'<p class="reject"><strong>Se descarta si:</strong> Solo funciona como fachada bonita, no puedes confirmar acceso o la historia solo existe en el texto.</p>'
            f'<p class="status">Dossier completo · ranking y capa peatonal verificados · confirma acceso el mismo día</p>'
            f'<p><a href="{escape(dossier["sources"][0]["url"])}">Fuente actual</a> · '
            f'{len(dossier["visual_reference_families"])} familias multiángulo</p></article>'
        )
    return "".join(cards)


def lesson_cards(learning: dict) -> str:
    labels = (
        ("observe", "OBSERVA"), ("try", "PRUEBA"), ("diagnose", "DIAGNOSTICA"),
        ("break_the_rule_when", "ROMPE LA REGLA CUANDO"), ("canon_6d_note", "CANON 6D"),
        ("competition_note", "CONCURSO"),
    )
    cards = []
    for lesson in learning["lessons"]:
        body = "".join(f'<p><strong>{label}:</strong> {escape(lesson[field])}</p>' for field, label in labels)
        cards.append(
            f'<article class="lesson-card"><p class="eyebrow">{escape(lesson["lesson_id"])}</p>'
            f'<h3>{escape(lesson["title"])}</h3><p><strong>OBSERVA:</strong> {escape(lesson["observe"])}</p>'
            f'<details><summary>Práctica y diagnóstico</summary>{body.split("</p>", 1)[1]}</details></article>'
        )
    return "".join(cards)


def video_transfer_cards(learning: dict) -> str:
    cards = []
    for module in learning["video_modules"]:
        seconds = int(module["timestamp_seconds"])
        url = f'https://www.youtube.com/watch?v={module["video_id"]}&t={seconds}'
        cards.append(
            f'<article class="video-transfer"><p class="eyebrow">VIDEO · Lección con subtítulos</p>'
            f'<h3>Decisión práctica: {escape(module["video_id"])}</h3><p>Observa cómo una decisión de posición, luz, composición o enfoque cambia la lectura de una escena.</p>'
            f'<p><strong>Al campo:</strong> Repite la idea en una parada real, cambia una sola variable y anota qué relación se volvió más clara.</p>'
            f'<p class="reject"><strong>Evita este error:</strong> No copies una regla automáticamente; comprueba si mejora la historia y respeta el encargo.</p>'
            f'<p class="source-links"><a href="{escape(url)}">Abrir momento citado · {seconds // 60}:{seconds % 60:02d}</a></p></article>'
        )
    return "".join(cards)


def technique_cards(learning: dict) -> str:
    return "".join(
        f'<article class="scene technique-card"><p class="eyebrow">TÉCNICA</p><h3>{escape(card["title"])}</h3>'
        f'<p>{escape(card["mechanism"])}</p><p><strong>Prueba:</strong> {escape(card["field_test"])}</p>'
        f'<p><strong>Diagnóstico:</strong> {escape(card["diagnosis"])}</p>'
        f'<p class="reject"><strong>Cuidado:</strong> {escape(card["misconception_warning"])}</p></article>'
        for card in learning["technique_cards"]
    )


def source_links(sources: list[str]) -> str:
    return " · ".join(f'<a href="{escape(url)}">Fuente {index}</a>' for index, url in enumerate(sources, 1))


def learning_labs(learning: dict) -> str:
    """Interactive labs whose geometry is computed in Python, not in the browser."""
    return lab_visuals.render_labs(learning)


def learning_path_eyebrow(learning: dict) -> str:
    labels = {
        "SEE": "VER", "POSITION": "POSICIONAR", "COMPOSE": "COMPONER", "LIGHT": "ILUMINAR",
        "WORK_THE_SCENE": "TRABAJAR", "FINISH": "TERMINAR", "COMPETE": "COMPETIR",
    }
    return " → ".join(labels.get(step, step) for step in learning["learning_path"])


def iphone_help_page() -> str:
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Mapas en iPhone · FocalRuta</title><style>{CSS}</style></head><body><header><p class="eyebrow">ELI5</p><h1>Abre tu ruta en iPhone 13 Pro</h1></header><main>
<section><h2>La forma fácil</h2><ol><li>Abre la guía de fotografía arquitectónica en Safari.</li><li>Busca tu distrito y toca <strong>Abrir tramo caminando</strong>.</li><li>Si tienes Google Maps, el enlace lo abre; si no, se abre en Safari.</li><li>Revisa cruces, cierres y veredas en pantalla antes de empezar. Pulsa Iniciar solo cuando estés en la primera parada.</li><li>Al terminar el tramo, vuelve a FocalRuta y abre el siguiente.</li></ol><p class="warning">Cada tramo tiene como máximo cinco paradas porque el navegador móvil admite hasta tres puntos intermedios.</p></section>
<section><h2>Si el enlace no abre</h2><ol><li>Comprueba que tienes conexión a internet.</li><li>Vuelve a FocalRuta, mantén pulsado <strong>Abrir tramo caminando</strong> y elige <strong>Abrir en una pestaña nueva</strong>.</li><li>Si Safari muestra la ruta, toca <strong>Abrir en la app</strong>. Si Google Maps no está instalado, continúa en el navegador.</li><li>Si sigue fallando, descarga el GeoJSON o KML en <strong>Archivos</strong> y conserva la lista de paradas; no pulses repetidamente un enlace que permanece bloqueado.</li></ol></section>
<section><h2>Si quieres ver capas KML</h2><ol><li>En una computadora abre Google My Maps e importa el KML del distrito. Incluye los puntos y la línea peatonal capturada.</li><li>Guarda el mapa en la misma cuenta de Google.</li><li>En tu iPhone abre Google Maps.</li><li>Toca <strong>You</strong>, luego <strong>Maps</strong>, y elige el mapa.</li></ol><p>El KML se puede guardar en Archivos, pero no se importa directamente a My Maps desde iPhone/iPad. Por eso FocalRuta usa enlaces de ruta directos como flujo principal.</p></section>
<p><a href="index.html">Volver a fotografía arquitectónica</a></p></main></body></html>'''

def field_card_page() -> str:
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tarjeta de campo · Fotografía arquitectónica</title><style>{CSS}</style></head><body><header><p class="eyebrow">TARJETA DESCARGABLE</p><h1>Protocolo de fotografía arquitectónica</h1><p>Guárdala en Archivos para trabajar sin conexión.</p></header><main><section><h2>Antes de salir</h2><ol><li>Elige una colección del distrito y descarga su mapa HTML, KML o GeoJSON.</li><li>Confirma acceso, luz y cierres en el momento; las rutas son capturas, no navegación en vivo.</li><li>Define una hipótesis: posición primero, focal después; protege altas luces.</li></ol></section><section><h2>En cada parada</h2><ol><li>Haz una toma de contexto y una de detalle.</li><li>Repite desde dos posiciones: cambia perspectiva, no solo focal.</li><li>Comprueba verticales, bordes, figura-fondo y gesto humano.</li><li>Anota qué cambió y qué evidencia lo demuestra.</li></ol></section><section><h2>Salida segura</h2><p>No unas puntos independientes como caminata. Si una transferencia supera el umbral publicado, usa Google Maps para recalcularla con conexión.</p><p><a href="index.html">Volver a la guía</a></p></section></main></body></html>'''

PHYSICS_REFERENCE = (
    ("Campo de visión", "semiángulo = atan(d / 2f)",
     "Con 36 mm de sensor, un 35 mm abre 27,2° a cada lado y un 85 mm sólo 11,9°. Alargar la focal cierra el campo: nunca lo abre.",
     "https://scantips.com/lights/fieldofviewmath.html"),
    ("Tamaño proyectado", "h = f · H / z",
     "La altura en el sensor cae con la distancia. Por eso dos fachadas cambian de relación cuando mueves los pies, y no cuando cambias de objetivo.",
     "https://ciechanow.ski/cameras-and-lenses/"),
    ("Punto de fuga vertical", "distancia = f / tan θ",
     "Con la cámara nivelada las verticales no convergen. Al inclinar θ grados su punto de fuga entra hacia el encuadre, y la convergencia crece con la tangente, no en línea recta.",
     "http://chenlab.ece.cornell.edu/people/Andy/publications/Andy_files/rotation_crv2005.pdf"),
    ("Brillo de una cara mate", "L = ρ/π · E · cos θ",
     "El tono de una fachada difusa depende del ángulo entre la luz y su perpendicular. En incidencia rasante llega a cero y sólo queda la luz ambiente.",
     "https://en.wikipedia.org/wiki/Lambert%27s_cosine_law"),
    ("Longitud de sombra", "L = h / tan(altura solar)",
     "Un volumen de 8 m proyecta 2,9 m de sombra con el sol a 70° y 45 m con el sol a 10°. La sombra crece sin límite cuando el sol baja.",
     "https://farside.ph.utexas.edu/teaching/316/lectures/node126.html"),
    ("Umbra y penumbra", "penumbra ≈ distancia · tan(tamaño angular)",
     "El sol mide 0,53°, así que su borde de sombra es duro. Un cielo de garúa cubre decenas de grados: la umbra desaparece y sólo queda una transición.",
     "https://en.wikipedia.org/wiki/Shadow"),
    ("Reflejo en vidrio", "R = F0 + (1 − F0)(1 − cos θ)⁵",
     "El vidrio devuelve un 4 % de frente y casi el 100 % en ángulo rasante. Lo que decide si ves el interior es el contraste entre el cielo reflejado y el interior transmitido.",
     "https://en.wikipedia.org/wiki/Schlick%27s_approximation"),
    ("Profundidad de campo", "H = f²/(N·c) + f",
     "Con c = 0,030 mm en formato completo, cerrar el diafragma aleja el límite lejano mucho más rápido que acerca el cercano.",
     "https://ciechanow.ski/cameras-and-lenses/"),
    ("Perspectiva aérea", "contraste ≈ exp(−bruma · d)",
     "La garúa limeña no sólo apaga: separa planos. Si dos capas conservan el mismo contraste, no habrá profundidad y hará falta solape.",
     "https://ciechanow.ski/lights-and-shadows/"),
)


def symptom_index() -> str:
    items = "".join(
        f'<li><a href="#tecnica-{escape(technique_id)}">{escape(symptom)}</a></li>'
        for symptom, technique_id in lab_visuals.SYMPTOM_INDEX
    )
    return (
        '<section id="sintomas"><p class="eyebrow">EMPIEZA POR AQUÍ</p><h2>¿Qué le pasó a tu foto?</h2>'
        '<p>Si vienes de una salida con una imagen que no funcionó, entra por el síntoma. '
        'Cada enlace lleva a la familia técnica que explica la causa y al laboratorio donde puedes probarla.</p>'
        f'<ul class="symptom-list">{items}</ul></section>'
    )


def physics_reference() -> str:
    rows = "".join(
        f'<article class="physics-row"><h3>{escape(name)}</h3><p class="formula">{escape(formula)}</p>'
        f'<p>{escape(reading)}</p><p class="source-links"><a href="{escape(url)}">Fuente</a></p></article>'
        for name, formula, reading, url in PHYSICS_REFERENCE
    )
    return (
        '<section id="fisica"><p class="eyebrow">DE DÓNDE SALEN LOS DIBUJOS</p><h2>La física que usan los laboratorios</h2>'
        '<p>Los nueve laboratorios no dibujan formas a ojo: calculan estas relaciones y aplican el resultado. '
        'Predicen la dirección y el orden de magnitud de cada efecto; no son renders calibrados y no anticipan '
        'píxeles, exposición real ni el comportamiento de un objetivo concreto.</p>'
        f'<div class="physics-grid">{rows}</div></section>'
    )


def technique_articles(learning: dict) -> str:
    articles = []
    for index, card in enumerate(learning["technique_cards"], 1):
        technique_id = card["technique_id"]
        lab = lab_visuals.TECHNIQUE_LABS.get(technique_id)
        practice = (
            f'<p><a href="index.html#lab-{escape(lab)}">Probarlo en el laboratorio interactivo</a></p>'
            if lab
            else '<p><a href="index.html#rules">Abrir el decodificador del encargo</a></p>'
        )
        articles.append(
            f'<article class="wiki-technique" id="tecnica-{escape(technique_id)}">'
            f'<p class="eyebrow">FAMILIA {index} DE 9</p><h3>{escape(card["title"])}</h3>'
            f'<p>{escape(card["mechanism"])}</p>{lab_visuals.technique_diagram(technique_id)}'
            f'<p class="viz-caption">{escape(lab_visuals.TECHNIQUE_CAPTIONS[technique_id])}</p>'
            f'<p><strong>Qué probar:</strong> {escape(card["field_test"])}</p>'
            f'<p><strong>Qué observar:</strong> {escape(card["diagnosis"])}</p>'
            f'<p class="reject"><strong>Cuándo descartarlo:</strong> {escape(card["misconception_warning"])}</p>'
            f'{practice}<p class="source-links">{source_links(card["sources"])}</p></article>'
        )
    return "".join(articles)


def evidence_articles(ledger: dict) -> str:
    cards = []
    for video in ledger["videos"]:
        claims = video.get("timestamped_claims") or []
        if not claims:
            continue
        title = video.get("exact_title") or video.get("working_title") or f'Video {video["video_id"]}'
        channel = video.get("channel") or "Canal no verificado"
        items = "".join(
            f'<li>{escape(claim["claim"])} '
            f'<a href="https://www.youtube.com/watch?v={escape(video["video_id"])}&t={int(claim["timestamp_seconds"])}s">'
            f'ver desde {int(claim["timestamp_seconds"])} s</a></li>'
            for claim in claims
        )
        cards.append(
            f'<article class="evidence-card"><h3>{escape(title)}</h3><p class="eyebrow">{escape(channel)}</p>'
            f'<ul>{items}</ul><span class="status">Afirmación contrastada con los subtítulos del propio video</span></article>'
        )
    return "".join(cards)


WIKI_CSS = (
    ".wiki-technique,.evidence-card,.physics-row{padding:18px;border:1px solid var(--line);border-radius:14px;"
    "background:var(--card);margin-block:14px}.wiki-diagram{width:100%;height:auto;max-width:420px;display:block;"
    "margin:14px 0;background:#fffdf8;border:1px solid var(--line);border-radius:12px}"
    ".symptom-list{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:8px}"
    ".symptom-list a{display:block;min-height:44px;padding:11px 14px;border:1px solid var(--line);border-radius:12px;"
    "background:var(--card);text-decoration:none;font-weight:650}.symptom-list a:hover{border-color:var(--accent)}"
    ".physics-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:12px}"
    ".formula{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:1.02rem;color:var(--green);font-weight:700}"
    ".evidence-card ul{padding-left:20px}.evidence-card li{margin-block:8px}"
)


def technique_wiki_page(learning: dict, ledger: dict) -> str:
    unavailable = sum(video["transcript_status"] != "CAPTURED" for video in ledger["videos"])
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wiki de técnicas · FocalRuta</title><style>{CSS}{WIKI_CSS}</style></head><body>
<header><p class="eyebrow">WIKI · TÉCNICA, FÍSICA Y PROCEDENCIA</p><h1>Técnicas de fotografía arquitectónica</h1><p>Nueve familias técnicas, la física que las explica y las fuentes en video que las sostienen. Los dibujos son síntesis originales calculadas con las mismas fórmulas que usan los laboratorios: enseñan la relación, no sustituyen la prueba con cámara.</p></header>
<nav aria-label="Wiki"><a href="index.html#learn">Volver a aprender</a><a href="#sintomas">Síntomas</a><a href="#tecnicas">Técnicas</a><a href="#fisica">Física</a><a href="#evidencia">Evidencia</a></nav>
<main>{symptom_index()}
<section id="tecnicas"><p class="eyebrow">NUEVE FAMILIAS</p><h2>De la idea a una prueba visible</h2><p>Cada familia sigue el mismo ciclo: qué mecanismo la produce, qué probar en la calle, qué observar al revisar y cuándo conviene descartarla.</p>{technique_articles(learning)}</section>
{physics_reference()}
<section id="evidencia"><p class="eyebrow">PROCEDENCIA</p><h2>Evidencia en video, con marca de tiempo</h2><p>Cada afirmación enlaza al segundo exacto del video que la sostiene. De los {len(ledger["videos"])} videos del registro, {unavailable} quedaron marcados como «Transcripción no disponible»: sin subtítulos verificables no se les atribuye ninguna enseñanza, ni siquiera una plausible.</p>{evidence_articles(ledger)}</section>
<p><a href="index.html">Volver a la guía de fotografía arquitectónica</a></p></main></body></html>'''


def beginner_guide() -> str:
    return '''<section id="how-to-read" class="beginner-guide"><p class="eyebrow">PARA EMPEZAR · SIN CONOCIMIENTOS PREVIOS</p><h2>Cómo usar esta guía</h2><p>Esta página es una compañera de salida, no un examen. Lee una sección, prueba una decisión pequeña y anota qué cambió. Si una palabra es nueva, aquí tienes el mapa:</p><dl><dt>Matriz de preparación</dt><dd>Compara lugares con cuatro preguntas de práctica. R0 es una mirada equilibrada; R1 busca evitar la postal; R2 pregunta cómo vive la gente el lugar; R3 prioriza forma y luz. Los números son prioridades de entrenamiento, no una nota ni una predicción de concurso.</dd><dt>Tarjeta de lugar</dt><dd>Cuenta qué se puede observar, desde dónde probarlo, qué evidencia falta y qué haría fallar la foto. “Campo” significa que todavía debes comprobarlo personalmente.</dd><dt>Laboratorio</dt><dd>Es un dibujo interactivo. Primero predice, luego mueve un control, mira el cambio y repite la idea con tu cámara. El dibujo enseña una relación; no promete el resultado exacto de un lente.</dd><dt>Ruta y colección</dt><dd>Una colección agrupa tramos caminables del mismo distrito. Una parada independiente no es un tour: llega a ella por separado. Las distancias son capturas verificadas, no tráfico en vivo.</dd><dt>Brief</dt><dd>Escribe qué pide realmente tu encargo o convocatoria antes de disparar: tema, entrega, fecha, acceso y límites de edición.</dd></dl><p><strong>Orden recomendado:</strong> empieza por una tarjeta, practica un laboratorio, elige una colección y termina con la tarjeta descargable de campo.</p></section>'''

def reorder_story(page: str) -> str:
    """Put learning before evaluation while retaining stable anchor IDs."""
    pattern = re.compile(r'<section id="([^"]+)".*?</section>', re.DOTALL)
    sections = {match.group(1): match.group(0) for match in pattern.finditer(page)}
    order = STORY_ORDER
    first = page.index('<section id="ranking"')
    last_match = next(match for match in pattern.finditer(page) if match.group(1) == "rules")
    return page[:first] + "".join(sections[item] for item in order) + page[last_match.end():]


def render(rules: dict, learning: dict, photographers: dict, cohort: dict | None = None, candidates: list[dict] | None = None, verification: dict | None = None, ranking: dict | None = None, routes: dict | None = None, discoveries: dict | None = None, discovery_dossiers: dict | None = None) -> str:
    cohort = cohort or json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    candidates = candidates or json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))
    verification = verification or json.loads(VERIFICATION_PATH.read_text(encoding="utf-8"))
    ranking = ranking or json.loads(RANKING_PATH.read_text(encoding="utf-8"))
    routes = routes or json.loads(ROUTES_PATH.read_text(encoding="utf-8"))
    discoveries = discoveries or json.loads(DISCOVERIES_PATH.read_text(encoding="utf-8"))
    discovery_dossiers = discovery_dossiers or json.loads(DISCOVERY_DOSSIERS_PATH.read_text(encoding="utf-8"))
    visual_started = sum(bool(item["visual_reference_families"]) for item in verification["records"])
    desk_verified = sum(item["verification_complete"] for item in verification["records"])
    options = "".join(f'<option value="{escape(s["canonical_id"])}">{escape(s["name"])}</option>' for s in candidates)
    modes = "".join(f"<li>{escape(mode)}</li>" for mode in photographers["seeing_modes"])
    masters = "".join(
        f'<article class="scene"><h3>{escape(card["photographer"])}</h3><p>{escape(card["signature_question"])}</p>'
        f'<p><strong>Prueba:</strong> {escape(card["field_drill"])}</p></article>'
        for card in photographers["transfer_cards"]
    )
    physics_json = json.dumps(lab_visuals.physics_tables(), ensure_ascii=False, separators=(",", ":"))
    lessons_html = lesson_cards(learning)
    videos_html = video_transfer_cards(learning)
    labs_html = learning_labs(learning)
    techniques_html = technique_cards(learning)
    jurors = " · ".join(escape(name) for name in rules["jurors"])
    routed_stops = sum(len(layer["stops"]) for layer in routes["district_layers"])
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#10211d"><link rel="icon" href="../../assets/app-icon.svg" type="image/svg+xml"><title>Fotografía arquitectónica · FocalRuta</title><style>{CSS}</style></head><body>
<header id="today"><p class="eyebrow">FOCALRUTA · LABORATORIO DE CAMPO</p><h1>Arquitectura<br>en foco</h1><p>Aprende a convertir forma, luz, uso y tiempo en una fotografía que se sostenga antes de la explicación.</p><div class="command"><div class="command-grid"><article><strong>Practica</strong><p>Tres posiciones antes de elegir focal.</p></article><article><strong>Explora</strong><p>{len(candidates)} lugares y escenas; {visual_started} tienen forénsica visual y {desk_verified} dossier de escritorio verificado.</p></article><article><strong>Decide</strong><p>CONTRATO vs USO y una prueba A/B/C/D/E.</p></article><article><strong>Adapta</strong><p>Decodifica cada brief antes de capturar o editar.</p></article></div></div></header>
{navigation()}<main>
<section id="ranking"><p class="eyebrow">MATRIZ DE PREPARACIÓN · NO ES PRONÓSTICO</p><h2>Compara fortalezas y fragilidades</h2><p>R0–R3 son lentes de práctica —balance, anti-postal, habitar y forma/campo—, no criterios oficiales ni estimaciones de resultados. La dispersión muestra sensibilidad a prioridades distintas y Pareto identifica escenas con compromisos útiles.</p><div class="ranking-controls"><div><label for="ranking-scenario">Lente de práctica</label><select id="ranking-scenario"><option value="r0">R0 · balanceado</option><option value="r1">R1 · anti-postal</option><option value="r2">R2 · habitar</option><option value="r3">R3 · forma/campo</option></select></div><div><label for="ranking-limit">Mostrar N o todas</label><select id="ranking-limit"><option value="5">5</option><option value="15" selected>15</option><option value="40">40</option><option value="all">Todas</option></select></div></div><p id="ranking-count-status" role="status" aria-live="polite"></p><div class="scenes" id="ranking-cards">{ranking_cards(ranking)}</div></section>
<section id="field-priorities"><p class="eyebrow">TOP 5 DE CAMPO</p><h2>Valor fotográfico que también se puede intentar</h2><p>Este orden combina potencial, causalidad, evidencia, acceso y factibilidad. Consulta abajo qué escenas ya tienen evidencia peatonal; una escena sin ruta todavía exige verificación manual.</p><div class="scenes">{field_priority_cards(ranking)}</div></section>
<section id="route"><p class="eyebrow">RUTAS PEATONALES · AUDITORÍA DE GEOMETRÍA</p><h2>Colecciones de ruta por distrito</h2><p>Una colección reúne segmentos realmente caminables y declara aparte los puntos que requieren traslado. No se presenta un pin aislado como si fuera un tour. Cada parada incluye dirección breve y latitud/longitud; el mapa HTML funciona offline y Google Maps ofrece una recalculación vigente cuando hay conexión.</p><p class="warning"><strong>{len(routes.get("omitted_intertour_transfers", []))} traslados omitidos:</strong> superaban el umbral operativo y no se presentan como caminata continua.</p><label for="route-district">Filtrar distrito</label><select id="route-district"><option value="all">Todos</option>{route_district_options(routes)}</select><p id="route-count-status" role="status" aria-live="polite"></p><p><a href="iphone-maps.html">Cómo abrirlo en iPhone 13 Pro, paso a paso</a> · <a href="field-card.html" download>Descargar tarjeta de campo</a></p><div class="scenes" id="route-collections">{route_collection_cards(routes)}</div><h3>Detalle de segmentos y puntos</h3><div class="scenes" id="route-cards">{route_cards(routes)}</div></section>
<section id="style-radar"><p class="eyebrow">RADAR · MODERNO / ART NOUVEAU / GEOMETRÍA</p><h2>Nuevos edificios que se ganaron una comparación</h2><p><strong>6/6 dossiers incorporados al ranking y a capas peatonales distritales verificadas.</strong> Cada hallazgo tiene diez pases, A/B/C/D/E, tres preguntas y forénsica multiángulo. Confirma acceso el mismo día antes de salir.</p><div class="scenes">{discovery_cards(discoveries, discovery_dossiers)}</div></section>
<section id="scenes"><p class="eyebrow">UNIVERSO CANÓNICO</p><h2>Todos los lugares y escenas</h2><p>Las {len(candidates)} identidades reconciliadas tienen el mismo contrato de fuentes, imágenes, composición, preguntas, diez pases y A/B/C/D/E. El ranking de escritorio ya puede compararlas; ninguna queda habilitada como ruta hasta verificar ventanas y acceso en campo.</p><label for="scene-limit">Mostrar N escenas</label><select id="scene-limit"><option value="10">10 escenas</option><option value="25">25 escenas</option><option value="40">40 escenas</option><option value="all" selected>Todas las escenas</option></select><p id="scene-count-status" role="status" aria-live="polite">Mostrando todas las escenas.</p><div class="scenes" id="scene-cards">{scene_cards(candidates, cohort, verification)}</div></section>
<section id="learn"><p class="eyebrow">{learning_path_eyebrow(learning)}</p><h2>Aprende antes de perseguir una locación</h2><p>Nueve laboratorios, uno por cada familia técnica. En cada uno mueves un control, la geometría cambia según la física que la gobierna y el texto te dice qué acabas de provocar. Empieza siempre prediciendo: es lo que hace que la relación se te quede.</p><p>Cada laboratorio aísla <strong>una sola</strong> relación para que puedas reconocerla después con la cámara. No es una simulación calibrada: predice hacia dónde va el efecto y cuánto pesa, no los píxeles que dará tu toma.</p><p>{escape(learning["pedagogy"]["evidence"])}</p><div class="learning-grid">{labs_html}</div><h3>Nueve familias técnicas</h3><div class="scenes">{techniques_html}</div><h3>17 ciclos de campo</h3><div class="learning-grid">{lessons_html}</div><h3>Videos convertidos en decisiones</h3><p>Los enlaces abren el momento exacto; el aprendizaje esencial permanece aquí y funciona offline.</p><div class="learning-grid">{videos_html}</div><h3>Seis modos de ver</h3><ol class="modes">{modes}</ol><h3>Preguntas de maestros</h3><div class="scenes">{masters}</div></section>
<section id="field-run"><p class="eyebrow">OFFLINE · GUARDADO LOCAL</p><h2>CONTRATO vs USO</h2><p>Observa diez minutos. Resume el propósito original, registra cinco verbos, encuentra tres posiciones y elige focal al final.</p><form id="field-form"><label for="field-scene">Escena</label><select id="field-scene" name="scene">{options}</select><label for="contract">Propósito original · 8 palabras</label><input id="contract" name="contract" maxlength="90"><label for="verbs">Cinco verbos observados</label><textarea id="verbs" name="verbs"></textarea><label for="device">Dispositivo arquitectónico que causa la acción</label><textarea id="device" name="device"></textarea><label for="failure">Por qué todavía falla la mejor toma</label><textarea id="failure" name="failure"></textarea><div class="actions" role="group" aria-label="Decisión de campo"><button type="button" data-decision="STAY">STAY</button><button type="button" data-decision="MOVE">MOVE</button><button type="button" data-decision="RETURN_OTHER_LIGHT">RETURN OTHER LIGHT</button></div><p id="save-status" role="status" aria-live="polite">Se guarda solo en este dispositivo.</p></form><div class="actions"><button id="export-field" type="button" class="secondary">Exportar notas</button><button id="import-field" type="button" class="secondary">Importar notas</button><button id="clear-field" type="button" class="secondary">Borrar notas</button></div><input id="import-file" type="file" accept="application/json" hidden></section>
<section id="ai-firewall"><p class="eyebrow">EDICIÓN SEGÚN EL BRIEF</p><h2>Separa captura, revelado, composición y generación</h2><p>Una operación aceptable en un encargo puede descalificar otro. No uses eliminación, montaje o generación hasta confirmar la regla vigente.</p></section><section id="rules" class="architecture-preflight"><p class="eyebrow">DECODIFICADOR DE BRIEF · OFFLINE</p><h2>Convierte reglas nuevas en decisiones de campo</h2><p>No conserva reglas de una convocatoria vencida. Antes de participar, copia desde la fuente oficial: elegibilidad, tema, originalidad, cantidad y formato de archivos, fechas y zona horaria, permisos, límites de edición/IA, acceso y canal de entrega.</p><label for="brief-source">Fuente oficial y fecha de consulta</label><input id="brief-source" name="briefSource"><label for="brief-theme">Tema y qué debe ser visible sin texto</label><textarea id="brief-theme" name="briefTheme"></textarea><label for="brief-files">Cantidad, formato, tamaño y nombre</label><textarea id="brief-files" name="briefFiles"></textarea><label for="brief-editing">Edición, composición, eliminación e IA</label><textarea id="brief-editing" name="briefEditing"></textarea><label for="brief-rights">Elegibilidad, acceso, permisos y releases</label><textarea id="brief-rights" name="briefRights"></textarea><label for="brief-deadline">Cierre y zona horaria</label><input id="brief-deadline" name="briefDeadline"><p class="warning">Si una regla es ambigua, pregunta al organizador y conserva la respuesta; esta herramienta no inventa una interpretación.</p></section>
<noscript><section><h2>Matriz sin JavaScript</h2><p>Las {len(candidates)} tarjetas y sus rangos R0–R3 permanecen visibles; los filtros requieren JavaScript.</p><h2>Los nueve laboratorios, en versión de calle</h2><p>Sin JavaScript los diagramas no se mueven, pero cada laboratorio equivale a una prueba que puedes hacer con la cámara en la mano.</p><p><strong>1. Posición y focal:</strong> fotografía lo mismo desde tres distancias; después repite desde una sola posición cambiando de objetivo. Sólo la primera prueba cambia qué tapa qué.</p><p><strong>2. Verticales:</strong> haz una toma nivelada y otra inclinada. Compara cuánto se estrecha el borde superior del edificio.</p><p><strong>3. Jerarquía:</strong> recorre los cuatro bordes del visor y di en voz alta qué se mira primero, segundo y tercero.</p><p><strong>4. Vacío y bordes:</strong> repite la toma dejando más aire y comprueba que ningún contorno quede rozando el borde.</p><p><strong>5. Capas:</strong> busca una posición donde un plano cercano tape parcialmente uno lejano; con garúa el contraste hará el resto.</p><p><strong>6. Secuencia:</strong> compara postal, cambio de posición, focal desde la misma posición, presencia o ausencia y otra luz.</p><p><strong>7. Luz y material:</strong> vuelve a la misma fachada con luz lateral, con sol alto y con garúa; mide con la vista cuánto crece la sombra.</p><p><strong>8. Exposición:</strong> fija primero la obturación que congela el gesto y el diafragma que da la profundidad; deja que el ISO sea la consecuencia.</p><p><strong>9. Reflejos:</strong> rodea una fachada vidriada y anota en qué ángulo empiezas a ver el interior.</p><h2>CONTRATO vs USO</h2><p>Observa 10 minutos, escribe propósito en 8 palabras, anota 5 verbos, encuentra 3 posiciones, inspecciona bordes y elige focal al final.</p><h2>Brief</h2><p>Anota fuente, elegibilidad, tema, archivos, fechas, permisos y límites de edición antes de disparar.</p></section></noscript></main><footer>FocalRuta guarda las notas en tu navegador. La exportación JSON permite moverlas entre dispositivos.</footer><script>const PHYSICS={physics_json};
{SCRIPT}</script></body></html>'''

NAV_MARKER = '<nav aria-label="Secciones de la guía">'
COPY_SUBSTITUTIONS = (
    (">STAY<", ">ME QUEDO<"),
    (">MOVE<", ">ME MUEVO<"),
    (">RETURN OTHER LIGHT<", ">VUELVO CON OTRA LUZ<"),
    ("TOP 5 DE CAMPO", "5 PRIORIDADES PARA COMPROBAR"),
    ("OFFLINE · GUARDADO LOCAL", "GUARDADO EN ESTE DISPOSITIVO"),
    ("EDICIÓN SEGÚN EL BRIEF", "EDICIÓN SEGÚN EL ENCARGO"),
    ("DECODIFICADOR DE BRIEF", "DECODIFICADOR DEL ENCARGO"),
)
WIKI_LINK = (
    '<h3>Nueve familias técnicas</h3>'
    '<p><a href="wiki-tecnicas.html">Abrir la wiki: cada familia con su diagrama, su laboratorio y la evidencia en video'
    ' que la sostiene</a>. Si llegas con una foto que no funcionó, la wiki abre por síntoma.</p>'
)


def build_challenge_page(*values) -> str:
    """Single definition of the published page, shared with the release verifier."""
    page = render(*values).replace("Arquitectura<br>en foco", "Fotografía<br>arquitectónica")
    page = page.replace(NAV_MARKER, beginner_guide() + NAV_MARKER, 1)
    page = reorder_story(page)
    page = page.replace('<section id="learn">', '<section id="learn">' + PHYSICS_GUIDE, 1)
    page = page.replace("<h3>Nueve familias técnicas</h3>", WIKI_LINK, 1)
    for source, target in COPY_SUBSTITUTIONS:
        page = page.replace(source, target)
    return page


def main() -> None:
    values = [json.loads(path.read_text(encoding="utf-8")) for path in (RULES_PATH, LEARNING_PATH, PHOTOGRAPHERS_PATH, COHORT_PATH, CANONICAL_PATH, VERIFICATION_PATH, RANKING_PATH, ROUTES_PATH, DISCOVERIES_PATH, DISCOVERY_DOSSIERS_PATH)]
    PUBLIC_CANDIDATES_PATH.write_text(json.dumps(public_candidates(values[4], values[5]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_challenge_page(*values), encoding="utf-8")
    IPHONE_HELP.write_text(iphone_help_page(), encoding="utf-8")
    FIELD_CARD.write_text(field_card_page(), encoding="utf-8")
    ledger = json.loads(VIDEO_LEDGER_PATH.read_text(encoding="utf-8"))
    TECHNIQUE_WIKI.write_text(technique_wiki_page(values[1], ledger), encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
