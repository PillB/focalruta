import hashlib
from pathlib import Path

from PIL import Image

from scripts.architecture_preflight import evaluate_submission


def make_jpeg(path: Path, target_size: int = 5_100_000) -> None:
    Image.new("RGB", (32, 32), "white").save(path, "JPEG")
    with path.open("ab") as output:
        output.write(b"\0" * (target_size - path.stat().st_size))


def valid_metadata():
    return {
        "capture_year": 2026,
        "title": "Umbral",
        "place": "Lima",
        "capture_date": "2026-08-27",
        "description": "Una relación arquitectónica observada.",
        "backup_exists": True,
        "allowed_edits_only": True,
        "no_fundamental_retouch": True,
        "no_ai_image_processing": True,
    }


def test_preflight_accepts_one_compliant_file_without_altering_it(tmp_path):
    candidate = tmp_path / "carolina-val.jpg"
    make_jpeg(candidate)
    before = hashlib.sha256(candidate.read_bytes()).hexdigest()
    result = evaluate_submission([candidate], valid_metadata())
    after = hashlib.sha256(candidate.read_bytes()).hexdigest()
    assert result["eligible"] is True
    assert result["violations"] == []
    assert result["file"]["width_px"] == 32
    assert result["file"]["height_px"] == 32
    assert result["file"]["color_mode"] == "RGB"
    assert before == after


def test_preflight_rejects_zero_or_multiple_files(tmp_path):
    assert "EXACTLY_ONE_FILE" in evaluate_submission([], valid_metadata())["violations"]
    first, second = tmp_path / "a-b.jpg", tmp_path / "c-d.jpeg"
    make_jpeg(first)
    make_jpeg(second)
    assert "EXACTLY_ONE_FILE" in evaluate_submission([first, second], valid_metadata())["violations"]


def test_preflight_enforces_boundaries_filename_year_and_confirmations(tmp_path):
    candidate = tmp_path / "wrong name.png"
    candidate.write_bytes(b"x")
    metadata = valid_metadata() | {
        "capture_year": 2019,
        "backup_exists": False,
        "allowed_edits_only": False,
        "no_fundamental_retouch": False,
        "no_ai_image_processing": False,
    }
    violations = set(evaluate_submission([candidate], metadata)["violations"])
    assert {"INVALID_EXTENSION", "FILE_TOO_SMALL", "INVALID_FILENAME", "CAPTURE_BEFORE_2020"} <= violations
    assert {"BACKUP_NOT_CONFIRMED", "EDITS_NOT_CONFIRMED", "RETOUCH_NOT_CONFIRMED", "AI_NOT_CONFIRMED"} <= violations


def test_preflight_rejects_more_than_25_mb(tmp_path):
    candidate = tmp_path / "ana-perez.jpeg"
    make_jpeg(candidate, 25_000_001)
    assert "FILE_TOO_LARGE" in evaluate_submission([candidate], valid_metadata())["violations"]
