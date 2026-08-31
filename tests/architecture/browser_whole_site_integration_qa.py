"""Browser evidence for the FocalRuta-to-architecture journey at release viewports."""
from __future__ import annotations

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ROOT = ROOT / "dist/canon6d_sota_hosted"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "architectural_photography/qa/final/whole_site_integration"
VIEWPORTS = ((390, 844), (430, 932), (844, 390), (932, 430), (820, 1000), (1440, 1100))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


def inspect_viewport(browser, base_url: str, width: int, height: int) -> dict:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base_url}/index.html", wait_until="domcontentloaded")
    card = page.locator("#architecture-challenge")
    card.scroll_into_view_if_needed()
    card.screenshot(path=str(OUT / f"home-entry-{width}x{height}.png"))
    entry = card.get_by_role("link", name="Abrir Arquitectura en Foco")
    entry.scroll_into_view_if_needed()
    entry_clear = page.evaluate("""()=>{const target=document.querySelector('#architecture-challenge a[href]')?.getBoundingClientRect();const nav=document.querySelector('.mobile-bottom-nav')?.getBoundingClientRect();return !target||!nav||nav.height===0||target.bottom<=nav.top}""")
    entry.focus()
    entry.click()
    challenge_url = page.url
    challenge_title = page.get_by_role("heading", name="Arquitectura en foco")
    challenge_title.wait_for(state="visible")
    page.screenshot(path=str(OUT / f"challenge-{width}x{height}.png"), full_page=False)
    back = page.get_by_role("link", name="FocalRuta")
    back.focus()
    back.click()
    metrics = page.evaluate("()=>({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth})")
    result = {
        "viewport": [width, height],
        "page_errors": errors,
        "horizontal_overflow": metrics["scrollWidth"] > metrics["clientWidth"],
        "entry_not_occluded": entry_clear,
        "challenge_navigation": "/challenges/arquitectura-en-foco/" in challenge_url,
        "round_trip_complete": page.locator("#architecture-challenge").count() == 1,
    }
    context.close()
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    handler = partial(QuietHandler, directory=str(PUBLIC_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=CHROME)
            base_url = f"http://127.0.0.1:{server.server_port}"
            results = [inspect_viewport(browser, base_url, *viewport) for viewport in VIEWPORTS]
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    passed = all(not item["page_errors"] and not item["horizontal_overflow"] and item["entry_not_occluded"] and item["challenge_navigation"] and item["round_trip_complete"] for item in results)
    report = {"passed": passed, "viewports": results}
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
