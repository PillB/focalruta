#!/usr/bin/env python3
"""Hold every page type to a speed budget, as a phone on a slow network sees it.

Requirement X02. Lighthouse (pinned in package-lock.json) loads each page with
its default mobile settings: a mid-range phone, simulated Slow 4G and a 4x
slower CPU. The pages are served gzipped, the way GitHub Pages serves them
(`static_server.py`), or fetched from the live site with --base-url.

Each page runs three times and the median of every metric is judged, because
Lighthouse's own variability guidance warns against single runs. The timing
budgets are Lighthouse's "good" control points for mobile (a metric at its
budget scores 0.9): first paint 1.8 s, largest paint 2.5 s, blocking time
200 ms, layout shift 0.1, speed index 3.4 s, and a performance score of at
least 90. The byte budgets are per page type and leave room for content, not
for a new framework. No page may ask another origin for anything: nothing a
reader opens tells a third party they did.

FocalRuta_STANDALONE.html is left out on purpose: it is the 15 MB offline copy
a reader downloads once, with every diagram inside, not a page anyone browses.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import evidence
import qa_matrix
import static_server

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
REPORT = ROOT / "PERF_BUDGET_QA.json"
RUNS = 3

CHALLENGE = "challenges/arquitectura-en-foco/"
# Page, page type, transfer budget in KB: gzip, everything loaded before the page
# settles. About 1.5 times what each type weighed when the budgets were set
# (home 121, field card 43, plans 207-226, challenge 57): room for content, not
# for a framework.
PAGES = (
    ("index.html", "home", 180),
    ("field_card.html", "field card", 70),
    *((f"plans/plan_{letter}.html", "plan page", 340) for letter in "abcdef"),
    (CHALLENGE + "index.html", "challenge", 100),
    (CHALLENGE + "wiki-tecnicas.html", "challenge guide", 40),
    (CHALLENGE + "field-card.html", "challenge guide", 40),
    (CHALLENGE + "iphone-maps.html", "challenge guide", 40),
    (CHALLENGE + "maps/barranco-tour-1.html", "route map", 20),
    ("404.html", "not found", 20),
)
TIMING_BUDGETS = (
    # (Lighthouse audit, budget, unit shown in the report)
    ("first-contentful-paint", 1800, "ms"),
    ("largest-contentful-paint", 2500, "ms"),
    ("total-blocking-time", 200, "ms"),
    ("cumulative-layout-shift", 0.1, ""),
    ("speed-index", 3400, "ms"),
)
MIN_SCORE = 0.90


def lighthouse_command() -> list[str]:
    configured = os.environ.get("FOCALRUTA_LIGHTHOUSE", "")
    binary = Path(configured) if configured else ROOT / "node_modules/.bin/lighthouse"
    if not binary.is_file():
        sys.exit(f"Lighthouse not found at {binary}: run `npm ci` or point FOCALRUTA_LIGHTHOUSE at it")
    return [str(binary)]


def chrome_path() -> str:
    """The Chromium every other suite uses; Lighthouse needs it by path.

    Playwright names the build it expects whether or not it is installed, and
    Lighthouse would then fail inside chrome-launcher, page after page: stop
    here with the reason instead (X01).
    """
    path = qa_matrix.browser_options().get("executable_path")
    if not path:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            path = playwright.chromium.executable_path
    if not Path(path).is_file():
        sys.exit(f"Lighthouse needs Chromium at {path}, which is not there: run "
                 "`python3 -m playwright install chromium` or set FOCALRUTA_CHROME")
    return path


def run_lighthouse(url: str, chrome: str) -> dict:
    with tempfile.TemporaryDirectory() as scratch:
        output = Path(scratch) / "report.json"
        command = lighthouse_command() + [
            url, "--quiet", "--only-categories=performance", "--output=json", f"--output-path={output}",
            "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
        ]
        completed = subprocess.run(command, env={**os.environ, "CHROME_PATH": chrome},
                                   capture_output=True, text=True, timeout=240)
        if completed.returncode != 0 or not output.is_file():
            raise RuntimeError(f"Lighthouse failed on {url}: {completed.stderr[-800:]}")
        return json.loads(output.read_text(encoding="utf-8"))


def summarize(report: dict, origin: str) -> dict:
    """The numbers one run contributes: metrics, bytes, requests, other origins."""
    audits = report["audits"]
    requests = audits["network-requests"]["details"]["items"]
    foreign = sorted({item["url"] for item in requests
                      if item["url"].startswith("http") and _origin(item["url"]) != origin})
    breakdown = audits.get("lcp-breakdown-insight", {}).get("details", {}).get("items", [])
    element = next((item.get("nodeLabel") or item.get("snippet", "") for item in breakdown if item.get("type") == "node"), "")
    return {
        "lighthouse": report["lighthouseVersion"],
        "score": report["categories"]["performance"]["score"],
        **{name: audits[name]["numericValue"] for name, _budget, _unit in TIMING_BUDGETS},
        "kb": round(audits["total-byte-weight"]["numericValue"] / 1024, 1),
        "requests": len(requests),
        "other_origins": foreign,
        "lcp_element": element[:160],
    }


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def median_of(runs: list[dict]) -> dict:
    keys = ["score", "kb", "requests"] + [name for name, _budget, _unit in TIMING_BUDGETS]
    merged = {key: statistics.median(run[key] for run in runs) for key in keys}
    merged["other_origins"] = sorted({url for run in runs for url in run["other_origins"]})
    merged["lcp_element"] = runs[0]["lcp_element"]
    merged["lighthouse"] = runs[0]["lighthouse"]
    return merged


def judge(page: str, kind: str, kb_budget: float, measured: dict) -> list[dict]:
    """One check per budget, each naming the measured value and the limit."""
    checks = [{"name": f"{page}: performance score ≥ {MIN_SCORE:.2f}", "pass": measured["score"] >= MIN_SCORE,
               "detail": measured["score"]}]
    for audit, budget, unit in TIMING_BUDGETS:
        value = measured[audit]
        checks.append({"name": f"{page}: {audit} ≤ {budget}{unit}", "pass": value <= budget,
                       "detail": round(value, 3)})
    checks.append({"name": f"{page}: {kind} transfer ≤ {kb_budget} KB", "pass": measured["kb"] <= kb_budget,
                   "detail": measured["kb"]})
    checks.append({"name": f"{page}: no request to another origin", "pass": not measured["other_origins"],
                   "detail": measured["other_origins"][:5]})
    return checks


def measure(base: str, chrome: str, only: list[str]) -> tuple[list[dict], list[dict]]:
    origin = _origin(base)
    pages, checks = [], []
    for page, kind, kb_budget in PAGES:
        if only and page not in only:
            continue
        url = base + ("" if page == "index.html" else page)
        runs = [summarize(run_lighthouse(url, chrome), origin) for _ in range(RUNS)]
        measured = median_of(runs)
        pages.append({"page": page, "kind": kind, "median": measured, "runs": runs})
        checks += judge(page, kind, kb_budget, measured)
        print(f"{page}: score {measured['score']:.2f}, LCP {measured['largest-contentful-paint']:.0f} ms, "
              f"TBT {measured['total-blocking-time']:.0f} ms, {measured['kb']} KB", flush=True)
    return pages, checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", help="measure a deployed copy instead of dist/ (e.g. the live site)")
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--dist", type=Path, default=DIST, help="serve another copy of the hosted build")
    parser.add_argument("--only", action="append", default=[], help="measure only this page (repeatable)")
    arguments = parser.parse_args()
    chrome = chrome_path()
    server = None if arguments.base_url else static_server.serve(arguments.dist)
    base = arguments.base_url or static_server.base_url(server)
    try:
        pages, checks = measure(base.rstrip("/") + "/", chrome, arguments.only)
    finally:
        if server:
            server.shutdown()
    failures = [check for check in checks if not check["pass"]]
    report = {"passed": not failures, "checks": len(checks), "failures": failures, "base_url": base,
              "lighthouse": pages[0]["median"]["lighthouse"], "runs_per_page": RUNS, "pages": pages, "results": checks}
    evidence.write_report(arguments.report, report, [DIST / page for page, _kind, _kb in PAGES])
    print(json.dumps({"passed": report["passed"], "checks": report["checks"], "failures": failures},
                     ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
