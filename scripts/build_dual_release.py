from pathlib import Path
from PIL import Image
import re, shutil, hashlib, json, os
import service_worker

SRC=Path(__file__).resolve().parents[1]
OUT=SRC/'dist'/'canon6d_sota_hosted'
if OUT.exists(): shutil.rmtree(OUT)
(OUT/'assets').mkdir(parents=True); (OUT/'data').mkdir(); (OUT/'diagrams-webp').mkdir(); (OUT/'plans').mkdir(); (OUT/'downloads').mkdir(); (OUT/'.github/workflows').mkdir(parents=True)

# Convert diagrams to lossless WebP once: exact diagram text/lines, granular lazy assets.
img_meta={}
for p in sorted((SRC/'diagrams').glob('*.png')):
    q=OUT/'diagrams-webp'/(p.stem+'.webp')
    with Image.open(p) as im:
        if im.mode not in ('RGB','RGBA'): im=im.convert('RGBA' if 'A' in im.mode else 'RGB')
        im.save(q,'WEBP',lossless=True,method=6)
        img_meta[p.name]={'w':im.width,'h':im.height,'bytes':q.stat().st_size}

html=(SRC/'index.html').read_text(encoding='utf-8')
# Extract all inline CSS into hosted stylesheet. Preserve exact visual parity.
styles=[]
def take_style(m): styles.append(m.group(1)); return ''
html=re.sub(r'<style(?:\s+[^>]*)?>(.*?)</style>',take_style,html,flags=re.S|re.I)
hosted_css='\n\n'.join(styles)
(OUT/'assets/hosted.css').write_text(hosted_css,encoding='utf-8')
# The stylesheet and the plan data are named with their revision, so a page from one
# build never gets another build's copy from a cache that answers by URL: an older
# worker's, or the browser's HTTP cache (Pages sends max-age=600).
html=html.replace('</head>','<link rel="stylesheet" href="./assets/hosted.css?v='+service_worker.revision(OUT/'assets/hosted.css')+'">\n</head>',1)

# External canonical plan data.
html,n=re.subn(r'<script>\s*const PLANS_DATA = .*?;\s*</script>', '<script src="./data/plans_embedded.js"></script>',html,count=1,flags=re.S)
if n!=1: raise RuntimeError('PLANS_DATA block not found')
shutil.copy2(SRC/'data/plans_embedded.js',OUT/'data/plans_embedded.js')
shutil.copy2(SRC/'data/plans.json',OUT/'data/plans.json')
html=html.replace('<script src="./data/plans_embedded.js">','<script src="./data/plans_embedded.js?v='+service_worker.revision(OUT/'data/plans_embedded.js')+'">',1)

# Externalize dynamic images: no 12MB inline asset map.
html,n=re.subn(r'<script>\s*const INLINE_ASSETS=.*?function assetUrl\(path\)\{return INLINE_ASSETS\[path\]\|\|path;\}\s*</script>',
'''<script>\nfunction assetUrl(path){\n  return path.replace(/^diagrams\\/(.+)\\.png$/, './diagrams-webp/$1.webp');\n}\n</script>''',html,count=1,flags=re.S)
if n!=1: raise RuntimeError('INLINE_ASSETS block not found')

# Static teaching panels: map data URIs by alt to granular WebP.
alt_to_file={'Tercios':'composition_tercios.webp','Perspectiva':'composition_perspectiva.webp','Simetría':'composition_simetria.webp','Enmarcado':'composition_enmarcado.webp','Espacio negativo':'composition_espacio_neg.webp','Punto de interés':'composition_punto_interes.webp','Minimalismo':'composition_minimalismo.webp','Capas':'composition_capas.webp','Comparativa 35/50/85 a 2.5 m':'lens_comparison_25cm.webp','Comparativa 35/50/85 a 4 m':'lens_comparison_40cm.webp','Comparativa 35/50/85 a 6 m':'lens_comparison_60cm.webp'}
for alt,fn in alt_to_file.items():
    pat=r'(<img\s+src=")[^"]+("\s+alt="'+re.escape(alt)+r'")'
    html,c=re.subn(pat,lambda m:m.group(1)+'./diagrams-webp/'+fn+m.group(2),html,count=1)
    if c!=1: raise RuntimeError('static teaching image not found '+alt)

# Give static images dimensions/lazy decode where not already present.
def img_hints(m):
    tag=m.group(0)
    if 'loading=' not in tag: tag=tag[:-1]+' loading="lazy" decoding="async">'
    return tag
html=re.sub(r'<img\b[^>]*>',img_hints,html)
registration='''<script>\nif('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js',{scope:'./'}).catch(error=>FocalRutaDiagnostico.record('trabajador',error&&error.message||String(error),'sw.js')));}\n</script>'''
html=html.replace('</body>',registration+'\n</body>',1)
(OUT/'index.html').write_text(html,encoding='utf-8')

# Native challenge and its public canonical data.
shutil.copytree(SRC/'challenges',OUT/'challenges')
shutil.copytree(SRC/'data'/'architecture',OUT/'data'/'architecture')

# Standalone canonical file kept separately, unmodified behavior.
shutil.copy2(SRC/'index.html',OUT/'FocalRuta_STANDALONE.html')
shutil.copy2(SRC/'field_card.html',OUT/'field_card.html')
# Hosted plan pages load the diagrams the hosted index already ships, as lazy
# files, instead of ~2.4 MB of inline base64 per page (Lighthouse 46 on a phone).
# Once a page has loaded it asks the worker to cache itself and its diagrams
# (the first visit happens before the worker controls the page), so one visit
# still leaves the whole plan usable offline. plans/ in the repo and
# the download ZIP keep the self-contained copies for the iPhone Files app.
WARM_DIAGRAMS = """<script>window.addEventListener('load',()=>{const c=navigator.connection;if(!('serviceWorker' in navigator)||(c&&c.saveData))return;const urls=[location.href.split('#')[0],...Object.values(DIAGRAMS).map(u=>new URL(u,location.href).href)];navigator.serviceWorker.ready.then(r=>r.active&&r.active.postMessage({type:'warm',urls})).catch(()=>{});});</script>"""
for p in sorted((SRC/'plans').glob('plan_*.html')):
    page=p.read_text(encoding='utf-8')
    files={key:f'../diagrams-webp/{p.stem}_{key}.webp' for key in json.loads(re.search(r'const DIAGRAMS = (\{.*?\});\n',page,re.S).group(1))}
    page,n=re.subn(r'const DIAGRAMS = \{.*?\};\n',lambda _m:'const DIAGRAMS = '+json.dumps(files)+';\n',page,count=1,flags=re.S)
    if n!=1: raise RuntimeError('DIAGRAMS map not found in '+p.name)
    (OUT/'plans'/p.name).write_text(page.replace('</body>',WARM_DIAGRAMS+'\n</body>',1),encoding='utf-8')
shutil.copy2(SRC/'downloads/canon6d_photo_planner_assets.zip',OUT/'downloads/canon6d_photo_planner_assets.zip')
for name in ['404.html','manifest.webmanifest']:
    if (SRC/name).exists(): shutil.copy2(SRC/name,OUT/name)
for icon in ['app-icon.svg','icon-192.png','icon-512.png','icon-maskable-192.png','icon-maskable-512.png']:
    if (SRC/'assets'/icon).exists(): shutil.copy2(SRC/'assets'/icon,OUT/'assets'/icon)

# PWA: small shell pre-cache, granular runtime cache. Never return HTML for an image/style request.
# Crawlers: everything is public; list the pages people should land on.
SITE='https://pillb.github.io/focalruta/'
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE+'sitemap.xml\n',encoding='utf-8')
pages=['','field_card.html','challenges/arquitectura-en-foco/index.html','challenges/arquitectura-en-foco/wiki-tecnicas.html']+['plans/'+p.name for p in sorted((OUT/'plans').glob('*.html'))]
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{SITE}{page}</loc></url>\n' for page in pages)+'</urlset>\n',encoding='utf-8')

# The worker's bytes must change whenever anything it serves changes, or browsers keep the old cache.
content_hash=hashlib.sha256()
for f in sorted(x for x in OUT.rglob('*') if x.is_file()):
    content_hash.update(f.relative_to(OUT).as_posix().encode()); content_hash.update(f.read_bytes())
cache_version='focalruta-'+content_hash.hexdigest()[:12]
# The worker lives in assets/sw.template.js; scripts/service_worker.py fills in its
# version and the revision of every file it may keep.
service_worker.write(OUT,cache_version)

# Pages workflow from official artifact pattern.
workflow='''name: Deploy FocalRuta to Pages\non:\n  push:\n    branches: [ main ]\n  workflow_dispatch:\npermissions:\n  contents: read\n  pages: write\n  id-token: write\nconcurrency:\n  group: pages\n  cancel-in-progress: true\njobs:\n  deploy:\n    environment:\n      name: github-pages\n      url: ${{ steps.deployment.outputs.page_url }}\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/configure-pages@v5\n      - uses: actions/upload-pages-artifact@v3\n        with:\n          path: .\n      - name: Deploy\n        id: deployment\n        uses: actions/deploy-pages@v4\n'''
(OUT/'.github/workflows/pages.yml').write_text(workflow,encoding='utf-8')

# Build metrics/hashes.
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
metrics={
 'hosted_html_bytes':(OUT/'index.html').stat().st_size,
 'standalone_html_bytes':(OUT/'FocalRuta_STANDALONE.html').stat().st_size,
 'css_bytes':(OUT/'assets/hosted.css').stat().st_size,
 'data_js_bytes':(OUT/'data/plans_embedded.js').stat().st_size,
 'diagram_count':len(img_meta),
 'diagram_webp_bytes':sum(x['bytes'] for x in img_meta.values()),
 'hosted_html_sha256':sha(OUT/'index.html'),
 'standalone_sha256':sha(OUT/'FocalRuta_STANDALONE.html')
}
(OUT/'BUILD_METRICS.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
(OUT/'README.md').write_text('''# FocalRuta — SOTA dual release\n\n- `index.html`: hosted/PWA target; lean HTML, external CSS/data and granular lazy WebP diagrams.\n- `FocalRuta_STANDALONE.html`: single-file iPhone/offline attachment target.\n- `field_card.html`: quick operational card.\n- `plans/`: individual self-contained plan pages.\n- `diagrams-webp/`: hosted diagram assets.\n- `sw.js`: versioned shell/runtime cache.\n- `.github/workflows/pages.yml`: GitHub Pages workflow.\n''',encoding='utf-8')
print(json.dumps(metrics,indent=2))
