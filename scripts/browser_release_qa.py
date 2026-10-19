"""Fresh browser matrix for current standalone, hosted and individual-plan targets."""
from __future__ import annotations

import functools
import json
import re
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit
from playwright.sync_api import sync_playwright
import evidence
import qa_matrix
import reading_floor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "CURRENT_BROWSER_QA.json"
# Every artefact this matrix actually loads, fingerprinted into the report.
AUDITED = [
    ROOT / "index.html",
    ROOT / "dist/canon6d_sota_hosted/index.html",
    ROOT / "field_card.html",
    ROOT / "dist/canon6d_sota_hosted/field_card.html",
    ROOT / "data/plans.json",
    *sorted((ROOT / "plans").glob("plan_*.html")),
    *sorted((ROOT / "dist/canon6d_sota_hosted/plans").glob("plan_*.html")),
    ROOT / "dist/canon6d_sota_hosted/sw.js",
]
results = []


def record(name, passed, detail=""):
    results.append({"name": name, "pass": bool(passed), "detail": detail})
    if not passed:
        raise AssertionError(f"{name}: {detail}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        # No HTTP caching: otherwise Chromium's heuristic freshness answers
        # "offline" requests from its disk cache and the worker is never tested.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


# Settle every image on load or error (a cache miss offline ends in error), then
# list the ones without pixels. decode() alone can reject on a slow load.
DECODE_ALL = """async()=>{const xs=[...document.querySelectorAll('.shot-card img')];xs.forEach(x=>x.loading='eager');
await Promise.all(xs.map(x=>x.complete?null:new Promise(done=>{x.addEventListener('load',done,{once:true});x.addEventListener('error',done,{once:true});setTimeout(done,20000)})));
return xs.filter(x=>!x.naturalWidth).map(x=>x.src.split('/').pop())}"""
# The worker keys every copy by its revision (path?__rev=…), so compare paths, not URLs.
WARMED = """async()=>{let n=0;for(const k of await caches.keys()){for(const r of await (await caches.open(k)).keys()){if(new URL(r.url).pathname.endsWith('.webp'))n++}}
return n>=20&&!!(await caches.match(location.href,{ignoreSearch:true}))}"""


def wait_until(page, predicate: str, timeout_s: float = 30.0) -> None:
    """Poll an async predicate. page.wait_for_function treats a returned Promise
    as truthy and returns at once (checked against Playwright 1.55), so a
    predicate that reads the Cache API must be awaited through page.evaluate."""
    deadline = time.monotonic() + timeout_s
    while not page.evaluate(predicate):
        if time.monotonic() > deadline:
            raise TimeoutError(f"still false after {timeout_s:.0f} s: {predicate[:80]}")
        page.wait_for_timeout(250)


def hosted_plan_offline(browser):
    """U05: a hosted plan page visited once works offline, both subjects, all ten diagrams."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT / "dist/canon6d_sota_hosted")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.goto(f"http://127.0.0.1:{server.server_address[1]}/plans/plan_a.html", wait_until="load", timeout=60000)
    page.wait_for_function("navigator.serviceWorker.controller!==null", timeout=30000)
    wait_until(page, WARMED, 30)
    # Stop the server rather than emulate offline: Chromium's offline emulation
    # does not reach requests the service worker makes, so it cannot fail.
    server.shutdown()
    server.server_close()
    page.reload(wait_until="load")
    record("hosted plan_a offline after one visit: page itself", "plan-orientation" in page.content())
    for subject in ("human", "dog"):
        page.evaluate("s=>setVariant(s)", subject)
        missing = page.evaluate(DECODE_ALL)
        count = page.locator(".shot-card img").count()
        record(f"hosted plan_a offline after one visit: {subject} diagrams decode", count == 10 and not missing, missing)
    context.close()


PANEL_FLOOR = """(panel)=>{const small=[],tiny=[];for(const e of document.querySelectorAll(panel+', '+panel+' *')){const r=e.getBoundingClientRect();
if(!r.width||!r.height)continue;if([...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(getComputedStyle(e).fontSize)<12)small.push(e.tagName);
if(e.matches('summary,button,a')&&(r.width<44||r.height<44))tiny.push(e.textContent.trim().slice(0,20))}return {small,tiny}}"""


def error_log(browser):
    """X04: failures on a plan page reach the home page's log, cleaned, and nothing is sent."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT / "dist/canon6d_sota_hosted")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    context = browser.new_context(viewport={"width": 390, "height": 844})
    sent = []
    context.on("request", lambda request: sent.append(request.method + " " + request.url))
    plan = context.new_page()
    plan.goto(base + "plans/plan_b.html?token=secreto#x", wait_until="networkidle", timeout=60000)
    sent.clear()
    # Both fire after evaluate returns: Playwright would otherwise await the rejected promise itself.
    plan.evaluate("setTimeout(()=>{throw new Error('prueba del registro https://example.org/a?clave=1')},0);"
                  "setTimeout(()=>{Promise.reject(new Error('promesa de prueba'))},0)")
    plan.wait_for_timeout(500)
    record("error log: a thrown error and a rejected promise send no request", sent == [], sent)
    home = context.new_page()
    home.goto(base, wait_until="load", timeout=60000)
    home.locator("#diag > summary").click()
    items = home.locator("#diag-list li").all_inner_texts()
    record("error log: the home page lists both, with the page they came from",
           len(items) == 2 and all("/plans/plan_b.html" in item for item in items)
           and any("prueba del registro https://example.org/a" in item for item in items), items)
    stored = home.evaluate("localStorage.getItem('focalruta-errores-v1')")
    record("error log: no query string, fragment or browser identity is kept",
           not re.search(r"secreto|clave|token|Mozilla|HeadlessChrome", stored), stored)
    record("error log: the report link carries the log to a new GitHub issue",
           (home.locator("#diag-report").get_attribute("href") or "").startswith("https://github.com/PillB/focalruta/issues/new?")
           and "promesa de prueba" in parse_qs(urlsplit(home.locator("#diag-report").get_attribute("href")).query)["body"][0])
    floor = home.evaluate(PANEL_FLOOR, "#diag")
    record("error log: 12 px text and 44 px controls in the open panel", not floor["small"] and not floor["tiny"], floor)
    # Without a clipboard (an older browser, a page opened from a file) «Copiar» did nothing at all
    # (red team on PR #21, F7): it now says so and selects the log, ready to copy by hand.
    home.evaluate("Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true})")
    home.locator("#diag-copy").click()
    said, selected = home.locator("#diag-copy").inner_text().strip(), home.evaluate("String(getSelection())")
    record("error log: without a clipboard, «Copiar» says so and selects the log",
           said == "Selecciona y copia el texto" and "promesa de prueba" in selected, [said, selected[:80]])
    home.locator("#diag-clear").click()
    kept = home.locator("#diag-list li").count()
    home.locator("#diag-clear").click()
    record("error log: clearing takes a second tap", kept == 2 and home.locator("#diag-list li").count() == 0
           and home.locator("#diag-empty").is_visible(), kept)
    context.close()
    server.shutdown()


NOTICE = "#offline-notice"
# The home page's own stylesheet, as the page applied it: the copy served under another
# path resolved it under that path and got nothing.
LANDED = """(base)=>({path:location.pathname+location.search,
rules:[...document.styleSheets].filter(s=>s.href&&s.href.startsWith(base+'assets/hosted.css')).map(s=>{try{return s.cssRules.length}catch(e){return -1}})})"""
# The last one is well formed but no page of the site: Pages is case-sensitive, so its link
# would lead nowhere (red team on PR #21, F6).
FORGED = ("javascript:alert(1)", "//example.org/x.html", "<img src=x onerror=alert(1)>.html", "../../x.html", "plans/plan_c.html#x",
          "plans/PLAN_C.html")


def unsaved_page_offline(browser):
    """Live check of 56a6e97, M7: offline, a page never saved opens the home page, which says
    which page it was and links back to it and to the field card; a forged name shows nothing."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT / "dist/canon6d_sota_hosted")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    context = browser.new_context(viewport={"width": 320, "height": 640})
    page = context.new_page()
    shown = []
    for forged in FORGED:
        page.goto(base + "index.html?sin-conexion=" + quote(forged, safe=""), wait_until="domcontentloaded", timeout=60000)
        if page.locator(NOTICE).is_visible():
            shown.append([forged, page.evaluate("s=>[...document.querySelectorAll(s+' a')].map(a=>a.href)", NOTICE)])
    record("offline notice: a forged page name shows nothing", not shown, shown)
    page.goto(base, wait_until="load", timeout=60000)
    page.wait_for_function("navigator.serviceWorker.controller!==null", timeout=30000)
    # A real cut, as in U05: Chromium's offline emulation does not reach the worker's own requests.
    server.shutdown()
    server.server_close()
    for path, name in (("plans/plan_c.html", "el plan C"), ("challenges/arquitectura-en-foco/wiki-tecnicas.html", "«wiki-tecnicas»")):
        page.goto(base + path, wait_until="load", timeout=60000)
        landed = page.evaluate(LANDED, base)
        record(f"offline: {path}, never saved, opens the styled home page", landed["path"] == "/index.html"
               and len(landed["rules"]) == 1 and landed["rules"][0] > 100, landed)
        notice = page.locator(NOTICE)
        said = notice.inner_text() if notice.is_visible() else None
        links = page.evaluate("s=>[...document.querySelectorAll(s+' a')].map(a=>a.href)", NOTICE)
        record(f"offline: the home page says {name} was not saved, with links back to it and to the field card",
               bool(said) and name in said and links == [base + path, base + "field_card.html"], [said, links])
        floor = page.evaluate(PANEL_FLOOR, NOTICE)
        fits = page.evaluate("s=>{const n=document.querySelector(s),d=document.documentElement;"
                             "return !!n&&n.scrollWidth<=n.clientWidth&&d.scrollWidth<=d.clientWidth}", NOTICE)
        record(f"offline notice for {path} at 320 px: 12 px text, 44 px controls, nothing past the edge",
               bool(said) and not floor["small"] and not floor["tiny"] and fits, [floor, fits])
    context.close()


# V19: each dialog opened from the button a reader would press keeps the rest of the
# page out of reach while open (a native modal, or everything else inert), then, closed
# with Escape, hands focus back to that button and leaves nothing on the page inert.
DIALOGS = (
    ("session", "button[onclick='openSessionRun()']:visible", "#session-run-dialog"),
    ("field card", "button[onclick='openFieldCard()']:visible", "#field-card-modal"),
    ("shot", "#plan-detail-content button[onclick^='openModal(']:visible", "#shot-modal"),
)
FOCUS_INSIDE = "(d)=>{const m=document.querySelector(d);return !!m&&m.contains(document.activeElement)}"
AFTER_ESCAPE = """(d)=>{const m=document.querySelector(d);return {closed:!(m.open||m.classList.contains('fc-modal-open')),
back:document.activeElement?.dataset.qaTrigger==='1',inert:[...document.querySelectorAll('[inert]')].map(e=>e.id||e.tagName)}}"""
# Blocked: the dialog is :modal, or every other child of <body> is inert.
BLOCKS_THE_REST = """(d)=>{const m=document.querySelector(d),rest=[...document.body.children].filter(el=>!el.contains(m)&&!['SCRIPT','STYLE','TEMPLATE'].includes(el.tagName));
return {modal:m.matches(':modal'),rest_inert:rest.every(el=>el.inert)}}"""
# Where Tab leaves focus: outside the dialog counts only if it lands on the page, not the browser.
FOCUS_ESCAPED = "(d)=>{const m=document.querySelector(d),a=document.activeElement;return !!a&&a!==document.body&&!m.contains(a)?(a.id||a.tagName):''}"
TABS = 30


def keeps_the_rest_out_of_reach(page, dialog):
    blocked = page.evaluate(BLOCKS_THE_REST, dialog)
    escaped = []
    for _ in range(TABS):
        page.keyboard.press("Tab")
        escaped.append(page.evaluate(FOCUS_ESCAPED, dialog))
    escaped = sorted({e for e in escaped if e})
    return (blocked["modal"] or blocked["rest_inert"]) and not escaped, {**blocked, "tab_reached": escaped}


def dialogs_give_focus_back(page, target_name):
    for name, trigger, dialog in DIALOGS:
        button = page.locator(trigger).first
        button.evaluate("b=>{document.querySelectorAll('[data-qa-trigger]').forEach(x=>delete x.dataset.qaTrigger);b.dataset.qaTrigger='1'}")
        button.click()
        record(f"{target_name} {name} dialog takes focus from its button", page.evaluate(FOCUS_INSIDE, dialog))
        record(f"{target_name} {name} dialog keeps the rest of the page out of reach while open",
               *keeps_the_rest_out_of_reach(page, dialog))
        page.keyboard.press("Escape")
        after = page.evaluate(AFTER_ESCAPE, dialog)
        record(f"{target_name} {name} dialog closes on Escape and gives focus back", after["closed"] and after["back"] and not after["inert"], after)


# V18 with a reader's own gear: lens names as long as real ones, which a select
# sizes itself to (red team, second pass on PR #20). 375 px is the iPhone SE and mini.
LONG_GEAR = {"body": "apsc_canon", "iso": 12800, "lenses": [
    {"name": "Zoom de kit 18–55 mm f/3.5–5.6", "min": 18, "max": 55, "wide": 3.5, "tele": 5.6},
    {"name": "Teleobjetivo de viaje 70–300 mm f/4.5–6.3 con estabilizador", "min": 70, "max": 300, "wide": 4.5, "tele": 6.3}]}
LONG_GEAR_WIDTHS = (320, 375)


def long_gear_page(browser, width, path):
    context = browser.new_context(viewport={"width": width, "height": 640})
    context.add_init_script(f"try{{localStorage.setItem('focalruta-equipo-v1',{json.dumps(json.dumps(LONG_GEAR))})}}catch(e){{}}")
    page = context.new_page()
    page.goto((ROOT / path).as_uri(), wait_until="load", timeout=60000)
    return context, page


def field_card_floor(page) -> dict:
    page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    return {"cut": page.evaluate(reading_floor.CUT_OFF, ""), "numbers": reading_floor.numbers_in(page.evaluate(reading_floor.SHOWN_WORDS, ""))}


def record_long_gear(path, width, floor):
    record(f"{path} {width} with long lens names: nothing cut off", not floor["cut"], floor["cut"][:12])
    # V20: the "Con tu equipo" lines are written only for a reader's own gear.
    record(f"{path} {width} with your own gear: numbers written the Peruvian way", not floor["numbers"], floor["numbers"][:12])


def nothing_cut_with_long_gear(browser):
    for width in LONG_GEAR_WIDTHS:
        for path in ("index.html", "dist/canon6d_sota_hosted/index.html"):
            context, page = long_gear_page(browser, width, path)
            record_long_gear(path, width, reading_floor.audit_home(page))
            context.close()
    for path in ("dist/canon6d_sota_hosted/field_card.html", *[f"dist/canon6d_sota_hosted/plans/plan_{x}.html" for x in "abcdef"]):
        context, page = long_gear_page(browser, LONG_GEAR_WIDTHS[0], path)
        floor = reading_floor.audit_plan_page(page) if "plans/" in path else field_card_floor(page)
        record_long_gear(path, LONG_GEAR_WIDTHS[0], floor)
        context.close()


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=["--no-sandbox"], **qa_matrix.browser_options())
    targets = {
        "standalone": ROOT / "index.html",
        "hosted": ROOT / "dist/canon6d_sota_hosted/index.html",
    }
    for target_name, target in targets.items():
        for width, height in qa_matrix.REQUIRED_VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(target.as_uri(), wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(150)
            record(f"{target_name} {width} no overflow", page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"))
            record(f"{target_name} {width} no page errors", not errors, errors)
            page.close()

        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(target.as_uri(), wait_until="domcontentloaded", timeout=60000)
        for plan in [f"plan_{letter}" for letter in "abcdef"]:
            for subject in ("human", "dog"):
                for slot in ("day", "afternoon", "night"):
                    count = page.evaluate("([p,s,t])=>{selectPlan(p);setVariant(s);setTime(t);return document.querySelectorAll('#plan-detail-content .shot-card').length}", [plan, subject, slot])
                    record(f"{target_name} {plan}/{subject}/{slot} ten cards", count == 10, count)
                    image_count = page.locator("#plan-detail-content .shot-card img").count()
                    record(f"{target_name} {plan}/{subject}/{slot} ten diagrams", image_count == 10, image_count)
        motion = []
        for mode in ("freeze", "pan", "ghost", "trails", "paint", "zoom"):
            page.locator(f'[data-motion="{mode}"]').click()
            page.locator("#motion-shutter").fill("10")
            low = page.locator("#motion-span").inner_text()
            page.locator("#motion-shutter").fill("90")
            high = page.locator("#motion-span").inner_text()
            motion.append([mode, low, high])
            record(f"{target_name} motion {mode} differential", low != high, [low, high])
        before = page.locator("#comp-pos").inner_text()
        page.locator("#comp-stage").focus()
        page.keyboard.press("ArrowLeft")
        record(f"{target_name} composition keyboard", before != page.locator("#comp-pos").inner_text())
        page.evaluate("openSessionRun()")
        record(f"{target_name} Session Run modal", page.locator("#session-run-dialog").evaluate("e=>e.open"))
        page.keyboard.press("Escape")
        page.evaluate("openFieldCard()")
        inert = page.evaluate("[...document.body.children].filter(e=>e.id!=='field-card-modal'&&!['SCRIPT','STYLE'].includes(e.tagName)).every(e=>e.inert)")
        record(f"{target_name} Field Card inert", inert)
        page.keyboard.press("Escape")
        page.evaluate("openModal('plan_f','F10')")
        record(f"{target_name} shot detail modal", page.locator("#shot-modal").evaluate("e=>e.open"))
        page.keyboard.press("Escape")
        dialogs_give_focus_back(page, target_name)
        record(f"{target_name} ZIP link resolves", page.locator('a[href="downloads/canon6d_photo_planner_assets.zip"]').first.evaluate("a=>new URL(a.href).protocol==='file:'"))
        record(f"{target_name} interaction errors", not errors, errors)
        page.close()

        # V10-V12: the reading floor, at every size in the matrix, in every state a reader reaches.
        for width, height in qa_matrix.REQUIRED_VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(target.as_uri(), wait_until="load", timeout=60000)
            floor = reading_floor.audit_home(page)
            record(f"{target_name} {width} no text under 12 px", not floor["small"], floor["small"][:12])
            record(f"{target_name} {width} every control at least 44 px", not floor["tiny"], floor["tiny"][:12])
            record(f"{target_name} {width} interface in Spanish", not floor["english"], floor["english"])
            record(f"{target_name} {width} numbers written the Peruvian way", not floor["numbers"], floor["numbers"][:12])
            record(f"{target_name} {width} session and shot dialogs open", not floor["unreached"], floor["unreached"])
            record(f"{target_name} {width} nothing cut off at the edges", not floor["cut"], floor["cut"][:12])
            page.close()

    narrow = browser.new_page(viewport={"width": 320, "height": 640})
    narrow.goto((ROOT / "dist/canon6d_sota_hosted/field_card.html").as_uri(), wait_until="load", timeout=60000)
    narrow.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    cut = narrow.evaluate(reading_floor.CUT_OFF, "")
    record("field_card 320 nothing cut off at the edges", not cut, cut[:12])
    narrow.close()
    for letter in "abcdef":
        narrow = browser.new_page(viewport={"width": 320, "height": 640})
        narrow.goto((ROOT / f"dist/canon6d_sota_hosted/plans/plan_{letter}.html").as_uri(), wait_until="domcontentloaded", timeout=60000)
        cut = reading_floor.audit_plan_page(narrow)["cut"]
        record(f"plan_{letter} 320 nothing cut off at the edges", not cut, cut[:12])
        narrow.close()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((ROOT / f"plans/plan_{letter}.html").as_uri(), wait_until="domcontentloaded", timeout=60000)
        for subject in ("human", "dog"):
            for slot in ("day", "afternoon", "night"):
                page.evaluate("([s,t])=>{setVariant(s);setTime(t)}", [subject, slot])
                record(f"plan_{letter} {subject}/{slot} ten cards", page.locator(".shot-card").count() == 10)
        record(f"plan_{letter} correction panel", "35.8 × 23.9 mm" in (page.locator("details").text_content() or ""))
        floor = reading_floor.audit_plan_page(page)
        record(f"plan_{letter} no text under 12 px", not floor["small"], floor["small"][:12])
        record(f"plan_{letter} every control at least 44 px", not floor["tiny"], floor["tiny"][:12])
        record(f"plan_{letter} interface in Spanish", not floor["english"], floor["english"])
        record(f"plan_{letter} numbers written the Peruvian way", not floor["numbers"], floor["numbers"][:12])
        record(f"plan_{letter} no overflow", page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"))
        record(f"plan_{letter} no errors", not errors, errors)
        page.close()
    nothing_cut_with_long_gear(browser)
    hosted_plan_offline(browser)
    unsaved_page_offline(browser)
    error_log(browser)
    browser.close()

report = {"passed": all(item["pass"] for item in results), "checks": len(results),
          "viewports": [list(viewport) for viewport in qa_matrix.REQUIRED_VIEWPORTS],
          "failures": [item for item in results if not item["pass"]], "results": results}
evidence.write_report(OUT, report, AUDITED)
print(json.dumps({"passed": report["passed"], "checks": report["checks"], "failures": report["failures"]}, ensure_ascii=False, indent=2))
