"""Fresh browser matrix for current standalone, hosted and individual-plan targets."""
from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import evidence

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "CURRENT_BROWSER_QA.json"
# Every artefact this matrix actually loads, fingerprinted into the report.
AUDITED = [
    ROOT / "index.html",
    ROOT / "dist/canon6d_sota_hosted/index.html",
    ROOT / "field_card.html",
    ROOT / "data/plans.json",
    *sorted((ROOT / "plans").glob("plan_*.html")),
]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
results = []


def record(name, passed, detail=""):
    results.append({"name": name, "pass": bool(passed), "detail": detail})
    if not passed:
        raise AssertionError(f"{name}: {detail}")


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=CHROME, args=["--no-sandbox"])
    targets = {
        "standalone": ROOT / "index.html",
        "hosted": ROOT / "dist/canon6d_sota_hosted/index.html",
    }
    for target_name, target in targets.items():
        for width, height in ((390, 844), (820, 1000), (1440, 1000)):
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
                for time in ("day", "afternoon", "night"):
                    count = page.evaluate("([p,s,t])=>{selectPlan(p);setVariant(s);setTime(t);return document.querySelectorAll('#plan-detail-content .shot-card').length}", [plan, subject, time])
                    record(f"{target_name} {plan}/{subject}/{time} ten cards", count == 10, count)
                    image_count = page.locator("#plan-detail-content .shot-card img").count()
                    record(f"{target_name} {plan}/{subject}/{time} ten diagrams", image_count == 10, image_count)
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
        record(f"{target_name} ZIP link resolves", page.locator('a[href="downloads/canon6d_photo_planner_assets.zip"]').first.evaluate("a=>new URL(a.href).protocol==='file:'"))
        record(f"{target_name} interaction errors", not errors, errors)
        page.close()

    for letter in "abcdef":
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((ROOT / f"plans/plan_{letter}.html").as_uri(), wait_until="domcontentloaded", timeout=60000)
        for subject in ("human", "dog"):
            for time in ("day", "afternoon", "night"):
                page.evaluate("([s,t])=>{setVariant(s);setTime(t)}", [subject, time])
                record(f"plan_{letter} {subject}/{time} ten cards", page.locator(".shot-card").count() == 10)
        record(f"plan_{letter} correction panel", "35.8 × 23.9 mm" in (page.locator("details").text_content() or ""))
        record(f"plan_{letter} no overflow", page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"))
        record(f"plan_{letter} no errors", not errors, errors)
        page.close()
    browser.close()

report = {"passed": all(item["pass"] for item in results), "checks": len(results), "failures": [item for item in results if not item["pass"]], "results": results}
evidence.write_report(OUT, report, AUDITED)
print(json.dumps({"passed": report["passed"], "checks": report["checks"], "failures": report["failures"]}, ensure_ascii=False, indent=2))
