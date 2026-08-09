# Canon 6D Planner — Regression & Merge Audit

## Executive result

The master build intentionally merges the strongest parts of the earliest planner with the iPhone/Field-Card build instead of choosing one branch. The earliest build was stronger for learning and planning; the recent build was stronger for mobile execution. The master has both.

| Capability | Earliest planner | Recent iPhone build | Master |
|---|---:|---:|---:|
| Complete plans | 5 | 4 | **6** |
| Required shots per plan | 10 | 10 | **10** |
| Plan diagrams (human + dog) | ~100 | 80 | **120** |
| Home / Building Lab | Yes | Lost | **Recovered** |
| Abtao / district-financial route | Yes | Lost | **Recovered** |
| Optical FoV/DoF learning lab | Yes | Reduced/lost | **Recovered + constrained by real lens maxima** |
| Explicit PoseArt coaching | Yes | Reduced/lost | **Recovered as interactive Pose Coach** |
| Sources / methodology | Yes | Lost | **Recovered and corrected** |
| Human / dog switch | Yes | Yes | **Yes + safety-aware exceptions** |
| Day / afternoon / night | No | Yes | **Yes** |
| Quick Start | No | Yes | **Yes** |
| Lens comparison diagrams | Limited | Yes | **Yes + perspective wording corrected** |
| Composition examples | Limited | Yes | **Yes** |
| iPhone standalone | No | Yes | **Yes** |
| Mobile bottom navigation | No | Yes | **Yes** |
| Integrated Field Card | No | Yes | **Yes, canonical baseline** |
| Offline/PWA hosted mode | No | No | **Added** |
| Individual offline plan pages | Yes | Regressed/stale | **6 regenerated from canonical source** |

## Corrections propagated everywhere

1. **Actual gear**: EF 35mm f/2 IS USM; EF 50mm f/1.8 STM; EF 85mm f/1.8 USM; EF 35–80mm f/4–5.6 III; EOS 6D Mark I 35.8×23.9 mm sensor.
2. **Nadir / cenital**: nadir = camera below pointing vertically up; cenital = camera above pointing vertically down.
3. **Perspective**: camera position/distance determines geometric perspective. Focal length changes angle of view and framing; the familiar “telephoto compression” normally appears because the photographer moves farther back to preserve framing.
4. **Fair prime comparison**: same camera position and common f/2 for 35/50/85 comparisons. 85mm f/1.8 is shown separately when demonstrating its true maximum aperture.
5. **Dog safety/effect semantics**: ghost = controlled human mover with dog out; urban traffic long exposure = dog out/no subject; lightpainting avoids strong direct light into eyes.
6. **Field Card baseline** is the operational starting point. Plan-specific settings may differ because of scene/light and are labelled as variations, not contradictory “truths”.
7. **Zooming** uses the actual 35–80 zoom; camera remains fixed while the zoom ring moves.

## Master information architecture

### Plan / learn
- Quick Start
- Actual equipment cards
- Optical Lab: lens, aperture, camera→subject distance, subject→background separation, FoV, frame width, DoF, hyperfocal
- Lens comparison
- Composition examples
- Camera-angle guide
- Pose Coach / PoseArt cues
- Sources and methodology

### Execute in the field
- Six complete routes
- Human/dog and time-of-day switches
- 10 shot cards with diagram, Field Card baseline, scene-specific variation, pose/action and safety
- Integrated Field Card with progress persistence
- Individual plan pages

### Delivery modes
- Self-contained iPhone master HTML
- Hosted/PWA project build
- Printable/offline Field Card
- Six self-contained plan pages

## Recovered plans

- **Plan E — Home / Building Lab**: weather-proof, controlled and repeatable; especially useful for ghost, lightpainting and A/B learning.
- **Plan F — Abtao / Distrito Financiero**: close-to-base urban architecture, park, geometry, panning and traffic-light opportunities.

## Regression gates

The final QA must fail the build if any of these regressions reappear:
- fewer than 6 plans or any plan with fewer than 10 shots;
- fewer than 120 plan diagrams;
- wrong lens maximum aperture/model;
- nadir/cenital reversal;
- dog recommended as moving ghost subject or beside urban traffic long exposure;
- stale “4 plans / 80 diagrams” copy;
- exact residential street number in public HTML;
- broken iPhone horizontal layout;
- Field Card, optics lab, Pose Coach, plan switch, subject switch or time switch not interactive;
- standalone plan page depending on sibling CSS/images.

The generated plan pages now also expose the canonical gear, perspective, nadir/cenital, dog-safety, zooming and baseline-vs-variation corrections in a visible disclosure. `scripts/verify_release.py` fails if any one of these corrections, routes, subject/time states or diagrams is lost from a delivery target.
