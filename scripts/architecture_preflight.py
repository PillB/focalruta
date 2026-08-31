#!/usr/bin/env python3
"""Read-only local submission preflight for Arquitectura en Foco 2026."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Mapping

from PIL import Image


MINIMUM_BYTES = 5_000_000
MAXIMUM_BYTES = 25_000_000
FILENAME_PATTERN = re.compile(r"^[^\W\d_]+(?:-[^\W\d_]+)+$", re.UNICODE)
REQUIRED_TEXT = ("title", "place", "capture_date", "description")


def inspect_image(path: Path) -> dict:
    details = {"path": str(path), "bytes": path.stat().st_size, "width_px": None, "height_px": None, "color_mode": None}
    try:
        with Image.open(path) as image:
            details.update(width_px=image.width, height_px=image.height, color_mode=image.mode)
    except (OSError, ValueError):
        pass
    return details


def file_violations(path: Path, details: Mapping) -> list[str]:
    violations = []
    if path.suffix.lower() not in {".jpg", ".jpeg"}:
        violations.append("INVALID_EXTENSION")
    if details["bytes"] < MINIMUM_BYTES:
        violations.append("FILE_TOO_SMALL")
    if details["bytes"] > MAXIMUM_BYTES:
        violations.append("FILE_TOO_LARGE")
    if not FILENAME_PATTERN.fullmatch(path.stem):
        violations.append("INVALID_FILENAME")
    if details["width_px"] is None:
        violations.append("UNREADABLE_IMAGE_METADATA")
    return violations


def metadata_violations(metadata: Mapping) -> list[str]:
    violations = []
    if int(metadata.get("capture_year", 0)) < 2020:
        violations.append("CAPTURE_BEFORE_2020")
    if any(not str(metadata.get(field, "")).strip() for field in REQUIRED_TEXT):
        violations.append("MISSING_FORM_METADATA")
    confirmations = {
        "backup_exists": "BACKUP_NOT_CONFIRMED",
        "allowed_edits_only": "EDITS_NOT_CONFIRMED",
        "no_fundamental_retouch": "RETOUCH_NOT_CONFIRMED",
        "no_ai_image_processing": "AI_NOT_CONFIRMED",
    }
    violations.extend(code for field, code in confirmations.items() if metadata.get(field) is not True)
    return violations


def evaluate_submission(paths: Iterable[Path], metadata: Mapping) -> dict:
    selected = [Path(path) for path in paths]
    violations = []
    details = None
    if len(selected) != 1:
        violations.append("EXACTLY_ONE_FILE")
    else:
        details = inspect_image(selected[0])
        violations.extend(file_violations(selected[0], details))
    violations.extend(metadata_violations(metadata))
    return {"eligible": not violations, "violations": violations, "file": details, "mutated": False}
