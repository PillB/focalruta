import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKBENCH = ROOT / "architectural_photography" / "research" / "videos"
DATA = ROOT / "data" / "architecture"


def test_all_supplied_videos_have_verified_metadata_and_real_transcript_files():
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["url_occurrences"] == 21
    assert ledger["unique_video_ids"] == 20
    assert len(ledger["videos"]) == 20
    for video in ledger["videos"]:
        assert video["metadata_status"].startswith("VERIFIED")
        assert video["exact_title"] and video["channel"] and video["publication_date"]
        assert video["transcript_status"] == "CAPTURED"
        transcript = json.loads((ROOT / video["transcript_path"]).read_text(encoding="utf-8"))
        assert transcript["source"] == "YOUTUBE_CAPTION_TRACK"
        assert transcript["segments"]
        assert all({"text", "start", "duration"} <= segment.keys() for segment in transcript["segments"])


def test_curriculum_has_all_required_lessons_and_field_shape():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    assert len(learning["lessons"]) == 17
    required = {"observe", "try", "diagnose", "break_the_rule_when", "canon_6d_note", "competition_note", "sources"}
    assert all(required <= lesson.keys() for lesson in learning["lessons"])
    assert all(all(lesson[field] for field in required) for lesson in learning["lessons"])


def test_curriculum_preserves_optics_and_editing_truth():
    text = json.dumps(json.loads((DATA / "learning.json").read_text(encoding="utf-8")), ensure_ascii=False)
    assert "camera position" in text.lower()
    assert "field of view" in text.lower()
    assert "background distance" in text.lower()
    assert "DoF" in text
    assert "magic ISO" in text
    assert "fundamental" in text.lower()


def test_video_attributions_have_timestamp_and_known_video():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    known = {video["video_id"] for video in ledger["videos"]}
    for lesson in learning["lessons"]:
        for source in lesson["sources"]:
            if source["type"] == "VIDEO_TRANSCRIPT":
                assert source["video_id"] in known
                assert isinstance(source["timestamp_seconds"], (int, float))
