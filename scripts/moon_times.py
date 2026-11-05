"""Moonrise, moonset and phase for planning a night shoot in Lima (W09).

Python twin of the moon half of assets/sun_times.js. The Moon's position is Paul Schlyter's
low-precision method ("How to compute planetary positions", stjarnhimlen.se): Keplerian
elements plus the twelve largest perturbations in longitude, five in latitude and two in
distance, good to about 2' in longitude, which moves a rise by under ten seconds. A rise or a
set is the upper limb on the horizon seen from the ground: the geocentric height crosses
0.7275 x parallax - 34' (Meeus, Astronomical Algorithms, 2nd ed., ch. 15). The lit fraction
is (1 + cos i) / 2 with the phase angle i from the Sun-Moon elongation (Meeus ch. 48).
tests/planner/test_moon_times.py holds both twins to the US Naval Observatory's tables.
"""
from __future__ import annotations

import math
from datetime import date

from sun_times import LIMA_LAT, LIMA_LON, LIMA_UTC_OFFSET_H, julian_day

EARTH_RADIUS_KM = 6378.14
AU_KM = 149_597_870.7
STEP_MIN = 10


def _norm(angle: float) -> float:
    return angle % 360


def _kepler(mean_anomaly: float, e: float) -> float:
    m = math.radians(mean_anomaly)
    big_e = m + e * math.sin(m) * (1 + e * math.cos(m))
    for _ in range(5):
        big_e -= (big_e - e * math.sin(big_e) - m) / (1 - e * math.cos(big_e))
    return big_e


def _sun(d: float) -> tuple[float, float, float]:
    """Ecliptic longitude (deg), distance (AU) and mean anomaly (deg) of the Sun."""
    w, e, m = 282.9404 + 4.70935e-5 * d, 0.016709 - 1.151e-9 * d, _norm(356.0470 + 0.9856002585 * d)
    big_e = _kepler(m, e)
    x, y = math.cos(big_e) - e, math.sqrt(1 - e * e) * math.sin(big_e)
    return _norm(math.degrees(math.atan2(y, x)) + w), math.hypot(x, y), m


def _perturbations(mm: float, ms: float, d_: float, f: float) -> tuple[float, float, float]:
    s = lambda a: math.sin(math.radians(a))  # noqa: E731
    c = lambda a: math.cos(math.radians(a))  # noqa: E731
    longitude = (-1.274 * s(mm - 2 * d_) + 0.658 * s(2 * d_) - 0.186 * s(ms) - 0.059 * s(2 * mm - 2 * d_)
                 - 0.057 * s(mm - 2 * d_ + ms) + 0.053 * s(mm + 2 * d_) + 0.046 * s(2 * d_ - ms)
                 + 0.041 * s(mm - ms) - 0.035 * s(d_) - 0.031 * s(mm + ms) - 0.015 * s(2 * f - 2 * d_)
                 + 0.011 * s(mm - 4 * d_))
    latitude = (-0.173 * s(f - 2 * d_) - 0.055 * s(mm - f - 2 * d_) - 0.046 * s(mm + f - 2 * d_)
                + 0.033 * s(f + 2 * d_) + 0.017 * s(2 * mm + f))
    distance = -0.58 * c(mm - 2 * d_) - 0.46 * c(2 * d_)
    return longitude, latitude, distance


def moon_ecliptic(jd: float) -> dict[str, float]:
    """Geocentric ecliptic longitude and latitude (deg) and distance (Earth radii) of the Moon."""
    d = jd - 2451543.5
    node, incl, perigee = _norm(125.1228 - 0.0529538083 * d), 5.1454, _norm(318.0634 + 0.1643573223 * d)
    a, e, m = 60.2666, 0.054900, _norm(115.3654 + 13.0649929509 * d)
    big_e = _kepler(m, e)
    x, y = a * (math.cos(big_e) - e), a * math.sqrt(1 - e * e) * math.sin(big_e)
    v, r = math.degrees(math.atan2(y, x)), math.hypot(x, y)
    n, i, vw = math.radians(node), math.radians(incl), math.radians(v + perigee)
    xh = r * (math.cos(n) * math.cos(vw) - math.sin(n) * math.sin(vw) * math.cos(i))
    yh = r * (math.sin(n) * math.cos(vw) + math.cos(n) * math.sin(vw) * math.cos(i))
    zh = r * math.sin(vw) * math.sin(i)
    sun_long, _sun_r, ms = _sun(d)
    mean_long = _norm(m + perigee + node)
    elongation, arg_lat = _norm(mean_long - sun_long), _norm(mean_long - node)
    d_long, d_lat, d_r = _perturbations(m, ms, elongation, arg_lat)
    return {
        "longitude": _norm(math.degrees(math.atan2(yh, xh)) + d_long),
        "latitude": math.degrees(math.atan2(zh, math.hypot(xh, yh))) + d_lat,
        "distance": r + d_r,
    }


def _equatorial(longitude: float, latitude: float, jd: float) -> tuple[float, float]:
    obliquity = math.radians(23.4393 - 3.563e-7 * (jd - 2451543.5))
    lon, lat = math.radians(longitude), math.radians(latitude)
    x = math.cos(lon) * math.cos(lat)
    y = math.sin(lon) * math.cos(lat) * math.cos(obliquity) - math.sin(lat) * math.sin(obliquity)
    z = math.sin(lon) * math.cos(lat) * math.sin(obliquity) + math.sin(lat) * math.cos(obliquity)
    return math.degrees(math.atan2(y, x)), math.degrees(math.asin(z))


def moon_horizontal(jd: float, lat: float = LIMA_LAT, lon: float = LIMA_LON) -> dict[str, float]:
    """Geocentric height and bearing (deg) of the Moon's centre, and its horizontal parallax."""
    moon = moon_ecliptic(jd)
    ra, dec = _equatorial(moon["longitude"], moon["latitude"], jd)
    sidereal = _norm(280.46061837 + 360.98564736629 * (jd - 2451545.0) + lon)
    hour, phi, delta = math.radians(sidereal - ra), math.radians(lat), math.radians(dec)
    height = math.asin(math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.cos(hour))
    east = -math.cos(delta) * math.sin(hour)
    north = math.cos(phi) * math.sin(delta) - math.sin(phi) * math.cos(delta) * math.cos(hour)
    return {"height": math.degrees(height), "azimuth": _norm(math.degrees(math.atan2(east, north))),
            "parallax": math.degrees(math.asin(1 / moon["distance"]))}


def _limb(jd: float) -> float:
    """How far (deg) the upper limb stands above the horizon, as the eye sees it."""
    place = moon_horizontal(jd)
    return place["height"] - (0.7275 * place["parallax"] - 34 / 60)


def illumination(jd: float) -> dict[str, float | bool]:
    """Lit fraction of the disc (0-1) and whether it is growing."""
    moon = moon_ecliptic(jd)
    sun_long, sun_r, _m = _sun(jd - 2451543.5)
    psi = math.acos(math.cos(math.radians(moon["latitude"])) * math.cos(math.radians(moon["longitude"] - sun_long)))
    sun_km, moon_km = sun_r * AU_KM, moon["distance"] * EARTH_RADIUS_KM
    phase_angle = math.atan2(sun_km * math.sin(psi), moon_km - sun_km * math.cos(psi))
    return {"fraction": (1 + math.cos(phase_angle)) / 2, "waxing": _norm(moon["longitude"] - sun_long) < 180}


def phase_name(fraction: float, waxing: bool) -> str:
    if fraction < 0.03:
        return "luna nueva"
    if fraction > 0.97:
        return "luna llena"
    if 0.45 <= fraction <= 0.55:
        return "cuarto creciente" if waxing else "cuarto menguante"
    if fraction < 0.45:
        return "luna creciente" if waxing else "luna menguante"
    return "gibosa creciente" if waxing else "gibosa menguante"


def _crossing(jd_a: float, jd_b: float, rising: bool) -> float:
    for _ in range(30):
        middle = (jd_a + jd_b) / 2
        if (_limb(middle) > 0) == rising:
            jd_b = middle
        else:
            jd_a = middle
    return (jd_a + jd_b) / 2


def moon_day(day: date, utc_offset_h: float = LIMA_UTC_OFFSET_H) -> dict:
    """Moonrise and moonset on a local calendar day (None when there is none), with bearings."""
    start = julian_day(day) - utc_offset_h / 24
    out: dict = {"rise": None, "set": None, "rise_azimuth": None, "set_azimuth": None}
    previous = _limb(start)
    for step in range(1, 24 * 60 // STEP_MIN + 1):
        jd = start + step * STEP_MIN / 1440
        now = _limb(jd)
        if (previous <= 0 < now) or (previous > 0 >= now):
            rising = now > 0
            moment = _crossing(jd - STEP_MIN / 1440, jd, rising)
            key = "rise" if rising else "set"
            if out[key] is None:
                out[key] = (moment - start) * 1440
                out[f"{key}_azimuth"] = moon_horizontal(moment)["azimuth"]
        previous = now
    return out


def moon_at(day: date, minutes_local: float, utc_offset_h: float = LIMA_UTC_OFFSET_H) -> dict:
    """Height of the upper limb (deg), bearing and lit fraction at a local minute."""
    jd = julian_day(day) + (minutes_local - utc_offset_h * 60) / 1440
    lit = illumination(jd)
    return {"height": _limb(jd), "azimuth": moon_horizontal(jd)["azimuth"], **lit,
            "phase": phase_name(lit["fraction"], lit["waxing"])}


if __name__ == "__main__":
    import sys

    from sun_times import clock
    target = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    info = moon_day(target)
    lit = moon_at(target, 0)
    print({k: (clock(v) if k in ("rise", "set") and v is not None else v) for k, v in info.items()}, lit)
