"""Synchronize the public master HTML from canonical data and current generated diagrams.
Project-relative only; safe to rerun after generators.
"""
from pathlib import Path
from PIL import Image
import base64, io, json, re

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
DATA=ROOT/'data'/'plans.json'
DIAG=ROOT/'diagrams'

def as_webp_uri(path:Path)->str:
    with Image.open(path) as im:
        im=im.convert('RGBA') if im.mode in ('RGBA','LA') else im.convert('RGB')
        buf=io.BytesIO(); im.save(buf,format='WEBP',lossless=True,method=6)
    return 'data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')

plans=json.loads(DATA.read_text(encoding='utf-8'))
compact=json.dumps(plans,ensure_ascii=False,separators=(',',':'))
(ROOT/'data'/'plans_embedded.js').write_text('const PLANS_DATA = '+compact+';\n',encoding='utf-8')

t=INDEX.read_text(encoding='utf-8')

# Site-wide orientation: explain the job, vocabulary and recovery path before
# any planner control asks the reader to choose an option.
orientation = '''<section id="eli5-orientation" class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8" aria-labelledby="eli5-orientation-title"><div class="rounded-2xl border-2 border-emerald-200 bg-emerald-50 p-5 sm:p-7"><span class="chip bg-emerald-100 text-emerald-800 mb-2">PARA EMPEZAR · SIN JERGAS</span><h2 id="eli5-orientation-title" class="text-2xl font-bold mb-3">Qué vas a hacer aquí</h2><div class="grid gap-4 md:grid-cols-3 text-sm leading-relaxed"><div><h3 class="font-bold">Qué significa</h3><p><strong>Focal</strong> es cuánto de la escena entra en el encuadre; <strong>PDC</strong> (profundidad de campo) es cuánto queda nítido delante y detrás del foco. <strong>ISO</strong> amplifica la señal y también puede añadir grano.</p></div><div><h3 class="font-bold">Qué vas a hacer</h3><p>Elige un plan, mira el dibujo, prueba una sola variable y haz una foto de comprobación. Primero mueve la cámara; después decide la focal. Lee la tarjeta de campo antes de salir.</p></div><div><h3 class="font-bold">Si algo falla</h3><p>Si una ruta no abre, usa la lista de paradas y confirma el cruce en campo. Si una foto no sale, revisa movimiento, foco, luz y bordes por separado; no cambies todo a la vez.</p></div></div><details class="mt-4"><summary class="cursor-pointer font-semibold">Más palabras útiles</summary><p class="mt-2 text-sm"><strong>Histograma</strong>: gráfico que muestra cuánta luz hay en cada tono. <strong>KML</strong> y <strong>GeoJSON</strong>: archivos para llevar puntos y líneas a una app de mapas. Son ayudas de planificación, no pruebas de que el lugar esté abierto.</p></details></div></section>'''
t = re.sub(r'<section id="eli5-orientation".*?</section>\s*', '', t, count=1, flags=re.S)
t, n = re.subn(r'<!-- QUICK START GUIDE -->', orientation + '\n<!-- QUICK START GUIDE -->', t, count=1)
if n != 1: raise RuntimeError('orientation insertion point not found')
t = t.replace('</svg>\n        <div class="optics-legend"', '</svg><p class="viz-caption text-sm text-slate-200">Visualización: las líneas comparan campo de visión y profundidad de campo; el gráfico es una guía de relación, no una medición de tu cámara en ese instante.</p>\n        <div class="optics-legend"', 1)
# Canonical data script.
t,n=re.subn(r'<script>\s*const PLANS_DATA = .*?;\s*</script>', '<script>\nconst PLANS_DATA = '+compact+';\n</script>', t, count=1, flags=re.S)
if n!=1: raise RuntimeError('Could not replace PLANS_DATA')

# Current generated images used by dynamic cards and teaching modules.
paths=sorted([p for p in DIAG.glob('*.png') if p.name.startswith(('plan_','composition_','lens_comparison_'))])
assets={f'diagrams/{p.name}':as_webp_uri(p) for p in paths}
asset_js=json.dumps(assets,separators=(',',':'))
t,n=re.subn(r'<script>\s*const INLINE_ASSETS=.*?function assetUrl\(path\)\{return INLINE_ASSETS\[path\]\|\|path;\}\s*</script>',
            '<script>\nconst INLINE_ASSETS='+asset_js+';\nfunction assetUrl(path){return INLINE_ASSETS[path]||path;}\n</script>',t,count=1,flags=re.S)
if n!=1: raise RuntimeError('Could not replace INLINE_ASSETS')

# Static teaching panels are also updated from the freshly generated source image.
alt_to_file={
 'Tercios':'composition_tercios.png','Perspectiva':'composition_perspectiva.png','Simetría':'composition_simetria.png',
 'Enmarcado':'composition_enmarcado.png','Espacio negativo':'composition_espacio_neg.png','Punto de interés':'composition_punto_interes.png',
 'Minimalismo':'composition_minimalismo.png','Capas':'composition_capas.png',
 'Comparativa 35/50/85 a 2.5m':'lens_comparison_25cm.png','Comparativa 35/50/85 a 4m':'lens_comparison_40cm.png',
 'Comparativa 35/50/85 a 6m':'lens_comparison_60cm.png'}
for alt,fn in alt_to_file.items():
    uri=assets['diagrams/'+fn]
    pattern=r'(<img\s+src=")[^"]+("\s+alt="'+re.escape(alt)+r'")'
    t,n=re.subn(pattern,lambda m:m.group(1)+uri+m.group(2),t,count=1)
    if n!=1: raise RuntimeError(f'Could not update static teaching image: {alt}')

# Privacy & current counts are release invariants.
t=t.replace('4 planes × 10 tomas × 2 variantes (perro/humano) = 80 diagramas únicos.',
            '6 planes × 10 tomas × 2 variantes (perro/humano) = 120 diagramas únicos.')
INDEX.write_text(t,encoding='utf-8')
print(f'synchronized {len(paths)} images and {len(plans["plans"])} plans into {INDEX}')
