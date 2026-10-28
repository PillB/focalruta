"""
generate_plan_pages.py — Generate all individual plan HTMLs from the canonical plan data.
Each plan HTML embeds its JSON/diagram data and uses the production static CSS bundle.
No Tailwind Play CDN or runtime font/icon CDN is required.
"""

import os
from pathlib import Path
import json
import base64
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plans_data import PLANS, GEAR, COMPOSITION_RULES, CAMERA_ANGLES, TECHNIQUES, FIELD_BASELINES, POSE_NAMES
from exposure_model import SCENE_LIGHT
from PIL import Image
import io

ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = str(ROOT / "plans")
DIAG_DIR = str(ROOT / "diagrams")
os.makedirs(PLAN_DIR, exist_ok=True)


def embed_image_b64(path):
    """Lossless WebP keeps every label pixel-identical to the PNG at a fraction of the bytes."""
    with Image.open(path) as im:
        im = im.convert("RGBA") if im.mode in ("RGBA", "LA") else im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="WEBP", lossless=True, method=6)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/webp;base64,{data}"


# HTML template with __PLACEHOLDERS__ (no f-string conflicts)
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0f172a">
<link rel="manifest" href="../manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<script id="diagnostics-js">
__DIAG_JS__</script>
<title>__PLAN_NAME__ · Plan fotográfico · FocalRuta</title>
<meta name="description" content="__PLAN_DESCRIPTION__">
<link rel="icon" href="../assets/app-icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/icon-192.png">
<style>__SITE_CSS__</style>
<style>
.skip-link{position:absolute;left:8px;top:-64px;z-index:200;padding:10px 14px;border-radius:10px;background:#0f172a;color:#fff;font-weight:700;font-size:14px;text-decoration:none}.skip-link:focus{top:8px}
body { font-family: 'Inter', system-ui, sans-serif; background: #FBFAF5; color: #0F172A; }
.glass { backdrop-filter: blur(8px); background: rgba(255,255,255,0.85); }
/* The bar is 64 px tall on every screen: the name takes two lines at most, and on a phone
   the label and the word "Imprimir" give way so neither the name nor the buttons are cut.
   The place is the page's first line, not the bar's: a long one would be cut there. */
.plan-title { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2; overflow: hidden; }
.plan-place { white-space: nowrap; }
@media (max-width: 640px) { .plan-place, .plan-action-label { display: none; } }
.toggle-active { background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); color: white; box-shadow: 0 4px 12px rgba(37,99,235,0.3); }
.toggle-inactive { background: #F1F5F9; color: #475569; }
.diagram-frame { box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 0 0 1px #E2E8F0; }
.diagram-frame img { width: 100%; height: auto; display: block; }
.chip { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
.reasoning-block { background: linear-gradient(135deg, #FEF3C7 0%, #FED7AA 100%); border-left: 4px solid #F59E0B; }
.do-block { background: #ECFDF5; border-left: 4px solid #16A34A; }
.dont-block { background: #FEF2F2; border-left: 4px solid #DC2626; }
.time-toggle-day { background: linear-gradient(135deg, #FEF3C7 0%, #F59E0B 100%); color: #451A03; }
.time-toggle-afternoon { background: linear-gradient(135deg, #FED7AA 0%, #EA580C 100%); color: #7C2D12; }
.time-toggle-night { background: linear-gradient(135deg, #1E293B 0%, #4338CA 100%); color: #F1F5F9; }
.shot-card { transition: all 0.3s ease; }
.shot-card:hover { transform: scale(1.01); }
.step-number { background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; flex-shrink: 0; }
.pose-pill { background: linear-gradient(135deg, #F3E8FF 0%, #E9D5FF 100%); color: #6B21A8; border: 1px solid #C4B5FD; }
.lens-pill { background: #DBEAFE; color: #1E3A8A; border: 1px solid #93C5FD; }
.aperture-pill { background: #DCFCE7; color: #14532D; border: 1px solid #86EFAC; }
.shutter-pill { background: #FEE2E2; color: #7F1D1D; border: 1px solid #FCA5A5; }
.iso-pill { background: #F1F5F9; color: #334155; border: 1px solid #CBD5E1; }
.nd-pill { background: #1F2937; color: #F9FAFB; border: 1px solid #111827; }
.scene-light-line { font-size: 13px; color: #475569; margin-bottom: 6px; }
/* V15: the setting adapted to the reader's gear. */
.gear-line { margin: .35rem 0 .5rem; padding: .5rem .7rem; border-left: 4px solid #0f766e; background: #f0fdfa; border-radius: 8px; font-size: .8125rem; color: #134e4a; line-height: 1.45; }
.gear-line .gear-values { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 700; }
.gear-line .gear-notes { display: block; margin-top: .2rem; }
.gear-line-no { border-left-color: #b45309; background: #fffbeb; color: #78350f; }
/* V11: every control at least 44 x 44 px, for a thumb in the field. */
summary { min-height: 44px; padding-block: 10px; box-sizing: border-box; }
button, .toggle-active, .toggle-inactive { min-width: 44px; min-height: 44px; }
.unviable-note { font-size: 12px; color: #7C2D12; background: #FFEDD5; border: 1px solid #FDBA74; border-radius: 8px; padding: 6px 10px; margin-bottom: 6px; }
.gradient-bg { background: linear-gradient(135deg, #0F172A 0%, #1E40AF 50%, #7C3AED 100%); }
@media print { .no-print { display: none !important; } .shot-card { page-break-inside: avoid; } }
/* N9: the plan's bar and the Sujeto/Hora bar stay at the top only on screens with room for them,
   measured in the reader's text size (40.0625 by 31.25 em, 641 by 500 px at the default 16 px);
   on a phone, or a phone on its side, they would cover from a fifth to over a third of the
   screen, so there top:auto makes sticky act like relative, in place. Focus and in-page links
   land clear of whatever stays (WCAG 2.4.11, technique C43). The script after the Sujeto/Hora
   bar writes the bars' heights to --fr-nav and --fr-bar; without it the rem values stand in. It
   also marks html.fr-bar-in-flow while the Sujeto/Hora bar is not stuck: the room at the top is
   then the plan's bar alone, and a section below the Sujeto/Hora bar carries its height in its
   margin, so a jump lands in the same place either way (N14). */
html { scroll-padding-top: .75rem; }
@media not all and (min-width: 40.0625em) and (min-height: 31.25em) { nav.glass, section.plan-toggles { top: auto; } }
@media (min-width: 40.0625em) and (min-height: 31.25em) {
  section.plan-toggles { top: var(--fr-nav, 4rem); }
  html { scroll-padding-top: calc(var(--fr-nav, 4rem) + var(--fr-bar, 4.5rem) + .75rem); }
  section[id]:has(~ section.plan-toggles) { scroll-margin-top: calc(-1 * var(--fr-bar, 4.5rem)); }
  html.fr-bar-in-flow { scroll-padding-top: calc(var(--fr-nav, 4rem) + .75rem); }
  html.fr-bar-in-flow section[id]:has(~ section.plan-toggles) { scroll-margin-top: 0; }
  html.fr-bar-in-flow section.plan-toggles ~ section[id] { scroll-margin-top: var(--fr-bar, 4.5rem); }
}
</style>
</head>
<body class="bg-paper text-ink">
<a class="skip-link" href="#contenido">Saltar al contenido</a>



<nav class="glass sticky top-0 z-50 border-b border-slate-200 no-print">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center space-x-3 min-w-0">
        <div class="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center flex-shrink-0">
          <span aria-hidden="true" style="font-size:20px">📷</span>
        </div>
        <div class="min-w-0">
          <h1 class="plan-title text-sm sm:text-base font-bold leading-tight">__PLAN_NAME__</h1>
          <p class="plan-place text-xs text-slate-500">Plan individual</p>
        </div>
      </div>
      <div class="flex items-center space-x-2 flex-shrink-0">
        <a href="../index.html" class="px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-lg transition whitespace-nowrap">← Volver</a>
        <button onclick="window.print()" aria-label="Imprimir" class="px-3 py-2 text-xs font-semibold bg-ink text-white rounded-lg hover:bg-slate-700 transition whitespace-nowrap">🖨<span class="plan-action-label"> Imprimir</span></button>
      </div>
    </div>
  </div>
</nav>

<main id="contenido">
<section id="plan-orientation" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4" aria-labelledby="plan-orientation-title"><div class="bg-emerald-50 border-2 border-emerald-200 rounded-xl p-4"><h2 id="plan-orientation-title" class="font-bold text-base text-emerald-950">Cómo leer este plan</h2><div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-2 text-xs leading-relaxed text-emerald-950"><p><strong>Qué cambia:</strong> la hora, el sujeto y la toma modifican la luz o la acción. El dibujo te enseña dónde poner cámara, sujeto y fondo.</p><p><strong>Cómo comprobarlo:</strong> haz una foto, amplíala al 100% y revisa foco, movimiento, altas luces y bordes. Si cambia la perspectiva, moviste la cámara.</p><p><strong>Si no funciona:</strong> conserva la posición y cambia una sola variable. Si no hay acceso, luz o actividad, usa el plan B de la tarjeta y anota el motivo.</p></div></div></section>

<section class="plan-toggles sticky top-16 z-40 bg-paper/95 backdrop-blur border-y border-slate-200 no-print py-3">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-2">
      <span class="text-xs font-bold text-slate-700 uppercase tracking-wider">Sujeto:</span>
      <div class="inline-flex rounded-lg border border-slate-200 overflow-hidden">
        <button id="toggle-human" onclick="setVariant('human')" class="toggle-active px-3 py-1.5 text-xs font-bold transition">👤 Humano</button>
        <button id="toggle-dog" onclick="setVariant('dog')" class="toggle-inactive px-3 py-1.5 text-xs font-bold transition">🐶 Perro</button>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-xs font-bold text-slate-700 uppercase tracking-wider">Hora:</span>
      <div class="inline-flex rounded-lg border border-slate-200 overflow-hidden">
        <button id="toggle-day" onclick="setTime('day')" class="time-toggle-day px-3 py-1.5 text-xs font-bold transition">☀️ Día</button>
        <button id="toggle-afternoon" onclick="setTime('afternoon')" class="toggle-inactive px-3 py-1.5 text-xs font-bold transition">🌅 Tarde</button>
        <button id="toggle-night" onclick="setTime('night')" class="toggle-inactive px-3 py-1.5 text-xs font-bold transition">🌙 Noche</button>
      </div>
    </div>
  </div>
</section>
<script>
/* N11: the room kept at the top is the bars' real height, whatever the reader's text size. Each bar
   is watched whole, padding and border included: the top bar's padding holds a phone's safe area.
   N14: the room counts the Sujeto/Hora bar only while that bar is stuck and shows under the site's
   bar. While it still sits lower down the page, or once it has gone up under the site's bar at the
   end of its section (N14b), html.fr-bar-in-flow keeps room for the site's bar alone; kept for
   both, the browser counted a control just under the site's bar as out of view and scrolled the
   page to it (csswg-drafts#7930). Read on every scroll, on any change of size, and before each key
   or press. */
(()=>{const nav=document.querySelector('nav.glass'),bar=document.getElementById('toggle-human')?.closest('section');if(!nav||!bar||!window.ResizeObserver)return;const html=document.documentElement,root=html.style,set=(k,v)=>{if(root.getPropertyValue(k)!==v)root.setProperty(k,v)},place=()=>{const r=bar.getBoundingClientRect(),at=parseFloat(getComputedStyle(bar).top)+.5;html.classList.toggle('fr-bar-in-flow',!(r.top<=at&&r.bottom>at))},keep=()=>{set('--fr-nav',nav.getBoundingClientRect().height+'px');set('--fr-bar',bar.getBoundingClientRect().height+'px');place()},watch=new ResizeObserver(keep);watch.observe(nav,{box:'border-box'});watch.observe(bar,{box:'border-box'});watch.observe(html);addEventListener('scroll',place,{passive:true});['keydown','pointerdown'].forEach(t=>addEventListener(t,place,{capture:true,passive:true}))})();
/* N13: Tab and Shift+Tab onto a control of a bar wholly in view, from inside the bar or from the
   control next to it, move focus without scrolling. Inside the room scroll-padding keeps at the
   top, the browser counts that control as out of view and scrolls the page by half a screen on
   every press (csswg-drafts#7930), before any focus event a page could answer. The next control
   is found as the browser finds it, in document order among what can take focus; every other
   move, and any move from a dialog or a radio button, stays the browser's. */
(()=>{const bars=[document.querySelector('nav.glass'),document.getElementById('toggle-human')?.closest('section')].filter(Boolean),html=document.documentElement,FOCUSABLE='a[href],area[href],button,input:not([type=hidden]),select,textarea,iframe,object,embed,summary,audio[controls],video[controls],[contenteditable],[tabindex]',takes=e=>e.tabIndex>=0&&!e.disabled&&!e.closest('[inert]')&&(e.checkVisibility?e.checkVisibility():e.getClientRects().length>0),whole=b=>{const r=b.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight-(parseFloat(getComputedStyle(html).scrollPaddingBottom)||0)};document.addEventListener('keydown',e=>{if(e.key!=='Tab'||e.altKey||e.ctrlKey||e.metaKey||e.defaultPrevented)return;const now=document.activeElement;if(!now||now===document.body||now.type==='radio'||now.closest('dialog,[aria-modal="true"]')||!bars.some(whole))return;const list=[...document.querySelectorAll(FOCUSABLE)].filter(takes),i=list.indexOf(now),next=i<0?null:list[i+(e.shiftKey?-1:1)],bar=next&&next.type!=='radio'&&bars.find(b=>b.contains(next));if(!bar||!whole(bar))return;e.preventDefault();next.focus({preventScroll:true})})})();
</script>

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-4">
  <details class="bg-blue-50 border border-blue-200 rounded-xl p-4">
    <summary class="font-bold text-sm text-blue-950 cursor-pointer">Criterios canónicos · correcciones compartidas con la tarjeta de campo</summary>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 text-xs leading-relaxed text-blue-950">
      <p><strong>Equipo real:</strong> EOS 6D Mark I (sensor 35.8 × 23.9 mm); EF 35mm f/2 IS USM; EF 50mm f/1.8 STM; EF 85mm f/1.8 USM; EF 35–80mm f/4–5.6 III.</p>
      <p><strong>Perspectiva:</strong> cambia geométricamente al mover la cámara. Cambiar focal desde el mismo punto cambia ángulo de visión y recorte, no la relación espacial.</p>
      <p><strong>Ángulos:</strong> nadir = cámara debajo apuntando 90° hacia arriba; cenital = cámara encima apuntando 90° hacia abajo.</p>
      <p><strong>Seguridad:</strong> en modo perro, fantasma usa una persona controlada con el perro fuera; larga exposición de tráfico se hace sin sujeto/perro junto a la calzada; la pintura con luz nunca dirige luz intensa a los ojos.</p>
      <p><strong>Efecto zoom:</strong> usa el 35–80 con la cámara fija; cambia la focal durante la exposición alrededor de un centro fuerte.</p>
      <p><strong>Referencia frente a plan:</strong> la tarjeta de campo es el punto de partida. La variación indicada en cada toma responde a luz/escena; conserva la variable que crea el efecto.</p>
    </div>
  </details>
</section>

<section class="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <div class="h-1.5 rounded-full mb-6" style="background: linear-gradient(90deg, __PALETTE_0__, __PALETTE_2__)"></div>
    <h2 class="text-4xl font-extrabold mb-3 animate-slide-up">__PLAN_NAME__</h2>
    <p class="text-slate-600 mb-4">__PLAN_LOCATION__</p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
      <div class="bg-slate-50 rounded-lg p-3 border border-slate-200">
        <div class="text-xs text-slate-500 mb-1">📍 Acceso estimado</div>
        <div class="font-bold">__DISTANCE__</div>
      </div>
      <div class="bg-slate-50 rounded-lg p-3 border border-slate-200">
        <div class="text-xs text-slate-500 mb-1">🕐 Mejor ventana</div>
        <div class="font-bold text-xs">__WINDOW__</div>
      </div>
      <div class="bg-slate-50 rounded-lg p-3 border border-slate-200">
        <div class="text-xs text-slate-500 mb-1">🎨 Paleta</div>
        <div class="flex gap-1 mt-1">__PALETTE_SWATCHES__</div>
      </div>
    </div>
    <div class="mt-4 p-4 bg-amber-50 border-l-4 border-amber-400 rounded">
      <div class="text-xs font-bold text-amber-700 mb-1">¿POR QUÉ ESTA LOCACIÓN?</div>
      <p class="text-sm text-amber-900">__PLAN_WHY__</p>
    </div>
    <div class="mt-3 p-4 bg-slate-50 border-l-4 border-slate-400 rounded">
      <div class="text-xs font-bold text-slate-700 mb-1">ACCESO Y PERMISOS</div>
      <p class="text-sm text-slate-800">__PLAN_ACCESS__</p>
    </div>
  </div>
  <div id="shots-grid" class="grid grid-cols-1 lg:grid-cols-2 gap-6"></div>
</section>

</main>
<footer class="bg-ink text-white py-8 mt-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <p class="text-sm text-slate-400">__PLAN_NAME__ · Plan individual de FocalRuta</p>
  </div>
</footer>

<script id="gear-js">
__GEAR_JS__</script>
<script>
const DATA = __PLAN_JSON__;
const DIAGRAMS = __DIAGRAMS_JSON__;
let currentVariant = 'human';
let currentTime = 'day';

function setVariant(v) {
  currentVariant = v;
  document.getElementById('toggle-human').className = (v === 'human' ? 'toggle-active' : 'toggle-inactive') + ' px-3 py-1.5 text-xs font-bold transition';
  document.getElementById('toggle-dog').className = (v === 'dog' ? 'toggle-active' : 'toggle-inactive') + ' px-3 py-1.5 text-xs font-bold transition';
  renderShots();
}

function setTime(t) {
  currentTime = t;
  ['day','afternoon','night'].forEach(tt => {
    const btn = document.getElementById('toggle-' + tt);
    btn.classList.remove('time-toggle-day', 'time-toggle-afternoon', 'time-toggle-night');
    btn.classList.add('toggle-inactive');
  });
  const activeBtn = document.getElementById('toggle-' + t);
  activeBtn.classList.remove('toggle-inactive');
  if (t === 'day') activeBtn.classList.add('time-toggle-day');
  else if (t === 'afternoon') activeBtn.classList.add('time-toggle-afternoon');
  else if (t === 'night') activeBtn.classList.add('time-toggle-night');
  renderShots();
}

function timeLabel(t) {
  return { day: 'DÍA', afternoon: 'TARDE', night: 'NOCHE' }[t] || '';
}

function ndLabel(stops){
  if(!stops) return '';
  return `${stops===10 ? 'ND1000' : 'ND'+(2**stops)} · ${stops} pasos`;
}
function sceneLightText(ts){
  const light=(DATA.scene_light||{})[ts.scene];
  if(!light) return '';
  const ev=light.ev_low===light.ev_high ? `EV ${light.ev_low}` : `EV ${light.ev_low} a ${light.ev_high}`;
  return `${light.label} (${ev})`;
}
function settingsChips(ts){
  return `<span class="chip lens-pill">${ts.lens}</span><span class="chip aperture-pill">${ts.aperture}</span><span class="chip shutter-pill">${ts.shutter}</span><span class="chip iso-pill">ISO ${ts.iso}</span>`+
    (ts.nd_stops ? `<span class="chip nd-pill" title="Filtro de densidad neutra de ${ts.nd_stops} pasos">${ndLabel(ts.nd_stops)}</span>` : '');
}
function slotStatus(ts){
  const light=sceneLightText(ts);
  const line=light ? `<div class="scene-light-line">☀︎ Luz prevista: ${light}</div>` : '';
  if(ts.viable===false) return `<div class="unviable-note" role="note"><strong>No viable a esta hora.</strong> Cambia el horario arriba o pospón esta toma.</div>`+line;
  return line;
}
function poseName(view){
  const names=(DATA.pose_names||{})[view.kind]||{};
  return names[view.data.pose] || view.data.pose.replace(/_/g,' ');
}
function baselineForShot(plan, shot) {
  const b=DATA.field_baselines||{};
  if(shot.technique==='mucha_pdc'||shot.technique==='poca_pdc'){
    const same=plan.shots.filter(s=>s.technique===shot.technique);
    const pos=Math.max(0,same.findIndex(s=>s.id===shot.id));
    return b[`${shot.technique}_${Math.min(pos+1,2)}`]||null;
  }
  return b[shot.technique]||null;
}
function effectiveSubject(shot){
  if(currentVariant==='dog'&&shot.technique==='fantasma') return {label:'PERSONA · perro fuera', kind:'human', data:shot.subjects.human};
  if(currentVariant==='dog'&&shot.technique==='larga_exp') return {label:'SIN SUJETO · perro fuera', kind:null, data:null};
  return {label: currentVariant==='human'?'Humano':'Perro', kind:currentVariant, data:shot.subjects[currentVariant]};
}

function renderShots() {
  const plan = DATA.plan;
  const container = document.getElementById('shots-grid');
  container.innerHTML = plan.shots.map((shot, idx) => {
    const diagramKey = shot.id + '_' + currentVariant;
    const diagramSrc = DIAGRAMS[diagramKey] || '';
    const timeSettings = shot.settings_by_time[currentTime];
    const technique = DATA.techniques[shot.technique];
    const baseline = baselineForShot(plan,shot);
    const subjectView = effectiveSubject(shot);
    return `
      <article class="shot-card bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden animate-fade-in" style="animation-delay:${idx*0.05}s">
        <div class="p-5 border-b border-slate-100">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="step-number" style="width:28px;height:28px;font-size:12px">${idx+1}</span>
              <span class="font-mono text-xs text-slate-500">${shot.id}</span>
            </div>
            <span class="chip bg-purple-100 text-purple-700">📷&nbsp;${shot.technique_label}</span>
          </div>
          <div class="flex flex-wrap gap-1.5 mb-2">${settingsChips(timeSettings)}</div>
          ${window.FocalRutaEquipo ? FocalRutaEquipo.lineFor(shot, timeSettings) : ''}
          ${slotStatus(timeSettings)}
          <div class="text-xs text-slate-600 mb-2">
            <span class="font-bold">Composición:</span> ${shot.composition_label} ·
            <span class="font-bold">Ángulo:</span> ${shot.angle_label} ·
            <span class="font-bold">Distancia:</span> ${shot.subject_distance_m} m ·
            <span class="font-bold">Fondo:</span> ${shot.background_distance_m} m
          </div>
          <div class="text-xs text-slate-700 italic">${shot.scene_notes}</div>
        </div>
        <div class="diagram-frame bg-paper">
          ${diagramSrc ? `<img src="${diagramSrc}" alt="Diagrama ${shot.id}, ${currentVariant === 'human' ? 'con persona' : 'con perro'}" width="1744" height="1058" loading="${idx<2?'eager':'lazy'}" decoding="async" /><p class="px-4 py-2 text-xs leading-relaxed text-slate-600"><strong>Qué mirar:</strong> compara las distancias dibujadas y el borde del encuadre con tu escena. Es una relación orientativa, no una promesa de píxeles.</p>` : '<div class="p-8 text-center text-slate-400">Diagrama no disponible</div>'}
        </div>
        <div class="p-5 space-y-3">
          ${baseline ? `<div class="bg-slate-50 border border-slate-300 rounded-lg p-3"><div class="text-xs font-black tracking-wider text-slate-700">TARJETA DE CAMPO · REFERENCIA</div><div class="text-xs font-mono mt-1">${baseline.lens} · ${baseline.aperture} · ${baseline.shutter} · ISO ${baseline.iso}</div><div class="text-xs text-slate-600">${baseline.af} · ${baseline.geometry}</div><div class="text-xs text-blue-700 mt-1">El plan puede variar por escena/luz; conserva la variable que define el efecto.</div></div>` : ''}
          <div class="reasoning-block p-3 rounded-lg">
            <div class="text-xs font-bold text-amber-800 mb-1">RAZONAMIENTO</div>
            <p class="text-xs text-amber-900 leading-relaxed">${shot.reasoning}</p>
          </div>
          <div class="do-block p-3 rounded-lg">
            <div class="text-xs font-bold text-emerald-700 mb-1">✓ HACER</div>
            <ul class="text-xs text-emerald-900 space-y-1 list-disc list-inside">
              ${shot.dos.map(d => `<li>${d}</li>`).join('')}
            </ul>
          </div>
          <div class="dont-block p-3 rounded-lg">
            <div class="text-xs font-bold text-red-700 mb-1">✗ EVITAR</div>
            <ul class="text-xs text-red-900 space-y-1 list-disc list-inside">
              ${shot.donts.map(d => `<li>${d}</li>`).join('')}
            </ul>
          </div>
          ${timeSettings.notes ? `
          <div class="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
            <div class="text-xs font-bold text-blue-700 mb-1">NOTA ${timeLabel(currentTime)}</div>
            <p class="text-xs text-blue-900">${timeSettings.notes}</p>
          </div>` : ''}
          <div class="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <div class="text-xs font-bold text-purple-700 mb-1">🎭 SUJETO (${subjectView.label})</div>
            ${subjectView.data ? `<p class="text-xs text-purple-900"><strong>${poseName(subjectView)}</strong>: ${subjectView.data.action}</p>` : `<p class="text-xs text-purple-900"><strong>SIN SUJETO</strong>: prioriza trazas/escena y seguridad.</p>`}
          </div>
        </div>
      </article>
    `;
  }).join('');
}

window.addEventListener('DOMContentLoaded', renderShots);
// The gear chosen on the home page applies here too (V15).
window.addEventListener('storage', e => { if (e.key === 'focalruta-equipo-v1') renderShots(); });
</script>
<script>if(('serviceWorker' in navigator)&&(location.protocol==='http:'||location.protocol==='https:')){window.addEventListener('load',()=>navigator.serviceWorker.register('../sw.js').catch(e=>FocalRutaDiagnostico.record('trabajador',e&&e.message||String(e),'sw.js')));}</script>

</body>
</html>
"""


def generate_plan_html(plan):
    plan_id = plan["id"]
    print(f"  Encoding diagrams for {plan_id}...")
    diagrams_b64 = {}
    for shot in plan["shots"]:
        for variant in ["human", "dog"]:
            fname = f"{plan_id}_{shot['id']}_{variant}.png"
            fpath = os.path.join(DIAG_DIR, fname)
            if os.path.exists(fpath):
                diagrams_b64[f"{shot['id']}_{variant}"] = embed_image_b64(fpath)
    print(f"    ✓ {len(diagrams_b64)} diagrams encoded")

    plan_data = {
        "plan": plan,
        "composition_rules": COMPOSITION_RULES,
        "camera_angles": CAMERA_ANGLES,
        "techniques": TECHNIQUES,
        "field_baselines": FIELD_BASELINES,
        "pose_names": POSE_NAMES,
        "scene_light": {
            key: {"ev_low": low, "ev_high": high, "label": label, "source": source}
            for key, (low, high, label, source) in SCENE_LIGHT.items()
        },
    }

    palette = plan.get("palette", ["#3b5d3b","#6b8e4e","#c4a35a","#d9d4c5"])
    palette_swatches = "".join(f'<div class="w-6 h-6 rounded" style="background:{c}"></div>' for c in palette)

    html = HTML_TEMPLATE
    site_css=(Path(__file__).resolve().parents[1]/"assets"/"site.css").read_text(encoding="utf-8")
    html = html.replace("__SITE_CSS__", site_css)
    description = f"Diez tomas planificadas en {plan['location']} para Canon 6D, con diagramas a escala y ajustes para día, tarde y noche."
    html = html.replace("__PLAN_DESCRIPTION__", description.replace('"', "&quot;"))
    html = html.replace("__PLAN_NAME__", plan["name"])
    html = html.replace("__PLAN_LOCATION__", plan["location"])
    html = html.replace("__DISTANCE__", plan["distance_from_home"])
    html = html.replace("__WINDOW__", plan["best_window"])
    html = html.replace("__PALETTE_0__", palette[0])
    html = html.replace("__PALETTE_2__", palette[2])
    html = html.replace("__PALETTE_SWATCHES__", palette_swatches)
    html = html.replace("__PLAN_WHY__", plan["why"])
    html = html.replace("__PLAN_ACCESS__", plan["access"])
    html = html.replace("__PLAN_JSON__", json.dumps(plan_data, ensure_ascii=False))
    html = html.replace("__DIAGRAMS_JSON__", json.dumps(diagrams_b64, ensure_ascii=False))
    html = html.replace("__GEAR_JS__", (Path(__file__).resolve().parents[1] / "assets" / "gear.js").read_text(encoding="utf-8"), 1)
    html = html.replace("__DIAG_JS__", (Path(__file__).resolve().parents[1] / "assets" / "diagnostics.js").read_text(encoding="utf-8"), 1)

    out_path = os.path.join(PLAN_DIR, f"{plan_id}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def main():
    print("Generating individual plan HTMLs...")
    for plan in PLANS:
        path = generate_plan_html(plan)
        size = os.path.getsize(path) / (1024 * 1024)
        print(f"  ✓ {path} ({size:.1f} MB)")
    print("\nAll individual plan HTMLs generated.")


if __name__ == "__main__":
    main()
