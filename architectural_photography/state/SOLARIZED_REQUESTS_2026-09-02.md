# Las seis solicitudes, con su estado real

Actualizado el 2026-09-02 tras la ronda 7. La versión anterior de este documento
daba por cerradas cinco de las seis solicitudes; la inspección del código
generado demostró que tres de esos cierres eran falsos. Aquí queda el estado
comprobable, con la evidencia que lo sostiene.

## 1. Wiki de técnicas desde los videos

**Pedido.** Una wiki pública en español construida desde el registro de videos y
la investigación relacionada, con cada afirmación atada a su marca de tiempo.

**Estado anterior.** Declarado completo. En realidad las nueve familias técnicas
compartían **un único diagrama**, byte a byte, y la página tenía dos anclas para
nueve secciones.

**Ahora.** `wiki-tecnicas.html` tiene nueve diagramas propios derivados de la
geometría, ancla estable por familia, un índice que abre por síntoma, una
referencia de física con la fuente de cada fórmula y las 18 afirmaciones con
marca de tiempo agrupadas por video. Los 24 videos sin subtítulos verificables
siguen marcados «Transcripción no disponible» y no se les atribuye enseñanza.

**Prueba.** `test_each_technique_family_has_its_own_diagram`,
`test_each_technique_family_is_directly_linkable`,
`test_wiki_offers_a_symptom_entry_point_into_the_techniques`,
`test_video_technique_wiki_is_evidence_linked_and_offline_ready`.

## 2. Física de las visualizaciones

**Pedido.** Que perspectiva, escala, luz, sombras, reflejos y halos sean fieles a
la física aunque el estilo sea simplificado.

**Estado anterior.** Declarado completo y desplegado. En realidad el campo de
visión se **abría** al alargar la focal, el punto de fuga se movía en sentido
contrario al real, las sombras eran polígonos escritos a mano y el halo, el
brillo y el reflejo no los tocaba ningún script.

**Ahora.** `scripts/optics_physics.py` es la única definición de la óptica del
proyecto y la comparten los generadores de diagramas. Todo lo que dibuja la
página lo calculó antes Python: campo de visión `atan(d/2f)`, proyección
estenopeica, punto de fuga proyectivo, esquinas bajo inclinación, Lambert
`cos θ`, sombra `h/tan(altura)`, penumbra por tamaño angular, Schlick con
relación de luminancias, profundidad de campo, desenfoque de movimiento,
perspectiva aérea, halo por exposición y escalera de ISO.

**Prueba.** 16 invariantes en `test_optics_physics.py` y 22 medidos sobre la
página real en los seis viewports requeridos.

## 3. Estilo de escritura

**Pedido.** Texto claro, con contexto inmediato para cada término y sin jerga
suelta, siguiendo la investigación sobre escritura que no suene automática.

**Ahora.** Aplicado a la orientación, los nueve laboratorios, la wiki, el bloque
sin JavaScript y los mapas offline. Las etiquetas de navegación dicen qué se
hace —«Comparar», «Rutas», «En campo»— en vez de nombrar módulos internos. Se
eliminó la duplicación entre «Cuidado» y «Límite del modelo», que repetían la
misma frase en cinco laboratorios.

**Prueba.** `test_whole_site_eli5.py`, `test_physics_copy_rejects_fake_lens_magic_and_unbounded_effects`.

## 4. Cinco pasadas editoriales y de usabilidad

**Ahora.** Repetidas sobre el material corregido y registradas en
`research/editorial_usability_review_2026-09-02.md`. Encontraron y corrigieron
dos colisiones de identificador que rompían `getElementById`, nueve archivos de
mapa publicados que ninguna ruta enlazaba y un bloque sin JavaScript que cubría
cinco laboratorios de nueve.

## 5. Diez alternativas de flujo pedagógico

**Estado anterior.** No existía la comparación; sólo una nota diciendo que las
otras nueve quedaban «documentadas».

**Ahora.** `research/pedagogical_flow_alternatives_2026-09-02.md` compara diez
alternativas contra carga cognitiva, descubrimiento, práctica, recuperación y
transferencia, cita la referencia que sostiene cada juicio y dice por qué un
experto rechazaría cada alternativa perdedora. Gana una combinación: columna
vertebral de tarea completa, entrada por síntoma y ciclo de Merrill dentro de
cada técnica. Lo implementado es el ganador; las otras nueve quedan como
opciones de diseño, no como funcionalidades fingidas.

## 6. Revisión y rearquitectura del sitio completo

**Ahora.** `build_challenge_page()` unifica el pipeline que estaba duplicado
entre el generador y el verificador —eran dos fuentes de verdad para la misma
página—. La navegación se deriva del mismo orden que fija `reorder_story()`, así
que ya no puede contradecir lo que el lector recorre. Local, hospedado,
standalone y offline se regeneraron y quedan en paridad.

## Límites que se mantienen

No se copiaron imágenes externas, no se publicaron chats ni transcripciones
privadas, y ninguna simulación se presenta como render calibrado: los
laboratorios predicen dirección y orden de magnitud, no píxeles. Las rutas no se
recalcularon en esta ronda porque el router externo falló y el contrato obliga a
detenerse tras el primer fallo confirmado de disponibilidad.
