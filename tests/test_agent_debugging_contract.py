from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_agent_contract_requires_research_after_first_failed_fix_hypothesis():
    contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required_phrases = (
        "first failed fix hypothesis",
        "research the error online",
        "before the next fix attempt",
        "primary documentation",
        "record the sources",
        "what evidence changed the hypothesis",
    )
    assert all(phrase in contract for phrase in required_phrases)
