"""Sun times shown by the Lima sun panel.

Requirements: S01 (sunrise, sunset and twilight within two minutes of an
independent ephemeris), S02 (golden and blue hour boundaries), S03 (sunset
bearing), S04 (the browser panel runs the same arithmetic as the Python twin).

Reference values were computed with the `astral` 3.2 package (an independent
implementation of the NOAA equations) for San Isidro, Lima (-12.097,
-77.036, America/Lima) and are written here as constants, so the test needs
neither the package nor the network.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import sun_times as st  # noqa: E402

TOLERANCE_MIN = 2.0

# date: (civil dawn, golden AM start, sunrise, golden AM end, golden PM start, sunset, golden PM end, civil dusk, sunset azimuth)
REFERENCE = {
    "2026-06-21": ("06:04:18", "06:13:04", "06:27:45", "06:57:41", "17:22:20", "17:52:16", "18:06:57", "18:15:43", 293.8),
    "2026-12-21": ("05:17:34", "05:26:30", "05:41:19", "06:10:59", "18:01:39", "18:31:19", "18:46:08", "18:55:04", 245.8),
    "2026-10-17": ("05:20:14", "05:28:26", "05:42:07", "06:09:39", "17:37:20", "18:04:53", "18:18:35", "18:26:48", 260.1),
}
KEYS = ("blue_am_start", "golden_am_start", "sunrise", "golden_am_end",
        "golden_pm_start", "sunset", "golden_pm_end", "blue_pm_end")


def minutes(hms: str) -> float:
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 60 + m + s / 60


@pytest.mark.parametrize("day", sorted(REFERENCE))
def test_python_sun_times_match_an_independent_ephemeris(day):
    plan = st.day_plan(date.fromisoformat(day))
    *times, azimuth = REFERENCE[day]
    for key, expected in zip(KEYS, times):
        assert plan[key] == pytest.approx(minutes(expected), abs=TOLERANCE_MIN), (day, key)
    assert plan["sunset_azimuth"] == pytest.approx(azimuth, abs=1.0)


def test_sunset_swings_across_the_sea_through_the_year():
    # The old Plan B copy said 278-288 deg; the real swing is about 246-294 deg.
    bearings = [st.sunset_azimuth(date(2026, month, 21)) for month in range(1, 13)]
    assert min(bearings) < 250 and max(bearings) > 290


def test_peru_has_no_daylight_saving_shift():
    # Sunrise moves smoothly; a DST jump would show up as a ~60 min step.
    days = [date(2026, m, d) for m in range(1, 13) for d in (1, 15)]
    rises = [st.event_minutes(d, st.SUNRISE_ELEVATION, True) for d in days]
    assert max(abs(a - b) for a, b in zip(rises, rises[1:])) < 20


JS = ROOT / "assets" / "sun_times.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_browser_panel_uses_the_same_arithmetic():
    script = (
        f"const S=require({json.dumps(str(JS))});"
        "const out={};"
        f"for (const d of {json.dumps(sorted(REFERENCE))}) out[d]=S.dayPlan(d);"
        "process.stdout.write(JSON.stringify(out));"
    )
    result = json.loads(subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout)
    for day, js_plan in result.items():
        py_plan = st.day_plan(date.fromisoformat(day))
        for key in KEYS + ("sunset_azimuth",):
            assert js_plan[key] == pytest.approx(py_plan[key], abs=0.05), (day, key)


# S05: the panel opens on today's date in Lima, whatever the reader's own clock says.
# The old code shifted the instant by the reader's UTC offset and then read local
# getters; when the reader's zone changed daylight saving in between, it landed on
# the wrong day (red team: Europe/Madrid at 2026-03-29T05:30Z showed 2026-03-28).
TODAY_CASES = [
    ("Europe/Madrid", "2026-03-29T05:30:00Z"),   # Madrid springs forward at 01:00Z that day
    ("America/New_York", "2026-11-01T05:30:00Z"),  # New York falls back at 06:00Z
    ("Asia/Tokyo", "2026-10-17T04:59:00Z"),       # Lima still on the 16th
    ("America/Lima", "2026-10-17T05:00:00Z"),     # Lima midnight exactly
    ("Pacific/Kiritimati", "2026-01-01T04:59:59Z"),
]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize("zone,instant", TODAY_CASES)
def test_panel_opens_on_today_in_lima_from_any_reader_time_zone(zone, instant):
    from datetime import datetime
    from zoneinfo import ZoneInfo

    moment = datetime.fromisoformat(instant.replace("Z", "+00:00"))
    expected = moment.astimezone(ZoneInfo("America/Lima")).date().isoformat()
    script = (f"const S=require({json.dumps(str(JS))});"
              f"process.stdout.write(S.limaToday(Date.parse({json.dumps(instant)})));")
    env = {"PATH": __import__("os").environ["PATH"], "TZ": zone}
    shown = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True, env=env).stdout
    assert shown == expected, (zone, instant, shown)


def test_panel_reads_the_date_from_the_shared_helper():
    panel = (ROOT / "index.html").read_text(encoding="utf-8").split("<!-- LIMA_SUN_PANEL_END -->")[0][-3000:]
    assert "S.limaToday(Date.now())" in panel
    assert "getTimezoneOffset" not in panel
