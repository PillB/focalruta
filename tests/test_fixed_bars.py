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


def test_room_grows_with_the_readers_text():
    assert not fixed_bars.has_room(650, 800, text=20)  # where the Sujeto/Hora bar wraps at 20 px (red team N11)
    assert fixed_bars.has_room(802, 625, text=20) and not fixed_bars.has_room(800, 1000, text=20)
    assert not fixed_bars.has_room(1440, 749, text=24) and fixed_bars.has_room(962, 750, text=24)


def test_without_room_for_larger_text_the_bars_must_go():
    assert fixed_bars.what_stays(Page(stuck(800)), 650, 800, home=True, text=20)[0].startswith("a bar stays")
    assert fixed_bars.what_stays(Page(away(800)), 650, 800, home=True, text=20) == []  # no bottom bar that wide
    assert fixed_bars.what_stays(Page(stuck(800)), 1024, 800, home=False, text=20) == []


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


def test_a_link_is_judged_only_once_the_page_has_settled():
    """Sections drawn only near the screen can push the target down after the jump (red team N12)."""
    page = Page(hrefs=["#tecnicas"], landings={"#tecnicas": {"top": 673, "floor": 0, "edge": False}})
    order = []
    page.wait_for_timeout = lambda ms: order.append(ms)
    page.evaluate = (lambda original: lambda script, arg=None: order.append(script) or original(script, arg))(page.evaluate)
    assert fixed_bars.jumps(page) == ["#tecnicas starts at 673 px, what stays ends at 0 px"]
    assert order.index(fixed_bars.CLICK) < order.index(fixed_bars.SETTLE) < order.index(fixed_bars.LANDED)


def test_opening_the_page_at_the_lowest_section_is_judged_like_a_jump():
    page = Page(landings={"#tecnicas": {"top": 1909, "floor": 0, "edge": False}})
    opened = []
    page.goto = lambda url, **_: opened.append(url)
    page.evaluate = (lambda original: lambda script, arg=None: "#tecnicas" if script == fixed_bars.DEEPEST else original(script, arg))(page.evaluate)
    assert fixed_bars.address(page, "file:///index.html") == ["opened at #tecnicas starts at 1909 px, what stays ends at 0 px"]
    assert opened == ["file:///index.html#tecnicas"]
    assert fixed_bars.address(Page(), "file:///plan.html") == []  # no links: nothing to open


class Dialogs(Page):
    """Buttons that open a dialog (None for one off screen) and where the middle of the screen is at each look."""

    def __init__(self, opened, after):
        super().__init__()
        self.opened, self.after = list(opened), list(after)

    def evaluate(self, script, arg=None):
        if script == fixed_bars.OPEN:
            return self.opened.pop(0)
        if script == fixed_bars.SEEN:
            return self.after.pop(0)
        if "length" in script:
            return len(self.opened)
        return super().evaluate(script, arg)


def test_a_dialog_closed_from_a_bar_on_screen_must_leave_the_page_still():
    """What is in the middle of the screen must stay where it was, whatever the scroll position does."""
    page = Dialogs([None, {"name": "Abrir tarjeta de campo", "top": 500}, {"name": "▶ Sesión", "top": 500}], [1086, 500, 500])
    assert fixed_bars.dialogs_leave_page_still(page) == ["Abrir tarjeta de campo: the page moved 586 px"]
    assert page.pressed == ["Escape", "Escape"]  # a button off screen opens nothing
    assert page.after == []  # one look at a page that moved, two at one that stayed


def test_a_page_that_moves_a_little_after_closing_fails_too():
    page = Dialogs([{"name": "▶ Sesión", "top": 500}], [500, 540])  # red team: scrollBy 40 at 400 ms
    assert fixed_bars.dialogs_leave_page_still(page) == ["▶ Sesión: the page moved 40 px"]
    assert fixed_bars.LOOKS[0] < 400 < sum(fixed_bars.LOOKS)


STILL = {"inside": True, "name": "↑", "moved": 0}


class Tabs(Page):
    """A page whose bars sit where asked: how many controls each has, whether a bar is still whole
    once focus has left it, and how far each press inside a bar moved the page."""

    def __init__(self, controls, moves=(), whole=(), spots=None):
        super().__init__()
        self.controls, self.moves, self.whole, self.spots, self.measured = dict(controls), list(moves), list(whole), spots, 0
        self.motion = []

    def emulate_media(self, reduced_motion):
        self.motion.append(reduced_motion)

    def evaluate(self, script, arg=None):
        if script == fixed_bars.SPOT:
            return self.spots.pop(0) if self.spots else {"top": 85, "want": 85}
        if script == fixed_bars.FIRST:
            return self.controls.get(arg[0], 0)
        if script == fixed_bars.MARK:
            return self.whole.pop(0) if self.whole else True
        if script == fixed_bars.MOVED:
            self.measured += 1
            return self.moves.pop(0) if self.moves else STILL
        return super().evaluate(script, arg)


def test_a_press_that_moves_the_page_fails_once_per_bar_place_and_direction():
    page = Tabs({"top bar": 3, "Sujeto/Hora bar": 2}, [
        STILL, {"inside": True, "name": "▶ Inicio", "moved": 436},  # Tab across the top bar: home, 1280 x 800, before N13
        STILL, STILL, {"inside": True, "name": "↑", "moved": 441}])  # Shift+Tab across it, out, and Tab back in
    assert fixed_bars.tab_in_bars_leaves_page_still(page) == [
        "top bar stuck, Tab to ▶ Inicio: the page moved 436 px", "top bar stuck, Tab to ↑: the page moved 441 px"]
    assert page.pressed[:6] == ["Tab", "Tab", "Shift+Tab", "Shift+Tab", "Shift+Tab", "Tab"]
    assert len(page.pressed) == 6 + 6 * 3 + 2 * 4 + 6 * 3  # each Sujeto/Hora pass: across, out and back in; then motion on


def test_a_move_seen_only_with_motion_on_says_so_and_the_readers_setting_comes_back():
    page = Tabs({"top bar": 3, "Sujeto/Hora bar": 2}, [STILL] * 18 + [{"inside": True, "name": "▶ Inicio", "moved": 120}])
    assert fixed_bars.tab_in_bars_leaves_page_still(page) == ["top bar stuck, motion on, Tab to ▶ Inicio: the page moved 120 px"]
    assert page.motion == ["reduce", "no-preference", "reduce"]


def test_the_press_out_of_a_bar_may_scroll_and_a_bar_not_whole_on_screen_is_not_tried():
    page = Tabs({"top bar": 0, "Sujeto/Hora bar": 2}, whole=[False] * 12)
    assert fixed_bars.tab_in_bars_leaves_page_still(page) == []
    assert page.pressed == ["Tab", "Tab", "Shift+Tab", "Shift+Tab"] * 6  # across and out; never back into a bar now off screen
    assert page.measured == 12  # only the press across each bar is judged


def test_focus_that_leaves_a_bar_early_ends_the_pass_without_a_complaint():
    page = Tabs({"Sujeto/Hora bar": 4}, [{"inside": False, "name": "Planes", "moved": 900}] * 12)
    assert fixed_bars.tab_in_bars_leaves_page_still(page) == []
    assert len(page.pressed) == 12


def test_a_place_the_page_cannot_reach_is_skipped():
    """A stuck bar never reaches a spot lower down, however far the page is scrolled."""
    page = Tabs({"Sujeto/Hora bar": 2}, spots=[{"top": 65, "want": 85}] * 12)
    assert fixed_bars.place(page, "under the top bar") is False
    assert fixed_bars.place(page, "at the bottom") is False
    assert page.pressed == []
