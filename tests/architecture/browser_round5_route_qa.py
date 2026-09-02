#!/usr/bin/env python3
"""Responsive route UI QA plus deterministic forensic leg report."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "architectural_photography/qa/rounds/round5"
URL = os.environ.get("ARCHITECTURE_QA_URL", "http://127.0.0.1:8766/challenges/arquitectura-en-foco/")
VIEWPORTS = ((390, 844), (430, 932), (844, 390), (932, 430), (820, 1000), (1440, 1100))


def straight_distance_m(first: dict, second: dict) -> float:
    latitude = math.radians((first["latitude"] + second["latitude"]) / 2)
    dx = math.radians(second["longitude"] - first["longitude"]) * math.cos(latitude)
    dy = math.radians(second["latitude"] - first["latitude"])
    return 6_371_000 * math.hypot(dx, dy)


def geometry_bounds(layer: dict) -> dict | None:
    coordinates = [point for leg in layer["legs"] for point in leg["geometry"]["coordinates"]]
    if not coordinates:
        return None
    longitude, latitude = zip(*coordinates)
    return {
        "west": min(longitude),
        "east": max(longitude),
        "south": min(latitude),
        "north": max(latitude),
        "vertices": len(coordinates),
    }


def detour_ratios(layer: dict) -> list[float]:
    stops = {stop["canonical_id"]: stop for stop in layer["stops"]}
    return [leg["road_distance_m"] / max(straight_distance_m(stops[leg["from"]], stops[leg["to"]]), 1) for leg in layer["legs"]]


def route_assessment(longest: dict | None, maximum_detour: float) -> str:
    if longest is None:
        return "single verified map point; no tour claimed"
    if longest["road_distance_m"] > 800:
        return "retained endpoint transfer; splitting would isolate a scene"
    if maximum_detour > 1.8:
        return "short road-conforming detour; barrier pattern disclosed"
    return "compact road-conforming photographic sequence"


def route_forensics() -> list[dict]:
    routes = json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))
    rows = []
    for index, layer in enumerate(routes["district_layers"], 1):
        distances = [leg["road_distance_m"] for leg in layer["legs"]]
        longest = max(layer["legs"], key=lambda leg: leg["road_distance_m"], default=None)
        longest_summary = None if longest is None else {key: longest[key] for key in ("from", "to", "road_distance_m", "road_duration_s", "source_retrieved_at", "eta_label")}
        ratios = detour_ratios(layer)
        maximum_detour = round(max(ratios, default=1), 2)
        layer_slug = Path(layer["geojson_path"]).stem
        rows.append({
            "layer_index": index,
            "layer_id": layer_slug,
            "district": layer["district"],
            "ordered_stop_ids": [stop["canonical_id"] for stop in layer["stops"]],
            "stops": len(layer["stops"]),
            "total_road_distance_m": round(sum(distances), 1),
            "longest_leg": longest_summary,
            "long_leg_warning": bool(longest and longest["road_distance_m"] > 800),
            "maximum_road_to_straight_ratio": maximum_detour,
            "geometry_bounds": geometry_bounds(layer),
            "screenshot": f"architectural_photography/qa/rounds/round5/route_layers/{layer_slug}.png",
            "assessment": route_assessment(longest, maximum_detour),
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
    page.emulate_media(reduced_motion="reduce")
    page.locator('nav a[href="#route"]').click()
    page.wait_for_timeout(50)
    anchor_clearance = page.evaluate("document.querySelector('#route').getBoundingClientRect().top-document.querySelector('nav').getBoundingClientRect().bottom")
    page.locator("#route").screenshot(path=OUT / f"route-{width}x{height}.png")
    boxes = [box for card in page.locator("#route .scene").all() if (box := card.bounding_box())]
    columns = len({round(box["x"]) for box in boxes})
    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    row = {
        "viewport": [width, height],
        "status": response.status if response else None,
        "overflow": overflow,
        "anchor_clearance": anchor_clearance,
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


def capture_route_cards(browser, forensic_rows: list[dict]) -> None:
    output = OUT / "route_layers"
    output.mkdir(parents=True, exist_ok=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(URL, wait_until="networkidle", timeout=60_000)
    cards = page.locator("#route-cards .scene")
    for index, row in enumerate(forensic_rows):
        card = cards.nth(index)
        card.scroll_into_view_if_needed()
        card.screenshot(path=ROOT / row["screenshot"])
        bounds = row["geometry_bounds"]
        geometry = "single pin" if bounds is None else f'{bounds["vertices"]} road vertices inside {bounds["west"]:.5f}…{bounds["east"]:.5f} longitude and {bounds["south"]:.5f}…{bounds["north"]:.5f} latitude'
        row["forensic_description"] = (
            f'{row["district"]} layer {row["layer_id"]}: {row["stops"]} ordered stops, '
            f'{row["total_road_distance_m"]:.1f} m total; {geometry}. '
            f'Maximum road/straight ratio {row["maximum_road_to_straight_ratio"]:.2f}. '
            f'Assessment: {row["assessment"]}.'
        )
    page.close()


def main() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        records = [inspect(browser, width, height) for width, height in VIEWPORTS]
        forensic_rows = route_forensics()
        capture_route_cards(browser, forensic_rows)
        browser.close()
    route_data = json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))
    # The route section intentionally exposes both district collection cards and
    # their layer-detail cards; count both rather than treating the collections
    # as accidental duplicates.
    expected_cards = len(route_data["district_layers"]) + len(route_data.get("route_collections", []))
    passed = all(row["status"] == 200 and row["iphone_help_status"] == 200 and not row["overflow"] and row["anchor_clearance"] >= 0 and not row["page_errors"] and not row["console_errors"] and not row["failed_resources"] and row["district_cards"] == expected_cards for row in records)
    report = {"passed": passed, "url": URL, "records": records, "route_forensics": forensic_rows}
    (OUT / "browser_route_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "viewports": len(records)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
