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

---

# Continuación · 2026-09-04 · duplicación y colgados

La ronda anterior dejó estos puntos como deuda explícita. Se atacan con el mismo
método: prior art → opciones ordenadas → prueba sobre el artefacto real →
comparación medida → RED/GREEN.

## 8. La matriz de viewports era tres listas, y una incumplía el contrato

**Síntoma.** Ninguno visible. Cuatro guiones de navegador llevaban cada uno su
copia de la tupla N01, y otros dos llevaban una **distinta y más corta**.

**Causa raíz.** No es sólo duplicación: `REQUIREMENTS_INVENTORY.md:144` exige
como **N01 MUST** seis viewports —390×844, 430×932, 844×390, 932×430, 820×1000 y
1440×1100— pero `browser_release_qa.py` y `live_pages_qa.py` comprobaban
**tres**, y una de ellas era **1440×1000**, un tamaño que N01 no nombra. La
cobertura obligatoria estaba incompleta y la duplicación lo ocultaba.

**Implementado.** `scripts/qa_matrix.py` define `REQUIRED_VIEWPORTS` una sola vez
y los seis guiones la importan. Un test compara la tupla con la línea N01 del
propio inventario, así que la lista no puede divergir del requisito sin fallar.

**Efecto medido, no supuesto.** La matriz de navegador pasó de **234 a 246
checks, con cero fallos**: los cuatro viewports que N01 exigía y nadie probaba ya
estaban bien, pero ahora se verifican de verdad. La puerta de release dejó de
comparar un número opaco y ahora comprueba **cobertura**: el informe declara qué
viewports recorrió y `verify_release.py` exige que ese conjunto sea exactamente
el de N01, nombrando los que falten o sobren.

## 9. Cuatro `await` que no podían fallar, sólo colgarse

**Prior art consultado.** [microsoft/playwright#13253](https://github.com/microsoft/playwright/issues/13253)
sigue **abierto**: `page.evaluate` no tiene tiempo límite propio; su argumento
`timeout` cubre la disponibilidad del elemento, no la promesa. Y
[MDN](https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/ready)
documenta que `navigator.serviceWorker.ready` **espera indefinidamente** por
diseño y nunca se rechaza. No es un defecto que corregir: es una propiedad
contra la que hay que protegerse.

**Opciones ordenadas y comparadas.**

| Opción | Veredicto |
|---|---|
| `Promise.race` **dentro** del JavaScript evaluado | ✔ corrige en el origen: el navegador rechaza y Python nunca se bloquea |
| `set_default_timeout` | parcial: cubre localizadores y navegación, **no hace nada** por `evaluate` |
| `pytest-timeout` | sólo red de seguridad; los guiones de QA no los recoge pytest |
| Hilo en Python con `join(timeout)` | deja el navegador colgado y filtra el hilo |

Se implementó la primera como corrección y las dos siguientes como defensa en
profundidad: `qa_matrix.bounded_async()` envuelve la expresión, `harden()` fija
tiempos explícitos en siete puntos de creación de página, y `pytest.ini` añade un
límite global.

**Cuatro sitios corregidos:** `browser_architecture_release_qa.py:32` y
`live_pages_qa.py:148` (`serviceWorker.ready`), más el barrido de recursos —cada
`fetch` con su `AbortSignal.timeout`— y el de decodificación de imágenes, donde
`.catch()` sólo atrapaba rechazos, no una promesa que nunca se resuelve.

## 10. Mi propia prueba nueva era un falso verde

**Síntoma.** El contrato «ningún `await` sin límite» pasaba con 17 verdes
mientras dos `await` sin límite seguían en el archivo.

**Causa raíz.** La inspección usaba una expresión regular no codiciosa. El
JavaScript contiene sus propias comillas (`'serviceWorker' in navigator`), así
que el cierre `['\"]` disparaba antes de tiempo y **truncaba el cuerpo**: la
palabra `await` quedaba fuera de la captura y la prueba informaba de cero casos.

**Implementado.** Análisis con `ast` en vez de regex, más una **meta-prueba** que
exige ver al menos 15 llamadas a `evaluate` y al menos una con `await`. Con ella
el contrato se puso en rojo de inmediato y encontró los dos colgados reales.

**Lección.** Una comprobación que sólo ha pasado no demuestra nada sobre lo que
detectaría. Por eso el guardián de óptica se refactorizó a la función pura
`optics_drift()`, ejercitada en ambas direcciones: constante intacta, constante
desviada, dos desviadas a la vez y laboratorio ausente.

## 11. Corrección a la ronda 9: la óptica JS no se publica dos veces

La ronda 9 afirmó que las dos copias JavaScript de la óptica «se publican».
**Es falso.** Sólo `upgrade_optics_accessibility.py` es la viva: su marcador de
`stops`/`presets` está en `index.html`, mientras que el de `sota_upgrade.py`
(`maxScene=30`) **no aparece** en la página y ningún guion invoca ese archivo.
Es código superado, no una segunda copia en producción.

El riesgo real es más estrecho: una copia viva que puede desviarse de
`optics_physics.py`. Se cubre con un test que compara las constantes que
**realmente se publican** (`coc`, `sw`) contra el módulo probado, y con otro que
exige que la salida del generador superado no reaparezca.

## 12. Coste de CI que yo mismo introduje

La puerta de regeneración de la ronda 9 subió el workflow Quality de **30 s a
95 s**, porque la regeneración corría dos veces: como paso de CI y otra vez
dentro de `test_regenerating_leaves_the_tree_unchanged`. La prueba se salta ahora
bajo `GITHUB_ACTIONS`, conservando su valor en local, donde ese paso no existe.

## Deuda que permanece

- `research_video_ledger.py:71,73` llama a la API de transcripciones sin tiempo
  límite. Es la misma clase ya corregida dos veces; queda fuera porque ese guion
  no forma parte de ningún ciclo automático.
- `pytest.ini` declara `timeout = 600`, pero sin `pytest-timeout` instalado
  pytest lo ignora con un aviso. CI lo instala; en local no hay red de seguridad
  salvo que se instale a mano. El propio archivo lo dice ahora, para que nadie
  suponga una protección que no está activa.

---

# Continuación · 2026-09-04 (tarde) · deuda pendiente cerrada

## 13. La tercera aparición de «sólo puede colgarse, nunca fallar»

**Auditoría completa de `scripts/research_video_ledger.py`.** Sus cinco llamadas
de red: `yt_dlp` con `socket_timeout: 20` ✓, dos `requests.get(..., timeout=30)` ✓,
y **`api.list()` más `track.fetch()` sin límite alguno**. Sólo esas dos.

**Prior art.** [jdepoix/youtube-transcript-api#324](https://github.com/jdepoix/youtube-transcript-api/issues/324)
sigue abierto: la biblioteca **no tiene** opción de tiempo límite. Y hay una
trampa: `requests.Session` tampoco la tiene, porque `timeout` es argumento de
cada petición, no atributo de la sesión. Pasarle una `Session` normal como
`http_client` **no habría cambiado nada**.

**Opciones ordenadas.**

| Opción | Veredicto |
|---|---|
| Subclase de `Session` que inyecta el plazo en cada `request()` | ✔ cubre todas las llamadas y usa el único punto de extensión documentado |
| `HTTPAdapter(max_retries=…)` | controla reintentos, **no** el tiempo límite |
| `socket.setdefaulttimeout()` | global y brusco; afecta a E/S ajena |
| Hilo con `join(timeout)` | la petición sigue viva y el hilo se filtra |

**Implementado.** `scripts/bounded_http.py`: `bounded_session()` devuelve una
sesión que pone el plazo por defecto en cada petición y **respeta** el que ya
traiga la llamada. Se pasa como `http_client` en el único punto de uso.

**Probado sin red y sin la biblioteca instalada** —`youtube_transcript_api` no
está en este entorno— sustituyendo el `request` del padre por un grabador. Una de
las pruebas fija además la **razón** de existir del módulo: si algún día
`requests.Session` gana un `timeout` propio, esa prueba falla y avisa de que el
módulo puede retirarse.

## 14. La lista de dependencias vivía sólo en el workflow

**Síntoma.** `pytest.ini` declaraba `timeout = 600`, pero sin `pytest-timeout`
pytest lo ignora con un aviso: en local no había ninguna red de seguridad
mientras el archivo aparentaba prometerla.

**Causa raíz.** No era el aviso: era que la lista de dependencias existía
**únicamente** dentro de `.github/workflows/quality.yml`. El entorno de quien
desarrolla podía diferir del de CI sin que nada lo detectara. La misma
duplicación de fuente de verdad que ya se corrigió para la óptica, los umbrales
de ruta y los viewports.

**Implementado.** `requirements-dev.txt` con la razón de cada dependencia y de
cada versión fijada; el workflow instala desde él; y
`test_ci_and_contributors_install_the_same_dependency_set` exige que lo haga y
que `pytest-timeout` esté presente mientras `pytest.ini` declare un `timeout`.
Ahora divergir requiere romper una prueba.

**Sigue siendo cierto** que en un entorno sin instalar el archivo, el aviso
aparece. La diferencia es que existe un comando único que lo resuelve y el
`pytest.ini` lo señala.

## Estado de la deuda

Cerrada. Del inventario que abrió estas rondas —diagnóstico imposible, evidencia
caducada, estado sin respaldo, duplicación de verdad, colgados silenciosos y
pruebas tautológicas— no queda ningún punto abierto. Lo que resta es de campo,
no de código: comprobar a pie el enlace de 854 m entre Puente Villena y Larcomar.

## 15. Publicación no atómica del build hospedado (incidente propio)

**Síntoma.** Un `git commit` de esta sesión registró **176 borrados espurios** de
`dist/canon6d_sota_hosted`, con los archivos presentes en disco.

**Primera hipótesis (descartada).** Que algo los ignorara. `git check-ignore -v`
no devolvió nada y no había `.gitignore` dentro de `dist/`.

**Causa raíz.** `build_dual_release.py:7` hacía `shutil.rmtree(OUT)` y volvía a
poblar el árbol durante varios segundos. Yo ejecuté `git add -A` mientras una
suite en segundo plano —cuya prueba de regeneración reconstruye `dist/`— estaba
justo en esa ventana. **La publicación no era atómica**, así que cualquier lector
del directorio en ese instante veía un árbol vacío o parcial: una tarea de CI, un
guion de QA o, como aquí, un `git add`.

El repositorio ya tenía el patrón correcto en
`build_architecture_routes.publish_downloads`: preparar aparte y cambiar de golpe.

**Implementado.** El build escribe en `dist/.canon6d_sota_hosted.staging` y sólo
al final, con todo correcto, hace el intercambio con `os.replace`. Un `atexit`
retira el staging si el build falla, para no dejar basura. Quien lea `dist/` ve
la publicación anterior o la nueva, nunca una a medias.

**Prueba de comportamiento, no de texto.** Se rompe el build a propósito
—eliminando `field_card.html`, que se copia ya empezado el árbol— y se exige que
la publicación anterior siga **intacta**. Antes del arreglo esa prueba destruía
el árbol publicado; ahora conserva los 244 archivos.

**Dos defectos más que salieron de ahí.**

1. `shutil.copytree` publicaba `.DS_Store` en el sitio. Ahora se excluye.
2. El build **copiaba `data/plans.json` sin mirarlo**: mi inyección de fallo dejó
   un fragmento corrupto de 16 bytes publicado y el build informó de éxito. Ahora
   valida el JSON antes de copiarlo y se niega a publicar datos ilegibles. Fue el
   propio `artifact_diff` de la ronda 9 el que localizó la contaminación:
   `first difference at offset 1 of 153950`.

**Lección de proceso.** Estas pruebas tienen que romper cosas reales para
demostrar que el build falla con seguridad, y una interrupción a mitad dejaba el
repositorio dañado —me borró `field_card.html` una vez—. La restauración pasó a
hacerse con `git checkout --` en el desmontaje del fixture, de modo que el
archivo vuelve byte a byte aunque la copia de respaldo hubiera fallado, y el
fixture barre además cualquier staging huérfano.
