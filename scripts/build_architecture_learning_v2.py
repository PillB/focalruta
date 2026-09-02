#!/usr/bin/env python3
"""Build the evergreen, evidence-bounded architecture learning curriculum."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEARNING = ROOT / "data" / "architecture" / "learning.json"
LEDGER = ROOT / "architectural_photography" / "research" / "videos" / "VIDEO_LEDGER.json"

NIKON_PC = "https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/the-pc-lens-advantage-what-you-see-is-what-youll-get"
NIKON_COMPOSITION = "https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/5-easy-composition-guidelines"
GESTALT = "https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/"

# Public order of the interactive labs, one per technique family.
LAB_ORDER = [
    "perspective-position", "vertical-convergence", "hierarchy-edges",
    "negative-space-edges", "depth-layers", "composition-sequence",
    "light-material", "exposure-triangle", "reflection-glare",
]

TECHNIQUES = [
    ("viewpoint-before-focal", "Punto de vista antes que focal", "La posición decide perspectiva, solapes y fondo; la focal recorta el campo desde esa posición.", "Marca tres posiciones legales y compara relaciones antes de montar 35, 50 u 85 mm.", "Si cerca/lejos cambia, cambió la posición; si todo escala junto, cambió el campo de visión.", "Un 85 mm no comprime por magia: normalmente te obliga a alejarte.", [NIKON_PC]),
    ("perspective-shift-tilt", "Perspectiva, convergencia y desplazamiento", "Nivelar el sensor conserva verticales; inclinarlo produce convergencia. El desplazamiento reencuadra sin inclinar.", "Haz nivelada, inclinada y nivelada desde más altura; decide cuál expresa mejor el edificio.", "Distingue convergencia intencional de una corrección que recorta información útil.", "Enderezar no es siempre correcto y un diagrama no sustituye una óptica PC calibrada.", [NIKON_PC]),
    ("lines-symmetry-hierarchy", "Líneas, simetría y jerarquía", "Dirección, contraste, repetición y aislamiento ordenan la primera, segunda y tercera lectura.", "Traza la línea dominante y comprueba si llega al sujeto o expulsa la mirada.", "Si todos los elementos pesan igual, cambia posición, espera o elimina del borde.", "Simetría y tercios son herramientas, no pruebas de una composición lograda.", [NIKON_COMPOSITION, GESTALT]),
    ("negative-space-edge-control", "Espacio negativo y control de bordes", "El vacío separa figura y fondo; los bordes determinan si la mirada permanece dentro.", "Haz un barrido de cuatro bordes y una versión con más vacío sin recortar después.", "Busca tangencias, objetos de alto contraste y formas que compitan con el sujeto.", "Vacío no significa limpieza decorativa: debe sostener escala, espera o tensión.", [NIKON_COMPOSITION, GESTALT]),
    ("depth-figure-ground", "Capas, profundidad y figura-fondo", "Oclusión, escala, contraste y continuidad separan planos y hacen legible la relación espacial.", "Construye primer plano, dispositivo, acción y fondo; luego quita una capa.", "Si persona y borde se fusionan, espera o desplázate lateralmente.", "Abrir diafragma no repara un fondo con forma o brillo contradictorios.", [GESTALT]),
    ("gesture-absence", "Gesto decisivo y ausencia significativa", "Una persona importa cuando su verbo revela el diseño; la ausencia importa cuando quedan uso, espera o residuo.", "Precompón una versión con verbo y otra vacía con evidencia social.", "Descarta la figura que solo aporta escala y el vacío que solo aporta pulcritud.", "No escenifiques, invadas privacidad ni fuerces presencia humana.", [GESTALT]),
    ("light-material-weather", "Luz, material, reflejos y clima", "Dirección, tamaño y color de la fuente revelan relieve, volumen, transparencia y reflexión.", "Repite posición con lateral, mediodía, garúa y hora azul; registra qué relación aparece.", "Protege altas luces y separa atmósfera útil de arquitectura ilegible.", "Hora dorada no es universalmente mejor; el clima debe explicar la forma.", [NIKON_COMPOSITION]),
    ("exposure-focus-iso-motion", "Exposición, foco, ISO y movimiento", "Obturador, apertura e ISO responden a gesto, profundidad y altas luces; la nitidez tiene varias causas.", "Fija primero movimiento y PDC; diagnostica foco, trepidación, sujeto, óptica y atmósfera por separado.", "Cambia una sola causa y revisa histograma, alerta y ampliación crítica.", "No existe ISO mágico ni un único obturador que cure toda falta de nitidez.", [NIKON_COMPOSITION]),
    ("contest-safe-editing", "Edición compatible con cada convocatoria", "Captura, revelado, composición/eliminación y generación son categorías distintas que cada brief puede permitir o prohibir.", "Antes de editar, convierte las reglas vigentes en una lista de operaciones permitidas y dudosas.", "Si una operación cambia contenido o geometría material, detente y consulta la regla o al organizador.", "No generalices las fronteras de un concurso antiguo ni supongas que IA o relleno generativo están permitidos.", [NIKON_COMPOSITION]),
]


LEGACY_LAB_COPY = {
    "perspective-position": {
        "misconception_warning": "Un 85 mm no comprime por arte de magia. Comprime porque, para conservar el tamaño del sujeto, te obliga a retroceder: es el paso atrás lo que junta los planos.",
        "model_limit": "Calcula la proyección estenopeica sobre un sensor de 36 mm. No modela distorsión, viñeteo ni el rendimiento de un objetivo concreto.",
    },
    "vertical-convergence": {
        "misconception_warning": "Enderezar no siempre es lo correcto: la convergencia puede expresar altura. Y corregirla después recorta información que quizá necesitabas.",
        "model_limit": "Proyecta las cuatro esquinas de una fachada de 12 m a 26 m con un 35 mm. No sustituye una óptica descentrable ni predice cuánto recortará tu corrección.",
    },
    "hierarchy-edges": {
        "misconception_warning": "La simetría y los tercios son herramientas, no pruebas de que la composición funcione. Si todo pesa igual, el problema es la posición, no la rejilla.",
        "model_limit": "Modela atención y competencia de bordes, no física. El orden de lectura real depende de la escena y de quien mira.",
    },
    "light-material": {
        "misconception_warning": "La hora dorada no es universalmente mejor. Lo que decide es si esa luz explica la forma del edificio o sólo lo tiñe.",
        "model_limit": "Aplica cos θ, h/tan(altura solar) y el tamaño angular de la fuente. No predice exposición, color del cielo ni el comportamiento de un material concreto.",
    },
}


def technique_cards() -> list[dict]:
    keys = ("technique_id", "title", "mechanism", "field_test", "diagnosis", "misconception_warning", "sources")
    if any(len(row) != len(keys) for row in TECHNIQUES):
        raise ValueError("technique row does not match the public schema")
    return [dict(zip(keys, row)) for row in TECHNIQUES]


def exemplars() -> list[dict]:
    conditions = ("posición frontal / luz neutra", "posición oblicua / luz lateral", "distancia o clima alternativo")
    urls = (NIKON_PC, NIKON_COMPOSITION, GESTALT)
    rows = []
    for card in technique_cards():
        for index, condition in enumerate(conditions, 1):
            rows.append({
                "technique_id": card["technique_id"], "family_id": f'{card["technique_id"]}-{index}',
                "source_url": urls[index - 1], "author": "Nikon USA" if index < 3 else "Wagemans et al.",
                "date": "s. f." if index < 3 else "2012", "rights_status": "LINK_ONLY", "condition": condition,
                "proves": "Referencia para comparar una variable visual y formular una predicción de campo.",
                "cannot_prove": "No prueba que una escena, luz, acceso o resultado equivalente exista en Lima.",
            })
    return rows


NEW_LABS = [
    {
        "simulation_id": "negative-space-edges", "title": "Espacio negativo y disciplina de bordes",
        "prediction_prompt": "Predice qué borde expulsa la mirada antes de mover la cámara.",
        "manipulation": "Ajusta el margen alrededor del sujeto y mira qué contorno queda tangente al borde.",
        "observable_feedback": "El lab marca en rojo cada tangencia: dos contornos que casi se tocan y compiten.",
        "diagnostic_rule": "Si un objeto toca el borde sin entrar del todo, decide: entra entero o sale entero.",
        "model_limit": "Mide distancias en el propio dibujo; no mide tu encuadre real ni la distorsión de tu óptica.",
        "field_drill": "Haz un barrido de los cuatro bordes antes de disparar y repite la toma con más vacío.",
        "misconception_warning": "Más vacío no es mejor por sí solo: el vacío debe sostener escala, espera o tensión.",
        "sources": [NIKON_COMPOSITION, GESTALT],
    },
    {
        "simulation_id": "depth-layers", "title": "Capas, profundidad y perspectiva aérea",
        "prediction_prompt": "Predice qué capa desaparece primero cuando la bruma aumenta.",
        "manipulation": "Mueve la distancia de cada plano y la bruma; observa contraste y solape.",
        "observable_feedback": "El contraste de cada plano cae con la distancia según exp(−bruma·d/200 m) y los solapes se reordenan.",
        "diagnostic_rule": "Si dos planos tienen el mismo contraste, no hay profundidad: busca solape o cambia la hora.",
        "model_limit": "Modela la caída de contraste atmosférica, no la dispersión espectral real de la garúa limeña.",
        "field_drill": "Construye primer plano, dispositivo, acción y fondo; luego quita una capa y compara.",
        "misconception_warning": "Abrir el diafragma no repara un fondo con forma o brillo contradictorios.",
        "sources": [GESTALT, NIKON_COMPOSITION],
    },
    {
        "simulation_id": "exposure-triangle", "title": "Obturación, diafragma, ISO y nitidez",
        "prediction_prompt": "Predice qué se rompe primero si bajas dos pasos de obturación.",
        "manipulation": "Cambia un vértice del triángulo; el lab compensa el resto para mantener la misma exposición.",
        "observable_feedback": "El desenfoque de movimiento crece con el tiempo de exposición, la zona nítida con el número f y el ruido con la raíz del ISO.",
        "diagnostic_rule": "Fija primero el movimiento que quieres congelar y la profundidad que necesitas; el ISO es la consecuencia.",
        "model_limit": "Usa un círculo de confusión de 0,030 mm y una velocidad de paso típica; no predice el ruido de tu sensor.",
        "field_drill": "Fija movimiento y profundidad, deja subir el ISO y compara al 100 % antes de juzgar.",
        "misconception_warning": "No existe un ISO mágico ni un obturador único que cure toda falta de nitidez.",
        "sources": [NIKON_COMPOSITION],
    },
    {
        "simulation_id": "reflection-glare", "title": "Reflejos, brillo y halo",
        "prediction_prompt": "Predice si acercarte al vidrio de frente aumenta o reduce el reflejo.",
        "manipulation": "Cambia el ángulo con el que miras el vidrio y la exposición.",
        "observable_feedback": "El porcentaje reflejado sigue Schlick: 4 % de frente y casi 100 % en ángulo rasante; el halo se contrae al cerrar pasos.",
        "diagnostic_rule": "Si el reflejo tapa el interior, camina hacia un ángulo más frontal antes de tocar la cámara.",
        "model_limit": "Aproximación de Schlick para vidrio (n≈1,5); no modela recubrimientos, polarizadores ni vidrio tintado.",
        "field_drill": "Rodea una fachada vidriada y anota en qué ángulo el interior se vuelve legible.",
        "misconception_warning": "Un polarizador no elimina el reflejo en cualquier ángulo: depende de la geometría.",
        "sources": [NIKON_COMPOSITION, NIKON_PC],
    },
]


def update_labs(data: dict) -> None:
    generated = {"composition-sequence", *(lab["simulation_id"] for lab in NEW_LABS)}
    data["simulations"] = [lab for lab in data["simulations"] if lab["simulation_id"] not in generated]
    for lab in data["simulations"]:
        lab["manipulation"] = f'Cambia únicamente el control de {lab["title"].lower()} y compara con tu predicción.'
        lab["observable_feedback"] = lab["diagnostic_rule"]
        lab["misconception_warning"] = LEGACY_LAB_COPY[lab["simulation_id"]]["misconception_warning"]
        lab["model_limit"] = LEGACY_LAB_COPY[lab["simulation_id"]]["model_limit"]
    data["simulations"].append({
        "simulation_id": "composition-sequence", "title": "Una escena, cinco decisiones",
        "prediction_prompt": "Predice qué cambio transforma el significado, no solo el aspecto.",
        "manipulation": "Recorre cinco variantes manteniendo explícito qué variable cambia.",
        "observable_feedback": "Compara relación espacial, jerarquía, uso y legibilidad de luz en cada estado.",
        "diagnostic_rule": "Aísla una variable por toma y conserva el estado que cambia la lectura, no solo el acabado.",
        "model_limit": "Viñetas SVG abstractas; no representan un edificio, óptica, clima ni persona reales.",
        "field_drill": "Haz la secuencia sin borrar fallos: postal, posición, focal fija, presencia/ausencia y otra condición de luz.",
        "misconception_warning": "Cambiar varias variables a la vez impide saber qué mejoró la imagen.",
        "sources": [NIKON_PC, NIKON_COMPOSITION, GESTALT],
        "variants": [
            {"variant_id": "default-postcard", "label": "Postal por defecto"},
            {"variant_id": "changed-position", "label": "Cambia posición"},
            {"variant_id": "fixed-position-focal", "label": "Focal, posición fija"},
            {"variant_id": "human-presence", "label": "Presencia / ausencia"},
            {"variant_id": "light-weather", "label": "Luz / clima"},
        ],
    })
    data["simulations"].extend(json.loads(json.dumps(NEW_LABS)))
    data["simulations"].sort(key=lambda lab: LAB_ORDER.index(lab["simulation_id"]))


def validated_claims(learning: dict) -> dict[str, list[dict]]:
    claims: dict[str, list[dict]] = {}
    for lesson in learning["lessons"]:
        for source in lesson["sources"]:
            if source["type"] == "VIDEO_TRANSCRIPT":
                claims.setdefault(source["video_id"], []).append({
                    "timestamp_seconds": source["timestamp_seconds"],
                    "claim": lesson["observe"], "evidence_status": "TRANSCRIPT_VALIDATED",
                })
    for module in learning["video_modules"]:
        claims.setdefault(module["video_id"], []).append({
            "timestamp_seconds": module["timestamp_seconds"],
            "claim": module["mechanism"], "evidence_status": "TRANSCRIPT_VALIDATED",
        })
    return claims


def normalize_ledger(learning: dict) -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    claims = validated_claims(learning)
    for video in ledger["videos"]:
        captured = video.get("transcript_status") == "CAPTURED"
        source = video.get("transcript_provenance", {}).get("source")
        if captured and source not in {"YOUTUBE_CAPTION_TRACK", "SUPADATA_NATIVE_CAPTION"}:
            source = "YOUTUBE_CAPTION_TRACK"
        video["transcript_provenance"] = {"source": source or "UNAVAILABLE", "path": video.get("transcript_path")}
        if video.get("metadata_status", "").startswith("VERIFIED"):
            video["timestamped_claims"] = claims.get(video["video_id"], [])
            status = "CURRICULUM_TRANSFER_VALIDATED" if video["timestamped_claims"] else "CAPTION_CAPTURED_NO_PUBLIC_TRANSFER"
            video["curriculum_cross_validation"] = {"status": status, "agreements": [], "disagreements": []}
        else:
            video["timestamped_claims"] = []
            video["curriculum_cross_validation"] = {
                "status": "CAPTION_CAPTURED_ATTRIBUTION_BLOCKED", "agreements": [], "disagreements": [],
            }
        video.setdefault("tags", [])
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    data = json.loads(LEARNING.read_text(encoding="utf-8"))
    data["schema_version"] = "2.0.0"
    data["learning_path"] = ["SEE", "POSITION", "COMPOSE", "LIGHT", "WORK_THE_SCENE", "FINISH", "COMPETE"]
    data["technique_cards"] = technique_cards()
    data["visual_exemplar_families"] = exemplars()
    update_labs(data)
    LEARNING.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    normalize_ledger(data)


if __name__ == "__main__":
    main()
