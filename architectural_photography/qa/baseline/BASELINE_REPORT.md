# Round 0 zero-change baseline

- Commit: `9a415311f8d34772a6391193434bbf22c7b9af5b`
- Production edits before capture: none.
- `python3 scripts/verify_release.py`: PASS.
- Six-view local hosted/PWA capture: PASS at 390×844, 430×932, 844×390, 932×430, 820×1000, and 1440×1100.
- Each captured viewport: HTTP 200, no horizontal overflow, no page errors, no console errors, no failed resources, keyboard focus reachable, service worker registered and controlling.
- Screenshots: `home-<width>x<height>.png` in this directory.
- Existing `scripts/visual_resource_audit.py`: FAIL on a pre-existing inactive subject-toggle contrast defect (white text against near-white background, measured 1.05:1).
- Existing `scripts/browser_release_qa.py` and `scripts/optics_accessibility_qa.py`: assertions ran, but the managed macOS runner hung during `browser.close()`; interrupted teardown is not recorded as a pass.
- Complexity chore: BLOCKED because `python3 -m ruff` is not installed.

The contrast issue and teardown behavior predate architecture implementation and must not be attributed to the new challenge. Architecture work may not regress any passing baseline invariant.
