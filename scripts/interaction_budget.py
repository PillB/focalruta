#!/usr/bin/env python3
"""How long a reader waits for the screen to answer a tap, on the phones readers carry (X06).

Lighthouse judges a page as it loads; it does not tap anything. Interaction to Next
Paint (INP) is the Core Web Vital for taps: from the input to the next frame the
browser paints, read here from the Event Timing entries INP itself is built on. A
tap is "good" within 200 ms and "poor" beyond 500 ms (web.dev/articles/inp).

A fixed CPU slowdown measures the machine as much as the page: 4x on a fast laptop
and 4x on a slow CI runner are different phones. So the slowdown is calibrated the
way Chrome DevTools calibrates its presets (devtools-frontend,
panels/mobile_throttling/CalibrationController.ts): Lighthouse's BenchmarkIndex runs
in the browser and the slowdown is bisected until it scores as DevTools' reference
phones do, 1000 for a mid-tier phone (a Pixel 5) and 264 for a low-tier one (a Moto
G Power 2022). A machine slower than a tier is measured as it is, and the report
says so: its numbers are worse than that phone's, never better.

INP ends at the first frame painted after the tap, so a page can answer sooner by
painting part of the change and doing the rest a frame later, which is what yielding
is for (web.dev/articles/optimize-inp). That later frame is still part of the wait:
each tap also names what the reader tapped for, and the time until it is on screen,
from Element Timing (which, like Event Timing, ends when the frame is shown), is held
to the same marks. Before any page is tapped, the check taps a page built to answer at
once and show its content 300 ms later, and must see both.
"""
from __future__ import annotations

import statistics

import qa_matrix

# (tier, BenchmarkIndex DevTools targets, INP budget in ms): good on a mid-tier phone,
# never poor on a low-tier one. The budget holds for the first paint and for what was tapped for.
TIERS = (("mid-tier phone", 1000, 200), ("low-tier phone", 264, 500))
RUNS = 5
# How long to keep waiting for what a tap was for, after the tap has answered.
SHOWN_WAIT_MS = 3000
# The screens taps are made on: a phone, and a tablet held upright, the narrowest common screen on
# which the field card's first shot is in view as it opens (on a phone it starts below the screen).
PHONE = {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 3}
TABLET = {"viewport": {"width": 768, "height": 1024}, "device_scale_factor": 2}
# (page, what the reader does, what they tap, what the tap is for, as a selector and in words, screen).
# Each run starts from a fresh visit; {value} is the value of the control tapped.
OPEN_CARD = 'button[onclick="openFieldCard()"]:visible'
INTERACTIONS = (
    ("index.html", "open the field card", OPEN_CARD, "#field-card-modal .fc-plans .fc-option", "the card's plans", PHONE),
    ("index.html", "open the field card at tablet width", OPEN_CARD, "#field-card-modal .fc-shot", "the first shot", TABLET),
    ("index.html", "open a shot's detail", 'button:has-text("Abrir detalle ampliado"):visible',
     "#modal-body .reasoning-block", "the shot's reasoning", PHONE),
    ("field_card.html", "pick another plan", '.fc-plans label:has(input:not(:checked))',
     '.fc-plan-name[data-plan="{value}"]', "the plan's name", PHONE),
    ("field_card.html", "pick another light", '.fc-slots label:has(input:not(:checked))',
     '.fc-slot[data-slot="{value}"]', "the settings for that light", PHONE),
    ("field_card.html", "tick a shot", '.fc-shot:visible .fc-check-wrap', ".fc-check:checked + .fc-box", "the tick", PHONE),
)

# Lighthouse's BenchmarkIndex with a duration, as DevTools runs it (250 ms a run).
BENCHMARK = """(duration) => { const half = duration / 2;
  function gc() { const start = Date.now(); let n = 0;
    while (Date.now() - start < half) { let s = ''; for (let j = 0; j < 10000; j++) s += 'a'; if (s.length === 1) throw new Error('never'); n++; }
    return Math.round(n / 10 / ((Date.now() - start) / 1000)); }
  function noGc() { const a = [], b = []; for (let i = 0; i < 100000; i++) a[i] = b[i] = i; const start = Date.now(); let n = 0;
    while (n % 10 !== 0 || Date.now() - start < half) { const src = n % 2 === 0 ? a : b, tgt = n % 2 === 0 ? b : a;
      for (let j = 0; j < src.length; j++) tgt[j] = src[j]; n++; }
    return Math.round(n / 10 / ((Date.now() - start) / 1000)); }
  return (gc() + noGc()) / 2; }"""
OBSERVE = """(shows) => { const t = window.__tap = {events: [], start: null, painted: null, drawn: null};
  new PerformanceObserver(list => { for (const e of list.getEntries())
    if (e.interactionId) t.events.push({name: e.name, duration: e.duration}); })
    .observe({type: 'event', durationThreshold: 16, buffered: true});
  // Element Timing reports when tagged text is first on screen, as Event Timing does for the tap.
  // Tag what the tap is for, now and whenever the page adds it.
  new PerformanceObserver(list => { for (const e of list.getEntries())
    if (t.start !== null && e.renderTime > t.start) t.painted = Math.min(t.painted ?? Infinity, e.renderTime - t.start); })
    .observe({type: 'element'});
  const tag = () => { for (const e of document.querySelectorAll(shows)) for (const n of [e, ...e.querySelectorAll('*')]) n.setAttribute('elementtiming', 'shows'); };
  tag();
  new MutationObserver(tag).observe(document.body, {childList: true, subtree: true});
  // A change to something already painted (a tick) is no first paint: then the time is taken once
  // the first frame in which it is displayed, and drawn where on screen, has been drawn.
  const onScreen = e => { const r = e.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth; };
  const shown = e => e.checkVisibility() && (!onScreen(e) || e.checkVisibility({contentVisibilityAuto: true}));
  const frame = () => { if (![...document.querySelectorAll(shows)].some(shown)) return requestAnimationFrame(frame);
    const drawn = new MessageChannel(); drawn.port1.onmessage = () => { t.drawn = performance.now() - t.start; }; drawn.port2.postMessage(0); };
  addEventListener('pointerdown', e => { t.start = e.timeStamp; requestAnimationFrame(frame); }, {capture: true, once: true}); }"""


# A page that answers its tap at once and shows what it was for 300 ms later: the check
# has to see the answer and the 300 ms, or it cannot see work a page puts off.
DEFERRED_MS = 300
DEFERRED_PAGE = ("data:text/html;charset=utf-8,<!doctype html><meta name=viewport content='width=device-width'>"
                 "<button id=tap style='width:240px;height:60px'>Abrir</button><p id=head hidden>Abierto</p>"
                 "<p id=body hidden>Contenido</p><script>tap.onclick=()=>{head.hidden=false;"
                 "requestAnimationFrame(()=>setTimeout(()=>{const end=performance.now()+" + str(DEFERRED_MS) + ";"
                 "while(performance.now()<end);body.hidden=false}))}</script>")


def sees_deferred_work(browser) -> dict:
    """The instrument's own check: on DEFERRED_PAGE, unthrottled, the tap answers well before
    the content and the content comes no sooner than the work put off before it."""
    run = tap_once(browser, DEFERRED_PAGE, "#tap", "#body", 1)
    answered, shown = (None, None) if run is None else (round(run[0]), run[1] and round(run[1]))
    seen = answered is not None and shown is not None and answered < DEFERRED_MS <= shown
    return {"name": f"the tap check sees content a page puts off by {DEFERRED_MS} ms", "pass": seen,
            "detail": {"answered_ms": answered, "shown_ms": shown}}


def calibrate(browser) -> dict:
    """The CPU slowdown that makes this machine score as each tier's phone."""
    page = browser.new_page()
    session = page.context.new_cdp_session(page)
    scores: dict[float, float] = {}

    def score(rate: float) -> float:
        if rate not in scores:
            session.send("Emulation.setCPUThrottlingRate", {"rate": rate})
            # DevTools takes one run per rate; a shared CI machine is noisier, so the median of three.
            scores[rate] = statistics.median(page.evaluate(BENCHMARK, 250) for _ in range(3))
        return scores[rate]

    score(1)
    scores.clear()  # the first run warms V8 up, as DevTools does
    host = score(1)
    rates = {name: bisect(score, target, host) for name, target, _budget in TIERS}
    page.close()
    return {"host_benchmark_index": host, "rates": rates}


def bisect(score, target: float, host: float) -> float:
    """DevTools' search: halve the interval until the score is within 10 of the target."""
    if host <= target:
        return 1.0
    lower, upper, rate = 1.0, round(host / target * 1.5, 2), 1.0
    for _ in range(8):
        rate = round((lower + upper) / 2, 2)  # the throttling backend keeps hundredths
        measured = score(rate)
        if abs(measured - target) < 10:
            break
        lower, upper = (lower, rate) if measured < target else (rate, upper)
    return rate


def tap_once(browser, url: str, selector: str, shows: str, rate: float,
             screen: dict = PHONE) -> tuple[float, float | None] | None:
    """One tap from a fresh visit: its longest event in ms (0 when every event took under 16 ms),
    and the ms until what it was for is on screen (None when it never was). None when there is
    nothing to tap, which fails the checks by name instead of stopping the run."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    context = browser.new_context(**screen, is_mobile=True, has_touch=True)
    qa_matrix.harden(context)
    try:
        page = context.new_page()
        context.new_cdp_session(page).send("Emulation.setCPUThrottlingRate", {"rate": rate})
        page.goto(url, wait_until="load")
        page.wait_for_timeout(1500)
        target = page.locator(selector).first
        try:
            target.wait_for(state="visible", timeout=10_000)
        except PlaywrightTimeout:
            return None
        value = target.locator("input").first.get_attribute("value") if "{value}" in shows else None
        target.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.evaluate(OBSERVE, shows.format(value=value))
        target.click()
        page.wait_for_timeout(700)
        try:
            page.wait_for_function("() => window.__tap.painted !== null || window.__tap.drawn !== null", polling=100, timeout=SHOWN_WAIT_MS)
        except PlaywrightTimeout:
            pass
        tap = page.evaluate("() => window.__tap")
        answered = max((event["duration"] for event in tap["events"] if event["name"] in ("pointerdown", "pointerup", "click")), default=0)
        return answered, tap["drawn"] if tap["painted"] is None else tap["painted"]
    finally:
        context.close()


def judge(page: str, action: str, tier: str, budget: float, runs: list[float | None],
          claim: str = "answers", missing: str = "nothing to tap") -> tuple[dict, dict]:
    """The median of the runs against the tier's budget; a run that measured nothing fails."""
    name = f"{page}: {action} {claim} within {budget} ms on a {tier}"
    result = {"page": page, "action": action, "claim": claim, "tier": tier, "median_ms": None, "runs_ms": runs}
    if None in runs:
        return result, {"name": name, "pass": False, "detail": missing}
    result["median_ms"] = statistics.median(runs)
    return result, {"name": name, "pass": result["median_ms"] <= budget, "detail": result["median_ms"]}


def measure(browser, base: str, pages: set[str]) -> tuple[dict, list[dict]]:
    """Every interaction on every tier, median of RUNS fresh visits: one check for the answer to
    the tap and one for what it was for."""
    checks = [sees_deferred_work(browser)]
    print(f"{checks[0]['name']}: {checks[0]['detail']}", flush=True)
    calibration = calibrate(browser)
    results = []
    for page, action, selector, shows, what, screen in INTERACTIONS:
        if page not in pages:
            continue
        url = base + ("" if page == "index.html" else page)
        for tier, _target, budget in TIERS:
            runs = [tap_once(browser, url, selector, shows, calibration["rates"][tier], screen) for _ in range(RUNS)]
            answered = [None if run is None else round(run[0]) for run in runs]
            shown = [None if run is None or run[1] is None else round(run[1]) for run in runs]
            for result, check in (judge(page, action, tier, budget, answered),
                                  judge(page, action, tier, budget, shown, f"shows {what}", "not on screen in time")):
                results.append(result)
                checks.append(check)
                print(f"{check['name']}: {check['detail']} {result['runs_ms']}", flush=True)
    calibration["host_slower_than"] = [tier for tier, target, _budget in TIERS
                                       if calibration["host_benchmark_index"] <= target]
    return {**calibration, "runs_per_interaction": RUNS, "results": results}, checks
