"""Optical Lab science, exhaustive authored values, and accessibility runtime QA."""
from __future__ import annotations
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
results=[]
def check(name,condition,detail=''):
    results.append({'name':name,'pass':bool(condition),'detail':detail})
    if not condition: raise AssertionError(f'{name}: {detail}')

MATRIX=r'''mode=>{const q=s=>document.querySelector(s),fire=(e,t='input')=>e.dispatchEvent(new Event(t,{bubbles:true})),lens=q('#opt-lens'),ap=q('#opt-ap'),dist=q('#opt-dist'),bg=q('#opt-bg'),light=q('#opt-light'),shutter=q('#opt-shutter'),iso=q('#opt-iso'),failures=[],floors=[];let optical=0,exposure=0;
 const valid=()=>{const text=['#opt-fov','#opt-width','#opt-dof','#opt-total','#opt-split','#opt-hyper','#opt-blur','#opt-status','#opt-exposure','#opt-svg-desc'].map(x=>q(x).textContent).join('|'),zone=q('#opt-defocus-zone'),far=q('#opt-far-line'),dots=[...q('#opt-bokeh-dots').children],r=dots.filter((_,i)=>i%4===0).map(x=>+x.getAttribute('r'));if(/NaN|undefined/.test(text)||!text.includes('profundidad de campo'))return 'invalid output';if(zone.parentElement.style.display!=='none'&&Math.abs((40 + +zone.getAttribute('height'))-(+far.getAttribute('y1')))>0.1)return 'blur threshold mismatch';if(r.some((x,i)=>i&&x<r[i-1]))return 'blur discs do not grow';return ''};
 if(mode!=='exposure')for(let li=0;li<lens.options.length;li++){lens.selectedIndex=li;fire(lens,'change');const minimum=+lens.selectedOptions[0].dataset.min,aps=[...ap.options].map(x=>+x.value);floors.push([minimum,aps[0]]);for(const n of aps){ap.value=n;fire(ap,'change');for(let d=+dist.min;d<=+dist.max+.001;d+=+dist.step){dist.value=d.toFixed(1);fire(dist);optical++;const e=valid();if(e)failures.push([li,n,d,'distance',e])}for(let b=+bg.min;b<=+bg.max+.001;b+=+bg.step){bg.value=b.toFixed(1);fire(bg);optical++;const e=valid();if(e)failures.push([li,n,b,'background',e])}}}
 lens.selectedIndex=2;fire(lens,'change');ap.value='4';fire(ap,'change');dist.value='3';fire(dist);bg.value='8';fire(bg);const geometry=()=>['#opt-cone','#opt-dof-band','#opt-near-line','#opt-focus-line','#opt-far-line','#opt-bg-line','#opt-defocus-zone','#opt-bokeh-dots'].map(x=>q(x).outerHTML).join('|'),base=geometry(),exposureStates=new Set;
 if(mode!=='optical')for(let ev=+light.min;ev<=+light.max;ev+=+light.step)for(const t of [...shutter.options].map(x=>x.value))for(const s of [...iso.options].map(x=>x.value)){light.value=ev;fire(light);shutter.value=t;fire(shutter,'change');iso.value=s;fire(iso,'change');exposure++;exposureStates.add(q('#opt-exposure-overlay').getAttribute('fill')+'|'+q('#opt-exposure-overlay').getAttribute('opacity')+'|'+q('#opt-light-label').textContent);if(geometry()!==base)failures.push([ev,t,s,'exposure changed geometry'])}
 light.value='15';fire(light);shutter.value='0.008';fire(shutter,'change');iso.value='100';fire(iso,'change');ap.value='16';fire(ap,'change');const balanced=q('#opt-exposure').textContent.includes('equilibrada');
 bg.value='2';fire(bg);const bgA=[q('#opt-bg-line').getAttribute('y1'),q('#opt-blur').textContent,q('#opt-bokeh-dots').innerHTML],fixedA=[q('#opt-dof').textContent,q('#opt-total').textContent,q('#opt-hyper').textContent];bg.value='25';fire(bg);const bgB=[q('#opt-bg-line').getAttribute('y1'),q('#opt-blur').textContent,q('#opt-bokeh-dots').innerHTML],fixedB=[q('#opt-dof').textContent,q('#opt-total').textContent,q('#opt-hyper').textContent];
 return{optical,exposure,failures,floors,exposureStates:exposureStates.size,balanced,bgChanged:JSON.stringify(bgA)!==JSON.stringify(bgB),dofFixed:JSON.stringify(fixedA)===JSON.stringify(fixedB)}}'''

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=CHROME,args=['--no-sandbox'])
    live_url=os.environ.get('OPTICS_QA_URL')
    targets={'live':live_url} if live_url else {'standalone':ROOT/'index.html','hosted':ROOT/'dist/canon6d_sota_hosted/index.html'}
    for target_name,target in targets.items():
        page=browser.new_page(viewport={'width':390,'height':844}); errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(target if isinstance(target,str) else target.as_uri(),wait_until='domcontentloaded',timeout=90000)
        check(f'{target_name} complete enhanced lab',page.locator('#opt-light').count()==1)
        mode=os.environ.get('OPTICS_QA_MODE','all'); matrix=page.evaluate(MATRIX,mode)
        if mode!='exposure':
            check(f'{target_name} every physical aperture floor',all(a>=m for m,a in matrix['floors']),matrix['floors'])
            check(f'{target_name} every authored optical slider value',matrix['optical']>=12000,{'states':matrix['optical'],'failures':matrix['failures'][:3]})
        if mode!='optical': check(f'{target_name} every exposure combination',matrix['exposure']==2093,{'states':matrix['exposure'],'visualStates':matrix['exposureStates']})
        check(f'{target_name} all state invariants',not matrix['failures'],matrix['failures'][:5])
        check(f'{target_name} exposure independence and known EV vector',matrix['balanced'])
        check(f'{target_name} background changes bokeh not DoF',matrix['bgChanged'] and matrix['dofFixed'],matrix)
        states=[]
        for preset in ('deep','portrait','action','zoom'):
            page.locator(f'[data-opt-preset="{preset}"]').click(); states.append(page.locator('#opt-svg-desc').text_content())
        check(f'{target_name} four distinct presets',len(set(states))==4,states)
        page.locator('#visibility-toggle').click()
        check(f'{target_name} sunlight mode',page.locator('body').evaluate("b=>b.classList.contains('sun-mode')"))
        tiny=page.evaluate("()=>[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(s.fontSize)<11}).map(e=>[e.tagName,getComputedStyle(e).fontSize,e.textContent.trim().slice(0,30)]).slice(0,10)")
        check(f'{target_name} no visible text below 11px',not tiny,tiny)
        check(f'{target_name} runtime errors',not errors,errors); page.close()
    browser.close()

report={'passed':all(x['pass'] for x in results),'checks':len(results),'failures':[x for x in results if not x['pass']],'results':results}
(ROOT/os.environ.get('OPTICS_QA_OUT','OPTICS_ACCESSIBILITY_QA.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'checks':report['checks'],'failures':report['failures']},ensure_ascii=False,indent=2))
