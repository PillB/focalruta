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
from plans_data import PLANS, GEAR, COMPOSITION_RULES, CAMERA_ANGLES, TECHNIQUES, FIELD_BASELINES

ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = str(ROOT / "plans")
DIAG_DIR = str(ROOT / "diagrams")
os.makedirs(PLAN_DIR, exist_ok=True)


def embed_image_b64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{data}"


# HTML template with __PLACEHOLDERS__ (no f-string conflicts)
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0f172a">
<link rel="manifest" href="../manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>__PLAN_NAME__ — Plan individual</title>
<style>__SITE_CSS__</style>
<style>
body { font-family: 'Inter', system-ui, sans-serif; background: #FBFAF5; color: #0F172A; }
.glass { backdrop-filter: blur(8px); background: rgba(255,255,255,0.85); }
.toggle-active { background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); color: white; box-shadow: 0 4px 12px rgba(37,99,235,0.3); }
.toggle-inactive { background: #F1F5F9; color: #475569; }
.diagram-frame { box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 0 0 1px #E2E8F0; }
.diagram-frame img { width: 100%; height: auto; display: block; }
.chip { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600; }
.reasoning-block { background: linear-gradient(135deg, #FEF3C7 0%, #FED7AA 100%); border-left: 4px solid #F59E0B; }
.do-block { background: #ECFDF5; border-left: 4px solid #16A34A; }
.dont-block { background: #FEF2F2; border-left: 4px solid #DC2626; }
.time-toggle-day { background: linear-gradient(135deg, #FEF3C7 0%, #F59E0B 100%); color: #78350F; }
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
.gradient-bg { background: linear-gradient(135deg, #0F172A 0%, #1E40AF 50%, #7C3AED 100%); }
@media print { .no-print { display: none !important; } .shot-card { page-break-inside: avoid; } }
</style>
</head>
<body class="bg-paper text-ink">

<section id="plan-orientation" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4" aria-labelledby="plan-orientation-title"><div class="bg-emerald-50 border-2 border-emerald-200 rounded-xl p-4"><h2 id="plan-orientation-title" class="font-bold text-base text-emerald-950">Cómo leer este plan</h2><div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-2 text-xs leading-relaxed text-emerald-950"><p><strong>Qué cambia:</strong> la hora, el sujeto y la toma modifican la luz o la acción. El dibujo te enseña dónde poner cámara, sujeto y fondo.</p><p><strong>Cómo comprobarlo:</strong> haz una foto, amplíala al 100% y revisa foco, movimiento, altas luces y bordes. Si cambia la perspectiva, moviste la cámara.</p><p><strong>Si no funciona:</strong> conserva la posición y cambia una sola variable. Si no hay acceso, luz o actividad, usa el plan B de la tarjeta y anota el motivo.</p></div></div></section>

<nav class="glass sticky top-0 z-50 border-b border-slate-200 no-print">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
          <span aria-hidden="true" style="font-size:20px">📷</span>
        </div>
        <div>
          <h1 class="text-base font-bold leading-tight">__PLAN_NAME__</h1>
          <p class="text-xs text-slate-500">Plan individual · __PLAN_LOCATION__</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <a href="../index.html" class="px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-lg transition">← Volver</a>
        <button onclick="window.print()" class="px-3 py-2 text-xs font-semibold bg-ink text-white rounded-lg hover:bg-slate-700 transition">🖨 Imprimir</button>
      </div>
    </div>
  </div>
</nav>

<section class="sticky top-16 z-40 bg-paper/95 backdrop-blur border-y border-slate-200 no-print py-3">
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

<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-4">
  <details class="bg-blue-50 border border-blue-200 rounded-xl p-4">
    <summary class="font-bold text-sm text-blue-950 cursor-pointer">Criterios canónicos · correcciones compartidas con la Field Card</summary>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 text-xs leading-relaxed text-blue-950">
      <p><strong>Equipo real:</strong> EOS 6D Mark I (sensor 35.8 × 23.9 mm); EF 35mm f/2 IS USM; EF 50mm f/1.8 STM; EF 85mm f/1.8 USM; EF 35–80mm f/4–5.6 III.</p>
      <p><strong>Perspectiva:</strong> cambia geométricamente al mover la cámara. Cambiar focal desde el mismo punto cambia ángulo de visión y recorte, no la relación espacial.</p>
      <p><strong>Ángulos:</strong> nadir = cámara debajo apuntando 90° hacia arriba; cenital = cámara encima apuntando 90° hacia abajo.</p>
      <p><strong>Seguridad:</strong> en modo perro, fantasma usa una persona controlada con el perro fuera; larga exposición de tráfico se hace sin sujeto/perro junto a la calzada; lightpainting nunca dirige luz intensa a los ojos.</p>
      <p><strong>Zooming:</strong> usa el 35–80 con la cámara fija; cambia la focal durante la exposición alrededor de un centro fuerte.</p>
      <p><strong>Baseline vs plan:</strong> la Field Card es el punto de partida. La variación indicada en cada toma responde a luz/escena; conserva la variable que crea el efecto.</p>
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
  </div>
  <div id="shots-grid" class="grid grid-cols-1 lg:grid-cols-2 gap-6"></div>
</section>

<footer class="bg-ink text-white py-8 mt-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <p class="text-sm text-slate-400">__PLAN_NAME__ · Plan individual de FocalRuta</p>
  </div>
</footer>

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
  if(currentVariant==='dog'&&shot.technique==='fantasma') return {label:'PERSONA · perro fuera', data:shot.subjects.human};
  if(currentVariant==='dog'&&shot.technique==='larga_exp') return {label:'SIN SUJETO · perro fuera', data:null};
  return {label: currentVariant==='human'?'Humano':'Perro', data:shot.subjects[currentVariant]};
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
          <div class="flex flex-wrap gap-1.5 mb-3">
            <span class="chip lens-pill">${shot.lens_focal}mm</span>
            <span class="chip aperture-pill">${shot.aperture}</span>
            <span class="chip shutter-pill">${timeSettings.shutter}</span>
            <span class="chip iso-pill">ISO ${timeSettings.iso}</span>
          </div>
          <div class="text-xs text-slate-600 mb-2">
            <span class="font-bold">Composición:</span> ${shot.composition_label} ·
            <span class="font-bold">Ángulo:</span> ${shot.angle_label} ·
            <span class="font-bold">Distancia:</span> ${shot.subject_distance_m}m ·
            <span class="font-bold">Fondo:</span> ${shot.background_distance_m}m
          </div>
          <div class="text-xs text-slate-700 italic">${shot.scene_notes}</div>
        </div>
        <div class="diagram-frame bg-paper">
          ${diagramSrc ? `<img src="${diagramSrc}" alt="Diagrama ${shot.id} ${currentVariant}" /><p class="px-4 py-2 text-[11px] leading-relaxed text-slate-600"><strong>Qué mirar:</strong> compara las distancias dibujadas y el borde del encuadre con tu escena. Es una relación orientativa, no una promesa de píxeles.</p>` : '<div class="p-8 text-center text-slate-400">Diagrama no disponible</div>'}
        </div>
        <div class="p-5 space-y-3">
          ${baseline ? `<div class="bg-slate-50 border border-slate-300 rounded-lg p-3"><div class="text-[10px] font-black tracking-wider text-slate-700">FIELD CARD · BASELINE</div><div class="text-[11px] font-mono mt-1">${baseline.lens} · ${baseline.aperture} · ${baseline.shutter} · ISO ${baseline.iso}</div><div class="text-[11px] text-slate-600">${baseline.af} · ${baseline.geometry}</div><div class="text-[10px] text-blue-700 mt-1">El plan puede variar por escena/luz; conserva la variable que define el efecto.</div></div>` : ''}
          <div class="reasoning-block p-3 rounded-lg">
            <div class="text-xs font-bold text-amber-700 mb-1">RAZONAMIENTO</div>
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
            ${subjectView.data ? `<p class="text-xs text-purple-900"><strong>${subjectView.data.pose.replace(/_/g,' ').toUpperCase()}</strong>: ${subjectView.data.action}</p>` : `<p class="text-xs text-purple-900"><strong>SIN SUJETO</strong>: prioriza trazas/escena y seguridad.</p>`}
          </div>
        </div>
      </article>
    `;
  }).join('');
}

window.addEventListener('DOMContentLoaded', renderShots);
</script>
<script>if(('serviceWorker' in navigator)&&(location.protocol==='http:'||location.protocol==='https:')){window.addEventListener('load',()=>navigator.serviceWorker.register('../sw.js').catch(()=>{}));}</script>

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
    }

    palette = plan.get("palette", ["#3b5d3b","#6b8e4e","#c4a35a","#d9d4c5"])
    palette_swatches = "".join(f'<div class="w-6 h-6 rounded" style="background:{c}"></div>' for c in palette)

    html = HTML_TEMPLATE
    site_css=(Path(__file__).resolve().parents[1]/"assets"/"site.css").read_text(encoding="utf-8")
    html = html.replace("__SITE_CSS__", site_css)
    html = html.replace("__PLAN_NAME__", plan["name"])
    html = html.replace("__PLAN_LOCATION__", plan["location"])
    html = html.replace("__DISTANCE__", plan["distance_from_home"])
    html = html.replace("__WINDOW__", plan["best_window"])
    html = html.replace("__PALETTE_0__", palette[0])
    html = html.replace("__PALETTE_2__", palette[2])
    html = html.replace("__PALETTE_SWATCHES__", palette_swatches)
    html = html.replace("__PLAN_WHY__", plan["why"])
    html = html.replace("__PLAN_JSON__", json.dumps(plan_data, ensure_ascii=False))
    html = html.replace("__DIAGRAMS_JSON__", json.dumps(diagrams_b64, ensure_ascii=False))

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
