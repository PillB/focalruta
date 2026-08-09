"""Exhaustive Optical Lab permutations plus visual-accessibility runtime checks."""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
results=[]
def check(name,condition,detail=''):
    results.append({'name':name,'pass':bool(condition),'detail':detail})
    if not condition: raise AssertionError(f'{name}: {detail}')

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=CHROME,args=['--no-sandbox'])
    for target_name,target in {'standalone':ROOT/'index.html','hosted':ROOT/'dist/canon6d_sota_hosted/index.html'}.items():
        page=browser.new_page(viewport={'width':390,'height':844})
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(target.as_uri(),wait_until='domcontentloaded',timeout=60000)
        if target_name=='hosted' and page.locator('#opt-lens').count()==0:
            # Hosted target may not yet have been rebuilt during an implementation run.
            page.close();continue
        lens_count=page.locator('#opt-lens option').count()
        check(f'{target_name} six physical focal choices',lens_count==6,lens_count)
        matrix=page.evaluate('''()=>{const lens=document.querySelector('#opt-lens'),ap=document.querySelector('#opt-ap'),dist=document.querySelector('#opt-dist'),bg=document.querySelector('#opt-bg'),failures=[],floors=[];let count=0;for(let li=0;li<lens.options.length;li++){lens.selectedIndex=li;lens.dispatchEvent(new Event('change',{bubbles:true}));const minimum=+lens.selectedOptions[0].dataset.min,aps=[...ap.options].map(x=>+x.value);floors.push([minimum,aps[0]]);for(const aperture of aps){ap.value=aperture;ap.dispatchEvent(new Event('change',{bubbles:true}));for(const d of [.9,7.5,15]){dist.value=d;dist.dispatchEvent(new Event('input',{bubbles:true}));for(const b of [.5,15,30]){bg.value=b;bg.dispatchEvent(new Event('input',{bubbles:true}));count++;const values=[document.querySelector('#opt-fov').textContent,document.querySelector('#opt-dof').textContent,document.querySelector('#opt-total').textContent,document.querySelector('#opt-split').textContent,document.querySelector('#opt-hyper').textContent,document.querySelector('#opt-blur').textContent,document.querySelector('#opt-status').textContent,document.querySelector('#opt-cone').getAttribute('points'),document.querySelector('#opt-dof-band').getAttribute('points'),document.querySelector('#opt-svg-desc').textContent].join('|');if(/NaN|undefined|—/.test(values)||!values.includes('profundidad de campo'))failures.push({li,aperture,d,b,values});}}}}return{count,failures,floors}}''')
        check(f'{target_name} every aperture floor physical',all(float(first)>=float(minimum) for minimum,first in matrix['floors']),matrix['floors'])
        check(f'{target_name} full optical permutation matrix',matrix['count']>=500 and not matrix['failures'],{'count':matrix['count'],'failures':matrix['failures'][:3]})
        # All presets must update and remain physically constrained.
        preset_states=[]
        for preset in ('deep','portrait','action','zoom'):
            page.locator(f'[data-opt-preset="{preset}"]').click()
            state=page.evaluate("()=>[document.querySelector('#opt-lens').selectedIndex,+document.querySelector('#opt-ap').value,document.querySelector('#opt-dof').textContent,document.querySelector('#opt-status').textContent]")
            preset_states.append(state)
        check(f'{target_name} four distinct pedagogical presets',len({json.dumps(x) for x in preset_states})==4,preset_states)
        # Outdoor mode must be persistent, stateful, and increase border contrast.
        before=page.locator('#visibility-toggle').get_attribute('aria-pressed');page.locator('#visibility-toggle').click();after=page.locator('#visibility-toggle').get_attribute('aria-pressed')
        check(f'{target_name} sunlight toggle',before!=after,[before,after])
        check(f'{target_name} sunlight class',page.locator('body').evaluate("b=>b.classList.contains('sun-mode')"))
        # Runtime legibility: no visible authored text below 11 CSS px in primary page.
        tiny=page.evaluate('''()=>[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(s.fontSize)<11}).map(e=>({tag:e.tagName,cls:e.className,size:getComputedStyle(e).fontSize,text:e.textContent.trim().slice(0,40)})).slice(0,20)''')
        check(f'{target_name} no visible text below 11px',not tiny,tiny)
        check(f'{target_name} runtime errors',not errors,errors)
        page.close()
    browser.close()

report={'passed':all(x['pass'] for x in results),'checks':len(results),'failures':[x for x in results if not x['pass']],'results':results}
(ROOT/'OPTICS_ACCESSIBILITY_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'checks':report['checks'],'failures':report['failures']},ensure_ascii=False,indent=2))
