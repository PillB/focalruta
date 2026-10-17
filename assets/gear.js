/* Your gear (requirements V13 to V15). The plans are solved for a Canon EOS 6D
   and its four lenses. A reader with another camera or other lenses gets, next
   to each planned setting, the equivalent for their gear:
   - the same framing: the focal that gives the plan's field of view on their
     sensor, or their nearest lens and the distance that keeps the subject the
     same size;
   - the same depth of field in proportion to the subject distance: the
     hyperfocal distance scales with the camera distance, with the circle of
     confusion scaled to the sensor;
   - the same exposure, keeping the variable that makes the effect: the shutter
     for motion techniques, the aperture for depth-of-field techniques.
   Pure helpers are exported for tests/test_gear.py; the rest needs a page. */
(function (root) {
  'use strict';
  var REF_W = 35.8, REF_COC = 0.03, BASE_ISO = 100, FASTEST = 1 / 4000, NARROWEST = 22, KEY = 'focalruta-equipo-v1';
  var APERTURES = [1, 1.1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.5, 2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1, 8, 9, 10, 11, 13, 14, 16, 18, 20, 22];
  var ISOS = [100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000, 20000, 25600, 32000, 40000, 51200];
  var SHUTTERS = [1 / 4000, 1 / 3200, 1 / 2500, 1 / 2000, 1 / 1600, 1 / 1250, 1 / 1000, 1 / 800, 1 / 640, 1 / 500, 1 / 400, 1 / 320, 1 / 250, 1 / 200, 1 / 160, 1 / 125,
    1 / 100, 1 / 80, 1 / 60, 1 / 50, 1 / 40, 1 / 30, 1 / 25, 1 / 20, 1 / 15, 1 / 13, 1 / 10, 1 / 8, 1 / 6, 1 / 5, 1 / 4, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.3, 1.6, 2, 2.5,
    3.2, 4, 5, 6, 8, 10, 13, 15, 20, 25, 30];
  // Techniques whose effect is the depth of field keep their aperture; the rest keep their shutter.
  var APERTURE_LED = ['mucha_pdc', 'poca_pdc'];
  var BODIES = [
    { id: 'canon_6d', name: 'Canon EOS 6D (la de los planes)', w: 35.8, iso: 25600, sensor: 'Sensor de 35,8 × 23,9 mm.' },
    { id: 'full_frame', name: 'Otra de formato completo', w: 36, iso: 25600, sensor: 'Sensor de 36 × 24 mm: casi igual que la 6D.' },
    { id: 'apsc_canon', name: 'APS-C de Canon (factor 1,6)', w: 22.3, iso: 12800, sensor: 'Sensor de 22,3 × 14,9 mm (EOS 2000D a R7).' },
    { id: 'apsc', name: 'APS-C de otras marcas (factor 1,5)', w: 23.5, iso: 12800, sensor: 'Sensor de 23,5 × 15,6 mm (Nikon DX, Sony APS-C, Fujifilm X).' },
    { id: 'm43', name: 'Micro Cuatro Tercios (factor 2)', w: 17.3, iso: 6400, sensor: 'Sensor de 17,3 × 13 mm (OM System, Panasonic Lumix G).' },
    { id: 'one_inch', name: 'Sensor de 1 pulgada (factor 2,7)', w: 13.2, iso: 6400, sensor: 'Sensor de 13,2 × 8,8 mm (compactas avanzadas).' }
  ];
  var KIT = [
    { name: 'EF 35mm f/2 IS USM', min: 35, max: 35, wide: 2, tele: 2, filter: 67 },
    { name: 'EF 50mm f/1.8 STM', min: 50, max: 50, wide: 1.8, tele: 1.8, filter: 49 },
    { name: 'EF 85mm f/1.8 USM', min: 85, max: 85, wide: 1.8, tele: 1.8, filter: 58 },
    { name: 'EF 35–80mm f/4–5.6 III', min: 35, max: 80, wide: 4, tele: 5.6, filter: 52 }
  ];
  // Common lenses a reader can add with one tap; filter threads vary by model, so they are left out.
  var COMMON = [
    { name: 'Zoom de kit 18–55 mm f/3.5–5.6', min: 18, max: 55, wide: 3.5, tele: 5.6 },
    { name: 'Zoom de kit 16–50 mm f/3.5–5.6', min: 16, max: 50, wide: 3.5, tele: 5.6 },
    { name: 'Zoom de kit 14–42 mm f/3.5–5.6', min: 14, max: 42, wide: 3.5, tele: 5.6 },
    { name: 'Zoom 24–70 mm f/2.8', min: 24, max: 70, wide: 2.8, tele: 2.8 },
    { name: 'Zoom 24–105 mm f/4', min: 24, max: 105, wide: 4, tele: 4 },
    { name: 'Zoom 70–200 mm f/4', min: 70, max: 200, wide: 4, tele: 4 },
    { name: '23 mm f/2', min: 23, max: 23, wide: 2, tele: 2 },
    { name: '35 mm f/1.8', min: 35, max: 35, wide: 1.8, tele: 1.8 },
    { name: '50 mm f/1.8', min: 50, max: 50, wide: 1.8, tele: 1.8 },
    { name: '85 mm f/1.8', min: 85, max: 85, wide: 1.8, tele: 1.8 }
  ];

  function reference() { return { body: 'canon_6d', iso: 25600, lenses: KIT.map(function (l) { return Object.assign({}, l); }) }; }
  function bodyOf(gear) { return BODIES.filter(function (b) { return b.id === gear.body; })[0] || BODIES[0]; }
  function isReference(gear) { return JSON.stringify(gear) === JSON.stringify(reference()); }

  function nearest(list, value) {
    return list.reduce(function (best, x) { return Math.abs(Math.log(x / value)) < Math.abs(Math.log(best / value)) ? x : best; }, list[0]);
  }
  function fNumber(text) { return parseFloat(String(text).replace('f/', '')); }
  function seconds(text) {
    var s = String(text).replace('Bulb', '').trim(), canon = /^(\d+)"(\d)?$/.exec(s);
    if (canon) return +canon[1] + (canon[2] ? +canon[2] / 10 : 0);
    if (s.indexOf('/') > 0) return +s.split('/')[0] / +s.split('/')[1];
    return parseFloat(s);
  }
  function shutterText(t) {
    if (t > 30) return 'Bulb ' + Math.round(t) + '"';
    var x = nearest(SHUTTERS, t);
    if (x < 0.3) return '1/' + Math.round(1 / x);
    var whole = Math.floor(x + 1e-9), tenth = Math.round((x - whole) * 10);
    return whole + '"' + (tenth ? tenth : '');
  }
  function decimal(x) { return (Math.round(x * 10) / 10).toFixed(1).replace('.', ','); }

  // A zoom's widest aperture narrows from the wide end to the tele end.
  function widestAt(lens, focal) {
    if (lens.max === lens.min) return lens.wide;
    var share = (focal - lens.min) / (lens.max - lens.min);
    return lens.wide + Math.max(0, Math.min(1, share)) * (lens.tele - lens.wide);
  }

  // '35mm' -> {focal: 35}; '35-80mm @50' -> {focal: 50}; '35-80mm' (zooming during the exposure) -> {from: 35, to: 80}.
  function planLens(text) {
    var m = /^(\d+)(?:-(\d+))?mm(?:\s*@\s*(\d+))?/.exec(String(text).replace('–', '-'));
    if (!m) return null;
    if (m[2] && !m[3]) return { from: +m[1], to: +m[2] };
    return { focal: +(m[3] || m[1]) };
  }

  // The lens that comes closest to the plan: framing missed (the reader has to
  // move) plus depth of field lost to a lens that cannot open far enough.
  function chooseLens(lenses, wanted, plan, coc) {
    var best = null;
    lenses.forEach(function (lens) {
      var focal = Math.max(lens.min, Math.min(lens.max, wanted)), miss = Math.abs(Math.log(focal / wanted));
      var distance = plan.distance * focal / wanted, widest = widestAt(lens, focal);
      var lost = Math.max(0, 2 * Math.log2(widest / apertureFor(plan, focal, distance, coc)));
      var score = (miss < 0.03 ? 0 : miss) + lost / 2 + widest / 1000;
      if (!best || score < best.score) best = { lens: lens, focal: focal, distance: distance, score: score };
    });
    return best;
  }

  function chooseZoom(lenses, from, to) {
    var best = null;
    lenses.filter(function (l) { return l.max / l.min >= 1.5; }).forEach(function (lens) {
      var a = Math.max(lens.min, from), b = Math.min(lens.max, to), span = b > a ? Math.log(b / a) : 0;
      if (!best || span > best.span) best = { lens: lens, from: a, to: b, span: span };
    });
    return best;
  }

  // Same hyperfocal in proportion to the subject distance: the sharp zone
  // scales with the camera distance (thin lens, f much shorter than d).
  function apertureFor(plan, focal, distanceM, coc) {
    var target = plan.hyperfocal * distanceM / plan.distance;
    return target > focal ? focal * focal / (coc * (target - focal)) : NARROWEST;
  }

  function snapAperture(n, widest, planFarIsInfinite, focal, distance, coc) {
    var allowed = APERTURES.filter(function (x) { return x >= widest - 0.05; });
    var snapped = nearest(allowed, Math.max(n, widest));
    // A plan sharp to infinity stays sharp to infinity: round toward more depth.
    if (planFarIsInfinite && focal * focal / (snapped * coc) + focal > distance * 1000 - focal && snapped < NARROWEST) {
      snapped = allowed[Math.min(allowed.length - 1, allowed.indexOf(snapped) + 1)];
    }
    return snapped;
  }

  // ISO that keeps log2(N²/t) − log2(ISO/100) + ND equal to the plan's.
  function isoNeeded(r, plan) { return plan.iso * Math.pow(r.n / plan.n, 2) * plan.t / r.t * Math.pow(2, r.nd - plan.nd); }

  function tooMuchLight(r, plan) {
    var extra = Math.log2(BASE_ISO / isoNeeded(r, plan));
    if (r.apertureLed) {
      r.t = r.t / Math.pow(2, extra);
      if (r.t < FASTEST) { var nd = Math.ceil(Math.log2(FASTEST / r.t) - 1e-9); r.nd += nd; r.t *= Math.pow(2, nd); }
      r.t = nearest(SHUTTERS, r.t);
      return;
    }
    var target = Math.min(16, r.n * Math.pow(2, extra / 2)), n = APERTURES.filter(function (x) { return x >= r.n && x <= target * 1.03; }).pop();
    if (n > r.n) { r.n = n; r.stoppedDown = true; }
    var left = Math.log2(BASE_ISO / isoNeeded(r, plan));
    if (left > 1 / 6) r.nd += Math.ceil(left - 1e-9);
  }

  function tooLittleLight(r, plan, body) {
    var short = Math.log2(isoNeeded(r, plan) / body.iso);
    if (r.nd > 0) { r.nd -= Math.min(r.nd, Math.ceil(short - 1e-9)); short = Math.log2(isoNeeded(r, plan) / body.iso); }
    if (short <= 0) return;
    if (r.apertureLed) { r.t = r.t * Math.pow(2, short); r.slower = true; r.t = r.t > 30 ? Math.round(r.t) : nearest(SHUTTERS, r.t); return; }
    var open = APERTURES.filter(function (x) { return x >= r.widest - 0.05 && x >= r.n / Math.pow(2, short / 2) * 0.97; })[0];
    if (open < r.n) { r.n = open; r.opened = true; }
  }

  function lightBalance(r, plan, body) {
    if (isoNeeded(r, plan) < BASE_ISO / Math.pow(2, 1 / 6)) tooMuchLight(r, plan);
    else if (isoNeeded(r, plan) > body.iso * Math.pow(2, 1 / 6)) tooLittleLight(r, plan, body);
    var iso = isoNeeded(r, plan), allowed = ISOS.filter(function (x) { return x <= body.iso; });
    r.iso = nearest(allowed, Math.max(BASE_ISO, Math.min(body.iso, iso)));
    var short = Math.log2(iso / body.iso);
    if (short > 1 / 6) r.shortStops = short;
    return r;
  }

  function notesFor(r, plan) {
    var notes = [];
    if (r.distance && Math.abs(r.distance / plan.distance - 1) > 0.05) {
      notes.push(r.distance > plan.distance ? 'Retrocede a ' + decimal(r.distance) + ' m (el plan está a ' + decimal(plan.distance) + ' m) para el mismo encuadre.'
        : 'Acércate a ' + decimal(r.distance) + ' m (el plan está a ' + decimal(plan.distance) + ' m), o quédate y recorta.');
    }
    if (r.apertureLimited) notes.push('Tu lente no abre tanto: habrá más zona nítida y menos desenfoque de fondo que en el plan.');
    if (r.stoppedDown) notes.push('Cierro el diafragma para no pasarte de luz: algo más de zona nítida.');
    if (r.opened) notes.push('Abro el diafragma por falta de luz: algo menos de zona nítida.');
    if (r.slower) notes.push('Exposición más larga por falta de luz: usa trípode.');
    if (r.nd !== plan.nd) notes.push(r.nd ? 'Filtro ND de ' + r.nd + ' pasos.' : 'Sin filtro ND.');
    if (r.shortStops) notes.push('Faltan ' + decimal(r.shortStops) + ' pasos de luz con ISO ' + r.iso + ': sube el ISO o acepta una foto más oscura.');
    return notes;
  }

  /* The plan's setting for one light slot, adapted to `gear`.
     setting: {technique, lens, aperture, shutter, iso, nd_stops, distance}. */
  function adapt(setting, gear) {
    var body = bodyOf(gear), k = body.w / REF_W, coc = REF_COC * k, lens = planLens(setting.lens);
    var limits = { iso: +gear.iso || body.iso };
    if (!lens || !gear.lenses.length) return { ok: false, reason: 'Añade al menos un lente a tu equipo.' };
    var plan = { n: fNumber(setting.aperture), t: seconds(setting.shutter), iso: +setting.iso, nd: +(setting.nd_stops || 0), distance: +setting.distance };
    var r = { ok: true, nd: plan.nd, t: plan.t, apertureLed: APERTURE_LED.indexOf(setting.technique) >= 0 };
    plan.focal = lens.from ? lens.to : lens.focal;
    plan.hyperfocal = plan.focal * plan.focal / (plan.n * REF_COC) + plan.focal;
    var focal;
    if (lens.from) {
      var zoom = chooseZoom(gear.lenses, lens.from * k, lens.to * k);
      if (!zoom) return { ok: false, reason: 'El efecto zoom necesita un objetivo zoom: añade uno a tu equipo.' };
      focal = zoom.to; r.lensName = zoom.lens.name; r.lensText = Math.round(zoom.from) + '–' + Math.round(zoom.to) + ' mm, girando el anillo durante la exposición';
      r.widest = widestAt(zoom.lens, focal); r.distance = plan.distance;
    } else {
      var pick = chooseLens(gear.lenses, lens.focal * k, plan, coc);
      focal = pick.focal; r.lensName = pick.lens.name; r.distance = pick.distance; r.widest = widestAt(pick.lens, focal);
      r.lensText = Math.round(focal) + ' mm' + (pick.lens.max > pick.lens.min ? ' (zoom ' + pick.lens.min + '–' + pick.lens.max + ')' : '');
    }
    var planInfinite = plan.distance * 1000 - plan.focal >= plan.hyperfocal;
    var ideal = apertureFor(plan, focal, r.distance, coc);
    r.apertureLimited = ideal < r.widest - 0.05;
    r.n = snapAperture(Math.min(ideal, NARROWEST), r.widest, planInfinite, focal, r.distance, coc);
    lightBalance(r, plan, limits);
    return {
      ok: true, focal: focal, lens: r.lensText, lens_name: r.lensName, distance_m: r.distance, f_number: r.n, aperture: 'f/' + r.n,
      seconds: r.t, shutter: shutterText(r.t), iso: r.iso, nd_stops: r.nd, coc_mm: coc,
      flags: { apertureLimited: r.apertureLimited, stoppedDown: !!r.stoppedDown, opened: !!r.opened, slower: !!r.slower, short: r.shortStops || 0 },
      notes: notesFor(r, plan)
    };
  }

  function lineHtml(setting, gear) {
    if (!gear || isReference(gear) || setting.viable === false) return '';
    var r = adapt(setting, gear);
    if (!r.ok) return '<div class="gear-line gear-line-no"><strong>Con tu equipo:</strong> ' + r.reason + '</div>';
    return '<div class="gear-line"><strong>Con tu equipo:</strong> <span class="gear-values">' + r.lens + ' · ' + r.aperture + ' · ' + r.shutter + ' · ISO ' + r.iso +
      (r.nd_stops ? ' · ND ' + r.nd_stops + ' pasos' : '') + '</span>' + (r.notes.length ? ' <span class="gear-notes">' + r.notes.join(' ') + '</span>' : '') + '</div>';
  }

  // The circle of confusion for the reader's sensor: the 6D's 0.03 mm scaled by the width ratio.
  function cocOf(gear) { return REF_COC * bodyOf(gear).w / REF_W; }

  var api = { REF_W: REF_W, REF_COC: REF_COC, cocOf: cocOf, BODIES: BODIES, KIT: KIT, COMMON: COMMON, reference: reference, isReference: isReference, planLens: planLens,
              widestAt: widestAt, seconds: seconds, shutterText: shutterText, adapt: adapt, lineHtml: lineHtml, bodyOf: bodyOf };

  // A stored lens is the reader's own data but still goes into the page as
  // HTML: keep the numbers and a name without markup, or drop it.
  function cleanLens(l) {
    if (!l || typeof l !== 'object') return null;
    var n = { name: String(l.name || '').replace(/[<>&"]/g, ''), min: +l.min, max: +l.max, wide: +l.wide, tele: +l.tele };
    if ('filter' in l) n.filter = +l.filter;
    return n.min >= 4 && n.max >= n.min && n.max <= 1200 && n.wide >= 0.95 && n.tele >= n.wide && n.tele <= 32 ? n : null;
  }
  function load() {
    try {
      var g = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (g && BODIES.some(function (b) { return b.id === g.body; }) && Array.isArray(g.lenses) && +g.iso > 0) {
        return { body: g.body, iso: +g.iso, lenses: g.lenses.map(cleanLens).filter(Boolean) };
      }
    } catch (e) {}
    return reference();
  }
  function save(gear) { try { if (isReference(gear)) localStorage.removeItem(KEY); else localStorage.setItem(KEY, JSON.stringify(gear)); } catch (e) {} }
  api.load = load;
  api.save = save;
  // The adapted line for a shot in the light slot the page shows.
  api.lineFor = function (shot, setting) {
    return lineHtml(Object.assign({ technique: shot.technique, distance: shot.subject_distance_m }, setting), load());
  };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }
  root.FocalRutaEquipo = api;

  // The gear picker on the home page (#gear-config). Without JavaScript it stays
  // hidden and the page describes the Canon 6D kit the plans are solved for.
  var panel = document.getElementById('gear-config');
  if (!panel) return;
  var $ = function (id) { return document.getElementById(id); };
  var gear = load();
  function lensName(l) {
    var focal = l.max > l.min ? l.min + '–' + l.max + ' mm' : l.min + ' mm';
    return l.name || focal + ' f/' + l.wide + (l.tele !== l.wide ? '–' + l.tele : '');
  }
  function changed() {
    save(gear); paint();
    document.dispatchEvent(new CustomEvent('focalruta:equipo', { detail: gear }));
  }
  function paint() {
    var body = bodyOf(gear);
    $('gear-body').value = body.id;
    $('gear-body-hint').textContent = body.sensor;
    $('gear-iso').value = String(gear.iso);
    $('gear-lens-list').innerHTML = gear.lenses.map(function (l, i) {
      return '<li><span>' + lensName(l) + '</span><button type="button" class="sota-btn" data-remove="' + i + '" aria-label="Quitar ' + lensName(l) + '">Quitar</button></li>';
    }).join('') || '<li class="gear-empty">Sin lentes: añade al menos uno.</li>';
    $('gear-status').textContent = isReference(gear) ? 'Usas el equipo de los planes: cada toma muestra sus ajustes tal cual.'
      : 'Planes adaptados a ' + body.name.split(' (')[0] + ' con ' + gear.lenses.length + (gear.lenses.length === 1 ? ' lente' : ' lentes') + ': cada toma muestra también «Con tu equipo».';
  }
  $('gear-body').innerHTML = BODIES.map(function (b) { return '<option value="' + b.id + '">' + b.name + '</option>'; }).join('');
  $('gear-iso').innerHTML = [1600, 3200, 6400, 12800, 25600, 51200].map(function (x) { return '<option value="' + x + '">ISO ' + x + '</option>'; }).join('');
  $('gear-common').innerHTML = '<option value="">Elige un lente…</option>' + COMMON.map(function (l, i) { return '<option value="' + i + '">' + l.name + '</option>'; }).join('');
  $('gear-body').addEventListener('change', function () {
    gear.body = this.value;
    gear.iso = bodyOf(gear).iso;
    changed();
  });
  $('gear-iso').addEventListener('change', function () { gear.iso = +this.value; changed(); });
  $('gear-common').addEventListener('change', function () {
    if (this.value === '') return;
    gear.lenses.push(Object.assign({}, COMMON[+this.value])); this.value = ''; changed();
  });
  $('gear-lens-list').addEventListener('click', function (e) {
    var b = e.target.closest('[data-remove]');
    if (b) { gear.lenses.splice(+b.getAttribute('data-remove'), 1); changed(); }
  });
  $('gear-add').addEventListener('click', function () {
    var min = +$('gear-min').value, max = +$('gear-max').value || min, wide = +$('gear-wide').value, tele = +$('gear-tele').value || wide;
    if (!(min >= 4 && min <= 1200 && max >= min && max <= 1200 && wide >= 0.95 && wide <= 32 && tele >= wide && tele <= 32)) {
      $('gear-status').textContent = 'Revisa el lente: focal entre 4 y 1200 mm, la larga no menor que la corta, y apertura entre f/0.95 y f/32.';
      return;
    }
    gear.lenses.push({ name: '', min: min, max: max, wide: wide, tele: tele });
    gear.lenses[gear.lenses.length - 1].name = lensName(gear.lenses[gear.lenses.length - 1]);
    ['gear-min', 'gear-max', 'gear-wide', 'gear-tele'].forEach(function (id) { $(id).value = ''; });
    changed();
  });
  $('gear-reset').addEventListener('click', function () { gear = reference(); changed(); });
  panel.hidden = false;
  paint();
})(typeof window !== 'undefined' ? window : this);
