# FocalRuta — Planner Fotográfico Maestro · San Isidro, Lima

Production master combining the strongest learning features of the first planner with the iPhone/Field-Card workflow of the latest build.

## What is now canonical

- **Camera:** Canon EOS 6D Mark I · full-frame CMOS 35.8×23.9 mm · 20.2 MP · 11 AF points · ~4.5 fps.
- **Lenses:** EF 35mm f/2 IS USM; EF 50mm f/1.8 STM; EF 85mm f/1.8 USM; EF 35–80mm f/4–5.6 III.
- **6 complete plans × 10 required photographs = 60 planned shots.**
- **120 plan diagrams** (human + dog/safety-aware variant), plus 3 lens-comparison and 8 composition diagrams.
- Residential addresses and home-relative route distances are intentionally excluded from public artifacts.

## Six routes

| Plan | Concept | Best use |
|---|---|---|
| A | El Olivar | strongest nature / layers / portrait learning |
| B | Malecón / Costa Verde | open backgrounds, movement, golden hour |
| C | San Isidro nocturno / calle urbana | nearby night effects |
| D | Centro Histórico | architecture and urban narrative |
| E | Home / Building Lab | weather-proof, repeatable controlled experiments |
| F | Abtao / Distrito Financiero | nearby urban geometry, park, panning and light trails |

Every plan still covers: 2× mucha PDC, 2× poca PDC, congelado, barrido, fantasma, lightpainting, larga exposición and zooming.

## Key master features

1. **Integrated Field Card** — operational baseline, 10 checkable shots, Rescue, Composition and Equipment tabs, local progress.
2. **Optical Lab** — interactive FoV, frame width, DoF and hyperfocal. Aperture floor follows the selected real lens.
3. **Pose Coach** — recovered PoseArt-style families and field cues for S-Curve, Power Stance, Wall Lean, Hip Shift, Model Walk, Arms Overhead, Soft Sit and Look Back.
4. **Six plans + two subject modes + three time windows**.
5. **Safety-aware subject logic** — ghost uses a person with dog out; traffic long exposure keeps dog out/no subject.
6. **Correct angle semantics** — nadir points up; cenital points down.
7. **Correct perspective teaching** — perspective is controlled by camera position; focal length controls angle of view/framing.
8. **iPhone-safe standalone master** plus hosted/PWA mode and six self-contained individual plan pages.

## Files

```text
index.html                     canonical single-file/standalone master source
field_card.html                standalone field card
manifest.webmanifest           hosted install metadata
sw.js                          hosted offline/runtime cache
assets/                        production CSS + app icon
data/                          canonical JSON + Field Card fragments
plans/                         plan_a.html … plan_f.html (self-contained)
diagrams/                      120 plan + 11 teaching PNGs
scripts/
  plans_data.py                canonical gear/plans/baselines
  generate_diagrams.py         120 plan diagrams
  generate_lens_comparison.py  3 fair lens comparisons
  generate_composition_examples.py
  generate_plan_pages.py       six self-contained plan pages
  generate_field_card.py
  integrate_field_card.py
  build_dual_release.py        builds lean hosted + standalone targets under dist/
  verify_release.py            cross-target correction/feature parity gate
dist/canon6d_sota_hosted/      deployable lean Pages/PWA release
REGRESSION_AUDIT.md            first-vs-latest-vs-master audit
MASTER_QA.md                   final validation report (generated at release)
```

## Rebuild order

```bash
python scripts/generate_diagrams.py
python scripts/generate_lens_comparison.py
python scripts/generate_composition_examples.py
python scripts/generate_field_card.py
python scripts/generate_plan_pages.py
```

`scripts/plans_data.py` generates `data/plans.json`, which is the canonical runtime snapshot. Avoid hand-editing individual plan pages: regenerate them. `scripts/verify_release.py` checks generated-target parity.

## Optical conventions

- FoV uses the EOS 6D 35.8×23.9 mm imaging area.
- DoF uses CoC 0.030 mm as a planning convention, not a hard physical boundary.
- A fair focal-length comparison from the same camera position uses a common aperture where possible (f/2 for the three primes).
- Subject→background distance is treated as an independent design variable.

## Public deployment

See `DEPLOY_GITHUB_PAGES.md`. Build the deployable tree with `python3 scripts/build_dual_release.py`; the result is `dist/canon6d_sota_hosted`. Its hosted target includes a manifest and service worker, while `FocalRuta_STANDALONE.html` keeps attachment/file-mode reliability.
