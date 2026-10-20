#!/usr/bin/env python3
"""One responsive matrix, one way to bound an awaited browser expression, and
one way to find the browser and axe-core on any machine.

Two duplication defects lived here. Four browser scripts each carried their own
copy of the N01 viewport tuple, and two more carried a *different, shorter* one
that also tested 1440×1000 — a size N01 does not name — so "the responsive
matrix" was three lists and the mandated coverage was silently incomplete.

Separately, `page.evaluate` has no promise timeout: its `timeout` argument
covers element availability, not the awaited promise
(microsoft/playwright#13253). `navigator.serviceWorker.ready` never rejects by
specification — it waits indefinitely for an active worker — so awaiting it on a
page that registers no worker blocks the whole run with no error. The fix has to
live inside the evaluated JavaScript, where a race can actually reject.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
AXE_VERSION = "4.10.3"

# N01: the responsive matrix every browser-facing round must cover.
REQUIRED_VIEWPORTS: tuple[tuple[int, int], ...] = (
    (320, 640),  # WCAG 1.4.10 Reflow: content must work at 320 CSS px wide (V18)
    (390, 844),
    (430, 932),
    (844, 390),
    (932, 430),
    (820, 1000),
    (1440, 1100),
)

DEFAULT_ACTION_TIMEOUT_MS = 30_000
DEFAULT_EVALUATE_TIMEOUT_MS = 20_000


def bounded_async(expression: str, timeout_ms: int = DEFAULT_EVALUATE_TIMEOUT_MS) -> str:
    """Wrap an async browser expression so a promise that never settles rejects.

    `expression` is JavaScript that evaluates to a promise. The result races a
    timer, so the browser rejects and Playwright raises instead of blocking.
    """
    return (
        "async()=>{const timeout=new Promise((_,reject)=>setTimeout("
        f"()=>reject(new Error('browser expression exceeded {timeout_ms} ms')),{timeout_ms}));"
        f"return Promise.race([(async()=>({expression}))(),timeout]);}}"
    )


def harden(context) -> None:
    """Give a Playwright context an explicit default instead of an implicit one."""
    context.set_default_timeout(DEFAULT_ACTION_TIMEOUT_MS)
    context.set_default_navigation_timeout(DEFAULT_ACTION_TIMEOUT_MS)


def browser_options() -> dict:
    """How to launch Chromium on this machine, decided once for every suite.

    FOCALRUTA_CHROME wins when set, and must exist: a typo would otherwise
    surface as a Playwright stack trace minutes into a run. Without it, the
    owner's Mac uses its installed Chrome, and anything else (CI, Linux) uses
    the Chromium that `python -m playwright install chromium` downloaded.
    """
    configured = os.environ.get("FOCALRUTA_CHROME", "")
    if configured:
        if not Path(configured).is_file():
            sys.exit(f"FOCALRUTA_CHROME points at {configured}, which is not a file")
        return {"executable_path": configured}
    return {"executable_path": MAC_CHROME} if Path(MAC_CHROME).is_file() else {}


def axe_source() -> str:
    """axe-core's source: FOCALRUTA_AXE when set, else the copy `npm ci` pinned."""
    configured = os.environ.get("FOCALRUTA_AXE", "")
    path = Path(configured) if configured else ROOT / "node_modules/axe-core/axe.min.js"
    if not path.is_file():
        sys.exit(f"axe-core {AXE_VERSION} not found at {path}: run `npm ci` or point FOCALRUTA_AXE at axe.min.js")
    return path.read_text(encoding="utf-8")
