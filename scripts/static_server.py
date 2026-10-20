#!/usr/bin/env python3
"""Serve the hosted build the way GitHub Pages does, for QA that measures it.

Python's SimpleHTTPRequestHandler sends every file uncompressed. GitHub Pages
gzips text responses, so a speed check against the plain handler charges the
home page roughly four times the bytes a reader actually downloads. This
handler compresses the text types when the browser asks for gzip, sends the
ten-minute cache lifetime Pages sends, and can mount the site under a prefix
such as /focalruta/, so the live-site check can be rehearsed on a local copy.

Its validators are content tags, so a revalidation after a deploy gets the new
file: Python's own Last-Modified answers 304 with the old body when a build
copied with its modification times is swapped in. deploy_rehearsal.py serves
its builds with this handler too, so the speed check and the deploy rehearsals
see the same Pages.
"""
from __future__ import annotations

import functools
import gzip
import hashlib
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

COMPRESSIBLE = frozenset({
    "text/html", "text/css", "text/javascript", "application/javascript", "application/json",
    "application/manifest+json", "image/svg+xml", "text/plain", "text/xml", "application/xml",
})


class PagesHandler(SimpleHTTPRequestHandler):
    """Static files with gzip for text, like GitHub Pages; quiet by default."""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".webmanifest": "application/manifest+json",
        ".webp": "image/webp",
    }

    def __init__(self, *args, prefix: str = "", site=None, **kwargs):
        self.prefix = prefix.rstrip("/")
        self.site = site
        super().__init__(*args, **kwargs)

    def parse_request(self) -> bool:
        # A rehearsed deploy switches the build between requests, not connections: a browser
        # opens sockets before it needs them, and one opened before the switch must get the
        # new build, as on Pages (red team on PR #21, F1).
        if self.site is not None:
            self.directory = str(self.site())
        return super().parse_request()

    def log_message(self, *args) -> None:
        pass

    def translate_path(self, path: str) -> str:
        if self.prefix:
            if path != self.prefix and not path.startswith(self.prefix + "/"):
                return str(Path(self.directory) / "outside-the-mount" / "404")
            path = path[len(self.prefix):] or "/"
        return super().translate_path(path)

    def send_header(self, keyword: str, value: str) -> None:
        if keyword != "Last-Modified":
            super().send_header(keyword, value)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "max-age=600")
        if getattr(self, "etag", None):
            self.send_header("ETag", self.etag)
        super().end_headers()

    def target(self) -> Path:
        target = Path(self.translate_path(self.path))
        if target.is_dir() and self.path.split("?", 1)[0].endswith("/"):
            target = target / "index.html"
        return target

    def send_head(self):
        target = self.target()
        self.etag = f'"{hashlib.sha256(target.read_bytes()).hexdigest()[:16]}"' if target.is_file() else None
        if self.etag and self.headers.get("If-None-Match") == self.etag:
            self.send_response(304)
            self.end_headers()
            return None
        return super().send_head()

    def do_GET(self) -> None:
        target = self.target()
        kind = self.guess_type(str(target))
        if not (target.is_file() and kind in COMPRESSIBLE and "gzip" in self.headers.get("Accept-Encoding", "")):
            super().do_GET()
            return
        self.etag = f'"{hashlib.sha256(target.read_bytes()).hexdigest()[:16]}-gzip"'
        if self.headers.get("If-None-Match") == self.etag:
            self.send_response(304)
            self.end_headers()
            return
        body = gzip.compress(target.read_bytes(), compresslevel=6, mtime=0)
        self.send_response(200)
        self.send_header("Content-Type", kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(directory, prefix: str = "") -> ThreadingHTTPServer:
    """Start a background server on a free port; the caller shuts it down.

    `directory` is a path, or a function returning the build to serve now, which
    is how a deploy is rehearsed: each request is answered from the build it returns.
    """
    site = directory if callable(directory) else None
    initial = directory() if callable(directory) else directory
    handler = functools.partial(PagesHandler, directory=str(initial), prefix=prefix, site=site)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def base_url(server: ThreadingHTTPServer, prefix: str = "") -> str:
    return f"http://127.0.0.1:{server.server_address[1]}{prefix.rstrip('/')}/"
