"""Idempotent Optical Decision Lab v2 + outdoor/readability accessibility pass."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "index.html"
html = path.read_text(encoding="utf-8")
html = html.replace('https://www.cambridgeincolour.com/tutorials/telephoto-lenses.htm" target="_blank" rel="noopener">Cambridge in Colour · viewpoint vs “compression”', 'https://files.canon-europe.com/files/webcontent/rf-lens-world/knowledge/perspective/index.html" target="_blank" rel="noopener">Canon · Perspectiva y focal')

# One-time repair for files produced by the former Field Card embedder, whose
# broad cleanup could erase the bounded SOTA lab script. The hosted build is a
# deterministic copy and provides a safe local recovery source.
if 'function initOpticsLab()' not in html:
    snapshot = ROOT / 'dist' / 'canon6d_sota_hosted' / 'index.html'
    if snapshot.exists():
        prior = snapshot.read_text(encoding='utf-8')
        recovered = re.search(r'// ---- SOTA labs \+ session run ----.*?(?=\n</script>)', prior, re.S)
        marker = '<script>\n<!-- FIELD CARD JS START -->'
        if recovered and marker in html:
            html = html.replace(marker, '<script>\n' + recovered.group(0) + '\n</script>\n' + marker, 1)

LAB = r'''<!-- OPTICAL_DECISION_LAB_V2_START -->
<section id="optics-lab" class="py-16 bg-slate-950 text-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-8"><span class="chip optics-chip mb-3">Optical Decision Lab · geometría dinámica</span><h3 class="text-3xl md:text-4xl font-bold mb-3">Decide por resultado; comprueba la geometría</h3><p class="optics-intro max-w-3xl mx-auto">Canon confirma que focal, apertura, distancia de enfoque y separación del fondo influyen en la profundidad de campo. Este laboratorio separa medidas geométricas calculadas de una previsualización pedagógica del desenfoque.</p></div>
    <div class="optics-layout">
      <div class="optics-visual-card">
        <svg id="optics-svg" viewBox="0 0 640 470" role="img" aria-labelledby="opt-svg-title opt-svg-desc" tabindex="0">
          <title id="opt-svg-title">Campo de visión y profundidad de campo</title><desc id="opt-svg-desc">Diagrama dinámico en escala logarítmica desde la cámara hasta el fondo.</desc>
          <defs><pattern id="opt-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#334155" stroke-width="1"/></pattern></defs>
          <rect width="640" height="470" rx="20" fill="#071421"/><rect x="42" y="34" width="556" height="382" fill="url(#opt-grid)" opacity=".65"/>
          <g id="opt-axis-ticks" aria-hidden="true"></g>
          <polygon id="opt-cone" points="320,416 70,40 570,40" fill="#2563eb" opacity=".22" stroke="#93c5fd" stroke-width="3"/>
          <polygon id="opt-dof-band" class="opt-dof-band" points="120,250 520,250 570,90 70,90"/>
          <line id="opt-near-line" class="opt-nearfar" x1="90" x2="550" y1="280" y2="280"/><line id="opt-focus-line" class="opt-focus-line" x1="90" x2="550" y1="220" y2="220"/><line id="opt-far-line" class="opt-nearfar" x1="90" x2="550" y1="100" y2="100"/>
          <line id="opt-bg-line" class="opt-bg-line" x1="72" x2="568" y1="55" y2="55"/>
          <text id="opt-bg-label" x="430" y="48" class="opt-label">FONDO</text><text id="opt-near-label" x="92" y="274" class="opt-label">NEAR</text><text id="opt-far-label" x="92" y="94" class="opt-label">FAR</text>
          <circle id="opt-subject" class="opt-subject-marker" cx="320" cy="220" r="14"/><text id="opt-subject-label" x="340" y="214" class="opt-label opt-label-focus">FOCO</text>
          <g transform="translate(288 409)" aria-hidden="true"><rect width="64" height="34" rx="6" fill="#fff"/><circle cx="32" cy="17" r="10" fill="#0f172a"/></g>
          <text x="320" y="460" text-anchor="middle" class="opt-scale-note">Escala logarítmica de distancia · no escala física de tamaño</text>
        </svg>
        <div class="optics-legend" aria-label="Leyenda"><span><i class="legend-fov"></i>FoV</span><span><i class="legend-dof"></i>DoF aceptable</span><span><i class="legend-focus"></i>Foco</span><span><i class="legend-bg"></i>Fondo</span></div>
        <div class="optics-preview" aria-label="Previsualización pedagógica de separación"><div class="preview-scene"><div id="opt-preview-bg" class="preview-background"></div><div class="preview-person" aria-hidden="true"></div><span>Previsualización conceptual</span></div><div><div class="optics-kicker">DISCO DE DESENFOQUE ESTIMADO</div><strong id="opt-blur">—</strong><p id="opt-blur-note">Modelo de lente delgada; no simula bokeh, aberraciones, luz ni exposición.</p></div></div>
        <div class="optics-ab"><div class="optics-kicker">A/B · POSICIÓN Y PERSPECTIVA</div><div id="opt-ab"></div></div>
      </div>
      <div class="optics-control-card">
        <div class="optics-kicker">1 · ELIGE LA INTENCIÓN</div>
        <div class="opt-preset-row" id="opt-presets"><button class="sota-btn" data-opt-preset="deep" aria-pressed="false">🏞️ Todo legible</button><button class="sota-btn" data-opt-preset="portrait" aria-pressed="true">🎯 Fondo cremoso</button><button class="sota-btn" data-opt-preset="action" aria-pressed="false">❄️ Acción</button><button class="sota-btn" data-opt-preset="zoom" aria-pressed="false">🔭 Zoom burst</button></div>
        <div class="optics-kicker optics-step">2 · AJUSTA UNA VARIABLE</div>
        <div class="optics-controls">
          <label>Lente y focal<select id="opt-lens"><option value="35" data-min="2">EF 35mm f/2</option><option value="50" data-min="1.8">EF 50mm f/1.8</option><option value="85" data-min="1.8" selected>EF 85mm f/1.8</option><option value="35" data-min="4">EF 35–80 @35mm f/4</option><option value="50" data-min="4.5">EF 35–80 @50mm f/4.5</option><option value="80" data-min="5.6">EF 35–80 @80mm f/5.6</option></select></label>
          <label>Apertura<select id="opt-ap" aria-describedby="opt-ap-help"></select><small id="opt-ap-help">Sólo pasos utilizables desde la apertura máxima del lente.</small></label>
          <label>Cámara → sujeto <output id="opt-dist-v" for="opt-dist">3.00 m</output><input id="opt-dist" type="range" min="0.9" max="15" step="0.1" value="3"></label>
          <label>Sujeto → fondo <output id="opt-bg-v" for="opt-bg">8.0 m</output><input id="opt-bg" type="range" min="0.5" max="30" step="0.5" value="8"></label>
        </div>
        <div class="optics-metrics" aria-live="polite"><div><output id="opt-fov">—</output><span>FoV horizontal</span></div><div><output id="opt-width">—</output><span>Ancho a foco</span></div><div><output id="opt-dof">—</output><span>Near → far</span></div><div><output id="opt-total">—</output><span>DoF total</span></div><div><output id="opt-split">—</output><span>Frente / detrás</span></div><div><output id="opt-hyper">—</output><span>Hiperfocal</span></div></div>
        <div id="opt-status" class="optics-status" role="status" aria-live="polite"></div>
        <details class="optics-method"><summary>Cómo leer y qué no promete</summary><ul><li><b>FoV/ancho:</b> geometría del sensor 35.8 mm y focal seleccionada.</li><li><b>Near/far/hiperfocal:</b> lente delgada con CoC 0.030 mm, una convención de planificación.</li><li><b>Disco estimado:</b> compara el desenfoque del plano de fondo con ese CoC; no representa calidad estética del bokeh.</li><li><b>Perspectiva:</b> sólo cambia al mover la cámara. Cambiar focal desde el mismo punto cambia encuadre.</li></ul></details>
      </div>
    </div>
  </div>
</section>
<!-- OPTICAL_DECISION_LAB_V2_END -->'''

CSS = r'''
/* ACCESSIBILITY_OUTDOOR_V2_START */
:root{--read-ink:#0b1220;--read-muted:#475569;--read-line:#94a3b8;--focus-ring:#facc15}
body{font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.55;color:var(--read-ink);text-rendering:optimizeLegibility}
.bg-slate-950,.bg-ink{background-color:#0f172a!important}.bg-white{background-color:#fff}.compos-rule-card .text-slate-400{color:#475569!important}.pose-coach-btn span{color:#7c4a00!important}.production-footer .text-slate-500,.production-footer .text-slate-600{color:#cbd5e1!important}
p,li{line-height:1.55}.text-slate-500,.text-slate-600,.sota-muted{color:var(--read-muted)!important}.text-xs{font-size:.8125rem!important}.text-\[10px\]{font-size:.75rem!important}.chip{font-size:.75rem!important;font-weight:800!important}
.border-slate-200,.border-slate-300{border-color:var(--read-line)!important}.diagram-frame,.sota-card,.plan-card,.shot-card{border-width:1.5px!important}
:where(a,button,input,select,summary,[tabindex]):focus-visible{outline:3px solid var(--focus-ring)!important;outline-offset:3px!important;box-shadow:0 0 0 2px #0f172a!important}
input[type=range]{min-height:44px;accent-color:#0f766e}select{min-height:48px;border:2px solid #64748b!important;color:#0b1220;background:#fff}
.visibility-toggle{min-height:44px;border:2px solid #64748b;border-radius:12px;background:#fff;color:#0b1220;padding:.45rem .7rem;font-size:.78rem;font-weight:900}.visibility-toggle[aria-pressed=true]{background:#facc15;color:#111827;border-color:#111827}
body.sun-mode{--read-ink:#000;--read-muted:#1f2937;--read-line:#475569;background:#fff;color:#000;font-weight:500}body.sun-mode .bg-paper,body.sun-mode .bg-white{background:#fff!important}body.sun-mode .shadow-sm,body.sun-mode .sota-card{box-shadow:none!important}body.sun-mode .text-slate-300,body.sun-mode .text-slate-400{color:#f8fafc!important}body.sun-mode .diagram-frame,body.sun-mode .sota-card,body.sun-mode .shot-card,body.sun-mode .plan-card{border-color:#334155!important;border-width:2px!important}
.optics-chip{background:#fef3c7;color:#713f12}.optics-intro{color:#e2e8f0;font-size:1rem;line-height:1.6}.optics-layout{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(360px,.9fr);gap:1.25rem}.optics-visual-card{background:#111e2e;border:2px solid #64748b;border-radius:20px;padding:1rem}.optics-control-card{background:#fff;color:#0b1220;border:2px solid #64748b;border-radius:20px;padding:1.25rem}.optics-kicker{font-size:.75rem;letter-spacing:.12em;font-weight:900;color:#0f766e}.optics-step{margin-top:1.25rem}.optics-controls{display:grid;gap:.85rem;margin-top:.55rem}.optics-controls label{display:grid;gap:.3rem;font-size:.875rem;font-weight:850}.optics-controls output{justify-self:end;margin-top:-1.75rem;font-variant-numeric:tabular-nums}.optics-controls small{color:#475569;font-size:.75rem}.optics-controls input{width:100%}
.optics-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.5rem;margin-top:1rem}.optics-metrics>div{background:#f1f5f9;border:1.5px solid #64748b;border-radius:12px;padding:.7rem;min-width:0}.optics-metrics output{display:block;font-weight:900;font-size:1rem;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.optics-metrics span{display:block;color:#334155;font-size:.7rem;font-weight:800;margin-top:.2rem}.optics-status{margin-top:.8rem;padding:.85rem;border:2px solid #0f766e;border-radius:12px;background:#ecfdf5;color:#064e3b;font-size:.82rem;line-height:1.5}.optics-method{margin-top:.75rem;border:1.5px solid #64748b;border-radius:12px;padding:.7rem}.optics-method summary{font-weight:900}.optics-method ul{margin:.6rem 0 0 1rem;font-size:.78rem;display:grid;gap:.35rem}
#optics-svg{width:100%;height:auto;min-height:300px}.opt-dof-band{fill:#22c55e;fill-opacity:.32;stroke:#86efac;stroke-width:2}.opt-nearfar{stroke:#4ade80;stroke-width:3;stroke-dasharray:8 5}.opt-focus-line{stroke:#fbbf24;stroke-width:4}.opt-bg-line{stroke:#f8fafc;stroke-width:4;stroke-dasharray:4 4}.opt-subject-marker{fill:#fbbf24;stroke:#fff;stroke-width:3}.opt-label{fill:#fff;font-size:13px;font-weight:900;paint-order:stroke;stroke:#071421;stroke-width:4px;stroke-linejoin:round}.opt-label-focus{fill:#fef3c7}.opt-scale-note{fill:#e2e8f0;font-size:12px}.opt-tick{fill:#e2e8f0;font-size:11px;font-weight:800}.opt-tick-line{stroke:#64748b;stroke-width:1.5}.optics-legend{display:flex;flex-wrap:wrap;gap:.75rem;margin:.5rem 0;color:#f8fafc;font-size:.75rem;font-weight:800}.optics-legend span{display:flex;align-items:center;gap:.35rem}.optics-legend i{width:18px;height:5px;border-radius:4px}.legend-fov{background:#93c5fd}.legend-dof{background:#4ade80}.legend-focus{background:#fbbf24}.legend-bg{background:#fff}
.optics-preview{display:grid;grid-template-columns:180px 1fr;gap:.8rem;align-items:center;background:#fff;color:#0b1220;border:2px solid #64748b;border-radius:14px;padding:.7rem}.preview-scene{height:110px;position:relative;overflow:hidden;border:2px solid #475569;border-radius:10px;background:#bfdbfe}.preview-background{position:absolute;inset:0;background:repeating-linear-gradient(90deg,#1e3a8a 0 12px,#dbeafe 12px 24px);transform:scale(1.08)}.preview-person{position:absolute;width:38px;height:72px;bottom:8px;left:50%;transform:translateX(-50%);border-radius:45% 45% 30% 30%;background:#f59e0b;border:3px solid #fff}.preview-person:before{content:"";position:absolute;width:26px;height:26px;left:3px;top:-20px;border-radius:50%;background:#f59e0b;border:3px solid #fff}.preview-scene span{position:absolute;left:5px;bottom:4px;background:#fff;color:#0b1220;padding:2px 5px;border-radius:4px;font-size:.7rem;font-weight:900}.optics-preview strong{font-size:1.2rem}.optics-preview p{font-size:.75rem;color:#334155;margin-top:.2rem}.optics-ab{margin-top:.7rem;background:#071421;border:2px solid #64748b;border-radius:14px;padding:.8rem;color:#f8fafc}.optics-ab .optics-kicker{color:#fde68a}.optics-ab #opt-ab{font-size:.8rem;line-height:1.55;margin-top:.25rem}
.sota-kicker{font-size:.75rem!important}.sota-metric small{font-size:.72rem!important}.hosted-badge{font-size:.7rem!important}@media(max-width:640px){.mobile-bottom-nav a,.mobile-bottom-nav button{font-size:11px!important}}
@media(max-width:900px){.optics-layout{grid-template-columns:1fr}.optics-visual-card{order:2}.optics-control-card{order:1}}@media(max-width:520px){.optics-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.optics-preview{grid-template-columns:1fr}.preview-scene{height:130px}.optics-control-card,.optics-visual-card{padding:.75rem}}
@media(prefers-contrast:more){body{--read-ink:#000;--read-muted:#1f2937;--read-line:#334155}.optics-visual-card,.optics-control-card{border-color:#fff}.opt-dof-band{fill-opacity:.48}}
/* ACCESSIBILITY_OUTDOOR_V2_END */
'''

JS = r'''function initOpticsLab(){
 const lens=document.getElementById('opt-lens'),dist=document.getElementById('opt-dist'),ap=document.getElementById('opt-ap'),bg=document.getElementById('opt-bg');if(!lens||!dist||!ap||!bg)return;
 const coc=.03,sw=35.8,stops=[1.8,2,2.2,2.8,3.2,4,4.5,5.6,6.3,8,9,11,13,16],presets={deep:{lens:'35',index:0,dist:4,ap:11,bg:10},portrait:{lens:'85',index:2,dist:3,ap:1.8,bg:8},action:{lens:'85',index:2,dist:7,ap:2.8,bg:12},zoom:{lens:'80',index:5,dist:6,ap:8,bg:12}};
 const fmt=m=>!Number.isFinite(m)?'∞':m>=10?m.toFixed(1)+' m':m.toFixed(2)+' m';
 function setApertures(wanted){const min=+lens.selectedOptions[0].dataset.min,allowed=stops.filter(x=>x>=min);ap.innerHTML=allowed.map(x=>`<option value="${x}">f/${x}</option>`).join('');const chosen=allowed.reduce((best,x)=>Math.abs(x-wanted)<Math.abs(best-wanted)?x:best,allowed[0]);ap.value=String(chosen)}
 function update(){
  const f=+lens.value,N=+ap.value,d=+dist.value,b=+bg.value,s=d*1000,sb=(d+b)*1000,H=f*f/(N*coc)+f,near=H*s/(H+s-f)/1000,far=s<H?H*s/(H-(s-f))/1000:Infinity,fov=2*Math.atan(sw/(2*f))*180/Math.PI,width=2*d*Math.tan(fov*Math.PI/360),front=d-near,behind=Number.isFinite(far)?far-d:Infinity,total=Number.isFinite(far)?far-near:Infinity;
  const v=f*s/(s-f),vb=f*sb/(sb-f),entrance=f/N,blur=entrance*Math.abs(v-vb)/vb,blurCoc=blur/coc,bgAbs=d+b,sceneMax=Math.max(30,bgAbs*1.12,Number.isFinite(far)?far*1.08:30),minScene=.35;
  const yFor=m=>416-(Math.log(Math.max(minScene,Math.min(sceneMax,m))/minScene)/Math.log(sceneMax/minScene))*376;
  const halfAt=m=>Math.min(278,20+(m/sceneMax)*250*Math.tan(fov*Math.PI/360)/Math.tan(54.2*Math.PI/360));
  const ny=yFor(near),sy=yFor(d),fy=yFor(Number.isFinite(far)?far:sceneMax),by=yFor(bgAbs),nh=halfAt(near),fh=halfAt(Number.isFinite(far)?far:sceneMax),topHalf=Math.min(278,35+250*fov/54.2);
  document.getElementById('opt-cone').setAttribute('points',`320,416 ${320-topHalf},40 ${320+topHalf},40`);document.getElementById('opt-dof-band').setAttribute('points',`${320-nh},${ny} ${320+nh},${ny} ${320+fh},${fy} ${320-fh},${fy}`);
  [['opt-near-line',ny],['opt-focus-line',sy],['opt-far-line',fy],['opt-bg-line',by]].forEach(([id,y])=>{const e=document.getElementById(id);e.setAttribute('y1',y);e.setAttribute('y2',y)});document.getElementById('opt-subject').setAttribute('cy',sy);
  const labels=[['opt-near-label',ny,`NEAR ${fmt(near)}`],['opt-far-label',fy,`FAR ${fmt(far)}`],['opt-bg-label',by,`FONDO ${fmt(bgAbs)}`],['opt-subject-label',sy,`FOCO ${fmt(d)}`]];labels.forEach(([id,y,t])=>{const e=document.getElementById(id);e.setAttribute('y',Math.max(48,Math.min(405,y-7)));e.textContent=t});
  const tickValues=[.5,1,2,3,5,10,20].filter(x=>x<sceneMax);document.getElementById('opt-axis-ticks').innerHTML=tickValues.map(x=>`<line class="opt-tick-line" x1="44" x2="62" y1="${yFor(x)}" y2="${yFor(x)}"/><text class="opt-tick" x="66" y="${yFor(x)+4}">${x}m</text>`).join('');
  document.getElementById('opt-dist-v').textContent=d.toFixed(1)+' m';document.getElementById('opt-bg-v').textContent=b.toFixed(1)+' m';document.getElementById('opt-fov').textContent=fov.toFixed(1)+'°';document.getElementById('opt-width').textContent=width.toFixed(2)+' m';document.getElementById('opt-dof').textContent=fmt(near)+' → '+fmt(far);document.getElementById('opt-total').textContent=fmt(total);document.getElementById('opt-split').textContent=fmt(front)+' / '+fmt(behind);document.getElementById('opt-hyper').textContent=fmt(H/1000);document.getElementById('opt-blur').textContent=blur.toFixed(3)+' mm · '+blurCoc.toFixed(1)+'× CoC';
  document.getElementById('opt-preview-bg').style.filter=`blur(${Math.min(14,Math.max(0,Math.log2(1+blurCoc)*2.2)).toFixed(1)}px)`;
  const relation=!Number.isFinite(far)?'El límite lejano llega a infinito; fondo y horizonte caen dentro de la DoF calculada.':bgAbs>far?'El fondo queda detrás del límite lejano: separación favorable para desenfoque.':'El fondo cae dentro o cerca de la DoF: seguirá relativamente legible.';document.getElementById('opt-status').innerHTML=`<b>Lectura:</b> ${relation} ${blurCoc<1?'El disco estimado es menor que el CoC elegido.':blurCoc<4?'Hay separación moderada del plano de fondo.':'La separación geométrica del fondo es fuerte.'}`;
  const refF=85,refD=3,refWidth=2*refD*Math.tan(2*Math.atan(sw/(2*refF))/2),sameFrame=refWidth/(2*Math.tan(fov*Math.PI/360));document.getElementById('opt-ab').innerHTML=`<b>Misma posición (${d.toFixed(1)} m):</b> ${f} mm muestra ${width.toFixed(2)} m de ancho; cambia el recorte, no la perspectiva geométrica.<br><b>Mismo encuadre que 85 mm a 3 m:</b> con ${f} mm la cámara iría a ≈${sameFrame.toFixed(1)} m; ese desplazamiento sí cambia relaciones de tamaño y perspectiva.`;
  const desc=`${f} milímetros a f ${N}, foco ${fmt(d)}, profundidad de campo desde ${fmt(near)} hasta ${fmt(far)}, fondo a ${fmt(bgAbs)}.`;document.getElementById('opt-svg-desc').textContent=desc;document.getElementById('optics-svg').setAttribute('aria-label',desc);
 }
 lens.addEventListener('change',()=>{setApertures(+ap.value||+lens.selectedOptions[0].dataset.min);update()});[dist,bg].forEach(e=>e.addEventListener('input',update));ap.addEventListener('change',update);document.getElementById('opt-presets').addEventListener('click',e=>{const btn=e.target.closest('[data-opt-preset]');if(!btn)return;const p=presets[btn.dataset.optPreset];lens.selectedIndex=p.index;setApertures(p.ap);dist.value=p.dist;bg.value=p.bg;document.querySelectorAll('[data-opt-preset]').forEach(x=>x.setAttribute('aria-pressed',String(x===btn)));update()});setApertures(1.8);update();
}
function initVisibilityMode(){const b=document.getElementById('visibility-toggle');if(!b)return;let on=false;try{on=localStorage.getItem('canon6d-sun-mode')==='1'}catch(e){};const apply=()=>{document.body.classList.toggle('sun-mode',on);b.setAttribute('aria-pressed',String(on));b.textContent=on?'☀️ Sol: activado':'☀️ Modo sol'};b.addEventListener('click',()=>{on=!on;try{localStorage.setItem('canon6d-sun-mode',on?'1':'0')}catch(e){}apply()});apply()}
'''

# Replace lab between stable section boundaries on the first run; refresh the bounded v2 block later.
if '<!-- OPTICAL_DECISION_LAB_V2_START -->' in html:
    html = re.sub(r'<!-- OPTICAL_DECISION_LAB_V2_START -->.*?<!-- OPTICAL_DECISION_LAB_V2_END -->', LAB, html, count=1, flags=re.S)
else:
    start = html.index('<!-- OPTICAL LAB — SOTA result-first -->')
    start = html.rfind('<!-- ============================================================ -->', 0, start)
    end_marker = '<!-- GLOBAL TOGGLES (sticky) -->'
    end = html.index(end_marker, start)
    end = html.rfind('<!-- ============================================================ -->', start, end)
    html = html[:start] + LAB + '\n\n' + html[end:]

# Replace old function only, preserving subsequent labs.
html, count = re.subn(r'function initOpticsLab\(\)\{.*?function initMotionLab\(\)', JS + '\nfunction initMotionLab()', html, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('Optics JS block not found')

# Insert accessibility CSS once.
html = re.sub(r'<style id="accessibility-outdoor-v2">.*?</style>\s*', '', html, flags=re.S)
html = html.replace('</head>', f'<style id="accessibility-outdoor-v2">{CSS}</style>\n</head>', 1)

# Add visibility control to desktop header, and initialize it.
if 'id="visibility-toggle"' not in html:
    needle = '<button type="button" onclick="openSessionRun()" title="Session Run"'
    html = html.replace(needle, '<button id="visibility-toggle" type="button" class="visibility-toggle" aria-pressed="false">☀️ Modo sol</button>\n        ' + needle, 1)
html = html.replace('initOpticsLab();initMotionLab();', 'initOpticsLab();initVisibilityMode();initMotionLab();', 1)

# Restore Session Run if an older Field Card integrator removed its DOM.
if 'id="session-run-dialog"' not in html:
    run_dialog = '''<!-- SOTA_SESSION_RUN_START -->
<dialog id="session-run-dialog" aria-labelledby="run-title"><div class="run-head"><div><div class="text-[10px] tracking-[.18em] uppercase text-emerald-300 font-black">SESSION RUN</div><strong id="run-title">Toma 1/10</strong></div><button type="button" class="sota-btn" onclick="closeSessionRun()" aria-label="Cerrar Session Run">✕</button></div><div class="run-body"><div class="run-progress mb-4"><div id="run-progress-bar" style="width:0%"></div></div><div id="run-content"></div><div class="run-footer"><button id="run-prev" class="sota-btn">← Anterior</button><button id="run-done" class="sota-btn sota-btn-gold">✓ Marcar</button><button id="run-next" class="sota-btn sota-btn-dark">Siguiente →</button></div></div></dialog>
<!-- SOTA_SESSION_RUN_END -->'''
    html = html.replace('<div id="field-card-modal"', run_dialog + '\n<div id="field-card-modal"', 1)

path.write_text(html, encoding="utf-8")
print('Optical Decision Lab v2 and accessibility/outdoor pass applied')
