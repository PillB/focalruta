"""W10: the field card converts a metered time to the ND's time and gives the hyperfocal distance.

The red team set FocalRuta beside the field apps photographers carry (PhotoPills, an ND
calculator, a depth-of-field table) and found the two numbers a long exposure and a
landscape need on site missing from the card: what the shutter must become with the ND that
is on the lens, and where to focus so the frame is sharp to infinity. Both are tables
printed in the card, so they work with no signal and no script. The checks recompute every
cell from first principles: a filter of n stops multiplies the time by 2^n, and the
hyperfocal distance is f^2 / (N c) + f with c = 0.030 mm, the normal-print circle of
confusion the rest of the site uses.
"""
from __future__ import annotations

import math
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = (ROOT / "field_card.html").read_text(encoding="utf-8")
STOPS_IN_KIT = (2, 3, 6, 10)
# The dial's labels round powers of 2^(1/3): "1/60" is 1/64 s, "15"" is 16 s, "30"" is 32 s.
LONGEST_TIMED_S = 32


def table(caption_word: str) -> list[list[str]]:
    found = re.search(rf'<table class="fc-table"[^>]*>\s*<caption>[^<]*{caption_word}.*?</table>', CARD, re.S)
    assert found, f"no field card table about {caption_word!r}"
    rows = re.findall(r"<tr>(.*?)</tr>", found.group(0), re.S)
    text = lambda cell: " ".join(unescape(re.sub(r"<[^>]+>", " ", cell)).split())  # noqa: E731  a <br> reads as a space
    return [[text(cell) for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)] for row in rows]


def seconds(label: str) -> float:
    if label.startswith("B · "):
        minutes = re.search(r"(\d+) min", label)
        secs = re.search(r"(\d+) s", label)
        return (int(minutes.group(1)) * 60 if minutes else 0) + (int(secs.group(1)) if secs else 0)
    if label.startswith("1/"):
        nominal = 1 / float(label[2:])
    else:
        whole, tenths = re.fullmatch(r'(\d+)"(\d*)', label).groups()  # the camera's 0"3, 1"3, 30"
        nominal = float(f"{whole}.{tenths or 0}")
    return 2 ** (round(3 * math.log2(nominal)) / 3)


def test_w10_the_nd_table_gives_every_kit_filter_its_time():
    rows = table("ND")
    head, body = rows[0], rows[1:]
    assert [int(re.search(r"(\d+) pasos", h).group(1)) for h in head[1:]] == list(STOPS_IN_KIT), head
    wrong = []
    for row in body:
        metered = seconds(row[0])
        for stops, shown in zip(STOPS_IN_KIT, row[1:]):
            want = metered * 2 ** stops
            if want > LONGEST_TIMED_S:
                ok = shown.startswith("B · ") and abs(seconds(shown) - want) <= 1
            else:
                ok = not shown.startswith("B") and abs(math.log2(seconds(shown) / want)) <= 1 / 6 + 1e-9
            if not ok:
                wrong.append((row[0], stops, shown, round(want, 3)))
    assert len(body) >= 10 and not wrong, wrong


def test_w10_the_hyperfocal_table_matches_the_formula_for_each_prime():
    rows = table("iperfocal")
    head, body = rows[0], rows[1:]
    focals = [int(re.search(r"(\d+) mm", h).group(1)) for h in head[1:]]
    wrong = []
    for row in body:
        n = float(row[0].removeprefix("f/"))
        for focal, shown in zip(focals, row[1:]):
            hyper = (focal * focal / (n * 0.030) + focal) / 1000
            far, near = (float(x) for x in re.findall(r"(\d+(?:\.\d+)?) m", shown))
            if abs(far - hyper) > 0.05 + 0.01 * hyper or abs(near - hyper / 2) > 0.05 + 0.01 * hyper:
                wrong.append((focal, n, shown, round(hyper, 2)))
    assert focals == [35, 50, 85] and len(body) == 4 and not wrong, wrong


def test_w10_the_tables_say_when_the_numbers_stop_holding():
    notes = re.findall(r'<p class="fc-table-note">(.*?)</p>', CARD, re.S)
    text = " ".join(unescape(re.sub(r"<[^>]+>", "", n)) for n in notes)
    assert "Bulb" in text and "30 s" in text and "histograma" in text
    assert "0.03 mm" in text and "100 %" in text and "difracción" in text
