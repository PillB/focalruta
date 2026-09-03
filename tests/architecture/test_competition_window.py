"""A closed competition may not be presented as the current one.

Requirements: E03, A03, O03. `competition_rules.json` describes a window that
closed on 2026-08-30. Nothing compared it against the real date, so the data
could be rendered as live indefinitely.
"""
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "data/architecture/competition_rules.json"


def _rules() -> dict:
    return json.loads(RULES.read_text(encoding="utf-8"))


def test_edition_state_matches_the_real_calendar():
    rules = _rules()
    state = rules.get("edition_state")
    assert state in {"OPEN", "CLOSED"}, "the edition must declare whether it is still open"
    closes = datetime.fromisoformat(rules["dates"]["closes_local"]).date()
    expected = "OPEN" if date.today() <= closes else "CLOSED"
    assert state == expected, (
        f"submission closed {closes} and today is {date.today()}; "
        f"the file still says {state}. Run scripts/verify_release.py after updating it."
    )


def test_a_closed_edition_says_so_in_words_a_reader_understands():
    rules = _rules()
    if rules.get("edition_state") != "CLOSED":
        return
    note = rules.get("edition_note", "")
    assert note, "a closed edition must explain that its dates are historical"
    assert str(datetime.fromisoformat(rules["dates"]["closes_local"]).date()) in note


def test_the_public_page_never_hardcodes_a_specific_edition_deadline():
    """The brief decoder asks the reader for the current dates; it must not assert them."""
    page = (ROOT / "challenges/arquitectura-en-foco/index.html").read_text(encoding="utf-8")
    for value in (_rules()["dates"]["closes_local"], "30 de agosto de 2026"):
        assert value not in page, f"the evergreen page must not publish {value}"
