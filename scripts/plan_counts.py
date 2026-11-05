"""W08: the copy says how many plans, shots and diagrams there are, from the plan data.

The home page, the field card and the app manifest were written by hand for six plans
("Seis rutas", "6 planes", "60 tomas", "120 diagramas"). Adding a plan to
scripts/plans_data.py left them wrong. This step rewrites each of those phrases from
data/plans.json and diagrams/, so a seventh plan only needs its data and its diagrams.
Run by regenerate_all.py after the pages are built; idempotent.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORDS = ["cero", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
         "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte"]
WORD = "|".join(WORDS[2:])
# The pages these phrases appear on, rewritten in place.
PAGES = ("index.html", "field_card.html", "manifest.webmanifest")


def number_word(n: int, capital: bool = False) -> str:
    """Spanish words for small counts, as the RAE's Ortografía (2010) prefers in prose; digits past twenty."""
    word = WORDS[n] if 0 <= n < len(WORDS) else str(n)
    return word[:1].upper() + word[1:] if capital else word


def counts(data: dict, root: Path = ROOT) -> dict[str, int]:
    plans = data["plans"]
    shots = sum(len(plan["shots"]) for plan in plans)
    return {"plans": len(plans), "shots": shots, "diagrams": 2 * shots,
            "all_diagrams": len(list((root / "diagrams").glob("*.png")))}


def _word(match: re.Match, n: int) -> str:
    return number_word(n, match.group(1)[:1].isupper()) + match.group(2)


def fill(text: str, c: dict[str, int]) -> str:
    """Every phrase that counts plans, shots or diagrams, with this data's numbers.

    "10 tomas" is one plan's size and stays; only the totals change.
    """
    rules = [
        (rf"\b((?i:{WORD}))( planes| rutas)\b", lambda m: _word(m, c["plans"])),
        (r"\b\d+( planes| opciones: )", lambda m: f"{c['plans']}{m.group(1)}"),
        (r"(🎯 )\d+( tomas)", lambda m: f"{m.group(1)}{c['shots']}{m.group(2)}"),
        (r"\b\d+( tomas planificadas| tomas en )", lambda m: f"{c['shots']}{m.group(1)}"),
        (r"(🎨 )\d+( diagramas)", lambda m: f"{m.group(1)}{c['diagrams']}{m.group(2)}"),
        (r"(= )\d+( diagramas)", lambda m: f"{m.group(1)}{c['diagrams']}{m.group(2)}"),
        (r"(los )\d+( diagramas de las tomas)", lambda m: f"{m.group(1)}{c['diagrams']}{m.group(2)}"),
        (r"(con sus )\d+( diagramas)", lambda m: f"{m.group(1)}{c['all_diagrams']}{m.group(2)}"),
    ]
    for pattern, replace in rules:
        text = re.sub(pattern, replace, text)
    return text


def main() -> int:
    data = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
    c = counts(data)
    for name in PAGES:
        path = ROOT / name
        before = path.read_text(encoding="utf-8")
        after = fill(before, c)
        if after != before:
            path.write_text(after, encoding="utf-8")
    print(f"counted {c['plans']} plans, {c['shots']} shots, {c['diagrams']} subject diagrams, {c['all_diagrams']} in all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
