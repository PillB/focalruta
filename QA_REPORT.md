# Current QA — Canon 6D San Isidro Planner

Validated: 2026-08-09. This report supersedes the historical four-plan/80-diagram QA result.

## Current release scope

- 6 plans × 10 assignment photographs.
- 2 subject modes × 3 time windows = 36 plan/subject/time route states.
- 120 plan diagrams plus 11 teaching diagrams.
- Standalone iPhone master, lean hosted/PWA target, standalone Field Card, six self-contained plan pages and a downloadable support bundle.
- Optical Decision Lab, Motion Lab, Composition Sandbox, Pose Coach, Session Run and enlarged shot detail.

## Correction parity

The canonical equipment, sensor, perspective, nadir/cenital, dog-safety, lightpainting, zooming and Field-Card-baseline rules are checked in canonical data and exposed visibly in every individual plan page. Hosted plan/data copies and the standalone master are byte-compared with their source artifacts.

## Current validation result

`PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_release.py` passes with no failures.

Fresh headless Chrome validation is recorded in `CURRENT_BROWSER_QA.json`: **234/234 checks passed** across the standalone master, lean hosted page and six standalone plans:

- all 6 plans × 2 subjects × 3 times loaded ten cards and ten diagrams in each master target;
- every Motion Lab mode produced different low/high shutter readings after the saturation fix;
- Composition Sandbox keyboard movement worked;
- Session Run, Field Card and enlarged shot detail opened and dismissed;
- Field Card made background content inert;
- no uncaught page errors were captured.

All six standalone plan pages separately passed their six subject/time combinations, ten rendered cards, visible correction-panel content, mobile overflow and zero page errors.

## Deployment status

The release is complete locally under `dist/canon6d_sota_hosted`. Public deployment cannot be validated until the intended GitHub repository or live URL is identified. This workspace is not a Git checkout; unrelated sibling repositories are deliberately excluded.
