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
"""
from __future__ import annotations

import statistics

import qa_matrix

# (tier, BenchmarkIndex DevTools targets, INP budget in ms): good on a mid-tier phone,
# never poor on a low-tier one.
TIERS = (("mid-tier phone", 1000, 200), ("low-tier phone", 264, 500))
RUNS = 5
# (page, what the reader does, what they tap). Each run starts from a fresh visit.
INTERACTIONS = (
    ("index.html", "open the field card", 'button[onclick="openFieldCard()"]:visible'),
    ("index.html", "open a shot's detail", 'button:has-text("Abrir detalle ampliado"):visible'),
    ("field_card.html", "pick another plan", '.fc-plans label:has(input:not(:checked))'),
    ("field_card.html", "pick another light", '.fc-slots label:has(input:not(:checked))'),
    ("field_card.html", "tick a shot", '.fc-shot:visible .fc-check-wrap'),
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
OBSERVE = """() => { window.__taps = []; new PerformanceObserver(list => { for (const e of list.getEntries())
  if (e.interactionId) window.__taps.push({name: e.name, duration: e.duration}); })
  .observe({type: 'event', durationThreshold: 16, buffered: true}); }"""


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


def tap_once(browser, url: str, selector: str, rate: float) -> float | None:
    """The longest event of one tap, in ms (0 when every event took under 16 ms); None when
    there is nothing to tap, which fails the check by name instead of stopping the run."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3,
                                  is_mobile=True, has_touch=True)
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
        target.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        page.evaluate(OBSERVE)
        target.click()
        page.wait_for_timeout(700)
        taps = page.evaluate("() => window.__taps")
        return max((tap["duration"] for tap in taps if tap["name"] in ("pointerdown", "pointerup", "click")), default=0)
    finally:
        context.close()


def judge(page: str, action: str, tier: str, budget: float, runs: list[float | None]) -> tuple[dict, dict]:
    """The median of the runs against the tier's budget; a run with nothing to tap fails."""
    name = f"{page}: {action} answers within {budget} ms on a {tier}"
    if None in runs:
        return ({"page": page, "action": action, "tier": tier, "median_ms": None, "runs_ms": runs},
                {"name": name, "pass": False, "detail": "nothing to tap"})
    median = statistics.median(runs)
    return ({"page": page, "action": action, "tier": tier, "median_ms": median, "runs_ms": runs},
            {"name": name, "pass": median <= budget, "detail": median})


def measure(browser, base: str, pages: set[str]) -> tuple[dict, list[dict]]:
    """Every interaction on every tier, median of RUNS fresh visits, one check each."""
    calibration = calibrate(browser)
    results, checks = [], []
    for page, action, selector in INTERACTIONS:
        if page not in pages:
            continue
        url = base + ("" if page == "index.html" else page)
        for tier, _target, budget in TIERS:
            runs = [tap_once(browser, url, selector, calibration["rates"][tier]) for _ in range(RUNS)]
            result, check = judge(page, action, tier, budget, [None if run is None else round(run) for run in runs])
            results.append(result)
            checks.append(check)
            print(f"{check['name']}: {check['detail']} {result['runs_ms']}", flush=True)
    calibration["host_slower_than"] = [tier for tier, target, _budget in TIERS
                                       if calibration["host_benchmark_index"] <= target]
    return {**calibration, "runs_per_interaction": RUNS, "results": results}, checks
