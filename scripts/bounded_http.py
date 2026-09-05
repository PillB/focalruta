#!/usr/bin/env python3
"""An HTTP session that cannot make a request without a deadline.

`youtube-transcript-api` exposes no timeout of its own (jdepoix/youtube-transcript-api#324
is still open), and `requests.Session` has none either: `timeout` is an argument
to each individual request, so setting an attribute on a Session does nothing and
handing the library a plain Session changes nothing.

The library does accept an `http_client` session, which is the one place a
deadline can be injected for every call it makes. This is the third time this
project has met the same shape — an operation that could only hang, never fail —
after the OSM router (`build_architecture_routes.get_json`) and the browser
harness (`qa_matrix.bounded_async`). A request with no deadline can never trip
the fail-fast rule, because it never fails.
"""
from __future__ import annotations

import requests

DEFAULT_TIMEOUT_SECONDS = 30


class _BoundedSession(requests.Session):
    """A Session that supplies a default timeout to every request."""

    def __init__(self, timeout: int) -> None:
        super().__init__()
        self.timeout = timeout

    def request(self, method, url, **kwargs):  # type: ignore[override]
        kwargs.setdefault("timeout", self.timeout)
        return super().request(method, url, **kwargs)


def bounded_session(timeout: int = DEFAULT_TIMEOUT_SECONDS) -> requests.Session:
    """A requests.Session whose every call carries a deadline.

    Accepts an explicit per-call `timeout` and leaves it alone; only supplies the
    default when the caller gave none.
    """
    return _BoundedSession(timeout)
