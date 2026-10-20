# Requirements Inventory — FocalRuta · Arquitectura en Foco 2026

This is the normalized source of truth reconstructed from the current request, the **23 historical user messages in the uploaded ZIP**, the official competition PDF, the supplied Master82 artifacts, and current `PillB/focalruta` / `PillB/solarize_skill`.

Priority: **MUST** = release blocker or explicit repeated request; **SHOULD** = strong quality requirement; **COULD** = only after all MUST/SHOULD gates are green.

## A. Mission / competitive strategy
- **A01 MUST** — Build one system that teaches architectural photography while helping allocate scarce shooting time toward the strongest single-photo competition submission. **Superseded 2026-10-17 by T01:** the 2026 edition closed and the owner asked for a general, production site.
- **A02 MUST** — Rank **scene hypotheses**, not famous buildings.
- **A03 MUST** — Official decision layer is limited to `creative/aesthetic proposal` and `coherence with theme`; internal scores are never called official. **Superseded 2026-10-17 by T02:** the 2026 edition closed and the owner asked for a general, production site.
- **A04 MUST** — Explicitly fight tourist/default-view bias and visual saturation.
- **A05 MUST** — Preserve the user's anti-postal question: **“What has everybody already photographed here—and what relationship becomes visible only if I change time, camera position, focal length or human presence?”**
- **A06 MUST** — Add a causal architecture question: **“What part of the original design still forces, enables, channels or contradicts what someone is doing here today—and what camera position makes that relationship visible without the caption rescuing the photograph?”**
- **A07 SHOULD** — The photograph should have first-read visual force before title/description adds nuance.

## B. Candidate universe / geography
- **B01 MUST** — Candidate discovery, ranking and routes are geographically limited to **Lima Metropolitana as Provincia de Lima and its 43 districts**. Callao, other Peruvian provinces/cities and foreign locations are out of scope unless the user explicitly changes this boundary.
- **B02 MUST** — Prioritize San Isidro, Miraflores, Centro de Lima/Cercado, San Borja, Barranco, Pueblo Libre, Magdalena del Mar, Surquillo and Lince; expand to other eligible Lima districts only when evidence justifies the travel.
- **B03 MUST** — The historical 40-place list is a floor, not a fixed universe.
- **B04 MUST** — Parque de las Américas is a graph edge for discovery, not an automatic favorite.
- **B05 MUST** — Bonilla W01–W20 are graph edges/frameworks, never a fame/authority bonus.
- **B06 MUST** — Every new candidate gets equal-depth evidence before it can outrank existing candidates.
- **B07 MUST** — Reconcile all historical ranking ledgers found in the root (known ZIP Master68 + current Master82; ingest 83/84/86 etc. if present).
- **B08 MUST** — Semantic deduplication precedes any new “Master N”. Known RED case: `Unidad Vecinal Nº3` vs `Unidad Vecinal N.º 3`.

## C. Ten substantive passes per serious candidate
The repeated “iterate 10 times each” request is implemented as **ten different evidence passes**, not ten rewrites:
1. Source truth: identity, architect/date/typology/location/current status and contradictions.
2. Original spatial contract: intended program/users/spatial devices.
3. Current life: use/users/restoration/closure/current changes.
4. Human verbs or meaningful absence: >=5 real/credible actions when people matter.
5. Architectural causality: threshold/path/stair/void/wall/material/edge/circulation/landscape device that produces behavior.
6. Visual saturation: multiple public reference viewpoints/times/weather; dominant cliché + under-photographed relation.
7. Light/material/geometry: shadow, overcast/garúa, texture, reflection, abstraction, micro/macro.
8. Camera position then optics: >=3 positions; camera height/orientation/distance; choose 35/50/85/zoom after position.
9. Decisive moment + execution: activity window, wait trigger, consent/privacy, safety, access, permission, kill/fallback.
10. One-frame contest test: A/B/C/D/E, first-read strength, official-theme coherence, counterargument, evidence that moves rank.

## D. CONTRACT vs USE field protocol
- **D01 MUST** — Observe 10 minutes unless an irrepeatable event occurs.
- **D02 MUST** — Original purpose in 8 words.
- **D03 MUST** — Record 5 real human verbs.
- **D04 MUST** — Find the verb most confirming/contradicting the design and the architectural device causing it.
- **D05 MUST** — Find 3 camera positions, inspect frame edges, choose position, then focal.
- **D06 MUST** — Make A/B/C/D/E proofs:
  - **A STRUCTURE** — architecture reads without event.
  - **B HABITAR** — human action changes meaning, not merely scale.
  - **C ANTI-POSTAL** — real non-default relationship/viewpoint/light.
  - **D LIGHT/MATERIAL** — architecture reads through reduction/material/shadow.
  - **E ONE-FRAME STORY** — final concept works before caption.
- **D07 MUST** — Every scene specifies position, height, orientation, focal, exposure intent, action, light, edge guards, wait/kill, ethics/access and fallback.
- **D08 MUST** — Log why the best attempt failed and update route/ranking; field state = `STAY | MOVE | RETURN_OTHER_LIGHT`.

## E. Competition rules
- **E01 MUST** — 18+ and resident Chile/Peru/Colombia.
- **E02 MUST** — exactly one submitted photograph.
- **E03 MUST** — submission closes 2026-08-30 23:59 local-country time; queries through 2026-08-29; results 2026-10-22.
- **E04 MUST** — JPG/JPEG **5–25 MB**. Preserve PDF minimum even if upload widget only displays maximum.
- **E05 MUST** — capture year >= 2020.
- **E06 MUST** — filename `nombre-apellido`; required title/place/date/year/brief description + personal fields.
- **E07 MUST** — high-resolution backup; bases suggest 300dpi, 5900×4100, RGB.
- **E08 MUST** — only explicitly allowed basic adjustments are presented as safe.
- **E09 MUST** — no digital retouch modifying fundamental image elements; no AI-generated/intervened/edited photo; no collage/montage altering photographed reality.
- **E10 MUST** — User's organizer clarification allows AI planning; do not spam warnings. Keep one concise firewall. Safest workflow: candidate RAW/JPEG never enters AI critique/scoring/editing; final file preflight is deterministic/local.
- **E11 MUST** — retain PDF/form/public-page source discrepancy instead of silently harmonizing it.

## F. Jury / organizer-history intelligence
- **F01 MUST** — Public-source dossier for Cristián Aninat, Hans Stoll, Camilo Monzón: projects, interviews, exhibitions, awards, judged competitions and public jury language when available.
- **F02 MUST** — no fabricated private psychology or taste; juror fit is low-weight uncertainty.
- **F03 MUST** — research Fundación Actual 2023–2025 official winners/finalists as organizer history, not a formula.
- **F04 SHOULD** — test recurring mechanisms: familiar-place rediscovery, light/shadow, geometry/pattern, decisive human action, old/new or context/action tension.

## G. Video / architectural-photography curriculum
- **G01 MUST** — process all 21 URL occurrences / 20 unique IDs.
- **G02 MUST** — transcript-first: exact title/channel/date; legitimate captions/transcript saved where available; `TRANSCRIPT_UNAVAILABLE` otherwise.
- **G03 MUST** — every video-attributed teaching needs timestamp/transcript evidence or clearly labeled secondary-source status.
- **G04 MUST** — fan-in to one coherent curriculum, not 20 summaries.
- **G05 MUST** — cover exposure/metering, ISO, focus/sharpness, focal/FoV/perspective, DoF, camera position, composition beyond rules, depth layering, directional light, edges/background, scene working, human gesture, decisive moment, rain/garúa, anti-dogma and architecture interiors/exteriors.
- **G06 MUST** — every lesson: `Observe → Try → Diagnose → Break the rule when`.
- **G07 MUST** — cross-check against camera physics/current Canon 6D and competition edit rules.
- **G08 MUST** — transfer cards for Iwan Baan, Fernando Guerra, Ezra Stoller, Hélène Binet, Lucien Hervé, Julius Shulman, Candida Höfer, Bas Princen/Gabriele Basilico lineage, Leonardo Finotti and current award examples.

## H. Gear / optics truth
- **H01 MUST** — current FocalRuta canonical gear unless verified update: EOS 6D Mark I; EF 35 f/2 IS; 50 f/1.8 STM; 85 f/1.8 USM; EF 35–80 f/4–5.6 III.
- **H02 MUST** — reconcile historical “35–85” and 5D Mark II references; never silently invent hardware.
- **H03 MUST** — **camera position/distance controls perspective; focal length controls AoV/framing at fixed position.**
- **H04 MUST** — do not teach “85 compresses” as lens magic; explain changed camera distance.
- **H05 MUST** — 35=context/layers; 50=balanced relation; 85=selective/distant layering; zoom=scouting/focal experiments — starting roles, not rules.
- **H06 MUST** — convergence can be error or expressive choice; in-camera geometry is primary under edit limits.
- **H07 MUST** — sharpness fault tree separates focus, camera shake, subject motion, insufficient DoF, diffraction/optics and atmosphere.
- **H08 MUST** — no magic-ISO dogma.

## I. Public-reference visual forensics
- **I01 MUST** — collect multiple useful public reference images for serious candidates across viewpoint/time/weather where available.
- **I02 MUST** — keep URL/author/publisher/date/rights, viewpoint, light, activity, cliché cluster, edge/background issues and what the image can/cannot prove.
- **I03 MUST** — do not redistribute unlicensed full-resolution copyrighted imagery.
- **I04 MUST** — search frequency is a saturation signal, never a population estimate.
- **I05 MUST** — generated mock images cannot prove a real scene/light/view exists.

## J. Ranking
- **J01 MUST** — official-proxy layer only: `creative_aesthetic_proxy`, `theme_coherence_proxy`. **Superseded 2026-10-17 by T02:** the 2026 edition closed and the owner asked for a general, production site. Model v2.0.0 renames them `visual_potential` and `architecture_in_use` and drops the contest-brief input.
- **J02 MUST** — no invented official weights; no “probability of winning” without calibration.
- **J03 MUST** — version scoring model/evidence and preserve immutable runs.
- **J04 MUST** — full rerank after material candidate/evidence changes.
- **J05 MUST** — >=4 scenarios: balanced/official proxy, anti-postal, inhabitation/story, formal+field. Since model v2.0.0 the first scenario is plain "balanced" (T02).
- **J06 MUST** — bounded deterministic sensitivity perturbation; rank distribution/spread/min/median/max or quantiles + Pareto status.
- **J07 MUST** — field/logistics rank separate from artistic/thematic.
- **J08 MUST** — fame/landmark status never positive feature.
- **J09 MUST** — Top 15 robust scenes + Top 5 field priorities + movers/counterarguments.

## K. Route
- **K01 MUST** — time-window route from scene to scene, not static place list.
- **K02 MUST** — objective uses strategic value + light + human activity + access + visit/wait − travel/uncertainty.
- **K03 MUST** — configurable date/start/end/transport/available hours.
- **K04 MUST** — real routing if available; otherwise clearly labeled conservative/geodesic estimate/manual override; never fake live ETA.
- **K05 MUST** — modes: max upside, high confidence, district sprint, golden/blue, habitar, anti-postal, reshoot-only, deadline.
- **K06 MUST** — every stop: why now, arrival, first viewpoint, A-E prompts, verbs, starting focal, wait limit, kill, nearby backup, online map + offline coordinates.
- **K07 MUST** — `STAY/MOVE/RETURN_OTHER_LIGHT` replans.
- **K08 MUST** — new location must displace a route slot on evidence; do not grow route indefinitely.
- **K09 SHOULD** — garúa/overcast is a creative mode.

## L. Native FocalRuta integration
- **L01 MUST** — architecture becomes native FocalRuta Challenge/subsite/tab; historical 1.4MB HTML is provenance/build reference, not canonical source.
- **L02 MUST** — reuse canonical gear and relevant teaching primitives.
- **L03 MUST** — preserve current 6 plans/120 plan diagrams/current features unless deliberate RED-tested change.
- **L04 MUST** — architecture Field Card + adapted Session Run; no irrelevant dog/pose flow.
- **L05 MUST** — canonical data/generator architecture; generated HTML is output.
- **L06 MUST** — hosted/PWA + standalone/offline core parity.
- **L07 MUST** — challenge discoverable from main FocalRuta UI.
- **L08 MUST** — local field-state save/export/import.
- **L09 MUST** — no-JS critical shortlist/rules fallback.
- **L10 MUST** — progressive disclosure: fast field mode, deep research secondary.
- **L11 MUST** — Tailwind/Motion/XYFlow requested as quality goals; bundle/compile locally or use robust native SVG/HTML if current static architecture would be harmed.
- **L12 MUST** — raw chat/system prompts/private exports are **PRIVATE_LOCAL**, gitignored, never public build/history.

## M. Learn from FocalRuta PR/history
- **M01 MUST** — PR #1 pattern: executable invariants/state families, not happy-path smoke tests.
- **M02 MUST** — PR #2 pattern: live hosted/PWA QA and actual service-worker registration.
- **M03 MUST** — PR #3 pattern: UI hierarchy/responsive polish after correctness.
- **M04 MUST** — extend `scripts/verify_release.py`/release-gate pattern rather than disconnected fake PASS JSON.
- **M05 MUST** — source → generated → hosted/standalone parity.

## N. iPhone / accessibility / runtime
- **N01 MUST** — 320×640 (WCAG 1.4.10 Reflow, added for V18), 390×844, 430×932, 844×390, 932×430, 820×1000, 1440×1100.
- **N02 MUST** — `scrollWidth <= clientWidth`; no console/page errors.
- **N03 MUST** — task-critical buttons/toggles/filters and meaningful permutation classes.
- **N04 MUST** — ~44px touch where practical, visible focus, keyboard, modal focus return, reduced motion, contrast/readability.
- **N05 MUST** — tables/cards intentional on mobile; landscape designed, not accidental.
- **N06 MUST** — offline state clear; core field flow/network loss tested.
- **N07 MUST** — recreate historical iPhone-button failure as RED regression.
- **N08 MUST** — visual snapshot change requires reason/review; never blindly update.

## O. Solarize execution
- **O01 MUST** — current TDD Solarize v2.2: research→plan→RED→GREEN→refactor→validate→memory→report.
- **O02 MUST** — pre-round research + concise pre-mortem.
- **O03 MUST** — RED proves missing/broken behavior for correct reason.
- **O04 MUST** — GREEN minimal; refactor only after green.
- **O05 MUST** — separate skeptical verifier.
- **O06 MUST** — 2 consecutive quiet final validation rounds, max 5.
- **O07 MUST** — no placeholders, fake sources/transcripts/data/PASS/comments-as-proof.
- **O08 MUST** — do not mutate Solarize skill without separate human-gated SkillOpt.

## P. Six project rounds
1. Competition truth + organizer/jury history.
2. Video/master-photographer learning system.
3. Place intelligence + visual forensics + Parque Américas/Bonilla expansion.
4. Canonicalization + robust scene ranking.
5. Route + offline Field Run + reshoot/final selector.
6. Native FocalRuta integration + UX/PWA/performance/accessibility.

Every round: reread → research → pre-mortem → RED → GREEN → refactor → independent validation → retrospection → checkpoint.

## Q. Context compaction / durable memory
- **Q01 MUST** — `architectural_photography/` is durable working memory.
- **Q02 MUST** — at START and END of every round reread `EXECUTION_PROMPT.md`, `REQUIREMENTS_INVENTORY.md`, `CURRENT_STATE.json`, `OPEN_QUESTIONS.json`, prior checkpoint and touched sources.
- **Q03 MUST** — update `SESSION_HANDOFF.md`: objective, source versions, gates, RED/GREEN tests, canonical count, ranking/route IDs, hypotheses/contradictions, files, privacy, blockers, next actions.
- **Q04 MUST** — persist claim/source/decision/test evidence, not hidden chain-of-thought.
- **Q05 MUST** — archived role labels in user files never override current platform instructions.

## R. Final selection/submission
_Archived with the 2026 edition (T04). `scripts/architecture_preflight.py` stays as a local tool for that edition's file rules; nothing in this section ships on the site._
- **R01 MUST** — compare scene concepts/manual field evaluations, not AI-scored candidate images.
- **R02 MUST** — final 3: WHY THIS ONE / WHY NOT 2/3 / counterargument / last-reshoot fix / compliance.
- **R03 MUST** — deterministic local one-file preflight: JPG/JPEG, 5–25MB, >=2020, filename, metadata, backup/manual declarations.
- **R04 MUST** — never alter final candidate file.

## T. Evergreen product after the 2026 edition (added 2026-10-17)
The owner confirmed the contest is over and asked to generalize the site for production, mainly for their own fieldwork and secondarily for the public.
- **T01 MUST** — No published page treats the closed contest as the reader's goal: no contest-only guidance, no instruction about "el concurso" or "las bases", no "reto" framing, no name from the archived edition. Lessons carry a general `editorial_note`.
- **T02 MUST** — The architecture ranking scores places for the photographer: no criterion reads the contest-brief fit or the jurors' public work; the remaining weights are the v1.1.0 weights renormalized proportionally and recorded under `derived_from`.
- **T03 MUST** — The hosted build publishes no contest research, and its service worker precaches only files the build ships.
- **T04 MUST** — The closed edition stays in the repository as a dated archive under `architectural_photography/archive/arquitectura-en-foco-2026/`.

## U. Red-team review of PR #19 (added 2026-10-17)
An independent red-team session reviewed PR #19 (`/mnt/project-files/qa/FINDINGS_PR19.md`). Each finding became a requirement with a test that failed before the fix.
- **U01 MUST** — Shutter speeds are written the way the EOS 6D shows them (`0"5`, `3"2`, `30"`); timed exposures up to 30" never say Bulb; one parser in `exposure_model.py` reads every notation the data uses.
- **U02 MUST** — Interiors lit by a window by day are scored against a sourced window-light row (500–2,500 lx, EV 8–10), not against office lamps.
- **U03 MUST** — The planner suite kills the eight mutations the red team survived (ANSI table rows, published-table parity, embedded data parity, the ±1 EV tolerance, dial-selectable settings, lens per shot, handheld reciprocal rule).
- **U04 MUST** — Every published page passes axe-core (WCAG 2.x A/AA and best practice) in a light phone pass and a dark desktop pass, with animations finished; every page has `lang="es"`, one `main` and one `h1`; the contrast audit checks text on gradients at every colour stop.
- **U05 MUST** — Hosted plan pages carry no inline images (≤ 400 KB each) and point every diagram at a shipped `diagrams-webp/` file; after one online visit the page and all 20 of its diagrams work with the server gone. The repo's `plans/` pages and the download ZIP stay self-contained. `verify_release.py` holds each hosted page byte-identical to its offline copy outside the diagram map and the cache-warming script, and each linked file byte-identical to the image the offline page inlines.
- **U06 MUST** — A plan note names the light its slot is scored against; alternatives in notes ("si no tienes el filtro…") land within a quarter stop of the slot's scene. The Lima sun panel opens on today's date in Lima from any reader time zone.
- **U07 MUST** — Reader-facing plan text is Spanish (no leftover English photo jargon; a space between a number and its unit). The integrated field card's remaining English labels are tracked for the field-first round.
- **U08 MUST** — Evidence and builds are reproducible and honest: QA reports record the commit they audited; only fingerprinted reports sit at the root; CI installs from `requirements-dev.txt`; the service worker precaches every manifest icon; the published source registry carries no contest material.

## V. Field use first, then the public (added 2026-10-17)
Step 3 of the plan the owner approved ("proceed"): field use first (offline, one-handed, a field card fully in Spanish, stronger planning), then public polish (navigation, configurable gear with the Canon 6D kit as default). Static halves in `tests/test_field_card.py`, `tests/test_home_page.py` and `tests/test_gear.py`; browser halves in `scripts/field_card_qa.py` and `scripts/browser_release_qa.py`.
- **V01 MUST** — Every word a reader sees on the field card is Spanish; camera labels stay as the 6D prints them (ONE SHOT, AI SERVO, Tv, Av, MF).
- **V02 MUST** — For every plan, shot and light slot the card shows that slot's lens, aperture, shutter, ISO and ND filter from `data/plans.json`, and marks slots that cannot be shot.
- **V03 MUST** — No card text under 12 px, on the card or in the home page's copy of it.
- **V04 MUST** — A packing list per plan names every lens, ND filter (with its thread) and support the plan's shots need.
- **V05 MUST** — The home page embeds exactly the card `generate_field_card.py` builds, through `regenerate_all.py`, and the integration replaces nothing but the card; every element a shipped page's script looks up by id is on that page. In its dialog the card is drawn as on its own page, element by element (what is drawn, backgrounds, padding, corners, visible borders, and the colour, size, weight, font and leading of its text), by day, in dark mode and with the night screen (X05).
- **V06 MUST** — The light slot follows the clock in Lima from any time zone, and each shot shows the time window its light occurs in on the chosen date.
- **V07 MUST** — After one visit and one tap, the plan pages and every diagram work with the server gone, and the offline pack survives a deploy.
- **V08 MUST** — One-handed use: the section bar stays in the bottom 15 % of a phone screen, a "next pending shot" button jumps to the first unticked shot, and arrow keys move between plans with a visible focus ring.
- **V09 MUST** — The card remembers the plan, light, ticks and night screen across reloads; clearing a list takes a second tap; the night screen is black and red. Whatever its saved state holds (a quote in a stored choice, a string, a list, ticks that are not a list of ticks), the card starts and keeps what it can, and the home page's button opens the card even if the card's script stops (red team, 2026-10-20).
- **V10 MUST** — No text a reader sees on the home page or the plan pages is under 12 px (SVG text measured as drawn), in every state a reader reaches.
- **V11 MUST** — Every control on the home page and the plan pages is at least 44 × 44 px; links inside a sentence are exempt (WCAG 2.5.8).
- **V12 MUST** — The interface of the home page and the plan pages is Spanish; cited English sources keep their published titles. No published page has English prose outside an element marked `lang="en"`, and English titles carry it (WCAG 3.1.2); each scene mechanism of the contest pages has a Spanish name (red team, 2026-10-20).
- **V13 MUST** — `assets/gear.js` adapts each planned setting to the reader's gear with the same framing, the same depth of field in proportion to the subject distance, the same exposure, and the plan's creative variable kept (shutter for motion, depth of field for depth-of-field shots); every limit of the gear (a lens that does not open enough, missing light, no zoom for a zoom burst) is said in the line, and light is said missing only from a third of a stop, the dial's step.
- **V14 MUST** — The Canon 6D kit is the default and changes nothing: no extra line, the same settings.
- **V15 MUST** — The home page offers the gear picker; the home page, the plan pages, the field card and the optics lab carry the same `gear.js` and show the reader's line; gear read back from storage cannot put markup on the page.
- **V16 MUST** — A page is served this build's files or the network's, never another build's copy: the service worker checks the bytes of every copy it keeps against the build (so neither the HTTP cache, which Pages sets to 10 minutes, nor a CDN node that has not caught up can slip an old file in), the home page names its stylesheet and data by revision (so an older worker still in control fetches the new ones), and every file it keeps, the web manifest included, is served offline. Pages and this build's files are revalidated with the server, so the HTTP cache cannot answer a page with the last build's; a page from another build gets the revision it names; a 404 or 5xx never replaces a copy the reader kept. The worker answers `{type:'version'}` on a MessageChannel port with its VERSION, and a rehearsal of a deploy checks the new build only once the active worker names it, after one update, on a server that answers each request from the build it serves at that moment (red team on PR #21, F1). (Red team on PR #20, majors 4 and L1; live check L3; second pass N2, N3; CI run 39089226401.)
- **V17 MUST** — An upgrade from the worker live at 9cd3044, or from any later one, keeps every page and diagram the reader had offline and downloads nothing that did not change; the files kept for the field are brought up to date on install, the field card says when some are from an earlier version or missing, and caches of the other sites on pillb.github.io are never touched. (Red team on PR #20, major 5 and the stale-pack minor.)
- **V18 MUST** — From a 320 px wide screen up (WCAG 1.4.10 Reflow), nothing a reader needs on the home page, the plan pages or the field card is cut off: no text or control runs past the edge of the screen outside a strip that scrolls sideways, no control's label is clipped or runs out of it, and no control sits on top of another, in every state a reader reaches, with the default kit and with a reader's own lenses whose names are as long as real ones (320 and 375 px; second pass N1). The tests read the pages that ship in `dist/`, not only their sources. (Red team on PR #20, majors 6 and 7.)
- **V19 MUST** — The session, field card and shot dialogs, opened from the button a reader presses and closed with Escape, take focus while open and give it back to that button, and leave nothing on the page inert. Each takes focus in the task that opens it, as `showModal()` does. (Red team on PR #20, major 7; CI on 518b9a3.)
- **V20 MUST** — Every number a reader sees, on the home page, the plan pages, the field card, the gear line and the diagrams, uses the point as its decimal mark (es-PE in CLDR, as the RAE's Ortografía of 2010 recommends) and stands one space from its unit symbol ("2.5 m", "0.03 mm", "1/2000 s"); lens names keep the maker's spelling ("EF 35mm f/2", and the kit's 35mm, 50mm, 85mm and 35–80mm, and a number right after a mount code, as in "EF 100mm Macro"), and any other number glued to "mm" is a measurement. A comma after a lone zero ("0,030") is a decimal comma, and a length is read from its own start, whatever element text touches it. Every text in the plans' data is checked too, since it reaches the reader through JavaScript. (Red team on PR #20, follow-up; red team on PR #21, F5.)
- **V21 MUST** — Offline, a page never kept on the device opens the home page under the home page's own address, styled, saying which page it was, with links back to it and to the field card; a forged page name, or one Pages cannot serve (upper case), shows nothing (red team on PR #21, F6). Offline checks cut the network by stopping the server, never with the browser's offline switch, which leaves the service worker's own requests on the network. (Live check of 56a6e97, M7 and T1.)

## X. Production hardening (added 2026-10-17)
Step 4 of the plan the owner approved ("proceed"): a release gate on every pull request, speed budgets including the plan pages, checks of the live site, and error monitoring that respects privacy. Static halves in `tests/test_ci_contract.py`, `tests/test_perf_budget.py`, `tests/test_diagnostics.py` and `tests/test_css_audit.py`; browser halves in `scripts/perf_budget_qa.py`, `scripts/live_pages_qa.py` and `scripts/browser_release_qa.py`.
- **X01 MUST** — Every browser suite (`regenerate_all.BROWSER_QA` and each `tests/architecture/browser_*.py`) runs in CI on every pull request, on Linux, with pinned tools (Playwright and its Chromium, axe-core and Lighthouse from `package-lock.json`); no suite assumes the owner's Mac, and a missing browser or axe-core stops the run with the reason. A failing suite does not keep the next one from running, every suite's report is kept as a CI artefact, and the suites pass with the fonts Linux Chromium falls back to (DejaVu Sans for `system-ui`), not only with those of the machine that ran them before. A failing suite names what failed, console errors and files that failed to load included. (First CI run of PR #21, run 39089226401; CI on 518b9a3.)
- **X02 MUST** — Every page type the site ships (home, field card, each plan page, the challenge and its guides, a route map, the not-found page) meets Lighthouse's "good" mark for mobile on first paint, largest paint, blocking time, layout shift and speed index, scores at least 90, stays within a byte budget for its type, and asks no other origin for anything; measured served as GitHub Pages serves it, median of three runs.
- **X03 MUST** — After every Pages deploy and every day, CI waits until the live site serves that commit's build, then checks it end to end (every page, plan state, image, dialog, the service worker, every same-origin resource, no request to another origin) and against the speed budgets; a failure fails the run. Only the job that deploys can write to Pages (red team on PR #21, F4).
- **X04 MUST** — Runtime errors, rejected promises, resources that fail to load and a service worker that fails to register are kept on the reader's device only, without query strings, fragments, the folders of a page opened from a file, quoted text (which can be what the reader typed; an apostrophe, as in "can't", opens no quote), the browser's identity or the reader's data, capped and de-duplicated; the home page shows the log in Spanish with copy, a prefilled GitHub report the reader sends, and clear; without a clipboard, copy says so and selects the log; the code has no way to send anything. (Red team on PR #21, F2 and F7.)
- **X05 MUST** — The browser keeps every declaration and selector in the CSS the site ships, read from the source text (the CSSOM has already thrown away what it could not parse): no HTML comment inside a stylesheet, whose words become the next rule's selector, and no shorthand a browser cannot parse. Only CSS written for another engine (`-moz-`, `-ms-`, `-webkit-overflow-scrolling`), a standard property beside its `-webkit-` twin, and descriptor blocks (`@font-face`, `@page`, `@property`) are exempt. (Found while following up the red team's page-size note on PR #21: the home page's card had lost its base rule since step 3, dark text on dark in dark mode, and the hosted home its `:root` colours.)
- **X06 MUST** — The taps a reader makes most (opening the field card and a shot's detail on the home page; picking a plan, picking a light and ticking a shot on the field card) answer with a paint within 200 ms on a mid-tier phone and never take more than 500 ms on a low-tier one (INP's "good" and "poor" marks), median of five fresh visits, measured from the Event Timing entries INP is built on with the CPU slowed until Lighthouse's BenchmarkIndex scores as Chrome DevTools' calibrated mid-tier (1000) and low-tier (264) phones do; a tap with nothing to tap fails by name. It runs with the speed budgets, in CI and on the live site.
