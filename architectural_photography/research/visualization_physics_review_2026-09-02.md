# Revisión física de las visualizaciones · 2026-09-02

Requisitos cubiertos: **G05, G07, H03, H04, H05, H06, H07, H08, N08, O03**.

Cada visualización pública se comparó contra la fórmula que un óptico o un
ingeniero de render aceptaría. Para cada fenómeno se registra el banco de
pruebas, lo que el código hacía antes, el motivo por el que un experto lo
rechazaría y la decisión tomada.

## 1. Campo de visión y focal

**Banco de pruebas.** El semiángulo de visión es `atan(d / (2·f))`, con `d` la
dimensión del sensor y `f` la focal. En un sensor de 36 mm de ancho, 35 mm da
≈27,3° de semiángulo y 85 mm da ≈11,9°. Alargar la focal **cierra** el campo.
Fuente: [Angle of view](https://shuttermuse.com/calculate-field-of-view-camera-lens/),
[The Math of Camera Field of View](https://scantips.com/lights/fieldofviewmath.html).

**Antes.** `halfFov = Math.min(58, 22 + focal/8)` en el lab 1: el cono se abría
al alargar la focal. Con 35 mm daba 26,4° y con 85 mm daba 32,6°.

**Rechazo del experto.** La lección declarada del lab es H03 —la posición
controla la perspectiva, la focal controla el encuadre— y el dibujo enseñaba lo
contrario: sugería que un 85 mm ve *más* escena. El propio repositorio ya tenía
la fórmula correcta en `get_fov()` (`scripts/generate_diagrams.py:115`), de modo
que había dos verdades ópticas incompatibles en el mismo proyecto.

**Decisión.** Una sola implementación en `scripts/optics_physics.py`;
`generate_diagrams.py` y `generate_lens_comparison.py` la importan. El lab dibuja
el cono real y muestra el semiángulo en grados junto al deslizador.

## 2. Punto de fuga vertical y convergencia

**Banco de pruebas.** Con la cámara nivelada, las verticales del mundo son
paralelas al plano del sensor y no convergen: su punto de fuga está en el
infinito. Al inclinar la cámara un ángulo θ, ese punto de fuga aparece a una
distancia `f_px / tan θ` del punto principal, medida en píxeles del sensor.
Cuanto mayor es la inclinación, **más cerca** del centro del encuadre cae el
punto de fuga y más marcada es la convergencia. Fuente:
[Using Vanishing Points to Correct Camera Rotation](http://chenlab.ece.cornell.edu/people/Andy/publications/Andy_files/rotation_crv2005.pdf).

**Antes.** `vanishingY = Math.max(8, 64 - tilt*1.6)` e `inset = tilt*1.4`:
lineales, y el punto de fuga *subía* alejándose del encuadre al inclinar.

**Rechazo del experto.** La relación es tangencial, no lineal, y el sentido del
movimiento estaba invertido: enseñaba que inclinar más aleja el punto de fuga.
Con eso, el estudiante no puede predecir cuánta convergencia obtendrá al
inclinar, que es exactamente la decisión de campo de H06.

**Decisión.** Las cuatro esquinas de la fachada se proyectan de verdad bajo
inclinación; el punto de fuga se sitúa en `f_px/tan θ` y a 0° se rotula
explícitamente «paralelas: punto de fuga en el infinito».

## 3. Sombreado difuso

**Banco de pruebas.** Ley del coseno de Lambert: la irradiancia sobre una cara
es proporcional a `cos θ`, con θ el ángulo entre la dirección de la luz y la
normal de la cara; la radiancia difusa reflejada es `ρ/π · E · cos θ` y no
depende del ángulo de observación. En incidencia rasante (θ→90°) tiende a cero.
Fuentes: [Lambert's cosine law](https://en.wikipedia.org/wiki/Lambert%27s_cosine_law),
[BRDF review, Mungan](https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/BRDFreview.pdf),
[Diffuse Reflection, PBR Book](https://pbr-book.org/4ed/Reflection_Models/Diffuse_Reflection).

**Antes.** Cuatro presets con rellenos fijos (`#c66b3d`, un gradiente, un gris)
y el atributo `data-physics-model="lambert-shadow"`. La cadena `cos` no aparecía
en ningún punto del JavaScript.

**Rechazo del experto.** El atributo afirmaba un modelo que no existía. Además,
al no derivar el tono del ángulo, las dos caras del volumen no mantenían la
relación de luminancia que el estudiante debe aprender a leer en fachada.

**Decisión.** Cada cara declara su normal; el tono se calcula con `cos θ` sobre
el azimut de luz elegido y se convierte a un gris/ámbar con la misma rampa para
todas las caras. Las caras que miran en dirección opuesta a la luz quedan en el
nivel de luz ambiente, no en negro absoluto.

## 4. Sombra proyectada, umbra y penumbra

**Banco de pruebas.** La longitud de la sombra de un objeto de altura `h` con el
sol a una altura angular `a` es `h / tan a`. Una fuente extendida produce umbra
(todos los rayos bloqueados) rodeada de penumbra (sólo algunos bloqueados); el
ancho de la penumbra sobre el plano receptor crece con el tamaño angular de la
fuente y con la distancia entre el ocluyente y ese plano, aproximadamente
`distancia · tan(diámetro angular)`. Cuanto más ancha es la fuente, más
difuminada es la sombra. Fuentes: [Shadow](https://en.wikipedia.org/wiki/Shadow),
[Law of geometric propagation, UT Austin](https://farside.ph.utexas.edu/teaching/316/lectures/node126.html).

Valores de referencia: el disco solar mide ≈0,53° de diámetro angular, así que a
2 m de distancia la penumbra mide ≈1,8 cm —un borde que se lee como duro—;
un cielo cubierto de garúa es una fuente de decenas de grados y la umbra
desaparece.

**Antes.** Polígonos `points="70,90 180,112 105,112"` escritos a mano por preset,
con la línea de dirección de la luz como literales independientes. Nada
garantizaba que la sombra siguiera al foco al cambiar de estado.

**Rechazo del experto.** Dos literales que se ajustaron a ojo pueden dejar de
concordar en cuanto se toque uno; y el estudiante no puede derivar la regla
«sombra larga = sol bajo» porque la longitud no dependía de la altura solar.

**Decisión.** Un único vector de luz (azimut + altura angular) gobierna la línea
de dirección, la longitud y la orientación de la sombra, el reparto Lambert
entre caras y el ancho de penumbra. El tamaño angular de la fuente es un control
explícito: sol directo ≈0,5°, cielo nublado ≈60°.

## 5. Reflejo especular

**Banco de pruebas.** Aproximación de Schlick a las ecuaciones de Fresnel:
`R(θ) = F0 + (1 − F0)(1 − cos θ)^5`, con `F0 ≈ 0,04` para vidrio (n≈1,5). En
incidencia normal refleja ≈4 %; en incidencia rasante tiende al 100 %,
independientemente del material. Fuentes:
[Schlick's approximation](https://en.wikipedia.org/wiki/Schlick%27s_approximation),
[The Schlick Fresnel Approximation, Ray Tracing Gems II](https://link.springer.com/content/pdf/10.1007/978-1-4842-7185-8_9.pdf).

**Antes.** `#composition-reflection`: dos trazos paralelos con `opacity=".55"`
constante, mostrados siempre en el estado «luz / clima» y nunca tocados por el
JavaScript.

**Rechazo del experto.** Es justo la relación que decide dónde plantarse frente
a una fachada vidriada: caminar hacia un ángulo más rasante multiplica el
reflejo. Un trazo de opacidad fija no enseña esa decisión.

**Decisión.** La opacidad del reflejo se calcula con Schlick a partir del ángulo
de incidencia elegido, y el lab muestra el porcentaje reflejado.

## 6. Halo y velo de luz

**Banco de pruebas.** El halo alrededor de una fuente brillante es dispersión en
la óptica y en la atmósfera; su extensión visible crece con la razón entre la
luminancia de la fuente y la exposición elegida, y satura cuando la fuente
supera el techo del sensor. Referencia conceptual de divulgación:
[Lights and Shadows, Ciechanowski](https://ciechanow.ski/lights-and-shadows/).

**Antes.** Un `<circle r="25">` con gradiente radial, fijo, nunca actualizado.

**Rechazo del experto.** Presentaba como fenómeno lo que era un adorno: no
respondía ni al brillo ni a la exposición, así que no podía enseñar «cierra un
paso y el halo se contrae».

**Decisión.** El radio del halo y la opacidad del núcleo se derivan del brillo de
la fuente y de la exposición en pasos; el lab declara que es una relación
monótona pedagógica, no una función de dispersión calibrada.

## 7. Profundidad de campo

**Banco de pruebas.** Distancia hiperfocal `H = f²/(N·c) + f`; límites
`cerca = H·s/(H + (s − f))`, `lejos = H·s/(H − (s − f))`, con `c = 0,030 mm`
para formato completo. Ya estaba implementado correctamente en
`estimate_dof()` (`scripts/generate_diagrams.py:206`).

**Decisión.** Se traslada al módulo compartido y se usa también en el lab nuevo
de exposición para que la apertura mueva de verdad la zona nítida.

## 8. Perspectiva aérea

**Banco de pruebas.** El contraste y la saturación de un plano decaen con la
distancia por dispersión atmosférica; en fotografía urbana es la señal que
separa capas cuando la geometría por sí sola no lo consigue.

**Antes.** No existía visualización de capas ni de profundidad.

**Decisión.** El lab de capas atenúa el contraste de cada plano según su
distancia y ordena los solapes por profundidad real.

## Límite declarado que se mantiene

Los labs calculan la **dirección y el orden de magnitud** de cada relación con
las fórmulas anteriores. No son renders calibrados: no predicen píxeles, ni
exposición real, ni el comportamiento de una óptica concreta. Ese límite sigue
visible en cada lab y en la wiki.
