#!/usr/bin/env python3
"""Verify supplied YouTube metadata and save legitimate transcript tracks when accessible."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL

import bounded_http


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "architectural_photography" / "research" / "videos" / "VIDEO_LEDGER.json"
TRANSCRIPTS = LEDGER.parent / "transcripts"
CHECKS = LEDGER.parent / "transcript_checks"


def metadata(video_id: str) -> tuple[dict, str | None]:
    options = {"quiet": True, "skip_download": True, "no_warnings": True, "socket_timeout": 20}
    try:
        with YoutubeDL(options) as client:
            data = client.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return {
            "exact_title": data.get("title"),
            "channel": data.get("channel") or data.get("uploader"),
            "publication_date": data.get("upload_date"),
            "metadata_status": "VERIFIED",
        }, None
    except Exception as error:  # network/provider failures are evidence states
        return oembed_metadata(video_id), str(error)


def publication_date(video_id: str) -> str | None:
    response = requests.get(f"https://www.youtube.com/watch?v={video_id}", timeout=30)
    response.raise_for_status()
    match = re.search(r'"(?:publishDate|uploadDate)":"([^"]+)"', response.text)
    return match.group(1) if match else None


def oembed_metadata(video_id: str) -> dict:
    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "exact_title": data["title"],
            "channel": data["author_name"],
            "publication_date": publication_date(video_id),
            "metadata_status": "VERIFIED_YOUTUBE_OEMBED_WATCH_PAGE",
        }
    except Exception:
        return {"exact_title": None, "channel": None, "publication_date": None, "metadata_status": "UNAVAILABLE"}


def transcript(video_id: str) -> tuple[dict, str | None]:
    path = TRANSCRIPTS / f"{video_id}.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("segments"):
            return {"transcript_status": "CAPTURED", "transcript_path": path.relative_to(ROOT).as_posix()}, None
    try:
        # The library has no timeout of its own, so the deadline is injected
        # through the one hook it offers: the session it makes requests with.
        api = YouTubeTranscriptApi(http_client=bounded_http.bounded_session())
        tracks = api.list(video_id)
        track = next(iter(tracks))
        fetched = track.fetch()
        payload = {
            "video_id": video_id,
            "language": track.language,
            "language_code": track.language_code,
            "is_generated": track.is_generated,
            "source": "YOUTUBE_CAPTION_TRACK",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "segments": [{"text": item.text, "start": item.start, "duration": item.duration} for item in fetched],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"transcript_status": "CAPTURED", "transcript_path": path.relative_to(ROOT).as_posix()}, None
    except Exception as error:
        return {"transcript_status": "TRANSCRIPT_UNAVAILABLE", "transcript_path": None}, str(error)


def process(row: dict) -> dict:
    if str(row.get("metadata_status", "")).startswith("VERIFIED"):
        meta, metadata_error = {}, None
    else:
        meta, metadata_error = metadata(row["video_id"])
    captions, transcript_error = transcript(row["video_id"])
    check = {
        "video_id": row["video_id"],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "metadata_error": metadata_error,
        "transcript_error": transcript_error,
    }
    (CHECKS / f"{row['video_id']}.json").write_text(json.dumps(check, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    merged = row | meta | captions | {"last_checked_at": check["retrieved_at"]}
    merged["transcript_provenance"] = {
        "source": "YOUTUBE_CAPTION_TRACK" if merged["transcript_status"] == "CAPTURED" else "UNAVAILABLE",
        "path": merged.get("transcript_path"),
        "checked_at": check["retrieved_at"],
    }
    merged.setdefault("timestamped_claims", [])
    merged.setdefault("curriculum_cross_validation", {"status": "NOT_YET_REVIEWED", "agreements": [], "disagreements": []})
    merged.setdefault("tags", [])
    return merged


def main() -> None:
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    CHECKS.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ledger["videos"] = [process(row) for row in ledger["videos"]]
    ledger["last_checked_at"] = datetime.now(timezone.utc).isoformat()
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {status: sum(row["transcript_status"] == status for row in ledger["videos"]) for status in ("CAPTURED", "TRANSCRIPT_UNAVAILABLE")}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
