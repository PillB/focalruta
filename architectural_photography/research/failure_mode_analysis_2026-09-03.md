# Análisis de modos de fallo · 2026-09-03

Requisitos: **M01, M04, M05, L05, Q01, Q03, E03, O03**.

No se corrigen incidencias sueltas. Cada apartado nombra la **clase** de defecto,
la hipótesis que hubo que descartar, la causa raíz y el chequeo que impide que
vuelva. Método aplicado en cada caso: prior art → opciones ordenadas → prueba
sobre el artefacto real → comparación medida → implementación → RED/GREEN.

---

## 1. Un fallo de paridad no podía decir dónde

**Síntoma.** `verify_architecture.py` respondía `"challenge page is stale;
regenerate it"` — el mismo texto para un byte de más que para un archivo vacío.
Localizar la diferencia costaba una investigación manual cada vez.

**Hipótesis descartada.** «Falta una función de diff». Falso: el problema es de
forma, no de biblioteca. `check(condition: bool, message)` recibe un booleano ya
calculado, así que **los operandos se han descartado antes de que exista la
oportunidad de diagnosticar**. Ninguna función añadida a ese helper podría ver
lo que se comparó.

**Causa raíz.** La firma del helper reduce la comparación demasiado pronto.
Seis comparaciones byte a byte en `verify_release.py` heredan el mismo límite.

**Prior art.** [diffoscope](https://reproducible-builds.org/tools/): ante
artefactos idénticos-salvo-algo, desempaquetar y aplicar un diff propio del
formato hasta mostrar dónde divergen.

**Opciones medidas** sobre la página real (398.880 bytes, línea más larga de
273.747 caracteres) renombrando un atributo:

| Opción | Salida | Tiempo | Veredicto |
|---|---|---|---|
| `unified_diff` por líneas | 5 líneas, la mayor de **273.750 caracteres** | 0,00 s | inservible |
| normalizar `><`→`>\n<` y diff | 7 líneas, la mayor de **109** | 0,02 s | legible |
| primer byte divergente + ventana | **offset 12.062 de 398.880** | 0,01 s | exacto |

**Implementado.** `scripts/artifact_diff.py` combina las dos últimas.
`check_equal(expected, actual, label)` sustituye al booleano en ambos guardianes.

**Efecto comprobado.** Un renombrado de un carácter produce ahora:
`offset 12065 of 398880 (expected 398880 bytes, got 398881)` con el `<path>`
exacto a ambos lados. En el release, un byte en `plan_a.html` da
`offset 314 of 4637462`.

**Impide la recaída.** `test_artifact_diff.py` (inicio, final, truncamiento,
inserción, bytes) y `test_gate_diagnostics.py`, que **induce** una regresión real
en la página y exige que el guardián la localice, no sólo que falle.

---

## 2. La evidencia que abría el release estaba caducada

**Síntoma.** Ninguno. Ése era el problema: `verify_release.py` pasaba.

**Causa raíz.** Los tres informes que abren la puerta
(`CURRENT_BROWSER_QA.json`, `OPTICS_ACCESSIBILITY_QA.json`,
`VISUAL_RESOURCE_QA.json`) sólo contenían `passed` y `checks`. **No registraban
qué habían auditado**, así que no existía forma de detectar la deriva. Estaban
comprometidos desde el **2026-08-09**; el sitio que auditan cambió por última vez
el **2026-09-02**. El guardián afirmaba «QA de navegador actual» sobre evidencia
anterior a todos los cambios de esta sesión.

`BUILD_METRICS.json` agravaba la ilusión: guardaba dos sha256 que **nadie leía**.

**Prior art.** El defecto documentado de los snapshots de Jest es que *no dicen
cuáles* quedaron obsoletos; y la corrección de la deriva documental es hacer el
artefacto **derivado** y que CI falle si no se refleja el cambio.

**Implementado.** `scripts/evidence.py` estampa `audited_at`, `audited_commit` y
`audited_artifacts` (sha256 por archivo inspeccionado) en cada informe.
`verify_release.py` ya no acepta «`passed` y 234 checks»: exige que **los hashes
sigan coincidiendo**, y consume además `BUILD_METRICS.json`.

**Efecto comprobado.** Añadir un byte a `field_card.html` produce
`CURRENT_BROWSER_QA.json is stale: field_card.html changed since it was audited
at 2026-09-03T19:47:41Z; re-run its generator`. Los tres informes se
regeneraron contra el build actual: 37, 22 y 234 checks, idénticos a los previos
—no hay regresión de comportamiento, sólo procedencia fresca—.

**Impide la recaída.** `test_qa_evidence_freshness.py` y el propio guardián.

---

## 3. El archivo de estado afirmaba lo que nadie comprobaba

**Síntoma.** El hilo entero empezó porque el estado declaraba una revisión física
que no existía. Se corrigió el **contenido** en la ronda 7 y el **mecanismo** no:
`CURRENT_STATE.json` no lo abre ningún script ni ningún test.

**Causa raíz.** Un archivo de afirmaciones sin lector. Los números `66` paradas,
`25` capas, `41` tramos y `1058` vértices —escritos por mí en las rondas 7 y 8—
no aparecían en ninguna prueba. `ARCHITECTURE_MODULE_INVENTORY.json` sufre lo
mismo y ya se quedó obsoleto una vez.

**Implementado.** `scripts/build_state_snapshot.py` **mide** 23 hechos leyendo
`routes.json`, `learning.json`, la auditoría de geometría, las páginas publicadas
y los informes de QA. Van al bloque `measured`; la historia no comprobable queda
en `narrative`, marcada como tal.

**Trampa encontrada al implementarlo.** La primera versión estampaba
`generated_at: now()`, así que **cada ejecución ensuciaba el árbol** y habría
convertido la nueva puerta de CI en ruido permanente. Es exactamente la fuente de
no-determinismo que cataloga reproducible-builds (marcas de tiempo). Se eliminó:
la procedencia vive en `route_generated_at` y en el historial de git.

**Impide la recaída.** `test_state_snapshot.py` compara lo comprometido con lo
medido y exige que cada clave se mueva cuando se mueve su artefacto.

---

## 4. No había una sola forma de preguntar «¿está al día lo generado?»

**Causa raíz.** El orden de generación sólo existía en prosa en `README.md`, y la
única puerta de staleness cubría **una** página. `learning.json`, la wiki, los
mapas y el build hospedado podían quedar atrasados sin que nada lo dijera.

**Prior art.** `make generate && git diff --exit-code`, el patrón estándar.

**Implementado.** `scripts/regenerate_all.py` ejecuta los cinco generadores
deterministas en orden de dependencia, con `--with-browser-qa` para los tres que
necesitan Chrome. CI ejecuta el guion y después `git diff --exit-code`.
`build_architecture_routes.py` queda fuera por depender del router externo, y el
guion lo dice explícitamente.

**Impide la recaída.** `test_regeneration_entrypoint.py` exige cobertura de cada
generador y que una regeneración deje el árbol intacto.

---

## 5. Pruebas que leían el código como texto

**Síntoma.** `test_round5_routes.py` afirmaba `"MAX_WALKING_LEG_M = 1000" in
source` y `"TemporaryDirectory" in source`.

**Causa raíz.** Comprobar la existencia de una cadena en el fuente no observa
comportamiento: renombrar la constante cambiando su valor habría pasado la prueba
y roto el producto. `AGENTS.md:43` prohíbe exactamente ese patrón, así que el
contrato estaba incumplido **dentro de la propia suite**.

**Implementado.** Se importan las constantes y se ejercita la conducta: que el
techo de conectividad sea mayor que la preferencia de transferencia, que ningún
tramo caminado lo supere, y que `atomic_json` no deje archivos temporales.

---

## 6. Prosa exacta como contrato

**Síntoma.** Reescribir textos rompió seis pruebas en un solo día de esta sesión;
había ~60 aserciones de frases literales en español.

**Causa raíz.** La prueba fijaba la **redacción** cuando lo que importa es la
**propiedad**. Además fallaba en el sentido contrario: una reescritura podía
suprimir el descargo de un lab y seguir pasando si la frase sobrevivía en otro
sitio de la página.

**Implementado.** `test_editorial_contracts.py` comprueba propiedades:
ninguna página promete probabilidad de ganar; **cada** lab declara su límite,
ofrece reinicio y estado inicial; cada control tiene `<label>`; el fallback sin
JavaScript cubre un ejercicio por lab; cada familia técnica llega a un sitio
donde practicarla; ninguna página publica un marcador sin resolver. Se conservan
como cadena literal sólo las afirmaciones donde la palabra **es** el contrato.

**Dos falsos positivos propios, detectados y corregidos antes de tocar el sitio.**
`TODO` es palabra española corriente («TODO desde ~2,5 m queda nítido»), así que
el chequeo de marcadores exige ahora la forma `TODO:`. Y el glosario se
comprobaba contra la página equivocada: KML pertenece al reto, no al planificador
raíz. Ninguno era un defecto del producto.

---

## 7. Un concurso cerrado que nada marcaba como cerrado

**Causa raíz.** `competition_rules.json` describe una edición cuyo plazo terminó
el **2026-08-30**, y `test_competition_rules.py` sólo comprobaba que el JSON
coincidiera consigo mismo: ninguna comparación con la fecha real, así que la
prueba seguiría pasando indefinidamente.

**Matiz importante.** La página pública **no** mostraba la fecha caducada: es
evergreen por contrato (`test_round1_page.py:10` exige que no aparezca) y el
decodificador pide al usuario las fechas de su convocatoria. El defecto era del
dato, no de lo que ve el lector.

**Implementado.** `edition_state` y `edition_note` explícitos, más
`test_competition_window.py`, que compara `closes_local` con la fecha de hoy.

---

## Deuda registrada, fuera del alcance acordado

- **Óptica duplicada en JavaScript.** `upgrade_optics_accessibility.py:93` y
  `sota_upgrade.py:131` reimplementan cada uno `atan(sw/2f)`, `H=f²/(N·c)+f` y
  las constantes `coc=.03, sw=35.8`. Ambas copias son **correctas hoy** y ambas
  se publican, pero son independientes de `scripts/optics_physics.py` y entre sí.
  Esto acota la afirmación de la ronda 7: el módulo unifica la óptica de Python y
  de los laboratorios del reto, **no** la del laboratorio óptico de la raíz.
- Umbrales de ruta (`800`/`1000`/`1500`) repetidos como literales en cinco
  archivos sin importar la constante.
- `VIEWPORTS` duplicado literalmente en cuatro guiones, con
  `browser_release_qa.py` y `live_pages_qa.py` ya **divergentes** (1440×1000
  frente a 1440×1100).
- Dos implementaciones distintas de distancia geodésica.
- Colgados restantes: `navigator.serviceWorker.ready` sin guarda en
  `browser_architecture_release_qa.py:32` y `live_pages_qa.py:148`
  (`page.evaluate` no tiene tiempo límite propio en Playwright), ausencia de
  `set_default_timeout` en todos los guiones y de `pytest-timeout` en la suite.
- `research_video_ledger.py:71,73` llama a la API de transcripciones sin límite
  de tiempo: la misma clase que ya costó una tarde en las rutas.
