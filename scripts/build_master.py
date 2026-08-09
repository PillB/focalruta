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
