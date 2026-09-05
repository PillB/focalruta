#!/usr/bin/env python3
"""Responsive and physical-invariant QA for the architecture learning laboratories.

Every check below reads geometry back out of the rendered DOM and asserts the
direction the physics predicts, so a lab that draws a plausible but wrong
picture fails here.
"""
from __future__ import annotations

import json
import hashlib
import math
import re
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qa_matrix  # noqa: E402  (needs the path above)
OUT = ROOT / "architectural_photography/qa/rounds/round2/learning_labs"
URL = os.environ.get("ARCHITECTURE_QA_URL", "http://127.0.0.1:8766/challenges/arquitectura-en-foco/")
VIEWPORTS = qa_matrix.REQUIRED_VIEWPORTS
COMPOSITION_MODES = ("default-postcard", "changed-position", "fixed-position-focal", "human-presence", "light-weather")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


def _number(page, selector: str, attribute: str) -> float:
    value = page.get_attribute(selector, attribute)
    return float(value) if value is not None else math.nan


def _cone_half_angle(page) -> float:
    """Recover the drawn half angle of view from the plan-view cone."""
    path = page.get_attribute("#perspective-fov", "d")
    origin_x, origin_y, edge_x, edge_y = (float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", path)[:4])
    return math.degrees(math.atan2(abs(origin_y - edge_y), edge_x - origin_x))


def _polygon_widths(page, selector: str) -> tuple[float, float]:
    points = [tuple(float(v) for v in pair.split(",")) for pair in page.get_attribute(selector, "points").split()]
    top = abs(points[1][0] - points[0][0])
    bottom = abs(points[2][0] - points[3][0])
    return top, bottom


def _shadow_centroid_x(page) -> float:
    points = [tuple(float(v) for v in pair.split(",")) for pair in page.get_attribute("#light-shadow", "points").split()]
    return sum(point[0] for point in points) / len(points)


def check_perspective(page) -> dict:
    page.locator("#perspective-position").fill("4")
    page.locator("#perspective-focal").select_option("35")
    wide_angle, wide_text = _cone_half_angle(page), page.locator("#perspective-feedback").inner_text()
    page.locator("#perspective-focal").select_option("85")
    long_angle, long_text = _cone_half_angle(page), page.locator("#perspective-feedback").inner_text()
    ratio = re.compile(r"proyecta ([0-9,]+)×")
    page.locator("#perspective-position").fill("7")
    far_text = page.locator("#perspective-feedback").inner_text()
    return {
        "fov_narrows_with_focal": long_angle < wide_angle - 5,
        "fov_matches_optics": abs(wide_angle - math.degrees(math.atan(36 / 70))) < 1.5,
        "focal_preserves_depth_ratio": ratio.search(wide_text).group(1) == ratio.search(long_text).group(1),
        "distance_changes_depth_ratio": ratio.search(long_text).group(1) != ratio.search(far_text).group(1),
    }


def check_vertical(page) -> dict:
    page.locator("#vertical-tilt").fill("0")
    level_top, level_bottom = _polygon_widths(page, "#vertical-building")
    level_text = page.locator("#vertical-feedback").inner_text()
    page.locator("#vertical-tilt").fill("10")
    mid_top, mid_bottom = _polygon_widths(page, "#vertical-building")
    page.locator("#vertical-tilt").fill("20")
    tilt_top, tilt_bottom = _polygon_widths(page, "#vertical-building")
    return {
        "level_verticals_stay_parallel": abs(level_top - level_bottom) < 0.5 and "infinito" in level_text,
        "tilt_makes_verticals_converge": tilt_top < tilt_bottom,
        "convergence_grows_with_tilt": (tilt_top / tilt_bottom) < (mid_top / mid_bottom) < 1.0,
    }


def check_light(page) -> dict:
    page.locator("#light-source").select_option("sol")
    page.locator("#light-altitude").select_option("45")
    page.locator("#light-azimuth").select_option("-70")
    left_sun, left_shadow = _number(page, "#light-sun", "cx"), _shadow_centroid_x(page)
    page.locator("#light-azimuth").select_option("70")
    right_sun, right_shadow = _number(page, "#light-sun", "cx"), _shadow_centroid_x(page)
    page.locator("#light-azimuth").select_option("0")
    page.locator("#light-altitude").select_option("70")
    high_text = page.locator("#light-feedback").inner_text()
    page.locator("#light-altitude").select_option("10")
    low_text = page.locator("#light-feedback").inner_text()
    hard = _number(page, "#light-penumbra-blur", "stdDeviation")
    page.locator("#light-source").select_option("garua")
    soft, diffuse_text = _number(page, "#light-penumbra-blur", "stdDeviation"), page.locator("#light-feedback").inner_text()
    metres = re.compile(r"sombra mide ([0-9,]+) m")
    return {
        "shadow_opposes_the_source": (right_sun > left_sun) and (right_shadow < left_shadow),
        "low_sun_casts_longer_shadow": _comma_float(metres.search(low_text).group(1)) > _comma_float(metres.search(high_text).group(1)),
        "wide_source_softens_the_edge": soft > hard,
        "diffuse_source_drops_the_umbra": "umbra desaparece" in diffuse_text,
    }


def _comma_float(text: str) -> float:
    return float(text.replace(",", "."))


def check_depth_and_edges(page) -> dict:
    page.locator("#depth-haze").fill("0")
    clear = _number(page, "#depth-plane-3", "opacity")
    page.locator("#depth-haze").fill("90")
    hazy = _number(page, "#depth-plane-3", "opacity")
    page.locator("#negative-margin").fill("40")
    roomy = _number(page, "#negative-warning", "opacity")
    page.locator("#negative-margin").fill("0")
    tight = _number(page, "#negative-warning", "opacity")
    page.locator("#hierarchy-mode").select_option("clean")
    clean_order = page.get_attribute("#hierarchy-order-1", "transform")
    page.locator("#hierarchy-mode").select_option("clutter")
    return {
        "haze_flattens_the_far_plane": hazy < clear,
        "tangency_only_warns_when_tight": tight > roomy,
        "reading_order_follows_the_variant": clean_order != page.get_attribute("#hierarchy-order-1", "transform"),
    }


def check_exposure_and_reflection(page) -> dict:
    page.locator("#exposure-aperture").select_option("5,6")
    page.locator("#exposure-shutter").select_option("500")
    fast = _number(page, "#exposure-streak", "width")
    page.locator("#exposure-shutter").select_option("15")
    slow = _number(page, "#exposure-streak", "width")
    page.locator("#exposure-aperture").select_option("1,8")
    shallow = _number(page, "#exposure-sharp", "width")
    page.locator("#exposure-aperture").select_option("11")
    deep = _number(page, "#exposure-sharp", "width")
    page.locator("#reflection-angle").select_option("0")
    frontal = _number(page, "#reflection-mirror", "opacity")
    page.locator("#reflection-angle").select_option("85")
    grazing = _number(page, "#reflection-mirror", "opacity")
    page.locator("#reflection-exposure").select_option("-3")
    dark_halo = _number(page, "#reflection-halo", "r")
    page.locator("#reflection-exposure").select_option("1")
    return {
        "slow_shutter_lengthens_the_streak": slow > fast,
        "stopping_down_widens_the_sharp_zone": deep > shallow,
        "grazing_angle_raises_the_reflection": grazing > frontal,
        "interior_fades_as_reflection_rises": _number(page, "#reflection-interior", "opacity") < 0.5,
        "brighter_exposure_grows_the_halo": _number(page, "#reflection-halo", "r") > dark_halo,
    }


def check_composition(page) -> dict:
    hashes = []
    for mode in COMPOSITION_MODES:
        page.locator("#composition-mode").select_option(mode)
        hashes.append(hashlib.sha256(page.locator("#composition-frame").screenshot()).hexdigest())
    page.locator('.lab-reset[data-lab="composition"]').click()
    return {
        "composition_states_distinct": len(set(hashes)) == len(COMPOSITION_MODES),
        "reset_ok": page.locator("#composition-mode").input_value() == "default-postcard",
    }


def inspect(browser, width: int, height: int, url: str = URL) -> dict:
    page = browser.new_page(viewport={"width": width, "height": height})
    qa_matrix.harden(page)
    errors, console_errors = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    response = page.goto(url, wait_until="networkidle", timeout=60_000)
    page.emulate_media(reduced_motion="reduce")
    page.locator('nav a[href="#learn"]').click()
    anchor_clear = page.evaluate(
        "()=>document.querySelector('#learn').getBoundingClientRect().top>=document.querySelector('nav').getBoundingClientRect().bottom"
    )
    result = {
        "viewport": [width, height],
        "status": response.status if response else None,
        "overflow": page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
        "page_errors": errors,
        "console_errors": console_errors,
        "labs": page.locator(".learning-lab").count(),
        "lessons": page.locator(".lesson-card").count(),
        "videos": page.locator(".video-transfer").count(),
        "anchor_clear": anchor_clear,
    }
    for checker in (check_perspective, check_vertical, check_light, check_depth_and_edges, check_exposure_and_reflection, check_composition):
        result.update(checker(page))
    page.locator("#learn").screenshot(path=OUT / f"learning-{width}x{height}.png")
    result["screenshot"] = str((OUT / f"learning-{width}x{height}.png").relative_to(ROOT))
    page.close()
    return result


BOOLEAN_CHECKS = (
    "fov_narrows_with_focal", "fov_matches_optics", "focal_preserves_depth_ratio", "distance_changes_depth_ratio",
    "level_verticals_stay_parallel", "tilt_makes_verticals_converge", "convergence_grows_with_tilt",
    "shadow_opposes_the_source", "low_sun_casts_longer_shadow", "wide_source_softens_the_edge",
    "diffuse_source_drops_the_umbra", "haze_flattens_the_far_plane", "tangency_only_warns_when_tight",
    "reading_order_follows_the_variant", "slow_shutter_lengthens_the_streak", "stopping_down_widens_the_sharp_zone",
    "grazing_angle_raises_the_reflection", "interior_fades_as_reflection_rises", "brighter_exposure_grows_the_halo",
    "composition_states_distinct", "anchor_clear", "reset_ok",
)


def row_passed(row: dict) -> bool:
    return bool(
        row["status"] == 200 and not row["overflow"] and not row["page_errors"] and not row["console_errors"]
        and row["labs"] == 9 and row["lessons"] == 17 and row["videos"] >= 6
        and all(row[key] for key in BOOLEAN_CHECKS)
    )


def main() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    public_root = ROOT / "challenges/arquitectura-en-foco"
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(public_root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            url = f"http://127.0.0.1:{server.server_port}/"
            rows = [inspect(browser, width, height, url) for width, height in VIEWPORTS]
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    passed = all(row_passed(row) for row in rows)
    failures = {key: [row["viewport"] for row in rows if not row.get(key)] for key in BOOLEAN_CHECKS}
    report = {
        "passed": passed, "url": "isolated-public-root", "viewports": rows,
        "failed_checks": {key: value for key, value in failures.items() if value},
    }
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "viewports": len(rows), "failed_checks": report["failed_checks"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
