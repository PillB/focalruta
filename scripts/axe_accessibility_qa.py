#!/usr/bin/env python3
"""Run axe-core on every page the hosted build ships, and require zero violations.

Requirement U04. The repo's own contrast audit only reads solid backgrounds on
five pages, so a reviewer running axe found landmark, heading and keyboard
issues it never looked for. This audit serves dist/ over HTTP (the way GitHub
Pages does), loads every published HTML page, and the states only a URL reaches
(STATES), in a light phone viewport and a dark desktop viewport, and runs axe with the WCAG 2.x A/AA and best-practice
rule sets.

Animations are finished before axe runs. Shot cards fade in with a staggered
0.5 s animation; axe blends text with its ancestors' current opacity, so a
mid-fade card reads as 3.7-4.4:1 even though the resting label is above 5:1.
WCAG judges the presented content, and readers who ask for reduced motion
never see the fade at all.

axe-core is pinned in package-lock.json: `npm ci` puts it in node_modules, or
point FOCALRUTA_AXE at another axe.min.js. The script stops at once if it is
missing.
"""
from __future__ import annotations

import functools
import json
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

import evidence
import qa_matrix

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
REPORT = ROOT / "AXE_ACCESSIBILITY_QA.json"
RULE_SETS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
# One light phone pass and one dark desktop pass cover both colour schemes and
# both layouts on every page without doubling the run to four passes.
PASSES = (
    {"label": "light-390", "viewport": {"width": 390, "height": 844}, "color_scheme": "light"},
    {"label": "dark-1280", "viewport": {"width": 1280, "height": 800}, "color_scheme": "dark"},
)
# States only a URL reaches: the home page as the service worker opens it offline in place
# of a page never kept on the device (live check of 56a6e97, M7).
STATES = ["index.html?sin-conexion=plans/plan_c.html"]
RUN_AXE = """async (tags) => {
  document.getAnimations().forEach(animation => { try { animation.finish(); } catch (e) {} });
  const result = await axe.run(document, {runOnly: {type: 'tag', values: tags}, resultTypes: ['violations', 'incomplete']});
  const describe = node => ({target: node.target.join(' '), summary: (node.failureSummary || '').slice(0, 240)});
  return {
    version: axe.version,
    violations: result.violations.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.slice(0, 5).map(describe), count: v.nodes.length})),
    incomplete: result.incomplete.map(v => ({id: v.id, count: v.nodes.length})),
  };
}"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def published_pages() -> list[str]:
    pages = sorted(str(path.relative_to(DIST)) for path in DIST.rglob("*.html"))
    if not pages:
        sys.exit("dist/canon6d_sota_hosted has no pages; run scripts/regenerate_all.py first")
    return pages


def audit_page(browser, base: str, page_path: str, settings: dict, source: str) -> dict:
    context = browser.new_context(viewport=settings["viewport"], color_scheme=settings["color_scheme"])
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + page_path, wait_until="load", timeout=60000)
    page.add_script_tag(content=source)
    outcome = page.evaluate(RUN_AXE, RULE_SETS)
    context.close()
    return {"page": page_path, "pass": settings["label"], "page_errors": errors, **outcome}


def main() -> int:
    source = qa_matrix.axe_source()
    pages = published_pages()
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(DIST)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"], **qa_matrix.browser_options())
        for settings in PASSES:
            results += [audit_page(browser, base, page_path, settings, source) for page_path in pages + STATES]
        browser.close()
    server.shutdown()
    checks = [
        {"name": f"{item['page']} [{item['pass']}] axe", "pass": not item["violations"] and not item["page_errors"],
         "detail": {"violations": item["violations"], "page_errors": item["page_errors"]}}
        for item in results
    ]
    report = {
        "passed": all(check["pass"] for check in checks),
        "checks": len(checks),
        "axe_version": results[0]["version"],
        "rule_sets": RULE_SETS,
        "passes": [settings["label"] for settings in PASSES],
        "failures": [check for check in checks if not check["pass"]],
        "incomplete": {f"{item['page']} [{item['pass']}]": item["incomplete"] for item in results if item["incomplete"]},
        "results": checks,
    }
    evidence.write_report(REPORT, report, [DIST / page for page in pages])
    summary = sorted({(violation["id"], violation["impact"]) for item in results for violation in item["violations"]})
    print(json.dumps({"passed": report["passed"], "checks": report["checks"], "failing": len(report["failures"]),
                      "violation_rules": summary}, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
