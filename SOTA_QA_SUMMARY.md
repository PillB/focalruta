# SOTA QA summary

- `canon6d_sota_qa/standalone_playwright.json`: 70/70 PASS — 4 responsive breakpoints, full 36 plan×subject×time matrix, Optical presets, physical aperture limits, 6 Motion modes, Composition keyboard/toggles, Session Run, Field Card and errors/overflow.
- `canon6d_sota_qa/postpatch_qa.json`: 9/9 PASS — exact final Field Card inert/focus behavior, restored native shot-detail across six plans, Session Run storage fallback.
- `canon6d_sota_qa/hosted_static_qa.json`: 27/27 PASS — hosted resource graph, 120 dynamic + 131 total WebPs, source-data parity, service-worker policies, modules in both targets, privacy and size reduction.

Browser note: this execution environment blocks HTTP localhost navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`), so the hosted service-worker lifecycle could not be exercised end-to-end in Chromium here. Browser functionality was therefore exhaustively tested on the exact standalone runtime (same application logic/CSS), while the hosted resource graph/SW policy was validated statically. A real live URL remains the final required environment-level test once a repository target exists.

## 2026-08-09 parity remediation

- Added `scripts/verify_release.py` as a repeatable release gate for the exact assignment matrix, 6 plans, 36 plan/subject/time data states, canonical gear, angle and perspective corrections, dog safety overrides, recovered first-version features, privacy and all 120 route diagrams.
- Added a visible “Criterios canónicos” panel to all six standalone plan pages so Field Card corrections are no longer implicit in embedded JSON only.
- Recalibrated Motion Lab. The earlier linear meter saturated at 100% for multiple long-exposure modes even though the old QA called those controls differential. The new logarithmic teaching scale produces distinct readings across every mode and explicitly states that it is conceptual, not a pixel/exposure prediction.
- Rebuilt the dual release under `dist/canon6d_sota_hosted`: hosted HTML 107,158 bytes; standalone HTML 12,244,373 bytes; 131 lossless WebPs totaling 8,597,302 bytes.
- Fresh headless Chrome pass on both master and lean hosted pages: six plans × ten shots loaded, all six Motion modes produced distinct low/high readings, Composition keyboard movement worked, Session Run/Field Card/shot-detail opened and closed correctly, Field Card background was inert, and no page errors were captured. Plan F standalone additionally passed 10-card, dog/night toggle and visible correction-panel checks at 390×844.
- A later full rerun expanded this to `CURRENT_BROWSER_QA.json`: **234/234 current checks**, including all 36 route states in each master target and all 36 subject/time states across the six standalone pages.
- Restored the missing user-facing download links and rebuilt `downloads/canon6d_photo_planner_assets.zip`; the release verifier now byte-compares its six plan pages, Field Card and canonical data with current sources.

## Optical Decision Lab v2 and outdoor accessibility

- Rebuilt the lab around the physical lens choices in the kit, including focal-dependent maximum apertures for the 35–80 mm zoom. The visualization now updates field of view, frame width, near/far depth-of-field limits, hyperfocal distance, front/behind split, background plane, and an explicitly conceptual thin-lens defocus estimate.
- Added the key pedagogical distinction between changing focal length from the same position and moving the camera to preserve framing: the latter changes perspective. The UI labels calculated geometry separately from the preview and states what it does not simulate.
- `OPTICS_ACCESSIBILITY_QA.json`: **16/16 PASS**. Both release targets exercised every lens and every permitted aperture across three focus distances and three subject-to-background separations (more than 500 combinations per target), all presets, narration, physical aperture floors, sunlight mode, font floor, and runtime errors.
- `VISUAL_RESOURCE_QA.json`: **37/37 PASS**. All 120 dynamic plan-image states decoded in each main target; Field Card and route-page images decoded; local links, fragments, and resources resolved; visible text stayed at or above 11 px; solid-background text met WCAG contrast; meaningful Optical SVG lines met the 3:1 non-text threshold.
- Added an opt-in sunlight mode, system-font stack, stronger borders and focus rings, darker light-background text, corrected dark-footer text, and matching Field Card/standalone-route readability rules. The site remains free of required remote font and icon dependencies.
