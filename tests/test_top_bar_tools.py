"""What the X08 checks call wrong (scripts/top_bar_tools.py), without a browser.

The browser half runs in scripts/browser_release_qa.py; these tests feed the judgement the
widths a browser would report and hold its boundaries.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import top_bar_tools  # noqa: E402


class Page:
    """Answers each probe from a script: how many tools, what each shows, and where focus is."""

    def __init__(self, shown=(), where=()):
        self.shown, self.where, self.pressed, self.asked = list(shown), list(where), [], []

    def evaluate(self, script, arg=None):
        self.asked.append(script)
        if "length" in script:
            return len(self.shown)
        if script == top_bar_tools.WHERE:
            return self.where.pop(0) if self.where else "past"
        if script == top_bar_tools.SHOWN:
            return self.shown.pop(0)
        raise AssertionError(script)

    def evaluate_handle(self, _script):
        return self

    def wait_for_timeout(self, _ms):
        pass

    @property
    def keyboard(self):
        return self

    def press(self, key):
        self.pressed.append(key)


def seen(name, width, shown):
    return {"name": name, "width": width, "shown": shown}


def test_a_control_counts_as_in_view_only_whole_give_or_take_a_px_of_rounding():
    assert top_bar_tools.cut(seen("PDF", 49, 49)) is None
    assert top_bar_tools.cut(seen("PDF", 49, 48)) is None
    assert top_bar_tools.cut(seen("▶ Sesión", 82, 3)) == "▶ Sesión: 3 of 82 px in view"  # red team N10 at 1366 px


def test_tools_must_be_whole_where_there_is_no_bottom_bar():
    page = Page(shown=[seen("☀️ Modo sol", 101, 77), seen("▶ Sesión", 82, 0), seen("Abrir tarjeta de campo", 84, 84), seen("PDF", 49, 49)])
    assert top_bar_tools.tools_in_view(page, 1280) == ["☀️ Modo sol: 77 of 101 px in view", "▶ Sesión: 0 of 82 px in view"]


def test_on_a_phone_the_bottom_bar_carries_the_tools_so_the_row_may_scroll():
    page = Page(shown=[seen("☀️ Modo sol", 101, 0)])
    assert top_bar_tools.tools_in_view(page, 640) == []
    assert page.asked == []  # nothing is even measured
    assert top_bar_tools.tools_in_view(Page(shown=[seen("☀️ Modo sol", 101, 0)]), 641) == ["☀️ Modo sol: 0 of 101 px in view"]


def test_focus_is_judged_only_inside_the_top_bar_and_the_pass_ends_past_it():
    page = Page(shown=[seen("▶ Inicio", 73, 73), seen("Óptica", 57, 22)], where=["before", "in", "in", "past", "in"])
    assert top_bar_tools.focus_in_top_bar(page) == ["Óptica: 22 of 57 px in view"]
    assert page.pressed == ["Tab"] * 4  # the skip link, two controls, then out of the bar


def test_focus_that_never_leaves_the_top_bar_stops_at_the_limit():
    page = Page(shown=[seen("▶ Inicio", 73, 73)] * top_bar_tools.TAB_LIMIT, where=["in"] * (top_bar_tools.TAB_LIMIT + 5))
    assert top_bar_tools.focus_in_top_bar(page) == []
    assert len(page.pressed) == top_bar_tools.TAB_LIMIT
