#!/usr/bin/env python3
"""Browser checks for the field card, as a reader uses it in the field.

Requirements V02-V09 and V15 (see tests/test_field_card.py and
tests/test_gear.py for the static half). The
card is served from dist/ over HTTP, the way GitHub Pages serves it, and
driven in Chromium at phone and desktop sizes, with JavaScript on and off,
with a fixed clock in Lima, under keyboard, reduced motion and print, inside
the home page's dialog, and offline with the server stopped.

Every check is recorded; the script reports all failures, not just the first,
and writes FIELD_CARD_QA.json bound to the files it audited.
"""
from __future__ import annotations

import functools
import json
import math
import shutil
import tempfile
import threading
import time
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

import deploy_rehearsal
import evidence
import qa_matrix
import reading_floor
import sun_times

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
REPORT = ROOT / "FIELD_CARD_QA.json"
DATA = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
PHONE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True}
AUDITED = [DIST / "field_card.html", DIST / "index.html", DIST / "sw.js", ROOT / "field_card.html", ROOT / "data" / "plans.json",
           deploy_rehearsal.LIVE_WORKER]
checks: list[dict] = []

TEXT_SIZES = """(root)=>{const app=document.querySelector(root);const small=[];const w=document.createTreeWalker(app,NodeFilter.SHOW_TEXT);let n;
while((n=w.nextNode())){if(!n.textContent.trim())continue;const el=n.parentElement;const r=el.getBoundingClientRect();
if(!el.getClientRects().length||r.width<=1||r.height<=1)continue;const fs=parseFloat(getComputedStyle(el).fontSize);
if(fs<12)small.push(fs+'px '+n.textContent.trim().slice(0,30))}return small}"""
TARGETS = """(root)=>{const bad=[];for(const el of document.querySelectorAll(root+' :is(label.fc-option,label.fc-tab,.fc-check-wrap,button,summary,label.fc-toggle,label.fc-date,input[type=date])')){
const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;if(r.width<43.5||r.height<43.5)bad.push((el.textContent||el.className).trim().slice(0,24)+' '+Math.round(r.width)+'x'+Math.round(r.height))}return bad}"""
FIRST_SLOT = """(root)=>{const s=[...document.querySelectorAll(root+' .fc-slot')].filter(e=>e.getClientRects().length);
return {count:s.length,plans:[...new Set(s.map(e=>e.dataset.plan))],slots:[...new Set(s.map(e=>e.dataset.slot))],
first:s[0]&&{shot:s[0].dataset.shot,exposure:s[0].querySelector('.fc-v-exposure').textContent,when:s[0].querySelector('.fc-when').textContent}}}"""
CHOSEN = "(name)=>{const r=document.querySelector(`#field-card-app input[name=${name}]:checked`);return r&&r.value}"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        # No HTTP caching: otherwise Chromium's heuristic freshness answers
        # "offline" requests from its disk cache and the worker is never tested.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def check(name: str, passed: bool, detail=None) -> bool:
    checks.append({"name": name, "pass": bool(passed), "detail": detail})
    print(("✓ " if passed else "✗ ") + name + ("" if passed else f": {detail}"), flush=True)
    return bool(passed)


def serve(handler=QuietHandler) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(handler, directory=str(DIST)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def expected(plan_id: str, slot: str) -> dict:
    plan = next(p for p in DATA["plans"] if p["id"] == plan_id)
    shot = plan["shots"][0]
    s = shot["settings_by_time"][slot]
    return {"shot": shot["id"], "exposure": f"{s['aperture']} · {s['shutter']} · ISO {s['iso']}"}


def pick(page, name: str, value: str, root: str = "#field-card-app") -> None:
    page.locator(f"{root} input[name={name}][value={value}]").locator("xpath=..").click()


def open_card(context, base: str, errors: list):
    page = context.new_page()
    page.set_default_timeout(10000)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.goto(base + "field_card.html", wait_until="load")
    return page


def readability(page, label: str, root: str = "#field-card-app") -> None:
    """V03 and one-handed use: text and targets in every section."""
    small, tiny = [], []
    for tab in ("shots", "techniques", "rescue", "framing", "gear"):
        pick(page, "fc-tab", tab, root)
        small += page.evaluate(TEXT_SIZES, root)
        tiny += page.evaluate(TARGETS, root)
    pick(page, "fc-tab", "shots", root)
    check(f"{label}: no text under 12 px in any section", not small, small[:8])
    check(f"{label}: every control at least 44 × 44 px", not tiny, tiny[:8])


def switching(page, label: str, root: str = "#field-card-app") -> None:
    """V02/V05: plan and light switch to that plan's exact settings."""
    pick(page, "fc-plan", "plan_c", root)
    pick(page, "fc-slot", "night", root)
    shown = page.evaluate(FIRST_SLOT, root)
    want = expected("plan_c", "night")
    check(f"{label}: plan C at night shows C01's night settings",
          shown["first"] and shown["first"]["shot"] == want["shot"] and shown["first"]["exposure"] == want["exposure"], shown["first"])
    check(f"{label}: only plan C's ten night slots are visible",
          shown["count"] == 10 and shown["plans"] == ["plan_c"] and shown["slots"] == ["night"], shown)
    pick(page, "fc-tab", "gear", root)
    check(f"{label}: packing list follows the plan",
          page.locator(f"{root} .fc-pack[data-plan=plan_c]").is_visible() and not page.locator(f"{root} .fc-pack[data-plan=plan_a]").is_visible())
    pick(page, "fc-tab", "shots", root)


def thumb_zone(page, label: str) -> None:
    def bar():
        return page.evaluate("()=>{const r=document.querySelector('.fc-tabs').getBoundingClientRect();return [r.top,r.bottom,innerHeight]}")
    top, bottom, height = bar()
    page.evaluate("window.scrollTo(0, 3000)")
    top2, bottom2, _ = bar()
    check(f"{label}: section bar stays in the bottom 15% while scrolling",
          abs(bottom - height) <= 1 and top >= 0.85 * height and abs(top2 - top) <= 1 and abs(bottom2 - bottom) <= 1, [top, bottom, top2, height])
    page.evaluate("window.scrollTo(0, 0)")


def memory(page, label: str) -> None:
    """Save and reload: plan, light, ticks and the night screen survive."""
    pick(page, "fc-plan", "plan_c")
    pick(page, "fc-slot", "night")
    page.locator(".fc-slot[data-plan=plan_c][data-slot=night] .fc-check-wrap").first.click()
    page.locator("label.fc-toggle", has_text="Pantalla de noche").click()
    page.reload(wait_until="load")
    kept = [page.evaluate(CHOSEN, "fc-plan"), page.evaluate(CHOSEN, "fc-slot"),
            page.locator(".fc-slot[data-plan=plan_c][data-slot=night] .fc-check").first.is_checked(),
            page.locator("#fc-count").inner_text(), page.locator("#fc-night").is_checked()]
    check(f"{label}: plan, light, tick and night screen survive a reload", kept == ["plan_c", "night", True, "1/10", True], kept)
    background = page.evaluate("getComputedStyle(document.querySelector('#field-card-app')).backgroundColor")
    check(f"{label}: night screen is black", background == "rgb(0, 0, 0)", background)
    page.locator("#fc-reset").click()
    page.locator("#fc-reset").click()
    check(f"{label}: reset clears this list after a second tap", page.locator("#fc-count").inner_text() == "0/10")
    page.locator("label.fc-toggle", has_text="Pantalla de noche").click()


def next_pending(page, label: str) -> None:
    pick(page, "fc-plan", "plan_a")
    pick(page, "fc-slot", "day")
    page.locator(".fc-slot[data-plan=plan_a][data-slot=day] .fc-check-wrap").first.click()
    hidden_at_top = not page.locator("#fc-next").is_visible()
    page.locator(".fc-shot[data-plan=plan_a]").nth(3).scroll_into_view_if_needed()
    page.locator("#fc-next").wait_for(state="visible", timeout=5000)
    page.locator("#fc-next").click()
    focused = page.evaluate("document.activeElement && document.activeElement.dataset.key")
    check(f"{label}: next button stays off the controls, then jumps to the first pending shot",
          hidden_at_top and focused == "plan_a/A02/day", [hidden_at_top, focused])
    page.locator(".fc-slot[data-plan=plan_a][data-slot=day] .fc-check-wrap").first.click()


def keyboard(page, label: str) -> None:
    page.focus("#field-card-app input[name=fc-plan][value=plan_a]")
    page.keyboard.press("ArrowRight")
    outline = page.evaluate("()=>{const s=document.activeElement.nextElementSibling;const c=getComputedStyle(s);return [c.outlineStyle,parseFloat(c.outlineWidth)]}")
    check(f"{label}: arrow keys move between plans with a visible focus ring",
          page.evaluate(CHOSEN, "fc-plan") == "plan_b" and outline[0] != "none" and outline[1] >= 2, outline)
    pick(page, "fc-plan", "plan_a")


def overflow(browser, base: str) -> None:
    sizes = [(320, 640), (390, 844), (430, 932), (844, 390), (1280, 800)]
    wide = []
    for width, height in sizes:
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        page.goto(base + "field_card.html", wait_until="load")
        if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"):
            wide.append(f"{width}x{height}")
        context.close()
    check("no horizontal overflow at 320, 390, 430, 844 landscape and 1280", not wide, wide)


def clock_cases(browser, base: str) -> None:
    """V06: the light slot follows the clock in Lima, whatever the phone's time zone."""
    plan = sun_times.day_plan(date(2026, 10, 17))
    day_window = f"· {sun_times.clock(plan['sunrise'])}–{sun_times.clock(plan['golden_pm_start'])}"
    for instant, slot, words in (("2026-10-17T15:00:00Z", "day", "de día"), ("2026-10-17T22:50:00Z", "afternoon", "se pone el sol"),
                                 ("2026-10-18T03:30:00Z", "night", "de noche")):
        context = browser.new_context(timezone_id="Europe/Madrid", **PHONE)
        page = context.new_page()
        page.clock.set_fixed_time(instant)
        page.goto(base + "field_card.html", wait_until="load")
        now = page.locator("#fc-now").inner_text()
        check(f"Lima {instant[11:16]}Z read from Madrid opens on {slot}", page.evaluate(CHOSEN, "fc-slot") == slot and words in now, now)
        if slot == "day":
            when = page.evaluate(FIRST_SLOT, "#field-card-app")["first"]["when"]
            check("A01's day window matches the Python ephemeris", when == day_window, [when, day_window])
        context.close()


def without_javascript(browser, base: str) -> None:
    context = browser.new_context(java_script_enabled=False, **PHONE)
    page = context.new_page()
    page.goto(base + "field_card.html", wait_until="load")
    switching(page, "no JavaScript")
    readability(page, "no JavaScript")
    context.close()


def reduced_motion_and_print(browser, base: str) -> None:
    context = browser.new_context(reduced_motion="reduce", **PHONE)
    page = context.new_page()
    page.goto(base + "field_card.html", wait_until="load")
    check("reduced motion: nothing animates", page.evaluate("document.getAnimations().length") == 0)
    page.emulate_media(media="print")
    shown = page.evaluate("()=>[[...document.querySelectorAll('.fc-shot')].filter(e=>e.getClientRects().length).length,getComputedStyle(document.querySelector('.fc-tabs')).display]")
    check("print: the chosen plan's ten shots and no controls", shown == [10, "none"], shown)
    context.close()


def in_home_dialog(browser, base: str) -> None:
    context = browser.new_context(**PHONE)
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + "index.html", wait_until="load")
    page.evaluate("openFieldCard()")
    root = "#field-card-modal #field-card-app"
    check("home page dialog opens the card", page.locator("#field-card-modal").is_visible())
    readability(page, "home page dialog", root)
    switching(page, "home page dialog", root)
    page.keyboard.press("Escape")
    check("home page dialog closes with Escape, without errors", not page.locator("#field-card-modal").is_visible() and not errors, errors)
    context.close()


# Whether the page behind the dialog is drawn (the first heading of its content, which also
# prints), and where it is scrolled to.
BEHIND = "() => [document.querySelector('#contenido h2').checkVisibility(), Math.round(scrollY)]"


def page_behind_home_dialog(browser, base: str) -> None:
    """Below 900 px the card covers the screen and the page behind it is not drawn while it is open;
    it comes back where the reader left it, prints, and stays drawn where it shows around the card."""
    context = browser.new_context(**PHONE)
    page = context.new_page()
    page.goto(base + "index.html", wait_until="load")
    page.evaluate("scrollTo({top: 2400, behavior: 'instant'})")
    before = page.evaluate(BEHIND)
    page.evaluate("openFieldCard()")
    page.wait_for_timeout(300)
    during = page.evaluate(BEHIND)
    page.emulate_media(media="print")
    printed = page.evaluate(BEHIND)[0]
    page.emulate_media(media="screen")
    page.locator("#field-card-modal .fc-modal-bar button").first.click()
    after = page.evaluate(BEHIND)
    check("home page dialog on a phone: the page behind is not drawn while the card covers it, and comes back where it was",
          before[0] and not during[0] and after == before, {"before": before, "open": during, "closed": after})
    check("home page dialog: printing with the card open prints the page", printed, printed)
    context.close()
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.goto(base + "index.html", wait_until="load")
    page.evaluate("openFieldCard()")
    page.wait_for_timeout(300)
    check("home page dialog at 1280 px, where the page shows around the card: the page stays drawn", page.evaluate(BEHIND)[0])
    context.close()


# Where focus is (the opener's onclick, whether it is shown, and whether it is on screen) and
# where the element marked by SEEN is on screen.
FOCUS = """() => { const a = document.activeElement, r = a.getBoundingClientRect();
  return [a.getAttribute('onclick'), a.checkVisibility(), r.bottom > 0 && r.top < innerHeight,
          Math.round(window.__seen.getBoundingClientRect().top)]; }"""
# What the reader sees: the element in the middle of the screen before the card opens. "The page
# stays where it was" means it stays put on screen. Drawing the page behind the card again can
# change sizes above it, and the browser then keeps it still by changing the scroll position
# (scroll anchoring), so the scroll position itself is not the measure.
SEEN = "() => { window.__seen = document.elementFromPoint(innerWidth / 2, innerHeight / 2); }"


def home_dialog_focus_after_resize(browser, base: str) -> None:
    """Opened, then the window crosses 900 px, which hides the opener used (the phone's bottom bar
    above it, the top bar's button below it), then closed: focus goes to an opener on the page,
    preferably one on screen, and the page does not move."""
    for start, end, opener in ((390, 1280, ".mobile-bottom-nav button"), (1280, 600, "nav.sticky button")):
        context = browser.new_context(viewport={"width": start, "height": 800})
        page = context.new_page()
        page.goto(base + "index.html", wait_until="load")
        page.evaluate("scrollTo({top: 2400, behavior: 'instant'})")
        page.wait_for_timeout(300)  # sections drawn only near the screen take their real size
        page.evaluate(SEEN)
        page.evaluate("(s) => { document.querySelector(s).focus({preventScroll: true}); openFieldCard(); }",
                      opener + '[onclick="openFieldCard()"]')
        page.set_viewport_size({"width": end, "height": 800})
        page.wait_for_timeout(200)
        before = page.evaluate(FOCUS)[3]
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)  # the page scrolls smoothly: give a focus scroll time to land
        focus = page.evaluate(FOCUS)
        check(f"home page dialog: closed after a resize from {start} to {end} px hides its opener, focus goes to an "
              "opener on the page and the page stays where it was",
              focus[:2] == ["openFieldCard()", True] and focus[3] == before, {"focus": focus, "seen before": before})
        context.close()


# What the card's memory may hold after an older version, an edit by hand or a damaged
# store: a quote in a stored choice (red team, 2026-10-20), JSON that is not an object, and
# a list of done shots that is not one.
DAMAGED_MEMORY = {
    "a quote in the stored choices": {"plan": 'plan_c"]', "subject": 'dog"', "slot": '"', "slotDay": "x", "done": {}},
    "a string": "plan_c",
    "a list": ["plan_c"],
    "done shots that are a number": {"plan": "plan_c", "done": 5},
}


def damaged_memory(browser, base: str) -> None:
    """V09: whatever the card finds in its memory, it starts and keeps working, and so does the home page's dialog."""
    card_broken, home_broken = {}, {}
    for case, stored in DAMAGED_MEMORY.items():
        context = browser.new_context(**PHONE)
        context.add_init_script(f"localStorage.setItem('focalruta-campo-v1', {json.dumps(json.dumps(stored))})")
        errors: list[str] = []
        page = open_card(context, base, errors)
        page.locator("#field-card-app .fc-slot:visible .fc-check-wrap").first.click()
        kept = page.evaluate("(() => { try { return JSON.parse(localStorage.getItem('focalruta-campo-v1')).done } catch (e) { return String(e) } })()")
        state = [page.evaluate(CHOSEN, "fc-slot"), page.locator("#fc-count").inner_text(), kept]
        if errors or not state[0] or state[1] != "1/10" or not isinstance(kept, dict) or len(kept) != 1:
            card_broken[case] = [state, errors[:2]]
        home_errors: list[str] = []
        home = context.new_page()
        home.on("pageerror", lambda e, sink=home_errors: sink.append(str(e)))
        home.goto(base + "index.html", wait_until="load")
        home.locator('button[onclick="openFieldCard()"]:visible').first.click()
        if home_errors or not home.locator("#field-card-modal").is_visible():
            home_errors.append(f"dialog visible: {home.locator('#field-card-modal').is_visible()}")
            home_broken[case] = home_errors[:3]
        context.close()
    check(f"damaged memory ({len(DAMAGED_MEMORY)} cases): the card starts, picks the light and saves the next tick",
          not card_broken, card_broken)
    check(f"damaged memory ({len(DAMAGED_MEMORY)} cases): the home page's button still opens the card", not home_broken, home_broken)


# A01 by day is 35 mm, f/11, 1/125, ISO 400 at 4 m, sharp to infinity. On a
# Canon APS-C sensor (22.3 mm wide) the same field of view is 35 × 22.3/35.8 =
# 21.8 mm; the same hyperfocal distance with the circle of confusion scaled to
# 0.0187 mm needs f/6.8, which rounds to f/7.1 and stays sharp to infinity;
# ISO 400 × (7.1/11)² = 167 rounds to ISO 160. Worked by hand, not by gear.js.
A01_APSC = "22 mm (zoom 18–55) · f/7.1 · 1/125 · ISO 160"


def gear_line(page, selector: str) -> str:
    # textContent: shot cards use content-visibility:auto, so innerText of an
    # off-screen card is empty although a reader scrolling to it sees the line.
    box = page.locator(selector)
    return " ".join((box.first.text_content() or "").split()) if box.count() and box.first.is_visible() else ""


def choose_apsc_kit(page) -> None:
    page.select_option("#gear-body", "apsc_canon")
    while page.locator("#gear-lens-list [data-remove]").count():
        page.locator("#gear-lens-list [data-remove]").first.click()
    for name in ("Zoom de kit 18–55 mm f/3.5–5.6", "50 mm f/1.8"):
        page.select_option("#gear-common", label=name)


def your_gear(browser, base: str) -> None:
    """V15: a reader with an APS-C body and a kit zoom gets the equivalent of every setting."""
    context = browser.new_context(**PHONE)
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + "index.html", wait_until="load")
    first_card = "#plan-detail-content .shot-card >> nth=0"
    check("your gear: the picker shows, set to the Canon 6D kit, and shots show no extra line",
          page.locator("#gear-config").is_visible() and page.input_value("#gear-body") == "canon_6d"
          and page.locator("#plan-detail-content .gear-line").count() == 0)
    choose_apsc_kit(page)
    page.evaluate("()=>{selectPlan('plan_a');setTime('day')}")
    line = gear_line(page, f"{first_card} >> .gear-line")
    check("your gear: A01 by day on an APS-C body with an 18–55 reads as worked by hand", A01_APSC in line, line)
    floor = [page.evaluate(reading_floor.TEXT_UNDER_FLOOR, [reading_floor.HOME_SKIP, reading_floor.MIN_TEXT_PX]),
             page.evaluate(reading_floor.TARGETS_UNDER_FLOOR, [reading_floor.HOME_SKIP, reading_floor.MIN_TARGET_PX])]
    check("your gear: the picker and the adapted lines hold 12 px text and 44 px controls", floor == [[], []], floor)
    focal = float(page.input_value("#opt-lens"))
    fov = page.locator("#opt-fov").inner_text()
    want = f"{2 * math.degrees(math.atan(22.3 / (2 * focal))):.1f}°"
    check("your gear: the optics lab measures the APS-C sensor", fov == want, [focal, fov, want])
    page.evaluate("openModal('plan_a','A01')")
    in_dialog = gear_line(page, "#shot-modal .gear-line")
    page.keyboard.press("Escape")
    page.evaluate("()=>{runIndex=0;openSessionRun()}")
    in_session = gear_line(page, "#session-run-dialog .gear-line")
    page.keyboard.press("Escape")
    check("your gear: the shot dialog and the session mode show it too",
          A01_APSC in in_dialog and A01_APSC in in_session, [in_dialog, in_session])
    page.reload(wait_until="load")
    page.evaluate("()=>{selectPlan('plan_a');setTime('day')}")
    check("your gear: kept on this device after a reload",
          page.input_value("#gear-body") == "apsc_canon" and A01_APSC in gear_line(page, f"{first_card} >> .gear-line"))
    card = context.new_page()
    card.goto(base + "field_card.html", wait_until="load")
    pick(card, "fc-plan", "plan_a")
    pick(card, "fc-slot", "day")
    slot = '#field-card-app .fc-slot[data-plan=plan_a][data-shot=A01][data-slot=day] .fc-gear'
    check("your gear: the field card shows the same adapted setting", "f/7.1 · 1/125 · ISO 160" in gear_line(card, slot), gear_line(card, slot))
    plan_page = context.new_page()
    plan_page.goto(base + "plans/plan_a.html", wait_until="load")
    check("your gear: the plan page shows it too", A01_APSC in gear_line(plan_page, "#shots-grid .shot-card >> nth=0 >> .gear-line"))
    page.click("#gear-reset")
    card.reload(wait_until="load")
    check("your gear: back to the Canon 6D kit, the extra lines go",
          page.locator("#plan-detail-content .gear-line").count() == 0 and card.locator(".fc-gear:visible").count() == 0
          and page.input_value("#opt-lens") == "85")
    check("your gear: no page errors", not errors, errors)
    context.close()


def axe_states(browser, base: str) -> None:
    source = qa_matrix.axe_source()
    run = "async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});return r.violations.map(v=>v.id+':'+v.nodes.length)}"
    for label, scheme, night in (("day", "light", False), ("dark", "dark", False), ("night screen", "light", True)):
        context = browser.new_context(color_scheme=scheme, **PHONE)
        page = context.new_page()
        page.goto(base + "field_card.html", wait_until="load")
        if night:
            page.locator("label.fc-toggle", has_text="Pantalla de noche").click()
        page.add_script_tag(content=source)
        found = page.evaluate(run)
        check(f"axe: no violations on the {label} card", not found, found)
        context.close()


# The build the active worker says it is, once nothing is installing or waiting; null while
# one is, or when the worker does not answer (the one live at 9cd3044 never does).
ACTIVE_BUILD = """async()=>{const r=await navigator.serviceWorker.getRegistration();
  if(!r||r.installing||r.waiting||!r.active||r.active.state!=='activated')return null;
  const c=new MessageChannel();
  return new Promise(done=>{c.port1.onmessage=e=>done(e.data&&e.data.version||null);setTimeout(()=>done(null),2000);
    r.active.postMessage({type:'version'},[c.port2])})}"""
KEPT = "async([name,key])=>(await (await caches.open(name)).keys()).some(r=>r.url.endsWith(key))"
DECODED = """async()=>{const xs=[...document.querySelectorAll('.shot-card img')];xs.forEach(x=>x.loading='eager');
  await Promise.all(xs.map(x=>x.complete?null:new Promise(d=>{x.addEventListener('load',d,{once:true});x.addEventListener('error',d,{once:true});setTimeout(d,20000)})));
  return [xs.length,xs.filter(x=>!x.naturalWidth).map(x=>x.src.split('/').pop()),document.title,
  [...document.childNodes].filter(n=>n.nodeType===Node.COMMENT_NODE).map(n=>n.data.trim()).join(' ')]}"""
UPDATE = "navigator.serviceWorker.getRegistration().then(r=>r.update()).then(()=>true,()=>false)"


def visit(page, url: str) -> list:
    """Load a page and return every response it got, from the worker or the network."""
    responses = []

    def keep(response):
        responses.append(response)
    page.on("response", keep)
    page.goto(url, wait_until="load")
    page.wait_for_timeout(1500)
    page.remove_listener("response", keep)
    return responses


def settle(page, site) -> None:
    """Check for a new worker now, as the next visit would, and wait until `site`'s has taken over.

    "Nothing installing or waiting, the active worker activated" also holds for the last
    worker, so it does not show that the new one took over: CI run 39089226401 went on to
    check the new build under the last worker. Wait until the active worker says it is
    `site`'s build. One update only: a second one would hide a first that went wrong, as the
    rehearsal server's did when it served the last build on a socket opened before the deploy
    (red team on PR #21, F1).
    """
    expected, said = deploy_rehearsal.version(site), None
    page.evaluate(UPDATE)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        said = page.evaluate(ACTIVE_BUILD)
        if said == expected:
            return
        page.wait_for_timeout(250)
    raise TimeoutError(f"{expected}'s worker never took over in 60 s; the active one says {said}")


def later(context, page) -> None:
    """Ten minutes on: Pages' max-age=600 has run out and the HTTP cache no longer answers."""
    context.new_cdp_session(page).send("Network.clearBrowserCache")


def kept_key(site, path: str) -> str:
    return f"{path}?__rev={deploy_rehearsal.service_worker.revision(site / path)}"


def check_fresh(name: str, page, url: str, pages, site) -> None:
    wrong = deploy_rehearsal.stale(visit(page, url), pages.base, site)
    check(name, not wrong, wrong)


def offline_plan(page, base: str, plan: str, build: str | None = None):
    page.goto(base + f"plans/{plan}.html", wait_until="load")
    count, broken, title, comments = page.evaluate(DECODED)
    name = next(p["name"] for p in DATA["plans"] if p["id"] == plan)
    # A page not kept sends the reader to the home page, whose title is not the plan's.
    return count == 10 and not broken and title.startswith(name) and (build is None or f"build {build}" in comments), [count, broken, title, comments]


def upgrade_from_live(browser, old) -> None:
    """V16, V17: a reader of the live site (9cd3044) opened plan C, and comes back after a deploy."""
    pages = deploy_rehearsal.Pages(old)
    context = browser.new_context(**PHONE)
    page = context.new_page()
    page.goto(pages.base, wait_until="load")
    page.wait_for_function("navigator.serviceWorker.controller!==null", timeout=30000)
    for path in ("plans/plan_c.html", "field_card.html"):
        page.goto(pages.base + path, wait_until="load")
        page.wait_for_timeout(1500)
    pages.deploy(DIST)
    later(context, page)
    check_fresh("V16 first visit after a deploy, still under the live worker: the home page gets only this build's files",
                page, pages.base, pages, DIST)
    settle(page, DIST)
    check_fresh("V16 under the new worker: the home page gets only this build's files", page, pages.base, pages, DIST)
    pages.stop()
    later(context, page)
    passed, detail = offline_plan(page, pages.base, "plan_c")
    check("V17 offline after the upgrade: plan C, opened before it, still opens with its 10 diagrams", passed, detail)
    page.goto(pages.base, wait_until="load")
    check("V16 offline: the home page and its web manifest come from the worker",
          page.locator("h1").count() == 1 and page.evaluate("fetch('manifest.webmanifest').then(r=>r.ok,()=>false)"))
    context.close()


def install_behind_http_cache(browser, old) -> None:
    """V16: the new worker installs while the browser's HTTP cache still holds the last build."""
    pages = deploy_rehearsal.Pages(old)
    context = browser.new_context(**PHONE)
    page = context.new_page()
    page.goto(pages.base, wait_until="load")
    page.wait_for_function("navigator.serviceWorker.controller!==null", timeout=30000)
    page.goto(pages.base + "field_card.html", wait_until="load")
    pages.deploy(DIST)
    settle(page, DIST)
    # No later(): the HTTP cache still holds the last build's pages and files, as it does for ten minutes.
    for path in ("", "field_card.html"):
        check_fresh(f"V16 installed behind the HTTP cache: {path or 'the home page'} gets only this build's files",
                    page, pages.base + path, pages, DIST)
    pages.stop()
    context.close()


def pack_status(page, words: str) -> bool:
    page.reload(wait_until="load")
    pick(page, "fc-tab", "gear")
    try:
        page.wait_for_function("(w)=>document.querySelector('#fc-pack-status').textContent.includes(w)", arg=words, timeout=20000)
        return True
    except Exception:  # noqa: BLE001 - a status that never arrives is the failure being checked
        return False


def kept_for_the_field(browser, work) -> None:
    """V07, V17: after one visit and one tap, plans and diagrams work with the server
    gone; the kept files follow a deploy, and the card says when they could not."""
    pages = deploy_rehearsal.Pages(DIST)
    context = browser.new_context(**PHONE)
    page = context.new_page()
    page.goto(pages.base + "field_card.html", wait_until="load")
    page.wait_for_function("navigator.serviceWorker.controller!==null", timeout=30000)
    pick(page, "fc-tab", "gear")
    page.locator("#fc-pack").click()
    page.wait_for_function("document.querySelector('#fc-pack-status').textContent.startsWith('Listo')", timeout=120000)
    following = deploy_rehearsal.build(work, "siguiente", ("plans/plan_c.html",))
    pages.deploy(following)
    settle(page, following)
    check("V17 a deploy brings the kept plan up to date on install",
          page.evaluate(KEPT, ["focalruta-pack", kept_key(following, "plans/plan_c.html")]))
    lagging = deploy_rehearsal.build(work, "con-retraso", ("plans/plan_d.html", "field_card.html"), source=following)
    shutil.copy2(following / "plans/plan_d.html", lagging / "plans/plan_d.html")  # the server has not caught up on plan D
    pages.deploy(lagging)
    settle(page, lagging)
    check("V17 the card says when a kept file is from an earlier version", pack_status(page, "versión anterior"),
          page.locator("#fc-pack-status").text_content())
    pages.stop()
    later(context, page)
    passed, detail = offline_plan(page, pages.base, "plan_c", "siguiente")
    check("offline after saving and two deploys: plan C is the new one, with all its diagrams", passed, detail)
    passed, detail = offline_plan(page, pages.base, "plan_d")
    check("offline: plan D, which could not be refreshed, still opens with all its diagrams", passed, detail)
    page.goto(pages.base + "field_card.html", wait_until="load")
    check("offline: the card itself opens", page.locator("#field-card-app").is_visible())
    page.goto(pages.base, wait_until="load")
    check("offline: the home page opens", page.locator("h1").count() == 1)
    context.close()


def deploys(browser) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        old = deploy_rehearsal.build(work, "en-vivo", ("assets/hosted.css", "data/plans_embedded.js", "plans/plan_c.html",
                                                       "field_card.html"), live_worker=True)
        for step, value in ((upgrade_from_live, old), (install_behind_http_cache, old), (kept_for_the_field, work)):
            guarded(step, browser, value)


def phone(browser, base: str) -> None:
    context = browser.new_context(timezone_id="America/Lima", **PHONE)
    errors: list[str] = []
    page = open_card(context, base, errors)
    readability(page, "phone")
    switching(page, "phone")
    thumb_zone(page, "phone")
    memory(page, "phone")
    next_pending(page, "phone")
    keyboard(page, "phone")
    check("phone: no console or page errors", not errors, errors)
    context.close()


def wait_until(page, predicate: str, timeout_s: float = 30.0) -> None:
    """Poll an async predicate. page.wait_for_function treats a returned Promise
    as truthy and returns at once (checked against Playwright 1.55), so a
    predicate that reads the Cache API must be awaited through page.evaluate."""
    deadline = time.monotonic() + timeout_s
    while not page.evaluate(predicate):
        if time.monotonic() > deadline:
            raise TimeoutError(f"still false after {timeout_s:.0f} s: {predicate[:80]}")
        page.wait_for_timeout(250)


def guarded(step, browser, base: str) -> None:
    """A step that cannot even find the card's controls is a failed check, not a crash."""
    try:
        step(browser, base)
    except Exception as error:  # noqa: BLE001 - every failure is reported, none stops the run
        check(f"{getattr(step, '__name__', 'step')} ran to the end", False, str(error).splitlines()[0][:200])


def main() -> int:
    server = serve()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"], **qa_matrix.browser_options())
        for step in (phone, clock_cases, without_javascript, reduced_motion_and_print, in_home_dialog, page_behind_home_dialog, home_dialog_focus_after_resize, damaged_memory, your_gear,
                     overflow, axe_states):
            guarded(step, browser, base)
        deploys(browser)
        browser.close()
    server.shutdown()
    failures = [c for c in checks if not c["pass"]]
    evidence.write_report(REPORT, {"passed": not failures, "checks": len(checks), "failures": failures, "results": checks}, AUDITED)
    print(json.dumps({"passed": not failures, "checks": len(checks), "failing": len(failures)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
