"""Rehearse a deploy in a real browser.

Builds of the site that differ in known files are served under /focalruta/ the
way GitHub Pages serves them (Cache-Control: max-age=600), and a deploy is a
switch of the build being served. scripts/field_card_qa.py uses this for V07,
V16 and V17: an upgrade from the worker live at 9cd3044, the first visit after
a deploy, an install while the HTTP cache still holds the last build, and the
files kept for the field following a deploy.
"""
from __future__ import annotations

import functools
import hashlib
import re
import shutil
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import service_worker

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
PREFIX = "/focalruta/"
LIVE_WORKER = ROOT / "tests" / "fixtures" / "sw_live_9cd3044.js"
LIVE_VERSION = "focalruta-069db98985ca"
MARKERS = {".html": "<!-- build {} -->\n", ".css": "\n/* build {} */\n", ".js": "\n// build {}\n"}
VERSIONED = ("assets/hosted.css", "data/plans_embedded.js")


def mark(path: Path, build: str) -> None:
    """Change a file the way a new build would, and say which build it is from."""
    path.write_text(path.read_text(encoding="utf-8") + MARKERS[path.suffix].format(build), encoding="utf-8")


def write_worker(site: Path, version: str) -> None:
    template = service_worker.TEMPLATE.read_text(encoding="utf-8")
    if "__FILES__" in template:
        service_worker.write(site, version)
    else:  # a template from before revisions (the RED runs used eb3c101's): only the version was filled in
        (site / "sw.js").write_text(template.replace("__CACHE_VERSION__", version), encoding="utf-8")


def build(into: Path, name: str, changes: tuple[str, ...] = (), live_worker: bool = False, source: Path = DIST) -> Path:
    """A copy of `source` as build `name`: `changes` carry its name; the worker is
    this repository's, or the one live at 9cd3044 with the home page as it named its files."""
    site = into / name
    shutil.copytree(source, site, ignore=shutil.ignore_patterns("FocalRuta_STANDALONE.html", "downloads"))
    for relative in changes:
        mark(site / relative, name)
    index = site / "index.html"
    html = index.read_text(encoding="utf-8")
    for asset in VERSIONED:
        revision = "" if live_worker else "?v=" + service_worker.revision(site / asset)
        html = re.sub(rf'"\./{re.escape(asset)}(?:\?v=[0-9a-f]+)?"', f'"./{asset}{revision}"', html)
    index.write_text(html, encoding="utf-8")
    version = "focalruta-" + hashlib.sha256(name.encode()).hexdigest()[:12]
    if live_worker:
        (site / "sw.js").write_text(LIVE_WORKER.read_text(encoding="utf-8").replace(LIVE_VERSION, version), encoding="utf-8")
    else:
        write_worker(site, version)
    return site


class Pages:
    """A Pages-like server whose build can be swapped, and stopped like a lost signal."""

    def __init__(self, site: Path):
        self.site = site
        pages = self

        class Handler(SimpleHTTPRequestHandler):
            def translate_path(self, path):
                path = unquote(urlsplit(path).path)
                if not path.startswith(PREFIX):
                    return str(pages.site / "outside-the-site" / "404")
                return str(pages.site / path[len(PREFIX):])

            # Like Pages: validators are content tags, so a revalidation after a deploy gets the new file.
            def send_head(self):
                path = Path(self.translate_path(self.path))
                path = path / "index.html" if path.is_dir() and self.path.split("?")[0].endswith("/") else path
                self.etag = f'"{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}"' if path.is_file() else None
                if self.etag and self.headers.get("If-None-Match") == self.etag:
                    self.send_response(304)
                    self.end_headers()
                    return None
                return super().send_head()

            def send_header(self, keyword, value):
                if keyword != "Last-Modified":
                    super().send_header(keyword, value)

            def end_headers(self):
                self.send_header("Cache-Control", "max-age=600")
                if getattr(self, "etag", None):
                    self.send_header("ETag", self.etag)
                super().end_headers()

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(site)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}{PREFIX}"

    def deploy(self, site: Path) -> None:
        self.site = site

    def stop(self) -> None:
        # Close the socket too: a stopped loop with an open socket accepts connections
        # and never answers, which is a hung network, not an absent one.
        self.server.shutdown()
        self.server.server_close()


def relative(url: str) -> str:
    path = unquote(urlsplit(url).path)[len(PREFIX):]
    return path + "index.html" if path == "" or path.endswith("/") else path


def stale(responses: list, base: str, site: Path) -> list[str]:
    """Same-origin files a page received with bytes other than `site`'s."""
    wrong = []
    for response in responses:
        if not response.url.startswith(base) or response.status != 200:
            continue
        expected = site / relative(response.url)
        try:
            body = response.body()
        except Exception:  # noqa: BLE001 - a response without a body (a redirect, an aborted image) has nothing to compare
            continue
        if expected.is_file() and body != expected.read_bytes():
            wrong.append(relative(response.url))
    return sorted(set(wrong))
