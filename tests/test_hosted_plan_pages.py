"""Hosted plan pages load their diagrams as files; the offline copies keep them inline.

Requirement U05. Each hosted plan page inlined its 20 diagrams as WebP data
URIs, about 2.4 MB of base64 parsed before first paint (Lighthouse 46 on a
phone), although the same images already ship in diagrams-webp/. The page in
the download bundle must stay self-contained, because it is opened from the
iPhone Files app with no server behind it.
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
BUNDLE = ROOT / "downloads" / "canon6d_photo_planner_assets.zip"
DIAGRAMS = re.compile(r"const DIAGRAMS = (\{.*?\});\n", re.S)
PLANS = [f"plan_{letter}" for letter in "abcdef"]
# Template, data and styles stay inline; only the diagrams move out.
HOSTED_PAGE_BUDGET_BYTES = 400_000


def diagram_map(html: str) -> dict:
    match = DIAGRAMS.search(html)
    assert match, "plan page has no DIAGRAMS map"
    return json.loads(match.group(1))


@pytest.mark.parametrize("plan", PLANS)
def test_hosted_plan_page_inlines_no_images(plan):
    page = DIST / "plans" / f"{plan}.html"
    html = page.read_text(encoding="utf-8")
    assert "data:image" not in html
    assert page.stat().st_size <= HOSTED_PAGE_BUDGET_BYTES, f"{plan}: {page.stat().st_size} bytes"


@pytest.mark.parametrize("plan", PLANS)
def test_hosted_plan_page_points_every_diagram_at_a_shipped_file(plan):
    hosted = diagram_map((DIST / "plans" / f"{plan}.html").read_text(encoding="utf-8"))
    offline = diagram_map((ROOT / "plans" / f"{plan}.html").read_text(encoding="utf-8"))
    assert set(hosted) == set(offline) and len(hosted) == 20
    missing = [url for url in hosted.values() if not (DIST / "plans" / url).resolve().is_file()]
    assert not missing, missing


@pytest.mark.parametrize("plan", PLANS)
def test_download_bundle_plan_page_stays_self_contained(plan):
    with zipfile.ZipFile(BUNDLE) as bundle:
        html = bundle.read(f"plans/{plan}.html").decode("utf-8")
    assert all(src.startswith("data:image/webp;base64,") for src in diagram_map(html).values())
