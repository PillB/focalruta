#!/usr/bin/env python3
"""Generate the dependency-free Arquitectura en Foco challenge."""
from __future__ import annotations
import json
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
OUTPUT = ROOT / "challenges/arquitectura-en-foco/index.html"

CSS = """:root{--ink:#10211d;--muted:#5e6d67;--paper:#f4f0e7;--card:#fffdf8;--accent:#b84c32;--green:#176b55;--line:#cbc2b2}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}a{color:inherit}header,main,footer{max-width:1040px;margin:auto;padding-inline:clamp(18px,4vw,48px)}header{padding-top:34px;padding-bottom:28px}h1{font-size:clamp(2.5rem,10vw,6rem);line-height:.88;margin:.3em 0}h2{font-size:clamp(1.7rem,5vw,3rem);line-height:1.05}.eyebrow,.status{font-size:.75rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:var(--green)}nav{position:sticky;top:0;z-index:5;display:flex;gap:6px;overflow:auto;padding:8px max(12px,env(safe-area-inset-left));background:rgba(244,240,231,.96);border-block:1px solid var(--line)}nav a{min-height:44px;display:grid;place-items:center;padding:0 13px;border-radius:999px;text-decoration:none;font-weight:750;white-space:nowrap}nav a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid var(--accent);outline-offset:2px}section{padding:34px 0;border-top:1px solid var(--line)}.command,.callout{padding:18px;border-radius:16px;background:var(--ink);color:white}.command-grid,.scenes{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}.command-grid article,.scene{padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--card)}.command-grid article{color:var(--ink)}.scene .reject{color:var(--muted);font-size:.92rem}.ranking-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px;margin-bottom:16px}.rank-number{font-size:2rem;font-weight:900;line-height:1}.rank-meta{display:flex;flex-wrap:wrap;gap:6px}.rank-meta span{padding:3px 8px;border:1px solid var(--line);border-radius:999px;font-size:.78rem}.modes{columns:2;gap:30px}label{display:block;font-weight:750;margin-top:13px}input,textarea,select,button{width:100%;min-height:44px;font:inherit}textarea{min-height:82px}button{margin-top:10px;padding:9px 14px;border:0;border-radius:10px;background:var(--ink);color:white;font-weight:800}.actions{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.actions button{background:var(--green)}.secondary{background:white!important;color:var(--ink)!important;border:1px solid var(--line)!important}.rule{font-weight:800}.warning{border-left:5px solid var(--accent);padding-left:16px}footer{padding-block:30px 70px;color:var(--muted)}@media(max-width:560px){.modes{columns:1}.actions{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}"""

SCRIPT = r"""const KEY='focalruta.architecture.field.v1',form=document.querySelector('#field-form'),status=document.querySelector('#save-status'),sceneLimit=document.querySelector('#scene-limit');
const state=()=>({...Object.fromEntries(new FormData(form).entries()),sceneLimit:sceneLimit.value});function applySceneLimit(){const cards=[...document.querySelectorAll('#scene-cards .scene')],limit=sceneLimit.value==='all'?cards.length:Number(sceneLimit.value);cards.forEach((card,index)=>card.hidden=index>=limit);document.querySelector('#scene-count-status').textContent=`Mostrando ${Math.min(limit,cards.length)} de ${cards.length} escenas.`}function applyRankingView(){const scenario=document.querySelector('#ranking-scenario').value,control=document.querySelector('#ranking-limit'),cards=[...document.querySelectorAll('#ranking-cards .scene')],limit=control.value==='all'?cards.length:Number(control.value);cards.sort((a,b)=>Number(a.dataset[scenario])-Number(b.dataset[scenario])||a.dataset.name.localeCompare(b.dataset.name,'es')).forEach((card,index)=>{card.hidden=index>=limit;card.querySelector('.rank-number').textContent=`#${card.dataset[scenario]}`;card.parentNode.appendChild(card)});document.querySelector('#ranking-count-status').textContent=`Mostrando ${Math.min(limit,cards.length)} de ${cards.length} según ${scenario.toUpperCase()}.`}function save(extra={}){localStorage.setItem(KEY,JSON.stringify({...state(),...extra,updatedAt:new Date().toISOString()}));status.textContent='Notas guardadas en este dispositivo.'}function restore(data){for(const [key,value] of Object.entries(data||{})){const control=key==='sceneLimit'?sceneLimit:form.elements.namedItem(key);if(control)control.value=value}status.textContent='Notas restauradas.'}try{restore(JSON.parse(localStorage.getItem(KEY)||'{}'))}catch(error){status.textContent='No se pudieron restaurar las notas.'}applySceneLimit();applyRankingView();sceneLimit.addEventListener('change',()=>{applySceneLimit();save()});document.querySelector('#ranking-scenario').addEventListener('change',applyRankingView);document.querySelector('#ranking-limit').addEventListener('change',applyRankingView);form.addEventListener('input',()=>save());document.querySelectorAll('[data-decision]').forEach(button=>button.addEventListener('click',()=>save({decision:button.dataset.decision})));
document.querySelector('#export-field').addEventListener('click',()=>{const blob=new Blob([localStorage.getItem(KEY)||JSON.stringify(state())],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='focalruta-arquitectura-campo.json';a.click();URL.revokeObjectURL(a.href)});document.querySelector('#import-field').addEventListener('click',()=>document.querySelector('#import-file').click());document.querySelector('#import-file').addEventListener('change',event=>{const file=event.target.files[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{try{const data=JSON.parse(reader.result);restore(data);save(data)}catch(error){status.textContent='El archivo no contiene notas válidas.'}};reader.readAsText(file)});document.querySelector('#clear-field').addEventListener('click',()=>{localStorage.removeItem(KEY);form.reset();status.textContent='Notas borradas.'});
const fileInput=document.querySelector('#candidate'),year=document.querySelector('#year'),result=document.querySelector('#result');document.querySelector('#check').addEventListener('click',()=>{const files=[...fileInput.files],errors=[];if(files.length!==1)errors.push('Selecciona exactamente un archivo.');if(files.length===1){const f=files[0],stem=f.name.replace(/\.[^.]+$/,'');if(!/\.jpe?g$/i.test(f.name))errors.push('Debe ser JPG o JPEG.');if(f.size<5000000||f.size>25000000)errors.push('Debe pesar entre 5 y 25 MB.');if(!/^[^\W\d_]+(?:-[^\W\d_]+)+$/u.test(stem))errors.push('Usa nombre-apellido.')}if(Number(year.value)<2020)errors.push('La captura debe ser de 2020 o posterior.');result.textContent=errors.length?errors.join(' '):'Pasa las comprobaciones automáticas.'});"""

def scene_cards(candidates: list[dict], cohort: dict, verification: dict) -> str:
    active = {item["canonical_id"]: item for item in cohort["candidates"]}
    progress = {item["canonical_id"]: item for item in verification["records"]}
    cards = []
    for candidate in candidates:
        verified = active.get(candidate["canonical_id"])
        mechanism = verified["primary_scene_mechanism"].replace("_", " ").title() if verified else "Mecanismo visual por investigar"
        rejection = verified["expert_rejection"] if verified else "Faltan fuentes actuales, forénsica visual, diez pases y pruebas A/B/C/D/E."
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
            f'<p><strong>Sobrevive porque:</strong> {escape(item["why_survives"])}</p><p><strong>Necesita:</strong> {escape(item["required_scene"])} · {escape(item["exact_view"])} · {escape(item["exact_light"])}</p><p class="reject"><strong>Contraargumento:</strong> {escape(item["strongest_counterargument"])}</p><p class="reject"><strong>Kill:</strong> {escape(item["field_failure"])}</p>'
            f'<p class="status">p50 {item["rank_distribution"]["p50"]} · p10–p90 {item["rank_distribution"]["p10"]}–{item["rank_distribution"]["p90"]} · confianza {round(item["evidence_confidence"] * 100)}%</p></article>'
        )
    return "".join(cards)

def field_priority_cards(ranking: dict) -> str:
    return "".join(
        f'<article class="scene"><div class="rank-number">#{item["field_rank"]}</div><p class="eyebrow">CAMPO · {escape(item["district"])}</p><h3>{escape(item["name"])}</h3><p>{escape(item["why_go_now"])}</p><p><strong>Prueba:</strong> {escape(item["required_scene"])}</p><p><strong>Fallback:</strong> {escape(item["fallback"])}</p><p class="status">confianza {round(item["field_confidence"] * 100)}% · encaje de ruta pendiente</p></article>'
        for item in ranking["top_5_field"]
    )

def render(rules: dict, learning: dict, photographers: dict, cohort: dict | None = None, candidates: list[dict] | None = None, verification: dict | None = None, ranking: dict | None = None) -> str:
    cohort = cohort or json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    candidates = candidates or json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))
    verification = verification or json.loads(VERIFICATION_PATH.read_text(encoding="utf-8"))
    ranking = ranking or json.loads(RANKING_PATH.read_text(encoding="utf-8"))
    visual_started = sum(bool(item["visual_reference_families"]) for item in verification["records"])
    desk_verified = sum(item["verification_complete"] for item in verification["records"])
    options = "".join(f'<option value="{escape(s["canonical_id"])}">{escape(s["name"])}</option>' for s in candidates)
    modes = "".join(f"<li>{escape(mode)}</li>" for mode in photographers["seeing_modes"])
    masters = "".join(
        f'<article class="scene"><h3>{escape(card["photographer"])}</h3><p>{escape(card["signature_question"])}</p>'
        f'<p><strong>Prueba:</strong> {escape(card["field_drill"])}</p></article>'
        for card in photographers["transfer_cards"]
    )
    lesson = learning["lessons"][1]
    jurors = " · ".join(escape(name) for name in rules["jurors"])
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#10211d"><link rel="icon" href="../../assets/app-icon.svg" type="image/svg+xml"><title>Arquitectura en Foco · FocalRuta</title><style>{CSS}</style></head><body>
<header id="today"><p class="eyebrow">FOCALRUTA · CHALLENGE 2026</p><h1>Arquitectura<br>en foco</h1><p>Una sola fotografía. Encuentra una relación entre diseño, vida cotidiana y ciudad que se lea antes de la explicación.</p><div class="command"><div class="command-grid"><article><strong>Practica</strong><p>Tres posiciones antes de elegir focal.</p></article><article><strong>Explora</strong><p>81 lugares y escenas; {visual_started} tienen forénsica visual y {desk_verified} dossier de escritorio verificado. Compáralos bajo cuatro escenarios internos.</p></article><article><strong>Decide</strong><p>CONTRATO vs USO y una prueba A/B/C/D/E.</p></article><article><strong>No olvides</strong><p>Un JPG/JPEG de 5–25 MB.</p></article></div></div></header>
<nav aria-label="Tareas del challenge"><a href="../../index.html">FocalRuta</a><a href="#today">Hoy</a><a href="#ranking">Ranking</a><a href="#scenes">Escenas</a><a href="#learn">Aprender</a><a href="#field-run">Campo</a><a href="#rules">Reglas</a></nav><main>
<section id="ranking"><p class="eyebrow">RANKING ROBUSTO · PROXY INTERNO</p><h2>Compara estabilidad, no una falsa certeza</h2><p>R0–R3 comparan valor relativo bajo preferencias internas; no predicen el resultado del concurso. Un rango estrecho indica estabilidad frente a perturbaciones plausibles de pesos; Pareto identifica escenas no dominadas en creatividad, tema, causalidad y anti-postal.</p><div class="ranking-controls"><div><label for="ranking-scenario">Escenario</label><select id="ranking-scenario"><option value="r0">R0 · balanceado</option><option value="r1">R1 · anti-postal</option><option value="r2">R2 · habitar</option><option value="r3">R3 · forma/campo</option></select></div><div><label for="ranking-limit">Mostrar Top N o todas</label><select id="ranking-limit"><option value="5">Top 5</option><option value="15" selected>Top 15</option><option value="40">Top 40</option><option value="all">Todas</option></select></div></div><p id="ranking-count-status" role="status" aria-live="polite"></p><div class="scenes" id="ranking-cards">{ranking_cards(ranking)}</div></section>
<section id="field-priorities"><p class="eyebrow">TOP 5 DE CAMPO · RUTA AÚN CERRADA</p><h2>Valor fotográfico que también se puede intentar</h2><p>Este orden combina potencial, causalidad, evidencia, acceso y factibilidad. No incorpora todavía ventanas horarias ni tiempos de viaje: eso pertenece al optimizador de la siguiente ronda.</p><div class="scenes">{field_priority_cards(ranking)}</div></section>
<section id="scenes"><p class="eyebrow">UNIVERSO CANÓNICO</p><h2>Todos los lugares y escenas</h2><p>Las 81 identidades reconciliadas tienen el mismo contrato de fuentes, imágenes, composición, preguntas, diez pases y A/B/C/D/E. El ranking de escritorio ya puede compararlas; ninguna queda habilitada como ruta hasta verificar ventanas y acceso en campo.</p><label for="scene-limit">Mostrar N escenas</label><select id="scene-limit"><option value="10">10 escenas</option><option value="25">25 escenas</option><option value="40">40 escenas</option><option value="all" selected>Todas las escenas</option></select><p id="scene-count-status" role="status" aria-live="polite">Mostrando todas las escenas.</p><div class="scenes" id="scene-cards">{scene_cards(candidates, cohort, verification)}</div></section>
<section id="learn"><p class="eyebrow">PRÁCTICA</p><h2>Aprende antes de perseguir una locación</h2><h3>Seis modos de ver</h3><ol class="modes">{modes}</ol><article class="callout"><h3>Posición antes que focal</h3><p><strong>Observa:</strong> {escape(lesson["observe"])}</p><p><strong>Prueba:</strong> {escape(lesson["try"])}</p></article><h3>Preguntas de maestros</h3><div class="scenes">{masters}</div></section>
<section id="field-run"><p class="eyebrow">OFFLINE · GUARDADO LOCAL</p><h2>CONTRATO vs USO</h2><p>Observa diez minutos. Resume el propósito original, registra cinco verbos, encuentra tres posiciones y elige focal al final.</p><form id="field-form"><label for="field-scene">Escena</label><select id="field-scene" name="scene">{options}</select><label for="contract">Propósito original · 8 palabras</label><input id="contract" name="contract" maxlength="90"><label for="verbs">Cinco verbos observados</label><textarea id="verbs" name="verbs"></textarea><label for="device">Dispositivo arquitectónico que causa la acción</label><textarea id="device" name="device"></textarea><label for="failure">Por qué todavía falla la mejor toma</label><textarea id="failure" name="failure"></textarea><div class="actions" role="group" aria-label="Decisión de campo"><button type="button" data-decision="STAY">STAY</button><button type="button" data-decision="MOVE">MOVE</button><button type="button" data-decision="RETURN_OTHER_LIGHT">RETURN OTHER LIGHT</button></div><p id="save-status" role="status" aria-live="polite">Se guarda solo en este dispositivo.</p></form><div class="actions"><button id="export-field" type="button" class="secondary">Exportar notas</button><button id="import-field" type="button" class="secondary">Importar notas</button><button id="clear-field" type="button" class="secondary">Borrar notas</button></div><input id="import-file" type="file" accept="application/json" hidden></section>
<section id="ai-firewall"><p class="eyebrow">FLUJO LIMPIO</p><h2>IA para planear, no para intervenir la foto</h2><p>Usa el planificador para investigar, aprender y organizar campo. La selección y evaluación final de la fotografía se mantienen manuales.</p></section><section id="rules" class="architecture-preflight"><p class="eyebrow">PREVUELO</p><h2>Reglas que pueden descalificarte</h2><p class="rule">Cierre: 30 de agosto de 2026 · 23:59, hora local.</p><p class="rule">Exactamente 1 JPG/JPEG · 5–25 MB · captura desde 2020 · nombre-apellido.</p><p>Jurado indicado en las bases: {jurors}.</p><p class="warning">El formulario muestra 25 MB como máximo; las bases también exigen el mínimo de 5 MB.</p><label for="candidate">Fotografía candidata</label><input id="candidate" type="file" accept=".jpg,.jpeg,image/jpeg"><label for="year">Año</label><input id="year" type="number" min="2020" max="2026" value="2026"><button id="check" type="button">Comprobar archivo</button><p id="result" role="status" aria-live="polite">Aún sin comprobar.</p></section>
<noscript><section><h2>Ranking sin JavaScript</h2><p>Las 81 tarjetas y sus rangos R0–R3 permanecen visibles arriba; los filtros Top N requieren JavaScript.</p><h2>CONTRATO vs USO</h2><p>Observa 10 minutos, escribe propósito en 8 palabras, anota 5 verbos, encuentra 3 posiciones, inspecciona bordes y elige focal al final.</p><h2>Reglas</h2><p>Un JPG/JPEG · 5–25 MB · captura desde 2020 · nombre-apellido.</p></section></noscript></main><footer>FocalRuta guarda las notas en tu navegador. La exportación JSON permite moverlas entre dispositivos.</footer><script>{SCRIPT}</script></body></html>'''

def main() -> None:
    values = [json.loads(path.read_text(encoding="utf-8")) for path in (RULES_PATH, LEARNING_PATH, PHOTOGRAPHERS_PATH, COHORT_PATH, CANONICAL_PATH, VERIFICATION_PATH, RANKING_PATH)]
    PUBLIC_CANDIDATES_PATH.write_text(json.dumps(public_candidates(values[-3], values[-2]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(*values), encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))

if __name__ == "__main__":
    main()
