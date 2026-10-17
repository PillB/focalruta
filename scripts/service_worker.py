"""Fill in assets/sw.template.js for a built site.

The worker keeps every file under its revision, the first 12 hex digits of its
SHA-256, and checks the bytes it receives against it (see the template's
header). This module computes those revisions, so the build and the browser
QA (which builds modified copies of the site to rehearse an upgrade) write the
worker the same way.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "sw.template.js"
# Kept on install: the home page, the field card and the architecture guide work
# offline after one visit.
CORE = (
    "index.html", "assets/hosted.css", "data/plans_embedded.js", "manifest.webmanifest", "field_card.html",
    "challenges/arquitectura-en-foco/index.html", "challenges/arquitectura-en-foco/iphone-maps.html",
    "data/architecture/learning.json", "data/architecture/ranking.json", "data/architecture/routes.json",
    "assets/icon-192.png", "assets/icon-512.png", "assets/icon-maskable-192.png", "assets/icon-maskable-512.png",
    "assets/app-icon.svg",
)
# Never kept: the worker itself, the 15 MB single-file copy and the ZIP (readers
# download those once), and files for crawlers and maintainers.
LEFT_OUT = {"sw.js", "FocalRuta_STANDALONE.html", "BUILD_METRICS.json", "README.md", "robots.txt", "sitemap.xml"}
LEFT_OUT_DIRS = (".github/", "downloads/")


def revision(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def files(site: Path) -> dict[str, str]:
    """Every file the worker may keep, as its URL path under the site, with its revision."""
    kept = {}
    for path in sorted(p for p in site.rglob("*") if p.is_file()):
        name = path.relative_to(site).as_posix()
        if name not in LEFT_OUT and not name.startswith(LEFT_OUT_DIRS):
            kept[quote(name)] = revision(path)
    return kept


def write(site: Path, version: str, template: Path = TEMPLATE) -> dict[str, str]:
    """Write site/sw.js and return the revisions it carries."""
    kept = files(site)
    missing = [name for name in CORE if name not in kept]
    if missing:
        raise RuntimeError(f"the worker's shell names files the build does not have: {missing}")
    source = template.read_text(encoding="utf-8")
    for slot in ("__CACHE_VERSION__", "__FILES__", "__CORE__"):
        if source.count(slot) != 1:
            raise RuntimeError(f"{template.name} must hold {slot} exactly once")
    worker = (source.replace("__CACHE_VERSION__", version)
              .replace("__FILES__", json.dumps(kept, separators=(",", ":")))
              .replace("__CORE__", json.dumps(list(CORE), separators=(",", ":"))))
    (site / "sw.js").write_text(worker, encoding="utf-8")
    return kept
