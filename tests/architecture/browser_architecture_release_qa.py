#!/usr/bin/env python3
"""Release-critical PWA, persistence, offline, keyboard and no-JS architecture QA."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "architectural_photography" / "qa" / "final" / "architecture_release"
# Serve dist/canon6d_sota_hosted: only the hosted build registers the service
# worker, and navigator.serviceWorker.ready never resolves without one.
BASE = os.environ.get("FOCALRUTA_QA_URL", "http://127.0.0.1:8777/")


def run() -> dict:
    errors: list[str] = []
    console_errors: list[str] = []
    failed: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="allow")
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("requestfailed", lambda request: failed.append(request.url))
        page.goto(BASE, wait_until="networkidle")
        page.evaluate("async()=>await navigator.serviceWorker.ready")
        page.get_by_role("link", name="Abrir fotografía arquitectónica").click()
        page.locator("#contract").fill("Conecta calle, umbral, sombra y vida cotidiana")
        page.locator("#verbs").fill("cruzar, esperar, mirar, conversar, descansar")
        page.reload(wait_until="networkidle")
        persisted = page.locator("#contract").input_value().startswith("Conecta calle")
        controlled = page.evaluate("Boolean(navigator.serviceWorker.controller)")
        page.locator("#composition-mode").select_option("light-weather")
        composition = "Luz y clima" in page.locator("#composition-feedback").inner_text()
        before = page.locator("#perspective-feedback").inner_text()
        page.locator("#perspective-position").focus()
        page.keyboard.press("ArrowRight")
        after = page.locator("#perspective-feedback").inner_text()
        keyboard = bool(after) and after != before
        context.set_offline(True)
        page.reload(wait_until="domcontentloaded")
        offline = page.locator("#learn").is_visible() and page.locator(".learning-lab").count() == 9
        context.set_offline(False)
        page.screenshot(path=OUT / "offline-persisted-390x844.png", full_page=False)
        context.close()

        nojs = browser.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
        fallback = nojs.new_page()
        fallback.goto(BASE + "challenges/arquitectura-en-foco/", wait_until="domcontentloaded")
        nojs_text = fallback.locator("noscript").inner_text()
        # one camera-only exercise per lab must survive without JavaScript
        exercises = len(re.findall(r"^\d+\. ", nojs_text, flags=re.M))
        nojs_ok = exercises == 9 and all(term in nojs_text for term in ("Secuencia", "CONTRATO vs USO", "Brief"))
        nojs.close()
        browser.close()
    return {
        "passed": all((persisted, controlled, composition, keyboard, offline, nojs_ok))
        and not errors and not console_errors and not failed,
        "persistence_after_reload": persisted,
        "service_worker_controlled": controlled,
        "composition_feedback": composition,
        "keyboard_control": keyboard,
        "offline_challenge": offline,
        "no_js_core": nojs_ok,
        "no_js_exercises": exercises,
        "page_errors": errors,
        "console_errors": console_errors,
        "failed_resources": failed,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = run()
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
