# Canon EOS 6D Planner — MASTER QA

Release date: 2026-08-09

## Result

**PASS**

- Static/canonical regression gates: **46/46 passed**.
- Final rendered Playwright release matrix: **112/112 passed**.
- Final diagrams: **120 plan variants + 11 teaching diagrams = 131 PNGs**.
- Complete routes: **6 plans × 10 required shots = 60 planned shots**.

## Rendered browser matrix

Master page rendered and exercised at:
- iPhone compact: 390×844, touch enabled.
- iPhone large: 430×932, touch enabled.
- Tablet: 820×1000.
- Desktop: 1440×1000.

The six standalone plan pages were also rendered at 390×844 and 1280×900; the standalone Field Card was rendered at 390×844 and 1200×900.

Validated interactions include plan selection, Human/Dog switch, Day/Night switch, Field Card open/close, 10 Field Card rows, 4 Field Card tabs, optical-lab output, real aperture floors, Pose Coach, mobile bottom navigation, dog-safety exceptions and plan diagrams.

Final release criteria: zero horizontal overflow, zero console errors, zero uncaught page errors and lazy-loaded diagrams explicitly decoded before image assertions.

## Canonical corrections verified

- EOS 6D sensor: 35.8×23.9 mm.
- EF 35mm f/2 IS USM; EF 50mm f/1.8 STM; EF 85mm f/1.8 USM; EF 35–80mm f/4–5.6 III.
- Nadir points vertically upward; cenital points vertically downward.
- Geometric perspective is taught as a camera-position effect; focal length controls angle of view/framing.
- Field Card baseline and plan-specific variations are labelled separately.
- Dog mode: ghost uses a controlled human mover with dog out; urban long exposure has no dog/subject.
- Exact residential street number is excluded from public output.

## PWA / hosted-mode checks

- `manifest.webmanifest` parses as JSON and uses `display: standalone`.
- `sw.js` passes Node syntax validation.
- Service worker cache version is `canon6d-master-v2`.
- Navigation fallback is scoped to navigation requests; failed image/CSS requests are not replaced by HTML.
- Master, Field Card and all six hosted plan pages reference the manifest/service worker.
- GitHub Pages workflow stages only runtime site assets into `_site`.

Service-worker lifecycle itself requires a real HTTP/HTTPS origin. The render QA used the fully self-contained HTML through Playwright `set_content()` because this artifact runtime blocks local server/file navigation; PWA structure/syntax was therefore validated separately.

## Regression found during this audit

A rerun of the Field Card integrator exposed an overly broad removal expression that could delete the Field Card DOM, shot modal and mobile bottom navigation while leaving their CSS/JS behind. The integrator was rewritten to use bounded/idempotent markers. A subsequent render confirmed the three DOM blocks and the full release matrix passes.

## Reports

- `REGRESSION_AUDIT.md` — earliest vs recent vs master feature comparison.
- Release static JSON: `canon6d_master_static_release.json` (distributed alongside the downloadable release).
- Release Playwright JSON: `release_playwright.json` (distributed alongside the downloadable release).
