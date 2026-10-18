/* Field card behaviour. The card itself is complete HTML: plan, light and tab
   switching are radio buttons, so it works with JavaScript off. This script adds
   what needs a clock or memory: the light slot for the time in Lima, each shot's
   time window for the chosen date, progress saved on this device, the next
   pending shot, the night screen and keeping the screen awake.
   Needs LimaSun (assets/sun_times.js). Pure helpers are exported for
   tests/test_field_card.py. */
(function (root) {
  'use strict';
  var LIMA_OFFSET_MIN = -300;
  var DAYLIGHT = ['sol_pleno', 'sol_velado', 'nublado_claro', 'sombra_abierta', 'ventana'];
  var DARK = ['calle_noche', 'iluminado_focos', 'trafico_noche', 'luces_lejanas', 'oscuridad'];
  var LAMPS = ['interior_casa', 'galeria', 'oficina'];

  function limaMinutes(ms) {
    var d = new Date(ms + LIMA_OFFSET_MIN * 60000);
    return d.getUTCHours() * 60 + d.getUTCMinutes();
  }

  // Day runs from sunrise to the start of the afternoon golden hour, afternoon
  // until the blue hour ends, night until the next sunrise.
  function slotWindows(p) {
    return { day: [p.sunrise, p.golden_pm_start], afternoon: [p.golden_pm_start, p.blue_pm_end], night: [p.blue_pm_end, null] };
  }

  function slotAt(minutes, p) {
    if (minutes >= p.sunrise && minutes < p.golden_pm_start) return 'day';
    if (minutes >= p.golden_pm_start && minutes < p.blue_pm_end) return 'afternoon';
    return 'night';
  }

  // When the light a shot was exposed for actually happens; null when the
  // light does not depend on the sun (lamp-lit interiors).
  function sceneWindow(scene, slot, p) {
    if (LAMPS.indexOf(scene) >= 0) return null;
    if (scene === 'antes_ocaso') return [p.golden_pm_start, p.sunset];
    if (scene === 'tras_ocaso') return [p.sunset, p.blue_pm_end];
    if (DARK.indexOf(scene) >= 0) return [p.blue_pm_end, null];
    if (DAYLIGHT.indexOf(scene) >= 0 && slot === 'day') return [p.sunrise, p.golden_pm_start];
    if (DAYLIGHT.indexOf(scene) >= 0 && slot === 'afternoon') return [p.golden_pm_start, p.sunset];
    return slotWindows(p)[slot];
  }

  function nextEvent(minutes, p) {
    var events = [[p.sunrise, 'sale el sol'], [p.golden_pm_start, 'empieza la hora dorada'],
                  [p.sunset, 'se pone el sol'], [p.blue_pm_end, 'termina la hora azul']];
    for (var i = 0; i < events.length; i++) if (events[i][0] > minutes) return { at: events[i][0], label: events[i][1] };
    return null;
  }

  function span(minutes) {
    var m = Math.max(0, Math.round(minutes)), h = Math.floor(m / 60);
    return h ? h + ' h ' + String(m % 60).padStart(2, '0') + ' min' : m + ' min';
  }

  function windowText(win, clock) {
    if (!win) return 'a cualquier hora';
    if (win[1] === null) return 'desde las ' + clock(win[0]);
    return clock(win[0]) + '–' + clock(win[1]);
  }

  var api = { limaMinutes: limaMinutes, slotWindows: slotWindows, slotAt: slotAt, sceneWindow: sceneWindow,
              nextEvent: nextEvent, span: span, windowText: windowText };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }
  root.FocalRutaCampo = api;

  var app = document.getElementById('field-card-app');
  if (!app || !root.LimaSun) return;
  var S = root.LimaSun, KEY = 'focalruta-campo-v1';
  var $ = function (sel) { return app.querySelector(sel); };
  var $$ = function (sel) { return Array.prototype.slice.call(app.querySelectorAll(sel)); };
  var state = {};
  try { state = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { state = {}; }
  state.done = state.done || {};
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function checked(name) { var r = app.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : null; }
  function choose(name, value) {
    var r = app.querySelector('input[name="' + name + '"][value="' + value + '"]');
    if (r) r.checked = true;
  }
  var today = S.limaToday(Date.now());
  var dateInput = $('#fc-date');

  function chosenDate() { return dateInput && dateInput.value ? dateInput.value : today; }

  function paintWindows() {
    var p = S.dayPlan(chosenDate()), wins = slotWindows(p);
    $$('[data-slot-window]').forEach(function (el) { el.textContent = windowText(wins[el.getAttribute('data-slot-window')], S.clock); });
    $$('.fc-when').forEach(function (el) {
      el.textContent = '· ' + windowText(sceneWindow(el.getAttribute('data-scene'), el.getAttribute('data-slot'), p), S.clock);
    });
    var now = $('#fc-now');
    if (!now) return;
    if (chosenDate() !== today) { now.textContent = 'Planificando el ' + chosenDate() + '. Puesta de sol a las ' + S.clock(p.sunset) + ', rumbo ' + Math.round(p.sunset_azimuth) + '° (' + S.compass(p.sunset_azimuth) + ').'; return; }
    var m = limaMinutes(Date.now()), next = nextEvent(m, p);
    var names = { day: 'día', afternoon: 'tarde', night: 'noche' };
    now.textContent = 'Ahora en Lima es de ' + names[slotAt(m, p)] + '. ' +
      (next ? 'En ' + span(next.at - m) + ' ' + next.label + ' (' + S.clock(next.at) + ').' : 'Mañana sale el sol a las ' + S.clock(S.dayPlan(today).sunrise) + '.') +
      ' Puesta de sol: rumbo ' + Math.round(p.sunset_azimuth) + '° (' + S.compass(p.sunset_azimuth) + ').';
  }

  function visibleSlots() {
    var plan = checked('fc-plan'), slot = checked('fc-slot');
    return $$('.fc-slot[data-plan="' + plan + '"][data-slot="' + slot + '"]');
  }

  function paintProgress() {
    var slots = visibleSlots(), done = slots.filter(function (s) { return s.querySelector('.fc-check').checked; }).length;
    var out = $('#fc-count');
    if (out) out.textContent = done + '/' + slots.length;
  }

  function restore() {
    if (state.plan) choose('fc-plan', state.plan);
    if (state.subject) choose('fc-subject', state.subject);
    var night = $('#fc-night');
    if (night) night.checked = !!state.night;
    var auto = slotAt(limaMinutes(Date.now()), S.dayPlan(today));
    choose('fc-slot', state.slotDay === today && state.slot ? state.slot : auto);
    $$('.fc-check').forEach(function (box) { box.checked = !!state.done[box.getAttribute('data-key')]; });
  }

  function toTop() {
    var scroller = app.closest('.fc-modal-scroll');
    if (scroller) scroller.scrollTo({ top: 0, behavior: 'auto' }); else window.scrollTo({ top: 0, behavior: 'auto' });
  }

  app.addEventListener('change', function (event) {
    var t = event.target;
    if (t.name === 'fc-plan') state.plan = t.value;
    if (t.name === 'fc-subject') state.subject = t.value;
    if (t.name === 'fc-slot') { state.slot = t.value; state.slotDay = today; }
    if (t.name === 'fc-tab') toTop();
    if (t.id === 'fc-night') state.night = t.checked;
    if (t.classList.contains('fc-check')) { if (t.checked) state.done[t.getAttribute('data-key')] = 1; else delete state.done[t.getAttribute('data-key')]; }
    if (t === dateInput) paintWindows();
    save(); paintProgress();
  });

  var next = $('#fc-next'), listHead = $('.fc-listhead');
  if (next) {
    next.hidden = false;
    // Show the button once the controls have scrolled away, so it never covers them.
    if (listHead && 'IntersectionObserver' in root) {
      new IntersectionObserver(function (entries) {
        var e = entries[0];
        next.classList.toggle('fc-next-on', !e.isIntersecting && e.boundingClientRect.top < 0);
      }).observe(listHead);
    } else next.classList.add('fc-next-on');
    next.addEventListener('click', function () {
      choose('fc-tab', 'shots');
      var pending = visibleSlots().filter(function (s) { return !s.querySelector('.fc-check').checked; })[0];
      var status = $('#fc-status');
      if (!pending) { if (status) status.textContent = 'Todas las tomas de este plan y esta luz están hechas.'; return; }
      var card = pending.closest('.fc-shot');
      card.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      pending.querySelector('.fc-check').focus({ preventScroll: true });
      if (status) status.textContent = 'Siguiente: ' + card.querySelector('.fc-name').textContent + '.';
    });
  }

  var reset = $('#fc-reset'), armed = null;
  if (reset) reset.addEventListener('click', function () {
    if (!armed) { reset.textContent = 'Toca otra vez para borrar'; armed = setTimeout(function () { reset.textContent = 'Reiniciar esta lista'; armed = null; }, 4000); return; }
    clearTimeout(armed); armed = null; reset.textContent = 'Reiniciar esta lista';
    visibleSlots().forEach(function (s) { var box = s.querySelector('.fc-check'); box.checked = false; delete state.done[box.getAttribute('data-key')]; });
    save(); paintProgress();
  });

  var awake = $('#fc-awake'), lock = null;
  if (awake && 'wakeLock' in navigator) {
    awake.closest('[hidden]') && (awake.closest('[hidden]').hidden = false);
    var request = function () { navigator.wakeLock.request('screen').then(function (l) { lock = l; }).catch(function () { awake.checked = false; }); };
    awake.addEventListener('change', function () { if (awake.checked) request(); else if (lock) { lock.release(); lock = null; } });
    document.addEventListener('visibilitychange', function () { if (awake.checked && document.visibilityState === 'visible') request(); });
  }

  // V07, V17: keep the plan pages and diagrams for the field, through the service
  // worker, and say whether the kept copy is this version's, an older one or incomplete.
  var packButton = $('#fc-pack'), packStatus = $('#fc-pack-status');
  var files = function (n) { return n === 1 ? 'Falta 1 archivo' : 'Faltan ' + n + ' archivos'; };
  var packText = function (d) {
    if (d.current === d.total) return 'Guardados para usar sin conexión' + (state.packed ? ' el ' + state.packed : '') + '.';
    if (!state.packed) return '';
    if (d.missing) return files(d.missing) + ' de tu copia sin conexión: vuelve a guardarla con señal.';
    return 'Tu copia sin conexión es de una versión anterior de FocalRuta: vuelve a guardarla con señal para tener los ajustes de ahora.';
  };
  if (packButton && 'serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {
    var packUrls = function () { return JSON.parse(packButton.getAttribute('data-urls')).map(function (u) { return new URL(u, location.href).href; }); };
    navigator.serviceWorker.ready.then(function (registration) {
      $('#fc-offline').hidden = false;
      if (state.packed) packStatus.textContent = 'Guardados para usar sin conexión el ' + state.packed + '.';
      registration.active.postMessage({ type: 'pack-status', urls: packUrls() });
      packButton.addEventListener('click', function () {
        var urls = packUrls();
        if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(function () {});
        packButton.disabled = true; packStatus.textContent = 'Guardando 0 de ' + urls.length + '…';
        registration.active.postMessage({ type: 'pack', urls: urls });
      });
    });
    navigator.serviceWorker.addEventListener('message', function (event) {
      var d = event.data || {};
      if (d.type === 'pack-status' && !packButton.disabled) { packStatus.textContent = packText(d); return; }
      if (d.type !== 'pack-progress') return;
      if (d.done < d.total) { packStatus.textContent = 'Guardando ' + d.done + ' de ' + d.total + '…'; return; }
      packButton.disabled = false;
      if (d.failed) { packStatus.textContent = files(d.failed) + ': vuelve a intentarlo con mejor señal.'; return; }
      state.packed = today; save();
      packStatus.textContent = 'Listo: ' + d.total + ' archivos guardados para usar sin conexión.';
    });
  }

  // V15: next to each setting, the same shot with the reader's gear (assets/gear.js),
  // unless it is the Canon 6D kit the plans are solved for.
  function paintGear() {
    var G = root.FocalRutaEquipo;
    if (!G) return;
    var gear = G.load(), same = G.isReference(gear);
    $$('.fc-gear').forEach(function (el) {
      el.innerHTML = same ? '' : G.lineHtml(JSON.parse(el.getAttribute('data-gear')), gear);
      el.hidden = !el.innerHTML;
    });
  }
  document.addEventListener('focalruta:equipo', paintGear);
  root.addEventListener('storage', function (event) { if (event.key === 'focalruta-equipo-v1') paintGear(); });

  if (dateInput) { dateInput.value = today; dateInput.closest('[hidden]') && (dateInput.closest('[hidden]').hidden = false); }
  restore(); paintWindows(); paintProgress(); paintGear();
  setInterval(paintWindows, 60000);
})(typeof window !== 'undefined' ? window : this);
