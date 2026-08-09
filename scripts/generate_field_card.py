from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'field_card.html'

LENSES = [
    ('35', 'EF 35mm f/2 IS USM', 'f/2', '0.24 m', '67 mm'),
    ('50', 'EF 50mm f/1.8 STM', 'f/1.8', '0.35 m', '49 mm'),
    ('85', 'EF 85mm f/1.8 USM', 'f/1.8', '0.85 m', '58 mm'),
    ('Z', 'EF 35–80mm f/4–5.6 III', 'f/4–5.6', '0.40 m', '52 mm'),
]

# id, icon, technique, lens, exposure, af, geometry, pass criterion
SHOTS = [
    ('01','▤','Mucha PDC · capas','35','f/11 · 1/125+ · ISO 100–400','One Shot · foco ≈4 m','FG ≥2 m · sujeto ≈4 m · fondo ≥10 m','3 planos se leen nítidos'),
    ('02','↔','Mucha PDC · simetría','35 / Z@35','f/8–11 · 1/125+ · ISO 100–400','One Shot · eje central','sujeto ≈5–6 m · cámara nivelada','eje centrado + detalle delante/detrás'),
    ('03','◎','Poca PDC · retrato','85','f/1.8 · 1/500+ · Auto ISO','One Shot · ojo cercano','sujeto ≈3 m · fondo ≥8 m DETRÁS','ojo clavado + fondo se derrite'),
    ('04','▣','Poca PDC · enmarcado','50','f/1.8 · 1/250+ · Auto ISO','One Shot · ojo/detalle','sujeto ≈2–2.5 m · fondo ≥5 m detrás','marco suave + sujeto aislado'),
    ('05','❄','Congelado','85','f/2.8 · 1/2000 · Auto ISO','AI Servo · centro · ráfaga','sujeto ≈6–8 m · pre-seguir','ojo/patas/cabello SIN blur'),
    ('06','→','Barrido','50','Tv 1/40 · ISO 100 · apertura auto','AI Servo · seguimiento','trayectoria LATERAL / casi paralela','sujeto reconocible + fondo streak'),
    ('07','◌','Fantasma','35','f/8 · 1 s · ISO 100','pre-enfoca → MF · trípode','fondo fijo · persona cruza cuadro','fondo nítido + sujeto translúcido'),
    ('08','✦','Lightpainting','35','f/8 · 10 s · ISO 100','pre-enfoca → MF · trípode','oscuridad · sujeto/objeto quieto','trazo limpio + cámara inmóvil'),
    ('09','≈','Larga exposición','35','f/11 · 5–15 s · ISO 100','pre-enfoca → MF · trípode','blue hour/noche · posición protegida','trazas continuas + luces conservadas'),
    ('10','⇆','Zooming','Z','f/8 · 2 s · ISO 100','pre-enfoca → MF · trípode','centro fuerte · cámara fija · 35↔80','centro legible + rayos radiales'),
]

RESCUE = [
    ('🎯','Foco falla','Estático: cierra f/1.8 → f/2.2–2.8. Acción: centro + AI Servo + pre-seguimiento. No bajes el shutter que define el efecto.'),
    ('🌫','Fondo no se borra','Primero ALEJA sujeto del fondo. Después abre diafragma / usa 85. Cambiar sólo f/ no compensa un fondo pegado.'),
    ('💨','Barrido parece congelado','Baja 1/60 → 1/40 → 1/30. Mantén trayectoria lateral y continúa el giro después de disparar.'),
    ('🫨','Barrido: todo borroso','Sube a 1/60, suaviza el giro desde la cintura y apunta a un detalle estable del sujeto.'),
    ('👻','Fantasma demasiado tenue','Haz que la persona se mueva más lento o haga una micro-pausa. Si queda sólida, haz lo contrario.'),
    ('🌟','Luces quemadas','ISO 100 → cierra a f/11–16 → reduce tiempo. De día, una exposición de segundos puede requerir ND/sombra.'),
    ('🔭','Zooming sin rayos','Usa luces/patrones contrastados, 2–4 s y recorre más rango 35↔80 sin mover el trípode.'),
    ('▰','Noche vibra','Trípode firme + temporizador 2 s/remoto + no tocar cámara. Revisa nitidez al 100% antes de seguir.'),
]

COMPOSITION = [
    ('▦','Tercios','Sujeto/ojos cerca de intersección; aire hacia mirada o movimiento.'),
    ('↗','Perspectiva','Líneas llevan al sujeto. Cambia POSICIÓN antes de cambiar lente.'),
    ('↔','Simetría','Eje central perfecto; nivelar antes de disparar.'),
    ('▣','Enmarcado','Rama/puerta/arco rodea sin tapar ojos ni articulaciones.'),
    ('□','Espacio negativo','Deja aire útil; no vacío accidental.'),
    ('◎','Punto de interés','Una cosa debe ganar la atención en <1 segundo.'),
    ('•','Minimalismo','Quita elementos hasta que nada compita.'),
    ('▤','Capas','Foreground + sujeto + background físicamente separados.'),
]
ANGLES = [
    ('↔','Eye-level','Lente a ojos: perro ~30–50 cm; humano según altura de ojos.'),
    ('↘','Picado','Cámara arriba → abajo; reduce presencia.'),
    ('↗','Contrapicado','Cámara abajo → arriba; aumenta presencia y convergencia.'),
    ('↑','Nadir','90° ARRIBA. Copa/edificios; vigila bordes con 35 mm.'),
    ('↓','Cenital','90° ABAJO. Patrón / lectura gráfica.'),
    ('◇','Holandés','Roll 10–15° sólo con intención de tensión.'),
]
PREP = [
    ('RAW','Archivo','RAW · espacio en SD · batería · lente limpio'),
    ('AF','Enfoque','quieto = One Shot · acción = AI Servo + centro'),
    ('▰','Soporte','≥0.5 s = trípode + 2 s/remoto; no tocar cámara'),
    ('100%','Chequeo','acción: ojo/patas · PDC: FG/BG · noche: altas luces'),
    ('🐶','Perro','correa y trayectoria segura; nunca junto a calzada activa'),
    ('HIST','Exposición','histograma/altas luces después de cada serie, no de cada frame'),
]

shot_rows=''.join(f'''<label class="fc-shot" data-shot="{n}">
<input class="fc-check" type="checkbox" aria-label="Marcar toma {n}">
<span class="fc-id"><b>{n}</b><i>{ico}</i></span>
<span class="fc-core"><strong>{title}</strong><em>{lens}</em><small>{exp}</small><small>{af}</small></span>
<span class="fc-proof"><small>{geo}</small><b>✓ {ok}</b></span>
</label>''' for n,ico,title,lens,exp,af,geo,ok in SHOTS)

rescue_cards=''.join(f'<article class="fc-mini fc-rescue"><span>{ico}</span><div><b>{title}</b><p>{tip}</p></div></article>' for ico,title,tip in RESCUE)
comp_cards=''.join(f'<article class="fc-mini"><span>{ico}</span><div><b>{title}</b><p>{tip}</p></div></article>' for ico,title,tip in COMPOSITION)
angle_cards=''.join(f'<article class="fc-mini"><span>{ico}</span><div><b>{title}</b><p>{tip}</p></div></article>' for ico,title,tip in ANGLES)
prep_cards=''.join(f'<article class="fc-mini"><span>{ico}</span><div><b>{title}</b><p>{tip}</p></div></article>' for ico,title,tip in PREP)
lens_cards=''.join(f'<article class="fc-lens"><b>{code}</b><div><strong>{name}</strong><small>máx. {maxap} · MFD {mfd} · filtro {flt}</small></div></article>' for code,name,maxap,mfd,flt in LENSES)

CSS=r'''
:root{--fc-ink:#0b1724;--fc-muted:#60707d;--fc-line:#dbe3e9;--fc-paper:#f4f1e9;--fc-navy:#061827;--fc-teal:#0e6b68;--fc-gold:#e1b72e;--fc-green:#087f5b;--fc-red:#a52a20}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--fc-paper);color:var(--fc-ink);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Arial,sans-serif}
#field-card-app{max-width:1040px;margin:auto;padding:10px 10px calc(76px + env(safe-area-inset-bottom));font-variant-numeric:tabular-nums}
.fc-hero{background:linear-gradient(145deg,#06131f,#0e3c48 58%,#29345b);color:#fff;border-radius:18px;padding:13px 13px 11px;box-shadow:0 12px 28px rgba(15,23,42,.14)}
.fc-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.fc-title b{font-size:16px;letter-spacing:-.02em}.fc-title small{display:block;font-size:9.5px;color:#cce1e5;margin-top:2px}.fc-progress{min-width:61px;text-align:center;padding:6px;border-radius:12px;background:#ffffff12;border:1px solid #ffffff20}.fc-progress b{font-size:18px}.fc-progress small{display:block;font-size:8px;color:#dce9ed}
.fc-lensline{display:flex;gap:4px;overflow-x:auto;padding:8px 0 2px;scrollbar-width:none}.fc-lensline::-webkit-scrollbar{display:none}.fc-pill{flex:0 0 auto;padding:4px 6px;border-radius:999px;background:#ffffff10;border:1px solid #ffffff18;font-size:9px;font-weight:800}.fc-principles{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin-top:8px}.fc-principles div{background:#ffffff0d;border-radius:9px;padding:6px}.fc-principles b{display:block;color:#f4d975;font-size:8.5px}.fc-principles span{font-size:8.6px;line-height:1.22;color:#edf6f7}
.fc-tabs{position:sticky;top:calc(4px + env(safe-area-inset-top));z-index:15;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;padding:7px 0 6px;background:rgba(244,241,233,.95);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}.fc-tab{min-height:44px;border:1px solid var(--fc-line);border-radius:11px;background:#fff;color:#334155;font-size:9.5px;font-weight:900}.fc-tab.fc-active{background:var(--fc-navy);border-color:var(--fc-navy);color:#fff}.fc-panel{display:none}.fc-panel.fc-active{display:block}.fc-panelhead{display:flex;align-items:end;justify-content:space-between;gap:8px;margin:3px 1px 7px}.fc-panelhead h2{font-size:13px;margin:0}.fc-panelhead p{font-size:9px;color:var(--fc-muted);margin:1px 0 0}.fc-reset{border:0;background:transparent;color:#64748b;text-decoration:underline;font-size:9px;padding:6px}
.fc-shots{display:grid;gap:5px}.fc-shot{display:grid;grid-template-columns:23px 34px minmax(0,1.08fr) minmax(0,.92fr);gap:6px;align-items:center;background:#fff;border:1px solid var(--fc-line);border-radius:12px;padding:7px;box-shadow:0 2px 9px rgba(15,23,42,.035);min-width:0;cursor:pointer}.fc-shot.fc-done{background:#f0fbf6;border-color:#9ad5c2}.fc-check{appearance:none;-webkit-appearance:none;width:21px;height:21px;border:2px solid #a7b3bd;border-radius:6px;margin:0;display:grid;place-items:center}.fc-check:checked{background:var(--fc-green);border-color:var(--fc-green)}.fc-check:checked:after{content:'✓';color:#fff;font-size:14px;font-weight:900}.fc-id{display:grid;place-items:center}.fc-id b{font-size:7.5px;color:#71808d}.fc-id i{font-style:normal;font-size:17px;line-height:1}.fc-core,.fc-proof{min-width:0}.fc-core strong{display:inline;font-size:10.4px;line-height:1.12}.fc-core em{display:inline-block;margin-left:5px;background:#e9f4f4;color:#0e5a58;border-radius:6px;padding:2px 4px;font-style:normal;font-size:8px;font-weight:900}.fc-core small,.fc-proof small{display:block;font-size:8.6px;line-height:1.2;color:#4e5e6a;overflow-wrap:anywhere;margin-top:2px}.fc-proof{border-left:1px solid #edf0f2;padding-left:6px}.fc-proof b{display:block;color:var(--fc-green);font-size:8.4px;line-height:1.18;margin-top:3px}
.fc-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}.fc-mini{display:flex;gap:8px;min-width:0;background:#fff;border:1px solid var(--fc-line);border-radius:11px;padding:8px}.fc-mini>span{flex:0 0 27px;width:27px;height:27px;border-radius:8px;background:#edf4f5;display:grid;place-items:center;font-size:11px;font-weight:900}.fc-mini b{font-size:9.5px}.fc-mini p{font-size:8.6px;line-height:1.28;margin:2px 0 0;color:#52616c}.fc-rescue{border-left:3px solid #e4aa31}.fc-lenses{display:grid;gap:5px;margin-bottom:7px}.fc-lens{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--fc-line);border-radius:11px;padding:8px}.fc-lens>b{display:grid;place-items:center;min-width:31px;height:31px;border-radius:9px;background:var(--fc-navy);color:#fff;font-size:10px}.fc-lens strong{display:block;font-size:9.7px}.fc-lens small{font-size:8.7px;color:#586874}.fc-note{margin-top:6px;padding:8px 9px;border-radius:11px;background:#fff8dc;border:1px solid #ead68d;color:#514823;font-size:8.7px;line-height:1.3}.fc-note b{color:#725a0b}.fc-danger{background:#fff2ee;border-color:#f0c4bb;color:#76251a}.fc-printstrip{display:none}
.fc-bottom{position:fixed;left:0;right:0;bottom:0;z-index:30;display:grid;grid-template-columns:1fr 1.1fr 1fr;gap:6px;padding:6px 9px calc(6px + env(safe-area-inset-bottom));background:rgba(255,255,255,.97);border-top:1px solid #dfe6eb;-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}.fc-bottom button,.fc-bottom a{min-height:44px;border:1px solid var(--fc-line);border-radius:11px;background:#fff;color:#334155;text-decoration:none;display:grid;place-items:center;font-size:9px;font-weight:900}.fc-bottom .fc-primary{background:var(--fc-navy);color:#fff;border-color:var(--fc-navy)}
@media(max-width:390px){#field-card-app{padding-left:7px;padding-right:7px}.fc-hero{border-radius:15px;padding:11px 10px}.fc-principles{grid-template-columns:1fr}.fc-principles div{display:flex;gap:6px}.fc-principles b{flex:0 0 auto}.fc-shot{grid-template-columns:21px 30px minmax(0,1.14fr) minmax(0,.86fr);gap:4px;padding:6px 5px}.fc-core strong{font-size:9.8px}.fc-core small,.fc-proof small{font-size:8.1px}.fc-proof b{font-size:8px}.fc-grid{grid-template-columns:1fr 1fr}.fc-mini{padding:7px 6px;gap:6px}.fc-mini>span{width:24px;height:24px;flex-basis:24px}.fc-mini p{font-size:8.2px}}
@media(min-width:700px){#field-card-app{padding:18px 18px 22px}.fc-shots{grid-template-columns:1fr 1fr}.fc-grid{grid-template-columns:repeat(4,1fr)}.fc-lenses{grid-template-columns:1fr 1fr}.fc-bottom{display:none}.fc-shot{min-height:72px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
@media print{@page{size:A4 landscape;margin:5.5mm}body{background:#fff!important}#field-card-app{max-width:none;padding:0}.fc-hero{border-radius:0;box-shadow:none;padding:6px 8px}.fc-title b{font-size:12px}.fc-title small,.fc-progress small{font-size:6.5px}.fc-progress b{font-size:12px}.fc-lensline{padding-top:3px}.fc-pill{font-size:6.7px;padding:2px 4px}.fc-principles{display:none}.fc-tabs,.fc-bottom,.fc-panelhead,.fc-check{display:none!important}.fc-panel{display:none!important}#fc-field{display:block!important}.fc-shots{grid-template-columns:1fr 1fr;gap:2.5px;margin-top:4px}.fc-shot{grid-template-columns:28px minmax(0,1.1fr) minmax(0,.9fr);padding:4px 5px;border-radius:5px;box-shadow:none}.fc-id{grid-column:1}.fc-core{grid-column:2}.fc-proof{grid-column:3}.fc-core strong{font-size:7.6px}.fc-core em{font-size:6px}.fc-core small,.fc-proof small,.fc-proof b{font-size:6.5px}.fc-printstrip{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:4px;margin-top:4px}.fc-printstrip>div{border:1px solid var(--fc-line);border-radius:5px;padding:4px;font-size:6.5px;line-height:1.25}.fc-printstrip b{font-size:7px}.fc-note{display:none}}
'''

CSS += r'''
/* READABILITY_OUTDOOR_V2 */
:root{--fc-muted:#334155;--fc-line:#64748b}body{font-size:16px;line-height:1.5;text-rendering:optimizeLegibility}.fc-hero,.fc-shot,.fc-mini,.fc-lens,.fc-note{border-width:1.5px}.fc-title small,.fc-pill,.fc-principles b,.fc-principles span,.fc-progress small,.fc-tab,.fc-panelhead p,.fc-reset,.fc-id b,.fc-core strong,.fc-core em,.fc-core small,.fc-proof small,.fc-proof b,.fc-mini b,.fc-mini p,.fc-lens strong,.fc-lens small,.fc-note,.fc-bottom button,.fc-bottom a{font-size:max(11px,0.69rem);line-height:1.35}.fc-title small,.fc-progress small,.fc-principles span{color:#f1f5f9}.fc-principles b{color:#fde68a}.fc-core small,.fc-proof small,.fc-mini p,.fc-lens small{color:#334155}.fc-id b{color:#475569}.fc-proof{border-color:#94a3b8}.fc-proof b{color:#066342}.fc-check{border-color:#475569}.fc-tab{border-width:2px}.fc-tab.fc-active{background:#061827!important;color:#fff!important}.fc-reset{color:#475569}:where(a,button,input,label):focus-visible{outline:3px solid #facc15;outline-offset:2px;box-shadow:0 0 0 2px #0f172a}
@media(max-width:520px){.fc-shot{grid-template-columns:24px 32px minmax(0,1fr);gap:5px}.fc-check{grid-column:1;grid-row:1/3}.fc-id{grid-column:2;grid-row:1/3}.fc-core{grid-column:3}.fc-proof{grid-column:3;border-left:0;border-top:1.5px solid #94a3b8;padding:5px 0 0}.fc-grid{grid-template-columns:1fr}.fc-mini p{font-size:12px}.fc-principles{grid-template-columns:1fr}.fc-panelhead h2{font-size:16px}}
@media(prefers-contrast:more){:root{--fc-muted:#111827;--fc-line:#334155}.fc-shot,.fc-mini,.fc-lens{border-width:2px}}
'''

APP=f'''
<div id="field-card-app">
<header class="fc-hero">
<div class="fc-head"><div class="fc-title"><b>FOCALRUTA · FIELD CARD</b><small>10 tomas · consulta en 5 segundos · valores de ARRANQUE</small></div><div class="fc-progress"><b id="fc-count">0/10</b><small>LISTAS</small></div></div>
<div class="fc-lensline"><span class="fc-pill">35 · f/2 IS</span><span class="fc-pill">50 · f/1.8 STM</span><span class="fc-pill">85 · f/1.8 USM</span><span class="fc-pill">35–80 · f/4–5.6 III</span></div>
<div class="fc-principles"><div><b>PDC PROFUNDA</b><span>35 · f/8–11 · tres distancias reales</span></div><div><b>PDC CORTA</b><span>85 f/1.8 · sujeto cerca · fondo LEJOS</span></div><div><b>MOVIMIENTO</b><span>manda el shutter: 1/2000 / 1/40 / 1 s</span></div></div>
</header>
<nav class="fc-tabs" aria-label="Secciones de la Field Card"><button class="fc-tab fc-active" data-fc-tab="fc-field">📷 CAMPO</button><button class="fc-tab" data-fc-tab="fc-rescue">⚡ RESCATE</button><button class="fc-tab" data-fc-tab="fc-compose">▦ COMPO</button><button class="fc-tab" data-fc-tab="fc-gear">⚙ EQUIPO</button></nav>
<section id="fc-field" class="fc-panel fc-active"><div class="fc-panelhead"><div><h2>Toca ✓ sólo después de revisar al 100%</h2><p>Si no aparece el criterio verde, repite antes de avanzar.</p></div><button class="fc-reset" id="fc-reset">reiniciar</button></div><div class="fc-shots">{shot_rows}</div><div class="fc-note"><b>REGLA MAESTRA:</b> Poca PDC = apertura + focal + cámara↔sujeto + sujeto↔fondo. Para más blur, la separación del FONDO suele cambiar más la imagen que abrir 1/3 de stop.</div>
<div class="fc-printstrip"><div><b>RESCATE</b><br>foco falla → f/2.2–2.8 · barrido congelado → 1/40→1/30 · noche vibra → 2 s timer</div><div><b>COMPO</b><br>▦ tercios · ↔ simetría · ▣ marco · □ negativo · ▤ capas</div><div><b>ÁNGULOS</b><br>↔ ojos · ↘ picado · ↗ contrapicado · ↑ nadir · ↓ cenital</div></div>
</section>
<section id="fc-rescue" class="fc-panel"><div class="fc-panelhead"><div><h2>Cuando la foto “no sale”</h2><p>Cambia una variable por vez; conserva la variable que define el efecto.</p></div></div><div class="fc-grid">{rescue_cards}</div><div class="fc-note fc-danger"><b>NO NEGOCIABLE:</b> para congelado no sacrifiques 1/2000; para barrido no “arregles” 1/40 subiendo a 1/250; para fantasma/larga/zooming no muevas la cámara.</div></section>
<section id="fc-compose" class="fc-panel"><div class="fc-panelhead"><div><h2>Composición + ángulo</h2><p>Una intención dominante; no “colecciones” reglas.</p></div></div><div class="fc-grid">{comp_cards}{angle_cards}</div></section>
<section id="fc-gear" class="fc-panel"><div class="fc-panelhead"><div><h2>Equipo real + preflight</h2><p>Máxima del lente no significa que debas usarla en todas las tomas.</p></div></div><div class="fc-lenses">{lens_cards}</div><div class="fc-grid">{prep_cards}</div><div class="fc-note"><b>FUENTE DE SPECS:</b> Canon Camera Museum / Canon. El 35–80 del proyecto es la versión III; si el texto del barril de tu unidad dice otra variante, conserva lo que indique el lente físico.</div></section>
</div>
'''

JS=r'''
(function(){
 const app=document.getElementById('field-card-app'); if(!app) return;
 const KEY='canon6d-fieldcard-v4';
 const checks=[...app.querySelectorAll('.fc-check')];
 function sync(){checks.forEach(c=>c.closest('.fc-shot')?.classList.toggle('fc-done',c.checked)); const n=checks.filter(c=>c.checked).length; const count=app.querySelector('#fc-count'); if(count) count.textContent=`${n}/10`; try{localStorage.setItem(KEY,JSON.stringify(checks.map(c=>c.checked)))}catch(e){}}
 try{const saved=JSON.parse(localStorage.getItem(KEY)||'[]'); checks.forEach((c,i)=>c.checked=!!saved[i])}catch(e){}
 checks.forEach(c=>c.addEventListener('change',sync)); sync();
 app.querySelector('#fc-reset')?.addEventListener('click',()=>{checks.forEach(c=>c.checked=false);sync()});
 function tab(id){app.querySelectorAll('.fc-tab').forEach(b=>b.classList.toggle('fc-active',b.dataset.fcTab===id)); app.querySelectorAll('.fc-panel').forEach(p=>p.classList.toggle('fc-active',p.id===id)); const scroller=app.closest('.fc-modal-scroll'); if(scroller) scroller.scrollTo({top:0,behavior:'auto'}); else window.scrollTo({top:0,behavior:'auto'});}
 app.querySelectorAll('.fc-tab').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.fcTab)));
 app.querySelector('[data-fc-open-field]')?.addEventListener('click',()=>tab('fc-field'));
 window.Canon6DFieldCard={tab,sync};
})();
'''

html=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#061827"><link rel="manifest" href="manifest.webmanifest"><meta name="apple-mobile-web-app-capable" content="yes"><title>Field Card · FocalRuta</title><style>{CSS}</style></head><body>{APP}<nav class="fc-bottom" aria-label="Acciones"><a href="index.html">← SITIO</a><button class="fc-primary" type="button" onclick="Canon6DFieldCard.tab('fc-field')">📷 CAMPO</button><button type="button" onclick="window.print()">🖨 IMPRIMIR</button></nav><script>{JS}</script><script>if(('serviceWorker' in navigator)&&(location.protocol==='http:'||location.protocol==='https:')){{window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{{}}));}}</script></body></html>'''
OUT.write_text(html,encoding='utf-8')
# Also export reusable fragments for the integrator.
(ROOT/'data'/'field_card_fragment.html').write_text(APP,encoding='utf-8')
(ROOT/'data'/'field_card.css').write_text(CSS,encoding='utf-8')
(ROOT/'data'/'field_card.js').write_text(JS,encoding='utf-8')
print(OUT)
