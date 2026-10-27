"""Where the sun is at any minute of a day in Lima, and the light it puts on a wall.

Requirements W01 (the sun's bearing and apparent height at any minute, within
0.3° of an independent ephemeris), W02 (the length and direction of a shadow)
and W03 (when a wall facing a given bearing has direct sun, and how steeply
it strikes it).

The reference positions are NREL's Solar Position Algorithm (pvlib 0.16.1,
`spa_python`, San Isidro at 100 m, 1013.25 hPa, 19 °C), which claims ±0.0003°.
`astral` 3.2, a second, unrelated implementation, agrees with every one of
them within 0.02°, except azimuth within 2° of the zenith, where a bearing is
not meaningful. They are written here as constants, so the test needs neither
package nor the network.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import sun_times as st  # noqa: E402

JS = ROOT / "assets" / "sun_times.js"

# "YYYY-MM-DD HH:MM" Lima time: (azimuth, apparent elevation), NREL SPA.
SPA = {
    "2026-06-21 07:00": (64.33, 6.50),
    "2026-06-21 12:00": (3.94, 54.39),
    "2026-06-21 17:00": (297.05, 10.83),
    "2026-12-21 06:30": (112.01, 10.24),
    "2026-12-21 12:15": (190.02, 78.48),
    "2026-12-21 18:00": (247.31, 6.36),
    "2026-10-17 09:00": (90.78, 47.36),
    "2026-10-17 15:30": (267.13, 36.85),
    "2026-03-20 12:10": (6.53, 77.79),
    "2026-10-23 12:00": (285.48, 88.08),  # the sun passes within 2° of the zenith
    "2026-02-18 12:20": (37.08, 89.19),   # and within 1°
}


def at(key: str) -> tuple[date, int]:
    day, hm = key.split()
    h, m = (int(x) for x in hm.split(":"))
    return date.fromisoformat(day), h * 60 + m


def bearing_gap(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


@pytest.mark.parametrize("key", sorted(SPA))
def test_w01_the_sun_stands_where_an_independent_ephemeris_puts_it(key):
    azimuth, elevation = SPA[key]
    position = st.sun_position(*at(key))
    assert position["apparent"] == pytest.approx(elevation, abs=0.3), key
    if elevation < 85:  # near the zenith a small error in height swings the bearing a long way
        assert bearing_gap(position["azimuth"], azimuth) < 0.3, key


def test_w01_forward_position_and_the_day_plan_agree_at_every_boundary():
    """Two separate computations in the module: the day plan inverts the hour angle for an
    elevation, the position runs forward from a time. At each boundary the plan names, the
    sun's geometric height must be that boundary's."""
    for day in (date(2026, 6, 21), date(2026, 12, 21), date(2026, 10, 17)):
        plan = st.day_plan(day)
        for key, elevation in (("blue_am_start", st.CIVIL_ELEVATION), ("sunrise", st.SUNRISE_ELEVATION),
                               ("golden_am_end", st.GOLDEN_HIGH_ELEVATION), ("golden_pm_start", st.GOLDEN_HIGH_ELEVATION),
                               ("sunset", st.SUNRISE_ELEVATION), ("blue_pm_end", st.CIVIL_ELEVATION)):
            assert st.sun_position(day, plan[key])["elevation"] == pytest.approx(elevation, abs=0.05), (day, key)
        assert bearing_gap(st.sun_position(day, plan["sunset"])["azimuth"], plan["sunset_azimuth"]) < 0.2


def test_w01_refraction_lifts_the_low_sun_and_leaves_the_high_sun_alone():
    """At the horizon the air lifts the sun's image about 0.5° (34′, Bennett 1982); at 45°
    by about 1′."""
    day = date(2026, 10, 17)
    low = st.sun_position(day, st.day_plan(day)["sunset"])
    assert 0.45 < low["apparent"] - low["elevation"] < 0.65
    high = st.sun_position(day, 9 * 60 + 40)
    assert high["elevation"] > 40 and 0 < high["apparent"] - high["elevation"] < 0.03


def test_w02_a_shadow_is_as_long_as_the_sun_is_low_and_points_away_from_it():
    assert st.shadow(1.70, {"apparent": 45.0, "azimuth": 100.0}) == pytest.approx((1.70, 280.0))
    length, bearing = st.shadow(1.70, st.sun_position(*at("2026-12-21 18:00")))
    assert length == pytest.approx(1.70 / math.tan(math.radians(6.36)), rel=0.03)  # about 15 m
    assert bearing_gap(bearing, 67.31) < 0.3
    assert st.shadow(1.70, st.sun_position(date(2026, 12, 21), 22 * 60)) is None  # night: no shadow


def test_w03_a_wall_is_lit_only_while_the_sun_is_up_and_in_front_of_it():
    """A west-facing wall on 17 October: in shade all morning, lit from about the time the
    sun crosses its plane (shortly after noon, when the sun is almost overhead) to sunset."""
    day = date(2026, 10, 17)
    windows = st.wall_light(day, 270.0)
    plan = st.day_plan(day)
    lit = windows["direct"]
    assert len(lit) == 1
    start, end = lit[0]
    assert 11 * 60 + 30 < start < 12 * 60 + 30
    assert end == pytest.approx(plan["sunset"], abs=2)
    # the sun grazes the wall right after it crosses the wall's plane and stands low before sunset
    assert windows["raking"] and windows["raking"][0][0] == pytest.approx(start, abs=2)
    assert st.wall_angle(st.sun_position(day, 10 * 60), 270.0) < 0  # morning: behind the wall


def test_w03_the_angle_on_a_wall_is_the_sun_seen_from_the_wall():
    """Head-on at the horizon is 90° to the surface; edge-on is 0°; the sun overhead is 0°."""
    assert st.wall_angle({"apparent": 0.0, "azimuth": 90.0}, 90.0) == pytest.approx(90.0)
    assert st.wall_angle({"apparent": 0.0, "azimuth": 180.0}, 90.0) == pytest.approx(0.0, abs=1e-9)
    assert st.wall_angle({"apparent": 90.0, "azimuth": 90.0}, 90.0) == pytest.approx(0.0, abs=1e-9)
    assert st.wall_angle({"apparent": 60.0, "azimuth": 90.0}, 90.0) == pytest.approx(30.0)


def test_w03_walls_facing_opposite_ways_share_no_minute_of_direct_sun():
    day = date(2026, 6, 21)
    for facing in (0.0, 45.0, 90.0, 135.0):
        a, b = st.wall_light(day, facing)["direct"], st.wall_light(day, facing + 180)["direct"]
        overlap = sum(max(0, min(e1, e2) - max(s1, s2)) for s1, e1 in a for s2, e2 in b)
        assert overlap <= 1, facing
        # in June the sun stays north of Lima at noon: a north wall gets sun all day, a south wall none
    assert st.wall_light(day, 180.0)["direct"] == []
    north = st.wall_light(day, 0.0)["direct"]
    assert north and north[0][0] == pytest.approx(st.day_plan(day)["sunrise"], abs=2)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_w01_w03_the_browser_runs_the_same_arithmetic():
    days = ["2026-06-21", "2026-10-17", "2026-12-21", "2026-02-18"]
    minutes = list(range(300, 1140, 37))
    script = (
        f"const S=require({json.dumps(str(JS))});const out={{}};"
        f"for(const d of {json.dumps(days)}){{out[d]={{pos:{json.dumps(minutes)}.map(m=>S.position(d,m)),"
        "walls:[0,90,180,270,300].map(b=>S.wallLight(d,b))}}"
        "process.stdout.write(JSON.stringify(out));"
    )
    result = json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)
    for day, js in result.items():
        d = date.fromisoformat(day)
        for minute, pos in zip(minutes, js["pos"]):
            py = st.sun_position(d, minute)
            assert pos["apparent"] == pytest.approx(py["apparent"], abs=0.01), (day, minute)
            assert bearing_gap(pos["azimuth"], py["azimuth"]) < 0.01, (day, minute)
        for facing, walls in zip((0, 90, 180, 270, 300), js["walls"]):
            py = st.wall_light(d, float(facing))
            for kind in ("direct", "raking", "frontal"):
                assert walls[kind] == [list(w) for w in py[kind]], (day, facing, kind)
