from pathlib import Path
from PIL import Image
import re, shutil, hashlib, json, os

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
html=html.replace('</head>','<link rel="stylesheet" href="./assets/hosted.css">\n<link rel="apple-touch-icon" href="./assets/icon-192.png">\n</head>',1)

# External canonical plan data.
html,n=re.subn(r'<script>\s*const PLANS_DATA = .*?;\s*</script>', '<script src="./data/plans_embedded.js"></script>',html,count=1,flags=re.S)
if n!=1: raise RuntimeError('PLANS_DATA block not found')
shutil.copy2(SRC/'data/plans_embedded.js',OUT/'data/plans_embedded.js')
shutil.copy2(SRC/'data/plans.json',OUT/'data/plans.json')

# Externalize dynamic images: no 12MB inline asset map.
html,n=re.subn(r'<script>\s*const INLINE_ASSETS=.*?function assetUrl\(path\)\{return INLINE_ASSETS\[path\]\|\|path;\}\s*</script>',
'''<script>\nfunction assetUrl(path){\n  return path.replace(/^diagrams\\/(.+)\\.png$/, './diagrams-webp/$1.webp');\n}\n</script>''',html,count=1,flags=re.S)
if n!=1: raise RuntimeError('INLINE_ASSETS block not found')

# Static teaching panels: map data URIs by alt to granular WebP.
alt_to_file={'Tercios':'composition_tercios.webp','Perspectiva':'composition_perspectiva.webp','Simetría':'composition_simetria.webp','Enmarcado':'composition_enmarcado.webp','Espacio negativo':'composition_espacio_neg.webp','Punto de interés':'composition_punto_interes.webp','Minimalismo':'composition_minimalismo.webp','Capas':'composition_capas.webp','Comparativa 35/50/85 a 2.5m':'lens_comparison_25cm.webp','Comparativa 35/50/85 a 4m':'lens_comparison_40cm.webp','Comparativa 35/50/85 a 6m':'lens_comparison_60cm.webp'}
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
html=html.replace('Master · 6 planes · 120 diagramas · Field Card validado','Hosted/PWA · 6 planes · 120 diagramas · SOTA labs')
registration='''<script>\nif('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js',{scope:'./'}).catch(error=>console.warn('PWA worker unavailable',error)));}\n</script>'''
html=html.replace('</body>','<div class="hosted-badge no-print" style="position:fixed;right:10px;bottom:74px;z-index:55">● hosted lean</div>\n'+registration+'\n</body>',1)
(OUT/'index.html').write_text(html,encoding='utf-8')

# Standalone canonical file kept separately, unmodified behavior.
shutil.copy2(SRC/'index.html',OUT/'FocalRuta_STANDALONE.html')
shutil.copy2(SRC/'field_card.html',OUT/'field_card.html')
for p in (SRC/'plans').glob('*.html'): shutil.copy2(p,OUT/'plans'/p.name)
shutil.copy2(SRC/'downloads/canon6d_photo_planner_assets.zip',OUT/'downloads/canon6d_photo_planner_assets.zip')
for name in ['404.html','manifest.webmanifest']:
    if (SRC/name).exists(): shutil.copy2(SRC/name,OUT/name)
for icon in ['app-icon.svg','icon-192.png','icon-512.png']:
    if (SRC/'assets'/icon).exists(): shutil.copy2(SRC/'assets'/icon,OUT/'assets'/icon)

# PWA: small shell pre-cache, granular runtime cache. Never return HTML for an image/style request.
sw='''const VERSION='canon6d-sota-v1';\nconst SHELL=VERSION+'-shell',RUNTIME=VERSION+'-runtime';\nconst CORE=['./','./index.html','./assets/hosted.css','./data/plans_embedded.js','./manifest.webmanifest','./field_card.html','./assets/icon-192.png','./assets/icon-512.png'];\nself.addEventListener('install',e=>e.waitUntil(caches.open(SHELL).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));\nself.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>![SHELL,RUNTIME].includes(k)).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));\nself.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);if(u.origin!==location.origin)return;if(r.mode==='navigate'){e.respondWith(fetch(r).then(x=>{if(x.ok)caches.open(RUNTIME).then(c=>c.put(r,x.clone()));return x}).catch(async()=>await caches.match(r)||await caches.match('./index.html')));return;}if(/\\.(?:webp|png|svg|css|js|json)$/.test(u.pathname)){e.respondWith(caches.match(r).then(cached=>{const fresh=fetch(r).then(x=>{if(x.ok)caches.open(RUNTIME).then(c=>c.put(r,x.clone()));return x}).catch(()=>cached);return cached||fresh}));}});\n'''
(OUT/'sw.js').write_text(sw,encoding='utf-8')

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
