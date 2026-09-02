# Revisión editorial y de usabilidad del sitio completo

Se revisaron `index.html`, las seis páginas de plan, la tarjeta de campo, el reto arquitectónico, la wiki, ayuda de iPhone, mapas offline, fallbacks sin JavaScript y la copia del build hospedado.

## Cinco pasadas aplicadas

1. **Estructura.** Cada entrada empieza con su propósito y el siguiente paso. El reto conserva sus anclas, pero enseña antes de pedir ranking o ruta.
2. **ELI5.** Cada control nuevo responde «qué significa», «qué hacer» y «si falla». La orientación del sitio define focal, PDC, ISO, histograma, KML y GeoJSON antes de usarlos.
3. **Causa y evidencia.** Las visualizaciones tienen nombre accesible y explicación cercana. Las tarjetas dicen qué comparar al 100% y qué observación confirma la hipótesis.
4. **Interacción.** Se mantuvieron controles nativos, foco visible, reset y `<details>` opcionales. La explicación esencial no depende de JavaScript ni de abrir un tooltip.
5. **Lectura real.** Se comprobó la copia en móvil, escritorio, offline y en la ruta alojada. Se acortaron instrucciones, se evitaron saltos de registro y se dejó el plan B junto a la acción.

## Reglas de estilo incorporadas

El artículo de Will Francis (13-03-2026) identifica señales frecuentes de texto artificial: vocabulario grandilocuente, contrastes prefabricados («no es X, es Y»), preámbulos vacíos, párrafos uniformes y exceso de guiones. Se adoptó su contramedida útil, no una lista ciega de palabras prohibidas: verbo concreto, ejemplo situado, punto primero y variación de ritmo. [Referencia](https://willfrancis.com/how-to-stop-claude-writing-like-an-ai/)

Se contrastó con [GOV.UK: principios de diseño](https://www.gov.uk/guidance/government-design-principles), [identificar necesidades](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/identify-user-needs/) y [principios de contenido](https://www.gov.uk/guidance/content-design/writing-for-user-needs): empezar por la necesidad, explicar relaciones al principio y quitar lo que no ayuda a decidir. Para opciones avanzadas se usa divulgación progresiva, siguiendo [Nielsen Norman Group](https://www.nngroup.com/articles/progressive-disclosure/).

## Rechazos de experto y límites

No se sustituyó evidencia de fuente por una voz «humana» inventada, ni se borraron nombres propios o URLs. Las citas y datos de procedencia siguen intactos; solo se reescribió la capa pública. Tampoco se presentó un SVG estilizado como fotografía real: el modelo visual conserva su límite declarado.

## Evidencia ejecutable

La cobertura está en `tests/architecture/test_whole_site_eli5.py`: orientación antes de controles, definiciones operativas, explicación cercana a cada SVG y plan de recuperación. La suite de arquitectura, los verificadores de arquitectura/release y las pruebas de navegador son la evidencia GREEN de las cinco pasadas.
