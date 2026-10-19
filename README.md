# FocalRuta

An offline-capable, Spanish-language photography field and teaching planner. The plans are solved for a Canon EOS 6D and four lenses; readers with another camera or other lenses set their gear once and every shot also shows the equivalent setting for it. It includes six ten-shot location plans, 120 subject diagrams, a dynamic Optical Decision Lab, motion and composition teaching tools, a pose coach, and a field card in Spanish that works one-handed and offline.

## Live site

GitHub Pages deploys the optimized runtime from `dist/canon6d_sota_hosted`
(`.github/workflows/pages.yml`). After every deploy, and every morning at 06:17 in
Lima, `.github/workflows/live-check.yml` waits until the live site serves that
commit's build, then runs `scripts/live_pages_qa.py` and the speed budgets against
it; a failed run emails the repository owner.

## Privacy

No page asks another site for anything: no fonts, scripts, analytics or trackers,
and the speed and live checks fail if one does. Errors are kept only on the reader's
device (`assets/diagnostics.js`, shown at the foot of the home page) and leave it only
if the reader copies the log or sends the prefilled GitHub report themselves. The log
names a page by its path on the site, or only by its file name when opened from a file,
and drops quoted text from messages, which can be what the reader typed.

## Validation

The release gate (`python3 scripts/verify_release.py`) fails unless six browser QA
reports at the repository root still match the files they audited, byte for byte:

- `CURRENT_BROWSER_QA.json` — 422 browser regression checks across seven viewports
  from 320 px wide, including a hosted plan page that must work offline after one visit;
  on the home page and every plan page, no text under 12 px, no control under 44 px, no
  English in the interface, nothing cut off at the edges and numbers written with a
  decimal point, also with a reader's own lenses; dialogs that give focus back to the
  button that opened them; and, offline, a page never saved opening the home page with
  a note naming it
- `OPTICS_ACCESSIBILITY_QA.json` — 22 optical-lab matrix and accessibility checks
- `VISUAL_RESOURCE_QA.json` — 37 image, resource-path, font-floor and contrast checks
  (contrast on gradients is checked at every colour stop)
- `AXE_ACCESSIBILITY_QA.json` — axe-core on all 39 published pages and the home page's
  offline notice, light phone and dark desktop passes, zero violations
- `FIELD_CARD_QA.json` — 56 field card checks on a phone: each plan's settings per light,
  the Lima clock, no JavaScript, print, keyboard, the home page dialog, axe, offline after
  rehearsed deploys (an upgrade from the worker live at 9cd3044, the HTTP cache Pages
  keeps for 10 minutes), and another camera and lenses
- `PERF_BUDGET_QA.json` — 112 speed checks: Lighthouse on a simulated phone and slow
  4G network, median of three runs, for the home page, the field card, all six plan
  pages and every challenge page type; Lighthouse's "good" marks for every timing,
  a byte budget per page type and no request to another origin

Set up with `python3 -m pip install -r requirements-dev.txt` (what CI installs, on
Python 3.11). For browser QA add `requirements-qa.txt`, `npm ci` (axe-core and
Lighthouse, pinned in `package-lock.json`) and `python3 -m playwright install chromium`.

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

CI runs every browser suite on every pull request (`.github/workflows/quality.yml`):
each script listed under `BROWSER_QA` in `regenerate_all.py`, and each
`tests/architecture/browser_*.py`. They find Chromium by themselves
(`qa_matrix.browser_options`: `FOCALRUTA_CHROME` if set, else Chrome on a Mac, else
Playwright's Chromium) and axe-core in `node_modules` (or `FOCALRUTA_AXE`). The
architecture suites need two roots served:

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
