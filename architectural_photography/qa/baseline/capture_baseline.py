#!/usr/bin/env python3
"""Capture the immutable pre-architecture browser baseline at required viewports."""

from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
URL = os.environ.get("FOCALRUTA_BASELINE_URL", "http://127.0.0.1:8765/")
VIEWPORTS = ((390, 844), (430, 932), (844, 390), (932, 430), (820, 1000), (1440, 1100))


def main() -> None:
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            args=["--no-sandbox"],
        )
        for width, height in VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": height})
            page_errors, console_errors, failed = [], [], []
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("requestfailed", lambda request: failed.append(request.url))
            response = page.goto(URL, wait_until="networkidle", timeout=90_000)
            page.screenshot(path=OUT / f"home-{width}x{height}.png", full_page=True)
            page.keyboard.press("Tab")
            focus_visible = page.evaluate("document.activeElement !== document.body")
            sw = page.evaluate(
                "async()=>{if(!('serviceWorker' in navigator))return {supported:false};"
                "const registration=await navigator.serviceWorker.getRegistration();"
                "return {supported:true,registered:!!registration,controlled:!!navigator.serviceWorker.controller}}"
            )
            records.append(
                {
                    "viewport": [width, height],
                    "status": response.status if response else None,
                    "scroll_width": page.evaluate("document.documentElement.scrollWidth"),
                    "client_width": page.evaluate("document.documentElement.clientWidth"),
                    "page_errors": page_errors,
                    "console_errors": console_errors,
                    "failed_resources": failed,
                    "keyboard_focus_reached": focus_visible,
                    "service_worker": sw,
                }
            )
            page.close()
        report = {
            "baseline_commit": "9a415311f8d34772a6391193434bbf22c7b9af5b",
            "url": URL,
            "records": records,
            "passed": all(
                row["status"] == 200
                and row["scroll_width"] <= row["client_width"]
                and not row["page_errors"]
                and not row["console_errors"]
                and not row["failed_resources"]
                and row["keyboard_focus_reached"]
                for row in records
            ),
        }
        (OUT / "browser_baseline.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"passed": report["passed"], "viewports": len(records)}, indent=2), flush=True)
        # Some managed macOS runners hang while Playwright closes Chrome. Evidence is
        # written before teardown; normal context management still gets first chance.
        browser.close()


if __name__ == "__main__":
    main()
