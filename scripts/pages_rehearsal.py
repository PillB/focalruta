"""Serve the hosted build under /focalruta/, as GitHub Pages does, for a live check rehearsal.

    python3 scripts/pages_rehearsal.py --port 8930 --slow plan_f_F10_human.webp --slow-ms 3000
    FOCALRUTA_LIVE_URL=http://127.0.0.1:8930/focalruta/ python3 scripts/live_pages_qa.py

--slow holds a file's answer back, as a slow CDN node does; --missing answers 404 for it,
as a broken deploy would. Requirement Y27: on 8 November 2026 the daily live check
reported the shot dialog's diagram as a failed request because it reloaded the page
0.1 s after opening the dialog. With --slow on that diagram the check of 2eff0ab
fails every time and the fixed one passes.
"""
from __future__ import annotations

import argparse
import functools
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "/focalruta"


class Rehearsal(SimpleHTTPRequestHandler):
    slow: frozenset[str] = frozenset()
    missing: frozenset[str] = frozenset()
    slow_seconds = 0.0
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".webp": "image/webp",
                      ".webmanifest": "application/manifest+json", ".js": "text/javascript"}

    def translate_path(self, path: str) -> str:
        path = path.split("?", 1)[0]
        inside = path == PREFIX or path.startswith(PREFIX + "/")
        return super().translate_path(path[len(PREFIX):] or "/" if inside else "/__outside_the_site__")

    def do_GET(self) -> None:
        name = self.path.split("?", 1)[0].rsplit("/", 1)[-1]
        if name in self.missing:
            self.send_error(404)
            return
        if name in self.slow:
            time.sleep(self.slow_seconds)
        try:
            super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            pass  # the browser gave up on the answer; that is what a rehearsal may test

    def log_message(self, *args) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8930)
    parser.add_argument("--root", type=Path, default=ROOT / "dist/canon6d_sota_hosted")
    parser.add_argument("--slow", action="append", default=[], help="a file name to answer late")
    parser.add_argument("--slow-ms", type=int, default=3000)
    parser.add_argument("--missing", action="append", default=[], help="a file name to answer 404")
    options = parser.parse_args()
    handler = type("Configured", (Rehearsal,), {"slow": frozenset(options.slow), "missing": frozenset(options.missing),
                                                 "slow_seconds": options.slow_ms / 1000})
    server = ThreadingHTTPServer(("127.0.0.1", options.port), functools.partial(handler, directory=str(options.root)))
    print(f"http://127.0.0.1:{options.port}{PREFIX}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
