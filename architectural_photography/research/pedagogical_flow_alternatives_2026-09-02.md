# Diez alternativas de flujo pedagógico · 2026-09-02

Requisitos cubiertos: **G04, G06, L10, M03, N03, O03**.

## Criterios y cómo se puntúan

Cinco criterios, 1 a 5, con la evidencia que sostiene el juicio:

1. **Carga cognitiva** — cuánto hay que sostener en memoria de trabajo antes de
   poder actuar. Teoría de carga cognitiva y efecto del ejemplo resuelto:
   [Sweller, Cognitive Architecture and Instructional Design: 20 Years Later](https://link.springer.com/article/10.1007/s10648-019-09465-5).
2. **Descubrimiento** — si el usuario encuentra lo que necesita sin conocer ya el
   vocabulario. [GOV.UK: content design](https://www.gov.uk/guidance/content-design/writing-for-user-needs),
   [NN/g: progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/).
3. **Práctica** — si cada bloque termina en una acción ejecutable con cámara.
   [Merrill, First Principles of Instruction](https://www.researchgate.net/publication/242222147_First_Principles_of_Instruction).
4. **Recuperación** — si el flujo obliga a recordar antes de mostrar la respuesta.
   [Roediger y Karpicke, repeated retrieval](https://learninglab.psych.purdue.edu/downloads/2007/2007_Karpicke_Roediger_JML.pdf).
5. **Transferencia** — si lo aprendido sobrevive al salir a la calle.

Referencia de calidad para las visualizaciones interactivas:
[Ciechanowski, Lights and Shadows](https://ciechanow.ski/lights-and-shadows/) y
[Cameras and Lenses](https://ciechanow.ski/cameras-and-lenses/), donde cada
control mueve una magnitud física y el texto explica qué mirar. Ese es el listón:
un control que no cambia geometría no enseña nada.

## Estado actual (base de comparación)

Orden real del DOM: orientación → aprender → radar de estilos → lugares →
ranking → prioridades → rutas → hoja de campo → decodificador de edición →
brief. La barra de navegación, en cambio, ofrece: inicio → preparación → ruta →
escenas → aprender → campo → brief.

| Criterio | Nota | Motivo |
|---|---|---|
| Carga cognitiva | 3 | Enseña antes de pedir ranking, pero la navegación contradice el orden y obliga a reconstruir el mapa mental. |
| Descubrimiento | 2 | «Preparación» y «Escenas» no dicen nada a quien nunca ha competido; la orientación y el radar de estilos no están en la navegación. |
| Práctica | 4 | Cada lección trae observar → probar → diagnosticar → cuándo romperla. |
| Recuperación | 3 | Los labs piden predecir, pero nada obliga a recordar después. |
| Transferencia | 4 | La hoja de campo y las rutas cierran el ciclo. |

**Defecto estructural confirmado:** el `nav` está escrito a mano
(`scripts/generate_architecture_pages.py:344`) mientras el orden visible lo fija
`reorder_story()` (`:313`). Son dos fuentes de verdad y ya divergieron.

## Las diez alternativas

### A1 · Tarea primero
Entra por «hoy salgo a fotografiar»: la página abre con la salida y cada
concepto aparece cuando la tarea lo exige.
**5 / 4 / 5 / 3 / 5.** Es el principio de tarea completa de Merrill: el
aprendizaje ocurre al abordar un problema real, no subhabilidades sueltas.
*Rechazo del experto:* sin ninguna demostración previa, un principiante absoluto
se queda sin ejemplo resuelto y la carga se dispara —el efecto del ejemplo
resuelto exige mostrar antes de pedir.

### A2 · Pregunta primero
Todo cuelga de la pregunta anti-postal: «¿qué ha fotografiado ya todo el mundo
aquí y qué relación sólo aparece si cambio hora, posición, focal o presencia
humana?».
**2 / 3 / 4 / 5 / 4.** Excelente para recuperación.
*Rechazo:* es descubrimiento puro. Para el novato la pregunta no tiene asideros
y la carga extrínseca es máxima; funciona sólo cuando ya existe vocabulario.

### A3 · Ciclo de Merrill por técnica
Cada familia técnica se convierte en un ciclo cerrado: problema → activación →
demostración → aplicación → integración.
**4 / 4 / 5 / 4 / 5.**
*Rechazo:* aplicado a las nueve familias produce nueve ciclos completos y una
página muy larga; sin una columna vertebral que las ordene, el usuario no sabe
por dónde empezar.

### A4 · Secuencia de Gagné
Los nueve eventos de instrucción aplicados a la página entera: captar atención,
objetivo, recuerdo previo, presentar, guiar, provocar ejecución, feedback,
evaluar, favorecer retención.
**4 / 3 / 4 / 4 / 3.**
*Rechazo:* es un guion lineal de aula. La página se usa de pie y a mitad de una
salida; obligar a atravesar nueve eventos para llegar a la ruta es hostil al
contexto real de uso.

### A5 · Cadena diagnóstica de fallos
Se entra por el síntoma: «mi edificio sale torcido», «sale plano», «no está
nítido», y desde ahí a la causa y a la técnica.
**5 / 5 / 4 / 4 / 4.**
*Rechazo:* como flujo único deja fuera a quien todavía no tiene fotos que
diagnosticar. Es una entrada excelente, no un currículo.

### A6 · Itinerario por lugar
El distrito y la ruta son el índice; la técnica aparece en la parada donde hace
falta.
**4 / 4 / 4 / 2 / 5.**
*Rechazo:* ata el aprendizaje a las rutas capturadas. Quien no está en Lima, o
sale de otra ruta, pierde el temario; y la teoría queda fragmentada en trozos
imposibles de repasar.

### A7 · Taller por restricción
Una restricción por sesión: una sola focal, una sola hora, un metro cuadrado.
**4 / 3 / 5 / 3 / 4.**
*Rechazo:* enseña disciplina pero no cubre el temario exigido por G05
(exposición, ISO, nitidez, campo, profundidad, luz, bordes, gesto, garúa). Es un
ejercicio complementario, no una estructura.

### A8 · Currículo en espiral
Tres vueltas al mismo temario con profundidad creciente.
**3 / 2 / 4 / 5 / 4.**
*Rechazo:* triplica el volumen de texto y en una sola página produce repetición
percibida como relleno. Además choca con el efecto de reversión por pericia: la
tercera vuelta estorba a quien ya domina la primera.

### A9 · Ruta por dificultad
Principiante → intermedio → avanzado, con puertas explícitas.
**4 / 3 / 3 / 3 / 3.**
*Rechazo:* obliga al usuario a autoclasificarse antes de tener criterio para
hacerlo, y las etiquetas de nivel desalientan a quien más las necesita.

### A10 · Decodificador inverso
Se parte de una fotografía terminada y se desmonta hacia las decisiones que la
produjeron.
**3 / 4 / 3 / 5 / 4.**
*Rechazo:* requiere un corpus de fotografías propias que se puedan mostrar. Sin
derechos sobre imágenes reales, el decodificador se quedaría en diagramas y
perdería justamente lo que lo hace valioso. I03 lo impide.

## Decisión

Gana una combinación con jerarquía explícita, no una alternativa aislada:

> **Columna vertebral A1 (tarea primero), con entrada diagnóstica A5 y estructura
> A3 dentro de cada técnica.**

El orden público se mantiene —orientación → aprender → explorar → preparar →
rutas → campo → decodificar— porque ya respeta demostración antes de aplicación,
que es lo que la carga cognitiva exige para un novato. Lo que cambia es el
andamiaje que hoy falta:

1. **La navegación pasa a derivarse del orden real del DOM.** Una sola fuente de
   verdad; se acaba la contradicción entre `nav` y `reorder_story()`.
2. **Etiquetas que dicen qué se hace, no cómo se llama el módulo:** «Cómo usar
   esta guía», «Aprender», «Lugares», «Comparar», «Rutas», «En campo», «Revelado»,
   «Bases». Necesidad primero, jerga después (GOV.UK).
3. **Entrada diagnóstica en la wiki (A5):** un índice de síntomas —torcido,
   plano, sucio de bordes, movido, quemado— que lleva a la familia técnica y a su
   lab. Es el camino de quien llega con una foto fallida, hoy inexistente.
4. **Cada técnica de la wiki como ciclo A3:** mecanismo → diagrama → qué probar →
   qué observar → cuándo romperla → lab interactivo → evidencia en video.
5. **La ruta de aprendizaje se deriva del dato** `learning_path` en lugar de estar
   traducida a mano en el generador.

## Lo que no se implementa y por qué

Nueve de las diez alternativas quedan documentadas, no construidas. Construir
diez flujos simultáneos multiplicaría el texto y la superficie de prueba sin
evidencia de que ninguno supere al ganador; el propio criterio de carga
cognitiva lo desaconseja. Este documento es la comparación pedida y la base para
revisar la decisión cuando haya datos de uso real.
