"""The route builder must fail on a stalled service instead of hanging.

Requirements: K04, O03. A request with no timeout can never trigger the
fail-fast rule, because it never fails.
"""
import sys
import threading
import time
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import build_architecture_routes as routes

STALL_SECONDS = 120


class StallingHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - http.server API
        time.sleep(STALL_SECONDS)

    def log_message(self, format: str, *args) -> None:
        return


@pytest.fixture()
def stalled_service():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(StallingHandler))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/route"
    server.shutdown()
    server.server_close()


def test_stalled_service_raises_within_a_bounded_wall_clock(stalled_service, monkeypatch):
    # Same code path, shortened budget, so the contract is checked in seconds.
    monkeypatch.setattr(routes, "CONNECT_TIMEOUT_SECONDS", 2)
    monkeypatch.setattr(routes, "MAX_TIME_SECONDS", 3)
    monkeypatch.setattr(routes, "FETCH_ATTEMPTS", 1)
    monkeypatch.setattr(routes, "RETRY_DELAY_SECONDS", 1)
    budget = routes.request_budget_seconds()
    outcome: dict[str, object] = {}

    def call() -> None:
        started = time.monotonic()
        try:
            routes.get_json(stalled_service)
            outcome["result"] = "returned"
        except Exception as error:  # noqa: BLE001 - any failure is acceptable, hanging is not
            outcome["result"] = type(error).__name__
        outcome["elapsed"] = time.monotonic() - started

    worker = threading.Thread(target=call, daemon=True)
    worker.start()
    worker.join(timeout=budget + 10)

    assert not worker.is_alive(), (
        "get_json hung against a stalled service; a request without a timeout can never fail fast"
    )
    assert outcome["result"] != "returned"
    assert outcome["elapsed"] < budget + 5


def test_fetch_budget_is_bounded_and_leaves_room_for_retries():
    assert 0 < routes.CONNECT_TIMEOUT_SECONDS <= 20
    assert routes.CONNECT_TIMEOUT_SECONDS < routes.MAX_TIME_SECONDS
    assert routes.request_budget_seconds() > routes.MAX_TIME_SECONDS * routes.FETCH_ATTEMPTS
    assert routes.request_budget_seconds() < 600
