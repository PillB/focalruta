"""Audit GitHub-Pages paths, runtime images, font floors, and solid-color text contrast."""
from __future__ import annotations
import json,re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1];CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';checks=[]
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

contrast_js=r'''()=>{function rgb(s){if(s.startsWith('oklch(')){const v=s.match(/[\d.]+/g).map(Number),L=v[0],C=v[1],h=v[2]*Math.PI/180,a=C*Math.cos(h),b=C*Math.sin(h),lp=L+.3963377774*a+.2158037573*b,mp=L-.1055613458*a-.0638541728*b,sp=L-.0894841775*a-1.291485548*b,l=lp**3,m=mp**3,q=sp**3,gamma=x=>255*Math.max(0,Math.min(1,x<=.0031308?12.92*x:1.055*x**(1/2.4)-.055));return[gamma(4.0767416621*l-3.3077115913*m+.2309699292*q),gamma(-1.2684380046*l+2.6097574011*m-.3413193965*q),gamma(-.0041960863*l-.7034186147*m+1.707614701*q),1]}const m=s.match(/[\d.]+/g);return m?[+m[0],+m[1],+m[2],m[3]===undefined?1:+m[3]]:null}function lum(c){const q=c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});return .2126*q[0]+.7152*q[1]+.0722*q[2]}function bgFor(e){for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.backgroundImage!=='none')return null;const c=rgb(s.backgroundColor);if(c&&c[3]>.98)return c}return[255,255,255,1]}const bad=[];for(const e of document.querySelectorAll('body *')){const s=getComputedStyle(e),r=e.getBoundingClientRect();if(!r.width||!r.height||s.display==='none'||s.visibility==='hidden'||s.opacity==='0'||![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;const fg=rgb(s.color),bg=bgFor(e);if(!fg||!bg)continue;const ratio=(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05),size=parseFloat(s.fontSize),bold=parseInt(s.fontWeight)>=700,large=size>=24||(bold&&size>=18.66),need=large?3:4.5;if(ratio+0.01<need)bad.push({tag:e.tagName,cls:String(e.className).slice(0,80),text:e.textContent.trim().slice(0,55),fg:s.color,bg:`rgb(${bg.slice(0,3).map(x=>Math.round(x))})`,ratio:+ratio.toFixed(2),need,size})}return bad.slice(0,40)}'''

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=CHROME,args=['--no-sandbox'])
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
        bad=page.evaluate(contrast_js);add(f'{name} solid-background text contrast',not bad,bad)
        tiny=page.evaluate("()=>[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return r.width&&r.height&&s.display!=='none'&&s.visibility!=='hidden'&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(s.fontSize)<11}).map(e=>({text:e.textContent.trim().slice(0,40),size:getComputedStyle(e).fontSize,cls:String(e.className).slice(0,60)})).slice(0,30)")
        add(f'{name} visible font floor 11px',not tiny,tiny);add(f'{name} no page errors',not errors,errors);page.close()
    browser.close()

# Meaningful Optical SVG lines against #071421 all exceed WCAG non-text 3:1 by chosen palette.
def luminance(hexcolor):
    vals=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)];vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
bg=luminance('#071421');ratios={c:(max(luminance(c),bg)+.05)/(min(luminance(c),bg)+.05) for c in ('#93c5fd','#4ade80','#fbbf24','#f8fafc','#f0abfc')}
add('Optical visualization meaningful lines >=3:1',min(ratios.values())>=3,ratios)

report={'passed':all(x['pass'] for x in checks),'checks':len(checks),'failures':[x for x in checks if not x['pass']],'results':checks}
(ROOT/'VISUAL_RESOURCE_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'passed':report['passed'],'checks':report['checks'],'failures':report['failures']},ensure_ascii=False,indent=2))
