#!/usr/bin/env python3
"""Independent responsive/runtime QA for the Round 1 challenge page."""

from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "architectural_photography" / "qa" / "rounds" / "round1"
URL = os.environ.get("ARCHITECTURE_QA_URL", "http://127.0.0.1:8766/challenges/arquitectura-en-foco/")
VIEWPORTS = ((390, 844), (430, 932), (844, 390), (932, 430), (820, 1000), (1440, 1100))


def inspect_viewport(browser, width: int, height: int) -> dict:
    page = browser.new_page(viewport={"width": width, "height": height})
    page_errors, console_errors, failed = [], [], []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("requestfailed", lambda request: failed.append(request.url))
    response = page.goto(URL, wait_until="networkidle", timeout=60_000)
    page.screenshot(path=OUT / f"rules-{width}x{height}.png", full_page=True)
    page.keyboard.press("Tab")
    result = {
        "viewport": [width, height],
        "status": response.status if response else None,
        "overflow": page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
        "page_errors": page_errors,
        "console_errors": console_errors,
        "failed_resources": failed,
        "focus_reached": page.evaluate("document.activeElement !== document.body"),
        "firewall_count": page.locator("#ai-firewall").count(),
    }
    page.close()
    return result


def passed(row: dict) -> bool:
    return (
        row["status"] == 200
        and not row["overflow"]
        and not row["page_errors"]
        and not row["console_errors"]
        and not row["failed_resources"]
        and row["focus_reached"]
        and row["firewall_count"] == 1
    )


def run() -> bool:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            args=["--no-sandbox"],
        )
        rows = [inspect_viewport(browser, width, height) for width, height in VIEWPORTS]
        report = {"url": URL, "passed": all(map(passed, rows)), "records": rows}
        (OUT / "browser_qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"passed": report["passed"], "viewports": len(rows)}, indent=2), flush=True)
        browser.close()
        return report["passed"]


def main() -> int:
    return 0 if run() else 1


if __name__ == "__main__":
    raise SystemExit(main())
