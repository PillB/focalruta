/* Error log on this device (requirement X04). FocalRuta has no server and
   sends nothing, so when something breaks on a reader's phone the phone is the
   only witness. This keeps the last 20 distinct failures in localStorage:
   uncaught errors, unhandled promise rejections, images, scripts or styles
   that fail to load, and a service worker that fails to register. For each it
   keeps what failed (cut to 160 characters, without markup), where (file and
   line, page path), how many times, and the first and last time.
   It never keeps query strings or fragments (they can carry anything), the
   browser's identity, or the reader's gear, ticks or other saved data, and it
   never makes a request: the log leaves the device only if the reader copies
   it or opens the prefilled report and sends it. The home page shows it in its
   footer. Pure helpers are exported for tests/test_diagnostics.py. */
(function (root) {
  'use strict';
  var KEY = 'focalruta-errores-v1', LIMIT = 20, TEXT = 160, REPORT_CHARS = 6000;
  var ISSUES = 'https://github.com/PillB/focalruta/issues/new';
  var KINDS = { error: 'Error', promesa: 'Promesa rechazada', recurso: 'No cargó', trabajador: 'Modo sin conexión' };

  // Any URL inside a message keeps its scheme, host and path; ?query and #fragment go.
  function stripUrls(text) {
    return text.replace(/\b((?:https?|file|blob):\/\/[^\s?#'"()<>]*)[?#][^\s'"()<>]*/g, '$1');
  }
  function clean(text) {
    var flat = stripUrls(String(text == null ? '' : text)).replace(/[<>&"]/g, '').replace(/\s+/g, ' ').trim();
    return flat.length > TEXT ? flat.slice(0, TEXT - 1) + '…' : flat;
  }
  function fileOf(url) {
    var path = String(url || '').split(/[?#]/)[0];
    return clean(path.slice(path.lastIndexOf('/') + 1));
  }
  function minute(date) { return date.toISOString().slice(0, 16) + 'Z'; }

  function entry(kind, message, source, line, column, page, now) {
    var where = fileOf(source) + (line ? ':' + line + (column ? ':' + column : '') : '');
    var stamp = minute(now);
    return { kind: KINDS[kind] ? kind : 'error', message: clean(message) || 'sin mensaje', where: where,
      page: clean(String(page || '').split(/[?#]/)[0]), count: 1, first: stamp, last: stamp };
  }
  function same(a, b) {
    return a.kind === b.kind && a.message === b.message && a.where === b.where && a.page === b.page;
  }
  // Newest first; a repeat moves to the top with its count raised; the stalest falls off.
  function add(list, item) {
    var kept = [], merged = item;
    for (var i = 0; i < list.length; i++) {
      if (same(list[i], item)) merged = { kind: item.kind, message: item.message, where: item.where, page: item.page,
        count: list[i].count + 1, first: list[i].first, last: item.last };
      else kept.push(list[i]);
    }
    return [merged].concat(kept).slice(0, LIMIT);
  }
  function valid(item) {
    return item && typeof item.message === 'string' && typeof item.count === 'number' && KINDS[item.kind];
  }

  function text(list) {
    if (!list.length) return 'Ningún error registrado en este dispositivo.';
    return list.map(function (item) {
      return (item.count > 1 ? item.count + ' veces' : '1 vez') + ' · ' + item.last.replace('T', ' ') + ' · ' +
        KINDS[item.kind] + ' · ' + item.message + (item.where ? ' · ' + item.where : '') + ' · en ' + item.page;
    }).join('\n');
  }
  function issueUrl(list) {
    var body = 'Registro de errores de FocalRuta (copiado por quien lo envía):\n\n' + text(list);
    if (body.length > REPORT_CHARS) body = body.slice(0, REPORT_CHARS - 1) + '…';
    return ISSUES + '?' + new URLSearchParams({ title: 'Error en FocalRuta', body: body });
  }

  var api = { KEY: KEY, LIMIT: LIMIT, TEXT: TEXT, clean: clean, fileOf: fileOf, entry: entry, add: add, text: text, issueUrl: issueUrl };
  if (typeof module === 'object' && module.exports) { module.exports = api; return; }

  function load() {
    try {
      var list = JSON.parse(root.localStorage.getItem(KEY) || '[]');
      return Array.isArray(list) ? list.filter(valid).slice(0, LIMIT) : [];
    } catch (e) { return []; }
  }
  function save(list) {
    try { root.localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* private mode or full: nothing to do */ }
  }
  function record(kind, message, source, line, column) {
    try {
      save(add(load(), entry(kind, message, source, line, column, root.location && root.location.pathname, new Date())));
      paint();
    } catch (e) { /* the log must never become the error */ }
  }
  api.load = load;
  api.record = record;
  api.clear = function () { save([]); paint(); };

  root.addEventListener('error', function (event) {
    var target = event.target;
    if (target && target !== root && target.tagName) {
      var url = target.currentSrc || target.src || target.href || '';
      record('recurso', target.tagName + ' ' + fileOf(url), url);
    } else {
      record('error', event.message || (event.error && event.error.message), event.filename, event.lineno, event.colno);
    }
  }, true);
  root.addEventListener('unhandledrejection', function (event) {
    var reason = event.reason;
    record('promesa', reason && reason.message ? reason.message : String(reason));
  });

  // The footer panel on the home page; other pages only record.
  function paint() {
    var doc = root.document, list = doc && doc.getElementById('diag-list');
    if (!list) return;
    var items = load();
    list.textContent = '';
    doc.getElementById('diag-empty').hidden = items.length > 0;
    items.forEach(function (item) {
      var li = doc.createElement('li');
      li.textContent = text([item]);
      list.appendChild(li);
    });
    doc.getElementById('diag-report').href = issueUrl(items);
    doc.getElementById('diag-count').textContent = items.length ? '(' + items.length + ')' : '';
  }
  function wire() {
    var doc = root.document, copy = doc.getElementById('diag-copy'), wipe = doc.getElementById('diag-clear');
    if (!copy) return;
    paint();
    copy.addEventListener('click', function () {
      var done = function () { copy.textContent = 'Copiado'; };
      if (root.navigator.clipboard) root.navigator.clipboard.writeText(text(load())).then(done, function () {});
    });
    wipe.addEventListener('click', function () {
      if (wipe.dataset.armed) { api.clear(); delete wipe.dataset.armed; wipe.textContent = 'Borrar el registro'; return; }
      wipe.dataset.armed = '1';
      wipe.textContent = 'Toca otra vez para borrar';
    });
  }
  if (root.document && root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', wire);
  else if (root.document) wire();
  root.FocalRutaDiagnostico = api;
})(typeof window !== 'undefined' ? window : this);
