"""Y22-Y23: the field card says how to stay safe at night and how to run a long exposure behind an ND.

The research audit on PR #24 (F17, F18) found the card silent on both. Night sessions in
Miraflores and Barranco carry a camera and a tripod where the UK's travel advice for Peru
reports street crime and armed robbery in tourist districts and advises against walking
alone at night. With a 10-stop ND the viewfinder goes dark and the AF cannot see, so the
frame is composed and focused, and the lens set to MF, before the filter goes on; Canon's
EOS 6D self-timer note says to cover the eyepiece, since light through the viewfinder throws
the exposure off. Both notes sit outside any one plan, so every plan's reader sees them.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = (ROOT / "field_card.html").read_text(encoding="utf-8")
PLANS = json.loads((ROOT / "data/plans.json").read_text(encoding="utf-8"))["plans"]


VOID = {"br", "img", "input", "meta", "link", "hr", "source", "wbr"}


class Tips(HTMLParser):
    """Each `.fc-mini` tip's title and text as a screen reader gets them, and whether it sits inside one plan's markup."""

    def __init__(self):
        super().__init__()
        self.stack: list[tuple[bool, bool]] = []  # (inside one plan's markup, aria-hidden)
        self.tips: dict[str, tuple[str, bool]] = {}
        self.tip: list[str] | None = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in VOID:
            return
        self.stack.append(("data-plan" in attrs, attrs.get("aria-hidden") == "true"))
        if tag == "li" and "fc-mini" in (attrs.get("class") or "").split():
            self.tip, self.depth, self.plan_only = [], len(self.stack), any(plan for plan, _ in self.stack)

    def handle_endtag(self, tag):
        if tag in VOID or not self.stack:
            return
        if self.tip is not None and len(self.stack) == self.depth:
            title, _, text = " ".join(" ".join(self.tip).split()).partition(" | ")
            self.tips[title] = (text, self.plan_only)
            self.tip = None
        self.stack.pop()

    def handle_data(self, data):
        if self.tip is not None and not any(hidden for _, hidden in self.stack):
            self.tip.append(data)
            if self.lasttag == "b" and data.strip():
                self.tip.append(" | ")


def mini(card: str, title: str) -> str | None:
    """The text of the card's tip with this title, if it is shown for every plan."""
    parser = Tips()
    parser.feed(card)
    text, plan_only = parser.tips.get(title, (None, True))
    return None if plan_only else text


def night_gaps(card: str) -> list[str]:
    text = mini(card, "De noche") or ""
    return [words for words in ("acompañado", "bolsa pequeña", "teléfono aparte", "iluminados", "trípode solo") if words not in text]


def nd_gaps(card: str) -> list[str]:
    text = mini(card, "Con el ND la foto falla") or ""
    gaps = [words for words in ("Compón", "enfoca", "MF", "enroscar el filtro", "tapa del ocular") if words not in text]
    if not gaps and not text.index("Compón") < text.index("MF") < text.index("enroscar el filtro"):
        gaps.append("compose, focus and MF before the filter")
    return gaps


def test_y22_the_card_says_how_to_go_out_at_night():
    assert any(shot["settings_by_time"].get("night") for plan in PLANS for shot in plan["shots"])
    assert not night_gaps(CARD), night_gaps(CARD)


def test_y23_the_nd_tip_puts_focus_before_the_filter_and_covers_the_eyepiece():
    assert any(s.get("nd_stops") == 10 for plan in PLANS for shot in plan["shots"] for s in shot["settings_by_time"].values() if s)
    assert not nd_gaps(CARD), nd_gaps(CARD)
