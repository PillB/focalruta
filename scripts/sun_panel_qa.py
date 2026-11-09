"""W04: the home page's sun panel shows where the sun is, and when a wall has its light.

Every value the panel prints is held to scripts/sun_times.py, the twin the planner
tests hold to NREL's SPA, so the browser check reads what a reader sees and compares
it with an independent computation, not with the page's own script.
"""
from __future__ import annotations

import math
import re
from datetime import date

import moon_times as mt
import sun_times as st

DAY = "2026-10-17"
FACING = 270.0
# 16:00 in Lima (UTC-5) on 2026-10-27.
CLOCK = "2026-10-27T21:00:00Z"

READ = """()=>({time:document.getElementById('sun-time-out')?.textContent,text:document.getElementById('sun-pos-text')?.textContent,
value:Number(document.getElementById('sun-time')?.value),min:Number(document.getElementById('sun-time')?.min),
max:Number(document.getElementById('sun-time')?.max),valuetext:document.getElementById('sun-time')?.getAttribute('aria-valuetext'),
wall:document.getElementById('sun-wall')?.textContent,drawn:document.getElementById('sun-map-wall')?.childElementCount,
mark:[...['cx','cy','visibility']].map(k=>document.getElementById('sun-map-mark')?.getAttribute(k)),
date:document.getElementById('sun-date')?.value,label:document.getElementById('sun-map')?.getAttribute('aria-label')})"""


def clock(minutes: float) -> str:
    return st.clock(minutes)


def spans(runs) -> str:
    return " y ".join(f"{clock(a)}–{clock(b)}" for a, b in runs) if runs else "en ningún momento"


def expected_sentence(day: date, minute: int) -> str:
    pos = st.sun_position(day, minute)
    if pos["apparent"] <= 0:
        return f"A las {clock(minute)} el sol está {max(1, round(-pos['apparent']))}° bajo el horizonte"
    length, _bearing = st.shadow(1.7, pos)
    return (f"A las {clock(minute)} el sol está al {compass(pos['azimuth'])} (rumbo {round(pos['azimuth']) % 360}°), "
            f"a {round(pos['apparent'])}° sobre el horizonte. Una persona de 1.70 m proyecta una sombra de {length:.1f} m")


NAMES = ["norte", "nor-noreste", "noreste", "este-noreste", "este", "este-sureste", "sureste", "sur-sureste",
         "sur", "sur-suroeste", "suroeste", "oeste-suroeste", "oeste", "oeste-noroeste", "noroeste", "nor-noroeste"]


def compass(bearing: float) -> str:
    return NAMES[round(bearing / 22.5) % 16]


def projected(day: date, minute: int) -> tuple[float, float]:
    pos = st.sun_position(day, minute)
    r = (90 - max(0.0, pos["apparent"])) / 90 * 100
    a = math.radians(pos["azimuth"])
    return r * math.sin(a), -r * math.cos(a)


def pick(page, day: str, facing: str) -> None:
    page.fill("#sun-date", day)
    page.dispatch_event("#sun-date", "change")
    page.select_option("#sun-facade", facing)


def slider_steps(page, record, name: str) -> None:
    """Keyboard alone moves the hour, and the printed position follows the clock it names."""
    day = date.fromisoformat(DAY)
    page.focus("#sun-time")
    page.keyboard.press("Home")
    start = page.evaluate(READ)
    plan = st.day_plan(day)
    record(f"{name} hour starts at the morning blue hour", start["value"] == start["min"] and start["min"] <= plan["blue_am_start"] < start["min"] + 5, start)
    record(f"{name} before sunrise the sun is below the horizon", expected_sentence(day, start["value"]) in (start["text"] or ""), [start["text"], expected_sentence(day, start["value"])])
    for _ in range(12 * 9):  # nine hours on, in 5-minute steps: mid-afternoon
        page.keyboard.press("ArrowRight")
    later = page.evaluate(READ)
    record(f"{name} arrow keys move the hour 5 minutes a press", later["value"] == start["value"] + 540, [start["value"], later["value"]])
    record(f"{name} the hour is named for assistive technology", later["valuetext"] == later["time"] == clock(later["value"]), later)
    record(f"{name} printed position matches the ephemeris", expected_sentence(day, later["value"]) in (later["text"] or ""), [later["text"], expected_sentence(day, later["value"])])
    x, y = projected(day, later["value"])
    cx, cy, shown = later["mark"]
    record(f"{name} the sun is drawn where it stands", shown == "visible" and abs(float(cx) - x) < 0.2 and abs(float(cy) - y) < 0.2, [later["mark"], round(x, 1), round(y, 1)])
    page.keyboard.press("End")
    end = page.evaluate(READ)
    record(f"{name} hour ends at the evening blue hour", end["value"] == end["max"] and end["max"] - 5 < plan["blue_pm_end"] <= end["max"] and end["mark"][2] == "hidden", end)


def wall_windows(page, record, name: str) -> None:
    day = date.fromisoformat(DAY)
    light = st.wall_light(day, FACING)
    state = page.evaluate(READ)
    for kind, label in (("direct", "Sol directo"), ("raking", "Luz rasante, que marca la textura"), ("frontal", "Luz casi de frente, que la aplana")):
        want = f"{label}: {spans(light[kind])}."
        record(f"{name} west wall {kind} light matches the ephemeris", want in (state["wall"] or ""), [want, state["wall"]])
    record(f"{name} the wall and its front are drawn", state["drawn"] == 3, state["drawn"])
    page.select_option("#sun-facade", "")
    record(f"{name} no wall chosen, none drawn", page.evaluate(READ)["drawn"] == 0)


def now_button(browser, url: str, record, name: str) -> None:
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.clock.install(time=CLOCK)
    page.goto(url, wait_until="load", timeout=60000)
    opened = page.evaluate(READ)
    record(f"{name} opens on today in Lima at the time it is there", opened["date"] == "2026-10-27" and opened["time"] == "16:00", opened)
    pick(page, "2026-12-21", "90")
    page.focus("#sun-time")
    page.keyboard.press("Home")
    page.click("#sun-now")
    back = page.evaluate(READ)
    record(f"{name} Ahora brings back today and the time", back["date"] == "2026-10-27" and back["time"] == "16:00", back)
    record(f"{name} the drawing names its date", bool(re.search(r"el 2026-10-27 .*sale al .*se pone al ", back["label"] or "")), back["label"])
    context.close()


# W09: a full moon rising at dusk, a new moon, a day the moon never rises, and a moon that is
# down at dusk and rises later; each read against the Python twin, held to USNO's tables.
MOON_DAYS = ("2026-11-24", "2026-11-09", "2026-11-01", "2026-12-06", "2026-10-28")
MOON_READ = "()=>({grid:document.getElementById('sun-grid')?.innerText,read:document.getElementById('moon-read')?.textContent})"


def moon_expected(day: date) -> tuple[list[str], str]:
    plan, md = st.day_plan(day), mt.moon_day(day)
    at = plan["blue_pm_end"]
    moon, lit = mt.moon_at(day, at), None
    lit = round(moon["fraction"] * 100)
    where = lambda b: f"por el {compass(b)}, rumbo {round(b) % 360}°"  # noqa: E731
    rumbo = lambda b: f"al {compass(b)} (rumbo {round(b) % 360}°)"  # noqa: E731
    cells = [f"Sale la luna\n{clock(md['rise']) if md['rise'] is not None else 'no sale'}\n"
             f"{where(md['rise_azimuth']) if md['rise'] is not None else 'en todo el día'}",
             f"Se pone la luna\n{clock(md['set']) if md['set'] is not None else 'no se pone'}\n"
             f"{where(md['set_azimuth']) if md['set'] is not None else 'en todo el día'}",
             f"{moon['phase'][0].upper() + moon['phase'][1:]}\n{lit} %\niluminada a las {clock(at)}"]
    when = f"Al terminar la hora azul ({clock(at)}) la luna "
    if lit < 3:
        sentence = "Luna nueva: esta noche la luna no suma luz a las tomas de noche."
    elif moon["height"] > 0:
        tail = ": suma luz a las tomas de noche y puede entrar en un encuadre hacia ese lado." if lit >= 50 else "."
        sentence = f"{when}está a {max(1, round(moon['height']))}° sobre el horizonte, {rumbo(moon['azimuth'])}{tail}"
    elif md["rise"] is not None and md["rise"] > at:
        sentence = f"{when}está bajo el horizonte; sale a las {clock(md['rise'])}, {rumbo(md['rise_azimuth'])}."
    else:
        sentence = f"{when}está bajo el horizonte y no sale antes de medianoche."
    return cells, sentence


def moon_read(page, record, name: str) -> None:
    for day in MOON_DAYS:
        page.fill("#sun-date", day)
        page.dispatch_event("#sun-date", "change")
        shown = page.evaluate(MOON_READ)
        cells, sentence = moon_expected(date.fromisoformat(day))
        record(f"{name} {day} moonrise, moonset and phase match the twin", all(c in (shown["grid"] or "") for c in cells), [cells, shown["grid"]])
        record(f"{name} {day} the night's moon is described", shown["read"] == sentence, [sentence, shown["read"]])


def check(browser, url: str, record, name: str) -> None:
    for width in (320, 1280):
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url, wait_until="load", timeout=60000)
        if not page.locator("#sun-time").count():
            record(f"{name} {width} sun position panel", False, "no #sun-time on the page")
        pick(page, DAY, str(int(FACING)))
        slider_steps(page, record, f"{name} {width}")
        wall_windows(page, record, f"{name} {width}")
        moon_read(page, record, f"{name} {width}")
        record(f"{name} {width} sun panel errors", not errors, errors)
        page.close()
    now_button(browser, url, record, name)
