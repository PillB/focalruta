"""W12: the field card puts the chosen session in the phone's calendar, with a reminder.

Planners such as PhotoPills let a photographer save a plan with an alert; FocalRuta told the
reader when the light comes but left remembering it to them. The card now writes an iCalendar
file (RFC 5545) for the plan, light and date chosen on it: the event starts half an hour
before that light, to set up, and ends when it does, with the place, the sun's times and the
packing list, and an alert two hours before. The checks hold the file to the RFC's rules and
its times to the Python sun twin, independently of the card's script.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sun_times as st  # noqa: E402

JS_CARD = ROOT / "assets" / "field_card.js"
JS_SUN = ROOT / "assets" / "sun_times.js"
CARD = (ROOT / "field_card.html").read_text(encoding="utf-8")
DAY = "2026-11-24"
SETUP_MIN = 30
NIGHT_SESSION_MIN = 120
PLACE = "Malecón Cisneros, Miraflores; frente al mar"
STAMP = "2026-10-28T15:00:00Z"


def calendar(slot: str) -> str:
    event = {"uid": f"plan_b-{slot}-{DAY}@focalruta", "summary": "FocalRuta · Plan B", "location": PLACE,
             "description": "Luz: tarde.\nLleva: trípode, ND8; agua", "date": DAY, "slot": slot}
    script = (f"global.LimaSun=require({json.dumps(str(JS_SUN))});const F=require({json.dumps(str(JS_CARD))});"
              f"const e={json.dumps(event)};const w=F.sessionWindow(e.slot,LimaSun.dayPlan(e.date));"
              f"process.stdout.write(F.icsText(Object.assign(e,{{start:w[0],end:w[1],stamp:Date.parse({json.dumps(STAMP)})}})));")
    # Bytes, not text=True: universal newlines would turn the file's CRLF into LF.
    return subprocess.run(["node", "-e", script], check=True, capture_output=True).stdout.decode("utf-8")


def unfold(text: str) -> list[str]:
    return text.replace("\r\n ", "").split("\r\n")


def utc(minutes_local: float) -> str:
    moment = datetime.combine(date.fromisoformat(DAY), datetime.min.time(), timezone.utc) + timedelta(minutes=round(minutes_local) + 300)
    return moment.strftime("%Y%m%dT%H%M%SZ")


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_w12_the_calendar_file_follows_rfc_5545():
    text = calendar("afternoon")
    assert text.endswith("\r\n") and "\n" not in text.replace("\r\n", "")
    assert all(len(line.encode("utf-8")) <= 75 for line in text.split("\r\n")), "a line is longer than 75 octets"
    lines = unfold(text)
    for block in ("VCALENDAR", "VEVENT", "VALARM"):
        assert lines.count(f"BEGIN:{block}") == lines.count(f"END:{block}") == 1, block
    for prop in ("VERSION:2.0", "PRODID:", "UID:plan_b-afternoon-2026-11-24@focalruta", "DTSTAMP:20261028T150000Z",
                 "DTSTART:", "DTEND:", "SUMMARY:FocalRuta · Plan B", "TRIGGER:-PT2H", "ACTION:DISPLAY"):
        assert any(line.startswith(prop) for line in lines), prop
    assert r"LOCATION:Malecón Cisneros\, Miraflores\; frente al mar" in lines
    assert r"DESCRIPTION:Luz: tarde.\nLleva: trípode\, ND8\; agua" in lines


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize("slot", ["day", "afternoon", "night"])
def test_w12_the_event_covers_the_light_chosen_with_time_to_set_up(slot):
    plan = st.day_plan(date.fromisoformat(DAY))
    start, end = {"day": (plan["sunrise"], plan["golden_pm_start"]),
                  "afternoon": (plan["golden_pm_start"], plan["blue_pm_end"]),
                  "night": (plan["blue_pm_end"], plan["blue_pm_end"] + NIGHT_SESSION_MIN)}[slot]
    lines = unfold(calendar(slot))
    shown = {line.split(":", 1)[0]: line.split(":", 1)[1] for line in lines if line.startswith(("DTSTART:", "DTEND:"))}
    assert shown == {"DTSTART": utc(start - SETUP_MIN), "DTEND": utc(end)}, (slot, shown)


def test_w12_the_card_offers_the_calendar_only_where_a_script_can_write_it():
    button = re.search(r'<button type="button" id="fc-ics"[^>]*>', CARD)
    assert button and " hidden" in button.group(0)
    script = JS_CARD.read_text(encoding="utf-8")
    assert "text/calendar" in script and "ics.hidden = false" in script
