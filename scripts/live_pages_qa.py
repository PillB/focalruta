"""Post-deploy smoke test for the public GitHub Pages project subpath."""
from playwright.sync_api import sync_playwright

URL = "https://pillb.github.io/focalruta/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

checks = []
def check(name, condition, detail=""):
    checks.append({"name": name, "pass": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=CHROME, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    failed = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda request: failed.append(f"{request.method} {request.url}"))
    response = page.goto(URL, wait_until="networkidle", timeout=90000)
    check("live home 200", response and response.status == 200, response.status if response else "no response")
    check("FocalRuta title", page.title().startswith("FocalRuta"), page.title())
    check("Optical Lab initialized", page.locator("#opt-fov").inner_text() not in ("", "—"))
    check("six plan cards", page.locator("#plan-cards .plan-card").count() == 6)
    broken = []
    for plan in [f"plan_{letter}" for letter in "abcdef"]:
        for subject in ("human", "dog"):
            page.evaluate("([p,s])=>{selectPlan(p);setVariant(s)}", [plan, subject])
            broken.extend(page.evaluate("""async()=>{const xs=[...document.querySelectorAll('#plan-detail-content img')];xs.forEach(x=>x.loading='eager');await Promise.all(xs.map(x=>x.decode().catch(()=>null)));return xs.filter(x=>!x.complete||!x.naturalWidth).map(x=>x.src)}"""))
    check("all 120 live dynamic image states", not broken, broken[:10])
    check("no live page errors", not errors, errors)
    check("no failed local requests", not [x for x in failed if URL in x], failed[:20])
    browser.close()

print({"passed": all(item["pass"] for item in checks), "checks": len(checks), "results": checks})
