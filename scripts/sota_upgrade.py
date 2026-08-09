from pathlib import Path
import re, json, math, shutil, hashlib, io
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
HTML=INDEX.read_text(encoding='utf-8')

CSS=r'''
/* SOTA_ENHANCEMENTS_START */
:root{--sota-teal:#0f766e;--sota-blue:#2563eb;--sota-gold:#d6a62e;--sota-ink:#0f172a;--sota-soft:#f8fafc}
.sota-actions{display:flex;gap:.5rem;flex-wrap:wrap}.sota-btn{min-height:44px;border:1px solid #cbd5e1;background:#fff;color:#0f172a;border-radius:12px;padding:.65rem .85rem;font-weight:800;font-size:.78rem;cursor:pointer;transition:.18s}.sota-btn:hover,.sota-btn:focus-visible{border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.14);outline:0}.sota-btn[aria-pressed="true"],.sota-btn.is-active{background:#0f766e;color:#fff;border-color:#0f766e}.sota-btn-dark{background:#0f172a;color:#fff;border-color:#0f172a}.sota-btn-gold{background:#fff7d6;border-color:#e2b93b;color:#714f00}
.sota-card{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:1rem;box-shadow:0 8px 30px rgba(15,23,42,.05)}.sota-kicker{font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;font-weight:900;color:#0f766e}.sota-muted{color:#64748b}.sota-metric{font-size:1.35rem;font-weight:900;line-height:1}.sota-metric small{font-size:.62rem;font-weight:700;color:#64748b;display:block;margin-top:.35rem;line-height:1.25}.sota-grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}.sota-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem}
.opt-preset-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.5rem}.opt-compare{display:grid;grid-template-columns:1fr 1fr;gap:.6rem}.opt-axis-label{font-size:11px;fill:#cbd5e1}.opt-dof-band{fill:#16a34a;opacity:.16}.opt-focus-line{stroke:#f59e0b;stroke-width:3}.opt-nearfar{stroke:#22c55e;stroke-width:2;stroke-dasharray:5 4}.opt-bg-line{stroke:#94a3b8;stroke-width:3}.opt-subject-marker{fill:#f59e0b;stroke:#fff;stroke-width:2}
.motion-stage{position:relative;height:250px;border-radius:18px;overflow:hidden;background:linear-gradient(#dbeafe 0 45%,#e2e8f0 45% 100%);border:1px solid #cbd5e1}.motion-road{position:absolute;left:0;right:0;bottom:36px;height:72px;background:#475569}.motion-road:after{content:"";position:absolute;left:0;right:0;top:34px;border-top:3px dashed #f8fafc}.motion-subject{position:absolute;width:54px;height:38px;border-radius:14px;background:#f59e0b;border:3px solid #fff;bottom:57px;left:46%;transform:translateX(-50%);box-shadow:0 4px 12px rgba(0,0,0,.2)}.motion-trail{position:absolute;height:12px;border-radius:999px;background:linear-gradient(90deg,transparent,#f59e0b);bottom:70px;right:52%;transform-origin:right center}.motion-bg-lines{position:absolute;inset:25px 0 auto;height:120px;background:repeating-linear-gradient(90deg,rgba(15,23,42,.14) 0 3px,transparent 3px 44px)}.motion-ghost{position:absolute;width:54px;height:86px;border-radius:40% 40% 30% 30%;background:#6366f1;bottom:51px;left:45%;opacity:.65}.motion-light{position:absolute;left:8%;right:8%;bottom:74px;height:9px;border-radius:999px;background:linear-gradient(90deg,#fde68a,#fff,#f87171);box-shadow:0 0 15px rgba(253,230,138,.8)}.motion-radial{position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at 50% 58%,rgba(168,85,247,.3) 0 2deg,transparent 2deg 16deg);opacity:.7}.motion-caption{position:absolute;top:12px;left:12px;right:12px;background:rgba(255,255,255,.88);backdrop-filter:blur(6px);border-radius:10px;padding:8px 10px;font-size:12px;font-weight:800;color:#334155}
.comp-stage{position:relative;aspect-ratio:3/2;border-radius:18px;overflow:hidden;background:linear-gradient(#dbeafe 0 58%,#cbd5a5 58%);border:1px solid #cbd5e1;touch-action:none}.comp-grid-third{position:absolute;inset:0;background:linear-gradient(90deg,transparent 33.1%,rgba(255,255,255,.75) 33.1% 33.5%,transparent 33.5% 66.2%,rgba(255,255,255,.75) 66.2% 66.6%,transparent 66.6%),linear-gradient(0deg,transparent 33.1%,rgba(255,255,255,.75) 33.1% 33.5%,transparent 33.5% 66.2%,rgba(255,255,255,.75) 66.2% 66.6%,transparent 66.6%)}.comp-center{position:absolute;left:50%;top:0;bottom:0;border-left:2px dashed rgba(255,255,255,.8)}.comp-frame{position:absolute;inset:11%;border:18px solid rgba(15,23,42,.42);border-radius:48% 48% 42% 42%}.comp-leading{position:absolute;left:0;bottom:0;width:100%;height:100%;background:linear-gradient(32deg,transparent 48.8%,rgba(255,255,255,.8) 49% 49.6%,transparent 49.8%),linear-gradient(-32deg,transparent 48.8%,rgba(255,255,255,.8) 49% 49.6%,transparent 49.8%)}.comp-subject{position:absolute;width:42px;height:74px;border-radius:45% 45% 32% 32%;background:#f59e0b;border:3px solid #fff;transform:translate(-50%,-50%);left:66.6%;top:66.6%;box-shadow:0 6px 20px rgba(0,0,0,.2);cursor:grab}.comp-subject:before{content:"";position:absolute;width:24px;height:24px;border-radius:50%;background:#f59e0b;border:3px solid #fff;left:6px;top:-20px}.comp-neg{position:absolute;right:6%;top:12%;font-size:11px;font-weight:900;color:#0f172a;background:rgba(255,255,255,.75);padding:5px 8px;border-radius:999px}
#session-run-dialog{width:min(760px,calc(100% - 18px));max-height:min(92dvh,900px);border:0;border-radius:22px;padding:0;box-shadow:0 30px 90px rgba(2,6,23,.38);color:#0f172a}#session-run-dialog::backdrop{background:rgba(2,6,23,.72);backdrop-filter:blur(7px)}.run-head{position:sticky;top:0;z-index:3;background:#071827;color:#fff;padding:14px 16px;display:flex;align-items:center;justify-content:space-between;gap:10px}.run-body{padding:16px;overflow:auto}.run-progress{height:7px;border-radius:999px;background:#e2e8f0;overflow:hidden}.run-progress>div{height:100%;background:#0f766e;transition:width .2s}.run-baseline{background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;padding:10px;font-size:12px}.run-current{display:grid;grid-template-columns:1fr 1fr;gap:10px}.run-diagram{width:100%;border-radius:12px;border:1px solid #e2e8f0;background:#fff}.run-delta{font-size:11px;color:#475569;margin-top:4px}.run-footer{display:flex;gap:8px;justify-content:space-between;position:sticky;bottom:0;background:linear-gradient(transparent,#fff 25%);padding-top:18px}.run-done{background:#dcfce7!important;border-color:#86efac!important}
.hosted-badge{display:inline-flex;align-items:center;gap:.35rem;background:#ecfeff;color:#155e75;border:1px solid #a5f3fc;border-radius:999px;padding:.3rem .55rem;font-size:.65rem;font-weight:900}
@media(max-width:640px){.sota-grid3{grid-template-columns:1fr}.opt-compare,.run-current{grid-template-columns:1fr}.motion-stage{height:220px}.sota-card{padding:.85rem}.mobile-bottom-nav{grid-template-columns:repeat(6,minmax(0,1fr))!important}.mobile-bottom-nav a,.mobile-bottom-nav button{font-size:9px!important}.mobile-bottom-nav .ico{font-size:16px!important}}
@media(prefers-reduced-motion:reduce){.motion-subject,.motion-trail,.motion-ghost,.motion-light,.motion-radial{transition:none!important;animation:none!important}}
/* SOTA_ENHANCEMENTS_END */
'''

def replace_between(text,start,end,new):
    a=text.find(start); b=text.find(end)
    if a<0 or b<0 or b<a: raise RuntimeError(f'markers missing {start} / {end}')
    return text[:a]+new+text[b:]

# Remove old enhancement if re-running.
HTML=re.sub(r'<style id="sota-enhancements">.*?</style>\s*','',HTML,flags=re.S)
HTML=HTML.replace('</head>',f'<style id="sota-enhancements">{CSS}</style>\n</head>',1)

OPTICS='''<!-- ============================================================ -->
<!-- OPTICAL LAB — SOTA result-first -->
<!-- ============================================================ -->
<section id="optics-lab" class="py-16 bg-slate-950 text-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-8"><span class="chip bg-white/10 text-amber-200 mb-3">Optical Decision Lab · result-first</span><h3 class="text-3xl md:text-4xl font-bold mb-3">Parte del resultado, no del número</h3><p class="text-slate-300 max-w-3xl mx-auto">Presets de intención + near/focus/far + comparación A/B. La banda verde representa la zona de nitidez aceptable calculada; el desenfoque del fondo depende además de cuánto se separa detrás del sujeto.</p></div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="rounded-2xl bg-slate-900 border border-slate-700 p-4 sm:p-6">
        <svg id="optics-svg" viewBox="0 0 600 430" class="w-full" aria-label="Visualización de campo de visión y profundidad de campo">
          <rect width="600" height="430" rx="20" fill="#08111f"/><polygon id="opt-cone" points="300,395 80,55 520,55" fill="#3b82f6" opacity=".15" stroke="#60a5fa" stroke-width="2"/>
          <line x1="300" y1="395" x2="300" y2="35" stroke="#93c5fd" stroke-dasharray="7 7"/>
          <rect id="opt-dof-band" class="opt-dof-band" x="80" y="120" width="440" height="150" rx="8"/><line id="opt-near-line" class="opt-nearfar" x1="95" x2="505" y1="270" y2="270"/><line id="opt-focus-line" class="opt-focus-line" x1="95" x2="505" y1="250" y2="250"/><line id="opt-far-line" class="opt-nearfar" x1="95" x2="505" y1="120" y2="120"/>
          <line id="opt-bg-line" class="opt-bg-line" x1="85" x2="515" y1="55" y2="55"/><text id="opt-bg-label" x="300" y="43" fill="#cbd5e1" text-anchor="middle" font-size="13">fondo</text>
          <circle id="opt-subject" class="opt-subject-marker" cx="300" cy="250" r="13"/><text id="opt-subject-label" x="320" y="247" fill="white" font-size="13">focus</text>
          <text id="opt-near-label" x="105" y="282" class="opt-axis-label">near</text><text id="opt-far-label" x="105" y="113" class="opt-axis-label">far</text>
          <g transform="translate(270 382)"><rect width="60" height="32" rx="5" fill="white"/><circle cx="30" cy="16" r="9" fill="#0f172a"/></g>
        </svg>
        <div class="sota-card mt-4 bg-slate-800 border-slate-700 text-white"><div class="sota-kicker text-amber-300">A/B · misma posición vs mismo encuadre</div><div id="opt-ab" class="text-xs text-slate-200 leading-relaxed mt-2"></div></div>
      </div>
      <div class="rounded-2xl bg-white text-slate-900 p-5 sm:p-6">
        <div class="sota-kicker mb-2">1 · ELIGE INTENCIÓN</div>
        <div class="opt-preset-row mb-5" id="opt-presets">
          <button class="sota-btn" data-opt-preset="deep">🏞️ Todo legible</button><button class="sota-btn" data-opt-preset="portrait">🎯 Fondo cremoso</button><button class="sota-btn" data-opt-preset="action">❄️ Acción</button><button class="sota-btn" data-opt-preset="zoom">🔭 Zoom burst</button>
        </div>
        <div class="sota-kicker mb-2">2 · CALIBRA</div>
        <div class="grid gap-4">
          <label class="text-sm font-bold">Lente<select id="opt-lens" class="mt-2 w-full border rounded-xl p-3 bg-white"><option value="35" data-min="2">35mm f/2</option><option value="50" data-min="1.8">50mm f/1.8</option><option value="85" data-min="1.8" selected>85mm f/1.8</option><option value="80" data-min="5.6">zoom @80mm f/5.6</option></select></label>
          <label class="text-sm font-bold">Cámara→sujeto <b id="opt-dist-v">3.0 m</b><input id="opt-dist" type="range" min="1.5" max="12" step="0.25" value="3" class="w-full mt-2"></label>
          <label class="text-sm font-bold">Apertura <b id="opt-ap-v">f/1.8</b><input id="opt-ap" type="range" min="1.8" max="16" step="0.1" value="1.8" class="w-full mt-2"></label>
          <label class="text-sm font-bold">Sujeto→fondo <b id="opt-bg-v">8 m</b><input id="opt-bg" type="range" min="1" max="25" step="0.5" value="8" class="w-full mt-2"></label>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-5"><div class="bg-blue-50 p-3 rounded-xl"><div id="opt-fov" class="font-black text-xl">—</div><div class="text-[10px] text-slate-500">FoV H</div></div><div class="bg-purple-50 p-3 rounded-xl"><div id="opt-width" class="font-black text-xl">—</div><div class="text-[10px] text-slate-500">ancho cuadro</div></div><div class="bg-emerald-50 p-3 rounded-xl"><div id="opt-dof" class="font-black text-sm">—</div><div class="text-[10px] text-slate-500">near→far</div></div><div class="bg-amber-50 p-3 rounded-xl"><div id="opt-hyper" class="font-black text-sm">—</div><div class="text-[10px] text-slate-500">hiperfocal</div></div></div>
        <p id="opt-lesson" class="mt-4 text-xs leading-relaxed text-slate-700 bg-slate-50 rounded-xl p-4"></p>
      </div>
    </div>
  </div>
</section>

'''
HTML=replace_between(HTML,'<!-- OPTICAL LAB — recovered from v1, rebuilt -->','<!-- ============================================================ -->\n<!-- GLOBAL TOGGLES (sticky) -->',OPTICS+'<!-- ============================================================ -->\n<!-- GLOBAL TOGGLES (sticky) -->')

MOTION='''
<!-- SOTA_MOTION_LAB_START -->
<section id="motion-lab" class="py-16 bg-gradient-to-b from-white to-slate-50 border-y border-slate-200">
 <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="text-center mb-9"><span class="chip bg-rose-100 text-rose-700 mb-3">Temporal Motion Lab</span><h3 class="text-3xl md:text-4xl font-bold mb-3">El obturador dibuja tiempo</h3><p class="text-slate-600 max-w-3xl mx-auto">Compara cómo cambia la huella temporal al variar velocidad, movimiento y seguimiento. Es un estimador pedagógico de tendencia, no un exposímetro ni una simulación óptica pixel-perfect.</p></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
   <div class="motion-stage" id="motion-stage" aria-label="Simulación conceptual de movimiento"><div class="motion-bg-lines" id="motion-bg-lines"></div><div class="motion-road"></div><div class="motion-trail" id="motion-trail"></div><div class="motion-light" id="motion-light" hidden></div><div class="motion-radial" id="motion-radial" hidden></div><div class="motion-ghost" id="motion-ghost" hidden></div><div class="motion-subject" id="motion-subject"></div><div class="motion-caption" id="motion-caption"></div></div>
   <div class="sota-card">
    <div class="sota-kicker">EFECTO</div><div id="motion-modes" class="sota-actions mt-2 mb-5"><button class="sota-btn is-active" data-motion="freeze">Congelado</button><button class="sota-btn" data-motion="pan">Barrido</button><button class="sota-btn" data-motion="ghost">Fantasma</button><button class="sota-btn" data-motion="trails">Trazas</button><button class="sota-btn" data-motion="paint">Lightpaint</button><button class="sota-btn" data-motion="zoom">Zooming</button></div>
    <label class="block text-sm font-bold mb-4">Exposición <b id="motion-shutter-v">1/2000 s</b><input id="motion-shutter" type="range" min="0" max="100" value="5" class="w-full mt-2"></label>
    <label class="block text-sm font-bold mb-4">Movimiento relativo <b id="motion-speed-v">rápido</b><input id="motion-speed" type="range" min="1" max="10" value="7" class="w-full mt-2"></label>
    <label class="block text-sm font-bold">Calidad de seguimiento <b id="motion-track-v">80%</b><input id="motion-track" type="range" min="0" max="100" value="80" class="w-full mt-2"></label>
    <div class="sota-grid3 mt-5"><div class="sota-card"><div id="motion-span" class="sota-metric">—<small>huella relativa</small></div></div><div class="sota-card"><div id="motion-risk" class="sota-metric">—<small>riesgo de blur</small></div></div><div class="sota-card"><div id="motion-target" class="sota-metric">—<small>baseline</small></div></div></div>
    <p id="motion-lesson" class="text-xs leading-relaxed text-slate-600 mt-4 bg-slate-50 rounded-xl p-3"></p>
   </div>
  </div>
 </div>
</section>
<!-- SOTA_MOTION_LAB_END -->
'''
HTML=re.sub(r'(<!-- ============================================================ -->\s*<!-- COMPOSITION RULES GUIDE -->)',MOTION+r'\n\1',HTML,count=1)

COMP='''
<!-- SOTA_COMPOSITION_LAB_START -->
<section id="composition-lab" class="py-16 bg-white">
 <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="text-center mb-9"><span class="chip bg-violet-100 text-violet-700 mb-3">Composition Sandbox</span><h3 class="text-3xl md:text-4xl font-bold mb-3">Mueve el sujeto y prueba la intención</h3><p class="text-slate-600 max-w-3xl mx-auto">Toca o arrastra dentro del frame 3:2 y enciende overlays. El objetivo no es “obedecer reglas”, sino ver cómo cambian balance, tensión, dirección y espacio negativo.</p></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
    <div class="comp-stage" id="comp-stage" tabindex="0" aria-label="Lienzo interactivo de composición. Usa flechas para mover el sujeto."><div id="comp-third" class="comp-grid-third"></div><div id="comp-center" class="comp-center" hidden></div><div id="comp-frame" class="comp-frame" hidden></div><div id="comp-leading" class="comp-leading" hidden></div><div class="comp-neg">espacio negativo</div><div id="comp-subject" class="comp-subject" role="img" aria-label="Sujeto"></div></div>
    <div class="sota-card"><div class="sota-kicker">OVERLAYS</div><div class="sota-actions mt-2" id="comp-controls"><button class="sota-btn is-active" data-comp="third">Tercios</button><button class="sota-btn" data-comp="center">Simetría</button><button class="sota-btn" data-comp="frame">Enmarcado</button><button class="sota-btn" data-comp="leading">Perspectiva</button></div><div class="sota-grid2 mt-5"><div class="sota-card"><div class="sota-kicker">POSICIÓN</div><div id="comp-pos" class="font-black text-xl mt-1">66%, 67%</div></div><div class="sota-card"><div class="sota-kicker">LECTURA</div><div id="comp-reading" class="text-sm font-bold mt-1">Tercio inferior derecho</div></div></div><p id="comp-lesson" class="text-xs text-slate-600 leading-relaxed mt-4 bg-slate-50 rounded-xl p-3">Prueba primero un tercio; luego centra el sujeto y enciende simetría. Si la imagen mejora al centrar, la simetría está sirviendo mejor que la regla de tercios.</p></div>
  </div>
 </div>
</section>
<!-- SOTA_COMPOSITION_LAB_END -->
'''
HTML=re.sub(r'(<!-- ============================================================ -->\s*<!-- CAMERA ANGLES GUIDE -->)',COMP+r'\n\1',HTML,count=1)

# Session run dialog and launcher.
RUN_DIALOG='''
<!-- SOTA_SESSION_RUN_START -->
<dialog id="session-run-dialog" aria-labelledby="run-title">
 <div class="run-head"><div><div class="text-[10px] tracking-[.18em] uppercase text-emerald-300 font-black">SESSION RUN</div><strong id="run-title">Toma 1/10</strong></div><button type="button" class="sota-btn" onclick="closeSessionRun()" aria-label="Cerrar Session Run">✕</button></div>
 <div class="run-body"><div class="run-progress mb-4"><div id="run-progress-bar" style="width:0%"></div></div><div id="run-content"></div><div class="run-footer"><button id="run-prev" class="sota-btn">← Anterior</button><button id="run-done" class="sota-btn sota-btn-gold">✓ Marcar</button><button id="run-next" class="sota-btn sota-btn-dark">Siguiente →</button></div></div>
</dialog>
<!-- SOTA_SESSION_RUN_END -->
'''
HTML=HTML.replace('<div id="field-card-modal"',RUN_DIALOG+'\n<div id="field-card-modal"',1)
# Desktop header button beside Field.
HTML=HTML.replace('<button type="button" onclick="openFieldCard()" title="Field Card"', '<button type="button" onclick="openSessionRun()" title="Session Run" class="px-2 sm:px-3 py-1.5 sm:py-2 text-[10px] sm:text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition whitespace-nowrap">▶ Run</button>\n        <button type="button" onclick="openFieldCard()" title="Field Card"',1)
# Mobile bottom nav: add Run.
HTML=HTML.replace('<button type="button" onclick="openFieldCard()"><span class="ico">📋</span><span>Field</span></button>', '<button type="button" onclick="openSessionRun()"><span class="ico">▶️</span><span>Run</span></button>\n  <button type="button" onclick="openFieldCard()"><span class="ico">📋</span><span>Field</span></button>',1)

# Replace old optical JS block up to DOM listener.
NEW_JS=r'''
// ---- SOTA labs + session run ----
function initOpticsLab(){
 const lens=document.getElementById('opt-lens'),dist=document.getElementById('opt-dist'),ap=document.getElementById('opt-ap'),bg=document.getElementById('opt-bg');if(!lens||!dist||!ap||!bg)return;
 const coc=.03,sw=35.8,maxScene=30;
 const presets={deep:{lens:'35',dist:4,ap:11,bg:10},portrait:{lens:'85',dist:3,ap:1.8,bg:8},action:{lens:'85',dist:7,ap:2.8,bg:10},zoom:{lens:'80',dist:6,ap:8,bg:12}};
 function yFor(m){return 395-Math.min(maxScene,Math.max(0,m))/maxScene*340}
 function update(){
  const opt=lens.selectedOptions[0],f=+lens.value,min=+opt.dataset.min,d=+dist.value,b=+bg.value;ap.min=min;if(+ap.value<min)ap.value=min;const N=+ap.value;
  const fov=2*Math.atan(sw/(2*f))*180/Math.PI,width=2*d*Math.tan(fov*Math.PI/360),H=(f*f)/(N*coc)+f,s=d*1000,near=(H*s)/(H+s-f)/1000,far=s<H?(H*s)/(H-(s-f))/1000:Infinity,bgAbs=d+b;
  document.getElementById('opt-dist-v').textContent=d.toFixed(2)+' m';document.getElementById('opt-ap-v').textContent='f/'+N.toFixed(1);document.getElementById('opt-bg-v').textContent=b.toFixed(1)+' m';document.getElementById('opt-fov').textContent=fov.toFixed(1)+'°';document.getElementById('opt-width').textContent=width.toFixed(2)+' m';document.getElementById('opt-dof').textContent=Number.isFinite(far)?near.toFixed(2)+'–'+far.toFixed(2)+' m':near.toFixed(2)+'m–∞';document.getElementById('opt-hyper').textContent=(H/1000).toFixed(2)+' m';
  const coneHalf=maxScene*Math.tan(fov*Math.PI/360)*(340/maxScene);document.getElementById('opt-cone').setAttribute('points',`300,395 ${300-coneHalf},55 ${300+coneHalf},55`);
  const sy=yFor(d),ny=yFor(near),fy=yFor(Number.isFinite(far)?far:maxScene),by=yFor(bgAbs);const subject=document.getElementById('opt-subject');subject.setAttribute('cy',sy);document.getElementById('opt-subject-label').setAttribute('y',sy-8);['opt-focus-line'].forEach(id=>{const e=document.getElementById(id);e.setAttribute('y1',sy);e.setAttribute('y2',sy)});const nl=document.getElementById('opt-near-line');nl.setAttribute('y1',ny);nl.setAttribute('y2',ny);const fl=document.getElementById('opt-far-line');fl.setAttribute('y1',fy);fl.setAttribute('y2',fy);const band=document.getElementById('opt-dof-band');band.setAttribute('y',Math.min(ny,fy));band.setAttribute('height',Math.abs(ny-fy));const bl=document.getElementById('opt-bg-line');bl.setAttribute('y1',by);bl.setAttribute('y2',by);document.getElementById('opt-bg-label').setAttribute('y',Math.max(15,by-7));document.getElementById('opt-near-label').setAttribute('y',ny+13);document.getElementById('opt-near-label').textContent='near '+near.toFixed(2)+'m';document.getElementById('opt-far-label').setAttribute('y',Math.max(14,fy-6));document.getElementById('opt-far-label').textContent='far '+(Number.isFinite(far)?far.toFixed(2)+'m':'∞');
  const referenceWidth=2*3*Math.tan(2*Math.atan(sw/(2*85))/2);const sameFrameDist=referenceWidth/(2*Math.tan(fov*Math.PI/360));document.getElementById('opt-ab').innerHTML=`<b>Misma posición (${d.toFixed(1)}m):</b> ${f}mm encuadra ${width.toFixed(2)}m de ancho. <br><b>Mismo encuadre que un 85mm a 3m:</b> con ${f}mm tendrías que situarte aprox. a ${sameFrameDist.toFixed(1)}m; ese cambio de posición sí cambia la perspectiva.`;
  document.getElementById('opt-lesson').innerHTML=`<strong>Resultado:</strong> foco a ${d.toFixed(2)}m; zona DoF ≈ ${Number.isFinite(far)?near.toFixed(2)+'–'+far.toFixed(2)+'m':near.toFixed(2)+'m–∞'}. Fondo real ≈ ${bgAbs.toFixed(1)}m desde cámara. ${bgAbs>(Number.isFinite(far)?far:d+1)?'El fondo está detrás del límite lejano y la separación favorece aislamiento.':'El fondo está relativamente cerca de la zona enfocada: sepáralo más si buscas bokeh.'}`;
 }
 document.getElementById('opt-presets')?.addEventListener('click',e=>{const btt=e.target.closest('[data-opt-preset]');if(!btt)return;const p=presets[btt.dataset.optPreset];lens.value=p.lens;dist.value=p.dist;ap.value=p.ap;bg.value=p.bg;document.querySelectorAll('[data-opt-preset]').forEach(x=>x.setAttribute('aria-pressed',x===btt?'true':'false'));update()});
 [lens,dist,ap,bg].forEach(el=>el.addEventListener('input',update));lens.addEventListener('change',update);update();
}
function initMotionLab(){
 const modeBox=document.getElementById('motion-modes'),sh=document.getElementById('motion-shutter'),speed=document.getElementById('motion-speed'),track=document.getElementById('motion-track');if(!modeBox||!sh)return;let mode='freeze';
 const specs={freeze:{base:'1/2000 s',secs:.0005,lesson:'Congelado: el éxito exige que la huella durante la exposición sea mínima.'},pan:{base:'1/40 s',secs:.025,lesson:'Barrido: el seguimiento reduce movimiento relativo del sujeto, mientras el fondo barre.'},ghost:{base:'1 s',secs:1,lesson:'Fantasma: cámara/fondo fijos; el sujeto ocupa muchas posiciones durante la exposición.'},trails:{base:'5–15 s',secs:8,lesson:'Trazas: fuentes de luz móviles integran una trayectoria continua con cámara inmóvil.'},paint:{base:'10 s',secs:10,lesson:'Lightpainting: la linterna es el sujeto móvil; el entorno permanece oscuro y fijo.'},zoom:{base:'2 s',secs:2,lesson:'Zooming: la cámara no se traslada; cambia la focal durante la exposición alrededor de un centro fuerte.'}};
 function secs(){const p=+sh.value/100;return .00025*Math.pow(80000,p)}
 function fmt(v){return v<.01?'1/'+Math.round(1/v)+' s':v<1?v.toFixed(2)+' s':v.toFixed(1)+' s'}
 function update(){const t=secs(),v=+speed.value,q=+track.value/100,relative=mode==='pan'?v*(1-q):v,raw=relative*t/.025,span=Math.min(100,Math.max(1,18*Math.log2(1+raw)));document.getElementById('motion-shutter-v').textContent=fmt(t);document.getElementById('motion-speed-v').textContent=v<4?'lento':v<7?'medio':'rápido';document.getElementById('motion-track-v').textContent=Math.round(q*100)+'%';document.getElementById('motion-span').innerHTML=Math.round(span)+'%<small>huella relativa</small>';document.getElementById('motion-risk').innerHTML=(span<12?'bajo':span<48?'medio':'alto')+'<small>riesgo de blur</small>';document.getElementById('motion-target').innerHTML=specs[mode].base+'<small>baseline</small>';document.getElementById('motion-lesson').textContent=specs[mode].lesson+' La escala visual es logarítmica para que exposiciones cortas y largas sigan siendo comparables; el modelo enseña tendencia, no predice píxeles ni exposición.';document.getElementById('motion-caption').textContent=`${mode.toUpperCase()} · ${fmt(t)} · movimiento ${v}/10 · seguimiento ${Math.round(q*100)}%`;
  const trail=document.getElementById('motion-trail'),ghost=document.getElementById('motion-ghost'),light=document.getElementById('motion-light'),rad=document.getElementById('motion-radial'),sub=document.getElementById('motion-subject'),bgLines=document.getElementById('motion-bg-lines');trail.hidden=!['freeze','pan'].includes(mode);ghost.hidden=mode!=='ghost';light.hidden=!['trails','paint'].includes(mode);rad.hidden=mode!=='zoom';sub.hidden=['trails','paint','zoom'].includes(mode);trail.style.width=(20+span*2.1)+'px';trail.style.opacity=span/110+.15;ghost.style.filter=`blur(${Math.min(20,span/4)}px)`;ghost.style.opacity=Math.max(.15,.85-span/130);bgLines.style.filter=mode==='pan'?`blur(${Math.min(14,(v*q)*1.4)}px)`:'none';rad.style.opacity=Math.min(.9,.2+t/3);
 }
 modeBox.addEventListener('click',e=>{const b=e.target.closest('[data-motion]');if(!b)return;mode=b.dataset.motion;modeBox.querySelectorAll('button').forEach(x=>x.classList.toggle('is-active',x===b));const target=specs[mode].secs;const p=Math.log(target/.00025)/Math.log(80000);sh.value=Math.max(0,Math.min(100,p*100));if(mode==='pan')track.value=85;else track.value=0;update()});[sh,speed,track].forEach(x=>x.addEventListener('input',update));update();
}
function initCompositionLab(){const stage=document.getElementById('comp-stage'),subject=document.getElementById('comp-subject'),controls=document.getElementById('comp-controls');if(!stage||!subject)return;let x=.666,y=.666;function render(){subject.style.left=(x*100)+'%';subject.style.top=(y*100)+'%';document.getElementById('comp-pos').textContent=Math.round(x*100)+'%, '+Math.round(y*100)+'%';const horiz=x<.4?'izquierdo':x>.6?'derecho':'central',vert=y<.4?'superior':y>.6?'inferior':'central';document.getElementById('comp-reading').textContent=(horiz==='central'&&vert==='central')?'Centro / simetría':`Tercio ${vert} ${horiz}`}
 function setFromEvent(e){const r=stage.getBoundingClientRect();x=Math.max(.06,Math.min(.94,(e.clientX-r.left)/r.width));y=Math.max(.1,Math.min(.9,(e.clientY-r.top)/r.height));render()};stage.addEventListener('pointerdown',e=>{stage.setPointerCapture?.(e.pointerId);setFromEvent(e)});stage.addEventListener('pointermove',e=>{if(e.buttons) setFromEvent(e)});stage.addEventListener('keydown',e=>{const d=e.shiftKey?.05:.02;if(e.key==='ArrowLeft')x-=d;else if(e.key==='ArrowRight')x+=d;else if(e.key==='ArrowUp')y-=d;else if(e.key==='ArrowDown')y+=d;else return;e.preventDefault();x=Math.max(.06,Math.min(.94,x));y=Math.max(.1,Math.min(.9,y));render()});controls.addEventListener('click',e=>{const b=e.target.closest('[data-comp]');if(!b)return;const id='comp-'+b.dataset.comp,el=document.getElementById(id),on=el.hasAttribute('hidden');el.toggleAttribute('hidden',!on);b.classList.toggle('is-active',on)});render();}
const RUN_CRITERIA={mucha_pdc:'✓ primer plano + sujeto + fondo legibles',poca_pdc:'✓ ojo/detalle crítico nítido + fondo claramente separado',congelado:'✓ cara/ojos y extremidades detenidos',barrido:'✓ sujeto reconocible + fondo direccional',fantasma:'✓ fondo inmóvil + persona semitransparente',lightpainting:'✓ trazo limpio + cámara inmóvil',larga_exp:'✓ trazas continuas + altas luces controladas',zooming:'✓ centro legible + rayos radiales'};
let runIndex=0,runLastTrigger=null;const RUN_MEMORY={};
function runKey(){return `canon6d-run-${currentPlan}-${currentVariant}`}
function runState(){const k=runKey();if(RUN_MEMORY[k])return [...RUN_MEMORY[k]];try{const s=JSON.parse(localStorage.getItem(k)||'[]');RUN_MEMORY[k]=s;return [...s]}catch(e){return []}}
function saveRun(s){const k=runKey();RUN_MEMORY[k]=[...s];try{localStorage.setItem(k,JSON.stringify(s))}catch(e){}}
function renderSessionRun(){const dlg=document.getElementById('session-run-dialog'),plan=PLANS_DATA.plans.find(p=>p.id===currentPlan);if(!dlg||!plan)return;runIndex=Math.max(0,Math.min(plan.shots.length-1,runIndex));const shot=plan.shots[runIndex],ts=shot.settings_by_time[currentTime],b=baselineForShot(plan,shot),sv=effectiveSubjectForShot(shot),state=runState(),done=!!state[runIndex],path=`diagrams/${plan.id}_${shot.id}_${currentVariant}.png`;document.getElementById('run-title').textContent=`${plan.id.replace('plan_','').toUpperCase()} · ${runIndex+1}/10 · ${shot.technique_label}`;document.getElementById('run-progress-bar').style.width=((state.filter(Boolean).length/10)*100)+'%';document.getElementById('run-content').innerHTML=`<div class="run-current"><div><img class="run-diagram" loading="eager" decoding="async" src="${assetUrl(path)}" alt="Diagrama ${shot.technique_label}"><div class="sota-kicker mt-3">SUJETO</div><div class="text-sm font-bold">${sv.label}</div><div class="run-delta">${sv.data?.action||sv.safety||''}</div></div><div><div class="sota-kicker">PLAN · ${currentTime}</div><div class="sota-grid2 mt-2"><div class="sota-card"><b>${ts.lens}</b><div class="run-delta">lente</div></div><div class="sota-card"><b>${ts.aperture}</b><div class="run-delta">apertura</div></div><div class="sota-card"><b>${ts.shutter}</b><div class="run-delta">obturador</div></div><div class="sota-card"><b>ISO ${ts.iso}</b><div class="run-delta">sensibilidad</div></div></div>${b?`<div class="run-baseline mt-3"><b>Field baseline:</b> ${b.lens} · ${b.aperture} · ${b.shutter} · ISO ${b.iso}<br>${b.af}<br>${b.geometry}</div>`:''}<div class="sota-card mt-3"><div class="sota-kicker">APRUEBA SI</div><b>${RUN_CRITERIA[shot.technique]||'✓ intención visual conseguida'}</b></div><p class="text-xs text-slate-600 mt-3">${ts.notes}</p></div></div>`;const doneBtn=document.getElementById('run-done');doneBtn.classList.toggle('run-done',done);doneBtn.textContent=done?'✓ Hecha':'✓ Marcar';document.getElementById('run-prev').disabled=runIndex===0;document.getElementById('run-next').disabled=runIndex===9;}
function openSessionRun(){const d=document.getElementById('session-run-dialog');if(!d)return;runLastTrigger=document.activeElement;renderSessionRun();d.showModal();}
function closeSessionRun(){const d=document.getElementById('session-run-dialog');if(d?.open)d.close();runLastTrigger?.focus?.()}
function initSessionRun(){const d=document.getElementById('session-run-dialog');if(!d)return;document.getElementById('run-prev').addEventListener('click',()=>{runIndex--;renderSessionRun()});document.getElementById('run-next').addEventListener('click',()=>{runIndex++;renderSessionRun()});document.getElementById('run-done').addEventListener('click',()=>{const s=runState();s[runIndex]=!s[runIndex];saveRun(s);renderSessionRun()});d.addEventListener('close',()=>runLastTrigger?.focus?.());}
function initAccessibleFieldCard(){const m=document.getElementById('field-card-modal');if(!m)return;let last=null;window.openFieldCard=function(){last=document.activeElement;m.classList.add('fc-modal-open');m.setAttribute('aria-hidden','false');document.body.classList.add('fc-modal-lock');const first=m.querySelector('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])');setTimeout(()=>first?.focus(),0)};window.closeFieldCard=function(){m.classList.remove('fc-modal-open');m.setAttribute('aria-hidden','true');document.body.classList.remove('fc-modal-lock');last?.focus?.()};m.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();closeFieldCard();return}if(e.key!=='Tab')return;const f=[...m.querySelectorAll('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(x=>!x.disabled&&x.offsetParent!==null);if(!f.length)return;const first=f[0],lastEl=f[f.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();lastEl.focus()}else if(!e.shiftKey&&document.activeElement===lastEl){e.preventDefault();first.focus()}});}
document.addEventListener('DOMContentLoaded',()=>{initOpticsLab();initMotionLab();initCompositionLab();initSessionRun();initAccessibleFieldCard()});
'''
# Remove legacy optics init block and field open/close/escape definitions only; keep field card state IIFE.
HTML=re.sub(r'function openFieldCard\(\).*?document\.addEventListener\(\'keydown\',e=>\{if\(e\.key===\'Escape\'\)closeFieldCard\(\)\}\);\s*','',HTML,flags=re.S)
HTML=re.sub(r'// ---- Optical Lab \(v1 feature restored, physically constrained\) ----.*?document\.addEventListener\("DOMContentLoaded",initOpticsLab\);',NEW_JS,HTML,flags=re.S)

# Ensure dynamic images have browser-native hints.
HTML=HTML.replace('<img src="${assetUrl(diagramPath)}" alt=', '<img loading="lazy" decoding="async" src="${assetUrl(diagramPath)}" alt=')

INDEX.write_text(HTML,encoding='utf-8')
print('SOTA enhancements applied to',INDEX)
import subprocess, sys
subprocess.run([sys.executable, str(ROOT/'scripts'/'finalize_sota_interactions.py')], check=True)
# Detail modal recovery is applied in the release source after this upgrade script; see index.html canonical SOTA block.
