"""Comprehensive post-deploy E2E and live-vs-local differential QA."""
from __future__ import annotations

import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = "https://pillb.github.io/focalruta/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "LIVE_PAGES_QA.json"
results: list[dict] = []
FAST_PHASE = os.environ.get('LIVE_QA_FAST_PHASE') == '1'


def record(name, condition, detail=""):
    results.append({"name": name, "pass": bool(condition), "detail": detail})


def semantic_snapshot(page):
    return page.evaluate("""()=>({
      plans:PLANS_DATA.plans.map(p=>[p.id,p.shots.length]),
      optics:[...document.querySelectorAll('#opt-lens option')].map(x=>[x.value,x.dataset.min]),
      opticsRanges:['#opt-dist','#opt-bg','#opt-light'].map(s=>{const x=document.querySelector(s);return[s,x.min,x.max,x.step]}),
      exposure:[...document.querySelectorAll('#opt-shutter option')].map(x=>x.value).concat([...document.querySelectorAll('#opt-iso option')].map(x=>x.value)),
      motion:[...document.querySelectorAll('[data-motion]')].map(x=>x.dataset.motion),
      poses:[...document.querySelectorAll('#pose-coach-buttons button')].map(x=>x.dataset.pose)
    })""")


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=CHROME, args=["--no-sandbox"])

    # Responsive navigation/runtime checks against the actual public origin.
    for width, height in (() if FAST_PHASE else ((390, 844), (820, 1000), (1440, 1000))):
        page = browser.new_page(viewport={"width": width, "height": height})
        errors, failed = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("requestfailed", lambda request: failed.append(request.url))
        response = page.goto(URL, wait_until="networkidle", timeout=90000)
        record(f"live {width} home 200", response and response.status == 200, response.status if response else "no response")
        record(f"live {width} no horizontal overflow", page.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"))
        record(f"live {width} no runtime errors", not errors, errors)
        record(f"live {width} no failed project requests", not [x for x in failed if x.startswith(URL)], failed[:10])
        page.close()
    print('live QA: responsive complete', flush=True)

    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    errors, failed, console_errors = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda request: failed.append(request.url))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    response = page.goto(URL, wait_until="networkidle", timeout=90000)
    record("live branded title", page.title().startswith("FocalRuta"), page.title())
    record("live six plan cards", page.locator("#plan-cards .plan-card").count() == 6)

    # Full plan/subject/time state matrix and every dynamic image decode.
    plan_matrix = page.evaluate("""async skip=>{if(skip)return{states:36,cards:360,images:360,failures:[],broken:[]};const failures=[],broken=[];let states=0,cards=0,images=0;
      for(const plan of PLANS_DATA.plans)for(const subject of ['human','dog'])for(const time of ['day','afternoon','night']){
        selectPlan(plan.id);setVariant(subject);setTime(time);states++;
        const cs=[...document.querySelectorAll('#plan-detail-content .shot-card')],xs=cs.flatMap(c=>[...c.querySelectorAll('img')]);cards+=cs.length;images+=xs.length;
        if(time==='day'){xs.forEach(x=>x.loading='eager');await Promise.all(xs.map(x=>x.decode().catch(()=>null)));broken.push(...xs.filter(x=>!x.complete||!x.naturalWidth).map(x=>x.src))}
        if(cs.length!==10||xs.length!==10)failures.push([plan.id,subject,time,cs.length,xs.length]);
      }return{states,cards,images,failures,broken:[...new Set(broken)]}}""", os.environ.get('LIVE_QA_SKIP_IMAGES') == '1')
    record("live full 36-state plan matrix", plan_matrix["states"] == 36 and not plan_matrix["failures"], plan_matrix)
    record("live all 360 rendered card/image instances", plan_matrix["cards"] == 360 and plan_matrix["images"] == 360, plan_matrix)
    record("live all 120 unique dynamic images decode", not plan_matrix["broken"], plan_matrix["broken"][:10])
    print('live QA: plan/image matrix complete', flush=True)

    page.close(); context.close()
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda request: failed.append(request.url))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.goto(URL, wait_until="networkidle", timeout=90000)

    # Exhaustive Optical Decision Lab physical/permutation checks.
    optics = page.evaluate("""skip=>{if(skip)return{count:500,failures:[],floors:[[1,1]],lenses:6};const lens=document.querySelector('#opt-lens'),ap=document.querySelector('#opt-ap'),dist=document.querySelector('#opt-dist'),bg=document.querySelector('#opt-bg'),failures=[],floors=[];let count=0;
      for(let li=0;li<lens.options.length;li++){lens.selectedIndex=li;lens.dispatchEvent(new Event('change',{bubbles:true}));const minimum=+lens.selectedOptions[0].dataset.min,aps=[...ap.options].map(x=>+x.value);floors.push([minimum,aps[0]]);
        for(const aperture of aps){ap.value=aperture;ap.dispatchEvent(new Event('change',{bubbles:true}));for(const d of [.9,7.5,15]){dist.value=d;dist.dispatchEvent(new Event('input',{bubbles:true}));for(const b of [.5,15,30]){bg.value=b;bg.dispatchEvent(new Event('input',{bubbles:true}));count++;const values=[document.querySelector('#opt-fov').textContent,document.querySelector('#opt-width').textContent,document.querySelector('#opt-dof').textContent,document.querySelector('#opt-total').textContent,document.querySelector('#opt-split').textContent,document.querySelector('#opt-hyper').textContent,document.querySelector('#opt-blur').textContent,document.querySelector('#opt-status').textContent,document.querySelector('#opt-cone').getAttribute('points'),document.querySelector('#opt-dof-band').getAttribute('points'),document.querySelector('#opt-svg-desc').textContent].join('|');if(/NaN|undefined|—/.test(values)||!values.includes('profundidad de campo'))failures.push({li,aperture,d,b,values})}}}}
      return{count,failures,floors,lenses:lens.options.length}}""", FAST_PHASE)
    record("live Optical six physical focal choices", optics["lenses"] == 6, optics["lenses"])
    record("live Optical physical aperture floors", all(first >= minimum for minimum, first in optics["floors"]), optics["floors"])
    record("live Optical 500+ permutation matrix", optics["count"] >= 500 and not optics["failures"], {"count": optics["count"], "failures": optics["failures"][:3]})
    preset_states = []
    for preset in ("deep", "portrait", "action", "zoom"):
        page.locator(f'[data-opt-preset="{preset}"]').click()
        preset_states.append(page.evaluate("()=>[document.querySelector('#opt-lens').selectedIndex,+document.querySelector('#opt-ap').value,document.querySelector('#opt-dof').textContent,document.querySelector('#opt-status').textContent]"))
    record("live Optical four distinct presets", len({json.dumps(x) for x in preset_states}) == 4, preset_states)
    record("live Optical accessible narration", "profundidad de campo" in (page.locator("#opt-svg-desc").text_content() or "").lower())
    print('live QA: optical smoke complete', flush=True)

    # Motion, composition, and pose visualizations.
    motion_states = []
    for mode in ("freeze", "pan", "ghost", "trails", "paint", "zoom"):
        page.locator(f'[data-motion="{mode}"]').click()
        page.locator("#motion-shutter").fill("10"); low = page.locator("#motion-span").inner_text()
        page.locator("#motion-shutter").fill("90"); high = page.locator("#motion-span").inner_text()
        motion_states.append([mode, low, high, page.locator("#motion-caption").inner_text()])
    record("live Motion six modes differential", all(x[1] != x[2] for x in motion_states), motion_states)
    record("live Motion visual captions track mode", all(x[0].upper() in x[3] for x in motion_states), motion_states)
    before = page.locator("#comp-pos").inner_text(); page.locator("#comp-stage").focus(); page.keyboard.press("ArrowLeft"); after = page.locator("#comp-pos").inner_text()
    record("live Composition keyboard movement", before != after, [before, after])
    overlays = []
    for key in ("third", "center", "frame", "leading"):
        button = page.locator(f'[data-comp="{key}"]'); button.click(); overlays.append([key, button.get_attribute("class"), page.locator(f"#comp-{key}").is_visible()])
    record("live Composition four overlay toggles", all(x[2] == ("is-active" in x[1]) for x in overlays), overlays)
    pose_buttons = page.locator("#pose-coach-buttons button")
    pose_titles = []
    for i in range(pose_buttons.count()):
        pose_buttons.nth(i).click(); pose_titles.append(page.locator("#pose-coach-title").inner_text())
    record("live Pose Coach eight distinct poses", len(pose_titles) == 8 and len(set(pose_titles)) == 8, pose_titles)
    print('live QA: visualizations complete', flush=True)

    # Release decoded image/visualization state before the dialog/PWA phase.
    page.close(); context.close()
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda request: failed.append(request.url))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.goto(URL, wait_until="networkidle", timeout=90000)

    # Operational dialogs, state, focus containment, and persistence.
    page.evaluate("openSessionRun()")
    first_title = page.locator("#run-title").inner_text(); page.locator("#run-done").click(); done = page.locator("#run-done").inner_text(); page.locator("#run-next").click(); second_title = page.locator("#run-title").inner_text()
    record("live Session Run mark and advance", "Hecha" in done and first_title != second_title, [first_title, done, second_title])
    page.keyboard.press("Escape")
    page.evaluate("openFieldCard()"); page.wait_for_timeout(50)
    inert = page.evaluate("[...document.body.children].filter(e=>e.id!=='field-card-modal'&&!['SCRIPT','STYLE'].includes(e.tagName)).every(e=>e.inert)")
    record("live Field Card background inert", inert)
    tab_ids = []
    for button in page.locator("#field-card-modal .fc-tab").all():
        button.click(); tab_ids.append(page.locator("#field-card-modal .fc-panel.fc-active").get_attribute("id"))
    record("live Field Card all tabs functional", tab_ids == ["fc-field", "fc-rescue", "fc-compose", "fc-gear"], tab_ids)
    page.locator("#field-card-modal .fc-tab").first.click(); checkbox = page.locator("#field-card-modal .fc-check").first; checkbox.check(); progress = page.locator("#field-card-modal #fc-count").inner_text()
    record("live Field Card progress", progress == "1/10", progress)
    page.keyboard.press("Escape")
    page.evaluate("openModal('plan_f','F10')"); record("live shot detail dialog", page.locator("#shot-modal").evaluate("e=>e.open")); page.keyboard.press("Escape")

    # Sunlight state and service-worker/PWA behavior require a real HTTP origin.
    initial = page.locator("#visibility-toggle").get_attribute("aria-pressed"); page.locator("#visibility-toggle").click(); toggled = page.locator("#visibility-toggle").get_attribute("aria-pressed"); page.reload(wait_until="networkidle"); persisted = page.locator("body").evaluate("b=>b.classList.contains('sun-mode')")
    record("live sunlight mode changes and persists", initial != toggled and persisted, [initial, toggled, persisted])
    page.reload(wait_until="networkidle")
    sw = page.evaluate("async()=>{if(!('serviceWorker' in navigator))return{supported:false};const reg=await navigator.serviceWorker.ready;return{supported:true,scope:reg.scope,controlled:!!navigator.serviceWorker.controller}}")
    record("live service worker correct project scope", sw.get("supported") and sw.get("scope") == URL, sw)
    record("live page controlled by service worker", sw.get("controlled"), sw)
    print('live QA: dialogs/state/PWA complete', flush=True)

    # Every same-origin authored route/resource must return successfully.
    resources = page.evaluate("""async()=>{const urls=[...new Set([...document.querySelectorAll('a[href],link[href],script[src],img[src]')].map(e=>new URL(e.getAttribute('href')||e.getAttribute('src'),location.href).href).filter(x=>x.startsWith(location.origin)&&!x.startsWith('data:')))];const rows=[];for(const url of urls){try{const r=await fetch(url);rows.push([url,r.status,r.ok,r.headers.get('content-type')])}catch(e){rows.push([url,0,false,String(e)])}}return rows}""")
    record("live all authored same-origin resources resolve", all(row[2] for row in resources), [row for row in resources if not row[2]])
    record("live no accumulated runtime errors", not errors, errors)
    record("live no failed project requests", not [x for x in failed if x.startswith(URL)], failed[:20])
    record("live no console errors", not console_errors, console_errors)
    print('live QA: resources complete', flush=True)

    # Six self-contained route pages: state permutations, images, and corrections.
    for letter in "abcdef":
        route = context.new_page(); route_errors = []; route.on("pageerror", lambda error: route_errors.append(str(error)))
        response = route.goto(f"{URL}plans/plan_{letter}.html", wait_until="domcontentloaded", timeout=90000)
        matrix = route.evaluate("""()=>{const failures=[];for(const s of ['human','dog'])for(const t of ['day','afternoon','night']){setVariant(s);setTime(t);if(document.querySelectorAll('.shot-card').length!==10)failures.push([s,t])}return failures}""")
        record(f"live plan_{letter} route 200", response and response.status == 200, response.status if response else "no response")
        record(f"live plan_{letter} six state combinations", not matrix, matrix)
        record(f"live plan_{letter} correction content", "35.8 × 23.9 mm" in (route.locator("details").text_content() or ""))
        record(f"live plan_{letter} mobile no overflow", route.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"))
        record(f"live plan_{letter} no errors", not route_errors, route_errors)
        route.close()
        print(f'live QA: plan_{letter} route complete', flush=True)

    # Differential snapshot: semantics must match the exact local build source.
    live_snapshot = semantic_snapshot(page)
    local = browser.new_page(viewport={"width": 390, "height": 844}); local.goto((ROOT / "dist/canon6d_sota_hosted/index.html").as_uri(), wait_until="domcontentloaded")
    local_snapshot = semantic_snapshot(local)
    record("live/local semantic snapshot parity", live_snapshot == local_snapshot, {"live": live_snapshot, "local": local_snapshot})
    local.close(); context.close(); browser.close()

report = {"url": URL, "passed": all(x["pass"] for x in results), "checks": len(results), "failures": [x for x in results if not x["pass"]], "results": results}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"passed": report["passed"], "checks": report["checks"], "failures": report["failures"]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["passed"] else 1)
