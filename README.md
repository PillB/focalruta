# FocalRuta

An offline-capable, Spanish-language photography field and teaching planner. The plans are solved for a Canon EOS 6D and four lenses; readers with another camera or other lenses set their gear once and every shot also shows the equivalent setting for it. It includes six ten-shot location plans, 120 subject diagrams, a dynamic Optical Decision Lab, motion and composition teaching tools, a pose coach, and a field card in Spanish that works one-handed and offline.

## Live site

GitHub Pages deploys the optimized runtime from `dist/canon6d_sota_hosted`.

## Validation

The release gate (`python3 scripts/verify_release.py`) fails unless five browser QA
reports at the repository root still match the files they audited, byte for byte:

- `CURRENT_BROWSER_QA.json` — 315 browser regression checks across six viewports,
  including a hosted plan page that must work offline after one visit and, on the home
  page and every plan page, no text under 12 px, no control under 44 px and no English
  in the interface
- `OPTICS_ACCESSIBILITY_QA.json` — 22 optical-lab matrix and accessibility checks
- `VISUAL_RESOURCE_QA.json` — 37 image, resource-path, font-floor and contrast checks
  (contrast on gradients is checked at every colour stop)
- `AXE_ACCESSIBILITY_QA.json` — axe-core on all 39 published pages, light phone and
  dark desktop passes, zero violations
- `FIELD_CARD_QA.json` — 48 field card checks on a phone: each plan's settings per light,
  the Lima clock, no JavaScript, print, keyboard, the home page dialog, axe, offline after
  a simulated deploy, and another camera and lenses

Set up with `python3 -m pip install -r requirements-dev.txt` (what CI installs, on
Python 3.11) and, for browser QA, `requirements-qa.txt`.

## Regenerating the architecture photography guide

Generated HTML is build output, never edited by hand: `scripts/verify_architecture.py`
re-renders the page and byte-compares it against the committed file. One entrypoint
runs every generator in dependency order (CI runs it and fails on any diff), then
the gates:

```bash
python3 scripts/regenerate_all.py   # add --with-browser-qa to refresh the QA reports

python3 -m pytest -q
python3 scripts/verify_architecture.py
python3 scripts/verify_release.py
python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'
```

`scripts/build_architecture_routes.py` is deliberately **not** part of that loop:
it depends on a live OSM router, so route data is regenerated only in a session
where that service is confirmed available.

Browser QA is not run by CI. Point `FOCALRUTA_CHROME` at a Chromium binary and
`FOCALRUTA_AXE` at axe-core 4.10.3's `axe.min.js`, serve two roots and run the
scripts in `scripts/` listed under `BROWSER_QA` in `regenerate_all.py` and each
`tests/architecture/browser_*.py`:

```bash
python3 -m http.server 8766 &                                  # repo root
(cd dist/canon6d_sota_hosted && python3 -m http.server 8777) &  # hosted build
```

`browser_architecture_release_qa.py` must run against the **hosted** root (8777):
only that build registers the service worker, and `navigator.serviceWorker.ready`
never resolves without one — it hangs rather than failing. The scripts check six
viewports, keyboard and focus behaviour, reduced motion, offline and no-JS
fallbacks, and — for the learning labs — twenty-two physical invariants measured
against the rendered DOM.

All camera optics live in one place, `scripts/optics_physics.py`. The diagram
generators and the interactive labs both import it, so there is a single
definition of field of view, projection, shadow geometry and depth of field.

See [SOTA_QA_SUMMARY.md](SOTA_QA_SUMMARY.md) for implementation and validation details.
