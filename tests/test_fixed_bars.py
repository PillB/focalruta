"""What the X07 checks call wrong (scripts/fixed_bars.py), without a browser.

The browser half runs in scripts/browser_release_qa.py; these tests feed the judgement
the boxes a browser would report and hold its boundaries.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fixed_bars  # noqa: E402


class Page:
    """Answers each probe from a script, keyed by the probe's text."""

    def __init__(self, bars=None, in_place=(), focus=(), covers=(), landings=None, hrefs=()):
        self.bars, self.in_place, self.landings, self.hrefs = bars, list(in_place), landings or {}, list(hrefs)
        self.focus, self.covers, self.pressed = list(focus), list(covers), []

    def evaluate(self, script, arg=None):
        if script == fixed_bars.BARS:
            return self.bars
        if script == fixed_bars.IN_PLACE:
            return self.in_place
        if script == fixed_bars.FOCUSED:
            return self.focus.pop(0) if self.focus else None
        if script == fixed_bars.JUMPS:
            return self.hrefs
        if script == fixed_bars.LANDED:
            return self.landings[arg]
        return 0

    def evaluate_handle(self, _script):
        return self

    def wait_for_timeout(self, _ms):
        pass

    @property
    def keyboard(self):
        return self

    def press(self, key):
        self.pressed.append(key)


def stuck(height=1000, low=None):
    return {"nav": {"top": 0, "bottom": 65}, "bar": {"top": 64, "bottom": 136}, "low": low, "height": height}


def away(height=844, low=None):
    return {"nav": {"top": -3000, "bottom": -2943}, "bar": {"top": -2000, "bottom": -1882}, "low": low, "height": height}


def test_room_starts_at_641_by_500():
    assert fixed_bars.has_room(641, 500)
    assert not fixed_bars.has_room(640, 1000)  # the bottom bar's last width
    assert not fixed_bars.has_room(1440, 499)  # a phone on its side, however wide


def test_bars_must_stay_where_there_is_room_and_go_where_there_is_not():
    assert fixed_bars.what_stays(Page(stuck()), 820, 1000, home=True) == []
    assert fixed_bars.what_stays(Page(away(low={"top": 787, "bottom": 844})), 390, 844, home=True) == []
    assert fixed_bars.what_stays(Page(away(1000)), 820, 1000, home=False)[0].startswith("the top bar scrolled away")
    assert fixed_bars.what_stays(Page(stuck(390)), 844, 390, home=False)[0].startswith("a bar stays")


def test_a_gap_or_overlap_between_the_bars_fails():
    gap = stuck() | {"bar": {"top": 72, "bottom": 144}}
    assert "not right under it" in fixed_bars.what_stays(Page(gap), 1440, 1100, home=True)[0]
    deep = stuck() | {"bar": {"top": 60, "bottom": 132}}
    assert "not right under it" in fixed_bars.what_stays(Page(deep), 1440, 1100, home=True)[0]


def test_the_home_page_keeps_its_bottom_bar_on_a_phone_only():
    assert "bottom bar" in fixed_bars.what_stays(Page(away()), 390, 844, home=True)[0]
    assert fixed_bars.what_stays(Page(away()), 390, 844, home=False) == []
    assert fixed_bars.what_stays(Page(away(390)), 844, 390, home=True) == []  # no bottom bar that wide


def test_a_bar_out_of_its_place_fails_even_when_the_rest_is_right():
    page = Page(away(low={"top": 787, "bottom": 844}), in_place=["section overlaps the section after it by 72 px"])
    assert fixed_bars.what_stays(page, 390, 844, home=True) == ["section overlaps the section after it by 72 px"]


def run_tabs(focus, covers):
    page = Page(focus=focus)
    page.evaluate = (lambda original: lambda script, arg=None: covers.pop(0) if script == fixed_bars.COVERED else original(script, arg))(page.evaluate)
    return fixed_bars.tab_through(page, "Tab"), page.pressed


def test_focus_wholly_or_partly_behind_a_bar_fails_unless_it_cannot_fit():
    focus = [{"key": str(n), "name": f"control {n}"} for n in (1, 2, 3, 4)] + [{"key": "1", "name": "control 1"}]
    covers = [{"hidden": 0, "shown": 44, "height": 44, "free": 800},
              {"hidden": 44, "shown": 44, "height": 44, "free": 800},
              {"hidden": 10, "shown": 44, "height": 44, "free": 800},
              {"hidden": 100, "shown": 900, "height": 1200, "free": 800}]
    wrong, _ = run_tabs(focus, covers)
    assert wrong == ["control 2: 44 of 44 px behind a bar", "control 3: 10 of 44 px behind a bar"]


def test_a_control_that_keeps_focus_across_presses_is_judged_once_and_the_pass_ends_at_a_repeat():
    focus = [{"key": "1", "name": "fecha"}, {"key": "1", "name": "fecha"}, {"key": "1", "name": "fecha"},
             {"key": "2", "name": "after"}, {"key": "1", "name": "fecha"}, {"key": "3", "name": "never reached"}]
    covers = [{"hidden": 0, "shown": 44, "height": 44, "free": 800}, {"hidden": 44, "shown": 44, "height": 44, "free": 800}]
    wrong, pressed = run_tabs(focus, covers)
    assert wrong == ["after: 44 of 44 px behind a bar"]
    assert len(pressed) == 5


def test_a_link_must_land_clear_of_what_stays_and_close_under_it():
    landings = {"#behind": {"top": 30, "floor": 136, "edge": False}, "#far": {"top": 220, "floor": 136, "edge": False},
                "#right": {"top": 148, "floor": 136, "edge": False}, "#end": {"top": 400, "floor": 136, "edge": True}}
    page = Page(hrefs=list(landings), landings=landings)
    page.evaluate = (lambda original: lambda script, arg=None: 500 if script == "scrollY" else original(script, arg))(page.evaluate)
    wrong = fixed_bars.jumps(page)
    assert wrong == ["#behind starts at 30 px, what stays ends at 136 px", "#far starts at 220 px, what stays ends at 136 px"]
