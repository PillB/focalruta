"""Spanish typography a reader sees on every published page (Z02).

Requirement Z02. The blind comparison of 21 Nov 2026 caught the field card breaking
«revisarla al 100 %» between the number and its sign, so the line below began with «%.».
The RAE's Ortografía (2010) writes the percent sign one space from its number, and that
space must not break: these tests read what each page shows, its text and the strings its
scripts write, and fail on a percent sign a line can separate from its number.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
PAGES = sorted(DIST.rglob("*.html")) + [ROOT / "index.html", ROOT / "field_card.html", *sorted((ROOT / "plans").glob("plan_*.html"))]
SCRIPTS = sorted(DIST.rglob("*.js")) + sorted((ROOT / "assets").glob("*.js"))
# A number, then a space a line may break at (space, tab, newline), then the sign.
BREAKABLE_PERCENT = re.compile(r"\d[ \t\n]+%")
# What a script writes after a number it computes: a string that opens with that space
# (`n + ' %'`) or a template that puts it after an interpolation (`${n} %`). A modulo,
# `(a + 360) % 360`, has no quote or `${}` before its space, so it never matches.
WRITTEN_PERCENT = re.compile(r"\d[ \t\n]+%|[\"'`][ \t]+%|\$\{[^}]*\}[ \t]+%")
COMMENT = re.compile(r"/\*.*?\*/|(?<![:\"'\\])//[^\n]*", re.S)


class Split(HTMLParser):
    """The text a page shows, and the source of its scripts, apart."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.code: list[str] = []
        self.inside: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.inside = tag

    def handle_endtag(self, tag):
        if tag == self.inside:
            self.inside = None

    def handle_data(self, data):
        if self.inside == "script":
            self.code.append(data)
        elif self.inside is None:
            self.text.append(data)


def breaks(text: str, pattern: re.Pattern = BREAKABLE_PERCENT) -> list[str]:
    return [text[max(0, m.start() - 20):m.end()] for m in pattern.finditer(text)]


def written(code: str) -> list[str]:
    return breaks(COMMENT.sub("", code), WRITTEN_PERCENT)


def test_z02_the_check_sees_a_breakable_percent_and_passes_a_kept_one():
    assert breaks("revisarla al 100 %. Los valores") == ["revisarla al 100 %"]
    assert breaks("al 100\u00a0% y un 4\u202f%") == []
    page = Split()
    page.feed('<p>al 80 % quieto</p><script>x="al 100 %"</script><style>.a{width:100%}</style>')
    assert [breaks(t) for t in page.text if breaks(t)] == [["al 80 %"]]
    assert written("".join(page.code)) == ['x="al 100 %']
    # The moon panel wrote «Math.round(f*100)+' %'»: a number the page computes, then a
    # string that opens with a breakable space. Modulo arithmetic is not a sign.
    code = "t=Math.round(f*100)+' %';u=`${n} %`;v=(a+360) % 360;w=n+'\u00a0%'"
    assert [m.group(0) for m in WRITTEN_PERCENT.finditer(code)] == ["' %", "${n} %"]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_z02_no_page_shows_a_percent_sign_a_line_can_separate_from_its_number(page):
    split = Split()
    split.feed(page.read_text(encoding="utf-8"))
    found = breaks(" ".join(split.text)) + written("\n".join(split.code))
    assert found == []


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_z02_no_script_writes_a_percent_sign_a_line_can_separate_from_its_number(script):
    assert written(script.read_text(encoding="utf-8")) == []
