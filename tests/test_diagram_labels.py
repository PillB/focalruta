"""Y19: every shot diagram can be read: no label covers another, and no park is drawn by the sea.

The red team on PR #24 found 24 of the 120 diagrams with labels drawn over each other (the
subject's action over its pose, the camera's name over the settings chips, the three depth
layers on one line) because their offsets were in metres, and 38 diagrams of parks, plazas
and rooms drawn against a sea horizon because "cámara", "enmarcado" and "San Martín" contain
"mar". The checks render every diagram with the generator and measure what matplotlib drew.
Skipped where matplotlib is not installed (the unit-test job); requirements-qa.txt has it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib.figure  # noqa: E402

COAST = re.compile(r"Malecón|Costa Verde|playa", re.I)


def extent(text, renderer):
    return (text.get_bbox_patch() or text).get_window_extent(renderer)


def overlap(a, b) -> float:
    w, h = min(a.x1, b.x1) - max(a.x0, b.x0), min(a.y1, b.y1) - max(a.y0, b.y0)
    return w * h if w > 1 and h > 1 else 0.0


@pytest.fixture(scope="module")
def drawn(tmp_path_factory):
    import generate_diagrams as g
    from plans_data import PLANS

    out, current = [], {}
    original = matplotlib.figure.Figure.savefig

    def measure(figure, *_args, **_kwargs):
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        panels = [[(t.get_text(), extent(t, renderer)) for t in ax.texts if t.get_visible() and t.get_text().strip()]
                  for ax in figure.axes]
        out.append({**current, "panels": panels, "edges": [ax.get_window_extent(renderer) for ax in figure.axes]})

    matplotlib.figure.Figure.savefig = measure
    try:
        for plan in PLANS:
            for shot in plan["shots"]:
                for variant in ("dog", "human"):
                    current = {"id": f"{shot['id']} {variant}", "coastal": bool(COAST.search(plan["location"]))}
                    g.render_diagram(shot, plan, variant, str(tmp_path_factory.mktemp("d") / "x.png"))
    finally:
        matplotlib.figure.Figure.savefig = original
    return out


@pytest.mark.timeout(300)
def test_y19_no_label_in_a_shot_diagram_covers_another(drawn):
    bad = []
    for diagram in drawn:
        for panel in diagram["panels"]:
            for i, (a_text, a) in enumerate(panel):
                bad += [(diagram["id"], a_text[:24], b_text[:24]) for b_text, b in panel[i + 1:] if overlap(a, b)]
    assert len(drawn) == 120 and not bad, bad[:10]


def test_y19_the_plan_view_labels_stay_out_of_the_side_view(drawn):
    bad = []
    for diagram in drawn:
        plan_view, side_view = diagram["panels"][0], diagram["edges"][1]
        bad += [(diagram["id"], text[:24]) for text, box in plan_view if box.x1 > side_view.x0]
    assert not bad, bad[:10]


def test_y19_inland_plans_are_never_drawn_against_the_sea(drawn):
    # El Olivar, San Isidro, the Centro, a home and Abtao are kilometres from the coast.
    bad = [diagram["id"] for diagram in drawn if not diagram["coastal"]
           and any(text == "HORIZONTE / MAR" for panel in diagram["panels"] for text, _box in panel)]
    assert not bad, bad
