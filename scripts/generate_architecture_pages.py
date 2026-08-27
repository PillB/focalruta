#!/usr/bin/env python3
"""Generate the dependency-free Round 1 architecture challenge shell."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "architecture" / "competition_rules.json"
LEARNING_PATH = ROOT / "data" / "architecture" / "learning.json"
PHOTOGRAPHERS_PATH = ROOT / "data" / "architecture" / "photographers.json"
OUTPUT = ROOT / "challenges" / "arquitectura-en-foco" / "index.html"


def render_learning(learning: dict, photographers: dict) -> str:
    modes = "".join(f"<li>{escape(mode)}</li>" for mode in photographers["seeing_modes"])
    cards = "".join(
        f'<article class="card"><h3>{escape(card["photographer"])}</h3>'
        f'<p><strong>Pregunta:</strong> {escape(card["signature_question"])}</p>'
        f'<p><strong>Prueba de campo:</strong> {escape(card["field_drill"])}</p>'
        f'<p><strong>Riesgo:</strong> {escape(card["misuse_risk"])}</p></article>'
        for card in photographers["transfer_cards"]
    )
    lesson = learning["lessons"][1]
    return (
        '<section id="learn"><h2>Aprende en el lugar</h2>'
        '<h3>Seis modos de ver</h3><ol class="modes">' + modes + '</ol>'
        '<article class="drill"><h3>Posición antes que focal</h3>'
        f'<p><strong>Observa:</strong> {escape(lesson["observe"])}</p>'
        f'<p><strong>Prueba:</strong> {escape(lesson["try"])}</p></article>'
        '<div class="cards">' + cards + '</div></section>'
    )


def render(rules: dict, learning: dict, photographers: dict) -> str:
    jurors = " · ".join(escape(name) for name in rules["jurors"])
    learning_html = render_learning(learning, photographers)
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="../../assets/app-icon.svg" type="image/svg+xml">
<title>Arquitectura en Foco · FocalRuta</title><style>
:root{{--ink:#14231f;--paper:#f7f3e9;--accent:#b84c32;--line:#c9c0ad}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}main{{max-width:920px;margin:auto;padding:clamp(20px,5vw,56px)}}h1{{font-size:clamp(2rem,8vw,4.8rem);line-height:.95}}section{{border-top:1px solid var(--line);padding:28px 0}}.rule{{font-weight:750}}.warning,.drill{{border-left:5px solid var(--accent);padding:14px 18px;background:#fff}}.modes{{columns:2;gap:28px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:14px}}.card{{padding:16px;border:1px solid var(--line);border-radius:8px;background:#fff}}label{{display:block;margin:12px 0 4px}}input,button{{font:inherit;min-height:44px}}input[type=file]{{max-width:100%}}button{{margin-top:16px;padding:8px 18px;background:var(--ink);color:white;border:0;border-radius:6px}}button:focus-visible,input:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}@media(max-width:520px){{.modes{{columns:1}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
</style></head><body><main>
<p>FocalRuta · Challenge 2026</p><h1>Arquitectura<br>en foco</h1>
<p>Una sola fotografía. Busca la relación entre diseño, vida cotidiana y ciudad que se lea antes de la explicación.</p>
<section id="rules"><h2>Reglas que pueden descalificarte</h2>
<p class="rule">Cierre: 30 de agosto de 2026 · 23:59, hora local del país.</p>
<p class="rule">Exactamente 1 JPG/JPEG · 5–25 MB · captura desde 2020 · archivo nombre-apellido.</p>
<p>Jurado indicado en las bases: {jurors}.</p>
<p>El formulario muestra 25 MB como máximo; las bases oficiales también exigen el mínimo de 5 MB.</p></section>
<section id="ai-firewall" class="warning"><h2>Flujo limpio con IA</h2><p>Usa este planificador para investigar y planear. Mantén el RAW/JPG/JPEG candidato fuera de crítica, selección, edición o mejora con IA salvo autorización específica y almacenada del organizador. La evaluación final es manual y el preflight local no modifica el archivo.</p></section>
{learning_html}
<section id="architecture-preflight"><h2>Preflight local</h2><p>Este navegador inspecciona nombre, formato y tamaño sin subir la fotografía.</p>
<label for="candidate">Fotografía candidata</label><input id="candidate" type="file" accept=".jpg,.jpeg,image/jpeg">
<label for="year">Año de captura</label><input id="year" type="number" min="2020" max="2026" value="2026">
<button id="check" type="button">Comprobar archivo</button><p id="result" role="status" aria-live="polite">Aún sin comprobar.</p></section>
<noscript><section><h2>Preflight sin JavaScript</h2><p>Comprueba manualmente: un solo JPG/JPEG, 5–25 MB, captura 2020 o posterior, nombre-apellido, respaldo y campos del formulario. Confirma solo ajustes básicos permitidos y ninguna alteración fundamental, collage o intervención con IA.</p></section></noscript>
</main><script>
const fileInput=document.querySelector('#candidate'),year=document.querySelector('#year'),result=document.querySelector('#result');
document.querySelector('#check').addEventListener('click',()=>{{const files=[...fileInput.files];const errors=[];if(files.length!==1)errors.push('Selecciona exactamente un archivo.');if(files.length===1){{const f=files[0],stem=f.name.replace(/\.[^.]+$/,'');if(!/\.jpe?g$/i.test(f.name))errors.push('Debe ser JPG o JPEG.');if(f.size<5000000||f.size>25000000)errors.push('Debe pesar entre 5 y 25 MB.');if(!/^[^\W\d_]+(?:-[^\W\d_]+)+$/u.test(stem))errors.push('Usa nombre-apellido.')}}if(Number(year.value)<2020)errors.push('La captura debe ser de 2020 o posterior.');result.textContent=errors.length?errors.join(' '):'Pasa las comprobaciones automáticas. Completa las confirmaciones manuales antes de enviar.';}});
</script></body></html>'''


def main() -> None:
    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    learning = json.loads(LEARNING_PATH.read_text(encoding="utf-8"))
    photographers = json.loads(PHOTOGRAPHERS_PATH.read_text(encoding="utf-8"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(rules, learning, photographers), encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
