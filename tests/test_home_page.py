"""The home page and the plan pages hold the reading floor (V10 and V12).

Step 3 of the plan Pablo approved: field use first. After the field card was
rebuilt, the rest of the site still had 34 text runs under 12 px on a phone
(the optics lab's labels at 11.2 px, each shot's light line at 11 px, the
bottom navigation at 11 px), 22 controls under 44 px (subject and time
toggles 31 px wide, footer links 17 px tall) and English in the interface:
"Home/Building Lab", "Abrir Field Card", "FoV, DoF", "MFD", "Zoom burst",
"FREEZE", "Lightpainting:", "Zooming:" and diagrams described as "human".

This file holds the static half, which runs in CI on every push: no CSS rule
or class sets text under 12 px, and no word of the interface is English. The
browser half, which measures rendered text and every control in several page
states, runs in scripts/browser_release_qa.py.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from reading_floor import MIN_TEXT_PX, english_in  # noqa: E402

INDEX = ROOT / "index.html"
PLAN_PAGES = sorted((ROOT / "plans").glob("plan_*.html"))
# The field card has its own tests (tests/test_field_card.py); its print rules are in points.
FIELD_CARD_BLOCKS = (
    ("<!-- FIELD CARD CSS START -->", "<!-- FIELD CARD CSS END -->"),
    ("<!-- FIELD CARD INTEGRATED -->", "<!-- FIELD CARD INTEGRATED END -->"),
    ("<!-- FIELD CARD JS START -->", "<!-- FIELD CARD JS END -->"),
)
INLINE_DATA = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=]+")
FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9.]+)(px|rem|em)\b")
FONT_SHORTHAND = re.compile(r"\bfont\s*:\s*[^;{}\"]*?\b([0-9.]+)px\b")
TAILWIND_SIZE = re.compile(r"\btext-\[([0-9.]+)(px|rem)\]")


def without_field_card(text: str) -> str:
    for start, end in FIELD_CARD_BLOCKS:
        if start in text:
            text = text[: text.index(start)] + text[text.index(end):]
    return text


def without_print_rules(css: str) -> str:
    """Drop every @media print block, matching braces."""
    out, i = [], 0
    while (at := css.find("@media print", i)) >= 0:
        out.append(css[i:at])
        depth, j = 0, css.index("{", at)
        while True:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
            if depth == 0:
                break
        i = j
    out.append(css[i:])
    return "".join(out)


def page_source(path: Path) -> str:
    return without_print_rules(INLINE_DATA.sub("data:", without_field_card(path.read_text(encoding="utf-8"))))


def under_floor(value: str, unit: str) -> bool:
    size = float(value) * (16 if unit in ("rem", "em") else 1)
    return size < MIN_TEXT_PX


def small_declarations(text: str) -> list[str]:
    found = [m.group(0) for m in FONT_SIZE.finditer(text) if under_floor(m.group(1), m.group(2))]
    found += [m.group(0) for m in FONT_SHORTHAND.finditer(text) if float(m.group(1)) < MIN_TEXT_PX]
    return found + [m.group(0) for m in TAILWIND_SIZE.finditer(text) if under_floor(m.group(1), m.group(2))]


class ShownText(HTMLParser):
    """Text and announced labels of a document, without scripts, styles or cited sources."""

    SKIPPED = {"script", "style", "noscript", "cite"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[bool] = []
        self.parts: list[str] = []

    def skipping(self) -> bool:
        return any(self.stack)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        skip = tag in self.SKIPPED or attrs.get("id") == "sources"
        if not (self.skipping() or skip):
            self.parts += [attrs.get(a) or "" for a in ("alt", "title", "aria-label", "placeholder")]
        if tag not in self.VOID:
            self.stack.append(skip)

    def handle_endtag(self, tag):
        if tag not in self.VOID and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if not self.skipping():
            self.parts.append(data)


def shown_text(path: Path) -> str:
    parser = ShownText()
    parser.feed(without_field_card(path.read_text(encoding="utf-8")))
    return " ".join(parser.parts)


def test_v10_home_page_sets_no_text_under_12px():
    assert small_declarations(page_source(INDEX)) == []


@pytest.mark.parametrize("page", PLAN_PAGES, ids=lambda p: p.name)
def test_v10_plan_pages_set_no_text_under_12px(page):
    assert small_declarations(page_source(page)) == []


def test_v10_the_scan_sees_each_kind_of_small_declaration():
    """Guard against a scan that passes because it reads nothing."""
    sample = ".a{font-size:11px}.b{font-size:.7rem}.c{font:700 10px/1 sans-serif}<p class='text-[10px]'>@media print{.d{font-size:8px}}"
    assert len(small_declarations(without_print_rules(sample))) == 4
    assert small_declarations(".a{font-size:12px}.b{font-size:.75rem}<p class='text-[12px]'>") == []


def test_v12_home_page_interface_is_spanish():
    assert english_in(shown_text(INDEX)) == []


@pytest.mark.parametrize("page", PLAN_PAGES, ids=lambda p: p.name)
def test_v12_plan_pages_interface_is_spanish(page):
    assert english_in(shown_text(page)) == []


def test_v12_the_scan_reads_labels_and_skips_cited_sources(tmp_path):
    sample = tmp_path / "sample.html"
    sample.write_text('<p>Abrir</p><img alt="Diagrama A01 human"><section id="sources"><p>Canon · Shutter</p></section>', encoding="utf-8")
    assert english_in(shown_text(sample)) == ["human"]
