#!/usr/bin/env python3
"""Derive the verifiable half of the state file from the repository itself.

`CURRENT_STATE.json` is read by no script and no test, so every claim in it was
narrative — including precise-sounding numbers like "66 stops, 25 layers,
41 legs, 1058 audited vertices" that appeared in no assertion anywhere. Claims
that can be measured are now measured here and checked by
`tests/architecture/test_state_snapshot.py`; history that cannot be measured
stays, but is marked as narrative so nobody mistakes it for evidence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "architectural_photography/state/CURRENT_STATE.json"
ROUTES = ROOT / "data/architecture/routes.json"
LEARNING = ROOT / "data/architecture/learning.json"
AUDIT = ROOT / "architectural_photography/routes/geometry_containment_audit.json"
CANDIDATES = ROOT / "data/architecture/candidates.json"
WIKI = ROOT / "challenges/arquitectura-en-foco/wiki-tecnicas.html"
CHALLENGE = ROOT / "challenges/arquitectura-en-foco/index.html"
QA_REPORTS = ("CURRENT_BROWSER_QA.json", "OPTICS_ACCESSIBILITY_QA.json", "VISUAL_RESOURCE_QA.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _route_facts() -> dict:
    routes = _load(ROUTES)
    layers = routes["district_layers"]
    return {
        "route_layers": len(layers),
        "route_stops": sum(len(layer["stops"]) for layer in layers),
        "route_legs": sum(len(layer["legs"]) for layer in layers),
        "route_singletons": sum(1 for layer in layers if len(layer["stops"]) == 1),
        "route_districts": len({layer["district"] for layer in layers}),
        "route_generated_at": routes["generated_at"],
        "omitted_intertour_transfers": len(routes.get("omitted_intertour_transfers", [])),
    }


def _geometry_facts() -> dict:
    audit = _load(AUDIT)
    return {
        "audited_route_layers": len(audit["layers"]),
        "audited_vertices": sum(row["checked_vertices"] for row in audit["layers"]),
        "vertices_outside_district": sum(row["outside_vertices"] for row in audit["layers"]),
        "audit_matches_route_run": audit.get("audited_route_run") == _load(ROUTES)["generated_at"],
    }


def _learning_facts() -> dict:
    learning = _load(LEARNING)
    wiki = WIKI.read_text(encoding="utf-8")
    challenge = CHALLENGE.read_text(encoding="utf-8")
    return {
        "interactive_labs": len(learning["simulations"]),
        "technique_families": len(learning["technique_cards"]),
        "field_lessons": len(learning["lessons"]),
        "wiki_technique_articles": wiki.count('class="wiki-technique"'),
        "published_labs": challenge.count('class="learning-lab"'),
        "canonical_candidates": len(_load(CANDIDATES)),
    }


def _evidence_facts() -> dict:
    facts = {}
    for name in QA_REPORTS:
        report = _load(ROOT / name)
        key = name.replace(".json", "").lower()
        facts[f"{key}_checks"] = report.get("checks")
        facts[f"{key}_passed"] = report.get("passed")
    return facts


def measure() -> dict:
    """Every claim here is read from an artefact, never typed by hand."""
    facts: dict = {}
    for part in (_route_facts(), _geometry_facts(), _learning_facts(), _evidence_facts()):
        facts.update(part)
    return dict(sorted(facts.items()))


def main() -> None:
    state = _load(STATE) if STATE.is_file() else {}
    narrative = state.get("narrative") or {
        key: value for key, value in state.items() if key not in {"measured", "narrative"}
    }
    narrative["evidence_status"] = (
        "Narrativa de ronda: decisiones, defectos corregidos e identificadores externos. "
        "No es evidencia comprobable; lo medible vive en el bloque «measured», generado por "
        "scripts/build_state_snapshot.py y verificado por tests/architecture/test_state_snapshot.py."
    )
    # No wall-clock stamp: this file is regenerated on every CI run and compared
    # with `git diff --exit-code`, so a timestamp would make it differ every time
    # and turn the staleness gate into noise. Provenance lives in the measured
    # facts (route_generated_at) and in git history.
    payload = {
        "schema_version": "2.0.0",
        "measured": measure(),
        "narrative": dict(sorted(narrative.items())),
    }
    temporary = STATE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, STATE)
    print(f"measured {len(payload['measured'])} facts; {len(payload['narrative'])} narrative keys retained")


if __name__ == "__main__":
    main()
