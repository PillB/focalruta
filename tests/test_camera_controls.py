"""W11: the field card says where each setting the plans use lives on the Canon EOS 6D.

Camera-specific guides (the manufacturer's quick reference, a model's cheat sheet) answer the
question a beginner has with the camera in hand: which dial is the aperture in M? The card
gave the numbers and never the controls. Every line here was read in Canon's EOS 6D
instruction manual (pages cited in the section); the checks hold the section to the gear
data and the dial the rest of the card uses, so the two cannot drift apart.
"""
from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import exposure_model as em  # noqa: E402

CARD = (ROOT / "field_card.html").read_text(encoding="utf-8")
GEAR = json.loads((ROOT / "data/plans.json").read_text(encoding="utf-8"))["gear"]["camera"]


def section() -> str:
    found = re.search(r'<h3 class="fc-h3" id="fc-h-controls">.*?</ul>\s*<p class="fc-table-note">.*?</p>', CARD, re.S)
    assert found, "the card has no section on the 6D's controls"
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", found.group(0))).split())


def test_w11_every_setting_the_plans_use_has_its_control():
    text = section()
    for words in ("dial de modo en M", "dial principal", "dial de control rápido", "botón ISO", "botón AF",
                  "ONE SHOT", "AI SERVO", "botón DRIVE", "2 s", "B (Bulb)", "bloqueo del espejo", "interruptor de bloqueo"):
        assert words in text, words


def test_w11_the_controls_agree_with_the_gear_and_the_dial():
    text = section()
    low, high = re.match(r"(\d+)–(\d+)", GEAR["iso"]).groups()
    assert f"de {low} a {high} en tercios de paso" in text
    assert f"≈{GEAR['fps']:g} fotos/s".replace(".", ",") in text or f"≈{GEAR['fps']:g} fotos/s" in text
    longest = em.THIRD_STOP_SHUTTERS[-1].rstrip('"')
    assert f"más de {longest} s" in text
    assert "RS-80N3" in text and "TC-80N3" in text  # the remotes the manual names for the 6D's N3 terminal
    assert re.search(r"manual de instrucciones de la EOS 6D.*págs?\. \d+", text)
