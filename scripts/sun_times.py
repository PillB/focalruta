"""Sun times for planning a shoot in Lima.

Python twin of assets/sun_times.js: both implement NOAA's general solar
position equations (https://gml.noaa.gov/grad/solcalc/calcdetails.html) with
the same constants, so the tests can hold the browser panel to independently
published values without a browser.

Event elevations follow the usual photographic definitions:
  sunrise/sunset  -0.833 deg (upper limb on the horizon, standard refraction)
  civil twilight  -6 deg
  golden hour     between +6 and -4 deg
  blue hour       between -4 and -6 deg
"""
from __future__ import annotations

import math
from datetime import date

# San Isidro, Lima. Every plan sits within ~8 km of it, which moves the times
# by well under a minute.
LIMA_LAT = -12.097
LIMA_LON = -77.036
LIMA_UTC_OFFSET_H = -5  # Peru keeps UTC-5 all year (no daylight saving)

SUNRISE_ELEVATION = -0.833
CIVIL_ELEVATION = -6.0
GOLDEN_HIGH_ELEVATION = 6.0
BLUE_GOLDEN_BOUNDARY = -4.0


def julian_day(day: date) -> float:
    """Julian day at 0h UT."""
    y, m = day.year, day.month
    if m <= 2:
        y, m = y - 1, m + 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day.day + b - 1524.5


def solar_declination_and_eot(jd: float) -> tuple[float, float]:
    """Declination (deg) and equation of time (minutes) at a Julian day."""
    t = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360
    m = math.radians(357.52911 + t * (35999.05029 - 0.0001537 * t))
    e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    c = (math.sin(m) * (1.914602 - t * (0.004817 + 0.000014 * t))
         + math.sin(2 * m) * (0.019993 - 0.000101 * t) + math.sin(3 * m) * 0.000289)
    omega = math.radians(125.04 - 1934.136 * t)
    apparent_long = math.radians(l0 + c - 0.00569 - 0.00478 * math.sin(omega))
    mean_obliq = 23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60) / 60
    obliq = math.radians(mean_obliq + 0.00256 * math.cos(omega))
    declination = math.degrees(math.asin(math.sin(obliq) * math.sin(apparent_long)))
    y = math.tan(obliq / 2) ** 2
    l0r = math.radians(l0)
    eot = 4 * math.degrees(y * math.sin(2 * l0r) - 2 * e * math.sin(m) + 4 * e * y * math.sin(m) * math.cos(2 * l0r)
                           - 0.5 * y * y * math.sin(4 * l0r) - 1.25 * e * e * math.sin(2 * m))
    return declination, eot


def event_minutes(day: date, elevation: float, rising: bool,
                  lat: float = LIMA_LAT, lon: float = LIMA_LON, utc_offset_h: float = LIMA_UTC_OFFSET_H) -> float | None:
    """Local clock minutes after midnight when the sun crosses `elevation`; None if it never does."""
    jd0 = julian_day(day)
    minutes_utc = 720.0 - 4 * lon
    for _ in range(3):
        declination, eot = solar_declination_and_eot(jd0 + minutes_utc / 1440)
        phi, delta = math.radians(lat), math.radians(declination)
        cos_h = (math.sin(math.radians(elevation)) - math.sin(phi) * math.sin(delta)) / (math.cos(phi) * math.cos(delta))
        if not -1 <= cos_h <= 1:
            return None
        hour_angle = math.degrees(math.acos(cos_h))
        noon_utc = 720.0 - 4 * lon - eot
        minutes_utc = noon_utc - 4 * hour_angle if rising else noon_utc + 4 * hour_angle
    return minutes_utc + utc_offset_h * 60


def sunset_azimuth(day: date, lat: float = LIMA_LAT, lon: float = LIMA_LON) -> float:
    """Compass bearing (deg, clockwise from north) of the sun at sunset."""
    minutes_utc = event_minutes(day, SUNRISE_ELEVATION, rising=False, lat=lat, lon=lon, utc_offset_h=0)
    declination, _eot = solar_declination_and_eot(julian_day(day) + minutes_utc / 1440)
    phi, delta = math.radians(lat), math.radians(declination)
    # At the horizon, cos(azimuth from north) = sin(dec) / cos(lat), corrected for the refraction dip.
    h = math.radians(SUNRISE_ELEVATION)
    cos_az = (math.sin(delta) - math.sin(phi) * math.sin(h)) / (math.cos(phi) * math.cos(h))
    return 360.0 - math.degrees(math.acos(max(-1.0, min(1.0, cos_az))))


def day_plan(day: date) -> dict[str, float]:
    """Every boundary the planner shows, in local minutes after midnight."""
    def at(elevation, rising):
        return event_minutes(day, elevation, rising)
    return {
        "blue_am_start": at(CIVIL_ELEVATION, True),
        "golden_am_start": at(BLUE_GOLDEN_BOUNDARY, True),
        "sunrise": at(SUNRISE_ELEVATION, True),
        "golden_am_end": at(GOLDEN_HIGH_ELEVATION, True),
        "golden_pm_start": at(GOLDEN_HIGH_ELEVATION, False),
        "sunset": at(SUNRISE_ELEVATION, False),
        "golden_pm_end": at(BLUE_GOLDEN_BOUNDARY, False),
        "blue_pm_end": at(CIVIL_ELEVATION, False),
        "sunset_azimuth": sunset_azimuth(day),
    }


def clock(minutes: float) -> str:
    total = int(round(minutes))
    return f"{total // 60:02d}:{total % 60:02d}"


if __name__ == "__main__":
    import sys
    target = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    for key, value in day_plan(target).items():
        print(f"{key:16s} {value:.1f}°" if key == "sunset_azimuth" else f"{key:16s} {clock(value)}")
