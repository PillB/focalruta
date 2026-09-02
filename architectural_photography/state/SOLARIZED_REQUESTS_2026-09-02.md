# Solicitudes solarizadas y preejecutadas

El catálogo de skills no expone Solarize en esta sesión. Se aplicó su objetivo operativo directamente: convertir cada petición en alcance, salida comprobable, límites y prueba antes de editar.

## 1. Wiki de técnicas desde videos

**Prompt ejecutable:** «Construye una wiki pública en español a partir del ledger de videos y la investigación relacionada. Usa solo metadatos y transcripciones legítimamente capturadas; enlaza cada afirmación a su timestamp; no publiques transcripciones privadas ni inventes atribuciones. Cada técnica debe incluir observar → probar → diagnosticar → cuándo romper la regla → transferencia al campo.»

**Preejecución:** completada en `wiki-tecnicas.html`, ledger y tests de procedencia.

## 2. Corrección de física visual

**Prompt ejecutable:** «Audita cada diagrama con óptica de cámara estenopeica, punto de fuga, Lambert, penumbra dependiente del tamaño de fuente y señales de material. Haz que cada estado cambie geometría visible, explica límites de calibración y prueba teclado, reset y reducción de movimiento.»

**Preejecución:** completada y desplegada; cinco labs tienen modelos/atributos, sombras, gradientes, reflejo/halo etiquetados y QA live 70/70.

## 3. Revisión de estilo anti-IA

**Prompt ejecutable:** «Reescribe la capa pública con verbos concretos, ejemplos situados, punto primero, ritmo variado y sin preámbulos grandilocuentes. Conserva nombres propios, URLs y evidencia. Define cada término antes de usarlo y deja una acción y un plan B.»

**Preejecución:** aplicada a orientación, planes, mapas, wiki y challenge; benchmark registrado en `research/editorial_usability_review_2026-09-02.md`.

## 4. Cinco pasadas editoriales/usabilidad

**Prompt ejecutable:** «Revisa home, planes, field card, challenge, wiki, iPhone, mapas offline y no-JS en cinco pasadas: orden, ELI5, causa/evidencia, interacción/accesibilidad y móvil/offline/paridad. Añade una prueba RED independiente por contrato y evidencia GREEN.»

**Preejecución:** completada; `test_whole_site_eli5.py` y suite completa (148) en verde; navegador seis viewports y PWA offline/no-JS en verde.

## 5. Diez alternativas de flujo óptimo

**Prompt ejecutable:** «Propón diez flujos alternativos para principiante, compara carga cognitiva, descubrimiento, práctica, recuperación y transferencia, y elige uno con evidencia de GOV.UK, NN/g, WCAG y aprendizaje activo. No cambies anclas compatibles ni ocultes el contexto esencial.»

**Preejecución:** la alternativa elegida quedó implementada como `orientación → aprender → practicar → explorar → preparar → campo → decodificar`; las otras nueve quedan documentadas como opciones de diseño para una siguiente ronda, no como funcionalidades fingidas.

## 6. Revisión/rearquitectura extrema del sitio completo

**Prompt ejecutable:** «Inspecciona el grafo completo de rutas y fuentes generadoras; corrige en la fuente, regenera hosted/standalone/offline, pasa privacidad, arquitectura, release, complejidad, seis viewports, foco, teclado, reduced-motion, overflow, recursos y live parity. Publica solo con CI y Pages verdes.»

**Preejecución:** completada para la ronda actual; PR #13 fusionado, Pages verde, live QA 70/70 y paridad byte exacta del challenge.

## Límites explícitos

No se copiaron imágenes externas, no se publicaron chats/transcripciones privadas y no se presentó una simulación pedagógica como render calibrado. Las solicitudes 1–4 y 6 están ejecutadas; la comparación extensa de diez alternativas es un artefacto de arquitectura para decidir la siguiente iteración, no una afirmación de que se implementaron diez sitios distintos.
