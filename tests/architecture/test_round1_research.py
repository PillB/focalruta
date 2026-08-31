import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "architecture"


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_organizer_history_has_all_editions_and_transfer_limits():
    rows = read("organizer_history.json")
    assert [row["year"] for row in rows] == [2023, 2024, 2025]
    assert all(row["official_source_ids"] for row in rows)
    assert all(row["first_read_mechanism"] and row["transfers_to_2026"] and row["does_not_transfer"] for row in rows)
    assert rows[1]["winner_title"] == "La Vida en Sombras"
    assert rows[2]["winner_title"] == "Patrones Subterráneos"


def test_judges_are_public_work_dossiers_not_predictions():
    rows = read("judges.json")
    assert {row["juror_id"] for row in rows} == {"cristian-aninat", "hans-stoll", "camilo-monzon"}
    for row in rows:
        assert row["verified_sources"]
        assert row["observable_visual_mechanisms"]
        assert row["counterexamples"]
        assert 0 <= row["confidence"] <= 1
        serialized = json.dumps(row, ensure_ascii=False).lower()
        assert "will love" not in serialized
        assert "probability of winning" not in serialized
        assert row["ranking_use"] == "LOW_WEIGHT_ROBUSTNESS_SIGNAL_ONLY"
