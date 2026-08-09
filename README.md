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

See [SOTA_QA_SUMMARY.md](SOTA_QA_SUMMARY.md) for implementation and validation details.
