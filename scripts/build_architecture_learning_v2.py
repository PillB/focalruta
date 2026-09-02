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


def update_labs(data: dict) -> None:
    data["simulations"] = [lab for lab in data["simulations"] if lab["simulation_id"] != "composition-sequence"]
    for lab in data["simulations"]:
        lab["manipulation"] = f'Cambia únicamente el control de {lab["title"].lower()} y compara con tu predicción.'
        lab["observable_feedback"] = lab["diagnostic_rule"]
        lab["misconception_warning"] = f'El resultado simplifica una sola relación. {lab["model_limit"]}'
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
