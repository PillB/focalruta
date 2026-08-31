#!/usr/bin/env python3
"""Responsive route UI QA plus deterministic forensic leg report."""
from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "architectural_photography/qa/rounds/round5"
URL = os.environ.get("ARCHITECTURE_QA_URL", "http://127.0.0.1:8766/challenges/arquitectura-en-foco/")
VIEWPORTS = ((390, 844), (430, 932), (844, 390), (932, 430), (820, 1000), (1440, 1100))


def route_forensics() -> list[dict]:
    routes = json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))
    rows = []
    for layer in routes["district_layers"]:
        distances = [leg["road_distance_m"] for leg in layer["legs"]]
        longest = max(layer["legs"], key=lambda leg: leg["road_distance_m"], default=None)
        longest_summary = None if longest is None else {key: longest[key] for key in ("from", "to", "road_distance_m", "road_duration_s", "source_retrieved_at", "eta_label")}
        rows.append({
            "district": layer["district"],
            "stops": len(layer["stops"]),
            "total_road_distance_m": round(sum(distances), 1),
            "longest_leg": longest_summary,
            "long_leg_warning": bool(longest and longest["road_distance_m"] > 2500),
            "assessment": "single verified map point; no tour claimed" if longest is None else "walkable photographic sequence",
        })
    return rows


def layout_description(width: int, height: int, columns: int, cards: int, overflow: bool) -> str:
    orientation = "landscape" if width > height else "portrait"
    overflow_text = "No horizontal overflow was detected" if not overflow else "Horizontal overflow was detected"
    return f"{width}px {orientation} route capture: {cards} district-tour cards arranged in {columns} responsive column(s). {overflow_text}; headings, distance disclosure, Google Maps actions and downloads remain inside the route section."


def inspect(browser, width: int, height: int) -> dict:
    page = browser.new_page(viewport={"width": width, "height": height})
    errors, console_errors, failed = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("requestfailed", lambda request: failed.append(request.url))
    response = page.goto(URL, wait_until="networkidle", timeout=60_000)
    page.locator("#route").screenshot(path=OUT / f"route-{width}x{height}.png")
    boxes = [box for card in page.locator("#route .scene").all() if (box := card.bounding_box())]
    columns = len({round(box["x"]) for box in boxes})
    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    row = {
        "viewport": [width, height],
        "status": response.status if response else None,
        "overflow": overflow,
        "page_errors": errors,
        "console_errors": console_errors,
        "failed_resources": failed,
        "district_cards": page.locator("#route .scene").count(),
        "iphone_help_status": page.request.get(URL + "iphone-maps.html").status,
        "screenshot": str((OUT / f"route-{width}x{height}.png").relative_to(ROOT)),
        "forensic_description": layout_description(width, height, columns, len(boxes), overflow),
    }
    page.close()
    return row


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        records = [inspect(browser, width, height) for width, height in VIEWPORTS]
        browser.close()
    expected_cards = len(json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))["district_layers"])
    passed = all(row["status"] == 200 and row["iphone_help_status"] == 200 and not row["overflow"] and not row["page_errors"] and not row["console_errors"] and not row["failed_resources"] and row["district_cards"] == expected_cards for row in records)
    report = {"passed": passed, "url": URL, "records": records, "route_forensics": route_forensics()}
    (OUT / "browser_route_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "viewports": len(records)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
