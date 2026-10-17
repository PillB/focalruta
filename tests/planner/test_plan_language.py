"""What the plan cards say agrees with what they compute, in Spanish.

Requirements: U06 (a note names the light its slot is scored against) and U07
(reader-facing plan text is Spanish: no leftover English photo jargon, and a
space between a number and its unit). Both come from the red team's review of
PR #19: sixteen morning notes said "a pleno sol" on slots scored as hazy sun
(EV 14, one stop under full sun), and eleven English terms survived the
translation.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANS_JSON = ROOT / "data" / "plans.json"

FULL_SUN = re.compile(r"\bpleno (?:sol|día)\b", re.I)
ENGLISH = re.compile(
    r"\b(?:DoF|rim light|prep|shutter|stops?|burst|foreground|background|panning|WB|full[- ]frame)\b|pie de foto",
    re.I,
)
# "3s", "20s:" or "4s —" instead of "3 s"; durations such as 1/125 are written without a unit here.
UNSPACED_SECONDS = re.compile(r"(?<![\w/])\d+(?:[.,]\d+)?s\b")
AGREEMENT = re.compile(r"\bestelas luminosos\b")
# Keys whose values are identifiers or the English half of a bilingual label.
NOT_READER_TEXT = {"en", "icon", "id", "technique", "composition", "angle", "pose", "scene", "lens", "shutter"}


def load():
    return json.loads(PLANS_JSON.read_text(encoding="utf-8"))


def reader_text(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            if key not in NOT_READER_TEXT:
                yield from reader_text(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from reader_text(value, f"{path}[{index}]")
    elif isinstance(node, str):
        yield path, node


def test_u06_notes_name_the_light_their_slot_is_scored_against():
    wrong = [
        f"{shot['id']} {time}: scored as {slot['scene']} but says '{FULL_SUN.search(slot['notes']).group(0)}'"
        for plan in load()["plans"] for shot in plan["shots"]
        for time, slot in shot["settings_by_time"].items()
        if FULL_SUN.search(slot.get("notes", "")) and slot.get("scene") != "sol_pleno"
    ]
    assert not wrong, wrong


def test_u07_reader_text_has_no_english_photo_jargon():
    hits = [f"{path}: {match.group(0)}" for path, text in reader_text(load())
            for match in ENGLISH.finditer(text)]
    assert not hits, hits


def test_u07_numbers_and_seconds_are_spaced_and_adjectives_agree():
    hits = [f"{path}: {match.group(0)}" for path, text in reader_text(load())
            for pattern in (UNSPACED_SECONDS, AGREEMENT) for match in pattern.finditer(text)]
    assert not hits, hits
