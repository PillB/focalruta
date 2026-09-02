#!/usr/bin/env python3
"""Generate the dependency-free Arquitectura en Foco challenge."""
from __future__ import annotations
import json
import re
from html import escape
from pathlib import Path

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
PHYSICS_GUIDE = '<aside class="beginner-guide"><h3>Modelo físico honesto</h3><p>La posición controla la perspectiva; la focal controla el encuadre desde una posición fija. Las sombras siguen la dirección de la luz: una fuente grande produce una penumbra suave y una fuente pequeña un borde duro. Los brillos, reflejos y halos dependen de material, ángulo y exposición; aquí se muestran como señales causales: no es una simulación calibrada ni una predicción de píxeles.</p></aside>'

CSS = """:root{--ink:#10211d;--muted:#5e6d67;--paper:#f4f0e7;--card:#fffdf8;--accent:#b84c32;--green:#176b55;--line:#cbc2b2}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}a{color:inherit}header,main,footer{max-width:1040px;margin:auto;padding-inline:clamp(18px,4vw,48px)}header{padding-top:34px;padding-bottom:28px}h1{font-size:clamp(2.5rem,10vw,6rem);line-height:.88;margin:.3em 0}h2{font-size:clamp(1.7rem,5vw,3rem);line-height:1.05}.eyebrow,.status{font-size:.75rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:var(--green)}nav{position:sticky;top:0;z-index:5;display:flex;gap:6px;overflow:auto;padding:8px max(12px,env(safe-area-inset-left));background:rgba(244,240,231,.96);border-block:1px solid var(--line)}nav a{min-height:44px;display:grid;place-items:center;padding:0 13px;border-radius:999px;text-decoration:none;font-weight:750;white-space:nowrap}nav a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid var(--accent);outline-offset:2px}section{padding:34px 0;border-top:1px solid var(--line)}.command,.callout{padding:18px;border-radius:16px;background:var(--ink);color:white}.command-grid,.scenes{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}.command-grid article,.scene{padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--card)}.command-grid article{color:var(--ink)}.scene .reject{color:var(--muted);font-size:.92rem}.ranking-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px;margin-bottom:16px}.rank-number{font-size:2rem;font-weight:900;line-height:1}.rank-meta{display:flex;flex-wrap:wrap;gap:6px}.rank-meta span{padding:3px 8px;border:1px solid var(--line);border-radius:999px;font-size:.78rem}.route-preview{display:block;width:100%;height:auto;margin:12px 0;border:1px solid var(--line);border-radius:10px;background:#e9eee9}.route-preview polyline{fill:none;stroke:var(--accent);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}.route-preview circle{fill:var(--ink);stroke:white;stroke-width:2}.route-preview text{fill:white;font:bold 8px system-ui;text-anchor:middle;dominant-baseline:central}.route-note{font-size:.82rem;color:var(--muted)}.modes{columns:2;gap:30px}label{display:block;font-weight:750;margin-top:13px}input,textarea,select,button{width:100%;min-height:44px;font:inherit}textarea{min-height:82px}button{margin-top:10px;padding:9px 14px;border:0;border-radius:10px;background:var(--ink);color:white;font-weight:800}.actions{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.actions button{background:var(--green)}.secondary{background:white!important;color:var(--ink)!important;border:1px solid var(--line)!important}.rule{font-weight:800}.warning{border-left:5px solid var(--accent);padding-left:16px}footer{padding-block:30px 70px;color:var(--muted)}@media(max-width:560px){.modes{columns:1}.actions{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}"""

CSS += ":root{--sticky-nav-offset:84px}html{scroll-padding-top:var(--sticky-nav-offset)}section{scroll-margin-top:var(--sticky-nav-offset)}"
CSS += ".learning-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:14px}.lesson-card,.learning-lab,.video-transfer{padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--card)}.lesson-card details{margin-top:8px}.lesson-card summary{min-height:44px;display:flex;align-items:center;font-weight:800;cursor:pointer}.learning-lab{grid-column:span 1}.lab-frame{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#eef0e9;margin:12px 0}.lab-readout{min-height:52px;padding:10px;border-radius:10px;background:#eef6f2}.source-links{font-size:.82rem;color:var(--muted)}@media(min-width:800px){.learning-lab{grid-column:span 2}}"
CSS += "header,main,footer{max-width:1160px;padding-inline:clamp(24px,6vw,72px)}section{padding-block:42px}.beginner-guide{background:#fffaf0;border:1px solid var(--line);border-radius:18px;padding:clamp(22px,4vw,42px);margin-block:20px}.beginner-guide dl{display:grid;grid-template-columns:minmax(10rem, .35fr) 1fr;gap:12px 24px}.beginner-guide dt{font-weight:850;color:var(--green)}.beginner-guide dd{margin:0;max-width:70ch}.scene,.lesson-card,.learning-lab,.video-transfer{min-width:0;overflow-wrap:anywhere}.scene p{max-width:72ch}@media(max-width:620px){.beginner-guide dl{grid-template-columns:1fr;gap:4px}.beginner-guide dd{margin-bottom:14px}}"
CSS += ".lab-cycle{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:10px 0}.lab-cycle span,.lab-legend span{padding:6px 8px;border-radius:8px;background:#eef6f2;font-size:.78rem;font-weight:750}.lab-legend{display:flex;flex-wrap:wrap;gap:6px}.lab-reset{width:auto;min-height:44px;background:var(--card);color:var(--ink);border:2px solid var(--green)}.learning-lab:focus-within{border-color:var(--green);box-shadow:0 0 0 3px rgba(23,107,85,.16)}.lab-frame{min-height:260px}.comparison-pane{stroke:#cbc2b2;stroke-width:2;fill:#fffdf8}.state-layer{transition:opacity .18s ease}.state-layer[hidden]{display:none}@media(max-width:700px){.learning-grid{display:block}.learning-lab{margin-bottom:14px;padding:14px}.lab-frame{min-height:220px}.lab-cycle{grid-template-columns:1fr 1fr}}@media(min-width:701px) and (max-width:1000px){.learning-grid{grid-template-columns:1fr 1fr}.learning-lab{grid-column:span 2}}@media(prefers-reduced-motion:reduce){.state-layer{transition:none}}"

SCRIPT = r"""const KEY='focalruta.architecture.field.v1',form=document.querySelector('#field-form'),status=document.querySelector('#save-status'),sceneLimit=document.querySelector('#scene-limit');
const state=()=>({...Object.fromEntries(new FormData(form).entries()),sceneLimit:sceneLimit.value});function applySceneLimit(){const cards=[...document.querySelectorAll('#scene-cards .scene')],limit=sceneLimit.value==='all'?cards.length:Number(sceneLimit.value);cards.forEach((card,index)=>card.hidden=index>=limit);document.querySelector('#scene-count-status').textContent=`Mostrando ${Math.min(limit,cards.length)} de ${cards.length} escenas.`}function applyRankingView(){const scenario=document.querySelector('#ranking-scenario').value,control=document.querySelector('#ranking-limit'),cards=[...document.querySelectorAll('#ranking-cards .scene')],limit=control.value==='all'?cards.length:Number(control.value);cards.sort((a,b)=>Number(a.dataset[scenario])-Number(b.dataset[scenario])||a.dataset.name.localeCompare(b.dataset.name,'es')).forEach((card,index)=>{card.hidden=index>=limit;card.querySelector('.rank-number').textContent=`#${card.dataset[scenario]}`;card.parentNode.appendChild(card)});document.querySelector('#ranking-count-status').textContent=`Mostrando ${Math.min(limit,cards.length)} de ${cards.length} según ${scenario.toUpperCase()}.`}function applyRouteFilter(){const district=document.querySelector('#route-district').value,cards=[...document.querySelectorAll('#route-cards .scene')];cards.forEach(card=>card.hidden=district!=='all'&&card.dataset.district!==district);const visible=cards.filter(card=>!card.hidden).length;document.querySelector('#route-count-status').textContent=`Mostrando ${visible} de ${cards.length} capas.`}function save(extra={}){localStorage.setItem(KEY,JSON.stringify({...state(),...extra,updatedAt:new Date().toISOString()}));status.textContent='Notas guardadas en este dispositivo.'}function restore(data){for(const [key,value] of Object.entries(data||{})){const control=key==='sceneLimit'?sceneLimit:form.elements.namedItem(key);if(control)control.value=value}status.textContent='Notas restauradas.'}try{restore(JSON.parse(localStorage.getItem(KEY)||'{}'))}catch(error){status.textContent='No se pudieron restaurar las notas.'}applySceneLimit();applyRankingView();applyRouteFilter();sceneLimit.addEventListener('change',()=>{applySceneLimit();save()});document.querySelector('#ranking-scenario').addEventListener('change',applyRankingView);document.querySelector('#ranking-limit').addEventListener('change',applyRankingView);document.querySelector('#route-district').addEventListener('change',applyRouteFilter);form.addEventListener('input',()=>save());document.querySelectorAll('[data-decision]').forEach(button=>button.addEventListener('click',()=>save({decision:button.dataset.decision})));
document.querySelector('#export-field').addEventListener('click',()=>{const blob=new Blob([localStorage.getItem(KEY)||JSON.stringify(state())],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='focalruta-arquitectura-campo.json';a.click();URL.revokeObjectURL(a.href)});document.querySelector('#import-field').addEventListener('click',()=>document.querySelector('#import-file').click());document.querySelector('#import-file').addEventListener('change',event=>{const file=event.target.files[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{try{const data=JSON.parse(reader.result);restore(data);save(data)}catch(error){status.textContent='El archivo no contiene notas válidas.'}};reader.readAsText(file)});document.querySelector('#clear-field').addEventListener('click',()=>{localStorage.removeItem(KEY);form.reset();status.textContent='Notas borradas.'});
function updatePerspective(){const position=Number(document.querySelector('#perspective-position').value),focal=Number(document.querySelector('#perspective-focal').value),scale=focal/35,near=70*scale/position,far=70*scale/(position+4),ratio=(near/far).toFixed(2),halfFov=Math.min(58,22+focal/8);document.querySelector('#perspective-near').setAttribute('height',Math.min(100,near));document.querySelector('#perspective-near').setAttribute('y',112-Math.min(100,near));document.querySelector('#perspective-far').setAttribute('height',Math.min(100,far));document.querySelector('#perspective-far').setAttribute('y',112-Math.min(100,far));document.querySelector('#perspective-fov').setAttribute('d',`M8 112L52 ${112-halfFov}M8 112L52 ${112+halfFov}`);document.querySelector('#perspective-feedback').textContent=`Posición ${position} m · ${focal} mm. Proyección h≈f·H/z; relación cercano/lejos ${ratio}×. La focal abre o cierra el campo de visión; la distancia cambia la relación.`}
function updateVertical(){const tilt=Number(document.querySelector('#vertical-tilt').value),inset=tilt*1.4,vanishingY=Math.max(8,64-tilt*1.6);document.querySelector('#vertical-building').setAttribute('points',`${28+inset},18 ${192-inset},18 192,112 28,112`);document.querySelector('#vertical-vanishing-point').setAttribute('cy',vanishingY);document.querySelector('#vertical-feedback').textContent=tilt===0?'Cámara nivelada: horizonte y verticales paralelas en este modelo.':'Inclinación '+tilt+'°: el punto de fuga sube y las verticales convergen. Decide si expresa altura o distrae del contrato espacial.'}
function updateHierarchy(){const mode=document.querySelector('#hierarchy-mode').value,clutter=document.querySelector('#hierarchy-clutter'),person=document.querySelector('#hierarchy-person');clutter.style.opacity=mode==='clutter'?'1':'.12';person.style.opacity=mode==='human'?'1':'.18';const copy={clean:'Primera lectura: umbral y eje. Los bordes permanecen silenciosos.',clutter:'La señal brillante y las tangencias de borde compiten con el umbral.',human:'La figura gana atención; aprueba sólo si su verbo cambia el significado del umbral.'};document.querySelector('#hierarchy-feedback').textContent=copy[mode]}
function updateLight(){const mode=document.querySelector('#light-mode').value,shadow=document.querySelector('#light-shadow'),face=document.querySelector('#light-face'),direction=document.querySelector('#light-direction'),blur=document.querySelector('#light-penumbra');const states={side:{shadow:'70,90 180,112 105,112',fill:'url(#light-gradient)',opacity:'.8',blur:'1.2',x1:18,y1:24,x2:70,y2:48,copy:'Luz lateral: relieve y textura ganan separación por gradiente y sombra.'},noon:{shadow:'70,90 112,101 84,105',fill:'#e7a563',opacity:'.95',blur:'.4',x1:28,y1:10,x2:80,y2:34,copy:'Mediodía: sombra corta y dura; vigila huecos negros y altas luces.'},garua:{shadow:'70,90 95,96 80,99',fill:'#9ca9a2',opacity:'.2',blur:'4',x1:8,y1:38,x2:70,y2:54,copy:'Garúa: fuente amplia, penumbra suave; color y microtextura separan materiales.'},back:{shadow:'40,90 12,112 70,112',fill:'#364b46',opacity:'.95',blur:'1',x1:210,y1:20,x2:145,y2:48,copy:'Contraluz: la silueta domina; conserva detalle sólo si la relación lo necesita.'}}[mode];shadow.setAttribute('points',states.shadow);shadow.style.opacity=states.opacity;face.setAttribute('fill',states.fill);direction.setAttribute('x1',states.x1);direction.setAttribute('y1',states.y1);direction.setAttribute('x2',states.x2);direction.setAttribute('y2',states.y2);blur.querySelector('feGaussianBlur').setAttribute('stdDeviation',states.blur);document.querySelector('#light-feedback').textContent=states.copy}
function updateComposition(){const mode=document.querySelector('#composition-mode').value,frame=document.querySelector('#composition-frame'),copy={"default-postcard":'Postal: eje central y edificio completo; legible, pero la relación urbana todavía es genérica.',"changed-position":'Posición: el desplazamiento lateral revela umbral, profundidad y solapes nuevos.',"fixed-position-focal":'Focal a posición fija: cambia el recorte, no la perspectiva entre los planos.',"human-presence":'Presencia: el gesto solo suma si demuestra cómo se usa el espacio; compara también la ausencia.',"light-weather":'Luz y clima: otra dirección o garúa puede separar material y volumen sin cambiar la geometría.'};frame.setAttribute('data-mode',mode);document.querySelectorAll('#composition-after .state-layer').forEach(layer=>layer.style.display=layer.dataset.state===mode?'inline':'none');document.querySelector('#composition-fixed-position').style.opacity=mode==='fixed-position-focal'?'1':'0';document.querySelector('#composition-feedback').textContent=copy[mode]}
[['#perspective-position','input',updatePerspective],['#perspective-focal','change',updatePerspective],['#vertical-tilt','input',updateVertical],['#hierarchy-mode','change',updateHierarchy],['#light-mode','change',updateLight],['#composition-mode','change',updateComposition]].forEach(([selector,event,handler])=>document.querySelector(selector).addEventListener(event,handler));updatePerspective();updateVertical();updateHierarchy();updateLight();updateComposition();
const labDefaults={perspective:{'perspective-position':'4','perspective-focal':'35'},vertical:{'vertical-tilt':'0'},hierarchy:{'hierarchy-mode':'clean'},light:{'light-mode':'side'},composition:{'composition-mode':'default-postcard'}};document.querySelectorAll('.lab-reset').forEach(button=>button.addEventListener('click',()=>{Object.entries(labDefaults[button.dataset.lab]).forEach(([id,value])=>{document.getElementById(id).value=value});({perspective:updatePerspective,vertical:updateVertical,hierarchy:updateHierarchy,light:updateLight,composition:updateComposition})[button.dataset.lab]();button.closest('.learning-lab').querySelector('input,select').focus()}));
document.querySelector('#route-district').addEventListener('change',()=>{const district=document.querySelector('#route-district').value;document.querySelectorAll('#route-collections .scene').forEach(card=>{card.hidden=district!=='all'&&!card.querySelector('.eyebrow').textContent.startsWith(district+' ·')})});
"""

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
    evidence = {lab["simulation_id"]: lab for lab in learning["simulations"]}
    perspective = evidence["perspective-position"]
    vertical = evidence["vertical-convergence"]
    hierarchy = evidence["hierarchy-edges"]
    light = evidence["light-material"]
    composition = evidence["composition-sequence"]
    html = f'''
<article class="learning-lab"><p class="eyebrow">LAB 1 · PERSPECTIVA</p><h3>{escape(perspective["title"])}</h3><p>{escape(perspective["prediction_prompt"])}</p><label for="perspective-position">Distancia de cámara · m</label><input id="perspective-position" type="range" min="2" max="10" value="4"><label for="perspective-focal">Focal</label><select id="perspective-focal"><option>35</option><option>50</option><option>85</option></select><svg class="lab-frame" role="img" aria-label="Diagrama de tamaños aparentes cercano y lejano" viewBox="0 0 220 120"><rect id="perspective-near" x="58" y="42" width="45" height="70" fill="#b84c32"/><rect id="perspective-far" x="135" y="70" width="45" height="42" fill="#176b55"/><line x1="8" y1="112" x2="212" y2="112" stroke="#10211d"/><text x="80" y="16">cerca</text><text x="157" y="16">lejos</text></svg><p id="perspective-feedback" class="lab-readout" role="status"></p><p><strong>Campo:</strong> {escape(perspective["field_drill"])}</p><p class="route-note">{escape(perspective["model_limit"])}</p><p class="source-links">{source_links(perspective["sources"])}</p></article>
<article class="learning-lab"><p class="eyebrow">LAB 2 · VERTICALES</p><h3>{escape(vertical["title"])}</h3><p>{escape(vertical["prediction_prompt"])}</p><label for="vertical-tilt">Inclinación hacia arriba · grados</label><input id="vertical-tilt" type="range" min="0" max="20" value="0"><svg class="lab-frame" role="img" aria-label="Diagrama de convergencia vertical" viewBox="0 0 220 120"><polygon id="vertical-building" points="28,18 192,18 192,112 28,112" fill="#80958d" stroke="#10211d" stroke-width="3"/><line x1="82" y1="18" x2="82" y2="112" stroke="#fff"/><line x1="138" y1="18" x2="138" y2="112" stroke="#fff"/></svg><p id="vertical-feedback" class="lab-readout" role="status"></p><p><strong>Campo:</strong> {escape(vertical["field_drill"])}</p><p class="route-note">{escape(vertical["model_limit"])}</p><p class="source-links">{source_links(vertical["sources"])}</p></article>
<article class="learning-lab"><p class="eyebrow">LAB 3 · JERARQUÍA</p><h3>{escape(hierarchy["title"])}</h3><p>{escape(hierarchy["prediction_prompt"])}</p><label for="hierarchy-mode">Variante</label><select id="hierarchy-mode"><option value="clean">Eje limpio</option><option value="clutter">Bordes con competencia</option><option value="human">Acción humana</option></select><svg class="lab-frame" role="img" aria-label="Diagrama de jerarquía y bordes" viewBox="0 0 220 120"><path d="M25 112V28H195V112M70 112V58H150V112" fill="none" stroke="#10211d" stroke-width="8"/><g id="hierarchy-clutter"><rect x="3" y="8" width="54" height="22" fill="#f2cf45"/><line x1="207" y1="5" x2="170" y2="70" stroke="#b84c32" stroke-width="8"/></g><g id="hierarchy-person"><circle cx="110" cy="72" r="9" fill="#b84c32"/><line x1="110" y1="80" x2="110" y2="108" stroke="#b84c32" stroke-width="6"/></g></svg><p id="hierarchy-feedback" class="lab-readout" role="status"></p><p><strong>Campo:</strong> {escape(hierarchy["field_drill"])}</p><p class="route-note">{escape(hierarchy["model_limit"])}</p><p class="source-links">{source_links(hierarchy["sources"])}</p></article>
<article class="learning-lab"><p class="eyebrow">LAB 4 · LUZ</p><h3>{escape(light["title"])}</h3><p>{escape(light["prediction_prompt"])}</p><label for="light-mode">Condición</label><select id="light-mode"><option value="side">Lateral</option><option value="noon">Mediodía</option><option value="garua">Garúa</option><option value="back">Contraluz</option></select><svg class="lab-frame" role="img" aria-label="Diagrama de luz, volumen y sombra" viewBox="0 0 220 120"><polygon id="light-shadow" points="70,90 180,112 105,112" fill="#364b46"/><rect id="light-face" x="55" y="30" width="70" height="62" fill="#c66b3d"/><polygon points="125,30 165,48 165,92 125,92" fill="#6f4230"/></svg><p id="light-feedback" class="lab-readout" role="status"></p><p><strong>Campo:</strong> {escape(light["field_drill"])}</p><p class="route-note">{escape(light["model_limit"])}</p><p class="source-links">{source_links(light["sources"])}</p></article>
<article class="learning-lab"><p class="eyebrow">LAB 5 · SECUENCIA</p><h3>{escape(composition["title"])}</h3><p>{escape(composition["prediction_prompt"])}</p><label for="composition-mode">Decisión aislada</label><select id="composition-mode">{''.join(f'<option value="{escape(item["variant_id"])}">{escape(item["label"])}</option>' for item in composition["variants"])}</select><svg id="composition-frame" class="lab-frame" role="img" aria-label="Comparación antes y después de cinco decisiones" viewBox="0 0 440 180"><rect class="comparison-pane" x="5" y="5" width="205" height="170"/><rect class="comparison-pane" x="230" y="5" width="205" height="170"/><text x="18" y="25">ANTES</text><text x="243" y="25">DESPUÉS</text><g id="composition-before"><path d="M35 155V55H180V155M85 155V105H130V155" fill="#80958d" stroke="#10211d" stroke-width="4"/><circle cx="108" cy="116" r="8" fill="#f2cf45"/></g><g id="composition-after"><g class="state-layer" data-state="default-postcard"><path d="M260 155V55H405V155M310 155V105H355V155" fill="#80958d" stroke="#10211d" stroke-width="4"/><circle cx="333" cy="116" r="8" fill="#f2cf45"/></g><g class="state-layer" data-state="changed-position"><path d="M245 155L278 48H408V155M325 155V98H370V155" fill="#80958d" stroke="#10211d" stroke-width="4"/><path d="M278 48L245 155" stroke="#b84c32" stroke-width="6"/></g><g class="state-layer" data-state="fixed-position-focal"><path d="M235 165V35H430V165M300 165V88H365V165" fill="#80958d" stroke="#10211d" stroke-width="5"/><rect x="260" y="46" width="145" height="105" fill="none" stroke="#b84c32" stroke-width="3" stroke-dasharray="7 5"/></g><g class="state-layer" data-state="human-presence"><path d="M260 155V55H405V155M310 155V105H355V155" fill="#80958d" stroke="#10211d" stroke-width="4"/><circle cx="333" cy="105" r="10" fill="#b84c32"/><path d="M333 115v32m0-20l-18 12m18-12l18 12" stroke="#b84c32" stroke-width="6"/></g><g class="state-layer" data-state="light-weather"><path d="M260 155V55H405V155M310 155V105H355V155" fill="#7891a0" stroke="#10211d" stroke-width="4"/><path d="M235 35l75 35M248 28l75 35M365 55l60 60" stroke="#5d7f91" stroke-width="4"/><polygon points="355,155 425,120 425,155" fill="#364b46"/></g></g><g id="composition-fixed-position" opacity="0"><path d="M205 145h30" stroke="#176b55" stroke-width="4"/><circle cx="220" cy="145" r="8" fill="#176b55"/><text x="170" y="168">cámara fija</text></g></svg><p id="composition-feedback" class="lab-readout" role="status"></p><p><strong>Campo:</strong> {escape(composition["field_drill"])}</p><p class="route-note">{escape(composition["model_limit"])}</p><p class="source-links">{source_links(composition["sources"])}</p></article>'''
    labs = ("perspective", "vertical", "hierarchy", "light", "composition")
    addition = '<div class="lab-cycle"><span>Predicción</span><span>Acción</span><span>Observación</span><span>Transferencia al campo</span></div><div class="lab-legend"><span>Terracota: atención o acción</span><span>Verde: referencia</span><span>Gris: arquitectura y sombra</span></div>'
    for lab in labs:
        html = html.replace("</article>", f'{addition}<button type="button" class="lab-reset" data-lab="{lab}">Restablecer ejemplo</button></article>', 1)
    html = html.replace('<rect id="perspective-near"', '<path id="perspective-fov" d="M8 112L52 80M8 112L52 144" fill="none" stroke="#176b55" stroke-width="2"/><rect id="perspective-near"', 1)
    html = html.replace('<svg class="lab-frame" role="img" aria-label="Diagrama de tamaños aparentes cercano y lejano"', '<svg class="lab-frame" data-physics-model="pinhole-projection" role="img" aria-label="Diagrama de proyección estenopeica: tamaños aparentes, cámara y campo de visión"', 1)
    html = html.replace('<line x1="8" y1="112" x2="212" y2="112" stroke="#10211d"/><text x="80" y="16">cerca</text>', '<line x1="8" y1="112" x2="212" y2="112" stroke="#10211d"/><path d="M8 112L48 92M8 112L48 132" stroke="#176b55" stroke-width="2"/><circle cx="8" cy="112" r="4" fill="#b84c32"/><text x="80" y="16">cerca</text>', 1)
    html = html.replace('<svg class="lab-frame" role="img" aria-label="Diagrama de convergencia vertical"', '<svg class="lab-frame" data-physics-model="vanishing-point" role="img" aria-label="Diagrama de punto de fuga, horizonte y convergencia vertical"', 1)
    html = html.replace('<line x1="82" y1="18" x2="82" y2="112" stroke="#fff"/><line x1="138" y1="18" x2="138" y2="112" stroke="#fff"/>', '<line id="vertical-horizon" x1="8" y1="64" x2="212" y2="64" stroke="#b84c32" stroke-dasharray="5 4"/><circle id="vertical-vanishing-point" cx="110" cy="64" r="4" fill="#b84c32"/><line x1="82" y1="18" x2="82" y2="112" stroke="#fff"/><line x1="138" y1="18" x2="138" y2="112" stroke="#fff"/>', 1)
    html = html.replace('<svg class="lab-frame" role="img" aria-label="Diagrama de jerarquía y bordes"', '<svg class="lab-frame" data-physics-model="layered-attention" role="img" aria-label="Diagrama de jerarquía por capas, orden de lectura y competencia de bordes"', 1)
    html = html.replace('<path d="M25 112V28H195V112M70 112V58H150V112"', '<g id="hierarchy-reading-order"><circle cx="88" cy="40" r="11" fill="#176b55"/><text x="88" y="44" fill="white" text-anchor="middle">1</text><circle cx="165" cy="45" r="11" fill="#80958d"/><text x="165" y="49" fill="white" text-anchor="middle">2</text><circle cx="110" cy="94" r="11" fill="#b84c32"/><text x="110" y="98" fill="white" text-anchor="middle">3</text></g><path d="M25 112V28H195V112M70 112V58H150V112"', 1)
    html = html.replace('<svg class="lab-frame" role="img" aria-label="Diagrama de luz, volumen y sombra"', '<svg class="lab-frame" data-physics-model="lambert-shadow" role="img" aria-label="Diagrama de luz direccional, caras iluminadas, sombra y penumbra"', 1)
    html = html.replace('<polygon id="light-shadow"', '<defs><linearGradient id="light-gradient" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7d47a"/><stop offset="1" stop-color="#c66b3d"/></linearGradient><filter id="light-penumbra" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter></defs><line id="light-direction" x1="18" y1="24" x2="70" y2="48" stroke="#f2cf45" stroke-width="5"/><polygon id="light-shadow"', 1)
    html = html.replace('<rect id="light-face" x="55" y="30" width="70" height="62" fill="#c66b3d"/>', '<rect id="light-face" x="55" y="30" width="70" height="62" fill="url(#light-gradient)"/>', 1)
    html = html.replace('fill="#364b46"/><rect id="light-face"', 'fill="#364b46" filter="url(#light-penumbra)"/><rect id="light-face"', 1)
    return html

def iphone_help_page() -> str:
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Mapas en iPhone · FocalRuta</title><style>{CSS}</style></head><body><header><p class="eyebrow">ELI5</p><h1>Abre tu ruta en iPhone 13 Pro</h1></header><main>
<section><h2>La forma fácil</h2><ol><li>Abre la guía de fotografía arquitectónica en Safari.</li><li>Busca tu distrito y toca <strong>Abrir tramo caminando</strong>.</li><li>Si tienes Google Maps, el enlace lo abre; si no, se abre en Safari.</li><li>Revisa cruces, cierres y veredas en pantalla antes de empezar. Pulsa Iniciar solo cuando estés en la primera parada.</li><li>Al terminar el tramo, vuelve a FocalRuta y abre el siguiente.</li></ol><p class="warning">Cada tramo tiene como máximo cinco paradas porque el navegador móvil admite hasta tres puntos intermedios.</p></section>
<section><h2>Si el enlace no abre</h2><ol><li>Comprueba que tienes conexión a internet.</li><li>Vuelve a FocalRuta, mantén pulsado <strong>Abrir tramo caminando</strong> y elige <strong>Abrir en una pestaña nueva</strong>.</li><li>Si Safari muestra la ruta, toca <strong>Abrir en la app</strong>. Si Google Maps no está instalado, continúa en el navegador.</li><li>Si sigue fallando, descarga el GeoJSON o KML en <strong>Archivos</strong> y conserva la lista de paradas; no pulses repetidamente un enlace que permanece bloqueado.</li></ol></section>
<section><h2>Si quieres ver capas KML</h2><ol><li>En una computadora abre Google My Maps e importa el KML del distrito. Incluye los puntos y la línea peatonal capturada.</li><li>Guarda el mapa en la misma cuenta de Google.</li><li>En tu iPhone abre Google Maps.</li><li>Toca <strong>You</strong>, luego <strong>Maps</strong>, y elige el mapa.</li></ol><p>El KML se puede guardar en Archivos, pero no se importa directamente a My Maps desde iPhone/iPad. Por eso FocalRuta usa enlaces de ruta directos como flujo principal.</p></section>
<p><a href="index.html">Volver a fotografía arquitectónica</a></p></main></body></html>'''

def field_card_page() -> str:
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tarjeta de campo · Fotografía arquitectónica</title><style>{CSS}</style></head><body><header><p class="eyebrow">TARJETA DESCARGABLE</p><h1>Protocolo de fotografía arquitectónica</h1><p>Guárdala en Archivos para trabajar sin conexión.</p></header><main><section><h2>Antes de salir</h2><ol><li>Elige una colección del distrito y descarga su mapa HTML, KML o GeoJSON.</li><li>Confirma acceso, luz y cierres en el momento; las rutas son capturas, no navegación en vivo.</li><li>Define una hipótesis: posición primero, focal después; protege altas luces.</li></ol></section><section><h2>En cada parada</h2><ol><li>Haz una toma de contexto y una de detalle.</li><li>Repite desde dos posiciones: cambia perspectiva, no solo focal.</li><li>Comprueba verticales, bordes, figura-fondo y gesto humano.</li><li>Anota qué cambió y qué evidencia lo demuestra.</li></ol></section><section><h2>Salida segura</h2><p>No unas puntos independientes como caminata. Si una transferencia supera el umbral publicado, usa Google Maps para recalcularla con conexión.</p><p><a href="index.html">Volver a la guía</a></p></section></main></body></html>'''

def technique_wiki_page(learning: dict, ledger: dict) -> str:
    cards = []
    for index, card in enumerate(learning["technique_cards"], 1):
        diagram = f'<svg class="lab-frame" role="img" aria-label="Diagrama causal de {escape(card["title"])}" viewBox="0 0 360 150"><rect x="18" y="38" width="92" height="76" rx="8" fill="#80958d"/><circle cx="290" cy="76" r="24" fill="#f2cf45"/><path d="M120 76H252" stroke="#b84c32" stroke-width="5"/><path d="M242 66l14 10-14 10" fill="none" stroke="#b84c32" stroke-width="5"/><text x="18" y="132">decisión</text><text x="258" y="132">lectura</text></svg>'
        cards.append(f'<article class="wiki-technique"><p class="eyebrow">TÉCNICA {index}</p><h2>{escape(card["title"])}</h2><p>{escape(card["mechanism"])}</p>{diagram}<p><strong>Qué probar:</strong> {escape(card["field_test"])}</p><p><strong>Qué observar:</strong> {escape(card["diagnosis"])}</p><p><strong>Cuándo descartarlo:</strong> {escape(card["misconception_warning"])}</p><p class="route-note">Síntesis causal: no predice píxeles ni sustituye la prueba de campo.</p></article>')
    evidence = []
    unavailable = sum(video["transcript_status"] != "CAPTURED" for video in ledger["videos"])
    for video in ledger["videos"]:
        title = video.get("exact_title") or video.get("working_title") or f'Video {video["video_id"]}'
        for claim in video["timestamped_claims"]:
            seconds = int(claim["timestamp_seconds"])
            url = f'https://www.youtube.com/watch?v={video["video_id"]}&t={seconds}s'
            evidence.append(f'<article class="evidence-card"><h3>{escape(title)}</h3><p>{escape(claim["claim"])}</p><p><a href="{escape(url)}">Ver evidencia desde {seconds} s</a></p><span class="status">Afirmación validada contra subtítulos</span></article>')
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wiki de técnicas · FocalRuta</title><style>{CSS}.wiki-technique,.evidence-card{{padding:18px;border:1px solid var(--line);border-radius:14px;background:var(--card);margin-block:14px}}</style></head><body><header><p class="eyebrow">WIKI · APRENDIZAJE CON PROCEDENCIA</p><h1>Técnicas de fotografía arquitectónica</h1><p>Manual derivado del ledger, las transcripciones verificadas y la investigación técnica relacionada.</p></header><nav aria-label="Wiki"><a href="index.html#learn">Volver a aprender</a><a href="#tecnicas">Técnicas</a><a href="#evidencia">Evidencia</a></nav><main><section id="tecnicas"><h2>De la idea a una prueba visible</h2><p>Los dibujos son síntesis pedagógicas originales, no fotogramas copiados.</p>{''.join(cards)}</section><section id="evidencia"><h2>Índice de evidencia en video</h2><p>{len(evidence)} afirmaciones con marca temporal. {unavailable} videos figuran como <strong>Transcripción no disponible</strong> y no aportan enseñanzas atribuidas.</p><div class="scenes">{''.join(evidence)}</div></section></main><footer>El ledger conserva título, canal, fecha, procedencia y estado de validación.</footer></body></html>'''

def beginner_guide() -> str:
    return '''<section id="how-to-read" class="beginner-guide"><p class="eyebrow">PARA EMPEZAR · SIN CONOCIMIENTOS PREVIOS</p><h2>Cómo usar esta guía</h2><p>Esta página es una compañera de salida, no un examen. Lee una sección, prueba una decisión pequeña y anota qué cambió. Si una palabra es nueva, aquí tienes el mapa:</p><dl><dt>Matriz de preparación</dt><dd>Compara lugares con cuatro preguntas de práctica. R0 es una mirada equilibrada; R1 busca evitar la postal; R2 pregunta cómo vive la gente el lugar; R3 prioriza forma y luz. Los números son prioridades de entrenamiento, no una nota ni una predicción de concurso.</dd><dt>Tarjeta de lugar</dt><dd>Cuenta qué se puede observar, desde dónde probarlo, qué evidencia falta y qué haría fallar la foto. “Campo” significa que todavía debes comprobarlo personalmente.</dd><dt>Laboratorio</dt><dd>Es un dibujo interactivo. Primero predice, luego mueve un control, mira el cambio y repite la idea con tu cámara. El dibujo enseña una relación; no promete el resultado exacto de un lente.</dd><dt>Ruta y colección</dt><dd>Una colección agrupa tramos caminables del mismo distrito. Una parada independiente no es un tour: llega a ella por separado. Las distancias son capturas verificadas, no tráfico en vivo.</dd><dt>Brief</dt><dd>Escribe qué pide realmente tu encargo o convocatoria antes de disparar: tema, entrega, fecha, acceso y límites de edición.</dd></dl><p><strong>Orden recomendado:</strong> empieza por una tarjeta, practica un laboratorio, elige una colección y termina con la tarjeta descargable de campo.</p></section>'''

def reorder_story(page: str) -> str:
    """Put learning before evaluation while retaining stable anchor IDs."""
    pattern = re.compile(r'<section id="([^"]+)".*?</section>', re.DOTALL)
    sections = {match.group(1): match.group(0) for match in pattern.finditer(page)}
    order = ("learn", "style-radar", "scenes", "ranking", "field-priorities", "route", "field-run", "ai-firewall", "rules")
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
    lessons_html = lesson_cards(learning)
    videos_html = video_transfer_cards(learning)
    labs_html = learning_labs(learning)
    techniques_html = technique_cards(learning)
    jurors = " · ".join(escape(name) for name in rules["jurors"])
    routed_stops = sum(len(layer["stops"]) for layer in routes["district_layers"])
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#10211d"><link rel="icon" href="../../assets/app-icon.svg" type="image/svg+xml"><title>Fotografía arquitectónica · FocalRuta</title><style>{CSS}</style></head><body>
<header id="today"><p class="eyebrow">FOCALRUTA · LABORATORIO DE CAMPO</p><h1>Arquitectura<br>en foco</h1><p>Aprende a convertir forma, luz, uso y tiempo en una fotografía que se sostenga antes de la explicación.</p><div class="command"><div class="command-grid"><article><strong>Practica</strong><p>Tres posiciones antes de elegir focal.</p></article><article><strong>Explora</strong><p>{len(candidates)} lugares y escenas; {visual_started} tienen forénsica visual y {desk_verified} dossier de escritorio verificado.</p></article><article><strong>Decide</strong><p>CONTRATO vs USO y una prueba A/B/C/D/E.</p></article><article><strong>Adapta</strong><p>Decodifica cada brief antes de capturar o editar.</p></article></div></div></header>
<nav aria-label="Tareas del laboratorio"><a href="../../index.html">FocalRuta</a><a href="#today">Inicio</a><a href="#ranking">Preparación</a><a href="#route">Ruta</a><a href="#scenes">Escenas</a><a href="#learn">Aprender</a><a href="#field-run">Campo</a><a href="#rules">Brief</a></nav><main>
<section id="ranking"><p class="eyebrow">MATRIZ DE PREPARACIÓN · NO ES PRONÓSTICO</p><h2>Compara fortalezas y fragilidades</h2><p>R0–R3 son lentes de práctica —balance, anti-postal, habitar y forma/campo—, no criterios oficiales ni estimaciones de resultados. La dispersión muestra sensibilidad a prioridades distintas y Pareto identifica escenas con compromisos útiles.</p><div class="ranking-controls"><div><label for="ranking-scenario">Lente de práctica</label><select id="ranking-scenario"><option value="r0">R0 · balanceado</option><option value="r1">R1 · anti-postal</option><option value="r2">R2 · habitar</option><option value="r3">R3 · forma/campo</option></select></div><div><label for="ranking-limit">Mostrar N o todas</label><select id="ranking-limit"><option value="5">5</option><option value="15" selected>15</option><option value="40">40</option><option value="all">Todas</option></select></div></div><p id="ranking-count-status" role="status" aria-live="polite"></p><div class="scenes" id="ranking-cards">{ranking_cards(ranking)}</div></section>
<section id="field-priorities"><p class="eyebrow">TOP 5 DE CAMPO</p><h2>Valor fotográfico que también se puede intentar</h2><p>Este orden combina potencial, causalidad, evidencia, acceso y factibilidad. Consulta abajo qué escenas ya tienen evidencia peatonal; una escena sin ruta todavía exige verificación manual.</p><div class="scenes">{field_priority_cards(ranking)}</div></section>
<section id="route"><p class="eyebrow">RUTAS PEATONALES · AUDITORÍA DE GEOMETRÍA</p><h2>Colecciones de ruta por distrito</h2><p>Una colección reúne segmentos realmente caminables y declara aparte los puntos que requieren traslado. No se presenta un pin aislado como si fuera un tour. Cada parada incluye dirección breve y latitud/longitud; el mapa HTML funciona offline y Google Maps ofrece una recalculación vigente cuando hay conexión.</p><p class="warning"><strong>{len(routes.get("omitted_intertour_transfers", []))} traslados omitidos:</strong> superaban el umbral operativo y no se presentan como caminata continua.</p><label for="route-district">Filtrar distrito</label><select id="route-district"><option value="all">Todos</option>{route_district_options(routes)}</select><p id="route-count-status" role="status" aria-live="polite"></p><p><a href="iphone-maps.html">Cómo abrirlo en iPhone 13 Pro, paso a paso</a> · <a href="field-card.html" download>Descargar tarjeta de campo</a></p><div class="scenes" id="route-collections">{route_collection_cards(routes)}</div><h3>Detalle de segmentos y puntos</h3><div class="scenes" id="route-cards">{route_cards(routes)}</div></section>
<section id="style-radar"><p class="eyebrow">RADAR · MODERNO / ART NOUVEAU / GEOMETRÍA</p><h2>Nuevos edificios que se ganaron una comparación</h2><p><strong>6/6 dossiers incorporados al ranking y a capas peatonales distritales verificadas.</strong> Cada hallazgo tiene diez pases, A/B/C/D/E, tres preguntas y forénsica multiángulo. Confirma acceso el mismo día antes de salir.</p><div class="scenes">{discovery_cards(discoveries, discovery_dossiers)}</div></section>
<section id="scenes"><p class="eyebrow">UNIVERSO CANÓNICO</p><h2>Todos los lugares y escenas</h2><p>Las {len(candidates)} identidades reconciliadas tienen el mismo contrato de fuentes, imágenes, composición, preguntas, diez pases y A/B/C/D/E. El ranking de escritorio ya puede compararlas; ninguna queda habilitada como ruta hasta verificar ventanas y acceso en campo.</p><label for="scene-limit">Mostrar N escenas</label><select id="scene-limit"><option value="10">10 escenas</option><option value="25">25 escenas</option><option value="40">40 escenas</option><option value="all" selected>Todas las escenas</option></select><p id="scene-count-status" role="status" aria-live="polite">Mostrando todas las escenas.</p><div class="scenes" id="scene-cards">{scene_cards(candidates, cohort, verification)}</div></section>
<section id="learn"><p class="eyebrow">VER → POSICIONAR → COMPONER → ILUMINAR → TRABAJAR → TERMINAR → COMPETIR</p><h2>Aprende antes de perseguir una locación</h2><p>Estos diagramas responden a decisiones de campo y dan feedback inmediato. <strong>No es una simulación óptica ni una previsualización de píxeles:</strong> cada lab aísla una relación para que puedas reconocerla después con la cámara.</p><p>{escape(learning["pedagogy"]["evidence"])}</p><div class="learning-grid">{labs_html}</div><h3>Nueve familias técnicas</h3><div class="scenes">{techniques_html}</div><h3>17 ciclos de campo</h3><div class="learning-grid">{lessons_html}</div><h3>Videos convertidos en decisiones</h3><p>Los enlaces abren el momento exacto; el aprendizaje esencial permanece aquí y funciona offline.</p><div class="learning-grid">{videos_html}</div><h3>Seis modos de ver</h3><ol class="modes">{modes}</ol><h3>Preguntas de maestros</h3><div class="scenes">{masters}</div></section>
<section id="field-run"><p class="eyebrow">OFFLINE · GUARDADO LOCAL</p><h2>CONTRATO vs USO</h2><p>Observa diez minutos. Resume el propósito original, registra cinco verbos, encuentra tres posiciones y elige focal al final.</p><form id="field-form"><label for="field-scene">Escena</label><select id="field-scene" name="scene">{options}</select><label for="contract">Propósito original · 8 palabras</label><input id="contract" name="contract" maxlength="90"><label for="verbs">Cinco verbos observados</label><textarea id="verbs" name="verbs"></textarea><label for="device">Dispositivo arquitectónico que causa la acción</label><textarea id="device" name="device"></textarea><label for="failure">Por qué todavía falla la mejor toma</label><textarea id="failure" name="failure"></textarea><div class="actions" role="group" aria-label="Decisión de campo"><button type="button" data-decision="STAY">STAY</button><button type="button" data-decision="MOVE">MOVE</button><button type="button" data-decision="RETURN_OTHER_LIGHT">RETURN OTHER LIGHT</button></div><p id="save-status" role="status" aria-live="polite">Se guarda solo en este dispositivo.</p></form><div class="actions"><button id="export-field" type="button" class="secondary">Exportar notas</button><button id="import-field" type="button" class="secondary">Importar notas</button><button id="clear-field" type="button" class="secondary">Borrar notas</button></div><input id="import-file" type="file" accept="application/json" hidden></section>
<section id="ai-firewall"><p class="eyebrow">EDICIÓN SEGÚN EL BRIEF</p><h2>Separa captura, revelado, composición y generación</h2><p>Una operación aceptable en un encargo puede descalificar otro. No uses eliminación, montaje o generación hasta confirmar la regla vigente.</p></section><section id="rules" class="architecture-preflight"><p class="eyebrow">DECODIFICADOR DE BRIEF · OFFLINE</p><h2>Convierte reglas nuevas en decisiones de campo</h2><p>No conserva reglas de una convocatoria vencida. Antes de participar, copia desde la fuente oficial: elegibilidad, tema, originalidad, cantidad y formato de archivos, fechas y zona horaria, permisos, límites de edición/IA, acceso y canal de entrega.</p><label for="brief-source">Fuente oficial y fecha de consulta</label><input id="brief-source" name="briefSource"><label for="brief-theme">Tema y qué debe ser visible sin texto</label><textarea id="brief-theme" name="briefTheme"></textarea><label for="brief-files">Cantidad, formato, tamaño y nombre</label><textarea id="brief-files" name="briefFiles"></textarea><label for="brief-editing">Edición, composición, eliminación e IA</label><textarea id="brief-editing" name="briefEditing"></textarea><label for="brief-rights">Elegibilidad, acceso, permisos y releases</label><textarea id="brief-rights" name="briefRights"></textarea><label for="brief-deadline">Cierre y zona horaria</label><input id="brief-deadline" name="briefDeadline"><p class="warning">Si una regla es ambigua, pregunta al organizador y conserva la respuesta; esta herramienta no inventa una interpretación.</p></section>
<noscript><section><h2>Matriz sin JavaScript</h2><p>Las {len(candidates)} tarjetas y sus rangos R0–R3 permanecen visibles; los filtros requieren JavaScript.</p><h2>Laboratorios sin JavaScript</h2><p><strong>Perspectiva:</strong> Mueve físicamente la cámara entre tres posiciones antes de cambiar focal.</p><p><strong>Verticales:</strong> Mantén la cámara nivelada y compara con una toma inclinada.</p><p><strong>Jerarquía:</strong> Escanea los cuatro bordes y nombra primera, segunda y tercera lectura.</p><p><strong>Luz:</strong> vuelve a la misma superficie con luz lateral, mediodía y garúa.</p><p><strong>Secuencia:</strong> compara postal, posición, focal fija, presencia o ausencia y otra luz.</p><h2>CONTRATO vs USO</h2><p>Observa 10 minutos, escribe propósito en 8 palabras, anota 5 verbos, encuentra 3 posiciones, inspecciona bordes y elige focal al final.</p><h2>Brief</h2><p>Anota fuente, elegibilidad, tema, archivos, fechas, permisos y límites de edición antes de disparar.</p></section></noscript></main><footer>FocalRuta guarda las notas en tu navegador. La exportación JSON permite moverlas entre dispositivos.</footer><script>{SCRIPT}</script></body></html>'''

def main() -> None:
    values = [json.loads(path.read_text(encoding="utf-8")) for path in (RULES_PATH, LEARNING_PATH, PHOTOGRAPHERS_PATH, COHORT_PATH, CANONICAL_PATH, VERIFICATION_PATH, RANKING_PATH, ROUTES_PATH, DISCOVERIES_PATH, DISCOVERY_DOSSIERS_PATH)]
    PUBLIC_CANDIDATES_PATH.write_text(json.dumps(public_candidates(values[4], values[5]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    page = render(*values).replace("Arquitectura<br>en foco", "Fotografía<br>arquitectónica")
    page = page.replace('<nav aria-label="Tareas del laboratorio">', beginner_guide() + '<nav aria-label="Tareas del laboratorio">', 1)
    page = reorder_story(page)
    page = page.replace('<section id="learn">', '<section id="learn">' + PHYSICS_GUIDE, 1)
    page = page.replace("<h3>Nueve familias técnicas</h3>", '<h3>Nueve familias técnicas</h3><p><a href="wiki-tecnicas.html">Abrir la wiki completa de técnicas, diagramas y evidencia de videos</a></p>', 1)
    for source, target in ((">STAY<", ">ME QUEDO<"), (">MOVE<", ">ME MUEVO<"), (">RETURN OTHER LIGHT<", ">VUELVO CON OTRA LUZ<"), ("TOP 5 DE CAMPO", "5 PRIORIDADES PARA COMPROBAR"), ("OFFLINE · GUARDADO LOCAL", "GUARDADO EN ESTE DISPOSITIVO"), ("EDICIÓN SEGÚN EL BRIEF", "EDICIÓN SEGÚN EL ENCARGO"), ("DECODIFICADOR DE BRIEF", "DECODIFICADOR DEL ENCARGO")):
        page = page.replace(source, target)
    OUTPUT.write_text(page, encoding="utf-8")
    IPHONE_HELP.write_text(iphone_help_page(), encoding="utf-8")
    FIELD_CARD.write_text(field_card_page(), encoding="utf-8")
    ledger = json.loads(VIDEO_LEDGER_PATH.read_text(encoding="utf-8"))
    TECHNIQUE_WIKI.write_text(technique_wiki_page(values[1], ledger), encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))

if __name__ == "__main__":
    main()
