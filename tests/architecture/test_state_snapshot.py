"""Claims in the state file must be derived from reality, not typed from memory.

Requirements: Q01, Q03, M01, O03. Nothing in the repository reads
CURRENT_STATE.json, so every number in it — including 66 stops, 25 layers,
41 legs and 1058 audited vertices — was unverifiable narrative.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_state_snapshot as snapshot

STATE = ROOT / "architectural_photography/state/CURRENT_STATE.json"


def test_state_file_separates_measured_facts_from_narrative():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    assert "measured" in state, "verifiable claims must live in their own block"
    assert isinstance(state["measured"], dict) and state["measured"]
    assert "narrative" in state, "unverifiable history must be marked as such"


def test_measured_block_matches_what_the_repository_actually_contains():
    committed = json.loads(STATE.read_text(encoding="utf-8"))["measured"]
    derived = snapshot.measure()
    assert committed == derived, (
        "the state file disagrees with the repository; run scripts/build_state_snapshot.py\n"
        f"committed: {json.dumps(committed, sort_keys=True)}\n"
        f"derived:   {json.dumps(derived, sort_keys=True)}"
    )


def test_measured_values_are_read_from_artifacts_not_hardcoded():
    """Each measured key must move when its underlying artefact moves."""
    derived = snapshot.measure()
    routes = json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))
    assert derived["route_layers"] == len(routes["district_layers"])
    assert derived["route_stops"] == sum(len(layer["stops"]) for layer in routes["district_layers"])
    assert derived["route_legs"] == sum(len(layer["legs"]) for layer in routes["district_layers"])
    learning = json.loads((ROOT / "data/architecture/learning.json").read_text(encoding="utf-8"))
    assert derived["interactive_labs"] == len(learning["simulations"])
    assert derived["technique_families"] == len(learning["technique_cards"])


def test_snapshot_is_idempotent():
    assert snapshot.measure() == snapshot.measure()
