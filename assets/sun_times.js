/* Sun times for Lima: JS twin of scripts/sun_times.py (NOAA general solar
   position equations, https://gml.noaa.gov/grad/solcalc/calcdetails.html).
   Golden hour: sun between +6° and −4°; blue hour: −4° to −6°. */
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

  function clock(minutes) {
    var total = Math.round(minutes);
    return String(Math.floor(total / 60)).padStart(2, '0') + ':' + String(total % 60).padStart(2, '0');
  }

  function compass(bearing) {
    var names = ['norte', 'nor-noreste', 'noreste', 'este-noreste', 'este', 'este-sureste', 'sureste', 'sur-sureste',
                 'sur', 'sur-suroeste', 'suroeste', 'oeste-suroeste', 'oeste', 'oeste-noroeste', 'noroeste', 'nor-noroeste'];
    return names[Math.round(bearing / 22.5) % 16];
  }

  var api = { dayPlan: dayPlan, clock: clock, compass: compass, eventMinutes: eventMinutes };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LimaSun = api;
})(typeof window !== 'undefined' ? window : this);
