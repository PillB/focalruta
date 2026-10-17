"""Audit GitHub-Pages paths, runtime images, font floors, and solid-color text contrast."""
from __future__ import annotations
import json,re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import evidence
import qa_matrix

ROOT=Path(__file__).resolve().parents[1];checks=[]
def add(name,ok,detail=''):
    checks.append({'name':name,'pass':bool(ok),'detail':detail})
    if not ok: raise AssertionError(f'{name}: {detail}')

# Static project-relative resource and fragment graph.
pages=[ROOT/'index.html',ROOT/'field_card.html',*sorted((ROOT/'plans').glob('*.html')),ROOT/'dist/canon6d_sota_hosted/index.html',ROOT/'dist/canon6d_sota_hosted/field_card.html',*sorted((ROOT/'dist/canon6d_sota_hosted/plans').glob('*.html'))]
for page in pages:
    soup=BeautifulSoup(page.read_text(errors='ignore'),'html.parser');missing=[]
    ids={x.get('id') for x in soup.find_all(id=True)}
    for tag,attr in [('a','href'),('link','href'),('script','src'),('img','src')]:
        for node in soup.find_all(tag):
            ref=node.get(attr)
            if not ref or ref.startswith(('data:','http:','https:','mailto:','javascript:')):continue
            parsed=urlsplit(ref)
            if not parsed.path:
                if parsed.fragment and parsed.fragment not in ids:missing.append(f'fragment #{parsed.fragment}')
                continue
            target=(page.parent/unquote(parsed.path)).resolve()
            if not target.exists():missing.append(ref)
    add(f'{page.relative_to(ROOT)} local links/resources',not missing,missing[:20])

# Text contrast against what is actually behind it. Solid backgrounds are
# checked directly; a gradient is checked at every colour stop (the worst stop
# decides, per WCAG's guidance for varying backgrounds), and gradient-clipped
# text is checked stop by stop against its backdrop. Until round 13 gradients
# were skipped, which hid a 3.72:1 label on every shot card. Colours go through
# a canvas so oklch() and color() resolve exactly as the screen shows them.
# Emoji-only glyphs are skipped: they render in their own colours.
contrast_js=r'''()=>{document.getAnimations().forEach(a=>{try{a.finish()}catch(e){}});
const cv=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
function rgb(s){cv.clearRect(0,0,1,1);cv.fillStyle='#000';cv.fillStyle=s;cv.fillRect(0,0,1,1);const d=cv.getImageData(0,0,1,1).data;return[d[0],d[1],d[2],d[3]/255]}
function over(top,base){return[0,1,2].map(i=>top[i]*top[3]+base[i]*(1-top[3])).concat(1)}
function lum(c){const q=c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});return .2126*q[0]+.7152*q[1]+.0722*q[2]}
function ratio(a,b){const x=lum(a),y=lum(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
const STOP=/(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\([^)]*\)|#[0-9a-f]{3,8}\b/gi;
function stops(image){return(image.match(STOP)||[]).map(rgb)}
function backdrop(e){let layers=[];for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.backgroundImage!=='none'){if(!s.backgroundImage.includes('gradient'))return null;if(!(n===e&&s.backgroundClip==='text'))layers.push(stops(s.backgroundImage))}const c=rgb(s.backgroundColor);if(c[3]>.98){return finish(layers,c)}}return finish(layers,[255,255,255,1])}
function finish(layers,base){let out=[base];for(const stopsOf of layers.reverse()){out=stopsOf.flatMap(st=>out.map(b=>over(st,b)))}return out}
const bad=[];for(const e of document.querySelectorAll('body *')){const s=getComputedStyle(e),r=e.getBoundingClientRect();const own=[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('');if(!r.width||!r.height||s.display==='none'||s.visibility==='hidden'||s.opacity==='0'||!/[\p{L}\p{N}]/u.test(own))continue;
const backs=backdrop(e);if(!backs)continue;const clipped=s.backgroundClip==='text'&&s.backgroundImage.includes('gradient');const fgs=clipped?stops(s.backgroundImage):[rgb(s.color)];
let worst=99;for(const b of backs)for(const f of fgs)worst=Math.min(worst,ratio(over(f,b),b));
const size=parseFloat(s.fontSize),bold=parseInt(s.fontWeight)>=700,large=size>=24||(bold&&size>=18.66),need=large?3:4.5;if(worst+0.01<need)bad.push({tag:e.tagName,cls:String(e.className).slice(0,80),text:e.textContent.trim().slice(0,55),fg:s.color,gradient:s.backgroundImage==='none'?'':s.backgroundImage.slice(0,90),ratio:+worst.toFixed(2),need,size})}return bad.slice(0,40)}'''

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox'],**qa_matrix.browser_options())
    for name,path in {'standalone':ROOT/'index.html','hosted':ROOT/'dist/canon6d_sota_hosted/index.html','field':ROOT/'field_card.html','plan_a':ROOT/'plans/plan_a.html','plan_f':ROOT/'plans/plan_f.html'}.items():
        page=browser.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(path.as_uri(),wait_until='domcontentloaded',timeout=60000)
        if name in ('standalone','hosted'):
            # Exercise every image-producing state and force lazy images to decode.
            broken=[]
            for plan in [f'plan_{x}' for x in 'abcdef']:
                for subject in ('human','dog'):
                    page.evaluate('([p,s])=>{selectPlan(p);setVariant(s)}',[plan,subject])
                    state=page.evaluate('''async()=>{const xs=[...document.querySelectorAll('#plan-detail-content img')];xs.forEach(x=>x.loading='eager');await Promise.all(xs.map(x=>x.decode().catch(()=>null)));return xs.filter(x=>!x.complete||!x.naturalWidth).map(x=>x.src)}''')
                    broken.extend(state)
            add(f'{name} all 120 state images decode',not broken,broken[:10])
            page.evaluate('openFieldCard()')
        else:
            state=page.evaluate('''async()=>{const xs=[...document.images];xs.forEach(x=>x.loading='eager');await Promise.all(xs.map(x=>x.decode().catch(()=>null)));return xs.filter(x=>!x.complete||!x.naturalWidth).map(x=>x.src)}''')
            add(f'{name} images decode',not state,state[:10])
        bad=page.evaluate(contrast_js);add(f'{name} text contrast on solid and gradient backgrounds',not bad,bad)
        tiny=page.evaluate("()=>[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return r.width&&r.height&&s.display!=='none'&&s.visibility!=='hidden'&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(s.fontSize)<11}).map(e=>({text:e.textContent.trim().slice(0,40),size:getComputedStyle(e).fontSize,cls:String(e.className).slice(0,60)})).slice(0,30)")
        add(f'{name} visible font floor 11px',not tiny,tiny);add(f'{name} no page errors',not errors,errors);page.close()
    browser.close()

# Meaningful Optical SVG lines against #071421 all exceed WCAG non-text 3:1 by chosen palette.
def luminance(hexcolor):
    vals=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)];vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
bg=luminance('#071421');ratios={c:(max(luminance(c),bg)+.05)/(min(luminance(c),bg)+.05) for c in ('#93c5fd','#4ade80','#fbbf24','#f8fafc','#f0abfc')}
add('Optical visualization meaningful lines >=3:1',min(ratios.values())>=3,ratios)

report={'passed':all(x['pass'] for x in checks),'checks':len(checks),'failures':[x for x in checks if not x['pass']],'results':checks}
evidence.write_report(ROOT/'VISUAL_RESOURCE_QA.json', report, pages);print(json.dumps({'passed':report['passed'],'checks':report['checks'],'failures':report['failures']},ensure_ascii=False,indent=2))
