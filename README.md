# FocalRuta

An offline-capable, Spanish-language photography field and teaching planner for a full-frame camera and a specific four-lens kit. It includes six ten-shot location plans, 120 subject diagrams, a dynamic Optical Decision Lab, motion and composition teaching tools, a pose coach, and an accessible Field Card.

## Live site

GitHub Pages deploys the optimized runtime from `dist/canon6d_sota_hosted`.

## Validation

- 234/234 current browser regression checks
- 16/16 Optical Decision Lab matrix and accessibility checks, covering more than 500 parameter combinations per release target
- 37/37 image, resource-path, font-floor, and contrast checks
- 120/120 dynamic shot diagrams decoded in both main release targets

Run the release gate with:

```bash
python3 scripts/verify_release.py
```

## Regenerating the Arquitectura en Foco challenge

Generated HTML is build output, never edited by hand: `scripts/verify_architecture.py`
re-renders the page and byte-compares it against the committed file. Run the
generators in dependency order, then the gates:

```bash
python3 scripts/build_architecture_learning_v2.py   # curriculum + video ledger
python3 scripts/generate_architecture_pages.py      # challenge, wiki, field card, iPhone help
python3 scripts/build_dual_release.py               # dist/canon6d_sota_hosted (what Pages serves)

python3 -m pytest -q
python3 scripts/verify_architecture.py
python3 scripts/verify_release.py
python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'
```

`scripts/build_architecture_routes.py` is deliberately **not** part of that loop:
it depends on a live OSM router, so route data is regenerated only in a session
where that service is confirmed available.

Browser QA is not run by CI. Serve two roots and run each script in
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
