/* Shot review for the session mode (W05-W07): what to check on the camera's screen after
   each shot, what to change when a check fails, and the session's summary. Pure functions:
   the home page's session dialog draws them, and Node loads this file for the tests. */
(function (root) {
  'use strict';

  // Where "sharp" is judged for each technique, zoomed to 100 % on the camera's screen.
  var SHARP = {
    mucha_pdc: 'El primer plano, el sujeto y el fondo se leen nítidos',
    poca_pdc: 'El ojo o el detalle que enfocaste está nítido',
    congelado: 'La cara y las extremidades están detenidas',
    barrido: 'El sujeto se reconoce: su cara o su torso no están corridos',
    fantasma: 'El fondo está inmóvil, sin trepidación',
    lightpainting: 'Lo que no se mueve está inmóvil: la cámara no vibró',
    larga_exp: 'Lo que no se mueve está inmóvil: la cámara no vibró',
    zooming: 'El centro se lee nítido'
  };

  // What to change when a check fails: one variable, and never the one that makes the effect.
  var FIX_SHARP = {
    mucha_pdc: 'Enfoca al sujeto o a la hiperfocal del plan y cierra a f/11. A pulso, para pasar al 100 %: 1 entre el doble de la focal (1/100 s con el 50 mm, 1/160 s con el 85 mm); el estabilizador del 35 mm permite ≈3 pasos más lento si nada se mueve. Más lento, trípode.',
    poca_pdc: 'Punto AF central sobre el ojo más cercano. Con el sujeto quieto, cierra de f/1.8 a f/2.2–2.8.',
    congelado: 'Tv a 1/1000–1/2000 s con AF AI SERVO; sube el ISO antes que bajar la velocidad.',
    barrido: 'Sube a 1/60, gira desde la cintura y apunta a un detalle estable del sujeto.',
    fantasma: 'Trípode firme y retardo de 2 s o disparador remoto: el fondo debe quedar inmóvil.',
    lightpainting: 'Trípode firme, retardo de 2 s o disparador remoto, y no toques la cámara.',
    larga_exp: 'Trípode firme, retardo de 2 s o disparador remoto, y no toques la cámara.',
    zooming: 'Deja quieto el anillo una fracción del tiempo al empezar y luego gíralo: el centro queda legible.'
  };
  var FIX_INTENT = {
    mucha_pdc: 'Acércate al primer plano y aleja el fondo: las capas se leen por distancia, no sólo por diafragma.',
    poca_pdc: 'Primero aleja al sujeto del fondo; después abre el diafragma o usa el 85 mm.',
    congelado: 'Dispara en ráfaga y quédate con el pico del gesto.',
    barrido: 'Baja de 1/60 a 1/40 y luego a 1/30. Mantén la trayectoria lateral y sigue girando después del disparo.',
    fantasma: 'Si sale tenue, que la persona cruce más despacio o se detenga un instante; si sale sólida, que se mueva más.',
    lightpainting: 'Ensaya el trazo antes, viste ropa oscura y alarga el tiempo si el trazo queda cortado.',
    larga_exp: 'Alarga la exposición hasta que las trazas sean continuas, sin mover la cámara.',
    zooming: 'Busca luces o patrones con contraste, expón de 1" a 4" y gira el anillo de 35 a 80 mm durante toda la exposición, sin mover el trípode.'
  };
  // Too bright: ISO first, then what does not make the effect. f/1.8 at 1/4000 s and ISO 100
  // meters EV 13.7, so in EV 15 sun a shallow-focus shot has nothing left but a filter or shade;
  // past f/11 the 6D's 6.5 µm pixels start to show diffraction, so seconds-long shots take an ND.
  var LONG_OVER = 'Baja a ISO 100 primero. Después cierra hasta f/11 y conserva el tiempo; si aún sobra luz, pon un ND más fuerte antes que cerrar a f/16–22, donde la difracción ablanda.';
  var FIX_OVER = {
    mucha_pdc: 'Baja a ISO 100 primero. Después acorta el tiempo hasta 1/4000 s. No abras el diafragma: las capas necesitan f/8–11.',
    poca_pdc: 'Baja a ISO 100 primero. Después acorta el tiempo hasta 1/4000 s; si a f/1.8–2 aún se quema, pon un ND de 2–3 pasos (rosca de 49 mm en el 50 mm, 58 mm en el 85 mm) o lleva al sujeto a la sombra. No cierres el diafragma: perderías el desenfoque.',
    congelado: 'Baja a ISO 100 primero. Después acorta a 1/4000 s o cierra el diafragma hasta f/4–5.6; nunca alargues el tiempo más allá de 1/2000 s.',
    barrido: 'Baja a ISO 100 primero. Después cierra hasta f/11 y conserva el tiempo; si aún sobra luz, pon un ND de 2–3 pasos antes que cerrar a f/16–22, donde la difracción ablanda.',
    fantasma: LONG_OVER,
    larga_exp: LONG_OVER,
    zooming: LONG_OVER,
    lightpainting: 'Baja a ISO 100 primero. Después cierra hasta f/11 o aleja la linterna; si el fondo sale gris, busca un rincón más oscuro: un ND oscurece por igual el trazo y el fondo, y más allá de f/11 la difracción ablanda.'
  };
  var FIX_UNDER = 'Sube el ISO antes de tocar la velocidad o el diafragma que crean el efecto; en Av o Tv, compensa +⅔ a +1 paso.';

  var LABELS = { s: 'nitidez', e: 'exposición', i: 'intención' };
  // What to do before the next shot about the check that failed most.
  var ADVICE = {
    s: 'Antes de la próxima toma, amplía al 100 % en la pantalla y revisa el foco y la estabilidad.',
    e: 'Activa el aviso de altas luces y mira el histograma RGB en la primera foto de cada luz nueva y después de cada serie.',
    i: 'Relee el criterio «Aprueba si» antes de disparar, no después.'
  };

  function checks(technique, criterion) {
    return [
      { key: 's', question: 'Al 100 %: ' + (SHARP[technique] || 'lo importante está nítido'),
        options: [['ok', 'Sí'], ['no', 'No']] },
      { key: 'e', question: 'Histograma RGB y aviso de altas luces (las zonas que parpadean)',
        options: [['ok', 'Bien'], ['over', 'Quemada'], ['under', 'Oscura']] },
      { key: 'i', question: 'Aprueba si: ' + (criterion || 'la intención visual se consigue'),
        options: [['ok', 'Sí'], ['no', 'No']] }
    ];
  }

  function complete(review) {
    return !!review && (review.legacy === true ||
      (['ok', 'no'].indexOf(review.s) >= 0 && ['ok', 'over', 'under'].indexOf(review.e) >= 0 && ['ok', 'no'].indexOf(review.i) >= 0));
  }

  // 'ok' when every check passed, 'retry' when one failed, null until all are answered.
  function verdict(review) {
    if (!complete(review)) return null;
    if (review.legacy) return 'ok';
    return review.s === 'ok' && review.e === 'ok' && review.i === 'ok' ? 'ok' : 'retry';
  }

  function fixes(technique, review) {
    var out = [];
    if (!complete(review) || review.legacy) return out;
    if (review.s === 'no') out.push(FIX_SHARP[technique] || 'Revisa el foco y la estabilidad, una sola variable cada vez.');
    if (review.e === 'over') out.push(FIX_OVER[technique] || LONG_OVER);
    if (review.e === 'under') out.push(FIX_UNDER);
    if (review.i === 'no') out.push(FIX_INTENT[technique] || 'Cambia una sola variable y repite.');
    return out;
  }

  // What an earlier version, an edit by hand or a damaged store left: keep only what this
  // script writes. `true` is the old "✓ Marcar": a shot passed without its checks.
  function readState(text, length) {
    var raw = null, out = [];
    try { raw = JSON.parse(text || '[]'); } catch (e) { raw = null; }
    for (var i = 0; i < length; i++) {
      var v = Array.isArray(raw) ? raw[i] : null, r = null;
      if (v === true) r = { legacy: true };
      else if (v && typeof v === 'object' && !Array.isArray(v)) {
        r = {};
        if (v.legacy === true) r.legacy = true;
        ['s', 'e', 'i'].forEach(function (k) { if (typeof v[k] === 'string') r[k] = v[k]; });
        if (!complete(r) && !Object.keys(r).length) r = null;
      }
      out.push(r);
    }
    return out;
  }

  // The session at a glance: shots passed, shots to repeat with what to change, and the check
  // that failed most, which names the lesson to review first.
  function summary(states, techniques) {
    var approved = 0, retry = [], pending = [], misses = { s: 0, e: 0, i: 0 };
    techniques.forEach(function (t, n) {
      var r = states[n], v = verdict(r);
      if (v === 'ok') approved++;
      else if (v === 'retry') {
        retry.push({ n: n, fixes: fixes(t, r) });
        if (r.s === 'no') misses.s++;
        if (r.e !== 'ok') misses.e++;
        if (r.i === 'no') misses.i++;
      } else pending.push(n);
    });
    var weakest = null;
    ['s', 'e', 'i'].forEach(function (k) { if (misses[k] && (!weakest || misses[k] > misses[weakest])) weakest = k; });
    return { approved: approved, retry: retry, pending: pending, weakest: weakest,
             label: weakest ? LABELS[weakest] : null, advice: weakest ? ADVICE[weakest] : null };
  }

  var api = { checks: checks, verdict: verdict, fixes: fixes, readState: readState, summary: summary, LABELS: LABELS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FocalRutaRevision = api;
})(typeof window !== 'undefined' ? window : this);
