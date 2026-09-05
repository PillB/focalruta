"""Every outbound request must carry a deadline it cannot silently outlive.

Requirements: K04, M01, O03.

`youtube-transcript-api` has no timeout option of its own — jdepoix/youtube-transcript-api#324
is still open — and `requests.Session` has no session-level timeout either, since
`timeout` is a per-request argument. Passing a plain Session as `http_client`
therefore changes nothing. The deadline has to be injected on every call.

These tests use a recording stand-in for the parent class, so they exercise the
real injection logic without a network and without the transcript library
installed.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import bounded_http


def test_a_request_without_a_timeout_gets_the_default(monkeypatch):
    seen = {}

    def record(self, method, url, **kwargs):
        seen.update(kwargs)
        return "response"

    monkeypatch.setattr(bounded_http.requests.Session, "request", record)
    session = bounded_http.bounded_session(7)
    assert session.request("GET", "https://example.invalid") == "response"
    assert seen["timeout"] == 7


def test_an_explicit_timeout_from_the_caller_is_respected(monkeypatch):
    seen = {}

    def record(self, method, url, **kwargs):
        seen.update(kwargs)

    monkeypatch.setattr(bounded_http.requests.Session, "request", record)
    bounded_http.bounded_session(7).request("GET", "https://example.invalid", timeout=2)
    assert seen["timeout"] == 2, "an explicit deadline must not be overridden"


def test_the_default_is_finite_and_sane():
    assert 0 < bounded_http.DEFAULT_TIMEOUT_SECONDS <= 60


def test_the_session_is_usable_where_a_requests_session_is_expected():
    """It must satisfy the http_client contract of the transcript library."""
    session = bounded_http.bounded_session()
    assert isinstance(session, bounded_http.requests.Session)
    assert session.timeout == bounded_http.DEFAULT_TIMEOUT_SECONDS


def test_a_plain_session_would_not_have_helped():
    """Guards the reason this module exists, not just the code it contains."""
    plain = bounded_http.requests.Session()
    assert not hasattr(plain, "timeout"), (
        "if requests grows a session-level timeout, this module can be retired"
    )


def test_the_transcript_script_hands_the_library_a_bounded_client():
    """The one caller must actually use it; a helper nobody wires in is decoration."""
    source = (ROOT / "scripts/research_video_ledger.py").read_text(encoding="utf-8")
    assert "bounded_http" in source
    assert "http_client" in source, "the library only accepts a deadline via http_client"
