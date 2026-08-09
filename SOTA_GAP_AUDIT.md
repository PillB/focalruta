# Canon 6D San Isidro Planner — SOTA gap audit & architecture decision record

Release date: 2026-08-09

## Executive result

The project now has two explicit deployment targets with one content/behavior model:

1. **Hosted / PWA** — lean HTML + external CSS/data + lazy, lossless WebP diagrams + versioned shell/runtime caching.
2. **Standalone iPhone** — one self-contained HTML for attachment/file-mode use where sibling assets are unreliable.

This prevents the prior optimization conflict where making the attachment reliable made the live site unnecessarily heavy.

## Prioritized gap ranking

| Rank | Gap / root cause | Alternatives compared | Decision implemented | Evidence |
|---|---|---|---|---|
| P0 | 12.24 MB initial HTML because 131 diagrams were embedded as data URIs | A single-file only; B hosted split only; C dual target | **C dual target** | Hosted index ≈107 KB; standalone ≈12.24 MB; 99.1% document reduction |
| P0 | Custom modal semantics/focus | ARIA-only custom trap; native `<dialog>`; full refactor | **Native dialog** for Session Run + shot detail; hardened inert/focus trap for Field Card | W3C modal behavior; post-patch QA 9/9 |
| P0 | Session Run mark state disappeared when localStorage unavailable | localStorage only; memory only; memory + persistence | **Memory working state + best-effort localStorage** | Reproduced in attachment-mode QA; fixed and verified |
| P1 | Optical Lab was calculator-first | numbers only; spatial visualization; inverse/result-first; AR | **Intent presets + near/focus/far band + A/B same-position/same-frame** | Four presets and physical aperture floors tested |
| P1 | No temporal model for six motion effects | static settings; exact renderer; conceptual temporal model | **Motion Lab** calibrated to assignment baselines | 6/6 modes interactive, parameter differential tested |
| P1 | Static composition guide | gallery; interactive sandbox; live-camera CV | **3:2 sandbox** with draggable/keyboard subject + overlays | Pointer/keyboard/toggle testing |
| P1 | Field Card was not tied to selected plan | generic card; full session runner; CV auto-detection | **Session Run Mode** uses plan × subject × time + baseline + criterion | Prev/next/mark + diagram + safety overrides |
| P1 | Dead shot-detail feature: modal code existed but no trigger | remove; restore custom; restore native | **Restore as native detail dialog** | Trigger/detail image validated across all 6 plans |
| P2 | PWA install metadata incomplete | SVG-only icon; PNG fixed sizes + SVG | **192/512 PNG + SVG + apple-touch-icon** | Manifest updated |
| P2 | Monolithic cache behavior | pre-cache everything; network only; shell + runtime SWR | **Small shell + runtime granular asset cache** | SW static gates; non-navigation requests never receive HTML fallback |
| P2 | Large below-fold DOM/images | eager; lazy images; component virtualization | **lazy + async decode + content-visibility** | 120 dynamic diagrams retain parity |
| P3 | Solar/golden-hour planning | static text; NOAA/Meeus local calculator; map/time planner | **Deferred** | Valuable, but not core to assignment and would expand date/location UX |
| P3 | AR camera/FoV overlay | decorative overlay; sensor/device calibration; full AR | **Deferred** | Shipping uncalibrated AR would create false geometric confidence |

## Differential/root-cause analyses

### 1. Hosted performance vs attachment reliability

**Symptom:** the iPhone-safe version worked as an isolated file, but a live deployment would parse a ~12 MB HTML document before the user needed most diagrams.

**Root cause:** the same artifact was being asked to solve two opposing deployment constraints.

**Fix:** dual build. Hosted diagrams are lossless WebP resources requested on demand; the standalone still embeds them.

### 2. Session completion state

**Symptom:** “Mark done” could immediately revert in opaque/file-like browser contexts.

**Root cause:** persistence (`localStorage`) was incorrectly used as the primary in-memory state. When storage access failed, re-render read an empty array.

**Fix:** `RUN_MEMORY` is authoritative for the running session; localStorage is optional persistence.

### 3. Modal accessibility

**Symptom:** Field Card visually behaved modally but background content was not made inert. Shot detail had modal markup/code but no invocation.

**Fix:** Session Run and shot detail now use native `<dialog>`; Field Card explicitly makes the outside document inert, traps focus, supports Escape, and restores focus.

### 4. Optical-learning gap

**Symptom:** users had to understand parameters before knowing what to choose.

**Fix:** presets begin with outcome (deep DoF, shallow portrait, action, zoom burst), then expose parameters. SVG shows near/focus/far and real background location. A/B text explicitly distinguishes same-position focal changes from perspective changes caused by camera relocation.

### 5. Motion-learning gap

**Symptom:** six of the ten assignment outcomes are fundamentally temporal, but the site explained them mostly with static values.

**Fix:** Motion Lab visualizes relative temporal footprint as shutter time, subject motion and tracking quality change. It explicitly labels itself a pedagogical trend model, not an exposure meter.

## Current release invariants

- Canon EOS 6D Mark I; verified lens model names remain canonical.
- 6 plans × 10 shots × 2 subject diagram variants.
- Dog safety overrides remain consistent for ghost and urban long exposure.
- Nadir points upward; cenital points downward.
- Hosted and standalone carry Optical Lab, Motion Lab, Composition Sandbox, Session Run, Field Card and shot detail.
- Exact residential street number is absent.

## QA summary

- Existing exhaustive SOTA matrix: **70/70 PASS**.
- Exact post-patch interaction regression: **9/9 PASS**.
- Hosted architecture/resource gates: **27/27 PASS**.
- Combined: **106/106 PASS**.
- Hosted document size reduction vs standalone: **~99.1%**.

## Deployment blocker

No exact GitHub repository or live URL exists in the provided project, current conversation context, personal-context search, or the authenticated PillB repository list. Searches for a Canon6D/photo-planner repository returned none. The local project is not a Git repository, and `gh` is not installed in the runtime. Therefore this release is **Pages-ready but was not pushed to an unrelated repository**.

## Primary research references

- W3C WAI-ARIA Authoring Practices — Modal Dialog Pattern and HTML `<dialog>` technique.
- W3C WCAG 2.2 — focus/keyboard/target-size guidance.
- web.dev — image performance, lazy loading, async decoding, responsive image guidance.
- MDN — installable PWA requirements, service worker caching and stale-while-revalidate patterns.
- PhotoPills User Guide — FoV/DoF classic, inverse, visual/AR and map planning interaction patterns.
- Canon — DoF/FoV educational material used by the existing project methodology.
