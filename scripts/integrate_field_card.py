"""Embed the canonical Field Card into index.html without touching unrelated UI blocks.
Idempotent and project-relative. It also ensures the shot modal and mobile bottom nav exist.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
fragment=(ROOT/'data'/'field_card_fragment.html').read_text(encoding='utf-8')
css=(ROOT/'data'/'field_card.css').read_text(encoding='utf-8')
js=(ROOT/'data'/'field_card.js').read_text(encoding='utf-8')

# Scope standalone Field Card styles for the embedded modal. Keep the outdoor
# readability appendix, which intentionally follows the standalone print block.
readability=''
if '/* READABILITY_OUTDOOR_V2 */' in css:
    readability='/* READABILITY_OUTDOOR_V2 */'+css.split('/* READABILITY_OUTDOOR_V2 */',1)[1]
css=css.rsplit('@media print',1)[0]+'\n'+readability
css=re.sub(r':root\{([^}]*)\}',r'#field-card-modal{\1}',css,count=1)
css=re.sub(r'\*\{box-sizing:border-box\}html\{[^}]*\}body\{[^}]*\}', '#field-card-modal *{box-sizing:border-box}', css, count=1)
modal_css=r'''
#field-card-modal{position:fixed;inset:0;z-index:120;background:rgba(3,13,22,.72);display:none;padding:0;-webkit-backdrop-filter:blur(9px);backdrop-filter:blur(9px)}
#field-card-modal.fc-modal-open{display:block}
.fc-modal-card{width:min(100%,1100px);height:100dvh;margin:auto;background:#f4f1e9;display:flex;flex-direction:column;box-shadow:0 0 60px rgba(0,0,0,.28)}
.fc-modal-bar{flex:0 0 auto;min-height:54px;padding:calc(6px + env(safe-area-inset-top)) 10px 6px;background:#061827;color:#fff;display:flex;align-items:center;gap:8px;justify-content:space-between;border-bottom:1px solid #ffffff18}
.fc-modal-bar strong{font-size:13px}.fc-modal-bar small{display:block;color:#dbeafe;font-size:11px;line-height:1.35;margin-top:1px}.fc-modal-bar button{min-width:44px;min-height:44px;border-radius:10px;border:1px solid #ffffff55;background:#ffffff12;color:#fff;font-size:11px;font-weight:900;padding:0 10px}
.fc-modal-scroll{flex:1;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;background:#f4f1e9}
#field-card-modal #field-card-app{padding-top:8px}
body.fc-modal-lock{overflow:hidden;touch-action:none}
.mobile-bottom-nav button{min-width:0;min-height:48px;border:0;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#475569;text-decoration:none;font-size:10px;font-weight:800;padding:0}.mobile-bottom-nav button .ico{font-size:18px;line-height:1}.mobile-bottom-nav button:active{background:#eff6ff;border-radius:12px;color:#1d4ed8}
@media(min-width:900px){#field-card-modal{padding:22px}.fc-modal-card{height:calc(100dvh - 44px);border-radius:22px;overflow:hidden}.fc-modal-bar{padding-top:6px}}
@media print{#field-card-modal{display:none!important}}
'''
modal_html='''<!-- FIELD CARD INTEGRATED -->
<div id="field-card-modal" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Field Card FocalRuta">
  <div class="fc-modal-card">
    <div class="fc-modal-bar"><button type="button" onclick="closeFieldCard()" aria-label="Cerrar Field Card">✕</button><div><strong>FIELD CARD · SESIÓN</strong><small>consulta rápida · progreso guardado en este dispositivo</small></div><button type="button" onclick="closeFieldCard();document.getElementById('quick-start')?.scrollIntoView({behavior:'smooth'})">SITIO</button></div>
    <div class="fc-modal-scroll">'''+fragment+'''</div>
  </div>
</div>
<!-- FIELD CARD INTEGRATED END -->
'''
shot_modal='''<!-- ============================================================ -->
<!-- MODAL: SHOT DETAIL -->
<!-- ============================================================ -->
<div id="shot-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 hidden items-center justify-center p-4" onclick="closeModal(event)">
  <div class="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto" onclick="event.stopPropagation()">
    <div class="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
      <h3 id="modal-title" class="font-bold text-lg">Detalle de toma</h3>
      <button type="button" onclick="document.getElementById('shot-modal').classList.add('hidden');document.getElementById('shot-modal').classList.remove('flex')" aria-label="Cerrar detalle" class="text-slate-500 hover:text-slate-900 min-w-[44px] min-h-[44px] grid place-items-center">✕</button>
    </div>
    <div id="modal-body" class="p-6"></div>
  </div>
</div>
'''
mobile_nav='''<nav class="mobile-bottom-nav no-print" aria-label="Navegación móvil">
  <a href="#top" class="active"><span class="ico">▶️</span><span>Inicio</span></a>
  <a href="#planes"><span class="ico">🗺️</span><span>Planes</span></a>
  <a href="#plan-detail"><span class="ico">📷</span><span>Tomas</span></a>
  <button type="button" onclick="openFieldCard()"><span class="ico">📋</span><span>Field</span></button>
  <a href="#guide"><span class="ico">🎓</span><span>Guía</span></a>
</nav>
'''
modal_js=f'''\n{js}\nfunction openFieldCard(){{const m=document.getElementById('field-card-modal');if(!m)return;m.classList.add('fc-modal-open');m.setAttribute('aria-hidden','false');document.body.classList.add('fc-modal-lock');setTimeout(()=>m.querySelector('.fc-modal-scroll')?.scrollTo({{top:0,behavior:'auto'}}),0);}}\nfunction closeFieldCard(){{const m=document.getElementById('field-card-modal');if(!m)return;m.classList.remove('fc-modal-open');m.setAttribute('aria-hidden','true');document.body.classList.remove('fc-modal-lock');}}\ndocument.addEventListener('keydown',e=>{{if(e.key==='Escape')closeFieldCard()}});\n'''

def patch(text:str)->str:
    # Remove ONLY our explicitly bounded previous blocks.
    text=re.sub(r'<style>\s*<!-- FIELD CARD CSS START -->.*?<!-- FIELD CARD CSS END -->\s*</style>\s*','',text,flags=re.S)
    text=re.sub(r'<!-- FIELD CARD INTEGRATED -->.*?<!-- FIELD CARD INTEGRATED END -->\s*','',text,flags=re.S)
    # Remove only marker-bounded Field Card code. Older generated files placed
    # later application code in the same <script>; requiring </script> after the
    # end marker could therefore consume the Optical/Motion/Session labs too.
    text=re.sub(r'<!-- FIELD CARD JS START -->.*?<!-- FIELD CARD JS END -->\s*','',text,flags=re.S)
    text=re.sub(r'<script>\s*</script>\s*','',text,flags=re.S)
    # Legacy unbounded block predates Session Run. Never let this migration consume newer dialogs.
    if '<!-- SOTA_SESSION_RUN_START -->' not in text:
        text=re.sub(r'<!-- FIELD CARD INTEGRATED -->.*?(?=<!-- ============================================================ -->\s*<!-- MODAL: SHOT DETAIL -->)','',text,flags=re.S)
    text=text.replace('</head>',f'<style>\n<!-- FIELD CARD CSS START -->\n{css}\n{modal_css}\n<!-- FIELD CARD CSS END -->\n</style>\n</head>',1)
    # Make top Field Card trigger functional if present as an anchor.
    text=re.sub(r'<a href="#quick-start" title="Checklist rápido"([^>]*)>📋</a>',r'<button type="button" onclick="openFieldCard()" title="Field Card"\1>📋</button>',text,count=1)
    # Ensure shot modal and mobile navigation exist before scripts.
    script_marker='<!-- ============================================================ -->\n<!-- SCRIPT: data and rendering are fully embedded for iPhone/Safari attachment mode -->'
    insertion=''
    if 'id="field-card-modal"' not in text: insertion+=modal_html+'\n'
    if 'id="shot-modal"' not in text: insertion+=shot_modal+'\n'
    if '<nav class="mobile-bottom-nav' not in text: insertion+=mobile_nav+'\n'
    if insertion:
        if script_marker not in text: raise RuntimeError('Main script marker not found')
        text=text.replace(script_marker,insertion+script_marker,1)
    # Footer resource if absent.
    needle='<li><a href="#tecnicas" class="hover:text-white transition">Guía de técnicas</a></li>'
    footer=text[text.find('<footer'):] if '<footer' in text else ''
    if needle in text and 'Abrir Field Card' not in footer:
        text=text.replace(needle,needle+'\n          <li><button type="button" onclick="openFieldCard()" class="hover:text-white transition text-left">Abrir Field Card</button></li>',1)
    text=text.replace('</body>',f'<script>\n<!-- FIELD CARD JS START -->\n{modal_js}\n<!-- FIELD CARD JS END -->\n</script>\n</body>',1)
    return text

INDEX.write_text(patch(INDEX.read_text(encoding='utf-8')),encoding='utf-8')
print('patched',INDEX)
