#!/usr/bin/env python3
"""Responsive interaction QA for the architecture learning laboratories."""
from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "architectural_photography/qa/rounds/round2/learning_labs"
URL = os.environ.get("ARCHITECTURE_QA_URL", "http://127.0.0.1:8766/challenges/arquitectura-en-foco/")
VIEWPORTS = ((390, 844), (430, 932), (844, 390), (932, 430), (820, 1000), (1440, 1100))


def inspect(browser, width: int, height: int) -> dict:
    page = browser.new_page(viewport={"width": width, "height": height})
    errors, console_errors = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    response = page.goto(URL, wait_until="networkidle", timeout=60_000)
    page.emulate_media(reduced_motion="reduce")
    page.locator('nav a[href="#learn"]').click()
    page.locator("#perspective-position").fill("2")
    near_ratio = page.locator("#perspective-feedback").inner_text()
    page.locator("#perspective-focal").select_option("85")
    focal_ratio = page.locator("#perspective-feedback").inner_text()
    page.locator("#vertical-tilt").fill("20")
    page.locator("#hierarchy-mode").select_option("human")
    page.locator("#light-mode").select_option("garua")
    page.locator("#learn").screenshot(path=OUT / f"learning-{width}x{height}.png")
    result = {
        "viewport": [width, height],
        "status": response.status if response else None,
        "overflow": page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
        "page_errors": errors,
        "console_errors": console_errors,
        "labs": page.locator(".learning-lab").count(),
        "lessons": page.locator(".lesson-card").count(),
        "videos": page.locator(".video-transfer").count(),
        "position_feedback": "Relación de tamaño" in near_ratio,
        "focal_preserves_ratio": near_ratio.split("Relación de tamaño cercano/lejos: ")[1].split("×")[0] == focal_ratio.split("Relación de tamaño cercano/lejos: ")[1].split("×")[0],
        "vertical_feedback": "convergen" in page.locator("#vertical-feedback").inner_text(),
        "hierarchy_feedback": "figura" in page.locator("#hierarchy-feedback").inner_text(),
        "light_feedback": "Garúa" in page.locator("#light-feedback").inner_text(),
        "screenshot": str((OUT / f"learning-{width}x{height}.png").relative_to(ROOT)),
    }
    page.close()
    return result


def main() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        rows = [inspect(browser, width, height) for width, height in VIEWPORTS]
        browser.close()
    boolean_checks = ("position_feedback", "focal_preserves_ratio", "vertical_feedback", "hierarchy_feedback", "light_feedback")
    passed = all(
        row["status"] == 200 and not row["overflow"] and not row["page_errors"] and not row["console_errors"]
        and row["labs"] == 4 and row["lessons"] == 17 and row["videos"] >= 6
        and all(row[key] for key in boolean_checks)
        for row in rows
    )
    report = {"passed": passed, "url": URL, "viewports": rows}
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "viewports": len(rows)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
