#!/usr/bin/env python3
"""Fail-closed geographic admission for Arquitectura en Foco candidates."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "architecture" / "geography.json"


def normalize_district(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip())
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def classify_candidate(district: str) -> str:
    if not district or not district.strip():
        return "QUARANTINE_UNRESOLVED_DISTRICT"
    policy = load_policy()
    value = normalize_district(district)
    priority = {normalize_district(item) for item in policy["priority_districts"]}
    eligible = {normalize_district(item) for item in policy["eligible_districts"]}
    if value in priority:
        return "ELIGIBLE_PRIORITY"
    if value in eligible:
        return "ELIGIBLE_METROPOLITAN"
    return policy["outside_scope_action"]
