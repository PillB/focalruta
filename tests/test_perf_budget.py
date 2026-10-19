"""The speed budgets judge what they claim to, on every page type (X02).

The browser half is scripts/perf_budget_qa.py, which runs Lighthouse; these
tests hold its arithmetic, its page list and its Pages-like server.
"""
from __future__ import annotations

import gzip
import http.client
import os
import sys
import time
import types
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import deploy_rehearsal  # noqa: E402
import perf_budget_qa  # noqa: E402
import static_server  # noqa: E402

DIST = ROOT / "dist/canon6d_sota_hosted"


def lighthouse_report(score=0.99, bytes=100 * 1024, extra_urls=(), **metrics) -> dict:
    """The parts of a Lighthouse 13 report the budget reads, healthy unless told otherwise."""
    values = {"first-contentful-paint": 1000, "largest-contentful-paint": 1200, "total-blocking-time": 50,
              "cumulative-layout-shift": 0.01, "speed-index": 1500, **metrics}
    requests = [{"url": "http://127.0.0.1:9/index.html"}, {"url": "data:image/svg+xml;base64,AAAA"}]
    audits = {name: {"numericValue": value} for name, value in values.items()}
    audits["total-byte-weight"] = {"numericValue": bytes}
    audits["network-requests"] = {"details": {"items": requests + [{"url": url} for url in extra_urls]}}
    audits["lcp-breakdown-insight"] = {"details": {"items": [{"type": "table"}, {"type": "node", "nodeLabel": "Fotografía"}]}}
    return {"lighthouseVersion": "13.5.0", "categories": {"performance": {"score": score}}, "audits": audits}


def failing(report: dict, kb_budget: float = 180) -> list[str]:
    measured = perf_budget_qa.median_of([perf_budget_qa.summarize(report, "http://127.0.0.1:9")] * 3)
    return [check["name"] for check in perf_budget_qa.judge("index.html", "home", kb_budget, measured) if not check["pass"]]


def test_x02_a_page_at_every_budget_passes_and_just_over_fails():
    at_budget = {name: budget for name, budget, _unit in perf_budget_qa.TIMING_BUDGETS}
    assert failing(lighthouse_report(**at_budget, score=0.90, bytes=180 * 1024)) == []
    for name, budget, _unit in perf_budget_qa.TIMING_BUDGETS:
        over = budget * 1.01 if budget < 1 else budget + 1
        assert failing(lighthouse_report(**{name: over})) == [f"index.html: {name} ≤ {budget}{_unit}"]
    assert failing(lighthouse_report(score=0.89)) == ["index.html: performance score ≥ 0.90"]
    assert failing(lighthouse_report(bytes=181 * 1024)) == ["index.html: home transfer ≤ 180 KB"]


def test_x02_any_request_to_another_origin_fails_but_inline_data_does_not():
    report = lighthouse_report(extra_urls=["https://tracker.example/pixel.js"])
    assert failing(report) == ["index.html: no request to another origin"]
    assert failing(lighthouse_report()) == []


def test_x02_the_median_of_three_runs_is_judged_not_the_worst_or_best():
    runs = [perf_budget_qa.summarize(lighthouse_report(**{"total-blocking-time": value}), "http://127.0.0.1:9")
            for value in (40, 900, 150)]
    assert perf_budget_qa.median_of(runs)["total-blocking-time"] == 150


def test_x02_every_page_type_the_site_ships_has_a_budget():
    budgeted = {page for page, _kind, _kb in perf_budget_qa.PAGES}
    shipped = {path.relative_to(DIST).as_posix() for path in DIST.rglob("*.html")}
    assert budgeted <= shipped, f"budgets for pages that do not exist: {sorted(budgeted - shipped)}"
    unbudgeted = shipped - budgeted - {"FocalRuta_STANDALONE.html"}
    # The 25 route maps share one generator and one template; barranco-tour-1 stands for them.
    assert all(page.startswith("challenges/arquitectura-en-foco/maps/") for page in unbudgeted), sorted(unbudgeted)
    assert {"index.html", "field_card.html", "404.html"} <= budgeted
    assert sum(page.startswith("plans/") for page in budgeted) == 6


def test_x02_the_local_server_compresses_like_pages_and_mounts_a_prefix():
    server = static_server.serve(DIST, "/focalruta")
    base = static_server.base_url(server, "/focalruta")
    try:
        request = urllib.request.Request(base, headers={"Accept-Encoding": "gzip"})
        with urllib.request.urlopen(request) as response:
            assert response.headers["Content-Encoding"] == "gzip"
            assert response.headers["Cache-Control"] == "max-age=600"
            assert gzip.decompress(response.read()) == (DIST / "index.html").read_bytes()
        with urllib.request.urlopen(base + "index.html") as response:
            assert response.headers["Content-Encoding"] is None
            assert response.read() == (DIST / "index.html").read_bytes()
        image = next((DIST / "diagrams-webp").glob("*.webp"))
        request = urllib.request.Request(base + "diagrams-webp/" + image.name, headers={"Accept-Encoding": "gzip"})
        with urllib.request.urlopen(request) as response:
            assert response.headers["Content-Encoding"] is None, "images are already compressed"
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/index.html")
            outside = 200
        except urllib.error.HTTPError as error:
            outside = error.code
        assert outside == 404
    finally:
        server.shutdown()


def fetch(url: str, **headers):
    request = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", **headers})
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.headers, gzip.decompress(response.read())
    except urllib.error.HTTPError as error:
        return error.code, error.headers, b""


def test_x02_the_deploy_rehearsals_see_the_same_pages_as_the_speed_check(tmp_path):
    """One Pages for the speed check and the deploy rehearsals (V16, V17): gzip,
    max-age=600, and a validator that answers 304 only while the file is unchanged,
    even when the next build was copied with the same modification times."""
    sites = []
    for name in ("anterior", "siguiente"):
        site = tmp_path / name
        site.mkdir()
        (site / "index.html").write_text(f"<!doctype html><title>{name}</title>", encoding="utf-8")
        os.utime(site / "index.html", (1_700_000_000, 1_700_000_000))
        sites.append(site)
    pages = deploy_rehearsal.Pages(sites[0])
    try:
        status, headers, body = fetch(pages.base)
        assert (status, headers["Content-Encoding"], headers["Cache-Control"]) == (200, "gzip", "max-age=600")
        assert body == (sites[0] / "index.html").read_bytes() and headers["ETag"]
        revalidate = {"If-None-Match": headers["ETag"], "If-Modified-Since": "Wed, 01 Jan 2031 00:00:00 GMT"}
        assert fetch(pages.base, **revalidate)[0] == 304
        pages.deploy(sites[1])
        status, _headers, body = fetch(pages.base, **revalidate)
        assert (status, body) == (200, (sites[1] / "index.html").read_bytes())
    finally:
        pages.stop()


def test_v16_a_connection_opened_before_a_deploy_gets_the_new_build(tmp_path):
    """Red team on PR #21, F1: Chromium opens sockets before it needs them. The rehearsal
    server chose the build when it accepted a connection, so a request sent after a deploy
    on a socket opened before it got the last build, and the field card's upgrade checks
    saw the last build's sw.js and files. Pages answers each request from what it serves now."""
    sites = []
    for name in ("anterior", "siguiente"):
        site = tmp_path / name
        site.mkdir()
        (site / "sw.js").write_text(f"const VERSION='{name}';", encoding="utf-8")
        sites.append(site)
    pages = deploy_rehearsal.Pages(sites[0])
    try:
        early = http.client.HTTPConnection("127.0.0.1", pages.server.server_address[1], timeout=10)
        early.connect()
        time.sleep(0.3)  # let the server accept it while the last build is still the one served
        pages.deploy(sites[1])
        early.request("GET", "/focalruta/sw.js")
        assert early.getresponse().read() == (sites[1] / "sw.js").read_bytes()
        early.close()
    finally:
        pages.stop()


def test_x01_a_missing_chromium_stops_the_speed_check_with_the_reason(monkeypatch, tmp_path):
    """Playwright names the Chromium build it expects; when that build is not
    installed, the run stops before serving anything and says what to do, not
    with a chrome-launcher stack trace from inside Lighthouse. Playwright itself
    is stood in for, so the check also runs where it is not installed (CI's
    lint-and-test job)."""
    class Missing:
        def __enter__(self):
            return type("P", (), {"chromium": type("C", (), {"executable_path": str(tmp_path / "chromium-0000/chrome")})})

        def __exit__(self, *exc):
            return False

    monkeypatch.delenv("FOCALRUTA_CHROME", raising=False)
    monkeypatch.setattr(perf_budget_qa.qa_matrix, "MAC_CHROME", str(tmp_path / "no-mac-chrome"))
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = Missing
    monkeypatch.setitem(sys.modules, "playwright", types.ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)
    with pytest.raises(SystemExit) as stopped:
        perf_budget_qa.chrome_path()
    assert "chromium-0000" in str(stopped.value) and "playwright install chromium" in str(stopped.value)


def test_x02_another_build_is_fingerprinted_as_itself_and_an_unknown_page_is_named(monkeypatch, tmp_path):
    """Red team on PR #21, F7: `--dist` measured one tree and fingerprinted dist/, so the
    report vouched for files it never served; `--only` with a page the check does not know
    crashed on an empty result instead of saying which pages it knows."""
    other = tmp_path / "otra"
    other.mkdir()
    (other / "index.html").write_text("<!doctype html><title>otra</title>", encoding="utf-8")
    written = {}
    monkeypatch.setattr(perf_budget_qa, "chrome_path", lambda: "chrome")
    monkeypatch.setattr(perf_budget_qa, "run_lighthouse", lambda url, chrome: {"stub": url})
    monkeypatch.setattr(perf_budget_qa, "summarize", lambda result, origin: {"lighthouse": "13.5.0", "lcp_element": "h1", "score": 1.0, "kb": 1, "requests": 1,
                                                                            "other_origins": [],
                                                                            **{name: 0 for name, _b, _u in perf_budget_qa.TIMING_BUDGETS}})
    monkeypatch.setattr(perf_budget_qa.evidence, "write_report", lambda path, report, audited: written.update(audited=list(audited)))
    monkeypatch.setattr(sys, "argv", ["perf_budget_qa.py", "--dist", str(other), "--only", "index.html", "--report", str(tmp_path / "r.json")])
    perf_budget_qa.main()
    assert written["audited"] and all(Path(path).is_relative_to(other) for path in written["audited"]), written["audited"][:2]
    monkeypatch.setattr(sys, "argv", ["perf_budget_qa.py", "--only", "plans/plan_z.html"])
    with pytest.raises(SystemExit) as stopped:
        perf_budget_qa.main()
    assert stopped.value.code == 2
