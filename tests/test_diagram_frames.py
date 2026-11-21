"""Every line a technique diagram draws stays inside its frame (Z09).

Requirement Z09. Two of four blind raters of 21 Nov 2026 saw the viewpoint diagram's lower
sight line run out of the bottom of its frame on the techniques page: the 35 mm half angle,
drawn 128 units long from a camera 34 units above the ground, ends 12 units below the
viewBox, so the browser cut it mid-stroke and the cone seemed to dive underground. These
tests read the drawn geometry, not the code that computes it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lab_visuals  # noqa: E402

NUMBER = r"-?\d+(?:\.\d+)?"


def path_points(d: str) -> list[tuple[float, float]]:
    """The vertices of a path written with M, L, H and V, absolute or relative."""
    points, x, y = [], 0.0, 0.0
    for command, args in re.findall(r"([MLHVmlhv])([^MLHVmlhv]*)", d):
        values = [float(v) for v in re.findall(NUMBER, args)]
        step = 1 if command in "HVhv" else 2
        for i in range(0, len(values), step):
            if command in "ML":
                x, y = values[i], values[i + 1]
            elif command in "ml":
                x, y = x + values[i], y + values[i + 1]
            elif command == "H":
                x = values[i]
            elif command == "h":
                x += values[i]
            elif command == "V":
                y = values[i]
            else:
                y += values[i]
            points.append((x, y))
    return points


def attrs(tag: str) -> dict[str, float]:
    return {k: float(v) for k, v in re.findall(rf'\s([a-z]+\d?)="({NUMBER})"', tag)}


def drawn_points(svg: str) -> list[tuple[str, float, float]]:
    """Every vertex and box corner the drawing puts on the page, named by its element."""
    out = []
    for tag in re.findall(r"<line\b[^>]*>", svg):
        a = attrs(tag)
        out += [("line", a["x1"], a["y1"]), ("line", a["x2"], a["y2"])]
    for d in re.findall(r'<path\b[^>]*\sd="([^"]+)"', svg):
        out += [("path", x, y) for x, y in path_points(d)]
    for pts in re.findall(r'<polygon\b[^>]*\spoints="([^"]+)"', svg):
        values = [float(v) for v in re.findall(NUMBER, pts)]
        out += [("polygon", values[i], values[i + 1]) for i in range(0, len(values), 2)]
    for tag in re.findall(r"<rect\b[^>]*>", svg):
        a = attrs(tag)
        out += [("rect", a["x"], a["y"]), ("rect", a["x"] + a["width"], a["y"] + a["height"])]
    for tag in re.findall(r"<circle\b[^>]*>", svg):
        a = attrs(tag)
        out += [("circle", a["cx"] - a["r"], a["cy"] - a["r"]), ("circle", a["cx"] + a["r"], a["cy"] + a["r"])]
    return out


def outside(svg: str) -> list[str]:
    x0, y0, width, height = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    return [f"{kind} ({x:g}, {y:g})" for kind, x, y in drawn_points(svg)
            if not (x0 <= x <= x0 + width and y0 <= y <= y0 + height)]


def test_z09_the_check_sees_a_line_leave_the_frame_and_passes_one_inside():
    frame = '<svg viewBox="0 0 360 150">{}</svg>'
    assert outside(frame.format('<path d="M34 96L162 161.83"/>')) == ["path (162, 161.83)"]
    assert outside(frame.format('<path d="M300 68v90"/><line x1="0" y1="0" x2="360" y2="150"/>')) == ["path (300, 158)"]
    assert outside(frame.format('<path d="M300 68v40h-20"/><rect x="10" y="10" width="20" height="20"/>')) == []


@pytest.mark.parametrize("technique", sorted(lab_visuals.TECHNIQUE_DIAGRAMS))
def test_z09_every_line_a_technique_diagram_draws_stays_inside_its_frame(technique):
    assert outside(lab_visuals.TECHNIQUE_DIAGRAMS[technique]()) == []
