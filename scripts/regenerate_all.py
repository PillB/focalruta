#!/usr/bin/env python3
"""Regenerate every derived artefact, in dependency order, from one entrypoint.

Until now that order lived only in prose in README.md, so "is the committed
output current?" was answered one file at a time — and the answer was wrong
more than once. With this script CI can use the standard pattern:

    python3 scripts/regenerate_all.py && git diff --exit-code

Anything a generator would have changed shows up as a diff and fails the build.

`build_architecture_routes.py` is deliberately excluded: it depends on the live
OSM router, so route data is rebuilt only in a session where that service is
confirmed available. The browser QA reports need a real Chrome and several
minutes, so they run only with --with-browser-qa.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Deterministic, dependency-ordered, no network.
CORE = (
    ("build_architecture_learning_v2.py", "curriculum and video ledger"),
    ("generate_architecture_pages.py", "challenge, wiki, field card, iPhone help"),
    ("build_master.py", "root PhotoPlanner index"),
    ("build_dual_release.py", "dist/canon6d_sota_hosted"),
    # Last: it measures the artefacts every step above produces.
    ("build_state_snapshot.py", "measured half of the state file"),
)

# Need a real Chrome; they fingerprint the artefacts they audit.
BROWSER_QA = (
    ("visual_resource_audit.py", "image, resource and contrast audit"),
    ("optics_accessibility_qa.py", "optical lab accessibility matrix"),
    ("browser_release_qa.py", "browser regression matrix"),
)


def run(script: str, purpose: str) -> int:
    print(f"→ {script} ({purpose})", flush=True)
    completed = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, timeout=3600)
    if completed.returncode != 0:
        print(f"✗ {script} exited {completed.returncode}", flush=True)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-browser-qa", action="store_true", help="also regenerate the Chrome-driven QA reports")
    arguments = parser.parse_args()
    steps = list(CORE) + (list(BROWSER_QA) if arguments.with_browser_qa else [])
    for script, purpose in steps:
        code = run(script, purpose)
        if code != 0:
            return code
    print(f"regenerated {len(steps)} steps", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
