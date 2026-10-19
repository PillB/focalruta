"""The CSS the site ships says what the browser will do with it (X05).

A browser drops what it cannot parse without a word. On the live site the home page's copy
of the field card lost its base rule, so in dark mode its text was dark on dark and in light
mode the plan, light and subject buttons lost their borders and their selected state: the
marker `<!-- FIELD CARD CSS START -->` sat inside the stylesheet, and `<!--` and `-->` are
skipped only between rules, so its words became the start of the next rule's selector and
the browser threw the rule away. The end marker took the hosted home's `:root` colours (focus
ring, reading ink) the same way. Three card buttons also lost their font to
`font:600 14px/1.2 inherit`, which no browser parses.

This file holds the static half, which runs in CI on every push: the parser in
`scripts/css_audit.py` reads what the browser reads, and no shipped stylesheet puts an HTML
comment inside a rule. The browser half asks Chromium about every declaration and selector the
site ships, and compares the home page's card with the card's own page, in
`scripts/browser_release_qa.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import css_audit  # noqa: E402

DIST = ROOT / "dist" / "canon6d_sota_hosted"
SHIPPED = sorted(DIST.rglob("*.html")) + [ROOT / "index.html", ROOT / "field_card.html"] + sorted((ROOT / "plans").glob("plan_*.html"))


def triples(css: str) -> list[tuple[str, str, str]]:
    return [(d["selector"], d["property"], d["value"]) for d in css_audit.parse(css)["declarations"]]


def test_x05_the_parser_reads_through_strings_data_uris_nesting_and_at_rules():
    css = """
    /* a comment { with: braces; } */
    .a{background:url(data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=) no-repeat;content:"a;b{c}"}
    @media (min-width:600px){.b{color:red!important}}
    .c{margin:0;& > .d{padding:1px}}
    @keyframes spin{from{transform:rotate(0)}to{transform:rotate(1turn)}}
    @font-face{font-family:X;src:url(x.woff2)}
    .e{font-weight:700}
    """
    assert triples(css) == [
        (".a", "background", "url(data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=) no-repeat"),
        (".a", "content", '"a;b{c}"'),
        (".b", "color", "red"),
        (".c", "margin", "0"),
        ("& > .d", "padding", "1px"),
        ("@keyframes spin (fotograma)", "transform", "rotate(0)"),
        ("@keyframes spin (fotograma)", "transform", "rotate(1turn)"),
        (".e", "font-weight", "700"),
    ]
    assert css_audit.parse(css)["selectors"] == [".a", ".b", ".c", "& > .d", ".e"]


def test_x05_an_html_comment_marker_becomes_part_of_the_next_selector():
    """What the browser does with it, so the browser half sees the rule it drops."""
    parsed = css_audit.parse("<!-- CARD START -->\n.fc-app{--fc-ink:#0b1724;color:var(--fc-ink)}\n<!-- CARD END -->")
    assert parsed["selectors"] == ["<!-- CARD START --> .fc-app"]


def test_x05_only_another_engines_css_and_a_webkit_twin_are_left_out():
    css = """.a{-moz-appearance:none;width:-moz-available;-webkit-overflow-scrolling:touch;line-clamp:2}
    .b{-webkit-line-clamp:2;line-clamp:2}
    ::-moz-selection{color:red}
    ::-moz-selection,::selection{color:red}
    .c{font:600 14px/1.2 inherit}"""
    check = css_audit.checkable(css_audit.parse(css))
    assert [(d["selector"], d["property"]) for d in check["declarations"]] == [
        (".a", "line-clamp"), ("::-moz-selection", "color"), ("::-moz-selection,::selection", "color"), (".c", "font")]
    # A list that mixes another engine's pseudo-element with ours is dropped whole, so it is asked about.
    assert [s["list"] for s in check["selectors"]] == [".a", ".b", "::-moz-selection,::selection", ".c"]


@pytest.mark.parametrize("page", SHIPPED, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_x05_no_shipped_stylesheet_puts_an_html_comment_inside_a_rule(page):
    broken = [f"{name}: {selector[:80]}" for name, text in css_audit.page_css(page)
              for selector in css_audit.parse(text)["selectors"] if "<!--" in selector or "-->" in selector]
    assert not broken, broken
