#!/usr/bin/env python3
"""Fail-closed static release gate for the architecture challenge."""

from __future__ import annotations

import json
from pathlib import Path

from generate_architecture_pages import (
    LEARNING_PATH,
    OUTPUT,
    PHOTOGRAPHERS_PATH,
    RULES_PATH,
    render,
    beginner_guide,
    reorder_story,
    PHYSICS_GUIDE,
)


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_MARKERS = ("2026-08-24-2026-08-26-architectural-photo-strategy", "Architectura_historical_log", "SYSTEM:", "DEVELOPER:")
PUBLIC_ROOTS = (ROOT / "challenges", ROOT / "data" / "architecture", ROOT / "dist")


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def public_files():
    for root in PUBLIC_ROOTS:
        if root.exists():
            yield from (path for path in root.rglob("*") if path.is_file() and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".zip"})


def main() -> int:
    failures = []
    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    learning = json.loads(LEARNING_PATH.read_text(encoding="utf-8"))
    photographers = json.loads(PHOTOGRAPHERS_PATH.read_text(encoding="utf-8"))
    expected = render(rules, learning, photographers).replace("Arquitectura<br>en foco", "Fotografía<br>arquitectónica")
    expected = expected.replace('<nav aria-label="Tareas del laboratorio">', beginner_guide() + '<nav aria-label="Tareas del laboratorio">', 1)
    expected = reorder_story(expected)
    expected = expected.replace('<section id="learn">', '<section id="learn">' + PHYSICS_GUIDE, 1)
    expected = expected.replace("<h3>Nueve familias técnicas</h3>", '<h3>Nueve familias técnicas</h3><p><a href="wiki-tecnicas.html">Abrir la wiki completa de técnicas, diagramas y evidencia de videos</a></p>', 1)
    for source, target in ((">STAY<", ">ME QUEDO<"), (">MOVE<", ">ME MUEVO<"), (">RETURN OTHER LIGHT<", ">VUELVO CON OTRA LUZ<"), ("TOP 5 DE CAMPO", "5 PRIORIDADES PARA COMPROBAR"), ("OFFLINE · GUARDADO LOCAL", "GUARDADO EN ESTE DISPOSITIVO"), ("EDICIÓN SEGÚN EL BRIEF", "EDICIÓN SEGÚN EL ENCARGO"), ("DECODIFICADOR DE BRIEF", "DECODIFICADOR DEL ENCARGO")):
        expected = expected.replace(source, target)
    check(OUTPUT.exists(), "generated challenge page missing", failures)
    check(OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == expected, "challenge page is stale; regenerate it", failures)
    check(rules["file"]["minimum_bytes"] == 5_000_000, "5 MB minimum missing", failures)
    check(rules["file"]["maximum_bytes"] == 25_000_000, "25 MB maximum missing", failures)
    for path in public_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        check(not any(marker in text for marker in PRIVATE_MARKERS), f"private marker in {path.relative_to(ROOT)}", failures)
    report = {"passed": not failures, "checks_failed": failures}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
