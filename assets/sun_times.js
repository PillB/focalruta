/* Sun times for Lima: JS twin of scripts/sun_times.py (NOAA general solar
   position equations, https://gml.noaa.gov/grad/solcalc/calcdetails.html).
   Golden hour: sun between +6° and −4°; blue hour: −4° to −6°.
   The moon (moonDay, moonAt) is the twin of scripts/moon_times.py: Schlyter's
   low-precision Moon, held to the US Naval Observatory's tables. */
(function (root) {
  'use strict';
  var LAT = -12.097, LON = -77.036, UTC_OFFSET_H = -5;
  var SUNRISE = -0.833, CIVIL = -6, GOLDEN_HIGH = 6, BLUE_GOLDEN = -4;
  var rad = Math.PI / 180, deg = 180 / Math.PI;

  function julianDay(iso) {
    var p = iso.split('-').map(Number), y = p[0], m = p[1], d = p[2];
    if (m <= 2) { y -= 1; m += 12; }
    var a = Math.floor(y / 100), b = 2 - a + Math.floor(a / 4);
    return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + b - 1524.5;
  }

  function declinationAndEot(jd) {
    var t = (jd - 2451545) / 36525;
    var l0 = ((280.46646 + t * (36000.76983 + t * 0.0003032)) % 360 + 360) % 360;
    var m = (357.52911 + t * (35999.05029 - 0.0001537 * t)) * rad;
    var e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t);
    var c = Math.sin(m) * (1.914602 - t * (0.004817 + 0.000014 * t)) +
            Math.sin(2 * m) * (0.019993 - 0.000101 * t) + Math.sin(3 * m) * 0.000289;
    var omega = (125.04 - 1934.136 * t) * rad;
    var lambda = (l0 + c - 0.00569 - 0.00478 * Math.sin(omega)) * rad;
    var meanObliq = 23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60) / 60;
    var obliq = (meanObliq + 0.00256 * Math.cos(omega)) * rad;
    var dec = Math.asin(Math.sin(obliq) * Math.sin(lambda)) * deg;
    var y = Math.pow(Math.tan(obliq / 2), 2), l0r = l0 * rad;
    var eot = 4 * deg * (y * Math.sin(2 * l0r) - 2 * e * Math.sin(m) + 4 * e * y * Math.sin(m) * Math.cos(2 * l0r) -
                         0.5 * y * y * Math.sin(4 * l0r) - 1.25 * e * e * Math.sin(2 * m));
    return [dec, eot];
  }

  function eventMinutes(iso, elevation, rising, offsetH) {
    var jd0 = julianDay(iso), minutesUtc = 720 - 4 * LON;
    for (var i = 0; i < 3; i++) {
      var de = declinationAndEot(jd0 + minutesUtc / 1440);
      var phi = LAT * rad, delta = de[0] * rad;
      var cosH = (Math.sin(elevation * rad) - Math.sin(phi) * Math.sin(delta)) / (Math.cos(phi) * Math.cos(delta));
      if (cosH < -1 || cosH > 1) return null;
      var hourAngle = Math.acos(cosH) * deg, noonUtc = 720 - 4 * LON - de[1];
      minutesUtc = rising ? noonUtc - 4 * hourAngle : noonUtc + 4 * hourAngle;
    }
    return minutesUtc + (offsetH === undefined ? UTC_OFFSET_H : offsetH) * 60;
  }

  function sunsetAzimuth(iso) {
    var minutesUtc = eventMinutes(iso, SUNRISE, false, 0);
    var de = declinationAndEot(julianDay(iso) + minutesUtc / 1440);
    var phi = LAT * rad, delta = de[0] * rad, h = SUNRISE * rad;
    var cosAz = (Math.sin(delta) - Math.sin(phi) * Math.sin(h)) / (Math.cos(phi) * Math.cos(h));
    return 360 - Math.acos(Math.max(-1, Math.min(1, cosAz))) * deg;
  }

  function dayPlan(iso) {
    return {
      blue_am_start: eventMinutes(iso, CIVIL, true),
      golden_am_start: eventMinutes(iso, BLUE_GOLDEN, true),
      sunrise: eventMinutes(iso, SUNRISE, true),
      golden_am_end: eventMinutes(iso, GOLDEN_HIGH, true),
      golden_pm_start: eventMinutes(iso, GOLDEN_HIGH, false),
      sunset: eventMinutes(iso, SUNRISE, false),
      golden_pm_end: eventMinutes(iso, BLUE_GOLDEN, false),
      blue_pm_end: eventMinutes(iso, CIVIL, false),
      sunset_azimuth: sunsetAzimuth(iso)
    };
  }

  // Saemundsson's refraction (Meeus eq. 16.4), as in scripts/sun_times.py.
  function refraction(elevation) {
    if (elevation < -1) return 0;
    return 1.02 / Math.tan((elevation + 10.3 / (elevation + 5.11)) * rad) / 60;
  }

  // Where the sun stands at a local minute: bearing from north, geometric and apparent height.
  function position(iso, minutesLocal) {
    var minutesUtc = minutesLocal - UTC_OFFSET_H * 60;
    var de = declinationAndEot(julianDay(iso) + minutesUtc / 1440);
    var ha = ((((minutesUtc + de[1] + 4 * LON) / 4 - 180 + 540) % 360 + 360) % 360 - 180) * rad;
    var phi = LAT * rad, delta = de[0] * rad;
    var cosZ = Math.sin(phi) * Math.sin(delta) + Math.cos(phi) * Math.cos(delta) * Math.cos(ha);
    var elevation = 90 - Math.acos(Math.max(-1, Math.min(1, cosZ))) * deg;
    var east = -Math.cos(delta) * Math.sin(ha);
    var north = Math.cos(phi) * Math.sin(delta) - Math.sin(phi) * Math.cos(delta) * Math.cos(ha);
    var azimuth = ((Math.atan2(east, north) * deg) % 360 + 360) % 360;
    return { azimuth: azimuth, elevation: elevation, apparent: elevation + refraction(elevation) };
  }

  // Length and bearing of the shadow an upright `height` casts on level ground; null at night.
  function shadow(height, pos) {
    if (pos.apparent <= 0) return null;
    return [height / Math.tan(pos.apparent * rad), (pos.azimuth + 180) % 360];
  }

  // Degrees between the sun's rays and a wall facing `facing`: 90 head-on, 0 grazing, < 0 behind.
  function wallAngle(pos, facing) {
    var v = Math.cos(pos.apparent * rad) * Math.cos((pos.azimuth - facing) * rad);
    return Math.asin(Math.max(-1, Math.min(1, v))) * deg;
  }

  // Raking light grazes a surface at 5-20 deg; from 60 deg it is nearly head-on.
  var RAKING_MAX = 20, FRONTAL_MIN = 60;

  function runs(flags, first) {
    var out = [], start = null;
    for (var i = 0; i <= flags.length; i++) {
      var on = i < flags.length && flags[i];
      if (on && start === null) start = i;
      else if (!on && start !== null) { out.push([first + start, first + i - 1]); start = null; }
    }
    return out;
  }

  // Local minutes, sunrise to sunset, when a wall facing `facing` has direct, raking and head-on sun.
  function wallLight(iso, facing) {
    var p = dayPlan(iso), first = Math.ceil(p.sunrise), last = Math.floor(p.sunset), angles = [];
    for (var m = first; m <= last; m++) {
      var pos = position(iso, m);
      angles.push(pos.apparent > 0 ? wallAngle(pos, facing) : -1);
    }
    return {
      direct: runs(angles.map(function (a) { return a > 0; }), first),
      raking: runs(angles.map(function (a) { return a > 0 && a <= RAKING_MAX; }), first),
      frontal: runs(angles.map(function (a) { return a >= FRONTAL_MIN; }), first)
    };
  }

  function clock(minutes) {
    var total = Math.round(minutes);
    return String(Math.floor(total / 60)).padStart(2, '0') + ':' + String(total % 60).padStart(2, '0');
  }

  function compass(bearing) {
    var names = ['norte', 'nor-noreste', 'noreste', 'este-noreste', 'este', 'este-sureste', 'sureste', 'sur-sureste',
                 'sur', 'sur-suroeste', 'suroeste', 'oeste-suroeste', 'oeste', 'oeste-noroeste', 'noroeste', 'nor-noroeste'];
    return names[Math.round(bearing / 22.5) % 16];
  }

  // Today's date in Lima for an instant in ms. Peru has kept UTC-5 all year
  // since 1994, so a fixed shift read with UTC getters is exact; the reader's
  // own zone, and its daylight-saving changes, never enter the arithmetic.
  function limaToday(ms) {
    var lima = new Date(ms - 5 * 3600000);
    return lima.getUTCFullYear() + '-' + String(lima.getUTCMonth() + 1).padStart(2, '0') + '-' +
      String(lima.getUTCDate()).padStart(2, '0');
  }

  // ---- Moon (W09): twin of scripts/moon_times.py, same constants and steps. ----
  function norm(a) { return ((a % 360) + 360) % 360; }

  function kepler(meanAnomaly, e) {
    var m = meanAnomaly * rad, E = m + e * Math.sin(m) * (1 + e * Math.cos(m));
    for (var i = 0; i < 5; i++) E -= (E - e * Math.sin(E) - m) / (1 - e * Math.cos(E));
    return E;
  }

  function sunEcliptic(d) {
    var w = 282.9404 + 4.70935e-5 * d, e = 0.016709 - 1.151e-9 * d, m = norm(356.0470 + 0.9856002585 * d);
    var E = kepler(m, e), x = Math.cos(E) - e, y = Math.sqrt(1 - e * e) * Math.sin(E);
    return { longitude: norm(Math.atan2(y, x) * deg + w), distance: Math.sqrt(x * x + y * y), anomaly: m };
  }

  function moonEcliptic(jd) {
    var d = jd - 2451543.5, s = function (a) { return Math.sin(a * rad); }, c = function (a) { return Math.cos(a * rad); };
    var node = norm(125.1228 - 0.0529538083 * d), incl = 5.1454 * rad, perigee = norm(318.0634 + 0.1643573223 * d);
    var a = 60.2666, e = 0.0549, m = norm(115.3654 + 13.0649929509 * d);
    var E = kepler(m, e), x = a * (Math.cos(E) - e), y = a * Math.sqrt(1 - e * e) * Math.sin(E);
    var v = Math.atan2(y, x) * deg, r = Math.sqrt(x * x + y * y), n = node * rad, vw = (v + perigee) * rad;
    var xh = r * (Math.cos(n) * Math.cos(vw) - Math.sin(n) * Math.sin(vw) * Math.cos(incl));
    var yh = r * (Math.sin(n) * Math.cos(vw) + Math.cos(n) * Math.sin(vw) * Math.cos(incl));
    var zh = r * Math.sin(vw) * Math.sin(incl);
    var sun = sunEcliptic(d), ms = sun.anomaly, mean = norm(m + perigee + node);
    var D = norm(mean - sun.longitude), F = norm(mean - node), mm = m;
    var dLon = -1.274 * s(mm - 2 * D) + 0.658 * s(2 * D) - 0.186 * s(ms) - 0.059 * s(2 * mm - 2 * D) -
      0.057 * s(mm - 2 * D + ms) + 0.053 * s(mm + 2 * D) + 0.046 * s(2 * D - ms) + 0.041 * s(mm - ms) -
      0.035 * s(D) - 0.031 * s(mm + ms) - 0.015 * s(2 * F - 2 * D) + 0.011 * s(mm - 4 * D);
    var dLat = -0.173 * s(F - 2 * D) - 0.055 * s(mm - F - 2 * D) - 0.046 * s(mm + F - 2 * D) +
      0.033 * s(F + 2 * D) + 0.017 * s(2 * mm + F);
    var dR = -0.58 * c(mm - 2 * D) - 0.46 * c(2 * D);
    return { longitude: norm(Math.atan2(yh, xh) * deg + dLon), latitude: Math.atan2(zh, Math.sqrt(xh * xh + yh * yh)) * deg + dLat,
             distance: r + dR, sun: sun };
  }

  function moonHorizontal(jd) {
    var moon = moonEcliptic(jd), ob = (23.4393 - 3.563e-7 * (jd - 2451543.5)) * rad;
    var lon = moon.longitude * rad, lat = moon.latitude * rad;
    var x = Math.cos(lon) * Math.cos(lat);
    var y = Math.sin(lon) * Math.cos(lat) * Math.cos(ob) - Math.sin(lat) * Math.sin(ob);
    var z = Math.sin(lon) * Math.cos(lat) * Math.sin(ob) + Math.sin(lat) * Math.cos(ob);
    var ra = Math.atan2(y, x) * deg, dec = Math.asin(z);
    var sidereal = norm(280.46061837 + 360.98564736629 * (jd - 2451545) + LON);
    var H = (sidereal - ra) * rad, phi = LAT * rad;
    var height = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H)) * deg;
    var east = -Math.cos(dec) * Math.sin(H), north = Math.cos(phi) * Math.sin(dec) - Math.sin(phi) * Math.cos(dec) * Math.cos(H);
    return { height: height, azimuth: norm(Math.atan2(east, north) * deg), parallax: Math.asin(1 / moon.distance) * deg, moon: moon };
  }

  // Upper limb above the horizon as the eye sees it: height - (0.7275 x parallax - 34').
  function limb(jd) { var p = moonHorizontal(jd); return p.height - (0.7275 * p.parallax - 34 / 60); }

  function illumination(jd) {
    var moon = moonEcliptic(jd), sun = moon.sun;
    var psi = Math.acos(Math.cos(moon.latitude * rad) * Math.cos((moon.longitude - sun.longitude) * rad));
    var sunKm = sun.distance * 149597870.7, moonKm = moon.distance * 6378.14;
    var i = Math.atan2(sunKm * Math.sin(psi), moonKm - sunKm * Math.cos(psi));
    return { fraction: (1 + Math.cos(i)) / 2, waxing: norm(moon.longitude - sun.longitude) < 180 };
  }

  function phaseName(fraction, waxing) {
    if (fraction < 0.03) return 'luna nueva';
    if (fraction > 0.97) return 'luna llena';
    if (fraction >= 0.45 && fraction <= 0.55) return waxing ? 'cuarto creciente' : 'cuarto menguante';
    if (fraction < 0.45) return waxing ? 'luna creciente' : 'luna menguante';
    return waxing ? 'gibosa creciente' : 'gibosa menguante';
  }

  function crossing(a, b, rising) {
    for (var i = 0; i < 30; i++) { var mid = (a + b) / 2; if ((limb(mid) > 0) === rising) b = mid; else a = mid; }
    return (a + b) / 2;
  }

  // Moonrise and moonset on a Lima calendar day, in local minutes (null when there is none).
  function moonDay(iso) {
    var start = julianDay(iso) - UTC_OFFSET_H / 24, step = 10 / 1440, out = { rise: null, set: null, rise_azimuth: null, set_azimuth: null };
    var previous = limb(start);
    for (var k = 1; k <= 144; k++) {
      var jd = start + k * step, now = limb(jd);
      if ((previous <= 0 && now > 0) || (previous > 0 && now <= 0)) {
        var rising = now > 0, key = rising ? 'rise' : 'set';
        if (out[key] === null) {
          var moment = crossing(jd - step, jd, rising);
          out[key] = (moment - start) * 1440;
          out[key + '_azimuth'] = moonHorizontal(moment).azimuth;
        }
      }
      previous = now;
    }
    return out;
  }

  // Upper-limb height, bearing and lit fraction at a local minute of a Lima day.
  function moonAt(iso, minutesLocal) {
    var jd = julianDay(iso) + (minutesLocal - UTC_OFFSET_H * 60) / 1440, lit = illumination(jd);
    return { height: limb(jd), azimuth: moonHorizontal(jd).azimuth, fraction: lit.fraction, waxing: lit.waxing,
             phase: phaseName(lit.fraction, lit.waxing) };
  }

  var api = { dayPlan: dayPlan, clock: clock, compass: compass, eventMinutes: eventMinutes, limaToday: limaToday,
              position: position, shadow: shadow, wallAngle: wallAngle, wallLight: wallLight,
              moonDay: moonDay, moonAt: moonAt, RAKING_MAX: RAKING_MAX, FRONTAL_MIN: FRONTAL_MIN };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LimaSun = api;
})(typeof window !== 'undefined' ? window : this);
