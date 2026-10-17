"""Every published page declares its language, one main landmark and one h1.

Requirement U04. These are the structural half of the axe findings the red team
raised on PR #19 (25 route maps had no `lang`; no page except the architecture
guide had a `main`; the field card had no `h1`). The browser half, including
contrast, runs in scripts/axe_accessibility_qa.py; this check runs in CI on
every push, without a browser, so a template change cannot quietly undo it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
# Script bodies hold HTML templates for cards and dialogs; only the document itself counts.
SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
PAGES = sorted(DIST.rglob("*.html"))


def markup(path: Path) -> str:
    return SCRIPT.sub("", path.read_text(encoding="utf-8"))


def test_the_hosted_build_has_pages_to_check():
    assert len(PAGES) >= 39, "build the hosted site first: python3 scripts/regenerate_all.py"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(DIST)))
def test_page_declares_spanish(page):
    assert re.search(r'<html\b[^>]*\blang="es"', markup(page)), f"{page.relative_to(DIST)} has no lang=\"es\""


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(DIST)))
def test_page_has_one_main_landmark_and_one_h1(page):
    html = markup(page)
    assert len(re.findall(r"<main\b", html)) == 1, f"{page.relative_to(DIST)} needs exactly one <main>"
    assert len(re.findall(r"<h1\b", html)) == 1, f"{page.relative_to(DIST)} needs exactly one <h1>"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(DIST)))
def test_complementary_content_is_not_nested_in_main(page):
    html = markup(page)
    main = re.search(r"<main\b.*?</main>", html, re.S)
    assert main and "<aside" not in main.group(0), f"{page.relative_to(DIST)} nests an <aside> inside <main>"
