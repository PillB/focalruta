# Session handoff

- Expansions after PR #24, 2026-10-27 (W01–W08, `/mnt/project-files/qa/pr24/evidence/`). W01–W04: the home page's sun panel now has an hour slider that prints where the sun is (bearing and apparent height, within 0.3° of NREL's SPA via pvlib 0.16.1; astral 3.2 agrees within 0.02°) and a 1.70 m person's shadow, draws the day's path on a sky map seen from above, and, for a wall facing any of 16 compass points, lists the minutes of direct, raking (≤20° to the surface; 5–20° in MNAC's glossary, 5–15° in conservation imaging) and head-on (≥60°) sun. Refraction is Saemundsson's (Meeus 16.4), as in SPA; NOAA's spreadsheet formula gave 0.40° at sunrise instead of the 0.57° the −0.833° convention implies, so it was not used. W05–W07: the session dialog reviews each shot with three checks (sharpness for its technique, exposure, the plan's criterion), gives the field card's own fix for a failed check, keeps the review on the device under the existing key (old ticks count as passed), and has a summary. W08: plan counts in the copy come from the data (`plan_counts.py`) and every check walks `qa_matrix.PLAN_LETTERS`; `tests/test_plan_counts.py` builds the site with a seventh plan. RED: 18 planner tests failed before `sun_position`; the W04 checks fail on main (no `#sun-time`) and on 4 of 4 arithmetic mutants; 19 review tests failed without `assets/shot_review.js` and 2 mutants were caught; the W05–W07 browser checks fail on main and on 5 of 5 mutants; the seventh-plan build fails with `plan_counts.py` left out of `regenerate_all.py`. Trade-offs: the sun is computed for San Isidro, and every plan is within about 8 km, which moves the times by well under a minute; a wall's facing is chosen from 16 points, not typed in degrees; the raking and head-on bounds are conventions from conservation imaging, not a measurement of texture; the review records what the reader judges on the camera's screen, it does not read the photo; the English version waits on Pablo's choice.
- PR A after PR #23, 2026-10-27: the last two open notes from the PR #21 sign-off. X09: every outside action in the three workflows is pinned to a full commit SHA with its release in a comment (checkout v5.1.0, setup-python v6.3.0, setup-node v5.0.0, upload-artifact v6.0.0, configure-pages v6.0.0, upload-pages-artifact v5.0.0, deploy-pages v5.0.1), SHAs read with `git ls-remote` on 2026-10-27; the tags are lightweight, so the SHA is the commit. V20: a maker's name before a glued "mm" ("Sigma 105mm") names a lens, as a mount code does. RED: both new X09 tests and the V20 maker test failed on 128dc4a; GREEN: 928 passed, 1 skipped; verify_release and verify_architecture pass; C901 ≤ 10 passes; regenerate_all leaves the tree clean. Trade-off: SHAs do not follow new patch releases on their own, so a pin moves only when someone updates it; no Dependabot config is added here. The three items the sign-off listed as open and PR #22 closed (field card INP, leftover English, a stored value with `"`) were rechecked in FINDINGS_PR22 V09/V12 and X06, and are not reworked.
- Whole-site integration gate, 2026-08-31: the FocalRuta homepage now contains a descriptive `Arquitectura en Foco 2026` Challenge landmark in addition to the compact nav shortcut. It explains the 87-scene, learning, ranking, district-route, offline-field and preflight scope; the Challenge retains a keyboard-operable return link to FocalRuta. Hosted and standalone artifacts were rebuilt.
- Module inventory: `architectural_photography/ARCHITECTURE_MODULE_INVENTORY.json` maps 12 public modules to their verification surfaces: command/today, ranking, field priorities, routes, style radar, all scenes, learning, field run, AI firewall, preflight, iPhone maps and offline shell.
- Mobile defect found and fixed: at 390×844 and 430×932 the fixed bottom navigation covered the homepage Challenge CTA after scroll. A behavioral occlusion test failed first, then mobile safe clearance was added. Six required viewports now complete homepage→Challenge→homepage navigation with zero overflow, page errors or CTA occlusion; screenshots and report are under `qa/final/whole_site_integration/`.
- Current GREEN: 119 architecture/contract tests; architecture verifier; release verifier; visual/resource audit 37/37; Optical Decision Lab science/accessibility audit 22/22; route QA 6/6 viewports and 26 cards; whole-site integration 6/6 viewports; `git diff --check`.
- Current blockers/trade-offs: the standalone Ruff executable was absent, but a single expert-documented `uvx ruff==0.12.11` run used the exact CI pin and passed C901≤10 in both quiet rounds. The legacy `browser_release_qa.py` still hangs during macOS Chrome teardown and produced no fresh report; equivalent current checks pass in the visual/resource and explicit-context browser suites. The external OSM router remains fail-fast blocked, so the repaired four-stop Miraflores subpath is disclosed as pending a fresh optimum calculation.
- Two consecutive quiet validation rounds: each passed 119 tests, architecture verifier, existing release verifier, Ruff 0.12.11 C901≤10, staged diff hygiene and staged/public-build private-path scans with no implementation change between rounds.
- PR #8 first CI run failed only because a new CLAUDE contract test compared the runner's dynamic absolute checkout path against the user's requested local absolute path. GitHub's workspace-path guidance supported the correction: CLAUDE now records both portable `AGENTS.md` and the local absolute path; the test asserts those stable contracts. Post-fix full local collection passed 127 tests (including unrelated untracked camera tests), both verifiers and Ruff; only the three contract/ledger files are included in the follow-up commit.
- Privacy: browser QA served only `dist/canon6d_sota_hosted`; serving the repository root was rejected. Raw private inputs and unrelated `camera_purchase/`, `scripts/build_camera_value.py`, and `tests/camera_value/` must remain unstaged. Exact staged/build marker scans remain mandatory before commit.
- Exact next actions: stage only architecture/integration artifacts, run the staged privacy scan, inspect the staged diff, commit, push and open a PR. Require the pinned Ruff CI gate and all repository checks before merge; verify Pages after deployment before claiming the new version live.

- Route geometry expert audit, 2026-08-31: downloadable KML/GeoJSON previously contained stop pins only. It now contains the captured OSM road `LineString` for every leg, and every multi-stop card renders an accessible numbered geometry preview. Google My Maps officially supports imported places and lines; the direct Google walking link remains the iPhone-first flow.
- District-purity correction: an external OSM polygon audit checked every route vertex, not only stops. Twenty-four of 25 original layers were fully contained; Miraflores tour 2 had five outside vertices on the 836.2 m Parque Tradiciones→Casa Raúl Porras edge. That edge is removed. Parque Tradiciones is now a standalone verified pin; the remaining four stops form a 521.2 m contained subpath.
- Scientific limitation: the OSM routed-foot service stalled during the fresh rebuild and was stopped after the first confirmed availability failure. The four-stop subpath preserves the contained portion of the earlier exact five-stop solution but is explicitly not presented as a newly calculated optimum. `snapshot_repair.status` remains `BOUNDARY_EXIT_REMOVED_ROUTER_REBUILD_PENDING` until a fresh four-stop matrix succeeds.
- Screenshot evidence: six responsive route-section captures and 26 individual layer screenshots pass. Every layer has a forensic description with ordered stops, road distance, vertex/bounds evidence, maximum road/straight ratio and assessment. Eight layers remain flagged for a 0.84–0.99 km transfer or a barrier-driven detour ratio; these are disclosed rather than silently split.
- UX forensic samples: the repaired Miraflores four-stop card is readable at 390 px, its four labels remain inside the preview, the limitation copy is visible before the route action and KML/GeoJSON links remain touchable. Miraflores tour 1 visibly exposes its 0.9 km transfer and two mobile stages. The full 390 px route-section capture has no clipping or overflow, but is intentionally supplemented by card-level captures because a full 26-card screenshot is too vertically compressed for path judgment.
- Current GREEN: 124/124 repository tests; architecture verifier PASS; release verifier PASS; repository-wide Ruff C901 ≤10 PASS; six viewports PASS; 26/26 layer captures written. Agent/Claude contracts now require expert rejection, methodological correctness, non-tautological tests, explicit trade-offs, first-failure research, API fail-fast behavior and the macOS `⌘⌥Q` close-program warning.

- Final deployed gate, 2026-08-31: PRs #4, #5 and #6 are merged; `main` is `194b72f6e25c70e056dc75f016e3b899a34111ca`. Quality run `33408313177` and Pages run `33408313045` succeeded. The Pages workflow now uses the official Node 24 action generations: checkout v5, configure-pages v6, upload-pages-artifact v5 and deploy-pages v5.
- Live challenge: `https://pillb.github.io/focalruta/challenges/arquitectura-en-foco/` returned HTTP 200 at 390×844 with 87 scene cards, 25 route layers, 66 route stops and all six style-scene additions. `iphone-maps.html` returned 200; anchor clearance is +7.515625 CSS px; overflow, page errors, console errors and failed resources are zero.
- Live PWA evidence: FocalRuta's canonical root shell registers `sw.js` at project scope. Entering through the shell, awaiting readiness, opening the architecture challenge and reloading leaves the challenge controlled by the worker. Trade-off: a first-ever direct deep link does not itself register the worker; offline control starts after the user has loaded the main FocalRuta shell once. The challenge and its core data/help are precached.
- Final local evidence: 118/118 tests passed; `scripts/verify_architecture.py` and `scripts/verify_release.py` passed; repository-wide Ruff C901 passed at maximum complexity 10; `git diff --check` passed. The PR #6 clean-checkout gate passed independently.
- Release status language: deployed and live-gated, but not “perfect.” Desk research, ranking and routing are operational; scene access, light, activity and photographic causality remain field hypotheses until on-site verification. Seven disclosed 0.84–0.99 km route transfers remain the accepted usability trade-off instead of fragmenting every route into singleton pins.

- Live Pages post-merge audit on 2026-08-31 found one accessibility defect after otherwise green deployment: sticky task navigation obscured hash-target headings by 62.5 CSS px on a 390×844 viewport. Follow-up branch `fix-architecture-sticky-nav` adds 70 px `scroll-margin-top`; the browser regression now measures nonnegative clearance at all six viewports (7.5–8.5 px observed).

- 2026-08-31 style-scene admission: six completed dossiers (UTEC, Torre Interbank, Casa Fernandini, Estación Desamparados, Edificio Petroperú and Torre Begonias) entered the current 87-scene universe. The immutable historical reconciliation remains 81 identities (Master68 + Master82 with UV3 merged). New scenes use `2026_STYLE_DOSSIER_EXPLICIT_EVIDENCE_ASSESSMENT`; no Master82 score or historical rank is inherited.
- Ranking run `2026-08-31-r4-v7`: 87 scenes, four scenarios, fixed-seed sensitivity and nine Pareto-front scenes. Route eligibility now derives from published route stop IDs instead of a hard-coded false value.
- OSM refresh and route rebuild: all six new scenes resolved to their stated district; UTEC and Petroperú use official-address query anchors after generic-name queries returned no result. Exact pedestrian-road permutation and administrative polygon containment produced 66 stops in 25 district-pure layers. The hard maximum photography-stop leg was tightened from 1.5 km to 1.0 km; observed maximum is 994.6 m. Seven 0.84–0.99 km transfers remain explicitly warned rather than splitting every layer into singleton pins.
- Runtime QA: `browser_round5_route_qa.py` passed 6/6 viewports with 25 cards, HTTP 200, no overflow, no page/console/resource errors, and iPhone-help HTTP 200. Screenshots and forensic descriptions are in `qa/rounds/round5/`.
- GREEN commands: `python3 -B -m pytest tests/architecture -q --tb=short -p no:cacheprovider` → 107 passed; `python3 -B scripts/verify_architecture.py` → PASS; `python3 -B scripts/verify_release.py` → PASS; pinned offline Ruff C901 max 10 → PASS.
- Privacy: browser server remained limited to `dist/canon6d_sota_hosted`; raw private workbench inputs were not served. Before commit, run staged/build marker scans and exclude unrelated untracked `camera_purchase/`, `scripts/build_camera_value.py`, and `tests/camera_value/`.
- Exact next actions: complete two quiet validation rounds, run staged privacy scan, checkpoint the architecture-only diff, then inspect PR/deployment availability and verify live Pages before any production-ready claim.

- Round 5 route foundation 2026-08-30: 81 geocoder queries were captured as review-only evidence; 56 returned no result and one false PREVI match was rejected. Administrative-boundary selection plus point-in-polygon containment and pedestrian-road routing admitted 21 stops into seven tours across Barranco, Lima, Miraflores, Pueblo Libre, San Borja and San Isidro. The remaining 60 scenes stay visible but unrouted.
- Route optimization: each admitted cluster uses a pedestrian road-distance matrix and exact open-path permutation search. Six immutable iterations record quarantine, district filtering, polygon containment, pedestrian matrix, exact permutation and iPhone staging. Screenshot forensics rejected 5.4 km, 2.9 km and 2.6 km legs; network-connected clustering reduced the published maximum leg to 2270.6 m and split San Borja into two tours.
- Native route UI: seven district-pure cards, direct universal Google walking links, mobile-safe stages of at most five stops, KML and GeoJSON downloads, and an ELI5 iPhone 13 Pro guide. The PWA v3 shell precaches the route UI, iPhone guide and route data; Google recalculates the current walking path when a link opens.
- Round 5 GREEN: `python3 -B -m pytest tests/architecture -q --tb=short -p no:cacheprovider` passed 94/94; `python3 -B scripts/verify_architecture.py` and `python3 -B scripts/verify_release.py` passed; pinned offline Ruff C901 max 10 passed. `browser_round5_route_qa.py` passed all six required viewports and stored screenshots plus forensic leg analysis in `qa/rounds/round5/`.
- Route trade-off/blocker: only 21/81 stops are admitted. Bulk fuzzy geocoding was not silently trusted, isolated points are not called tours, and no live ETA is claimed. The next route-data action is manual/current identity and coordinate verification for the 60 withheld scenes, followed by access/activity/light windows and field-driven replanning.

- Current objective: execute Round 3 place intelligence inside the 43-district Lima Metropolitana boundary, beginning with historical-run canonicalization and source reconciliation.
- FocalRuta baseline: `9a415311f8d34772a6391193434bbf22c7b9af5b`; active branch `agent/arquitectura-en-foco-2026`.
- Solarize: v2.2 requested; skill/repository unavailable in the current session catalog. Its stated lifecycle is being applied directly; Solarize was not modified.
- Competition last verified: 2026-08-27 from official PDF, official article, and live official form.
- Gates complete: source inventory; 36-member ZIP count; 23 historical-user-message ledger count; private-path `.gitignore`; staged/build/bundle marker scan; existing static release gate; required six-viewport local hosted/PWA capture.
- RED/GREEN evidence: `python3 scripts/verify_release.py` exited 0 with `passed: true`; `python3 architectural_photography/qa/baseline/capture_baseline.py` exited 0 with six viewports green, no overflow/errors/failed resources, keyboard focus reached, and registered/controlling service worker. Existing browser and optics suites completed assertions but hung during Chrome teardown, so they are not counted as fresh machine-readable passes. `scripts/visual_resource_audit.py` exposed a pre-existing 1.05:1 inactive-toggle contrast failure.
- Round 1 RED: `pytest tests/architecture/test_competition_rules.py` produced 5 expected missing-data failures.
- Round 1 GREEN: `pytest tests/architecture/test_competition_rules.py tests/architecture/test_round1_research.py` passed 7/7; existing release gate remained green.
- Canonical candidate count: 81 from the sanitized Master68/Master82 union. Master68 contributes 68 identities, all retained in Master82; Master82 adds 13 identities; its UV3 semantic duplicate reduces 82 rows to 81 identities. All remain `HISTORICAL_ONLY` and not ranking-eligible pending current verification.
- Ranking model/run: none current.
- Route run: none current.
- Active hypotheses: historical Master82 and Bonilla conclusions remain historical until source verification and reranking.
- Contradictions: Master82 UV3 duplicate is resolved through aliases `uv3` + `uv3-bonilla`; historical W03 labeling still differs between supplied inventories and must be reconciled.
- Privacy: Round 0 pass; private inputs ignored, manifest generated, public build/download scan found no private markers. Re-run before every commit/build/release.
- Production files changed: none. Repository instruction/privacy files and workbench scaffolding only.
- Round 1 UI/preflight GREEN: 13 unit/data/page tests pass; `scripts/verify_architecture.py` passes; new architecture code passes Ruff C901 at max complexity 10; independent browser QA passes all six required viewports after a RED missing-favicon run.
- Round 1 commit: `83b5117 feat: establish arquitectura challenge round one`.
- Round 2 video evidence: all 21 URL occurrences/20 unique IDs have exact YouTube titles, channels, publication timestamps, and saved timestamped caption tracks. Primary yt-dlp extraction failed consistently; official oEmbed/watch-page fallback verified metadata. A collector regression that attempted to downgrade cached transcripts was fixed so captured evidence is immutable.
- Round 2 RED/GREEN: curriculum tests produced three intended missing-file failures; transfer-card/UI tests then produced three intended failures. After implementation, 8/8 Round 2 learning checks and 21/21 architecture checks pass. The curriculum has 17 lessons; ten source-registered photographer transfer cards cover six seeing modes and explicit Latin American practice.
- Round 2 generated UI: the challenge now renders the six modes, position-before-focal drill, and ten transfer cards as visible content. `scripts/verify_architecture.py`, `scripts/verify_release.py`, focused C901 lint, and six-viewports browser QA pass.
- Diagram complexity GREEN: refactored the three inherited violations (25, 14, 21) into bounded render helpers. Repository-wide Ruff C901 passes at max 10 without exemptions. A new PR/main quality workflow pins Ruff 0.12.11 and runs the ceiling, full tests, architecture verifier and release verifier.
- Diagram regression: regenerated 120 plan and 8 composition diagrams; PNG metadata bytes changed, but decoded RGBA pixels and dimensions matched Git for all 128 affected files. Metadata-only rewrites were restored rather than committed.
- Transcript semantic audit: manually reviewed all 12 curriculum timestamp windows against saved caption tracks. Two `Fh6PIafC8wU` citations pointed to unrelated passages and were corrected to 324.9s (outer-edge distractions) and 1963.1s (anticipation/readiness for the moment).
- Current validation: 22/22 tests pass; repository-wide C901 passes; `verify_architecture.py` and `verify_release.py` pass; diff check passes.
- User geographic boundary: Lima Metropolitana is defined fail-closed as the 43 districts of Provincia de Lima. Priority field districts are Lima/Cercado, San Isidro, Miraflores, San Borja, Barranco, Pueblo Libre, Magdalena del Mar, Surquillo and Lince. Callao, other Peruvian provinces and foreign locations are quarantined; international examples are pedagogy only.
- Round 3 geography RED/GREEN: missing-policy collection failure became 3/3 passes. Official INEI/PCM sources establish the 43-district boundary. Historical neighborhood/cross-district aliases are explicit for Barrios Altos, Centro Histórico, Miraflores–Barranco and Lima media.
- Round 3 canonicalization RED/GREEN: missing-engine collection failure and a later 0/4 alias failure were resolved without widening geography. Master82 reconciles 82→81 through the explicit Unidad Vecinal 3 merge; historical IDs survive, inherited rank/score fields are absent, and all records remain historical-only/non-rankable.
- Bonilla W01–W20: 20 immutable snapshots generated. Direct source accessibility is separated from evidentiary role and candidate eligibility; no Bonilla source promotes a candidate, creates a ranking run or invents a Top 5. W01 Callao content is excluded from candidate seeding. Cantagallo is correctly retained as geographically inside Rímac/Lima but quarantined behind the explicit collaboration/consent ethics gate. W18 preserves the prior-condition field test.
- Bonilla claim graph: the 20 snapshots now resolve to 20 typed public source records and 20 unique framework claims in the global graph. Every claim explicitly forbids score/promotion and requires a current place/access source before route use.
- User discovery intake 2026-08-27-A: Parque de las Américas and Antigua Taberna Queirolo merge with existing canonical identities; Santo Domingo and Nuestra Señora de la Soledad are new discovery edges; “Huaca de Breña” remains identity-unresolved between Mateo Salado (Lima boundary with Breña/Pueblo Libre) and Huaca Independencia (Breña). All five remain non-rankable and non-routable.
- Verification cohort `VERIFY-2026-08-27-A`: six unordered research-queue identities—Ccori Wasi, Parque 3 de Octubre, Parque de las Américas, Antigua Taberna Queirolo, LUM and Puente de la Paz. Admission requires resolved canonical identity, eligible Lima geography, current primary source, non-closed access and a unique scene mechanism. Historical rank/score fields are ignored and stripped. A seventh distinct eligible mechanism fails closed until an explicit displacement decision is recorded.
- Production-facing dossier contract: `data/architecture/scene_dossier_schema.json` requires all ten evidence passes, exactly five A/B/C/D/E proofs, source/current-access fields, counterargument, kill condition and rank-moving evidence. Dossiers remain explicitly non-rankable/non-routable at this schema stage; later promotion requires a separate reviewed transition rather than editing these constants silently.
- Current validation after cohort source registration: 54/54 architecture tests pass; all nine current primary URLs for the six-candidate verification cohort resolve exactly once in the production source registry. Pinned Ruff 0.12.11 C901 max 10 passes via cached `uvx --offline`; architecture verifier, release verifier and diff check pass.
- User scope correction: legal and photography-permission research is omitted. Retain only practical open/closed state, schedule and essential contact checks. No legal permission ledger or legal-warning UI is part of the product.
- Native integration slice: the FocalRuta home navigation now discovers Arquitectura en Foco; the generated Challenge uses task navigation (`Hoy`, `Escenas`, `Aprender`, `Campo`, `Reglas`), labels the six candidates as an unordered verification queue, exposes the master-photographer prompts, provides local autosave plus JSON export/import and `STAY/MOVE/RETURN_OTHER_LIGHT`, and retains no-JS rules/protocol fallback. The dual-release build copies the Challenge and public architecture data into hosted output and PWA v2 precaches the core page/rules/learning data.
- Integration RED/GREEN: 5/6 native-integration assertions failed for missing discovery/navigation/state/fallback/build behavior, then 6/6 passed. Full regression initially exposed three removed semantic contracts (`ai-firewall`, `architecture-preflight`, `Seis modos de ver`); W3C page-structure guidance supported restoring stable descriptive regions/headings. Full architecture suite now passes 60/60; architecture/release verifiers and C901 max 10 pass.
- Browser integration: first Chromium launch failed inside the managed sandbox (`SIGABRT`, `kill EPERM`); escalation allowed launch. Second attempt correctly exposed the absent loopback server (`ERR_CONNECTION_REFUSED`); after starting the documented local prerequisite, `browser_round1_qa.py` passed all six required viewports and refreshed six screenshots.
- Explicit integration trade-offs: dependency-free HTML/CSS/JS is retained instead of React/Motion/XYFlow because the current static generator, standalone and offline architecture would otherwise take an unvalidated dependency migration. The first screen reports the 81-place universe and verification completeness, never a “Top 3,” because no valid ranking run exists. State remains local/exportable without a backend. The offline shell precaches only the field core rather than deep research archives.
- Equal-depth scope correction: the six-source cohort is only a verification pilot, not the product universe. The Challenge now exposes all 81 reconciled canonical identities and lets the user show 10, 25, 40 or all; the preference persists locally. Six are labeled “verification started” and 75 “equal depth pending.” No file order is called a Top N. A generated public `data/architecture/candidates.json` contains the 81 sanitized, non-rankable identities; production no longer reads the workbench directly at runtime.
- Blockers: current Solarize source remains unavailable locally/session-wide; existing legacy QA scripts hang during Chrome teardown in this managed runner. Neither blocks the tested Round 2 data/UI slice.
- Next actions: execute equal-depth source, image-reference, composition-question, ten-pass and A-B-C-D-E dossiers across the complete serious universe, using the six started records only as a pilot template. Resolve the “Huaca de Breña” identity and register Santo Domingo/La Soledad without privileging them. Only after equal-depth validation: build four-scenario robust ranking, then time-window routes and final selector. Live deployment remains prohibited until those gates and two quiet validation rounds pass.
- Production assessment: explicitly **not production-ready**. `PREPRODUCTION_AUDIT.md` records expert-rejection arguments and evidence benchmarks for rules, geography, candidates, ranking, routing, learning, UI, accessibility, PWA, privacy, performance, testing and deployment. No readiness claim is permitted while applicable rejections remain open.
- Equal-depth verification gate 2026-08-28: generated one identical fail-closed record for all 81 canonical identities. Every record requires ten passes, five A–E proofs, visual-reference families and composition questions; historical detail cannot set completion/rank/route eligibility. Current count is 25 `IN_PROGRESS`, 56 `NOT_STARTED`, 0 complete and 0 rankable/routable.
- Place source batch `PLACE-SOURCE-TRUTH-2026-08-28-A`: registered source-linked partial evidence for records 1–11 excluding unresolved UV3, plus Matute, Lima Centro de Convenciones, Quinta Leuro, Barranco funicular, Reducto 2, Barranco library, Cruz del Viajero, LUM, Queirolo and Parque Tradiciones. Missing current operational evidence remains explicit; no full dossier was promoted.
- The same source-truth batch now also covers BNP San Borja, Mirador Catalina Recavarren, Parque Municipal de Barranco, MAC Lima and Puente Villena/Bajada Balta from current operator or municipal sources. This raises source-linked records to 25 without changing completion eligibility.
- Verification tests: `python3 -m pytest tests/architecture -q` passed 65/65; `python3 scripts/verify_architecture.py` and `python3 scripts/verify_release.py` passed. Direct `python3 -m ruff` failed because Ruff is not installed in the system interpreter. After consulting official Ruff/uv documentation, the pinned runner was redirected to writable `UV_CACHE_DIR`, `UV_TOOL_DIR` and `UV_TOOL_BIN_DIR`; `uvx --from ruff==0.12.11 ... C901` then passed. The first download required approved network access; subsequent `--offline` execution passed.
- Equal-depth source review completion 2026-08-28: all 81 canonical identities now have an explicit source-review state across immutable batches A/B/C. States remain granular (`VERIFIED`, `CORROBORATED`, `PARTIAL`, `STALE`, `UNRESOLVED`); unresolved candidate-specific evidence is recorded for Pentagonito, Parque de la Felicidad, Huaca San Borja, the compact-city transect and other weak records rather than promoted. Casa Hacienda Orbea is currently marked closed, Quinta Heeren is under restoration without proven public access, and Cantagallo remains collaboration/consent gated. No candidate is rankable or routable.
- Historical-depth audit: Master82 contains 14 substantive canonical strategy rows and 67 empty historical shells after reconciliation. The ledger preserves this provenance explicitly and does not reconstruct missing answers. All 81 nevertheless receive the same ten-pass schema, three composition questions and five A–E historical hypothesis slots; these remain `HISTORICAL_ONLY`/`HYPOTHESIS`, never current proof.
- Verification GREEN after all-81 source review: `python3 -m pytest tests/architecture -q` passed 67/67; `python3 scripts/verify_architecture.py` and `python3 scripts/verify_release.py` passed; pinned offline Ruff C901 max 10 passed. Source-reference resolution and exactly-all-81 update coverage are executable invariants.
- Debugging escalation evidence: three failed data-shape assumptions triggered authoritative research before the next fix. Python mapping/truth-value documentation and JSON Schema cardinality guidance led to explicit fallbacks and empty-shell labeling; pytest data-driven guidance removed an undocumented hard-coded split. Research, environmental comparison and falsifiable predictions are recorded in `state/graph_memory/rejected_edits.jsonl`.
- Active verification blocker: desk source review now covers all 81, but equal-depth verification is not complete. All 81 still need candidate-specific public visual-reference families and current source-backed answers for the ten substantive passes; the 67 historical empty shells require the largest research effort. A–E records are design hypotheses, not field evidence. Ranking and routing remain prohibited.
- Historical visual intake 2026-08-28: a strict non-executing parser recovered 35 mapped image leads from historical `deep40Data`/`storyData` arrays and left 11 unmatched or out-of-scope. All recovered leads are explicitly ineligible as current evidence; proxy URLs and unresolved rights/provenance cannot promote a candidate.
- Current visual-forensics coverage: 10/81 candidates have 28 candidate-specific LINK_ONLY reference records across batches 01–02. The covered records are Parque 3 de Octubre, Torres de Limatambo, Residencial San Felipe, PREVI, Museo de la Electricidad/tranvía, Parque de las Américas, Huaca Santa Cruz, Conjunto Habitacional Palomino, Quinta de los Libertadores and Plaza a la Bandera. Huaca Santa Cruz has only two page-level official families and Parque 3 de Octubre only one current reference, so even covered candidates remain partial. The remaining 71 have no current candidate-specific visual-family batch yet.
- Visual-forensics trade-off: authoritative galleries whose extraction layer did not expose stable image asset URLs are stored as page locators, never as redistributed images or individual-image proof. This preserves auditability but weakens viewpoint-level conclusions until a browser/network or direct-source path yields stable assets.
- Latest verification: `python3 -m pytest tests/architecture -q --tb=short -p no:cacheprovider` passed 71/71; `python3 scripts/verify_architecture.py` and `python3 scripts/verify_release.py` passed; pinned offline Ruff 0.12.11 C901 max 10 passed; `git diff --check` passed. Equal-depth completion remains 0/81 and ranking/routing remain prohibited.
- Visual-forensics batch 03: UV3, Unidad Vecinal Matute, Lima Centro de Convenciones and Casa Museo Julia Codesido add 11 LINK_ONLY records, bringing coverage to 14/81 candidates and 39 references. UV3's supported mechanism is planned collective space transformed through resident appropriation; Matute's is the shift between city-scale, neighborhood-scale and sports-core space; LCC's is monumental civic void against ordinary neighboring/event life. Codesido remains page/video-locator evidence pending stable image assets and a timestamped walkthrough audit.
- Native progress integration: the generated Challenge and public `data/architecture/candidates.json` now derive visual-reference counts from the 81-record verification ledger. The stale hard-coded six-candidate pilot label was removed. The UI reports 14 candidates with visual forensics started, individual reference counts, and still forces `verification_complete=false` and `ranking_eligible=false` for every record.
- Integration trade-off: only sanitized progress counts enter the public build; deep research records, image URLs and historical artifacts remain in the workbench. This keeps the field shell small and private-safe but means detailed visual forensics are not yet browsable in production.
- Browser integration 2026-08-28: after the managed sandbox denied loopback binding with `PermissionError: [Errno 1]`, Python documentation and the matching Codex sandbox issue confirmed a policy denial rather than a port conflict. A loopback-only escalated server at `127.0.0.1:8765` enabled the existing six-viewport Chrome QA. All six returned 200 with no overflow, page errors, console errors or failed resources, and keyboard focus reached.
- Latest gates after batch 03/integration: 72/72 architecture tests pass; architecture and release verifiers pass; Ruff C901 max 10 passes; hosted/standalone build completes; six-viewport browser QA passes. Equal-depth completion remains 0/81; 67 candidates still lack current visual-reference families, so ranking, routing and production-ready claims remain prohibited.
- Visual-forensics batch 04: Parque Virginia Candamo, Huaca San Borja, Quinta Leuro and the Barranco funicular add 10 LINK_ONLY records. Coverage is now 18/81 candidates and 49 references; 63 candidates still lack current visual families. Candamo's supported distinction is its Chinese-Peruvian commemorative redesign and ordinary park system; Huaca San Borja remains strongest as an archaeological/urban-edge relationship; Quinta Leuro requires the collective court/path system rather than a single picturesque façade; the funicular must connect station, passage and slope while current rehabilitation/opening remains unverified.
- Progress-test refactor: removed the stale literal count of 14. The native-integration test now derives the expected started count from the authoritative 81-record ledger, compares every public candidate's count exactly, checks the rendered count, and continues to assert zero ranking promotion. This supports ongoing equal-depth batches without weakening mismatch detection.
- Latest gates after batch 04: 72/72 architecture tests pass; `verify_architecture.py`, `verify_release.py`, Ruff C901 max 10 and `git diff --check` pass. Equal-depth completion remains 0/81 and all candidates remain fail-closed.
- Batch 04 browser gate: the regenerated hosted Challenge passed all six required Chrome viewports with HTTP 200, no horizontal overflow, no page/console errors, no failed resources, keyboard focus reached and exactly one AI-firewall region. QA JSON and screenshots were refreshed.
- Visual-forensics batch 05: Reducto Nº 2/Casa Museo Cáceres, Biblioteca Municipal de Barranco, Santísima Cruz del Viajero and Torres/Centro Empresarial Camino Real add 12 LINK_ONLY records. Coverage is now 22/81 candidates and 61 references; 59 candidates still lack current visual families. The scene hypotheses now distinguish Reducto's ceremonies/park/museum, the library's active restored rooms and civic park edge, the cross as devotional route residue inside traffic infrastructure, and Camino Real's temporal contradiction between emptied retail podium and functioning renovated office towers.
- Batch 05 gates: regenerated canonical/public candidate data and hosted/standalone output; 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass. No candidate is promoted; completion remains 0/81.
- Visual-forensics batch 06: LUM, Antigua Taberna Queirolo, Casa Museo Marina Núñez del Prado and Parque Tradiciones add 12 LINK_ONLY records. Coverage is now 26/81 candidates and 73 references; 55 candidates still lack current visual families. LUM is modeled as a cliff/esplanade/ramp/roof-return sequence; Queirolo as a street-threshold versus empty/occupied interior system; Marina Núñez del Prado as house, sculpture garden and guided creative-residue experience; Parque Tradiciones as a landscape/noise buffer whose seated Ricardo Palma sculpture is a dominant cliché rather than the whole scene.
- Batch 06 currentity: the San Isidro municipality published a May 2026 house-museum gallery, January 2026 guided-visit report, July 2026 visit, and current venue schedule. Those sources corroborate present cultural use but do not establish exact future tour timing or unrestricted photographic positions.
- Batch 06 gates: regenerated public progress data and hosted/standalone output; 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 07: Plaza de los Libertadores/Santa María Magdalena, Centro de Convenciones–Estación La Cultura, BNP San Borja and Biblioteca Municipal/borde de lagunas del Olivar add 12 LINK_ONLY records. Coverage is now 30/81 candidates and 85 references; 51 candidates still lack current visual families.
- Batch 07 mechanisms: Pueblo Libre is treated as plaza/church/interior/night ensemble rather than façade; La Cultura as structural funnel from street through turnstiles and as an event-sensitive civic interchange; BNP as lateral institutional mass, self-reflexive 2026 architecture exhibition, and study-room/terrace use; El Olivar as accessible cultural-center arrival plus a directly documented lagoon-to-library sightline.
- Batch 07 gates: regenerated public progress and hosted/standalone outputs; 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 08: Gran Teatro Nacional, MAC Lima/parque/espejo de agua, Museo Larco/jardines and Huaca Huallamarca add 12 LINK_ONLY records. Coverage is now 34/81 candidates and 97 references; 47 candidates still lack current visual families.
- Batch 08 mechanisms: GTN is modeled as public terrace–foyer–working backstage sequence linked to La Cultura; MAC as industrial galleries embedded in terrace, park and two documented water mirrors; Larco as an adapted eighteenth-century house assembled with recovered elements and occupied through garden/courtyard/terrace routes; Huallamarca as stepped monument, access ramp and site museum seen against the modern city or reduced by night light.
- Batch 08 currentity and constraints: current official institutional pages corroborate active GTN, MAC and Larco use; Larco permits ordinary personal photography but prohibits tripods, selfie sticks and photo sessions, so competition-oriented access remains VERIFY_BEFORE_ROUTE. Huallamarca's official visitor information corroborates daytime access, while its night-light reference is historical and cannot establish 2026 illumination or after-hours entry.
- Batch 08 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 09: Huaca Pucllana, Museo Pedro de Osma/avenue, Parque María Reiche and Puente de los Suspiros/Bajada de Baños add 12 LINK_ONLY records. Coverage is now 38/81 candidates and 109 references; 43 candidates still lack current visual families.
- Batch 09 mechanisms: Pucllana is a guided ascent and active archaeological workplace across day/night conditions; Pedro de Osma links an eclectic house and gardens to its avenue but interior photography is currently prohibited; María Reiche is a day-use cliff park whose LED geometry is maintenance-dependent; Suspiros is a bridge-over-descent movement system, while the former funicular remains only a killable temporal hypothesis unless physical residue reads in-frame.
- Batch 09 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 10: Parque del Amor/El Beso, Larcomar/acantilado, Faro La Marina/Parque Raimondi and Parque Kennedy/civic core add 12 LINK_ONLY records. Coverage is now 42/81 candidates and 121 references; 39 candidates still lack current visual families.
- Batch 10 mechanisms: Parque del Amor is treated as a maintained mosaic-wall/rotunda system whose care work can defeat the postcard; Larcomar as an excavated cliff section with suspended occupation and a historically reversible threshold; Raimondi as a multi-use coastal field and node in a longer malecón chain; Kennedy as an open cultural center with family play and organized cat care rather than cats as decorative foreground.
- Batch 10 currentity: Kennedy's playground reopening is verified July 2026. Larcomar's closure reference is historical and cannot establish present closure. Lighthouse/paragliding operation and all event cadence remain VERIFY_BEFORE_ROUTE.
- Batch 10 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 11: Bosque El Olivar, Casa-Hacienda Moreyra, Casa Raúl Porras Barrenechea and Casa García Bryce add 12 LINK_ONLY records. Coverage is now 46/81 candidates and 133 references; 35 candidates still lack current visual families.
- Batch 11 mechanisms: El Olivar is an ecological/cultural network sustained by visible care and patrimonial-tree routes; Moreyra is the former agricultural/administrative core adapted to hospitality; Porras is a restored domestic-to-research sequence behind a reservation threshold; García Bryce is a private three-edge modern house supported by archival/current plan-section comparison, never by inferred interior access.
- Batch 11 source-quality decision: center-financial and San Isidro municipal-palace candidates were deferred because the first search did not yield three sufficiently distinct, current visual families. No weak duplicate references were added to satisfy the count.
- Batch 11 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 12: Ministerio de Cultura/Museo de la Nación, Torre Banco de la Nación, Pentagonito/bordes cívicos and Coliseo Eduardo Dibós add 12 LINK_ONLY records. Coverage is now 50/81 candidates and 145 references; 31 candidates still lack current visual families.
- Batch 12 mechanisms: the former Museo de la Nación is tested as monumental administrative volume periodically reoccupied by living culture; the BN tower as one element in a larger civic enclave rather than a height icon; Pentagonito as secure military perimeter temporarily converted to inclusive civic/running infrastructure; Dibós as an arena whose exterior exercise, mass school arrival and sport section create distinct occupancy families.
- Batch 12 currentity and rejection rules: Ruraq Maki, Caral displays, Dibós exercise and student event are corroborated in 2026. A cancelled Pentagonito race is retained specifically as evidence against assuming advertised events occur; future listings remain discovery-only and VERIFY_BEFORE_ROUTE.
- Batch 12 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 13: Mirador Catalina Recavarren, Parque Municipal/entorno cívico, La Ermita and Santísima Cruz add 12 LINK_ONLY records. Coverage is now 54/81 candidates and 157 references; 27 candidates still lack current visual families.
- Batch 13 mechanisms: Recavarren is a cliff section with lower path/funicular residue and an explicitly saturated sunset cluster; Parque Municipal is a former-town-hall library and free cultural stage with credible older-adult daily use; La Ermita is currently a closed 480-day restoration site whose material phases must replace romantic ruin imagery; Santísima Cruz is the active replacement church whose ritual threshold can be compared with the damaged/restoring Ermita.
- Batch 13 currentity: La Ermita works are verified June 2026 and must be treated as closed/construction access. Santísima Cruz schedules and photography conditions remain direct-verification items. Historical event calendars do not become current route windows.
- Batch 13 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 14: Centro Cívico/Real Plaza, Jirón de la Unión, Damero/intersection and Quinta Heeren/restoration add 12 LINK_ONLY records. Coverage is now 58/81 candidates and 169 references; 23 candidates still lack current visual families.
- Batch 14 mechanisms: Centro Cívico is a brutalist civic complex converted to long-day retail occupation whose reuse claim must be tested; Jirón de la Unión is a pedestrian-commercial spine that periodically becomes a linear civic stage; the Damero is treated at intersection scale through changing traffic priority and removed cable clutter; Quinta Heeren is a municipal restoration start with material-reading evidence, not a completed public-space promise.
- Batch 14 currentity and rejection rules: Quinta acquisition is verified October 2025 and restoration start January 2026, but future cultural/neighbor use is not current fact. June 2026 Damero traffic restoration proves reversible operation, not a permanent route condition. Centro Cívico interior photography remains unverified.
- Batch 14 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 15: Puente Villena/Bajada Balta/Costa Verde, Puente de la Paz/Armendáriz, Óvalo de Miraflores and Palacio Municipal/Virgen Milagrosa add 12 LINK_ONLY records. Coverage is now 62/81 candidates and 181 references; 19 candidates still lack current visual families.
- Batch 15 mechanisms: Villena is a changing bridge-edge and upper-city-to-coast access system rather than a sunset icon; Puente de la Paz is tested against its saturated glass-floor/selfie use through the pedestrian-above-traffic section; the Óvalo is a 1963 civic node newly transformed after fifteen years of abandonment; the palace/church pair combines municipal service, worship, park circulation and a free public-arts interior.
- Batch 15 currentity and rejection rules: May 2026 polycarbonate work makes older Villena edge views stale until field confirmation. The Óvalo fountain reopened in May 2026, but show schedules and safe ground positions remain unresolved. Puente de la Paz normal-day density and current operating constraints require direct verification. Palace arts hours are current operator data; interior photography conditions remain unverified.
- Batch 15 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 16: Choquehuanca/Basadre residential corridor, Palacio Municipal/Casa de la Cultura San Isidro, Nuestra Señora del Pilar and Country Club Lima Hotel add 12 LINK_ONLY records. Coverage is now 66/81 candidates and 193 references; 15 candidates still lack current visual families.
- Batch 16 mechanisms: Choquehuanca/Basadre is resolved through distinct privacy/permeability/deep-lot residential devices rather than a generic luxury skyline; the former municipal palace is a 1934 civic building reoccupied within a multi-building cultural network; Pilar layers an eighteenth-century transferred altarpiece inside a twentieth-century parish born from hacienda urbanization; the Country Club links the 1927 hotel, former golf/polo grounds, living-gallery circulation and surrounding urbanization contract.
- Batch 16 currentity and rejection rules: current parish service times establish recurring ritual windows but not photography permission. Hotel and palace interiors remain access-sensitive. Commissioned architecture portfolios demonstrate designed mechanisms but cannot prove present human use, so field confirmation remains mandatory.
- Batch 16 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 17: Casa Hacienda Orbea, Calle Porta/verticalization, Sáenz Peña–Domeyer–pasajes and Casa Emilio Harth-Terré add 12 LINK_ONLY records. Coverage is now 70/81 candidates and 205 references; 11 candidates still lack current visual families.
- Batch 17 mechanisms: Orbea is a productive/domestic hacienda ensemble embedded in the contemporary city, not a courtyard postcard; Porta requires a same-frame surviving-house/high-rise relationship and uses demolition archives only as comparison; Sáenz Peña/Domeyer is a street-scale reuse network with repeatable survey viewpoints; Harth-Terré is an archival-plan-to-current-private-house comparison whose lateral entry and material details matter more than a frontal façade.
- Batch 17 currentity and rejection rules: Orbea is private and prior-coordination only, so it remains closed to routing. Harth-Terré has conflicting protection descriptions between academic and municipal sources, current conservation is unevaluated, and interior access is excluded. Porta surviving fabric and all Barranco business hours require field verification.
- Batch 17 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Batch 17 build recovery: the first combined 30-second call ended while the non-atomic builder was between deleting the old hosted tree and writing the new index, so release verification correctly raised `FileNotFoundError`. After consulting Python `pathlib`/`shutil` documentation and recording the rejected hypothesis, the same build was resumed as a tracked long-running session, exited 0 with metrics, and the release verifier passed. No application workaround or suppressed error was introduced.
- Visual-forensics batch 18: Parque de la Felicidad, Casa Museo Ricardo Palma, Centro Cultural Ccori Wasi and Aulario 104 add 12 LINK_ONLY records. Coverage is now 74/81 candidates and 217 references; 7 candidates still lack current visual families.
- Batch 18 mechanisms: Felicidad is a lagoon/play/amphitheater system periodically transformed into ecological civic infrastructure; Ricardo Palma is a small domestic museum whose adjacent-development damage and present maintenance displace the period-room cliché; Ccori Wasi reconnects an adapted founding-campus casona to current exhibition/reading/auditorium use; Aulario 104 is a 313 m learning bar whose split grades and double-height circulation must be tested through real student movement.
- Batch 18 currentity and rejection rules: Ricardo Palma is currently marked in maintenance and is not route-eligible. Felicidad's map hours are non-authoritative and require direct verification. Ccori Wasi's July 2026 show proves active use but not the next installation. Aulario award/architect sources prove design identity, never current access or ranking value.
- Batch 18 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 19: Centro Financiero Canaval y Moreyra/Rivera Navarrete, Huaca Julio C. Tello, Agrupamiento Chabuca Granda and Edificio Álvarez Calderón add 12 LINK_ONLY records. Coverage is now 78/81 candidates and 229 references; 3 candidates still lack current visual families.
- Batch 19 mechanisms: the financial center is a pedestrian/transit-capacity conflict rather than a skyline; Julio C. Tello is a small archaeological remnant and walking-corridor node embedded in residential streets; Chabuca Granda densifies traditional Lima types through mixed housing, shops and common thresholds; Álvarez Calderón requires archival repeat-view and a street-scale dialogue with newer cross-block development rather than award nostalgia.
- Batch 19 currentity and rejection rules: financial-center improvements and mobility studies are historical baselines requiring field revalidation. Julio C. Tello has one generic national-inventory locator explicitly marked weak. Chabuca Granda resident use and shop activity are unverified. Álvarez Calderón's award status supplies no score and current conservation/access remain unresolved.
- Batch 19 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass before dual-release regeneration. Completion remains 0/81 and eligibility remains fail-closed.
- Visual-forensics batch 20: the Pueblo Libre–Lince–Surquillo compact-city transect, Jirón Trujillo/Puente de Piedra and Cantagallo add 9 LINK_ONLY records. Candidate-specific visual-family coverage reaches 81/81 with 238 references and zero candidates missing the visual-family field.
- Batch 20 mechanisms: the transect is derived from current zoning transitions and precise block-scale change rather than an arbitrary three-district tour; Jirón Trujillo/Puente de Piedra is a lived heritage and mobility section linking renovated Rímac infrastructure, the river/expressway crossing and the historic axis; Cantagallo is represented through community-led productive, health and housing-space evidence rather than exoticized surface pattern.
- Batch 20 currentity and rejection rules: the transect remains a multi-frame research construct until one single scene can carry its argument. Puente access and river-edge stopping conditions require field verification. Cantagallo remains non-routable and non-photographable without explicit community collaboration and consent; hidden telephoto observation is prohibited. Housing contamination/risk evidence is historical and must not be presented as a current measurement.
- Batch 20 gates: 72/72 architecture tests, architecture verifier, release verifier, Ruff C901 max 10 and diff check pass. A direct invariant check reports 81 candidates, 81 visual-started, 238 references and an empty missing list. Completion remains 0/81 because visual-family coverage alone does not verify the ten passes or A–E proofs.
- Wow-factor discovery `WOW-LIMA-2026-08-28-A`: ten Lima Metropolitana buildings were compared by distinct one-frame mechanism rather than spectacle or awards. Six enter the research mix pending equal depth: Campus UTEC, Museo de Sitio Pachacamac, Centro de Investigación Universidad del Pacífico, MALI/Palacio de la Exposición, Palacio de Torre Tagle and Edificio El Pacífico. Casa Fernandini, Museo de Arte Italiano and Pabellón El Olivar remain discovery-only; MUNA is quarantined because current ministry evidence says it remains in process. All ten have explicit expert rejection and kill conditions; fame/award bonuses are forbidden; all remain non-rankable and non-routable.
- Wow-factor trade-offs: admitting six identities increases the potential equal-depth universe from 81 to 87 and therefore delays ranking, but preserves the user's all-places parity requirement. UTEC's famous façade, Pachacamac's sculptural concrete and Torre Tagle's balconies are treated as saturation risks, not advantages. Private or operationally uncertain architecture is not promoted merely because experts recognize its design quality.
- Wow-factor RED/GREEN: the missing discovery ledger produced four intended failures. After adding ten source-backed records, `test_wow_factor_discovery.py` passed 4/4 and the full architecture suite passed 76/76. `verify_architecture.py`, `verify_release.py`, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` passed. The system interpreter still lacks Ruff; the established pinned offline runner remains the reproducible lint path.
- Next action: create equal-depth records and visual families for the six pending-admission identities, then complete current source-backed ten passes and A–E proofs across the expanded research mix. Do not mutate the canonical count from 81 until those six pass the same admission invariants.
- Equal-depth detailed batch D: LUM, Centro Cultural Ccori Wasi and Puente de la Paz now each have ten current/source-backed pass answers, three composition questions, three distinct visual-reference families and five fully specified A–E field proofs. Every proof records position, height, orientation, focal, exposure intent, expected action, light, edge guards, wait/kill triggers, access/ethics and fallback. They transition to `DESK_VERIFIED_FIELD_PENDING`, never to field-proven, rankable or routable.
- Completion-model correction: `build_equal_depth_verification.py` no longer hard-codes an impossible zero-complete result. Desk completion is computed only when all ten passes are `CORROBORATED|VERIFIED`, all five proofs are `READY_FOR_FIELD`, three visual families exist and all three composition questions are present. Ranking and route eligibility remain independently false. Public candidate data and the Challenge now expose the computed 3/81 desk-verification count without presenting a ranking.
- Multi-angle exemplar state: all 81 canonical identities have visual families, totaling 238 LINK_ONLY records. Each record includes viewpoint family, likely camera height, approximate FoV, light/weather, people/activity, edges/background, cliché cluster, proof scope and limitation. The six wow-factor discoveries remain outside the canonical 81 and do not yet claim equal-depth visual coverage.
- Batch D GREEN: generated ledger reports `81 records / 3 complete`; full architecture suite passes 77/77; architecture verifier, release verifier, pinned offline Ruff C901 max 10 and diff check pass. Dual release regenerated successfully. Six required browser viewports pass with no overflow, page errors, console errors or failed resources and keyboard focus reached.
- Batch D debugging evidence: the old test assumed every evidence-updated record remained exactly `IN_PROGRESS`; pytest guidance supported an explicit two-state assertion for `IN_PROGRESS|DESK_VERIFIED_FIELD_PENDING`. The first local server bind was prohibited by the sandbox; Python `http.server` documentation confirmed explicit loopback binding, then approved execution succeeded. The first browser run targeted its default port 8766 while the server was on 8765; Playwright documentation confirmed unreachable targets throw at `page.goto`, and the runner's existing `ARCHITECTURE_QA_URL` override produced a six-viewport pass. No application error was suppressed.
- Immediate next batch: advance the next source-strong canonical candidates through the same detailed contract, prioritizing records whose current identity/use and multi-angle families are already corroborated. Completion remains 3/81, so ranking and routes stay prohibited.
- Equal-depth detailed batch E: Parque 3 de Octubre/Skatepark, Residencial San Felipe and PREVI now join the desk-verified/field-pending cohort. Each has ten sourced answers, three composition questions, at least three distinct visual families and five fully specified A–E proofs. Completion is 6/81; all 81 remain unranked and non-routable.
- Visual-family parity correction: aggregate coverage previously hid that Parque 3 had one family and PREVI two. Batch 21 adds municipal civic-park/obstacle-sequence views for Parque 3 and a 2026 resident-authorship transformation family for PREVI. The immutable visual history now contains 241 unique stable reference IDs.
- Incremental-merge correction: the first batch-21 form repeated three earlier IDs and the tests correctly rejected it. JSON Schema uniqueness guidance and Python mapping-update semantics supported a delta-only batch plus stable-ID aggregate merge. Earlier immutable batches remain valid and later deltas are tested as exact subsets of the generated ledger.
- Batch E uncertainty: Parque 3's 2019 hours remain stale and 2026 programming does not prove routine skate density. San Felipe sources do not verify access to every elevated path or resident tolerance for photography. PREVI publications span different prototypes and may not be generalized to a selected dwelling. These are preserved as direct field gates, not erased by desk completion.
- Batch E GREEN: generated ledger reports `81 records / 6 complete`; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff C901 max 10 and diff check pass. Dual release regenerated. Browser QA passes all six required viewports with HTTP 200, no overflow/errors/failed resources and keyboard focus reached.
- Equal-depth detailed batch F: Parque de las Américas, Antigua Taberna Queirolo and Centro Cívico/Real Plaza now have ten source-backed pass answers, exactly three candidate-specific composition questions, at least three visual angle/condition families and five complete A–E field proofs. Desk completion is 9/81; ranking and route eligibility remain 0/81.
- Batch F evidence decisions: Parque de las Américas separates periodic civic/environmental programming from ordinary daily use and rejects a monument/sign portrait. Queirolo uses operator history only for chronology and current program, preserving independent-conservation and photography-condition uncertainty; its target is service circulation shaped by the former pulpería room order, not nostalgia or product imagery. Centro Cívico combines CAMMP's 1966–1970 project/plan evidence with the current Real Plaza operator page; opening hours and program are verified, but photography policy, pedestrian peaks and the one-frame legibility of civic-to-commercial mutation remain field gates.
- Batch F source verification: current primary/official pages were retrieved on 2026-08-28 for Real Plaza Centro Cívico (daily 07:00–22:00 and current tenant/service program), the CAMMP project record, Antigua Taberna Queirolo history/current operation, and Pueblo Libre municipal Parque de las Américas programming. Periodic event evidence is never promoted to a daily route window.
- Batch F GREEN: `python3 -B -m pytest tests/architecture -q --tb=short -p no:cacheprovider` passed 77/77; `python3 scripts/verify_architecture.py`, `python3 scripts/verify_release.py`, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` passed. `python3 scripts/build_dual_release.py` exited 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Browser QA passed all six required viewports with no reported overflow, page/console errors or failed resources and keyboard focus reached.
- Batch F privacy state: only sanitized public source metadata, generated public candidate data, Challenge HTML and QA screenshots changed. Raw chat ZIPs, prompt archives and private inputs remain excluded. Re-run staged/build marker scan immediately before commit.
- Immediate next action: advance the next three source-strong canonical records through the same ten-pass/A–E contract. Do not rank, route or admit the six wow-factor discoveries until equal-depth parity is achieved.
- Equal-depth detailed batch G: Plaza de los Libertadores/Santa María Magdalena, Agrupamiento Chabuca Granda and Casa García Bryce now satisfy the same ten-pass, three-question, multi-angle and five-proof desk contract. Completion is 12/81; rankable and routable counts remain zero.
- Batch G access/currentity decisions: 2026 Pueblo Libre sources prove episodic procession, civic and cultural occupation but not a daily schedule or unrestricted parish-interior photography. Current Chabuca scholarship corroborates continued housing relevance while shop activity and common-space access remain direct field gates. Casa García Bryce remains a private dwelling; its 2025 registered visit is exceptional evidence, so every interior proof is event-only and public-edge fallback is mandatory.
- Batch G GREEN: 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and diff check pass. Dual release exited 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Browser QA passed all six viewports with no reported overflow, page/console errors or failed resources and keyboard focus reached.
- Batch G privacy state: changes contain public-source metadata, generated sanitized candidate output, Challenge HTML and regression screenshots only. Staged private-marker scan remains mandatory before commit.
- Immediate next action after checkpoint: continue with the next source-strong incomplete cohort; preserve 0/81 ranking/route eligibility until equal-depth and later promotion gates are complete.
- Equal-depth detailed batch H: Aulario 104/Universidad Ricardo Palma, Casa-Hacienda Moreyra and Casa Raúl Porras Barrenechea now meet the ten-pass, three-question, multi-angle and five-proof desk contract. Completion is 15/81; rankable and routable counts remain zero.
- Batch H currentity/access decisions: URP's active 2026-II semester corroborates campus occupation but not public access or Aulario photography; every interior campus proof is authorization-gated. Casa Moreyra's current operator verifies restaurant/event use and hours, but architectural photography remains venue-approved and hospitality imagery cannot substitute for unstaged evidence. Porras has a current reserved institute/house-museum listing and 2026 guided-visit program, but booking and photography confirmation are mandatory.
- Batch H GREEN: 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and diff check pass. Dual release exited 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Browser QA passed all six viewports.
- Batch H privacy state: only public-source metadata, sanitized generated data/pages and regression screenshots changed; staged private-marker scan is required before commit.
- Immediate next action: checkpoint batch H, then select the next evidence-strong incomplete cohort without changing ranking/route eligibility.
- Equal-depth detailed batch I: Gran Teatro Nacional, Museo Larco/jardines and Larcomar/acantilado now satisfy the ten-pass, three-question, multi-angle and five-proof desk contract. Completion is 18/81; rankable and routable counts remain zero.
- Batch I currentity decisions: GTN's dense 2026 program verifies active audience use while backstage remains registered-tour only and December maintenance is represented. Museo Larco's current rules distinguish ordinary photography from prohibited sessions and require advance authorization for professional work. Larcomar operates under a 2026 municipal agreement that also requires cliff-slope maintenance/reinforcement, so same-day works, barriers and sightlines remain route blockers until checked.
- Batch I GREEN: 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and diff check pass. Dual release exited 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`.
- Batch I browser recovery: the first run failed with `ERR_CONNECTION_REFUSED` because a yielded orchestration cell was mistaken for socket readiness. Official Playwright web-server and Python http.server documentation were consulted and the rejected hypothesis was recorded. A direct HTTP 200 readiness probe preceded the second run; all six viewports then passed. No application behavior was changed or error suppressed.
- Batch I privacy state: only public-source metadata, sanitized generated data/pages, Graph Memory debugging evidence and QA screenshots changed; staged private-marker scan remains mandatory before commit.
- Immediate next action: checkpoint batch I and continue the next evidence-strong cohort while eligibility remains fail-closed.
- Equal-depth detailed batch J: Country Club Lima Hotel, Puente de los Suspiros/Bajada de Baños and Quinta de los Libertadores/MNAAHP now satisfy the ten-pass, three-question, multi-angle and five-proof desk contract. Completion is 21/81; rankable and routable counts remain zero.
- Batch J currentity/access decisions: Country Club's operator verifies current hotel/restaurant/living-gallery use but not hotel-wide photography, so interior proofs are permission-controlled and public exterior fallback is mandatory. Suspiros is treated as crossing-over-descent infrastructure; current crowd/repair state must be checked and the historic funicular hypothesis is killed absent visible residue. Quinta's government sources establish museum visitation and raised-house sequence, but hours/reservations and photography conditions remain direct checks.
- Batch J GREEN: 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and diff check pass. Dual release exited 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. An HTTP 200 readiness probe preceded browser QA; all six viewports passed.
- Batch J privacy state: only public-source metadata, sanitized generated data/pages and QA screenshots changed; staged private-marker scan remains mandatory before commit.
- Immediate next action: checkpoint batch J and continue the next incomplete cohort without relaxing eligibility.
- Equal-depth detailed batch K: Biblioteca Nacional del Perú, Bosque El Olivar and Damero de Lima/intersection now satisfy ten source-backed passes, exactly three composition questions, at least three LINK_ONLY visual families and five complete A–E field proofs. Completion is 24/81; ranking and route eligibility remain zero.
- Batch K evidence decisions: BNP must show the hall-to-reading/terrace circulation contract and cannot rely on monumental façade or a temporary anniversary exhibition. El Olivar is treated as maintained civic/ecological infrastructure; permanent care is verified but worker or guided-tour timing is never promised. The Damero must read from one safe ground-level intersection through perpendicular built lines and flows; June traffic restoration and cable removal remain block- and time-specific.
- Batch K expert-rejection trade-off: public/source-rich scenes were advanced ahead of harder private-access records, improving verifiability without granting them rank. This leaves 57 canonical identities pending at equal depth and preserves the slower all-places parity requirement instead of optimizing a shortlist prematurely.
- Batch K GREEN: `python3 scripts/build_equal_depth_verification.py` reports 81 records / 24 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six viewports passed.
- Batch K debugging evidence: two aspirational/invented script paths failed. Python command-line documentation and repository file discovery confirmed that script arguments must resolve to real paths; the actual entry points are `scripts/generate_architecture_pages.py` and `tests/architecture/browser_round1_qa.py`. Both rejected commands and falsifiable replacements are recorded in Graph Memory.
- Batch K privacy state: only public-source metadata, sanitized generated candidate data/pages, Graph Memory debugging evidence and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch K, then advance the next source-strong incomplete cohort while keeping all ranking and route promotion fail-closed.
- Equal-depth detailed batch L: Biblioteca Municipal de Barranco, Iglesia Santísima Cruz and Calle Porta/verticalization now meet ten sourced passes, exactly three candidate-specific composition questions, at least three LINK_ONLY visual families and five fully specified A–E proofs. Completion is 27/81; ranking and route eligibility remain zero.
- Batch L currentity decisions: the municipal library publishes current hours and services, while its 2024 coworking detail is explicitly recheck-only. Santísima Cruz is confirmed as an active parish and architecturally documented, but current worship cadence and photography permission require direct contact. Calle Porta's seven-block low/high conflict and 2025 mobility project are corroborated, but surviving houses and construction conditions require a block-by-block field audit.
- Batch L expert-rejection trade-off: Calle Porta remains desk-verified despite unresolved final block selection because every proof contains a hard kill condition requiring a current same-frame low/high relation; desk verification is not route promotion. Santísima Cruz does not use a secondary 2026 mass directory as authoritative timing evidence. The library's episodic programs are not converted into routine activity windows.
- Batch L GREEN: `python3 scripts/build_equal_depth_verification.py` reports 81 records / 27 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six viewports passed.
- Batch L privacy state: only public-source metadata, sanitized generated candidate data/pages and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch L and advance the next three current-source-strong incomplete scenes; do not enable rankings or routes.
- Equal-depth detailed batch M: Huaca Pucllana, Huaca Huallamarca and Huaca Santa Cruz now satisfy ten source-backed passes, exactly three composition questions, at least three LINK_ONLY visual families and five complete A–E field proofs. Completion is 30/81; ranking and route eligibility remain zero.
- Batch M visual parity: Huaca Santa Cruz previously had only two candidate-specific visual families. Immutable visual batch 22 adds one official 2025 perimeter/night-renewal family, bringing the global stable-reference ledger to 242 and Santa Cruz to the same minimum of three.
- Batch M currentity decisions: Pucllana's public excavation participation and May agenda are verified 2026 events but explicitly finished; they prove a working-heritage mechanism, not a route window. Huallamarca's ramp is represented as modern conservation/reconstruction rather than untouched ancient fabric, and published hours require direct recheck. Santa Cruz's 2026 ceremony is episodic; ordinary perimeter movement is the repeatable fallback, while current lighting/access remain unverified.
- Batch M expert-rejection trade-off: all three famous huacas remain desk-verified only because each scene rejects the default ruin/skyline postcard and encodes a causal present-use mechanism with a hard field kill condition. Fame, night spectacle and cultural events add no score and cannot enable ranking or routing.
- Batch M GREEN: `python3 scripts/build_equal_depth_verification.py` reports 81 records / 30 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six viewports passed.
- Batch M privacy state: only public-source metadata, one LINK_ONLY visual reference, sanitized generated candidate data/pages and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch M, then advance the next three incomplete candidates without relaxing equal-depth or eligibility gates.
- Equal-depth detailed batch N: Parque Municipal/entorno cívico, La Ermita and Mirador Catalina Recavarren now satisfy ten source-backed passes, exactly three composition questions, at least three LINK_ONLY visual families and five complete A–E field proofs. Completion is 33/81; ranking and route eligibility remain zero.
- Batch N currentity decisions: Parque Municipal uses verified daily municipal-service volume only as evidence of credible civic life, never as proof that a workshop occurs outdoors. La Ermita is explicitly closed under a 480-day restoration begun June 2026; future accessible/cultural use is not current. Recavarren's public recovery project and 2025-updated inventory do not prove completion, barrier state or lower-path access, so every proof is same-day-access gated.
- Batch N expert-rejection trade-off: restoration and recovery uncertainty remain part of the scene rather than reasons to fabricate stable access. This supports desk hypotheses but deliberately prevents route promotion. The famous sunset at Recavarren, romantic ruin at La Ermita and picturesque civic ensemble receive no value unless a causal current relationship survives.
- Batch N GREEN: `python3 scripts/build_equal_depth_verification.py` reports 81 records / 33 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six viewports passed.
- Batch N privacy state: only public-source metadata, sanitized generated candidate data/pages and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch N and continue the next evidence-strong incomplete cohort with eligibility fail-closed.
- Equal-depth detailed batch O: Parque Kennedy/civic core, Parque del Amor/El Beso and Faro La Marina/Parque Antonio Raimondi now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five fully specified A–E field proofs. Completion is 36/81; ranking and route eligibility remain zero.
- Batch O currentity decisions: Kennedy's playground reopening is verified 2026-07-02 and its public-event capacity is documented, but event recurrence is not assumed and identifiable children remain privacy-sensitive. Parque del Amor's curved walls and cliff terraces are treated as social infrastructure; a 2024 exercise program proves capacity, not a 2026 schedule. Faro and Raimondi are adjacent malecón nodes, but one-frame continuity, wind, barriers and any paragliding activity remain same-day field tests.
- Batch O expert-rejection trade-off: iconic recognition is explicitly treated as a liability when it substitutes for architectural causality. Cats, romantic gestures, El Beso, sunsets, the lighthouse and paragliders confer no value by themselves. The candidates remain desk-ready only because every proof targets a repeatable spatial device and contains a hard kill condition; unresolved crowd/wind/access conditions deliberately prevent rank or route promotion.
- Batch O visual decision: the existing immutable visual batch 10 already supplies three distinct candidate-specific LINK_ONLY families for each scene. No redundant references were added merely to increase the global count, which remains 242.
- Batch O GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 36 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six required viewports passed.
- Batch O recovery evidence: incorrect assumptions about two JSON collection paths and unprivileged loopback binding failed visibly. The official jq and Python http.server documentation were consulted, all hypotheses were recorded in Graph Memory, schema-aware queries succeeded, and the narrow approved loopback server enabled runtime validation without changing application code.
- Batch O privacy state: only public-source metadata, sanitized generated candidate data/pages, Graph Memory debugging evidence and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch O, then advance three more incomplete canonical scenes under the same evidence and fail-closed eligibility contract.
- Equal-depth detailed batch P: Torres de Limatambo/supermanzana, Museo de la Electricidad/Tranvía and Conjunto Habitacional Palomino now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 39/81; ranking and route eligibility remain zero.
- Batch P currentity decisions: Limatambo's municipal polideportivo and a 2026 school fair establish current civic capacity but neither opens residential space nor promises event recurrence. Electroperú verifies the reopened museum, free entry and education program, while its Monday-Saturday schedule conflicts with Barranco's Tuesday-Saturday listing and no current source proves tram movement. Palomino remains residential and CAMMP reports good conservation, but later public-space research and the estate's scale prevent that condition from being generalized.
- Batch P expert-rejection trade-off: two housing candidates are advanced only as privacy-first public-edge hypotheses. Resident action, alteration and orientation difficulty are never treated as spectacle. The museum's tram is modeled as a static heritage artifact unless operation is directly observed and authorized. These constraints reduce apparent opportunity but prevent historical assumptions from becoming false route promises.
- Batch P GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 39 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six required viewports passed.
- Batch P privacy state: only public-source metadata, sanitized generated candidate data/pages and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch P and continue the next incomplete cohort without changing rank or route eligibility.
- Equal-depth detailed batch Q: Plaza a la Bandera, Parque Virginia Candamo and Unidad Vecinal Nº3 now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 42/81; ranking and route eligibility remain zero.
- Batch Q visual parity: Virginia Candamo previously had two families. Immutable visual batch 23 adds one official maintained-green-infrastructure family, raising the global stable-reference ledger to 243 and the candidate to the same minimum of three without redistributing source imagery.
- Batch Q currentity decisions: Plaza a la Bandera's ceremonies and programs establish civic capacity but not a repeatable schedule; everyday crossing is the fallback. Virginia Candamo's 2019 redesign establishes paths/equipment and Chinese-Peruvian commemorative elements, while the 2025 municipal ledger proves continuing green-space service but not current equipment/lighting condition. UV3 remains inhabited and modified; 2023 research documents narrowed paths, deteriorated equipment and safety/maintenance problems that directly contradict an untouched garden-city narrative.
- Batch Q expert-rejection trade-off: patriotic and Chinese-Peruvian symbols are context, never automatic subject value. UV3's residents, appropriations and deterioration are not spectacle. All proofs use public-edge/privacy-first positions and hard kill conditions, deliberately reducing apparent opportunity to avoid turning ritual, culture or lived housing into decorative content.
- Batch Q GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 42 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six required viewports passed.
- Batch Q privacy state: only public-source metadata, one LINK_ONLY visual reference, sanitized generated candidate data/pages and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch Q and continue the next three incomplete canonical scenes under unchanged fail-closed eligibility.
- Equal-depth detailed batch R: Unidad Vecinal Matute/complejo deportivo, Lima Centro de Convenciones and Casa Museo Julia Codesido now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 45/81; ranking and route eligibility remain zero.
- Batch R visual parity: Julia Codesido previously had two families. Immutable visual batch 24 adds one official house/workshop/current-condition family, raising the global stable-reference ledger to 244 without redistributing source imagery or implying 2026 access.
- Batch R currentity decisions: Matute's renewed sports complex opened 2026-05-14, but routine density and residential-path access remain field checks. LCC has repeated verified 2026 events and an active operation/maintenance procurement, but completed events are not route windows and covered-plaza access may be security-controlled. The Codesido foundation has a current legal museum-preservation purpose, while no authoritative current schedule or photography permission was found; every interior proof is authorization-gated.
- Batch R expert-rejection trade-off: Matute's sports action must remain caused by the housing/shared-space route, not spectacle. LCC event prestige and monumental form add no value absent visible crowd distribution. Codesido is desk-ready only as a permission-controlled hypothesis; denied access kills the interior concept rather than triggering invented or intrusive alternatives.
- Batch R GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 45 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. HTTP 200 readiness preceded browser QA; all six required viewports passed.
- Batch R privacy state: only public-source metadata, one LINK_ONLY visual reference, sanitized generated candidate data/pages and QA screenshots changed. Raw private inputs remain ignored; staged private-marker scan is mandatory before commit.
- Immediate next action: checkpoint batch R and continue the next incomplete cohort without relaxing equal-depth or eligibility gates.
- Equal-depth detailed batch S: Quinta Leuro/quintas históricas, Estación/restos del Funicular de Barranco and Reducto Nº2/Casa Museo Cáceres now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 48/81; ranking and route eligibility remain zero.
- Batch S currentity decisions: Quinta Leuro is a currently listed monument with documented shared paths, varied dwellings and retained fabric, but internal access and resident rhythms remain field gates; conflicting municipal architect attributions are preserved and excluded from the scene claim. Barranco's funicular is inoperative, and municipal restoration/museum language is prospective: no operation, completed museum or safe visible track is claimed. Reducto Nº2 has verified 2026 cinema and voting use, but those completed events prove civic capacity rather than future route windows; the museum building is explicitly a station replica within a genuine battlefield landscape.
- Batch S expert-rejection trade-off: Quinta Leuro rejects picturesque-house cataloguing unless the collective passage visibly distributes current domestic thresholds. The funicular rejects ruin texture and station portraiture unless obsolete slope infrastructure meets present movement from a safe public position. Reducto rejects locomotive/ceremony postcards unless memorial terrain or museum thresholds visibly cause a contemporary civic verb. These stricter tests reduce apparent opportunity but prevent historical narrative or captions from rescuing weak frames.
- Batch S GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 48 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. A generated-build-only loopback server returned HTTP 200 and all six required viewports passed.
- Batch S privacy correction: repository-root HTTP serving was rejected because it could expose ignored private inputs. Python's documented `--directory` boundary was applied to serve only `dist/canon6d_sota_hosted`; the corrected browser run passed and the failed assumption is recorded in Graph Memory.
- Batch S privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence are in scope. Raw private inputs remain ignored; staged/build private-marker scan remains mandatory before commit.
- Immediate next action: checkpoint Batch S, then advance the next three incomplete canonical scenes without enabling ranking or routes.
- Equal-depth detailed batch T: Huaca San Borja, Santísima Cruz del Viajero and Torres/Centro Empresarial Camino Real now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 51/81; ranking and route eligibility remain zero.
- Batch T visual parity: Huaca San Borja previously had two visual families. Immutable visual batch 25 adds a current official heritage-mediation/activity family, raising the global stable-reference ledger to 245 without redistributing imagery or converting an episodic event into routine access.
- Batch T currentity decisions: a May 2026 Ministry activity proves mediated access at Huaca San Borja but not daily admission; earlier closure research remains a contradiction and every internal proof is authorization-gated. Cruz del Viajero is currently listed open and landscaped, but offerings, pedestrian density and lighting are field observations rather than scheduled facts. Camino Real's three office towers completed a major 2024 renovation and remain operational, while the commercial-center relaunch is still prospective; the complex is not described as uniformly renewed.
- Batch T expert-rejection trade-off: Huaca San Borja rejects aerial ancient/modern spectacle unless ground-level archaeological form governs current movement or mediation. Cruz del Viajero rejects an isolated devotional-object portrait unless the old waypoint visibly affects present travel. Camino Real rejects corporate glass hero imagery and unsupported dead-mall nostalgia unless active office circulation and unresolved podium space coexist in one current frame. These conditions deliberately preserve uncertainty and prevent premature routing/ranking.
- Batch T GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 51 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Generated-build-only HTTP readiness succeeded and all six required browser viewports passed.
- Batch T privacy state: only public-source metadata, one LINK_ONLY visual family, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch T and advance the next three incomplete canonical scenes under unchanged fail-closed eligibility.
- Equal-depth detailed batch U: Casa Museo Marina Núñez del Prado, Parque Tradiciones/Ricardo Palma and Centro de Convenciones/estación La Cultura now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 54/81; ranking and route eligibility remain zero.
- Batch U currentity decisions: the Marina museum has current 2026 municipal operation and repeated preregistered guided visits, but same-day entry and photography remain confirmation gates; its adjacent patrimonial olive supports a landscape relation without being attributed to the sculptor's design. Tradiciones' 120 m² play area reopened July 2, 2026, proving current family infrastructure but not a photography window or child density. La Cultura handled 7.6 million trips January–May 2026 and has current street-level bus information; the future Line 4 interchange is explicitly not current infrastructure.
- Batch U expert-rejection trade-off: Marina rejects sculpture documentation unless house, former workshop, garden and grove form one causal sequence. Tradiciones rejects staged bench/statue interaction and child spectacle unless park design integrates memory with ordinary adult/family use. La Cultura rejects generic train/viaduct imagery and the forced convention-center pairing; its frame must show street decision becoming controlled vertical transit. These narrower scene claims reduce narrative breadth to increase one-frame truth.
- Batch U GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 54 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Generated-build-only HTTP readiness succeeded and all six required browser viewports passed.
- Batch U privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch U and advance the next three incomplete canonical scenes under unchanged fail-closed eligibility.
- Equal-depth detailed batch V: Biblioteca Municipal/borde lagunas del Olivar, Centro Financiero Canaval y Moreyra–Rivera Navarrete and MAC Lima/parque-espejo de agua now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 57/81; ranking and route eligibility remain zero.
- Batch V currentity decisions: weekly 2026 reading-club activity and permanent lagoon maintenance are verified independently, but their same-frame overlap remains a field hypothesis. Canaval y Moreyra's expanded vestibules and Andrés Reyes addition are verified in May 2026, while additional boarding works and sidewalk comfort require direct recheck. MAC's 2026 programs prove active mediation and outdoor occupation, but the two water mirrors' current condition and event photography rules remain same-day gates.
- Batch V expert-rejection trade-off: the Olivar scene rejects picturesque reflection unless the library threshold causes a reading/crossing/maintenance verb. The financial district rejects tower spectacle and anonymous rush-hour density unless trench, vestibule, bridge/sidewalk and office entry form a legible section. MAC rejects perfect reflection and museum-event documentation unless gallery volumes, terrace, water and park visibly distribute cultural life. This preserves equal detail while preventing attractive but causally weak images from advancing.
- Batch V GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 57 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Generated-build-only HTTP readiness succeeded and all six required browser viewports passed.
- Batch V privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch V and advance the next three incomplete canonical scenes with eligibility still fail-closed.
- Equal-depth detailed batch W: Puente Villena/Bajada Balta/Costa Verde, Casa Hacienda Orbea and Calle Choquehuanca/Basadre residencial now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 60/81; ranking and route eligibility remain zero.
- Batch W currentity decisions: Villena's new transparent panels were completed June 11, 2026 and lighting/resurfacing are current, while Bajada Balta maintenance begun June 30 still requires completion/barrier verification. Orbea remains currently marked closed; older coordinated-entry language does not override that status and every interior proof is killed without explicit owner authorization. Choquehuanca 1424 and Basadre are verified designer-documented projects, but their corridor-wide relationship, current occupation and screen/void visibility remain field-selective.
- Batch W expert-rejection trade-off: the coastal candidate must choose one crossing/descent relation rather than use three adjacent systems as a caption-built story. Orbea accepts closure as meaningful absence only if the public enclosure visibly meets contemporary street life; otherwise the candidate is killed. Choquehuanca/Basadre rejects façade cataloguing, montage and telephoto surveillance: one privacy/depth device must visibly affect one current residential gesture from public ground.
- Batch W GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 60 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Generated-build-only HTTP readiness succeeded and all six required browser viewports passed.
- Batch W privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch W and advance the next three incomplete canonical scenes under unchanged fail-closed eligibility.
- Equal-depth detailed batch X: Palacio Municipal y de la Cultura de San Isidro, Sáenz Peña/Domeyer/pasajes and Casa Emilio Harth-Terré now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 63/81; ranking and route eligibility remain zero.
- Batch X currentity decisions: Palacio evidence verifies repeated 2026 council sessions and cultural programming, but civic and gallery uses may occupy different rooms and times, so one frame must choose one primary relationship. The March 2026 Ministry authorization for Sáenz Peña Stage I proves authorization, not construction start or completion; works and passage operators require field verification. Harth-Terré is an officially listed national monument and remains a private residence; CAMMP's conflicting no-protection field is preserved as a data-quality contradiction, while deterioration or demolition is not presented as current fact.
- Batch X expert-rejection trade-off: Palacio rejects stacking civic and cultural narratives unless both are simultaneously visible. Sáenz Peña rejects a montage of avenue, Domeyer and passages; the field frame must select one threshold where adaptive reuse channels present movement. Harth-Terré rejects façade-only reverence, window surveillance and telephoto intrusion; only a public-edge relation between entry geometry, boundary and ordinary street use survives. These constraints reduce apparent opportunity to protect one-frame causality and evidentiary accuracy.
- Batch X GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 63 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Generated-build-only HTTP readiness succeeded and all six required browser viewports passed.
- Batch X privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch X and advance the next three incomplete canonical scenes under unchanged fail-closed eligibility.
- Equal-depth detailed batch Y: Parque de la Felicidad, Ministerio de Cultura/former Museo de la Nación and Museo Pedro de Osma/Av. Pedro de Osma now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 66/81; ranking and route eligibility remain zero.
- Batch Y currentity decisions: two 2026 Parque de la Felicidad programs prove periodic ecological/civic occupation, not daily density or a future event window. Official Ministry language identifies its San Borja headquarters as what was the Museo de la Nación; Ruraq Maki and a monthly display prove selected public uses but not ordinary museum opening. Pedro de Osma is currently open Tuesday-Sunday 10:00-18:00, while its current visitor rules prohibit interior photography, so default proofs are exterior-only.
- Batch Y expert-rejection trade-off: Felicidad rejects reflection/bridge beauty and event spectacle unless permanent landscape devices visibly order action. The Ministry candidate rejects monumental façade and craft-market documentation unless inherited museum circulation visibly governs present administration/exchange. Pedro de Osma rejects interior imagery under the published rule and mansion nostalgia; its viable frame must show avenue, gate, garden and current arrival from public ground unless explicit competition-photography authorization is obtained.
- Batch Y GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 66 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release exits 0 with hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`. Generated-build-only HTTP readiness succeeded and all six required browser viewports passed.
- Batch Y privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch Y and advance Torre Banco de la Nación, Parque María Reiche and Parroquia Nuestra Señora del Pilar under unchanged fail-closed eligibility.
- Equal-depth detailed batch Z: Torre Banco de la Nación, Parque María Reiche and Parroquia Nuestra Señora del Pilar now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three distinct LINK_ONLY visual families and five complete A–E field proofs. Completion is 69/81; ranking and route eligibility remain zero.
- Batch Z currentity decisions: Banco de la Nación records prove an operating secured headquarters and controlled official visits, not a public observation deck or photography access. María Reiche has recurring/episodic 2026 exercise and environmental use, while a 2025 municipal diagnosis and repeated LED repairs make paths, services and illumination VERIFY_BEFORE_ROUTE. El Pilar publishes current recurring Mass/office hours, but service attendance never supplies photography permission or consent.
- Batch Z expert-rejection trade-off: Banco de la Nación rejects tallest-building, skyline and reflection spectacle unless podium architecture visibly converts city arrival into controlled vertical work. María Reiche rejects sunset and glowing-glyph postcards unless symbolic and ecological infrastructure causes present bodily movement. El Pilar rejects frontal symmetry, wedding coverage and isolated retablo imagery unless inherited parish architecture visibly channels ordinary communal ritual with explicit permission.
- Batch Z GREEN: `python3 -B scripts/build_equal_depth_verification.py` reports 81 records / 69 complete; 77/77 architecture tests, architecture verifier, release verifier, pinned offline Ruff 0.12.11 C901 max 10 and `git diff --check` pass. Dual release hashes remain hosted `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`; all six required browser viewports pass.
- Batch Z privacy state: only public-source metadata, sanitized generated candidate data/pages and QA evidence changed. Raw private inputs remain ignored; staged/build private-marker scan is mandatory before commit.
- Immediate next action: checkpoint Batch Z and advance Pentagonito/bordes cívicos, Casa Museo Ricardo Palma and Óvalo de Miraflores under unchanged fail-closed eligibility.
- Equal-depth detailed batch AA: Pentagonito/bordes cívicos, Casa Museo Ricardo Palma and Óvalo de Miraflores now satisfy ten source-backed passes, exactly three candidate-specific composition questions, at least three LINK_ONLY visual families and five complete A–E proofs. Completion is 72/81; ranking and route eligibility remain zero.
- Batch AA currentity decisions: a verified June Pentagonito race and a separately cancelled July event prove both civic use and schedule uncertainty; military/security details remain excluded. Ricardo Palma remains operator-marked in maintenance/closed despite an administrative service schedule, and 2024 damage is not presented as ongoing. Óvalo Central reopened 26 May 2026, while light/water operation, post-novelty use and safe viewpoints require same-day verification.
- Batch AA expert-rejection trade-off: Pentagonito rejects race and military spectacle unless the secure edge visibly enables public movement. Ricardo Palma rejects nostalgia, window views and unsupported damage claims unless closure/urban pressure is visible from public ground. Óvalo rejects fountain spectacle, light trails and unsafe central positions unless renewed infrastructure changes a legal pedestrian decision.
- Batch AA merge correction: the first build produced 70/81 because lexical filename order placed `batch_aa` before older `batch_c`, whose partial pass objects then overwrote newer evidence. RFC 7386 confirmed precedence is semantically material. Evidence documents now sort by `retrieved_at` with filename tie-breaker, and a regression asserts all three Batch AA records retain substantive newer answers.
- Batch AA GREEN: builder reports 81 records / 72 complete; 78/78 architecture tests, architecture verifier, release verifier, pinned Ruff C901 max 10 and diff check pass. Dual release hashes remain hosted `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`; explicit browser output confirms six viewports passed.
- Batch AA privacy state: public metadata, sanitized generated data/pages, the precedence regression and QA evidence only; raw private inputs remain ignored.
- Immediate next action: checkpoint Batch AA and advance Coliseo Eduardo Dibós, Huaca Julio C. Tello and Palacio Municipal/Virgen Milagrosa under unchanged fail-closed eligibility.
- Equal-depth detailed batch AB: Coliseo Eduardo Dibós, Huaca Julio C. Tello and Palacio Municipal/Virgen Milagrosa now satisfy ten source-backed passes, exactly three candidate-specific questions, at least three LINK_ONLY visual families and five complete A–E proofs. Completion is 75/81; ranking and route eligibility remain zero.
- Batch AB currentity decisions: repeated completed 2026 Dibós programs prove active arena and exterior use but not future admission or photography. Pueblo Libre's current corridor marks Julio C. Tello open, while hours, conservation and visitor route remain field checks. Official Miraflores records verify palace/church identity and function, not a synchronized event or guaranteed one-frame relationship.
- Batch AB expert-rejection trade-off: Dibós rejects athlete/stage/crowd reportage unless portals, concourses and tiers visibly create collectivity. Julio C. Tello rejects mound/sign inventory unless the protected edge redirects current neighborhood movement. Palacio/Virgen rejects paired postcards and caption-built duality; every proof kills the combined candidate if both thresholds and one choice gesture cannot coexist legally in frame.
- Batch AB GREEN: builder reports 81 records / 75 complete; 78/78 architecture tests, architecture verifier, release verifier, pinned Ruff C901 max 10 and diff check pass. Dual release hashes remain hosted `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`; all six required browser viewports pass.
- Batch AB privacy state: public metadata, sanitized generated data/pages and QA evidence only; raw private inputs remain ignored.
- Immediate next action: checkpoint Batch AB and advance Edificio Álvarez Calderón, Quinta Heeren/restauración 2026 and the compact-city transect under unchanged fail-closed eligibility.
- Equal-depth detailed batch AC: Edificio Álvarez Calderón, Quinta Heeren/restauración 2026 and the Pueblo Libre–Lince–Surquillo compact-city transect now satisfy ten source-backed passes, exactly three candidate-specific questions, at least three LINK_ONLY visual families and five complete A–E proofs. Completion is 78/81; ranking and route eligibility remain zero.
- Batch AC currentity decisions: CAMMP records Álvarez Calderón as inhabited and in good condition, but not as a dated 2026 survey; an undated intervention listing remains partial. MML acquisition of Quinta Heeren is verified, while restoration phase and access are unresolved. Official zoning and a 2026 Lince dispute prove development pressure, not a photographable three-district condition.
- Batch AC expert-rejection trade-off: Álvarez Calderón rejects modernist cataloguing and resident surveillance unless the portico visibly mediates current collective housing. Quinta Heeren rejects ruin/ghost/restoration spectacle unless public ownership and street life meet at a visible legal threshold. The transect is only a selection protocol: all proofs require one sourced block and reject the candidate if an itinerary, collage or comparative caption remains necessary.
- Batch AC GREEN: builder reports 81 records / 78 complete; 78/78 architecture tests, architecture verifier, release verifier, pinned Ruff C901 max 10 and diff check pass. Dual release hashes remain hosted `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`; all six required browser viewports pass.
- Batch AC privacy state: public metadata, sanitized generated data/pages and QA evidence only; raw private inputs remain ignored.
- Immediate next action: checkpoint Batch AC, complete Jirón Trujillo/Puente de Piedra, Jirón de la Unión and Cantagallo, then run the full 81-candidate completion audit without enabling ranking or routes.
- Equal-depth detailed batch AD: Jirón Trujillo/Puente de Piedra, Jirón de la Unión and Cantagallo now satisfy ten source-backed passes, exactly three candidate-specific questions, at least three LINK_ONLY visual families and five complete A–E proofs. The canonical equal-depth universe reaches 81/81; ranking and route eligibility remain zero.
- Batch AD currentity decisions: Jirón Trujillo has verified 2025 mobility renewal but Puente de Piedra's precise 2026 condition/safe stopping remains field verification. Jirón de la Unión's current inventory and January 2026 walk prove active pedestrian/memory use, while completed events are not future windows and one block must be selected. Cantagallo has verified 2026 community programs, but historical contamination/housing data are not current measurements and photography remains impossible without community-led collaboration and consent.
- Batch AD expert-rejection trade-off: Jirón Trujillo rejects skyline/bridge/heritage-route imagery unless one safe crossing section visibly joins current mobility layers. Jirón de la Unión rejects the nine-block vanishing-point crowd unless one lateral threshold carries commerce, memory or civic action unaided. Cantagallo has no outsider fallback: no consent/collaboration means no image; telephoto, vulnerability and Kené extraction are explicitly prohibited.
- Final equal-depth invariant: a dedicated regression now asserts exactly 81 records, all complete, all with current source IDs, ten nonempty source-linked pass answers, five proofs, at least three LINK_ONLY visual families, exactly three questions, and zero ranking/route eligibility. It passes with the complete suite at 79/79.
- Batch AD GREEN: builder reports 81 records / 81 complete; 79/79 architecture tests, architecture verifier, release verifier, pinned Ruff C901 max 10 and diff check pass. Dual release hashes remain hosted `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c` and standalone `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`; all six required browser viewports pass.
- Final equal-depth privacy state: public metadata, sanitized generated data/pages, final invariant test and QA evidence only. Raw private inputs remain ignored; public build/archive marker scans are clean.
- Next project action after this objective: use the now-equal-depth 81-scene evidence universe to build the robust ranking model and field routes; desk verification itself does not promote any candidate.
- Round 4 objective: rank all 81 equal-depth Lima scenes without importing historical order, expose uncertainty and keep routes closed until time-window/access evidence exists.
- Round 4 research benchmark: UK Government Analysis Function MCDA guidance and manual support normalized preference weights, explicit performance matrices, dominance review and sensitivity analysis; the model is a decision aid, not an outcome prediction. Rank-reversal literature informed the decision to expose scenario/rank distributions instead of trusting one scalar.
- Round 4 model/run: `architecture-ranking-v1.1.0` / `2026-08-30-r4-v5`; 81 scenes, R0 balanced official proxy, R1 anti-postal, R2 inhabitation/story, R3 formal/light/field feasibility; 2,000 fixed-seed perturbations per scenario at seed 20260830; six Pareto-front scenes; SHA-256 `e692b9d2ddf1b9cbfaae1f1875c784f56caa266627c5d25258ae2b2c6cc36a7d`.
- Round 4 historical isolation: Master82 raw criterion elicitation is explicitly declared as the base assessment provenance and canonicalized by identity; `masterRank`, R0-R3 ranks, robustIndex and fame are prohibited and absent from the performance matrix/generator feature access. Current equal-depth statuses, source sets and contradictions control confidence/access adjustments.
- Round 4 robust Top 15: PREVI; Edificio Álvarez Calderón; Centro Cívico/Real Plaza; Puente de la Paz/Armendáriz; Agrupamiento Chabuca Granda; Ccori Wasi; Parque 3 de Octubre; Residencial San Felipe; Quinta Heeren; Cantagallo; Unidad Vecinal Matute; Torres de Limatambo; Conjunto Palomino; compact-city transect; Unidad Vecinal Nº3.
- Round 4 field Top 5: Puente de la Paz/Armendáriz; Edificio Álvarez Calderón; Torres de Limatambo; Parque 3 de Octubre; Jirón de la Unión. Field rank now balances strategic value, causality, feasibility, access and evidence; route fit remains explicitly `NOT_EVALUATED_UNTIL_ROUND_5_TIME_WINDOW_ORIENTEERING`.
- Round 4 skeptical correction: v1.0.1 over-weighted convenience and placed strategically mid-ranked Reducto first in the field list. The immutable run remains provenance; v1.1.0 adds photographic upside and causality. Cantagallo remains robust/intellectual rankable but field rank 81 and cannot enter a route without community-led collaboration.
- Round 4 native UI: server-rendered 81-card ranking, R0-R3 selector, Top 5/15/40/all control, p10/p50/p90 range, Pareto marker, evidence confidence, separate field rank, Top 5 field cards, strongest counterargument, required view/light/action, kill and fallback. No-JS exposes all cards and rules; ranking JSON is PWA-core cached.
- Round 4 GREEN: `python3 -B -m pytest tests/architecture -q --tb=short -p no:cacheprovider` 87/87; architecture verifier PASS; release verifier PASS; pinned offline Ruff 0.12.11 C901 max 10 PASS; `git diff --check` PASS; deterministic rerun and immutable-write rejection tests PASS.
- Round 4 browser GREEN: Playwright-managed Chromium exits 0 after all six required viewports; each shows 81 under all, five under Top 5, R2 rank #1 first, no overflow/page/console/resource errors. System Chrome was rejected after a verified upstream macOS teardown hang.
- Round 4 build: dual release exits 0; hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c`; standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`.
- Round 4 privacy: public/build/archive scans contain zero raw private chat/prompt markers; only sanitized model, matrices, immutable runs, public ranking data, generated pages/build and QA artifacts are eligible to stage.
- Round 4 blockers/trade-offs: no formal stakeholder swing-weight workshop was performed, so scenario stability outranks tiny score differences; field rank has no live travel/time-window data; route eligibility is 0/81. Next action is Round 5 time-window orienteering, not automatic route promotion.

## Round 5 route checkpoint — 2026-08-30 23:32 America/Lima

- Objective: deliver district-pure, road-conforming Lima photography layers that open reliably on iPhone while retaining unresolved scenes outside published routes.
- Refs: FocalRuta baseline `60d86c56e104223988d4d77c6ca971ed16535c4f`; branch `agent/arquitectura-en-foco-2026`; latest committed checkpoint `95df867187c77920f7a15a0fa282e1b341c46a02`; Solarize `2.2.0` at `f2de955f2a2fd81dffeb7c538d83746e921e6cab`.
- Route run: `2026-08-30-r5-i6`; 60 verified stops, 15 layers, 10 districts, longest individual walking leg 2270.6 m. Exact permutation is used within bounded groups; path cover minimizes tour count before distance when no threshold-safe Hamiltonian path exists.
- New corroborated anchors: Huaca Santa Cruz, Casa Museo Marina Núñez del Prado and Instituto Raúl Porras Barrenechea. Each has an authoritative address, an independent named-place coordinate, provenance and district-polygon containment. Casa Museo Julia Codesido remains withheld because Nominatim returned only a road centerline.
- Six iterations: raw geocoder quarantine; district-token rejection; administrative-polygon containment; pedestrian matrix; exact permutation/path-cover audit; iPhone waypoint staging.
- Native UI: district selector, all route cards, mobile Google walking stages capped at five stops, singleton search links, KML/GeoJSON downloads, and an iPhone 13 Pro ELI5 guide. Six contemporary/Art Nouveau/brutalist discoveries are source-backed but remain admission-pending and do not silently enter ranks or routes.
- Failure recovery: direct DNS failure, empty composite geocoder results, non-atomic output deletion and transient curl receive error were researched and recorded. The builder now stages all map exports in a same-filesystem temporary directory, publishes with `os.replace`, removes stale files only after success and uses bounded retries for transient network failures.
- GREEN commands/results: architecture pytest 99/99; `python3 -B scripts/verify_architecture.py` PASS; `python3 -B scripts/verify_release.py` PASS; pinned Ruff 0.12.11 C901 max 10 PASS; `git diff --check` PASS after generator whitespace correction; browser route QA PASS at 390×844, 430×932, 844×390, 932×430, 820×1000 and 1440×1100 with zero overflow/page/console/resource errors.
- Build: hosted SHA-256 `b35b0bc0ff71ff97d7d5486cc46a361c99e2d274f5d4fcf5fe98a887eea7612c`; standalone SHA-256 `c7ebcf8c86713d05cdf2cddb1bb7b10b65b32cc7c43d7ecee86c242d0ff8808f`.
- Privacy: only public-source metadata, sanitized route data, generated maps/pages and QA captures changed. The generated build contains no raw chat/prompt filenames; raw private inputs remain ignored. No repository-root HTTP server was used.
- Blockers/trade-offs: 21 canonical concepts remain unrouted because geocoding is false, ambiguous, cross-district or not precise enough. Singletons are useful map layers but are explicitly not called walking tours. Snapshot OSM travel estimates are not live ETAs. Modern-style discoveries need equal-depth admission before ranking/routing.
- Exact next actions: research authoritative addresses/coordinates for the remaining named anchors; convert cross-district concepts to exact scene children or keep them excluded; complete style-discovery equal-depth dossiers; rerun route solve and both final quiet validation rounds before commit/deploy claims.

## Round 5 route/style continuation — 2026-08-30 23:55 America/Lima

- Objective: finish equal-depth evidence for the six modern/Art Nouveau/geometric discoveries and replace overly long district-route transfers with shorter road-network layers.
- Style evidence: UTEC, Torre Interbank, Casa Fernandini, Estación Desamparados, Edificio Petroperú and Torre Begonias now have ten substantive passes, five source-backed A–E proofs, exactly three composition questions and three LINK_ONLY multi-angle families each. All remain `DESK_VERIFIED_CANONICALIZATION_PENDING`, `ranking_eligible=false`, `route_eligible=false`.
- Native UI: the Radar now truthfully reports 6/6 complete dossiers and exposes one field question, the E-proof kill condition, a current source and reference-family count per building. It still says canonical reconciliation and full reranking are pending.
- Route benchmark decision: the former 2.5 km edge ceiling was rejected. Official pedestrian guidance uses approximately 800 m as a ten-minute catchment and tour-practice evidence favors short meaningful transfers. The solver now enforces 1.5 km maximum per road leg and the UI flags every leg over 800 m as a long transfer that should be split when the connecting street contributes no photographic story.
- Route run: `2026-08-30-r5-i6` regenerated from current OSM administrative polygons and routed-foot matrices; 60 verified stops, 20 district-pure layers, 10 districts, maximum road leg 1402.2 m. The former 2270.6 m San Borja and 2091.2 m Rímac jumps were split. Atomic staging preserved the prior build through an initial sandbox DNS failure.
- RED/GREEN: style page status regression failed then passed; 1.5 km route invariant failed on the old 1897.2 m leg then passed after regeneration; long-transfer UI regression failed before generation then passed. Final architecture suite 104/104; architecture verifier PASS; release verifier PASS; pinned Ruff 0.12.11 C901 max 10 PASS; `git diff --check` PASS.
- Browser: sanitized hosted-build server only; Playwright-managed Chromium passed 390×844, 430×932, 844×390, 932×430, 820×1000 and 1440×1100 with HTTP 200, no overflow, no page/console/resource errors, 20 route cards and iPhone-help HTTP 200. Updated screenshots and forensics live under `architectural_photography/qa/rounds/round5/`.
- Debug evidence: py_compile cache denial, wrong QA filename, macOS Chromium Mach-port denial, missing localhost server, sandbox bind denial, route-builder DNS failure and route-schema KeyError were researched and recorded in `state/graph_memory/rejected_edits.jsonl`; narrowly scoped browser/server escalation and canonical `legs` schema resolved the actual boundaries.
- Privacy: the local HTTP server was restricted to `dist/canon6d_sota_hosted`; a request to serve repository root was rejected because it could expose private inputs. No private workbench files were served.
- Trade-off: route layers increased from 15 to 20. This adds selector/card overhead but removes misleading 24–30 minute inter-stop walks. Six 0.84–1.40 km transfers remain and are now explicit warnings rather than hidden assumptions.
- Blockers: the six new discoveries are not yet part of the 81-scene canonical/ranking model; adding them requires a versioned 87-scene reconciliation and evidence-based assessment path that does not import historical Master82 ranks. Live deployment/Pages verification has not been performed in this checkpoint.
- Exact next actions: canonicalize the six discoveries as scene children without rewriting immutable 81-scene history; add non-historical performance assessments; rerank the full 87-scene universe; admit only route-safe winners; execute two quiet final validation rounds; then commit/PR/deploy and verify the live URL if repository permissions allow.
- 2026-09-01 route-usability follow-up: rejected the naïve hard 800 m clustering experiment after browser/forensic review showed 33 cards and 21 singleton layers versus the useful baseline. The supported expert rejection was fragmentation: a transfer threshold used as graph connectivity destroyed multi-stop walking-tour value.
- Accepted constrained model: the builder keeps a 1000 m hard connectivity ceiling; publication prefers 800 m and removes a long edge only when both resulting walks retain at least two stops. Result: 27 district-pure layers, 66 stops, one omitted interior Miraflores transfer, and five 840–995 m endpoint transfers retained because splitting would isolate a scene. Every retained transfer is disclosed in its card. Trade-off: compactness is improved without pretending every scene can form a compact tour; 14 verified singleton points remain points, not tours.
- Navigation/integration evidence: canonical and hosted home pages expose the Arquitectura en Foco challenge; the challenge returns to FocalRuta. `browser_whole_site_integration_qa.py` passed 390×844, 430×932, 844×390, 932×430, 820×1000 and 1440×1100 with zero page errors, zero horizontal overflow, unobscured entry, successful challenge navigation and successful round trip. Evidence: `architectural_photography/qa/final/whole_site_integration/report.json` and 12 screenshots.
- Route browser evidence: `browser_round5_route_qa.py` passed all six viewports with 27 cards, zero runtime/console/resource failures and per-layer screenshots. Forensic classifications: 5 compact multi-stop sequences, 5 disclosed retained endpoint transfers, 3 short barrier detours, and 14 singleton verified points.
- Exact GREEN commands: `python3 -B scripts/repair_architecture_route_snapshot.py`; `python3 -B scripts/generate_architecture_pages.py`; `python3 -B scripts/build_dual_release.py`; `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/architecture tests/test_repository_contract.py -q --tb=short -p no:cacheprovider` (123 passed); `python3 -B scripts/verify_architecture.py` (pass); `python3 -B scripts/verify_release.py` (pass); `uvx ruff==0.12.11 check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'` (pass); both browser QA commands (pass).
- Tooling/debug record: `python3 -m ruff` remains unavailable (`No module named ruff`). The first `uvx` attempt was blocked by the managed cache path; Astral's `UV_CACHE_DIR` documentation was consulted, but uv also required a sandbox-blocked tool-data path. The same pinned command passed outside the sandbox. Playwright initially failed at Chromium `MachPortRendezvousServer bootstrap_check_in`; Chromium source and the matching Codex sandbox issue confirmed an outer macOS Mach-registration restriction, and the unchanged QA passed outside the sandbox.
- External route service remains blocked: the OSM router stalled on the first fresh rebuild attempt and was not retried. The contained prior subpath is disclosed, not promoted to a new exact optimum. PREVI/Los Olivos remains withheld pending verified identity, coordinates, access and a stable route matrix; no fabricated district layer was added.
- Privacy state: generated public route data/pages and screenshots only. Raw chats/prompts remain ignored. Before commit, stage explicit architecture files only and scan the staged set; never stage `camera_purchase/`, `scripts/build_camera_value.py`, or `tests/camera_value/`.
- Exact next actions: run final staged privacy scan; commit the route-usability follow-up; open PR; inspect CI/diff; merge only if protected gates pass; verify Pages and the live home→challenge→home flow before updating live status.
- PR #9 CI recovery: GitHub Actions run `33541299167` failed with `ModuleNotFoundError: playwright` because a pure `route_assessment` unit test imported the browser-QA module, which imported Playwright eagerly. Pytest optional-dependency guidance was reviewed. Skipping the test was rejected because the classifier does not require a browser. Playwright is now imported only inside the browser `main()` entry point; prediction confirmed by the full minimal test environment locally: 131 passed. Architecture and release verifiers remain green.

## Round 2 learning-lab continuation — 2026-09-01 16:35 America/Lima

- Objective: expose the complete architectural-photography curriculum and convert verified video/source lessons into field-ready, interactive simulations native to FocalRuta.
- Refs: baseline/current main `338c180d7cf925ede982aefdddb5c133ab278116`; branch `architecture-learning-lab`; prior PR #9 Quality `33549695963` and Pages `33549696013` succeeded.
- Research benchmark: transcript-backed YouTube lessons are timestamped transfers rather than embeds; Nikon's PC-lens and composition guidance support viewpoint, tilt and hierarchy instruction; peer-reviewed active-learning, variable-retrieval and physical-simulation research support predict → manipulate → feedback → transfer. Each simulation declares that it is a pedagogical diagram, not an optical or pixel prediction.
- Delivered: all 17 lessons render with OBSERVA, PRUEBA, DIAGNOSTICA, ROMPE LA REGLA CUANDO, CANON 6D and CONCURSO; six transcript-backed video transfers link exact moments; four labs teach position/perspective, vertical convergence, hierarchy/edges and light/material; no-JS retains the essential field exercises; no video is embedded or needed offline.
- Expert-rejection decisions: rejected a video playlist because passive viewing does not prove field transfer; rejected photorealistic pseudo-simulation because the simplified geometry cannot predict a sensor image; rejected focal-length-as-compression language because camera position controls perspective; rejected hiding core instruction inside tooltips/details-only states. The concise cards keep first-read density manageable while every required field remains keyboard-accessible.
- RED/GREEN: the new Round 2 tests initially failed for missing lesson coverage, video synthesis, lab contracts, physics wording and no-JS fallback. Final `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/architecture tests/test_repository_contract.py -q --tb=short -p no:cacheprovider` passes 129/129; `python3 -B scripts/verify_architecture.py` PASS; `python3 -B scripts/verify_release.py` PASS; `PYTHONPATH=/private/tmp/focalruta-ruff-0.12.11 python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'` PASS; `git diff --check` PASS.
- Browser evidence: `browser_round2_learning_qa.py` and `browser_round1_qa.py` each pass 390×844, 430×932, 844×390, 932×430, 820×1000 and 1440×1100. The learning suite changes every control and independently asserts the fixed-position focal invariant; both suites report zero overflow/page/console/resource failures. Evidence is under `qa/rounds/round2/learning_labs/` and refreshed Round 1 captures.
- Debug record: the stale fixed ranking count in Round 1 browser QA was replaced with the canonical ranking-data count. The local HTTP server initially failed under sandbox socket binding; the already researched macOS sandbox boundary was honored and a narrowly scoped server exposed only `dist/canon6d_sota_hosted`. Ruff was absent from the base interpreter, so pinned 0.12.11 was installed only in `/private/tmp`; repository CI independently installs the same pin and runs C901.
- Privacy: raw chats/prompts remain ignored; public/build scans found no private filename/content markers. Only sanitized learning data, public source metadata, generated pages/build, executable tests and browser evidence are eligible for staging.
- Trade-offs: native SVG/HTML/CSS/JS was chosen over React/XYFlow/Motion to preserve the static, standalone and offline architecture; diagrams intentionally model one relation at a time and do not render lens distortion, exact projection, exposure or sensor output. External video playback requires a network, while all essential instruction remains local.
- Exact next actions: stage only this learning slice; run staged privacy/secret scan; commit and push; open PR; require Quality/Pages CI including pinned C901; merge only after green; verify live home → challenge → Learn, all four controls, service-worker behavior and return navigation before claiming deployment.

## Round 2 learning v2 blocked checkpoint — 2026-09-01 America/Lima

- Objective: extend the committed learning labs with the newly supplied 21-video set, a versioned cross-validation ledger, source-backed technique cards, LINK_ONLY visual exemplar families and a five-state composition-sequence lab.
- Requirements in scope: G01–G07, H03–H07, I01–I05, L-series learning/accessibility behavior and N-series privacy/offline behavior.
- RED evidence: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/architecture/test_round2_learning.py -q --tb=short -p no:cacheprovider` exited 1 with 14 passed / 4 failed. Intended missing contracts were ledger schema v2, technique cards, LINK_ONLY multi-condition exemplar families and the six-part/fifth-lab contract.
- Availability attempt: temporary dependencies `youtube-transcript-api 1.2.4` and `yt-dlp 2025.10.14` were installed under `/private/tmp/focalruta-video-research`; no repository dependency was changed. The first new video (`5zjA7yFPLr8`) returned yt-dlp provider error `The page needs to be reloaded`. The process was interrupted and exited 130 before its end-of-run ledger write.
- Gate decision: the expert/availability contract requires stopping after the first confirmed provider failure. No retry, alternate scraper, guessed title/channel/date, transcript summary, teaching attribution or strategic screenshot was used. The 21 exact IDs are retained only as unverified ID-level inputs with null attribution and `TRANSCRIPT_UNAVAILABLE` pending a later legitimate provider check.
- Files touched in the blocked round: `tests/architecture/test_round2_learning.py`, `architectural_photography/research/videos/VIDEO_LEDGER.json`, `scripts/research_video_ledger.py`, and this handoff. The committed page/data/build remain unchanged.
- Privacy: no captions, screenshots, raw chats or prompt archives were staged or copied into public output. Unrelated `camera_purchase/`, camera-value files and `LIVE_PAGES_QA.json` remain excluded.
- Unresolved failure: the v2 RED tests intentionally remain red and no GREEN/release/browser/quiet-round claim is made. Resume only when the YouTube metadata/caption service is demonstrably available; first make the acquisition script fail fast and atomic so one provider failure cannot continue through the batch.
- Persistence follow-up: the user explicitly requested smart retries and suggested Google Gemini. The installed plugin surface exposed no Gemini connector and no plugin-discovery action, so no claim of consulting Gemini was made. One independent exact-ID web-search batch for `5zjA7yFPLr8`, `ThImDec0ZNw`, `jjtjqhFsEoc` and `BaPIP21-jh4` returned unrelated YouTube results and no attributable record. Under the same first-confirmed-availability-failure gate, research stopped without trying transcript mirrors or converting search noise into evidence. A legitimate next input is creator-provided captions/transcripts, exported YouTube transcripts with timestamps, or restored exact-ID provider availability.
- Supadata MCP recovery: after the user securely configured `@supadata/mcp`, a 21-ID batch used `supadata_transcript` with `mode=native`, `text=false`, and 1,000-character timestamped chunks. Twenty English native caption tracks were captured; only `Rty9MHPFIxk` returned `transcript-unavailable`, consistent with the earlier direct `TranscriptsDisabled` result. Raw caption evidence is stored only under ignored `research/videos/transcripts/` with `SUPADATA_NATIVE_CAPTION` provenance and is not eligible for staging.
- MCP capability audit: `supadata_transcript` is valid for timestamped native captions; `supadata_check_transcript_status` is reserved for asynchronous jobs. Generic `supadata_scrape` against all 20 YouTube watch pages returned only YouTube's unsupported-browser shell and is rejected for title/channel/date provenance. Website `map`/`crawl` are irrelevant to single-video evidence and were not used. No AI `generate` or `auto` transcript mode was invoked.
- New RED evidence: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/architecture/test_round2_learning.py -q --tb=short -p no:cacheprovider` exits 1 with 13 passed / 5 failed. One legacy assertion still expects 21 occurrences rather than the now-correct 42/41 ledger; the other failures remain the intended ledger-v2 normalization, technique-card, exemplar-family and fifth-lab gaps. Exact title/channel/date verification remains incomplete and production learning content is unchanged.
- User-approved video substitution: removed caption-disabled `Rty9MHPFIxk` and replaced its occurrence with already-supplied, transcript-captured `vtrzEJjEL98`. The combined ledger remains 42 URL occurrences but now has 40 unique IDs; duplicate counts are `p0NlX54vKCA=2` and `vtrzEJjEL98=2`. The new supplied batch therefore has 21 occurrences / 20 unique IDs and complete native-caption coverage for all 20 unique videos.
- Follow-up duplicate correction: the user supplied four caption-verified alternatives. The duplicate `vtrzEJjEL98` occurrence was reduced to one; `skOVHEgBrZ0`, `dfjgV5r1e4k`, `Nzf8M4HiEUM` and `RuYJOWp05sk` were admitted after Supadata `mode=native` returned timestamped English captions for each. Combined ledger: 45 occurrences / 44 unique IDs; only `p0NlX54vKCA=2` remains duplicated. New batch: 24 occurrences / 24 unique videos, all with captured native-caption evidence. Exact title/channel/date verification and claim-level expert review remain pending.

## Round 2 learning v2 evergreen implementation — 2026-09-01 20:54 America/Lima

- Objective and requirements: implement G01–G07, H03–H08, I01–I05 and the learning/accessibility/offline portions of L/N while converting the expired public challenge into a progressive evergreen field lab. Canonical 87-scene data, routes, gear, PWA shell and historical competition evidence remain preserved.
- Delivered public learning: schema v2; path `SEE → POSITION → COMPOSE → LIGHT → WORK_THE_SCENE → FINISH → COMPETE`; 17 complete field cycles; nine technique families; 27 LINK_ONLY exemplar records across three conditions per family; five active SVG labs. The new composition lab isolates postcard, changed position, fixed-position focal, presence/absence and light/weather, with prediction, manipulation, feedback, limitation, transfer and misconception fields.
- Video ledger: 45 URL occurrences / 44 unique IDs. All 44 have captured native-caption evidence. The original 20 retain verified title/channel/date; 24 Supadata-captioned additions remain null-attribution and therefore publish no claims. Verified curriculum transfers now carry transcript timestamps in the ledger. No title, creator, date or claim was inferred from captions or search noise.
- Evergreen conversion: the public surface no longer exposes the expired 2026 deadline, jury or fixed 5–25 MB submission rule. The former ranking is framed as a non-predictive preparation matrix, and the former preflight is a local brief decoder covering source, eligibility, theme, files, deadline/time zone, releases/access and editing/AI. Immutable historic rules/runs remain research provenance.
- Expert-rejection decisions and trade-offs: Nikon PC guidance and Gestalt review reject focal-length-as-perspective magic and rule-only composition. Static SVG diagrams remain deliberately non-photorealistic because they cannot predict calibrated optics, weather or pixels. Public visuals are metadata/link-only; private transcript/screenshot evidence is not redistributed. The 24 new videos cannot be publicly attributed until exact metadata is independently verified, so their captions informed thematic cross-checking but not named claims.
- RED evidence: Round 2 began at 13 passed / 5 failed for legacy video counts, ledger-v2 shape, technique cards, exemplar families and the fifth lab. A Python 3.9 compatibility failure (`zip(strict=...)`) and non-idempotent migration `KeyError` were researched against Python documentation; the builder now validates row lengths and replaces the composition lab by ID. Two identical SHA rounds prove deterministic output.
- GREEN evidence: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/architecture tests/test_repository_contract.py -q --tb=short -p no:cacheprovider` passes 133/133; architecture verifier PASS; release verifier PASS; `/private/tmp/focalruta-ruff-0.12.11/bin/ruff ... C901` PASS; `git diff --check` PASS.
- Browser evidence: Round 1, Round 2 learning and whole-site suites each pass all six required viewports. The learning suite changes all five labs under reduced motion and verifies the fixed-position focal invariant. Reports show HTTP 200, keyboard focus, no overflow, no runtime/console/resource failures and successful home → challenge → home navigation. Chromium’s exact Mach-port sandbox denial was researched via openai/codex#21292; unchanged tests passed through narrow external execution.
- Privacy: transcript bodies remain ignored local research; public output contains only sanitized claims and source metadata. No API key or raw chat/prompt marker appears in the diff. Unrelated `camera_purchase/`, `scripts/build_camera_value.py`, `tests/camera_value/` and `LIVE_PAGES_QA.json` remain excluded.
- Remaining limitation: exact metadata for the 24 new caption tracks is still unavailable, so they remain `CAPTION_CAPTURED_ATTRIBUTION_BLOCKED`; this is an evidence limitation, not a runtime blocker. Live deployment/Pages verification was not performed.

## Conditional release gate — 2026-09-01 21:27 America/Lima

- User authorization: push, merge and deploy only if the exact repository standards and exhaustive Playwright checks pass. No Git or deployment mutation may proceed after a failing gate.
- Newly discovered RED: the first release-critical offline probe proved that a directory deep link was not matched by its precached `index.html`. Offline reload served the homepage at the challenge URL, producing `PLANS_DATA is not defined`, two 404 subresources and a failed learning-page assertion. MDN/web.dev cache-match and navigation-fallback guidance changed the hypothesis.
- Fix and independent GREEN: service worker v4 now tries the exact request and then a directory-to-`index.html` cache key before the generic root fallback. `browser_architecture_release_qa.py` proves shell entry, worker control, field-state save/reload, keyboard control, fifth-lab feedback, offline deep-route reload and no-JS core with zero page/console/resource errors.
- Exhaustive local browser evidence: Round 1 architecture, Round 2 learning and Round 5 route suites each pass all six required viewports (18 responsive runs); whole-site hosted-build navigation passes the same six (24 total responsive runs); the release-critical PWA probe passes persistence/offline/no-JS. Reduced motion, focus, control mutation, fixed-position focal invariant, overflow, authored resources and route help are covered by their respective suites.
- CI-equivalent GREEN: full repository pytest 141/141, architecture verifier PASS, release verifier PASS, pinned Ruff 0.12.11 C901≤10 PASS, visual/resource audit exit 0 and diff check PASS. Hosted and standalone artifacts were regenerated; hosted SHA-256 `534636e84b2a4c7a4b9504d300d8e9e66fdfe99f6f39ad67974b1b2c73f51f23`, standalone SHA-256 `66bad08f5f361a1539d6ea955be57a1dac6d05a4e93b7732d5ef82effab72c08`.
- Release sequence still required: explicitly stage only this architecture slice, scan staged content for private/API markers, commit and push the feature branch, open/update PR, wait for Quality CI, merge only on green, wait for Pages, then execute live differential/PWA QA before claiming deployment success.

## Round 5 route UX and threshold sensitivity — 2026-09-01

- Objective: make routes understandable to beginners, expose stop addresses/coordinates, provide offline maps and Google Maps fallbacks, and test ±50% around the 1000 m connectivity threshold.
- Delivered: 27 layer cards are grouped into 10 district collections; 14 singleton layers are labeled as independent points rather than tours. Every stop now has a brief address, latitude/longitude, KML, GeoJSON and a dependency-free offline SVG map. A downloadable Spanish field card and iPhone help page are generated with the subsite.
- Threshold evidence: 500 m, 1000 m and 1500 m screens were computed. Two singleton pairs fall under 1500 m straight-line distance (Palomino–Unidad Vecinal 3 at 1325.6 m; Puente de Piedra–Cantagallo at 1400.3 m), but no road matrix was captured. They remain explicit field/router candidates and are not merged on straight-line distance alone.
- Content/UI: public navigation and challenge copy now use “Fotografía arquitectónica”; the compatibility URL remains unchanged. The route copy explains segments, independent points, addresses and coordinates for first-time users. Existing downloadable cards, no-JS content and PWA shell remain intact.
- RED/GREEN: route browser QA initially exposed a stale expected-card invariant (27 layers versus 37 collection+detail cards); the test now independently counts both intentional surfaces. A sandboxed Chromium launch then failed with `MachPortRendezvousServer ... Permission denied (1100)`; exact-error research in OpenAI/Chromium issue reports confirmed the macOS sandbox boundary, and the unchanged six-viewport suite passed outside the sandbox. Final architecture suite 134 passed, architecture/release verifiers passed, pinned Ruff C901≤10 passed, route and whole-site six-viewport Playwright suites passed.
- Trade-offs: native SVG offline maps were chosen over Folium/remote tiles because they keep the static site standalone and avoid implying live optical or map accuracy. Threshold candidates are disclosed rather than merged until authoritative road distances exist; the external router previously stalled and was not retried under the availability gate.
- Artifacts: `data/architecture/routes.json`, generated route maps, `challenges/arquitectura-en-foco/field-card.html`, refreshed route/whole-site reports and screenshots.

## Round 5 beginner-content pass — 2026-09-01

- Added a self-contained “Cómo usar esta guía” explainer in plain Peruvian Spanish. It defines the preparation matrix (R0–R3), place cards, labs, route collections/independent points and brief decoder, and gives a recommended first-time workflow. It is static HTML and therefore remains available without JavaScript.
- Added an executable content contract requiring all five surfaces and the non-predictive matrix explanation. Architecture suite now passes 135 tests; architecture/release verifiers, pinned Ruff C901≤10 and six-viewport route/whole-site Playwright checks pass.
- Trade-off: canonical historical place narratives still contain source-preserved English quotations/fields in the underlying 87-scene dataset; translating those verbatim evidence fields would alter provenance. The new instructional chrome and route/field-card content is Spanish and explains how to interpret those source-backed fields.

## Round 6 Spanish-first content and visual polish — 2026-09-02

- Objective: remove user-facing English prose and fix the architectural guide's edge-hugging mobile layout while preserving evidence and compatibility URLs.
- Public rendering now uses Spanish beginner explanations for ranking cards, field priorities, style-discovery cards and video transfers. Internal source fields and URLs remain unchanged for provenance; proper names and technical acronyms are preserved where they identify a source or standard.
- CSS now applies a 24–72 px responsive content gutter, a 1160 px readable measure, improved card wrapping, section rhythm and a styled beginner glossary. Static no-JS content remains available.
- RED/GREEN: initial tests caught stale English label expectations and were updated to the new public contract. Final architecture/repository suite passes 136 tests; architecture/release verifiers and Ruff C901≤10 pass. Route and whole-site Playwright suites pass all six required viewports with no overflow or runtime/resource errors. Live Pages smoke test contains the beginner guide, Spanish ranking label and responsive gutter.
- Trade-off: translating the public presentation rather than raw evidence preserves source fidelity but means the underlying private/source dataset can still contain English quotations; those fields are no longer rendered in the beginner-facing cards.

## Visual learning, storytelling and video-wiki overhaul — 2026-09-02 11:13 America/Lima

- Objective / requirements: repair the composition visualization and anchor clearance; improve lab hierarchy, recovery, legends and responsive density; reorder the journey so learning precedes ranking/routes; add a Spanish technique wiki derived from the video ledger. Requirement mapping: A01/A04–A07, D05–D08, G04–G08, H03–H06, L06/L09/L10, N01–N08 and Q02–Q03.
- Expert benchmark and rejection gate: SVG 2 requires `display:none` to remove an SVG group and descendants from the rendering tree. The first `SVGElement.hidden` implementation produced identical raster hashes and was rejected. W3C SVG 2 rendering and MDN SVG visibility documentation changed the hypothesis: set the SVG group's `style.display` explicitly. Prediction: five mode screenshots produce five hashes; GREEN confirmed at every required viewport. Python's official dictionary documentation confirms subscription raises `KeyError` while `get()` supports absent optional metadata; the wiki therefore falls back from verified title to working title to video ID.
- RED evidence: `python3 -B -m pytest tests/architecture/test_round2_learning.py -q --tb=short -p no:cacheprovider` initially failed 3 new layout/lab tests (18 pass, 3 fail). The dedicated wiki test then failed because the artifact was absent. First wiki generation failed with `KeyError: 'working_title'`. First browser visual run passed anchor/reset/overflow but reported `composition_states_distinct=false` in all six viewports.
- GREEN behavior: five composition modes now contain state-specific SVG geometry, before/after panes and a persistent fixed-camera indicator for focal-only comparison. All five labs expose Predicción → Acción → Observación → Transferencia al campo, legends and keyboard-focus-returning reset controls. CSS supplies measured 84 px sticky clearance and desktop/tablet/mobile lab variants. Stable anchor IDs remain unchanged, while the public order is learn → style radar → places → ranking → priorities → routes → field worksheet → editing decoder.
- Wiki: `wiki-tecnicas.html` renders all nine canonical technique families with original causal diagrams, field test, observable diagnosis and invalidation warning. Every transcript-validated ledger claim is linked to its video timestamp. Videos without captured transcripts are counted and explicitly excluded from attributed teaching; raw transcript bodies remain local and are not republished.
- Verification: two consecutive quiet rounds of `python3 -B -m pytest tests/architecture tests/test_repository_contract.py tests/test_agent_debugging_contract.py -q --tb=short -p no:cacheprovider` passed 141/141; architecture and release verifiers passed; `/private/tmp/focalruta-ruff-0.12.11/bin/ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'` passed; `git diff --check` passed. The required direct `python3 -m ruff ...` command is blocked because Ruff is absent from the system interpreter; an offline `uvx` cache initialization also hit sandbox permissions, so the already pinned local 0.12.11 binary supplied equivalent executable evidence.
- Browser evidence: isolated-public-root learning QA passed all six required viewports with five distinct composition hashes, anchor clearance, reduced motion, keyboard-accessible controls/reset, no horizontal overflow and zero console/page errors. Whole-site hosted-dist QA passed the same six viewports with entry clearance, challenge round trip, zero overflow and zero page errors. The generic repository-wide HTTP server was rejected because it could expose private inputs; only public-root localhost servers were used.
- Build / privacy: dual release passed with hosted SHA-256 `b24cb8fac24c51d503e41a61d31f62fff3b89332b99b78dd7b71859ccb393dcd` and standalone SHA-256 `ab80ce6a540a829739598dc7e3d294afa946fd328579dc9f086caef837f4d514`. Public challenge/data/dist marker scan returned no private chat/prompt markers. Existing unrelated `camera_purchase/`, camera-value files and `LIVE_PAGES_QA.json` were not touched.
- Trade-offs / blockers: native SVG remains intentionally causal rather than photorealistic. The public wiki summarizes validated claims and creates diagrams from the canonical technique model; it does not claim that every source video visibly contains those exact diagrams. Public pages are longer because essential beginner context is visible.
- Follow-up authorization / live check: after the user explicitly authorized the destination, branch `architecture-learning-overhaul` was pushed, PR #11 merged as `dfcd6eb04c3ab09df58b90a3a88e46254e410b88`, Quality and Pages workflows passed, and the read-only `python3 -B scripts/live_pages_qa.py` passed 70 checks against the deployed site with zero failures. `LIVE_PAGES_QA.json` is ignored and remains outside the architecture slice.

## Physics visualization review and deployment — 2026-09-02 12:02 America/Lima

- Expert benchmark: pinhole projection (`h ∝ fH/z`), vanishing-point geometry, Lambertian directional shading, source-size-dependent penumbra, and SVG filter semantics. W3C SVG filter specifications document Gaussian blur, diffuse/specular lighting, point/distant/spot sources and compositing; Canon optics guidance supports focal-length/depth-of-field and camera-distance distinctions.
- Corrections: perspective lab now exposes projection equation and FOV wedge; vertical lab has horizon and moving vanishing point; light lab has directional arrow, gradient material, hard/soft shadow controls and Gaussian penumbra; hierarchy lab has explicit first/second/third reading layers. Glare, halo and reflection are labeled as material/angle/exposure cues, not calibrated predictions.
- RED/GREEN: new physics-model and anti-fake-effect tests initially failed on absent model attributes/copy; after implementation, 143 tests passed, architecture/release verifiers passed, Ruff C901≤10 passed and six-viewport browser QA passed. One browser assertion required updating from the old feedback phrase to the new projection-equation wording; the first generated page was correctly treated as stale until verifier expectations were updated.
- Deployment: PR #12 (`51a62d0`) merged as `0d875aa846e9fd625f4e3cbf3806d98d23d95e52`; Quality run `33659988923` and Pages run `33659988925` passed. Final live QA passed 70/70. Local/live HTML size is identical (277021 bytes) and all physics markers are present in both; no private markers appear live.
- Trade-off: these are physically coherent explanatory diagrams, not a calibrated renderer of a specific Canon 6D, lens, weather, BRDF or exposure pipeline. That limitation is explicit in public copy; adding photorealistic glare/reflections without measured material/light inputs would be an expert-rejected false precision.

## Whole-site editorial/usability five-pass review — 2026-09-02

- Scope: home, six plan pages, field card, architectural challenge, technique wiki, iPhone help, offline maps, no-JS fallback and hosted build.
- Benchmark: Will Francis' anti-AI-writing guidance (specific verbs, no filler, varied rhythm), GOV.UK user-needs/content principles (purpose and relationships first), Nielsen Norman progressive disclosure, WCAG focus/reflow guidance and W3C accessible visualization practice.
- Five passes: (1) information order and next action; (2) ELI5 context and glossary; (3) visual cause/evidence captions; (4) keyboard, recovery, no-JS and progressive disclosure; (5) mobile/offline/hosted consistency. The public layer now adds orientation before controls, explains every operational acronym, gives each plan a `Qué cambia / Cómo comprobarlo / Si no funciona` triad, and labels offline-map/diagram interpretation.
- RED/GREEN: `tests/architecture/test_whole_site_eli5.py` first failed all four contracts, then exposed three generated-surface gaps (plan orientation order, composition caption, stale map caption). After source fixes and regeneration, full architecture/repository/debugging suite passes 148 tests; architecture verifier PASS; release verifier PASS; pinned Ruff C901≤10 PASS; `git diff --check` PASS.
- Browser GREEN: learning and whole-site six-viewport suites pass; release-critical PWA probe passes persistence, service-worker control, keyboard, offline deep route and no-JS core with zero page/console/resource errors.
- Expert rejection and trade-off: style guidance was applied as a review lens, not a blanket banned-word filter. Provenance fields, proper names and URLs remain unchanged; public prose is clearer but source evidence is not rewritten. Longer orientation panels cost vertical space, accepted because hiding definitions would stump first-time users.

## Ronda 7 · Óptica calculada, nueve laboratorios, nueve diagramas y flujo alineado (2026-09-02)

**Objetivo.** Cerrar seis solicitudes: wiki de técnicas, corrección física de las
visualizaciones, estilo de escritura, cinco pasadas editoriales, diez
alternativas de flujo pedagógico y revisión completa del sitio. Requisitos:
G04, G05, G06, G07, H03–H08, I03, L05, L06, L10, M01, M03, M05, N01–N04, N08,
O03, O04, Q02, Q03.

**Relectura de contrato (Q02).** `AGENTS.md`, `REQUIREMENTS_INVENTORY.md`,
`CURRENT_STATE.json`, `SOLARIZED_REQUESTS_2026-09-02.md` y el generador de
páginas antes de editar.

### Rechazos de experto encontrados en el estado anterior

El checkpoint previo declaraba `PINHOLE_PROJECTION_VANISHING_POINT_LAMBERT_
SHADOW_PENUMBRA…` y `9_TECHNIQUE_FAMILIES_ORIGINAL_CAUSAL_DIAGRAMS_ALL_
VALIDATED`. La inspección del código generado contradijo ambas:

1. Los nueve diagramas de la wiki eran **el mismo SVG**, byte a byte salvo el
   `aria-label` (hash `128b35bf4581` ×9).
2. `halfFov = Math.min(58, 22 + focal/8)` **invertía la óptica**: el cono se
   abría al alargar la focal, contradiciendo la lección H03/H04 del propio lab,
   y contradiciendo `get_fov()`, que ya era correcta en el mismo repositorio.
3. `vanishingY = 64 − tilt·1.6`: lineal y en sentido contrario al real.
4. Las sombras eran cuatro polígonos escritos a mano; `cos` no aparecía en el
   JavaScript pese al atributo `data-physics-model="lambert-shadow"`.
5. `#composition-halo`, `#composition-glare` y `#composition-reflection` no eran
   tocados por ningún script: decoración presentada como fenómeno.
6. La barra de navegación ofrecía un orden que contradecía el orden real del DOM.
7. `ARCHITECTURE_MODULE_INVENTORY.json` declaraba 4 labs cuando había 5.

### RED antes de implementar

- `tests/architecture/test_optics_physics.py` — 16 invariantes físicos.
  RED inicial: `ModuleNotFoundError: No module named 'optics_physics'`.
- `tests/architecture/test_learning_flow_and_visual_uniqueness.py` — 9 contratos.
  RED inicial: 5 de 7 fallaban (orden de navegación, alcanzabilidad de secciones,
  unicidad de diagramas, anclas por técnica, índice por síntoma); después se
  añadieron en RED la detección de mapas huérfanos y la de identificadores
  duplicados, ambas fallando antes de la corrección.

### GREEN

- **`scripts/optics_physics.py`** (nuevo): única definición de la óptica del
  proyecto. `generate_diagrams.py` y `generate_lens_comparison.py` la importan;
  se comprobó **deriva numérica cero** en 270 casos de profundidad de campo y 9
  focales, de modo que los 120 diagramas PNG comprometidos siguen siendo
  reproducibles bit a bit (N08).
- **`scripts/lab_visuals.py`** (nuevo): geometría de los nueve laboratorios y de
  los nueve diagramas de la wiki. Python precalcula 194 estados y los incrusta
  como tabla JSON; el navegador sólo aplica atributos. Lo que verifica pytest es
  exactamente lo que dibuja la página.
- Labs 5 → **9**, uno por familia técnica: se añadieron espacio negativo y
  bordes, capas y perspectiva aérea, triángulo de exposición y reflejos/halo.
- Wiki reconstruida: nueve diagramas propios, anclas estables, índice por
  síntoma, referencia de física con fuente por fórmula y las 18 afirmaciones con
  marca de tiempo agrupadas por video.
- Navegación derivada de `STORY_ORDER`, la misma tupla que usa `reorder_story()`.
- `build_challenge_page()` unifica el pipeline que antes estaba duplicado entre
  `generate_architecture_pages.main()` y `verify_architecture.py`.
- Nueve archivos de mapa huérfanos retirados; dos colisiones de identificador
  (`light-source`, `depth-haze`) corregidas.

### Evidencia ejecutada

| Comando | Resultado |
|---|---|
| `python3 -m pytest -q` | 180 pass |
| `python3 scripts/verify_architecture.py` | `passed: true` |
| `python3 scripts/verify_release.py` | `passed: true` |
| `uvx ruff@0.12.11 check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'` | All checks passed |
| `browser_round1_qa.py` | passed, 6 viewports |
| `browser_round2_learning_qa.py` | passed, 6 viewports, 22 invariantes físicos |
| `browser_round5_route_qa.py` | passed, 6 viewports |
| `browser_architecture_release_qa.py` | ver registro de la ronda |
| `browser_whole_site_integration_qa.py` | ver registro de la ronda |

Los 22 invariantes medidos en el navegador incluyen: el cono se cierra al
alargar la focal y coincide con `2·atan(36/2f)`; la relación cerca/lejos no
cambia con la focal pero sí con la distancia; a 0° las verticales quedan
paralelas y la convergencia crece con la inclinación; la sombra gira en sentido
opuesto al sol y se alarga cuando el sol baja; una fuente ancha ensancha la
penumbra y borra la umbra; la bruma aplana el plano lejano; la tangencia sólo
avisa cuando el margen es corto; el orden de lectura sigue la variante; una
obturación lenta alarga la estela; cerrar el diafragma ensancha la zona nítida;
el ángulo rasante sube el reflejo y apaga el interior; y más exposición agranda
el halo.

### Compromisos declarados

- Los laboratorios calculan **dirección y orden de magnitud**, no píxeles,
  exposición real ni el comportamiento de una óptica concreta. El límite es
  visible en cada lab y detallado en `wiki-tecnicas.html#fisica`.
- Las tablas precalculadas añaden ~105 KB al HTML del reto. Se acepta a cambio
  de que el navegador no derive física por su cuenta.
- **Las rutas no se recalcularon**: `build_architecture_routes.py` depende del
  router OSM, registrado como `OSM_ROUTER_STALLED`. Por la regla de fallo rápido
  se conserva el `routes.json` verificado y no se reintenta.
- Nueve de las diez alternativas de flujo quedan **documentadas, no
  implementadas**. La comparación está en
  `research/pedagogical_flow_alternatives_2026-09-02.md`; construir diez flujos
  simultáneos contradice el propio criterio de carga cognitiva.
- Los diagramas siguen siendo síntesis originales: no se copió ninguna imagen
  externa ni se publicó transcripción privada (I03, L12).

### Documentos de investigación de la ronda

- `architectural_photography/research/visualization_physics_review_2026-09-02.md`
- `architectural_photography/research/pedagogical_flow_alternatives_2026-09-02.md`
- `architectural_photography/research/editorial_usability_review_2026-09-02.md` (segunda ronda)

### Escalación de depuración · `browser_architecture_release_qa.py` colgado

**Síntoma.** El guion no terminaba ni fallaba: se quedaba colgado más de diez
minutos sin escribir informe.

**Primera hipótesis (descartada).** Que las aserciones desactualizadas —cinco
laboratorios en vez de nueve, y un texto de teclado que ya no existía— lo
hicieran fallar. Se corrigieron y **siguió colgado**, así que la hipótesis era
falsa: una aserción falsa produce una excepción, no un bloqueo.

**Evidencia recogida antes del siguiente intento.** Se instrumentó cada paso con
tiempo y `timeout` propio, con salida sin buffer. `page.goto` respondía en 0,6 s
con estado 200; el siguiente paso,
`await navigator.serviceWorker.ready`, no resolvía nunca. Después se comprobó con
`grep -c "serviceWorker.register"` que `index.html` en la raíz del repositorio da
**0** y `dist/canon6d_sota_hosted/index.html` da **1**.

**Documentación primaria consultada.** La especificación de Service Workers
define `ServiceWorkerContainer.ready` como una promesa que **sólo se resuelve**
cuando hay un registro activo para ese ámbito; no rechaza si no lo hay. Un
`page.evaluate` que la espera se bloquea de forma indefinida, sin importar el
tiempo de espera de los localizadores de Playwright.

**Qué cambió la hipótesis.** El guion apuntaba por defecto a la raíz del
repositorio, donde nunca ha habido registro de service worker. La ronda anterior
lo ejecutó contra el build hospedado y por eso pasó; el valor por defecto estaba
mal desde el principio y el fallo era silencioso.

**Predicción falsable.** Sirviendo `dist/canon6d_sota_hosted` y apuntando
`FOCALRUTA_QA_URL` ahí, `serviceWorker.ready` resuelve y el guion termina.
**Confirmada:** `passed: true`, service worker con control, nueve laboratorios
visibles sin conexión y nueve ejercicios en el bloque sin JavaScript.

**Corrección permanente.** El valor por defecto pasó a `http://127.0.0.1:8777/`
con un comentario que explica por qué, y `README.md` documenta que ese guion
necesita la raíz hospedada. Un fallo que se manifestaba como cuelgue queda
convertido en una instrucción explícita.

### Cierre de la ronda 7 · desplegado y verificado en vivo

PR #14 fusionado en `main` (`d64dc75`). Workflow **Quality** `33696913241` y
**Deploy FocalRuta to Pages** `33696913261`, ambos en verde.

Verificación contra `https://pillb.github.io/focalruta/`:

- `challenges/arquitectura-en-foco/index.html` y `wiki-tecnicas.html` en vivo son
  **byte a byte idénticos** a los archivos locales generados.
- La página publicada expone los **nueve laboratorios**; la wiki publica nueve
  familias con **nueve diagramas de hash distinto**.
- Los nueve archivos de mapa huérfanos devuelven **404**: dejaron de publicarse.
- `browser_round1_qa.py` apuntando a la URL en vivo: `passed: true`, seis
  viewports, sin errores de consola, sin recursos fallidos, sin desbordamiento.

Estado: `ROUND_7_..._MERGED_AND_LIVE_VERIFIED`.

**Siguiente acción sugerida.** Reconstruir las rutas cuando el router OSM vuelva
a estar disponible, y decidir con datos de uso si alguna de las nueve
alternativas de flujo documentadas merece implementarse.

## Ronda 8 · Rutas reconstruidas con el router en vivo (2026-09-02)

**Autorización.** El usuario aclaró que la regla de detenerse tras el primer
fallo de disponibilidad apunta a APIs comerciales que pueden penalizarnos, no a
un router público, y autorizó **cuatro intentos** para esta reconstrucción.

**Estado del servicio.** Antes de tocar nada se sondearon los dos servicios:
`routing.openstreetmap.de/routed-foot` respondió 200 en 0,63 s y Nominatim 200
en 0,69 s. La reconstrucción terminó **en el primer intento, en 192,6 s**, así
que el presupuesto de cuatro no llegó a usarse.

### Defecto que hacía imposible cumplir la regla de fallo rápido

`get_json` invocaba `curl` **sin ningún tiempo límite**. Una conexión estancada
no fallaba: se colgaba indefinidamente, de modo que la regla de «detenerse tras
el primer fallo confirmado» nunca podía dispararse —no había fallo, había
bloqueo—. Eso explica el `OSM_ROUTER_STALLED` registrado en la ronda anterior.

Corrección: `--connect-timeout 12`, `--max-time 45`, tres reintentos con dos
segundos de espera y un `timeout` de proceso derivado de esos valores.
`tests/architecture/test_route_fetch_resilience.py` levanta un servidor local
que nunca responde y exige que `get_json` **falle dentro de un presupuesto
acotado** en lugar de colgarse; con el código anterior esa prueba no terminaba.

### Resultado de la reconstrucción

El grafo reconstruido es **estructuralmente idéntico** al que estaba verificado:
25 capas, 66 paradas, 10 puntos independientes, 41 tramos, agrupaciones idénticas
y cero capas vacías o malformadas. Datos de carretera nuevos confirman de forma
independiente las rutas que estaban congeladas por el bloqueo.

Durante el proceso el router encontró un enlace peatonal de 854 m que unía los
dos grupos de Miraflores en un solo recorrido de ocho paradas (3,48 km, 46 min).
La regla de publicación de 800 m lo volvió a separar y lo declaró como
transferencia omitida, que es exactamente la forma 5+3 que ya estaba publicada.
La regla funcionó como debía.

### Tres defectos encontrados y corregidos

1. **Auditoría de contención acoplada por posición.** El artefacto
   `geometry_containment_audit.json` no tenía generador en el repositorio y
   estaba indexado por `(distrito, índice)`. Cualquier reconstrucción que
   cambiara el número de capas de un distrito lo invalidaba y **rompía la
   publicación** con un `KeyError`. Ahora existe `scripts/audit_route_geometry.py`,
   que **vuelve a descargar cada polígono administrativo y reevalúa vértice a
   vértice**: 1058 vértices comprobados, 0 fuera de su distrito. Es evidencia
   independiente del constructor, no una copia de su afirmación. Además el paso
   de publicación ya no se cae si la auditoría pertenece a otra corrida.
2. **Reparación de frontera aplicada dos veces.** `split_target` separaba Parque
   Tradiciones de su capa, pero el constructor ya lo publica aislado por
   `FORCE_SINGLETONS`; el resultado era **una capa vacía y un duplicado**. Ahora
   la reparación reconoce que ya está satisfecha. Con el router en vivo la
   subruta reparada desaparece por completo: ya no hace falta el descargo de
   «subruta contenida de una solución exacta anterior» para ese caso.
3. **Mapas huérfanos.** Fusionar o partir capas dejaba archivos publicados que
   ninguna ruta enlazaba. `retire_unreferenced_maps()` los retira en el propio
   paso de publicación y los registra en `retired_map_files`; esta vez retiró 8.

### Evidencia

| Comando | Resultado |
|---|---|
| `build_architecture_routes.py` | rc 0, 192,6 s, 26 capas / 66 paradas, intento 1 de 4 |
| `repair_architecture_route_snapshot.py` | rc 0, 27 capas reparadas |
| `audit_route_geometry.py` | 25 capas, 1058 vértices, 0 fuera |
| `python3 -m pytest -q` | 189 pass |
| `verify_architecture.py` / `verify_release.py` | `passed: true` |
| Ruff C901 pinned 0.12.11 | limpio |
| `browser_round1_qa` / `round5_route` / `round2_learning` | pass, 6 viewports |
| `browser_architecture_release_qa` | pass · SW, offline, sin JS, 9 ejercicios |

### Compromisos

- Los dos pares aprobados de 1500 m siguen siendo una **pantalla en línea recta**,
  no rutas de carretera capturadas; se publican con ese estado explícito.
- La transferencia de 854 m entre los dos grupos de Miraflores queda declarada
  como omitida, no escondida.
- No se volvió a lanzar el constructor una vez obtenido un resultado válido: son
  servicios públicos y no hay motivo para repetir la carga.

### Cierre de la ronda 8 · fusionado y verificado en vivo

PR #15 fusionado en `main` (`c7008e3`); **Quality** y **Deploy to Pages** en verde.

Contra `https://pillb.github.io/focalruta/`:

- La página del reto en vivo es **byte a byte idéntica** a la generada localmente
  y publica los nueve laboratorios.
- **Todos** los `kml`, `geojson` y mapas offline referenciados por las 25 capas
  responden 200.
- Los archivos retirados por `retire_unreferenced_maps()` devuelven **404**: ya
  no se publican tours que no existen.

**Siguiente acción sugerida.** Comprobar en campo el enlace peatonal de 854 m
entre Puente Villena y Larcomar: si resulta caminable con cámara, sube el techo
de transferencia de 800 m con evidencia y Miraflores pasa a ser un recorrido
único de ocho paradas.

## Ronda 9 · Guardianes que diagnostican y evidencia que no caduca en silencio (2026-09-03)

**Objetivo.** Atacar las causas raíz que hicieron caras las dos rondas anteriores,
no sus síntomas: un fallo de paridad que no decía dónde, evidencia que envejecía
sin que nada lo notara, y afirmaciones de estado que ninguna prueba respaldaba.
Requisitos: **E03, G06, L05, L10, M01, M03, M04, M05, N03, N04, O03, Q01, Q03**.

**Método pedido y aplicado.** Prior art → opciones ordenadas → prueba sobre el
artefacto real → comparación medida → implementación → RED/GREEN → iterar.
El análisis completo está en
`research/failure_mode_analysis_2026-09-03.md`.

### Hallazgos que motivaron la ronda

| Hallazgo | Evidencia |
|---|---|
| Diagnóstico imposible por construcción | `check(condition: bool, label)` descarta los operandos antes de ejecutarse; cero usos de `difflib` en todo el repositorio |
| Evidencia de release caducada | Los tres informes que abren la puerta llevaban comprometidos desde **2026-08-09**; el sitio que auditan cambió el **2026-09-02**. Ninguno registraba qué había auditado |
| `BUILD_METRICS.json` no lo leía nadie | Dos sha256 escritos y jamás comparados |
| Estado sin respaldo | `CURRENT_STATE.json` no lo abre ningún script ni test. `66` paradas, `25` capas, `41` tramos y `1058` vértices —escritos por mí en las rondas 7 y 8— no aparecían en ninguna prueba |
| Pruebas tautológicas | `test_round5_routes.py` afirmaba `"MAX_WALKING_LEG_M = 1000" in source`, patrón que `AGENTS.md:43` prohíbe |
| Prosa como contrato | ~60 aserciones de frases literales; seis se rompieron en un solo día de esta sesión al reescribir textos |

### Experimento medido (opciones comparadas)

Sobre la página real —398.880 bytes, línea más larga de **273.747 caracteres**—
renombrando un atributo:

| Opción | Salida | Tiempo | Veredicto |
|---|---|---|---|
| `unified_diff` por líneas | 5 líneas, la mayor de 273.750 caracteres | 0,00 s | inservible |
| Normalizar `><`→`>\n<` y diff | 7 líneas, la mayor de 109 | 0,02 s | legible |
| Primer byte divergente + ventana | offset 12.062 de 398.880 | 0,01 s | exacto |

Se implementaron las dos últimas juntas.

### Entregado

- **`scripts/artifact_diff.py`** y `check_equal()` en ambos guardianes. Un
  carácter cambiado produce ahora `offset 12065 of 398880` con el `<path>` exacto
  a ambos lados; un byte en `plan_a.html`, `offset 314 of 4637462`.
- **`scripts/evidence.py`**: cada informe de QA estampa `audited_at`,
  `audited_commit` y el sha256 de cada archivo inspeccionado. `verify_release.py`
  exige que sigan coincidiendo y **consume** `BUILD_METRICS.json`. Los tres
  informes se regeneraron: 37, 22 y 234 checks, idénticos a los previos —sin
  regresión de comportamiento, sólo procedencia fresca—.
- **`scripts/regenerate_all.py`** + paso de CI `regenerate_all && git diff --exit-code`.
  Cubre curriculum, las cuatro páginas del reto, el índice raíz, el build
  hospedado y el estado. Excluye explícitamente el constructor de rutas.
- **`scripts/build_state_snapshot.py`**: 23 hechos medidos desde los artefactos,
  separados de la narrativa histórica.
- Contratos estructurales en `test_editorial_contracts.py` y sustitución de las
  aserciones que leían el código como texto por ejercicio real de las constantes.
- `competition_rules.json` marcado `CLOSED` con prueba contra la fecha real.

### Trampa encontrada durante la implementación

La primera versión de `build_state_snapshot.py` estampaba `generated_at: now()`,
así que **cada ejecución ensuciaba el árbol** y habría convertido la nueva puerta
de CI en ruido permanente. Es la fuente de no-determinismo que cataloga
reproducible-builds. Se eliminó la marca de tiempo. Comprobado: dos ejecuciones
seguidas dejan el árbol idéntico.

También se detectaron **dos falsos positivos en mis propios contratos nuevos**
antes de tocar el sitio: `TODO` es palabra española corriente («TODO desde
~2,5 m queda nítido»), y el glosario se comprobaba contra la página equivocada
—KML pertenece al reto, no al planificador raíz—. Ninguno era defecto del producto.

### Evidencia

| Comando | Resultado |
|---|---|
| `python3 -m pytest -q` | **265 pass**, 1 skip (antes 189) |
| `verify_architecture.py` / `verify_release.py` | `passed: true`, y **fallan con offset y contexto** al inducir un byte |
| `uvx ruff@0.12.11 … C901` | limpio |
| `regenerate_all.py` + `git diff` | sin cambios |

### Compromisos y deuda registrada

- La puerta global hará fallar cualquier PR que edite HTML generado a mano. Es
  deliberado.
- **La afirmación de la ronda 7 queda acotada:** `optics_physics.py` unifica la
  óptica de Python y de los laboratorios del reto, **no** la del laboratorio
  óptico de la raíz, que reimplementa `atan(sw/2f)` y la CoC por separado en
  `upgrade_optics_accessibility.py:93` y `sota_upgrade.py:131`. Ambas copias son
  correctas hoy y ambas se publican; el riesgo es divergencia futura.
- Fuera de alcance por acuerdo: umbrales de ruta repetidos en cinco archivos,
  `VIEWPORTS` duplicado en cuatro (ya divergente en `browser_release_qa.py`), dos
  implementaciones de haversine, y los colgados restantes
  (`navigator.serviceWorker.ready` sin guarda, sin `set_default_timeout`, sin
  `pytest-timeout`, `research_video_ledger.py:71` sin tiempo límite).

### Cierre de la ronda 9 · fusionado y verificado en vivo

PR #16 fusionado en `main` (`b5221a4`); **Quality** y **Deploy to Pages** en verde.

Contra `https://pillb.github.io/focalruta/`: la página del reto en vivo es **byte
a byte idéntica** a la generada y publica los nueve laboratorios. El bloque
`measured` del estado contiene 23 hechos leídos de los artefactos —entre ellos
`route_stops 66`, `route_layers 25`, `route_legs 41`, `audited_vertices 1058`,
`interactive_labs 9`— y 68 claves de narrativa marcadas como no comprobables.

**Coste introducido, medido.** El workflow Quality pasó de **30 s a 95 s**. La
regeneración se ejecuta dos veces: como paso de CI y otra vez dentro de
`test_regenerating_leaves_the_tree_unchanged`. Es duplicación real; la prueba
tiene valor en local, donde no existe el paso de CI, pero conviene que se salte
sola cuando el paso ya corrió (por ejemplo mirando `GITHUB_ACTIONS`). Queda
anotado como el primer arreglo de la próxima ronda.

**Siguiente acción sugerida.** Esa deduplicación de CI, y después la deuda ya
registrada: la óptica JS duplicada del laboratorio óptico raíz, los umbrales de
ruta repetidos, los `VIEWPORTS` divergentes y los colgados sin guarda.

## Ronda 10 · Verdad única y colgados acotados (2026-09-04)

**Objetivo.** La deuda registrada al cerrar la ronda 9: duplicación de constantes
y operaciones que se cuelgan en vez de fallar. Requisitos: **N01, N02, M01, M04,
M05, K04, O03**.

### Lo que resultó no ser sólo duplicación

Cuatro guiones de navegador llevaban su copia de la matriz N01 y otros dos una
**distinta y más corta**. El problema de fondo no era la repetición: era que
`browser_release_qa.py` y `live_pages_qa.py` comprobaban **tres** viewports —uno
de ellos **1440×1000**, que N01 no nombra— frente a los **seis** que
`REQUIREMENTS_INVENTORY.md:144` marca como MUST. La duplicación escondía un
incumplimiento de contrato.

`scripts/qa_matrix.py` centraliza la matriz y un test la compara contra la línea
N01 del inventario. **Efecto medido: 234 → 246 checks, cero fallos.** Los cuatro
viewports que nadie probaba ya estaban bien; ahora se verifican. La puerta de
release dejó de comparar un total opaco y comprueba **cobertura**: el informe
declara qué viewports recorrió y el verificador exige que sean exactamente los de
N01, nombrando los que falten o sobren.

### Colgados convertidos en fallos

`page.evaluate` no tiene tiempo límite propio
([playwright#13253](https://github.com/microsoft/playwright/issues/13253), abierto)
y `navigator.serviceWorker.ready` **nunca se rechaza** por especificación. Cuatro
`await` podían bloquear una sesión entera: los dos de `serviceWorker.ready`, el
barrido de recursos y el de decodificación de imágenes. `qa_matrix.bounded_async()`
mete la carrera **dentro** del JavaScript, que es el único sitio donde puede
rechazar. Como defensa en profundidad, `harden()` en siete puntos de creación de
página y un límite global en `pytest.ini`.

### Mi propia prueba nueva era un falso verde

El contrato «ningún `await` sin límite» pasaba con 17 verdes mientras dos
colgados seguían ahí: la regex no codiciosa se cerraba en las comillas del propio
JavaScript y truncaba el cuerpo, así que informaba de **cero** casos. Se sustituyó
por análisis con `ast` y una meta-prueba que exige ver ≥15 llamadas y ≥1 con
`await`. Entonces se puso en rojo y encontró los dos reales.

Por la misma razón el guardián de óptica se refactorizó a la función pura
`optics_drift()`, ejercitada en ambas direcciones.

### Corrección a la ronda 9

Afirmé que las dos copias JavaScript de la óptica «se publican». **Es falso.**
Sólo `upgrade_optics_accessibility.py` es la viva; el marcador de
`sota_upgrade.py` (`maxScene=30`) no aparece en `index.html` y nada lo invoca.
Una copia viva más código superado, no dos copias en producción.

### También

Umbral de transferencia y fórmula de distancia importados en vez de retecleados;
la regeneración deja de correr dos veces en CI (se salta bajo `GITHUB_ACTIONS`),
revirtiendo el coste de 30 s → 95 s que yo mismo introduje.

### Evidencia

| Comando | Resultado |
|---|---|
| `python3 -m pytest -q` | **286 pass**, 1 skip (antes 265) |
| `verify_architecture.py` / `verify_release.py` | `passed: true` |
| Ruff C901 pinned 0.12.11 | limpio |
| 5 suites de navegador | pass, 6 viewports, SW/offline/no-JS |
| Matriz de navegador | 234 → **246 checks**, cero fallos |

### Deuda que permanece

- `research_video_ledger.py:71,73` sigue sin tiempo límite; no está en ningún
  ciclo automático.
- `pytest.ini` declara `timeout = 600`, pero sin `pytest-timeout` instalado
  pytest lo ignora con un aviso. CI lo instala; en local no hay red salvo que se
  instale a mano. El archivo lo dice explícitamente.

### Cierre de la ronda 10 · fusionado y verificado en vivo

PR #17 fusionado en `main` (`9d63acd`); **Quality** y **Deploy to Pages** en verde.

Contra `https://pillb.github.io/focalruta/`: la página del reto en vivo es **byte
a byte idéntica** a la generada y publica los nueve laboratorios. La matriz de
navegador registra **246 checks sobre los seis viewports de N01**, y el bloque
`measured` del estado lo refleja: `current_browser_qa_checks = 246`.

**Coste de CI recuperado.** El workflow Quality bajó de **95 s a 69 s**
(02:15:48 → 02:16:57) tras dejar de regenerar dos veces. La ronda 9 lo había
subido de 30 s a 95 s; queda en 69 s, que incluye la puerta de staleness y una
suite un 8 % mayor.

**Siguiente acción sugerida.** La deuda restante es pequeña y está acotada:
`research_video_ledger.py:71,73` sin tiempo límite (fuera de todo ciclo
automático) e instalar `pytest-timeout` en local si se quiere la misma red que
tiene CI. Por lo demás, el enlace peatonal de 854 m entre Puente Villena y
Larcomar sigue siendo la comprobación de campo con más valor pendiente.

## Ronda 11 · Planificador fotográfico listo para producción (2026-10-17)

Pedido de Pablo: tratar la página como prototipo, investigar técnicas y fuentes,
verificar lo implementado y dejarla lista para producción.

### Requisitos y evidencia RED → GREEN

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| R01 | Ranking igual en cualquier Python | `mean([1e16,1,-1e16])` daba 1.0 en 3.13 (suma compensada de `sum`) | `ordered_sum` → 0.0 en 3.11 y 3.13 |
| P01 | Exposición de cada franja dentro de ±1 EV de la luz de escena (tabla ANSI PH2.7) | ninguna franja declaraba escena; 8/14 tests fallaban | 180 franjas re-resueltas, 0 violaciones |
| P02 | ND de catálogo (2, 3, 6, 10 pasos) nombrado en la nota | notas con "sin filtro" y densidades no estándar | ND nombrado; franjas imposibles marcadas "no viable" |
| P03–P04 | Límites de cámara/lente y envolvente de cada técnica | — | dentro de límites; obturadores escritos como en la 6D (`10"`, no `10`) |
| P05 | Afirmaciones ópticas del texto = modelo de lente delgada y sensor 35,8×23,9 | A01 hiperfocal 5,1 m (modelo 3,75); B01 5,0; C03 PDC 6 cm (9); C04 10 cm (27); D03 6 cm (9) | 0 discrepancias; mitos de "compresión" y del zoom burst retirados |
| P06 | `data/plans.json` = `plans_data.to_dict()` | — | igual; incluye `scene_light` y `pose_names` |
| S01–S04 | Panel solar de Lima (NOAA) dentro de 2 min/1° de `astral` 3.2; JS = Python | test de paridad JS falló sin `assets/sun_times.js` | 22 tests de `tests/planner` en verde |
| M04 | `regenerate_all.py` cubre datos, páginas de plan, tarjeta y ZIP | "plans_data.py is not reachable from the regeneration entrypoint" | cubierto; segunda regeneración sin cambios |

### Cambios visibles

- Tarjetas, detalle y modo sesión muestran lente, apertura, obturador e ISO **de la
  franja elegida** (antes mezclaban lente/apertura de cabecera con obturador/ISO de la
  franja), más filtro ND, luz prevista y aviso "no viable".
- 120 diagramas redibujados: chips medidos (antes se salían), PDC infinita dibujada
  (antes se omitía), fondos lejanos acortados y marcados "no a escala", etiquetas y
  poses en español.
- Copia en español sin jerga de desarrollo: fuera el panel "Regression audit",
  "se recuperaron…", créditos de matplotlib, KEY TAKEAWAYS, half-body, etc.
- Fuentes: la página de Canon Europe que atribuye la compresión a la focal se
  sustituyó por Wikipedia "Perspective distortion", la tabla EV y NOAA.
- Plan B: el ocaso va de ≈246° (dic.) a ≈294° (jun.), no 278–288°. Planes A y D ya
  no llaman "luz dorada" a franjas posteriores a la hora dorada.
- Producción: descripción, canonical y Open Graph; iconos maskable separados; `id`,
  `lang`, `dir` en el manifiesto; `robots.txt` y `sitemap.xml`; versión de caché del
  service worker = hash del contenido; 404 autónoma; fuera la insignia "hosted lean".
- ZIP de descarga reconstruido de forma determinista (contenía las páginas de plan
  previas a las correcciones). Páginas de plan en WebP sin pérdida: ~4,5 → ~2,4 MB.

### Comandos y resultados (todos con salida 0)

- `python3 -m pytest -q` → 302 passed, 1 skipped.
- `python3 scripts/verify_architecture.py` → passed. `python3 scripts/verify_release.py` → passed.
- `python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'` → All checks passed.
- `python3 scripts/regenerate_all.py` dos veces → árbol sin cambios.
- `FOCALRUTA_CHROME=/opt/pw-browsers/chromium` + servidor en `dist/canon6d_sota_hosted` (127.0.0.1:8777):
  visual/recursos 37/37, óptica/accesibilidad 22/22, matriz de navegador 246/246,
  y las 5 suites `tests/architecture/browser_*.py` en verde (6 viewports, SW, offline, sin JS).
- Lighthouse 12.8.2 (móvil simulado): portada 92/100/100/100; `plans/plan_a.html` 46/100/100/100 (antes 35 de rendimiento).

### Compromisos explícitos

- `optics_physics.FULL_FRAME_*` sigue en 36×24 mm para el modelo genérico; el campo
  visual de la 6D y los tests usan 35,8×23,9. La diferencia es <0,6 %.
- La escena `oscuridad` (−3 a −1 EV) es una estimación: no tiene fila en la tabla ANSI.
- Tolerancia de ±1 EV: lo que una foto de prueba y el histograma recuperan sin
  cambiar de técnica.
- Tomas de interior con mucha PDC usan ISO hasta 6400 en vez de trípode, para no
  cambiar la técnica.
- Se mantiene `skipWaiting()` en el service worker: sitio estático sin estado de
  formulario; prima recibir la versión nueva.
- Las páginas de plan siguen autocontenidas (2,4 MB) para uso sin conexión; por eso
  su rendimiento en Lighthouse es 46.
- `generate_diagrams.py` queda fuera de `regenerate_all.py` (necesita matplotlib, que
  CI no instala); los PNG se regeneraron a mano en esta ronda.
- La tarjeta de campo integrada conserva rótulos breves en inglés ("Eye-level", "FG/BG");
  se regenera desde `integrate_field_card.py`, fuera del ciclo automático.
- Los scripts de QA de navegador aceptan `FOCALRUTA_CHROME`; en este runner se
  enlazó `chromium_headless_shell-1187` → `-1194` porque Playwright 1.55 espera la 1187.

### Pendiente

- Verificar Pages en vivo tras el despliegue.
- El enlace PMC3482144 citado muestra un captcha; no se pudo comprobar su contenido.

## Ronda 12 · Guía general tras el cierre del concurso (2026-10-17)

Pablo confirmó que el concurso terminó y pidió generalizar el sitio para producción:
es sobre todo para su trabajo de campo y, en segundo lugar, para el público.
Requisitos nuevos en `REQUIREMENTS_INVENTORY.md`, sección T; A01, A03, J01, J05 y la
sección R quedan marcados como sustituidos o archivados.

### Requisitos y evidencia RED → GREEN (`tests/architecture/test_round12_evergreen.py`)

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| T01 | Ninguna página publicada orienta al lector hacia el concurso cerrado | 5 páginas de `dist/` fallaban: «CONCURSO:» ×17, «Las bases», «al concurso» y «Reto» en la guía; «las bases» en la wiki; «reto» en la tarjeta de campo; «Reto» en la portada y la versión autónoma. `learning.json` sin `editorial_note` | 0 coincidencias en las 39 páginas HTML publicadas; las 17 lecciones llevan `editorial_note` («CRITERIO») |
| T02 | El ranking puntúa para el fotógrafo, no para un jurado | el modelo tenía capas `OFFICIAL_PROXY` y `LOW_WEIGHT_ROBUSTNESS_ONLY`; mover `brief` o `judge` de 0 a 10 cambiaba la fila de la matriz | modelo `architecture-ranking-v2.0.0`: sin criterio de jurado ni de encaje con el tema del concurso; pesos = v1.1.0 renormalizados en proporción (`derived_from`); corrida inmutable `2026-10-17-r4-v8` |
| T03 | El build publicado no publica investigación del concurso y el SW sólo precachea lo que existe | `dist/` publicaba `competition_rules.json`, `judges.json` (con perfiles de los jurados) y `organizer_history.json` | ninguno se publica; ningún archivo de `dist/` nombra a los jurados; todas las URL de `CORE` existen en `dist/` |
| T04 | La edición cerrada queda archivada y fechada | no existía `architectural_photography/archive/` | los tres archivos están en `archive/arquitectura-en-foco-2026/` con sus tests originales |

### Cambios visibles

- Lecciones: «CONCURSO:» pasa a «CRITERIO:» con consejos generales. L17 se reescribió
  como «Edición honesta según el uso», con fuentes primarias: World Press Photo («What
  counts as manipulation») y la ayuda de Adobe sobre corrección de perspectiva (deja
  bordes vacíos que obligan a recortar).
- Técnica de edición: «Edición según el uso de la foto» (registro, encargo, concurso o
  portafolio), con las mismas fuentes en lugar de la guía de composición de Nikon.
- Navegación «Bases» → «Encargo»; el decodificador sirve para cualquier encargo o
  convocatoria. Ruta de aprendizaje «… → COMPETIR» → «… → ENTREGAR».
- Portada: «Reto especializado» → «Guía especializada»; meta descripciones sin «reto».
- Ayuda de iPhone: «ELI5» → «PASO A PASO». Lección L13 sin «Optical Lab».

### Efecto del modelo v2 en el ranking (v7 → v8)

- Mismo conjunto de 15 escenas robustas y mismo frente de Pareto (9).
- 51 de 87 rangos robustos se movieron, como máximo 7 puestos.
- Prioridades de campo: el mismo top 5; el 3.º y el 4.º intercambian lugar.

### Verificado

- PMC3482144 (pendiente de la ronda 11) es Wagemans et al. 2012, «A century of
  Gestalt psychology in visual perception: I», Psychological Bulletin (PubMed 22845751).
  Confirmado por búsqueda; europepmc.org está bloqueado por el proxy de este entorno.

### Compromisos explícitos

- Se conserva la ruta `challenges/arquitectura-en-foco/` (OQ-004): GitHub Pages no
  hace redirecciones de servidor y hay enlaces, marcadores y PWA instaladas que la usan.
- Las seis evaluaciones explícitas de 2026 (`new_candidate_assessments.json`) conservan
  su valor de «coherencia temática» con el nombre `architecture_in_use`; no se
  re-evaluaron a mano.
- La clave de investigación `one_frame_contest_test` y el id de técnica
  `contest-safe-editing` siguen igual: son internos y cambiarlos rompería anclas.
- `scripts/architecture_preflight.py` (reglas de archivo de 2026) queda como
  herramienta local archivada; no se publica.
- Las tarjetas del ranking siguen con texto genérico igual para las 87 escenas; los
  datos por escena (`why_survives`, `exact_view`…) están en inglés y no se publicaron.
- Señales retiradas del ranking: `juror_public_work_intersection` (peso 0,005–0,01
  según escenario) y el atributo Master82 `brief` dentro de la antigua
  `theme_coherence_proxy`. Los demás pesos se renormalizaron en proporción.

### Comandos y resultados (todos con salida 0)

- `python3 -m pytest -q` → 350 passed, 1 skipped (incluye 48 de `test_round12_evergreen.py`).
- `python3 scripts/verify_architecture.py` y `python3 scripts/verify_release.py` → passed.
- `python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'` → All checks passed.
- `python3 scripts/regenerate_all.py` → idempotente; `git diff --check` limpio.
- `FOCALRUTA_CHROME=/opt/pw-browsers/chromium` + servidor de `dist/` en 127.0.0.1:8777:
  visual/recursos 37/37, óptica/accesibilidad 22/22, matriz 246/246 y las 5 suites
  `tests/architecture/browser_*.py` en verde (6 viewports, SW, offline, sin JS).

### Pendiente

- Incorporar la revisión del red team (`/mnt/project-files/qa/FINDINGS_PR19.md`, sin
  bloqueos, 5 hallazgos mayores) en PR #19.
- Pasos 3 y 4 del plan (UX de campo y endurecimiento de producción) tras la fusión,
  según el hilo de planificación.

## Ronda 13 · Revisión del red team sobre PR #19 (2026-10-17)

Un hilo de red team revisó PR #19 (`/mnt/project-files/qa/FINDINGS_PR19.md`): sin
bloqueos, 5 hallazgos mayores y una lista de menores. Pablo aprobó el plan de cuatro
pasos («proceed»); esta ronda cierra el paso 1. Requisitos nuevos en
`REQUIREMENTS_INVENTORY.md`, sección U (U01–U08).

### Requisitos y evidencia RED → GREEN

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| U01 | Velocidades como las muestra la 6D (`0"5`, `3"2`, `30"`); hasta 30" nunca «Bulb» | 6 fallos en `tests/planner/test_shot_physics.py` (20 × `3.2"`, Bulb 20/25/30) | 35 pass; un solo parser en `exposure_model.py` |
| U02 | Interiores con ventana de día contra una fila de luz de ventana con fuente | 2 fallos: 14 franjas de C y E puntuadas contra «oficina» (EV 7–8) | fila `ventana` EV 8–10 (500–2500 lx con E = 2,5·2^EV); 14 franjas re-resueltas cerca de EV 9 |
| U03 | La suite mata las 8 mutaciones que sobrevivían | arnés `scratchpad/mut/mutate.py`: la suite de ad248c4 dejó vivas 8/8 | la suite nueva mata 8/8 |
| U04 | Todas las páginas pasan axe; `lang`, un `main`, un `h1`; contraste sobre degradados | axe 4.10.3 en reposo: 70 de 78 pasadas fallaban (sin `main`, 25 mapas sin `lang`, tarjeta de campo sin `h1`, tira de lentes inaccesible por teclado, `aside` dentro de `main`); `test_page_structure.py` 94 fallos; la auditoría ampliada halló RAZONAMIENTO 3,72:1 y el botón Día 4,22:1 | axe 78/78; 118 pass; auditoría de contraste 37/37 con degradados |
| U05 | Páginas de plan alojadas sin imágenes en línea y usables offline tras una visita | `test_hosted_plan_pages.py` 12 fallos (2,4–2,6 MB con data URI); con el servidor apagado la página no estaba en caché (el SW devolvía `index.html` y fallaba `PLANS_DATA`) | 18 pass; 148–154 KB; offline página + 10/10 diagramas por sujeto; Lighthouse móvil 100/100/100/100 (antes 35). `verify_release.py` exigía paridad byte a byte con `plans/` y fallaba en las 6 páginas; ahora compara todo salvo el mapa de diagramas y el script de caché, y que cada `.webp` sea la imagen embebida (dos mutaciones detectadas) |
| U06 | Cada nota nombra la luz con la que se puntúa; alternativas a ≤ ¼ de paso; el panel solar abre en la fecha de Lima | 15 notas «a pleno sol/día» sobre `sol_velado`; fecha: 6 fallos, y el código viejo mostraba 2026-03-28 en Madrid a las 05:30Z del 29 | 3 + 7 pass |
| U07 | Texto de los planes en español; número y unidad separados | 3 fallos (11 términos en inglés, 23 «3s»/«20s:») | pass; 8 diagramas redibujados porque su pie cita el razonamiento |
| U08 | Evidencia y build reproducibles | 4 reportes sin `audited_commit`; 10 JSON de QA en la raíz; CI sin archivo de dependencias; iconos maskable fuera del precache; `sources.json` publicado con 6 fuentes del concurso | commit auditado; sólo los 4 reportes con huellas en la raíz (los 6 de agosto, a `archive/qa-2026-08-09/`); `requirements-dev.txt` y `requirements-qa.txt`; iconos precacheados; fuentes del concurso archivadas |

### Lo que el red team midió y lo que resultó ser

- El «4,29:1» de las etiquetas verdes «HACER» se midió a mitad del fundido de entrada:
  axe mezcla el texto con la opacidad actual de la tarjeta. En reposo pasan con más de
  5:1. Buscar ese fallo destapó dos huecos reales: axe en reposo fallaba por
  estructura y la auditoría propia ignoraba el texto sobre degradados.
- La afirmación del PR «8 de 14 tests nuevos fallaban antes» era inexacta: con los
  datos de `main` fallan 10, casi todos estructurales (campos ausentes); sólo el de
  la hiperfocal de A01 es un error físico real. Se corrige en la descripción del PR.

### Compromisos explícitos

- La fila `ventana` (EV 8–10) es una estimación: la tabla ANSI no tiene fila para luz
  de ventana. Sale de 500–2500 lx junto a la ventana con E = 2,5·2^EV (C = 250).
- `oscuridad` (−3 a −1): ANSI da −3 a −2 bajo luna llena alta; el paso extra por el
  resplandor urbano de Lima es un supuesto conservador sin medir. Con ese tope, el
  light painting de A08–D08 de noche cumple el margen de 3 pasos por 0,00–0,02.
- Los fundidos de entrada siguen: durante 0,5 s el texto pasa por contrastes bajos.
  WCAG juzga el contenido presentado y con movimiento reducido no hay fundido.
- La caché offline de un plan alojado se llena al cargar la página (≈ 2 MB, igual
  que antes pero después del primer pintado); se omite si el lector pidió ahorrar datos.
- La tarjeta de campo integrada y algunos textos de la portada conservan etiquetas en
  inglés («Field Card», «Eye-level», «preflight», «shutter»): el paso 3 del plan la
  rehace entera en español. Lighthouse marca su texto como pequeño (< 12 px).
- axe-core no se versiona en el repo: `FOCALRUTA_AXE` apunta a `axe.min.js` 4.10.3 y
  el script se detiene si falta.
- Chromium no aplica la emulación offline a las peticiones del service worker; la
  prueba offline apaga el servidor en vez de emularla.

### Cierre (comandos, código de salida, resumen)

| Comando | Salida | Resumen |
|---|---|---|
| `python3 -m pytest -q` | 0 | 525 pass, 1 skip (`wiki-tecnicas.html` no usa Schlick) |
| `python3 scripts/verify_architecture.py` | 0 | `checks_failed: []` |
| `python3 scripts/verify_release.py` | 0 | `checks_failed: []` |
| `ruff check scripts tests --select C901` (máx. 10) | 0 | sin hallazgos |
| `python3 scripts/regenerate_all.py && git diff --exit-code` | 0 | 10 pasos, sin cambios |
| `git diff --cached --check` | 0 | sin espacios sobrantes |
| QA de navegador (`--with-browser-qa`, Chromium + axe 4.10.3) | 0 | visual 37/37, óptica 22/22, release 249/249, axe 78/78, cinco suites de arquitectura en verde |
| Lighthouse móvil (rendimiento) | — | portada 92, planes 100, tarjeta de campo 100, guía 91; accesibilidad 100 en todas |

Verificación independiente: el hilo de red team recibe el nuevo commit para su
segunda pasada; su veredicto se registra en la ronda siguiente.

### Corrección posterior: la prueba offline de U05 no esperaba

Al escribir las pruebas del paso 3 apareció que `page.wait_for_function` de
Playwright 1.55 da por cumplido un predicado que devuelve una promesa sin
esperarla (reproducido: `async()=>false` vuelve en 0,01 s). La espera de U05
(«página y 20 diagramas en caché») no esperaba, y el servidor de prueba no
prohibía la caché HTTP, así que Chromium podía responder «offline» desde su
caché de disco. `browser_release_qa.py` ahora sondea con `page.evaluate` y
sirve con `Cache-Control: no-store`. Con el arnés corregido, U05 sigue en
verde en este commit y en c4f96bf: página y 10/10 diagramas por sujeto.

### Segunda pasada del red team y evidencia limpia

El red team dio PASS a c4f96bf y b86aa96 (12/12 mutaciones propias muertas, axe en
reposo sin violaciones, offline con 0 imágenes rotas) con una nota: los reportes
decían `eec010a…+dirty`. La causa era mecánica: las suites corren una tras otra y
cada una escribe su reporte en la raíz, así que desde la segunda el árbol parecía
sucio. `evidence.current_commit` ya no cuenta los `*_QA.json` de la raíz y una prueba
exige que cada reporte nombre un commit limpio (RED: 3 de 4 reportes).

Al regenerar apareció otro fallo: los bucles de `browser_release_qa.py` reutilizaban
el nombre `time`, así que `time.monotonic()` fallaba al llegar a la comprobación
offline de U05 y el script moría sin escribir el reporte. La verificación de U05
citada arriba se hizo con un script aparte; la del script completo no había corrido.
Corregido en 28ef2aa. Evidencia sobre 28ef2aa sin cambios pendientes: visual 37/37,
óptica 22/22, release 249/249 (con U05), axe 78/78; pytest 530 pass, 1 skip;
`verify_architecture` y `verify_release` sin fallos; regeneración sin cambios.

## Ronda 14 · Primero el campo, después el público (2026-10-17)

Paso 3 del plan que Pablo aprobó («proceed»): uso en el campo primero (sin conexión,
con una mano, tarjeta de campo enteramente en español, planes más útiles) y después
el pulido público (navegación, equipo configurable con el kit de la 6D por defecto).
El coordinador confirmó que los pasos 3 y 4 no necesitan otra consulta y que van en
PR nuevos; fusionar sigue necesitando la palabra de Pablo. Requisitos nuevos en
`REQUIREMENTS_INVENTORY.md`, sección V (V01–V15).

### Requisitos y evidencia RED → GREEN

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V01–V06 | Tarjeta en español, ajustes exactos por franja, nada bajo 12 px, lista de equipaje por plan, la portada embebe la tarjeta generada, franjas según la hora de Lima | `tests/test_field_card.py`: 11 de 11 fallaban (la tarjeta vieja daba diez valores genéricos por técnica, en 8–11 px y medio en inglés) | 11 pass; tarjeta generada desde `data/plans.json` dentro de `regenerate_all.py` |
| V02–V09 (navegador) | Cambiar plan y luz, hora de Lima, sin JavaScript, imprimir, dentro del diálogo, axe, sin conexión | `field_card_qa.py` sobre la tarjeta vieja: 6 de 12 pasos no podían ni empezar (no había controles que pulsar) | FIELD_CARD_QA 48/48 (38 de la tarjeta y 10 de «tu equipo») |
| V05 (cableado) | La integración sólo reemplaza la tarjeta; cada `getElementById` de cada página apunta a un elemento que existe; cada función llamada desde el marcado se define una vez | la tarjeta nueva borró el diálogo «Modo sesión», que estaba dentro del bloque de la tarjeta: el botón no hacía nada y ninguna prueba lo vio. `test_page_wiring.py`: 3 fallos (dos portadas sin `session-run-dialog` ni sus 6 elementos; la integración tragaba un diálogo ajeno sin avisar). El red team halló `openFieldCard`/`closeFieldCard` definidas dos veces (en b86aa96: 2 y 2) | diálogo restaurado fuera del bloque; la integración se niega a reemplazar un bloque con otro marcado; una sola definición del diálogo de la tarjeta (inerte el resto, foco atrapado, Escape sólo si está abierta); 37 pass. `reading_floor.audit_home` informa de un diálogo que no se abre en vez de medir la página de detrás |
| V07 | Planes y diagramas funcionan sin servidor tras una visita y un toque, y sobreviven a un despliegue | el service worker viejo borraba toda caché que no fuera de su versión (`VERSION` = hash del contenido): cada despliegue vaciaba los planes visitados | paquete `focalruta-pack` explícito, fuera del versionado; la QA simula un despliegue y apaga el servidor |
| V10–V12 | Portada y páginas de plan: nada bajo 12 px, controles de 44 px, interfaz en español | estática: 14 de 16 fallos; navegador a 390 px: 690 textos bajo 12 px, 353 controles bajo 44 px y 13 palabras en inglés en los estados recorridos | 0 / 0 / 0 en las seis vistas obligatorias y en las seis páginas de plan, en todos los estados (`reading_floor.py`) |
| V13 | Ajuste equivalente para la cámara y los lentes del lector | sin la adaptación, el lector calculaba a mano factor de recorte, apertura equivalente y exposición. Mutaciones de `gear.js` que la suite mata: CoC sin escalar (4 fallos), hiperfocal sin escalar con la distancia (3), apertura copiada del plan (5), focal sin multiplicar por el factor (9), ND ignorado en el ISO (lo detecta la rejilla de 14 400 ajustes) | 31 pass: mismo encuadre (±2 %), misma PDC proporcional (hiperfocal a ⅙ de paso), misma exposición (⅓ de paso salvo luz que falte, y entonces lo dice) |
| V13 (notas) | Las notas no se contradicen y el trípode sigue la regla recíproca sobre la focal equivalente | con el `gear.js` anterior, 4 de 5 equipos reales fallaban: «tu lente no abre tanto» junto a «cierro el diafragma» (A05, B06…), y «usa trípode» a 1/100 con 31 mm en Micro 4/3 (equivalente 64 mm) | la nota del límite del lente se omite si al final se cierra el diafragma; trípode sólo por debajo de 1/(focal equivalente); «1 paso»; notas impersonales |
| V14 | El kit de la 6D es el valor por defecto y no cambia nada | — | ninguna línea extra; 180 franjas idénticas |
| V15 | Selector en la portada; el mismo `gear.js` en portada, páginas de plan, tarjeta y laboratorio óptico; el equipo guardado no puede inyectar marcado | sin limpiar, un lente guardado con `<img onerror>` llegaba tal cual a la página | 8 páginas con el mismo script; nombre limpio y lentes inválidos descartados; paso `your_gear` del navegador (9 comprobaciones, con el A01 calculado a mano: «22 mm (zoom 18–55) · f/7.1 · 1/125 · ISO 160») |

### Cambios visibles

- Tarjeta de campo nueva: plan y luz con un pulgar, barra de secciones abajo, «siguiente
  toma pendiente», ventanas horarias del día elegido, lista de equipaje por plan,
  pantalla de noche roja, pantalla siempre encendida, progreso guardado, imprime limpia.
  Funciona sin JavaScript (radios y `:has()`).
- Portada y planes: 12 px mínimo (las etiquetas del laboratorio óptico se escalan con
  el SVG y, por debajo de 520 px, pasan a la leyenda), botones y enlaces de 44 px,
  «Casa / Laboratorio», «tarjeta de campo», «campo visual», «enfoque mínimo», «efecto
  zoom», «pintura con luz». 120 diagramas redibujados («campo visual»).
- «Tu equipo»: cámara (seis formatos), ISO máximo aceptado y lentes (habituales o
  propios). Cada toma, plan y la tarjeta muestran «Con tu equipo: …» con lo que
  cambia y por qué; el laboratorio óptico usa el sensor y el círculo de confusión del
  lector. Se guarda en el dispositivo.

### Compromisos explícitos

- La equivalencia usa lente delgada y conserva la PDC en proporción a la distancia:
  si el lente obliga a acercarse o alejarse, cambia la perspectiva (lo dice la nota).
  El círculo de confusión es 0,03 mm × ancho del sensor / 35,8.
- Límites genéricos de cuerpo: 1/4000 s, f/22, ISO entre 100 y el máximo que el lector
  acepta. Una cámara con 1/8000 o ISO 50 rinde algo más de lo que se le promete.
- Con poca luz se quita antes el ND, luego se alarga la exposición (técnicas de
  apertura) o se abre el diafragma (técnicas de movimiento); si aun así falta luz, la
  línea dice cuántos pasos.
- La lista de equipaje sigue nombrando las roscas de filtro del kit de la 6D.
- El paquete sin conexión es explícito (≈ 11 MB: seis planes y sus 120 diagramas) y no
  se precachea al instalar: se baja con un toque en la tarjeta. Se copia de un
  despliegue al siguiente.
- La tarjeta de campo pesa 280 KB / 42 KB con gzip (antes 227 KB / 32 KB): la tabla de ajustes por
  franja para «tu equipo» y `gear.js` van dentro para que funcione sin conexión.
- Los diagramas PNG siguen con texto pequeño cuando el teléfono los reduce; se pueden
  ampliar en el visor.

### Cierre (comandos, código de salida, resumen)

| Comando | Salida | Resumen |
|---|---|---|
| `python3 -m pytest -q` | 0 | 628 pass, 1 skip |
| `python3 scripts/verify_architecture.py` | 0 | `checks_failed: []` |
| `python3 scripts/verify_release.py` | 0 | `checks_failed: []`; mínimos subidos a 315 (release) y 48 (tarjeta) |
| `ruff check scripts tests --select C901` (máx. 10) | 0 | sin hallazgos |
| `python3 scripts/regenerate_all.py && git diff --exit-code` | 0 | sin cambios |
| QA de navegador (`--with-browser-qa`, Chromium + axe 4.10.3) sobre e25098f limpio (rama rehecha sobre `main` tras fusionar PR #19) | 0 | visual 37/37, óptica 22/22, release 315/315, axe 78/78, tarjeta 48/48 |
| Cinco suites `tests/architecture/browser_*.py` | 0 | en verde sobre c60a6e3, una tras otra y sin regenerar en paralelo (antes, `whole_site_integration` falló una vez porque regeneré `dist/` mientras corría) |

Verificación independiente: el red team recibe el PR del paso 3 para revisarlo.

### Errores propios encontrados en esta ronda

- La tarjeta nueva borró «Modo sesión» (ver V05). Lo encontró la QA de release, no
  una prueba estática; ahora hay una.
- `browser_release_qa.py` no llegaba a su comprobación offline desde b86aa96 (`time`
  sombreado por un bucle). Corregido en PR #19 (28ef2aa).
- Los reportes decían `+dirty` por escribirse uno tras otro; `evidence.QA_REPORTS`
  exime sólo a los cinco reportes por nombre (pedido del red team).

## Ronda 15 · Lo que el red team encontró en PR #20 (2026-10-17)

El red team revisó PR #20 en eb3c101 y dijo «not yet»: siete hallazgos mayores (tres de
«tu equipo», la caché del service worker que halló la comprobación del sitio en vivo, el
HTML nuevo con CSS viejo tras un despliegue, la pérdida de las páginas sin conexión al
actualizar desde 9cd3044, el desborde a 320 px y pruebas que leían las páginas fuente en
vez de las que se publican) y una lista de menores, más L1–L5 del sitio en vivo
(`/mnt/project-files/qa/FINDINGS_PR20.md`, `LIVE_CHECK_PR19.md`). Esta ronda los corrige
en el mismo PR. Requisitos nuevos en `REQUIREMENTS_INVENTORY.md`: V16–V19; N01 añade
320×640.

### Requisitos y evidencia RED → GREEN

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V16 | Una página recibe archivos de esta build o de la red, nunca la copia de otra: cada copia se comprueba contra el resumen SHA-256 de la build; la portada nombra su hoja y sus datos por revisión; todo lo que se guarda, el manifest incluido, se sirve sin conexión | `tests/test_service_worker.py` con la plantilla de eb3c101 (`FOCALRUTA_SW_TEMPLATE`): 10 de 11 fallan (index, hosted.css y plans_embedded.js guardados desde la caché HTTP; la hoja de otra build servida; el manifest no se sirve sin conexión). Ensayo de despliegue en Chromium (`field_card_qa.py`, servidor tipo Pages con ETag y `max-age=600`): 7 de 12 fallan, entre ellos «primera visita tras un despliegue con el worker en vivo: hosted.css y plans_embedded.js de otra build» (M4) | 12/12 en pytest y 12/12 en el navegador; plantilla nueva `assets/sw.template.js` rellenada por `scripts/service_worker.py` (FILES = ruta → revisión, CORE) |
| V17 | Al actualizar desde el worker de 9cd3044 o uno posterior se conserva todo lo que el lector tenía sin conexión y sólo se baja lo que cambió; lo guardado para el campo se pone al día al instalar; la tarjeta dice si algo es de una versión anterior o falta; las cachés de los otros sitios de pillb.github.io no se tocan | RED en el mismo log: «sin conexión tras actualizar: el plan C, abierto antes, sigue con sus 10 diagramas» daba 0 diagramas y la portada (M5); «un despliegue pone al día el plan guardado» y «la tarjeta avisa de un archivo de una versión anterior» fallaban (decía «Guardados … el 2026-10-17») | adopta las cachés `focalruta-<hash>-*` y `canon6d-sota-v*` al instalar y borra sólo esas al activar; textos «Falta 1 archivo / Faltan N archivos…» y «Tu copia sin conexión es de una versión anterior…» |
| V13 (mayores 1–3) | Zoom fuera de rango, PDC perdida con lentes largos, pruebas que confiaban en la bandera de la propia función | 100-400 en el zoom de A10: «100–80 mm» sin nota; A01 en 100-400 a f/22 sin aviso; `test_gear.py` restaba `flags.short` y sobrevivían `APERTURE_LED = []`, sin alargar la obturación y umbral de 1 paso | el zoom que no llega da la razón «añade uno que cubra ese recorrido»; «nítido sólo hasta 44,2 m»; exposición esperada desde la ecuación EV; las cinco mutaciones fallan la suite; lentes hasta f/22 (`test_v13_the_slowest_lens…[22,25,32]`: antes `f/undefined`) |
| V18 | Desde 320 px nada se corta: nada pasa del borde fuera de una franja que se desplaza, ninguna etiqueta se recorta ni se sale de su control, ningún control queda encima de otro, en todos los estados | `reading_floor.CUT_OFF` sobre la build de 071e41a a 320×640: portada 327 hallazgos (formulario de equipo 28 px fuera de pantalla, «Quitar» cortado; enlaces del encabezado encogidos a 44 px con la etiqueta saliéndose), plan F 12 («🖨 Imprimir» fuera de pantalla). Mutantes de la portada corregida: sin `flex:0 0 auto` 80, sin `min-inline-size:0` 231 | 0 en ambas portadas, la tarjeta y los seis planes, en todos los estados, a 320, 390, 844 y 1440 |
| V18 (M7) | Las pruebas leen lo que se publica en `dist/` | mutantes en dist (palabra inglesa en index, `font-size:9px` en hosted.css, obturación errónea en field_card.html): las pruebas viejas pasan los tres | las nuevas fallan con cada uno |
| V19 | Los diálogos de sesión, tarjeta y toma, abiertos con su botón y cerrados con Escape, toman el foco, lo devuelven a ese botón y no dejan nada inerte | mutantes de la portada (sin devolver el foco, sin quitar `inert`, sesión con `show()` en vez de `showModal()`): las comprobaciones anteriores pasan los tres | la nueva falla con cada uno; 24/24 en ambas portadas a 390 y 1440 |
| L4, L5 | Fuentes vivas | el PDF de la UNMSM para la dirección del Instituto Raúl Porras Barrenechea da 404 sin copia en Wayback; `https://www.basprincen.com/` corta el TLS | Wikipedia (en) da la misma dirección (Calle Narciso de la Colina 398, Miraflores); basprincen por http |

Registros en el scratchpad de la sesión: `red_v16_v17_sw.log`, `red_v16_v17_browser.log`,
`red_gear_slow_lens.log`, `red_m7_mutants_{old,new}_tests.log`, `red_v18_cutoff.log`,
`green_v18_cutoff.log`, `red_v19_focus.log`, `green_v19_focus.log`.

### Menores atendidos

- ISO guardado bajo 100 («ISO undefined») o `1e309` (selector vacío): vuelve como el valor
  del selector más cercano. `lineFor` lee el equipo guardado una vez por cambio.
- Zoom cuyo extremo largo no llega: termina más cerca y lo dice (24-70: 35–70 mm, 7,0 m).
- «Faltan 1 archivos» → «Falta 1 archivo».
- Encabezado a 320 px: las acciones se desplazan con una pista de que hay más; en móvil se
  quedan las esenciales; «Guía» ya no se corta.
- L2: la tarjeta en `dist/` se mide también (V03 con las dos copias).

### Compromisos explícitos

- Un lector que aún tiene el worker de 9cd3044 y vuelve dentro de los 10 minutos de caché
  HTTP de Pages puede recibir todavía el HTML anterior desde esa caché y, si su worker no
  guardó la hoja anterior, verlo con la nueva. Con el worker nuevo no ocurre (V16), y la
  ventana se cierra sola.
- `sw.js` pesa 22 KB (6,7 KB con gzip) porque lleva la revisión de cada archivo.
- Si un nodo de la CDN sirve un archivo de CORE con un resumen viejo, la instalación falla
  y se reintenta en la visita siguiente; mientras, sigue el worker anterior.
- El `sw.js` de la raíz (canon6d-master-v2, muy antiguo) no se toca.
- Equipo: la nota de f/22 es aproximada; la regla del trípode ignora la estabilización; los
  solapes de zoom pequeños no llevan nota; se conservan el paso del ND (ningún hueco real lo
  alcanza) y el redondeo a infinito (un 38 mm propio lo necesita). Sin hacer: la etiqueta
  «factor 2» de Micro 4/3 (el cálculo usa 2,07), f/0.95 limitado a f/1, 1/4000 para todo
  cuerpo, límites de nombre y número de lentes, evento `storage` entre pestañas.
- V18 compara solapes sólo dentro de una misma capa (el encabezado fijo sobre el contenido
  que pasa por debajo no cuenta) y mide etiquetas sólo en controles con ancho propio.
- L4: la dirección viene ahora de Wikipedia y la coordenada de Commons, ambas de Wikimedia,
  así que ya no son editores independientes. UNMSM, BNP, Andina y El Peruano no publican la
  dirección. Se mantiene el estado y la confianza.
- L5: basprincen por http, sin TLS. El red team comprobó en vivo que responde 200; desde este
  contenedor la red externa está bloqueada (proxy 403) y no se pudo repetir.
- «Siempre decir Listo» en la tarjeta lo detecta la QA del navegador (`field_card_qa.py`), no
  pytest; pytest cubre el worker (V16, V17).

### Cierre (comandos, código de salida, resumen)

| Comando | Salida | Resumen |
|---|---|---|
| `python3 -m pytest -q` | 0 | 677 pass, 1 skip |
| `python3 scripts/verify_architecture.py` | 0 | `checks_failed: []` (incluye el escaneo de privacidad) |
| `python3 scripts/verify_release.py` | 0 | `checks_failed: []`; mínimos subidos a 360 (release) y 56 (tarjeta); cubre la matriz N01 con 320×640 |
| `ruff check scripts tests --select C901` (máx. 10) | 0 | sin hallazgos |
| `python3 scripts/regenerate_all.py && git diff --exit-code` | 0 | sin cambios salvo `CURRENT_STATE.json`, que mide el reporte nuevo (315 → 360) y va en el mismo commit |
| QA de navegador (`--with-browser-qa`, Chromium + axe 4.10.3) sobre 7f0fe75 limpio | 0 | visual 37/37, óptica 22/22, release 360/360, axe 78/78, tarjeta 56/56 |
| Cinco suites `tests/architecture/browser_*.py`, una tras otra | 0 | en verde en las siete vistas, 320×640 incluida |

Verificación independiente: el red team recibe el PR otra vez para revisarlo. Antes de
fusionar hace falta la palabra de Pablo.

### Referencia de experto por decisión

- V16–V17: el precacheo con revisión por archivo de Workbox (`precacheAndRoute` con
  `{url, revision}`) y el ciclo de vida del service worker de la especificación W3C; un
  experto rechazaría servir un CSS de otra build o vaciar lo guardado al actualizar, que es
  lo que hacía eb3c101.
- V18: WCAG 2.2, criterio 1.4.10 Reflow (contenido usable a 320 px CSS sin desplazamiento en
  dos dimensiones). `overflow-x:hidden` en `body` ocultaba el fallo en vez de evitarlo.
- V19: patrón de diálogo modal de WAI-ARIA APG (el foco entra al abrir y vuelve al control
  que lo abrió al cerrar) y el `inert` de HTML.
- L4–L5: una fuente de dirección que no responde no corrobora nada; se cambia por una que
  responde y se declara la pérdida de independencia.

### Errores propios encontrados en esta ronda

- Las pruebas de Node quedaban colgadas 90 s: el temporizador de `Promise.race` seguía vivo.
  Ahora se cancela.
- El servidor de pruebas mandaba `Last-Modified` y respondía 304 con el cuerpo viejo tras un
  despliegue; ahora usa ETag de contenido, como Pages.
- Las pruebas de arquitectura leían CORE de la plantilla, que ahora tiene `__CORE__`; leen el
  `sw.js` publicado.
- La primera versión de V18 no vio el defecto del encabezado (etiquetas que se salen con
  `overflow` visible); lo encontró un mutante y la comprobación se amplió.
- La espera de U05 en `browser_release_qa.py` buscaba claves que terminaran en `.webp` y la
  URL exacta de la página; con las claves por revisión (`?__rev=`) nunca se cumplía y la QA
  completa cayó. Ahora compara rutas; la recarga sin conexión y los diagramas decodificados
  que comprueba después no cambian. Lo encontró la corrida completa, no las sondas parciales.

### Segunda pasada del red team (287f197)

El red team confirmó corregidos los siete mayores anteriores, L1 y L3, reprodujo todas las
puertas y pidió cuatro cosas nuevas (`FINDINGS_PR20.md`, «Second pass at 287f197»).

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V18 (N1) | Nada se corta con el equipo propio del lector, con nombres de lente tan largos como los reales | con un 18–55 de kit y un 70–300 guardados, el `<select>` del laboratorio óptico medía lo que su opción más larga y empujaba el laboratorio fuera de la pantalla: 1451 hallazgos a 320 px y 1336 a 375 px en cada portada; «Quitar» se salía de su botón | 0 en ambas portadas a 320 y 375 px, en la tarjeta y en los seis planes (también con un nombre de 72 caracteres sin espacios); comprobación nueva en `browser_release_qa.py` |
| V16 (N2) | Una página abierta dentro de los 10 minutos de caché HTTP es de esta build | `test_v16_a_page_opened_within_the_http_cache_window_is_this_builds` fallaba (la raíz devolvía la portada anterior); en Chromium, el ensayo sin borrar la caché HTTP fallaba en la portada (`index.html` de la build anterior) | `navigate()` y los archivos de esta build se revalidan (`cache:'no-cache'`); pasa en Node y en Chromium. `install_behind_http_cache` ya no borra la caché HTTP antes de comprobar |
| V16 (N2, ?v) | Una página de otra build recibe la hoja que nombra | el mutante «`asset()` ignora `?v`» sobrevivía a toda la suite | `test_v16_a_page_from_another_build_gets_the_stylesheet_it_names` lo mata |
| V16 (N3) | Un 404 o 5xx no reemplaza la copia guardada | la página y el diagrama guardados devolvían 404 | devuelven la copia guardada |
| V13 (N4) | La luz que falta se dice desde ⅓ de paso, el paso del dial | con kits reales sobre la rejilla, «Faltan 0,3 pasos» a +0,28 EV y «0,2» a 0,17 EV | `test_v13_a_shortfall_is_said_only_from_a_third_of_a_stop` pasa |

Registros: `red_n1_long_gear.log`, `red_n2_n3_sw.log`, `red_green_n2_browser.log`,
`red_n4_gear.log`, `green_n2_n3_n4.log`.

También: la lista de palabras inglesas suma settings, back, download, close, next,
previous, print, share y save (un «← Back» en un plan publicado ya falla V12); ninguna
página la incumple. En Chromium, una página que el worker nunca guardó, abierta con red,
llega de la red (el `fetch(r,{cache:'no-cache'})` sobre una petición de navegación no
lanza error).

Compromisos de esta pasada:

- Revalidar páginas y archivos de esta build cuesta una petición condicional (304) cuando
  el worker no tiene la copia; con copia, no hay red.
- Una instalación fallida deja en las cachés compartidas los archivos que sí llegaron;
  son de esta build y verificados, la siguiente instalación los reutiliza y el siguiente
  `prune` borra los que sobren.
- Un faltante de luz menor que ⅓ de paso ya no se menciona: queda dentro de la tolerancia
  que el planificador declara.

Cierre de la segunda pasada:

| Comando | Salida | Resumen |
|---|---|---|
| `python3 -m pytest -q` | 0 | 681 pass, 1 skip |
| `python3 scripts/verify_architecture.py` | 0 | `checks_failed: []` |
| `python3 scripts/verify_release.py` | 0 | `checks_failed: []`; mínimo de release subido a 371 |
| `ruff check scripts tests --select C901` (máx. 10) | 0 | sin hallazgos |
| `python3 scripts/regenerate_all.py && git diff --exit-code` | 0 | sólo `CURRENT_STATE.json` (360 → 371), en el mismo commit |
| QA de navegador (`--with-browser-qa`) sobre 13253a4 limpio | 0 | visual 37/37, óptica 22/22, release 371/371, axe 78/78, tarjeta 56/56 |
| Cinco suites `tests/architecture/browser_*.py`, una tras otra | 0 | en verde en las siete vistas |

Verificación independiente: vuelve al red team. Fusionar sigue necesitando la palabra de Pablo.

## Ronda 16 · Listo para producción (2026-10-17/18)

Paso 4 del plan que Pablo aprobó («proceed»): una puerta de release en cada PR,
presupuestos de velocidad que incluyen las páginas de plan, comprobaciones del sitio
publicado y un registro de errores que respeta la privacidad. Va en un PR propio,
sobre el paso 3 (PR #20) ya fusionado; fusionar sigue necesitando la palabra de Pablo.
Requisitos nuevos en `REQUIREMENTS_INVENTORY.md`: sección X (X01–X04; la letra W ya
nombra fuentes de Bonilla), y V20–V21 en la sección V, que salieron de la última pasada
del red team y de la comprobación del sitio publicado.

### Requisitos y evidencia RED → GREEN

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X01 | Cada suite de navegador corre en CI en cada PR, en Linux, con herramientas fijadas; ninguna supone el Mac del dueño | en Linux sin `FOCALRUTA_CHROME`, 5 de 6 suites morían al lanzar el navegador («executable doesn't exist at /Applications/Google Chrome.app…») y axe pedía una ruta a mano; CI no corría ninguna: aprobaba con reportes de otra ejecución. `test_ci_contract.py`: 4 de 4 fallaban | `qa_matrix.browser_options()` y `axe_source()`; Playwright 1.55.0 en `requirements-qa.txt`, axe-core 4.10.3 y Lighthouse 13.5.0 en `package-lock.json`; `quality.yml` corre las seis suites en paralelo y las cinco de arquitectura; 4 pass |
| X02 | Presupuestos de velocidad por tipo de página, servidas como las sirve Pages | no había presupuesto. Cuatro copias estropeadas de la portada los rompen: un rastreador de otro origen («no request to another origin»), 300 KB más (transferencia 419 KB > 180; LCP 3.0 s; puntuación 0.89), un script que bloquea 0.9 s (TBT 3620 ms; 0.70) y un salto de diseño (CLS 0.68; 0.77). En las pruebas unitarias, cinco mutaciones caen (`<` en vez de `≤`, juzgar la peor corrida, ignorar otros orígenes, quitar la 404, ignorar los bytes) | 14 páginas × 8 = 112 comprobaciones en verde: todas puntúan 100; portada LCP 1.2 s y 127 KB; planes 0.9 s y 211–230 KB; tarjeta 1.1 s y 47 KB |
| X03 | Tras cada despliegue y cada mañana, CI espera a que el sitio sirva ese commit y lo comprueba entero | `live_pages_qa.py` sólo corría en el Mac (Chrome fijo), nunca en CI, y desde 2140c41 tenía un error de sintaxis en la comprobación de recursos que lo detenía antes de terminar; además buscaba «FREEZE» en subtítulos que el paso 3 pasó al español. Contra un servidor con la build anterior, la espera falla: «does not serve this commit's build» | `live-check.yml` (después de `deploy` en `pages.yml`, a diario 06:17 en Lima, y a mano); espera hasta 15 min por el CDN; ensayo local bajo `/focalruta/`: 88/88, sin peticiones a otros orígenes; presupuestos sobre la URL publicada |
| X04 | Registro de errores sólo en el dispositivo, limpio, sin forma de enviar nada | no existía: un fallo en el teléfono de un lector no dejaba rastro. Seis mutaciones de `diagnostics.js` caen: guardar la consulta, no agrupar repetidos, no limitar a 20, guardar el navegador, enviar a un servidor, dejar escapar un error del almacenamiento | `assets/diagnostics.js` es el primer script de las 19 páginas con script; panel «Registro de errores de este dispositivo» al pie de la portada (copiar, aviso prellenado en GitHub que envía el lector, borrar con dos toques); 9 pruebas en Node y 6 en navegador |

### Al juntarlo con el paso 3

El paso 4 se escribió sobre eb3c101 y la ronda 15 cambió después el worker, las pruebas
de despliegue y la QA del navegador. Al fusionarlos:

- Las suites suman lo de ambos: `browser_release_qa.py` lleva el registro de errores
  (X04) y los diálogos y el equipo largo (V18, V19); `field_card_qa.py` encuentra Chromium
  y axe-core solo (X01) y conserva los ensayos de despliegue (V16, V17).
- Había dos servidores «como Pages»: el del ensayo de despliegue de la ronda 15 (ETag de
  contenido, sin gzip) y el de los presupuestos de velocidad (gzip, con el
  `Last-Modified` de Python, que tras copiar una build con sus fechas responde 304 con el
  cuerpo viejo). Ahora hay uno: `static_server.PagesHandler` comprime, manda ETag de
  contenido y no `Last-Modified`, y sirve la build que un despliegue puso;
  `deploy_rehearsal.Pages` es ese mismo servidor bajo `/focalruta/`.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X02 (V16, V17) | Los ensayos de despliegue y la medición de velocidad ven el mismo Pages: gzip, `max-age=600` y un validador que sólo responde 304 mientras el archivo no cambió, aunque la build siguiente se copiara con las mismas fechas | `test_x02_the_deploy_rehearsals_see_the_same_pages_as_the_speed_check` con el `Pages` de la ronda 15: «Not a gzipped file»; mutante sin 304 en la rama comprimida: `assert 200 == 304` | pasa; `field_card_qa.py` 56/56 con los ensayos servidos comprimidos |

| X01 | Sin el Chromium que Playwright espera, la medición de velocidad se detiene al empezar y dice qué hacer | en este contenedor Playwright 1.55.0 pide `chromium-1187` y sólo hay 1194: Lighthouse falló dentro de chrome-launcher en la primera página, tras arrancar el servidor; `test_x01_a_missing_chromium_stops_the_speed_check_with_the_reason`: «DID NOT RAISE SystemExit» | se detiene antes de servir nada: «Lighthouse needs Chromium at …chromium-1187…: run `python3 -m playwright install chromium` or set FOCALRUTA_CHROME» |
| X02 (portada) | La portada queda dentro del presupuesto con margen, también en un CI más lento | con el paso 3 dentro, el bloqueo de la portada medía 196 ms de mediana (236, 196, 174.5) frente a 200 ms: el diseño inicial de 5667 elementos, 3909 de ellos en la tarjeta oculta, cae en tareas de 150–260 ms | `content-visibility:auto` en las secciones bajo la primera pantalla: 50–85 ms en tres corridas, puntuación 1.00; con todo dentro, mediana de tres: bloqueo 87 ms, LCP 1.2 s, 127 KB, puntuación 1.00 |

Registros: `red_x02_one_pages_new_static_old_rehearsal.log`, `mutant_x02_no_304_on_gzip.log`,
`green_x02_one_pages.log`, `red_x01_missing_chromium.log`, `green_x01_missing_chromium.log`;
mediciones: `lh_variants.py`.

### Lo que el red team dejó para este PR (tercera pasada sobre PR #20)

El red team aprobó PR #20 en d60d6ee («PASS, ready to merge») y dejó tres cosas que no
bloqueaban (`FINDINGS_PR20.md`, «Third pass»), y después una cuarta: el sitio mezclaba
la coma y el punto decimal. Pablo fusionó PR #20 el 2026-10-18 (56a6e97).

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V16 | Un archivo que la página nombra sin revisión, abierto dentro de los 10 minutos de caché HTTP, es de esta build | sin `cache:'no-cache'` en `asset()` las 15 pruebas de Node pasaban; la nueva `test_v16_a_file_opened_within_the_http_cache_window_is_this_builds` falla con ese mutante («plan_c_1.webp · 1» en vez de «· B») | 16/16 |
| V19 | Mientras un diálogo está abierto, el resto de la página queda fuera de alcance | sólo se comprobaba la tarjeta; con la sesión o la toma abiertas con `show()` en vez de `showModal()`, o la tarjeta sin `inert`, ninguna comprobación fallaba | «keeps the rest of the page out of reach while open»: `:modal` o todo lo demás inerte, y 30 Tab nunca salen del diálogo; falla con los tres mutantes, pasa en ambas portadas a 390 y 1440 |
| V18 | Ningún texto se corta con puntos suspensivos | el título «FocalRuta · San Isidro» quedaba en «FocalRuta · S…» de 700 a 1024 px (69–122 px de 136) y el lugar del plan C en la barra a 700 px (419 de 483); la comprobación sólo miraba etiquetas de controles | la comprobación cuenta cualquier texto con `text-overflow:ellipsis` que no cabe; 0 en ambas portadas y los seis planes a 320, 390, 700, 768, 820, 844, 932, 1024 y 1440 px |
| V20 | Cada número se escribe como se lee en el Perú: punto decimal (es-PE en CLDR; la Ortografía de la RAE de 2010 lo recomienda) y un espacio entre el número y su unidad | `gear.js` y las notas de los planes decían «Faltan 0,3 pasos» y «2,5 m» junto al «0.24 m» del laboratorio óptico, y las páginas de plan «Distancia: 2.5m». Con `reading_floor.numbers_in`: fallaban la portada, la tarjeta y las dos guías del desafío publicadas, las etiquetas de los diagramas («1,9», «2,8») y las notas que da el equipo propio («2,8», «3,0») | 0 en las 38 páginas publicadas (la copia autónoma es la portada), en las notas de todos los equipos y franjas, en las etiquetas de los diagramas (los 120 redibujados) y en el navegador en cada estado, también con el equipo propio; los nombres de lente conservan el «35mm» del fabricante |

Registros: `red_followup1_asset_revalidate.log`, `green_followup1_asset_revalidate.log`,
`red_green_followup2_dialogs.log`, `red_followup3_ellipsis.log`, `green_followup3_ellipsis.log`,
`red_v20_numbers.log`, `green_v20_numbers.log`.

### Lo que encontró la comprobación del sitio publicado (56a6e97)

Tras fusionar PR #20, el hilo de comprobación en vivo revisó el sitio publicado
(`qa/LIVE_CHECK_PR20.md`): 244/244 archivos idénticos a main, el paquete sin conexión
funciona y sobrevive a un despliegue, axe sin infracciones, L1–L5 cerrados. Dejó un mayor,
un fallo de método y un detalle; su L6 (`live_pages_qa.py` roto) ya estaba corregido en X03.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V21 (M7) | Sin conexión, una página nunca guardada abre la portada en su propia dirección, con estilo, diciendo cuál era y con enlaces a ella y a la tarjeta | el worker devolvía los bytes de la portada bajo `plans/plan_c.html`: hoja de estilo, imágenes y enlaces resolvían bajo `plans/` (0/11 imágenes, enlaces a `plans/plans/plan_a.html`). `test_v16_offline_a_page_never_kept_sends_the_reader_to_the_home_page_with_its_name`: «[200, None, 'index.html · B']»; en Chromium con el servidor parado, 6 de 7 comprobaciones nuevas fallan («path: /plans/plan_c.html, rules: []») | redirección 302 a `index.html?sin-conexion=<página>`; la portada dice «el plan C» o «la página «wiki-tecnicas»» y enlaza «Volver a intentar» y «Abrir la tarjeta de campo»; 7/7, también a 320 px y con axe (80/80). Un mutante que no valida el nombre deja «Volver a intentar» en `javascript:alert(1)` y en `example.org`: la comprobación falla |
| V21 (T1) | Las pruebas sin conexión cortan la red de verdad | `browser_architecture_release_qa.py` usaba `context.set_offline`, que deja en la red las peticiones del propio worker: con un worker que no guarda nada (`navigate` devuelve `fetch(r)`) pasaba igual | la suite sirve el sitio ella misma y para el servidor, como U05; con ese worker falla («offline reload: net::ERR_FAILED»), con el real pasa |
| V02 (detalle) | La línea de ajustes de la tarjeta se lee como dos palabras al copiarla o escucharla | `<span class="fc-v-lens">50 mm</span><span class="fc-v-exposure">f/13…` sin espacio: «50 mmf/13» en las 180 franjas de las cuatro copias (la flexbox lo ocultaba en pantalla) | un espacio entre ambas; `test_v02_the_lens_and_the_exposure_read_as_two_words` pasa en las cuatro |

Registros: `red_m7_node.log`, `green_m7_node.log`, `red_m7_browser.log`, `green_m7_browser.log`,
`mutant_m7_no_name_check.log`, `red_t1_old_method_mutant.log`, `red_t1_new_method_mutant.log`,
`green_t1_arch_release.log`, `red_nit_lens_exposure.log`, `green_nit_lens_exposure.log`.

### El primer CI de PR #21 (corrida 39089226401)

El primer CI que corrió las suites de navegador en Linux falló en tres trabajos que aquí
pasaban. Ninguno era un fallo del sitio publicado en un teléfono; dos eran fallos de las
pruebas y uno, el título del desafío, lo sería en una pantalla de 320 px con una fuente ancha.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X01 (fuentes de CI) | Las suites pasan con las fuentes que el Chromium de Linux usa por defecto, no sólo con las de la máquina que las corrió | con DejaVu Sans, la fuente que el Chromium de CI usa para `system-ui`, «arquitectónica» mide 327 px y la columna del título a 320 px mide 272: `browser_round1_qa`, `browser_round2_learning_qa` y `browser_round5_route_qa` fallan sólo por desbordamiento a 320 px, en CI y aquí con la configuración de fuentes de CI (`FONTCONFIG_FILE` sin Inter) | el tamaño mínimo del título baja de 2.5 a 2 rem y una palabra que aún no quepa se parte en vez de desbordar; las cinco suites en verde con las fuentes de CI |
| X01 (sin Playwright) | La prueba de «falta Chromium» corre donde Playwright no está instalado | el trabajo `lint-and-test` no instala Playwright: «ModuleNotFoundError: No module named 'playwright'»; aquí igual con `sys.modules['playwright']=None` (`red_x01_without_playwright.log`) | la prueba sustituye el módulo de Playwright; 7/7 con y sin Playwright; el mutante sin la comprobación del archivo sigue fallando («DID NOT RAISE SystemExit») |
| V16 (relevo del worker en el ensayo) | El ensayo de despliegue comprueba el build nuevo bajo el worker nuevo | CI: «installed behind the HTTP cache: the home page gets only this build's files: ['assets/hosted.css', 'data/plans_embedded.js', 'index.html']» y lo mismo para `field_card.html`. Si la primera `update()` tras el despliegue no encuentra nada, el `settle()` de f74b454 da esas dos líneas exactas (`red_settle_lost_update_old.log`); la prueba de Node del mensaje falla con la plantilla de f74b454 (`answered: []`) | el worker responde `{type:'version'}` por un MessageChannel con su VERSION, y `settle()` espera a que el worker activo diga que es el build desplegado, pidiendo otra actualización cada pocos segundos: con la misma primera `update()` perdida, 2/2 (`green_settle_lost_update_new.log`); la prueba de Node pasa |
| X01 (diagnóstico) | Un CI en rojo dice qué suite falló y deja su reporte | la primera suite de arquitectura imprimió sólo `{"passed": false}` y, con `bash -e`, las otras cuatro no corrieron | cada suite corre aunque falle otra, el registro nombra la que falla y los reportes quedan como artefacto del trabajo |

Registros en el scratchpad: `ci_r1/*.log`, `ci_x01/*.log`, `ci_fc/*.log`.

Escalada de investigación (activada, V16). La primera hipótesis fue que la `update()` del
ensayo se juntaba con otra en curso porque el `sw.js` anterior tardaba en llegar; con un
`sw.js` lento a propósito no se reprodujo. Fuentes:

- Especificación de Service Workers, «Schedule Job»: un trabajo de actualización equivalente
  a uno cuya promesa aún no se resolvió se agrega a ese y recibe su resultado (citado en
  `service_worker_jobs.cc` de Cobalt).
- Matt Falkenhagen (Chrome), public-webapps-github, enero de 2016: Chrome programa una
  actualización un segundo después de cargar una página dentro del alcance del worker, y
  programar otra aplaza el temporizador.

Parecido: el ensayo navega a `field_card.html`, despliega y llama a `update()` en
milisegundos, con la actualización de Chrome pendiente. Diferencia: CI usa Chromium 140 en
una máquina más lenta; aquí, 141. Hipótesis cambiada: sea cual sea el orden (una `update()`
unida a otra que vio el build anterior, o la página que ve el resultado antes que el worker
nuevo), «nada instalando y el activo activado» también se cumple con el worker anterior, así
que no prueba que el nuevo mande; hace falta evidencia positiva, la versión. Prueba falsable:
perder a propósito la primera `update()` reproduce las dos líneas de CI con el `settle()`
anterior y pasa con el nuevo; en CI el ensayo debe pasar, y si el worker nuevo no llegara a
instalarse fallaría con «never took over in 60 s; the active one says …», que separa ese caso.

Compromisos de esta corrección:

- A 320 px el título del desafío pasa de 40 a 32 px (a 360 px, de 40 a 36; desde 400 px no
  cambia). Con una fuente aún más ancha, la palabra se parte con guion donde el navegador
  sabe hacerlo en español y sin guion donde no.
- El worker responde un mensaje más, `version`, y sólo por un MessageChannel; dice lo que ya
  está escrito en `sw.js`.
- Las cinco suites de arquitectura siguen en un solo trabajo de CI y no en una matriz: un
  fallo ya no oculta los siguientes y se instala el navegador una vez en vez de cinco.
- Este contenedor prefería Inter para `system-ui` (la regla `56-prefer-inter.conf`, una
  aproximación a la fuente del Mac del dueño). El cierre anterior usó Inter y este usa las
  fuentes de CI, así que las dos configuraciones quedan probadas.

Errores propios: di por buenas las suites de arquitectura con una sola configuración de
fuentes; la columna del título a 320 px no dejaba margen. Y el primer `settle()` daba por
hecho que, cuando `update()` termina, la página ya ve el worker nuevo.

### Segunda pasada del red team sobre PR #21 (f74b454, `qa/FINDINGS_PR21.md`)

El red team reprodujo todo lo demás y dejó un mayor, un medio y cinco menores. CI en aada8b2,
con las correcciones de la sección anterior, ya estaba en verde en los ocho trabajos.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| F1 (V16, X02) | Un despliegue ensayado sirve el build nuevo a cada petición posterior, también por una conexión abierta antes | `static_server.serve` fijaba el build al aceptar la conexión; Chromium abre sockets antes de usarlos. `test_v16_a_connection_opened_before_a_deploy_gets_the_new_build`: «b"const VERSION='anterior';" == b"const VERSION='siguiente';"». El red team: tarjeta 53/56 en 3 de 3 corridas | el build se elige en `parse_request`, por petición; la prueba pasa. `settle()` pide una sola actualización y espera la versión del build desplegado: un segundo intento habría ocultado este fallo |
| F2 (X04, privacidad) | El registro no guarda carpetas del lector ni lo que escribió | con la copia abierta desde un archivo guardaba `/home/maria.perez/Descargas/…` como página y en los mensajes; el error de `JSON.parse` de Chrome guardaba «"Mi equipo Pablo 85mm"». Dos pruebas nuevas fallan (`red_f2_privacy.log`) | una página abierta desde un archivo queda con su nombre; una URL `file:` en un mensaje, `file://…/<nombre>`; el texto entre comillas queda «…», salvo un carácter o una dirección web. Las dos pruebas pasan |
| F3 (X01) | Toda suite usa el navegador que nombra CI | `browser_round1_qa`, `round2` y `round5` lanzaban el Chromium de Playwright: con `FOCALRUTA_CHROME=/no/such/chrome` round1 pasó igual; la prueba de contrato nueva los nombra | usan `qa_matrix.browser_options()`; con esa ruta, round1 se detiene con el motivo; la prueba pasa |
| F4 (X03) | Sólo el trabajo que publica puede escribir en Pages | `pages.yml` daba `pages: write` e `id-token: write` a todo el flujo, también a la comprobación que llama; la prueba nueva: «pages.yml grants writes to every job» | permisos de lectura arriba y de escritura sólo en `deploy` |
| F5 (V20) | La revisión de números ve segundos, milímetros y decimales largos | no veía «0,030 mm» (en el desafío y su guía de técnicas), «1/2000s» y «5–15s» (laboratorio de movimiento), «(24mm)» ni «35.8×23.9mm» | ve las tres formas y respeta los nombres de lente («EF 35mm f/2», «XF 35mmF2», y 35mm, 50mm, 85mm y 35–80mm del equipo); el sitio escribe «0.030 mm», «1/2000 s», «(24 mm)», «35.8 × 23.9 mm» e «ISO 100» |
| F6 (V21) | El aviso sin conexión no enlaza a una página que Pages no sirve | «plans/PLAN_C.html» mostraba el aviso con un enlace que da 404 (Pages distingue mayúsculas) | sólo rutas en minúscula, como todas las que guarda el worker; 7/7 con el caso nuevo |
| F7 (X02, X04) | `--dist` responde por el build que sirvió; `--only` desconocido lo dice; «Copiar» sin portapapeles avisa | el reporte de `--dist` tomaba las huellas de `dist/`; `--only plans/plan_z.html` caía con `IndexError`; sin portapapeles el botón no hacía nada («Copiar el registro», selección vacía) | huellas del build servido; `--only` desconocido sale con el código 2 y la lista de páginas; «Selecciona y copia el texto» y el registro queda seleccionado |

Al repetir las suites sobre 3558853, la release QA se detuvo en «standalone 320 numbers written
the Peruvian way: ['80mm']». Dos causas:

- Real: cuatro notas de «zooming» decían «gira el zoom de 35 a 80mm». Ahora, «de 35 a 80 mm».
  Una prueba nueva lee todo texto de `data/plans.json`, que llega al lector por JavaScript, así
  que un error así falla en pytest y no sólo en el navegador. Encontró además «E = 2,5·2^EV» en
  la fuente de la luz de ventana (ahora «2.5»). RED: `['2,5', '80mm']`; GREEN en 27e9759.
- Falso positivo de mi cambio de F5, en «exposición.35–80mm». Primera hipótesis: sólo el punto
  final de una frase toca la lente siguiente; un punto después de una palabra cierra la frase
  (27e9759). Falló: sobre 27e9759 las seis páginas de plan dieron «['80mm']» en
  «REFERENCIA35–80mm».

Escalada de investigación tras esa hipótesis fallida:

- Fuentes: MDN, `Node.textContent`, «Diferencias para o innerText» (textContent devuelve el
  texto de todos los nodos sin tener en cuenta el estilo); MDN, `HTMLElement.innerText` («If the
  element itself is not being rendered (for example, is detached from the document…), the
  returned value is the same as the Node.textContent property»); Juriy Zaytsev, «The poor,
  misunderstood innerText» (perfectionkills.com): textContent «ignores newlines created by <br>
  and around styled-as-block elements».
- Semejanzas y diferencias: el escaneo (`SHOWN_WORDS`) lee `textContent` de una copia separada
  del documento en Chromium, así que no hay corte entre elementos aunque se vean en líneas
  distintas, y `innerText` sobre esa copia daría lo mismo. Sobre el documento vivo, `innerText`
  sí separaría bloques, pero dejaría fuera lo oculto (diálogos cerrados) que el escaneo debe leer.
- Hipótesis nueva: cualquier carácter puede tocar el inicio de un número (una letra, un punto,
  un cierre de comillas), no sólo un punto. Un número debe leerse desde su propio inicio: el
  escaneo sólo evita empezar dentro de un número (después de una cifra, o de un punto o un guion
  que siguen a una cifra).
- Prueba falsable: `test_v20_a_number_is_read_from_its_own_start_whatever_touches_it` falla con
  `['80mm']` en «REFERENCIA35–80mm» y debe pasar, seguir viendo «de 35 a 80mm» y ver
  «DISTANCIA24mm» (un largo pegado a un título, que la regla anterior no veía). Pasa en d38d22f,
  y las seis páginas de plan y las dos portadas quedan sin largos pegados en el navegador.

Corrección de la investigación de la sección anterior: la causa del fallo de la tarjeta en CI
era F1, el servidor del ensayo, no el orden de los trabajos de actualización de Chrome. La
`update()` «perdida» que reproducía las líneas de CI era el mismo síntoma: la petición de
`sw.js` por un socket abierto antes del despliegue recibía el `sw.js` anterior, y la
actualización no encontraba nada nuevo. Los reintentos de `settle()` lo tapaban; por eso ahora
hay un solo intento. El apretón de manos con la versión se queda: es la prueba positiva de que
manda el worker nuevo.

Compromisos de esta pasada:

- Un mensaje de error pierde lo que iba entre comillas: «Cannot read properties of null
  (reading '…')» ya no dice qué propiedad. El archivo, la línea y la columna siguen ahí y
  ubican el fallo en el código; a cambio, nada que el lector escribió queda en el registro.
- Un apodo de lente pegado («el 85mm») sólo pasa si es una lente del equipo de los planes;
  otro número pegado a «mm» cuenta como medida y lleva espacio.
- Las acciones de GitHub siguen fijadas por etiqueta mayor y no por SHA: esta sesión sólo puede
  leer este repositorio, así que no puede verificar los SHA. Fijarlos (con Dependabot para
  mantenerlos) queda pendiente.
- El aviso sin conexión sigue apareciendo con señal si alguien abre a mano un enlace con
  `?sin-conexion=`: `navigator.onLine` dice «en línea» con wifi sin internet, y el aviso
  faltaría justo cuando hace falta.

Errores propios: al juntar los dos servidores de Pages en uno (X02) cambié de leer el build por
petición a leerlo por conexión, y mi primera explicación del fallo de CI culpó a Chrome; la
reproducción forzada mostró el síntoma, no la causa. Y probé la revisión de números de F5 sólo
con frases sueltas, no con el texto que lee el navegador: la release QA encontró el falso
positivo, dos veces, porque mi primer arreglo cubrió el caso visto y no la causa.

Cierre de esta pasada, en un árbol limpio con las fuentes de CI (DejaVu como `system-ui`):

| Comando | Salida | Resumen |
|---|---|---|
| `visual_resource_audit.py`, `optics_accessibility_qa.py`, `axe_accessibility_qa.py`, `field_card_qa.py`, `perf_budget_qa.py` en 27e9759 | 0 | 37/37, 22/22, 80/80, 56/56, 112/112 |
| las cinco suites de `tests/architecture/browser_*.py` en 27e9759 | 0 | todas en verde |
| `browser_release_qa.py` en f2446e5 | 0 | 422/422 |
| `pytest -q` | 0 | 762 pasan, 1 omitida (`test_editorial_contracts.py`: `wiki-tecnicas.html` no usa Schlick) |
| `pytest tests/architecture -q` | 0 | 344 pasan, 1 omitida |
| `verify_architecture.py`, `verify_release.py` | 0 | ningún fallo |
| `ruff … C901` a 10 | 0 | limpio |
| `regenerate_all.py && git diff --exit-code` | 0 | sin diferencias |

Sin fallos abiertos. Queda la revisión del red team sobre la cabeza nueva y el CI del PR.

### El CI de 518b9a3 (corrida 39275854658)

Seis de ocho trabajos en verde; dos rojos, los dos de este PR.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V19 | Un diálogo tiene el foco en la misma tarea que lo abre, como `showModal()` | CI: «hosted field card dialog takes focus from its button». `openFieldCard()` movía el foco en un `setTimeout(0)` y la comprobación lee el foco justo después del clic. La comprobación nueva («dialog has focus in the task that opens it») hace clic y lee el foco en la misma tarea: falla en la tarjeta y pasa en los diálogos de sesión y de toma, que usan `showModal()` | la tarjeta enfoca su botón de cerrar al abrirse, sin esperar; la comprobación nueva pasa en las dos portadas |
| X01 | Una suite que falla dice qué falló | `browser_round2_learning_qa.py` imprimió `"failed_checks": {}`: sólo listaba las invariantes, no los errores de consola. Con el Chromium completo que nombra CI (desde F3), la página pide su icono, `../../assets/app-icon.svg`, y la raíz aislada de la carpeta del desafío respondía 404: un error de consola en 320 px | la suite sirve `dist/canon6d_sota_hosted`, la raíz pública que publica Pages, y abre `/challenges/arquitectura-en-foco/`; el icono resuelve como en vivo y el repositorio sigue sin servirse. El resumen nombra cada condición que falla y lista los errores; con la raíz anterior dice `"no_console_errors": [[320, 640]]` y el 404 |

La carrera del foco no se reprodujo aquí: diez de diez clics con el foco ya dentro, en el
Chromium completo y en el headless shell. La causa se lee en el código (el foco se mueve una
tarea después) y la comprobación nueva la hace visible siempre, sin depender del orden de
las tareas en el runner.

Compromisos: la suite de los laboratorios revisa la copia publicada del desafío y no la de
`challenges/`. Son idénticas byte a byte: `build_dual_release.py` copia la carpeta tal cual
(`shutil.copytree`) y CI exige que regenerar no cambie nada.

Error propio: mis corridas «como en CI» usaban las fuentes de CI pero no su navegador. Sin
`FOCALRUTA_CHROME`, Playwright lanza en modo headless su «headless shell», que no pide el
icono de la página y ordena las tareas de otra forma; CI nombra el Chromium completo. Las
corridas locales ahora fijan `FOCALRUTA_CHROME=/opt/pw-browsers/chromium`.

### Revisión parcial del red team en 518b9a3

F1, F3, F4, F6 y F7 pasan; la tarjeta da 56/56 en 3 de 3 corridas y la explicación de las
fuentes queda confirmada. Pidió tres añadidos:

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X04 | Un apóstrofo no abre una cita | «TypeError: can't read 'Lente de maria.perez'» guardaba el nombre: el apóstrofo de «can't» se emparejaba con la comilla siguiente. `test_x04_an_apostrophe_does_not_open_a_quote` falla y deja «maria.perez» y «85mm» | una comilla simple abre una cita sólo tras un espacio o un signo y la cierra sólo antes de ellos; «can't» y «maría's» quedan como apóstrofos, y una comilla sin cerrar sigue perdiendo el resto. La prueba pasa |
| X01 | La suite de los laboratorios dice qué archivo falló | listaba los errores de consola sin la ruta del archivo | nombra `no_failed_resources` y las rutas; con la raíz anterior, «404 /assets/app-icon.svg» |
| V20 | Una lente escrita por el lector sin su número f no es una medida | «EF 100mm Macro», «RF 24-105mm», «EF-S 10-18mm», «XF 23mm» salían marcados | un código de montura justo antes del número nombra una lente; «DISTANCIA 24mm» y «a 80mm» siguen marcados |

Compromiso: la lista de monturas es corta (EF, EF-S, EF-M, RF, RF-S, XF, XC, FE, Z, AF, AF-S,
AF-P, DX). Una lente de otra montura escrita sin su número f cuenta como medida.

Cierre de esta pasada, en un árbol limpio con las fuentes de CI y el Chromium completo
(`FOCALRUTA_CHROME=/opt/pw-browsers/chromium`), como CI:

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en fd4c8de | 0 | release 428/428, axe 80/80, tarjeta 56/56, velocidad 112/112, visual 37/37, óptica 22/22 |
| las cinco suites de `tests/architecture/browser_*.py` en fd4c8de | 0 | todas en verde |
| `pytest -q` | 0 | 764 pasan, 1 omitida (`test_editorial_contracts.py`: `wiki-tecnicas.html` no usa Schlick) |
| `pytest tests/architecture -q` | 0 | 344 pasan, 1 omitida |
| `verify_architecture.py`, `verify_release.py` (mínimo de release 428) | 0 | ningún fallo |
| `ruff … C901` a 10 | 0 | limpio |
| `regenerate_all.py && git diff --exit-code` | 0 | sin diferencias |

Sin fallos abiertos. Queda el CI de la cabeza nueva y la corrida completa del red team.

### Cambios visibles

- Al pie de la portada, «Registro de errores de este dispositivo»: vacío si nada
  falló; si algo falló aquí, en un plan o en la tarjeta, lo lista y permite copiarlo o
  abrirlo como aviso en GitHub. Nada sale del teléfono sin que el lector lo envíe.
- Los números usan el punto decimal y separan la unidad («2.5 m», «Faltan 0.3 pasos»)
  en todo el sitio, también en los diagramas.
- El título de la portada ya no se corta entre 700 y 1024 px; la barra de los planes
  muestra «Plan individual» en vez del lugar, que ya encabeza el plan.
- Sin conexión, abrir una página que nunca se guardó lleva a la portada con un aviso
  ámbar: «Sin conexión: el plan C no se guardó en este teléfono, así que se abrió la
  portada», con «Volver a intentar» y «Abrir la tarjeta de campo». Antes se veía una
  portada rota, sin estilo ni imágenes y con enlaces que no llevaban a ninguna parte.
- El título de la página del desafío es algo más pequeño en pantallas de menos de 400 px
  (32 px a 320 px), para que «arquitectónica» quepa con cualquier fuente.
- Los tiempos del laboratorio de movimiento separan la unidad («1/2000 s», «10 s», «ISO 100»), y
  la nota de óptica dice «35.8 × 23.9 mm» y «0.03 mm»; el desafío, «0.030 mm»; las notas de
  «zooming», «de 35 a 80 mm».
- «Copiar el registro», sin portapapeles, dice «Selecciona y copia el texto» y deja el registro
  seleccionado.
- La tarjeta de campo, en la portada, pone el foco en su botón de cerrar en el mismo momento en
  que se abre.
- Nada más cambia a la vista: el resto es CI y comprobaciones.

### Compromisos explícitos

- La velocidad es de laboratorio (Lighthouse simula un teléfono y 4G lenta), no de
  lectores reales: no hay medición de campo porque exigiría enviar datos. Mediana de
  tres corridas; Lighthouse recomienda más para comparar versiones, pero tres bastan
  para un umbral con margen.
- Presupuestos de bytes ≈ 1.5 veces el peso actual de cada tipo; los de tiempo son la
  marca «buena» de Lighthouse para móvil.
- `FocalRuta_STANDALONE.html` (15 MB) no tiene presupuesto: es la copia que se
  descarga una vez, no una página que se navega. Los 25 mapas de ruta comparten
  plantilla: se mide uno.
- El registro sólo conoce los errores de quien lo envía; los de un lector que no
  avisa no se ven. A cambio, FocalRuta no recoge nada de nadie. Las páginas sin
  script (guías del desafío, mapas, 404) no lo llevan.
- Sin Content-Security-Policy: GitHub Pages no deja enviar cabeceras y una política
  en `<meta>` necesitaría `'unsafe-inline'` para los scripts en línea, así que
  bloquearía poco; en su lugar, las comprobaciones de velocidad y del sitio publicado
  fallan ante cualquier petición a otro origen.
- La comprobación diaria se desactiva si el repositorio pasa 60 días sin actividad
  (regla de GitHub para flujos programados); GitHub avisa por correo antes.
- Que un PR no pueda fusionarse con CI en rojo depende de una regla de rama en
  GitHub (Settings → Branches), que sólo puede activar el dueño.
- `content-visibility:auto` deja las secciones lejanas con una altura provisional de
  1000 px hasta que se acercan: la barra de desplazamiento cambia de largo la primera vez
  que se recorre la página (el anclaje de desplazamiento mantiene quieto lo que se lee).
  Al imprimir se dibuja todo. La auditoría V18 mide con todo dibujado, como lo ve el
  lector al llegar a cada sección.
- La barra de los planes ya no dice el lugar; lo dice entero la primera línea del plan.
- Los 120 diagramas se redibujaron para el punto decimal: quien guardó el paquete sin
  conexión vuelve a descargar los diagramas una vez (unos 11 MB) en la siguiente visita con red.
- El aviso sin conexión nombra la página por su ruta («el plan C», «la página
  «wiki-tecnicas»»), no por su título: el título está en la página que no se guardó. La
  dirección de la portada pierde el `?sin-conexion=` al mostrarlo, para que recargar con
  señal no repita el aviso.
- Una página nunca guardada sigue sin verse sin conexión: sólo se evita la portada rota.
- Los nombres de lente conservan la grafía del fabricante («EF 35mm f/2»): es un nombre,
  no una medida, y es como el lector lo busca.
- Las vistas previas de los planes en la portada siguen recortadas a tres líneas
  (`line-clamp`): el texto completo está en la página de cada plan, a un toque. La
  comprobación V18 cuenta los puntos suspensivos, no ese recorte.
- Lighthouse aconseja cinco corridas para comparar versiones; se mantienen tres porque la
  portada queda ahora a 115 ms o más del presupuesto de bloqueo.
- Los servidores sencillos de las demás suites (`QuietHandler`) siguen siendo el de
  Python sin compresión: comprueban funciones, no transferencias ni cachés, y cambiarlos
  no compraría nada.
- CI tarda más en cada PR: las suites de navegador corren en paralelo; la más lenta, la
  de velocidad, tardó unos ocho minutos aquí.

### Cierre (comandos, código de salida, resumen)

| Comando | Salida | Resumen |
|---|---|---|
| `python3 -m pytest -q` | 0 | 752 pass, 1 skip |
| `python3 scripts/verify_architecture.py` | 0 | `checks_failed: []` (incluye el escaneo de privacidad) |
| `python3 scripts/verify_release.py` | 0 | `checks_failed: []`; mínimos subidos a 421 (release), 80 (axe) y 112 (velocidad) |
| `ruff check scripts tests --select C901` (máx. 10) | 0 | sin hallazgos |
| `python3 scripts/regenerate_all.py && git diff --exit-code` | 0 | sin cambios |
| Seis suites con reporte (`visual_resource_audit`, `optics_accessibility_qa`, `browser_release_qa`, `axe_accessibility_qa`, `field_card_qa`, `perf_budget_qa`) sobre 1296b48 limpio | 0 | visual 37/37, óptica 22/22, release 421/421, axe 80/80, tarjeta 56/56, velocidad 112/112 |
| Cinco suites `tests/architecture/browser_*.py`, una tras otra | 0 | en verde en las siete vistas; la de release corta la red parando el servidor |
| Ensayo de X03 bajo `/focalruta/` (`live_pages_qa.py` y presupuestos sobre esa URL) | 0 | 88/88 y 24/24 |

Tras el primer CI de PR #21, sobre 92506cd limpio y con las fuentes de CI: visual 37/37,
óptica 22/22, release 421/421, axe 80/80, tarjeta 56/56, velocidad 112/112 y las cinco suites
de arquitectura en verde. `pytest -q` 753 pass, 1 skip; `verify_architecture.py` y
`verify_release.py` con `checks_failed: []`; `ruff … C901` sin hallazgos;
`regenerate_all.py && git diff --exit-code` sin cambios (todos con salida 0).

Verificación independiente: el PR va al red team y al hilo de comprobación en vivo, que
repite su revisión tras el despliegue. Fusionar sigue necesitando la palabra de Pablo.

### Referencia de experto por decisión

- X01: herramientas fijadas por versión (`package-lock.json`, `requirements-qa.txt`), como
  piden las guías de GitHub Actions para builds reproducibles; un experto rechazaría un CI
  que aprueba con reportes hechos en otra máquina, que es lo que pasaba.
- X02: los umbrales «buenos» de Core Web Vitals y de Lighthouse para móvil (web.dev); el
  ahorro de diseño con `content-visibility:auto` y `contain-intrinsic-size:auto` sigue la
  guía de web.dev (Baseline 2024: Chrome 85, Firefox 125, Safari 18).
- X03: comprobación sintética del sitio publicado tras cada despliegue y a diario; un
  experto rechazaría dar por desplegado lo que el CDN aún no sirve, por eso espera el commit.
- X04: privacidad desde el diseño: el registro no tiene forma de enviar nada; enviar es un
  acto del lector.
- V21: la página de respaldo sin conexión de web.dev y Workbox (una página guardada que se
  muestra cuando la red falla). Se redirige en vez de servir los bytes en otra dirección
  porque una navegación acepta una respuesta de redirección (modo «manual» de Fetch) y así
  las rutas relativas resuelven bien; un experto rechazaría una portada rota como respaldo.
  Las pruebas cortan la red parando el servidor porque el interruptor de Playwright no
  alcanza las peticiones del worker (11 peticiones medidas con `navigator.onLine=false`).
- V20: CLDR para es-PE (punto decimal), la Ortografía de la RAE (2010), que recomienda el
  punto, y el folleto del SI de la BIPM (9.ª ed., 5.4.3), que separa siempre el número de
  su unidad con un espacio. Un experto rechazaría dos marcas decimales en una misma página.

### Errores propios encontrados en esta ronda

- El primer `content-visibility` hizo que la auditoría de solapes viera 16–164 «solapes»
  por portada: mide posiciones con las secciones lejanas aún a su altura provisional.
  Ahora mide con todo dibujado.
- La medición de velocidad se probó al principio con `FOCALRUTA_CHROME` puesto a mano; sin
  él, en este contenedor, caía dentro de Lighthouse. Ahora se detiene con el motivo.

- Creé `requirements-browser.txt` sin ver que `requirements-qa.txt` ya fijaba lo
  mismo; lo borré y CI usa el existente.
- La primera medición de la portada dio LCP 3.4 s porque el servidor de Python no
  comprime: el sitio real sí. El servidor de QA (`static_server.py`) comprime como
  Pages y la portada mide 1.2 s.
- `live_pages_qa.py` llevaba roto desde 2140c41 (un paréntesis) sin que nadie lo
  notara porque nunca corría en CI.
- El primer cambio de comas por puntos en `index.html` pasó también por los datos en
  base64 y los bloques generados, y los estropeó; lo deshice y lo rehíce saltando esas líneas.
- `browser_round2_learning_qa.py` leía «proyecta 1,3×» con un patrón de dígitos y comas:
  con V20 no encontró nada y la suite se detuvo. Lo encontró la corrida completa; ahora lee
  sólo el punto, así que una coma que vuelva falla en V20 en vez de pasar aquí.
- Los reportes de la primera corrida sobre V20 quedaron «+dirty» porque las capturas de
  la corrida anterior seguían sin commit; se volvieron a generar sobre el árbol limpio.

Escalada de investigación: se activó una vez, por el relevo del worker en el ensayo de la
tarjeta (ver «El primer CI de PR #21»), cuya causa real encontró el red team (F1), y por la
revisión de números, que leía «80mm» en la lente del equipo (ver «Segunda pasada del red team
sobre PR #21»). Los demás RED se explicaron a la primera.

### La tarjeta del inicio perdía sus estilos (X05, 2d222b8)

Lo encontré midiendo la apertura de la tarjeta desde el inicio (la nota de tamaño del DOM del
red team): en las capturas del inicio en modo oscuro, la tarjeta tenía texto oscuro sobre
fondo oscuro. Ninguna comprobación lo veía, y está en el sitio publicado.

Dos causas, las dos silenciosas porque el navegador descarta sin avisar lo que no entiende:

- El marcador `<!-- FIELD CARD CSS START -->` estaba dentro de la hoja de estilos. `<!--` y
  `-->` sólo se ignoran entre reglas, en el nivel superior de la hoja; las palabras del
  marcador pasaban a ser el comienzo del selector de la regla siguiente, que deja de ser
  válido, y el navegador descartaba la regla entera. En el inicio era la regla base de la
  tarjeta (`.fc-app`: colores, fondo, márgenes, fuente); en el inicio publicado, el marcador
  de cierre se llevaba además el `:root` de `hosted.css` (anillo de foco y tintas de lectura).
- `font:600 14px/1.2 inherit` y `font:800 16px/1 inherit`: `inherit` sólo vale sola, así que
  el navegador descartaba la declaración y «Siguiente toma» y los dos botones de lista
  quedaban a 13.33 px, sin negrita, también en la página de la tarjeta.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X05 | Cada declaración y selector del CSS publicado es uno que el navegador conserva | sobre la build de c71bd3a, tres hojas pierden algo: las dos declaraciones `font` en la tarjeta, el inicio y `hosted.css`; el selector `<!-- FIELD CARD CSS START --> .fc-app` en el inicio y en `hosted.css`, y `<!-- FIELD CARD CSS END --> :root` en `hosted.css` | 16 hojas distintas, ninguna pierde nada |
| X05 | Ninguna hoja publicada mete un comentario HTML dentro de una regla (estático, en CI con `pytest`) | `test_x05_no_shipped_stylesheet_puts_an_html_comment_inside_a_rule` falla en 3 de 47 páginas: `index.html` y las portadas de `dist/` (publicada y descargable) | pasa en las 47; los marcadores son comentarios CSS (`/* FIELD CARD CSS START */`) y el integrador sigue encontrando los viejos, así que un `index.html` antiguo se repara al regenerar |
| V05 | La tarjeta en el diálogo del inicio se ve como en su propia página | con la misma comparación, elemento por elemento a 390 px: 10534 diferencias de día, 8017 en oscuro y 7999 con la pantalla nocturna, en las dos portadas | 0 en las seis |

La comparación de V05 encontró dos diferencias más que el marcador no explicaba, las dos por
algo que la tarjeta no fijaba y el inicio sí: `p, li {line-height:1.55}` cambiaba el
interlineado de la tarjeta, y la base del inicio hace que los botones hereden los dígitos
tabulares, que en la página de la tarjeta no heredaban. La tarjeta fija ahora
`.fc-app :where(p,li){line-height:inherit}` (con `:where()` no gana a ninguna clase) y sus
botones heredan `font-variant-numeric`.

#### Cambios visibles

- En el inicio, la tarjeta de campo se ve como en su página: en modo oscuro su texto vuelve a
  leerse; de día, los botones de plan, luz y sujeto vuelven a tener borde y a marcar el
  elegido; vuelve su fondo, sus márgenes y su fuente.
- «Siguiente toma» (16 px) y los dos botones de lista (14 px) vuelven a la negrita y al tamaño
  con que se diseñaron, en la tarjeta y en el inicio. Ocupan algo más; la tarjeta a 320 px no
  corta nada (V18 pasa).
- El inicio publicado recupera las variables de su `:root`: el anillo de foco amarillo y las
  tintas de lectura.

#### Compromisos explícitos

- La comprobación del navegador no pregunta por lo que está escrito para otro motor ni por lo
  que no puede juzgar fuera de su sitio: propiedades con prefijo, valores y seudoclases
  `-moz-`, `-ms-` y `-o-`, una propiedad estándar escrita junto a su gemela `-webkit-` en el
  mismo bloque (`line-clamp`), propiedades personalizadas (cualquier valor es válido hasta
  usarse), selectores anidados con `&` y los bloques de descriptores (`@font-face`, `@page`,
  `@property`). Un error dentro de esas excepciones pasa sin verse; por ejemplo, un valor mal
  escrito en una propiedad `-webkit-` que Chromium sí usa (`-webkit-line-clamp:2x`), o uno
  estándar escrito junto a su gemela (nota del red team; hoy no hay ninguno).
- X05 lee hojas de estilo, no los atributos `style` ni los estilos que pone el JavaScript. El red
  team los revisó a mano en 873df78 y son válidos; una comprobación automática queda fuera de
  este PR.
- La comparación de V05 mira lo que ve un lector: si el elemento se dibuja, su fondo, relleno,
  esquinas y cada borde visible y, si tiene texto propio, color, tamaño, peso, fuente,
  interlineado y dígitos. Deja fuera los bordes de 0 px (la base de Tailwind del inicio da a
  todo `border: 0 solid`, que no dibuja nada), la letra de elementos sin texto propio (la misma
  base da `font: inherit` a los campos, que no la muestran) y tamaños y posiciones, porque el diálogo pone la
  tarjeta en otro contenedor.
- Los marcadores del JavaScript de la tarjeta (`<!-- FIELD CARD JS START -->`) siguen como
  están: en un script clásico, `<!--` y `-->` al comienzo de línea son comentarios de una línea
  (ECMAScript, anexo B.1). Romperían el script si pasara a ser un módulo.

#### Referencia de experto

- CSS Syntax Level 3: CDO y CDC (`<!--`, `-->`) se descartan sólo en el nivel superior de la
  hoja; dentro del preludio de una regla son parte de él. Selectors Level 4: un selector no
  válido invalida la regla entera. CSS Values and Units 4: las palabras clave globales
  (`inherit`) no se combinan con otros valores.
- WCAG 2.2, 1.4.3 (contraste mínimo) y 2.4.7 (foco visible): un experto rechazaría un diálogo con
  texto oscuro sobre fondo oscuro y un foco sin el anillo que se diseñó.

#### Errores propios

- En el paso 3 puse la regla base de la tarjeta justo después del marcador `<!--` que venía del
  prototipo (allí ya se tragaba `#field-card-modal{--fc-ink…}`), y escribí la fuente de los
  botones con `inherit` dentro del atajo. El `:root` perdido de `hosted.css` ya estaba en main
  antes del paso 3.
- Ninguna comprobación comparaba la tarjeta del inicio con la de su página. La única que la
  abre en el inicio (`field_card_qa.py`) lo hace de día, donde el texto sin color caía al
  oscuro del inicio sobre fondo claro y se leía; axe revisa los estados de la tarjeta sólo en
  su página, y el inicio con el diálogo cerrado.
- La primera versión de la comprobación preguntaba por cada selector con
  `CSS.supports('selector(…)')`, que rechaza seudoelementos que una hoja sí acepta
  (`::-webkit-search-decoration`), y marcaba `line-clamp` en los planes, escrito junto a su
  gemela `-webkit-`. Ahora prueba cada lista de selectores como una regla, que es como la toma
  el navegador, y exime a la gemela.

Escalada de investigación: no se activó; cada diferencia tuvo una causa que se confirmó a la
primera.

#### Cierre (comandos, código de salida, resumen)

Sobre el árbol limpio, con las fuentes de CI y el Chromium completo
(`FOCALRUTA_CHROME=/opt/pw-browsers/chromium`), y sirviendo sólo la raíz pública `dist/`:

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en 2d222b8 | 0 | release 450/450 (16 hojas y 6 comparaciones nuevas), axe 80/80, tarjeta 56/56, velocidad 112/112, visual 37/37, óptica 22/22; reportes en b197362 |
| las cinco suites de `tests/architecture/browser_*.py` en 2d222b8 | 0 | todas en verde |
| `pytest -q` en b197362 | 0 | 814 pasan, 1 omitida (`test_editorial_contracts.py`: `wiki-tecnicas.html` no usa Schlick) |
| `pytest tests/architecture -q` | 0 | 344 pasan, 1 omitida (la misma) |
| `verify_architecture.py` (con el escaneo de privacidad), `verify_release.py` (mínimo de release 450) | 0 | `checks_failed: []` |
| `ruff … C901` a 10 | 0 | limpio |
| `regenerate_all.py && git diff --exit-code` | 0 | sin diferencias |

Sin fallos abiertos.

Verificación independiente: el red team aprobó 873df78 (`qa/FINDINGS_PR21.md`, «Recheck at
873df78»). Reprodujo el error en main con su propio lector de CSS (tinycss2) y Chromium:
`hosted.css` pierde los dos selectores con marcador, la tarjeta del inicio en oscuro tiene el
texto rgb(15,23,42) sobre fondo transparente y `--focus-ring` está vacío. En 873df78, sobre 40
hojas, sólo quedan las gemelas con prefijo y lo escrito para otro motor; la tarjeta del inicio
coincide con su página de día y en oscuro, a 320 y 390 px, en las dos portadas, y nada se sale a
320 px. `test_css_audit.py` falla 3 y pasa 47 en el árbol de main, y pasa 50 de 50 en 873df78.
Revisó a mano los atributos `style` y los valores que pone el JavaScript: todos válidos. Dejó dos
notas que no bloquean, ahora en los compromisos. Falta el hilo de comprobación en vivo, tras el
despliegue; fusionar sigue necesitando la palabra de Pablo.

## Ronda 17 · Lo que PR #21 dejó para después (2026-10-20)

PR #21 se fusionó con la palabra de Pablo («Merge now») como 9cd348d. El despliegue
(corrida 39457468967) publicó el worker `focalruta-1ce8b23ec608`, y su comprobación del
sitio publicado, presupuestos de velocidad incluidos, pasó a las 16:36 UTC; el hilo de
comprobación en vivo también lo aprobó. Esta ronda atiende lo que quedó pendiente: la nota
del red team sobre `choose()` (V09), el texto en inglés de las páginas del desafío (V12) y
la apertura lenta de la tarjeta desde el inicio, que ahora tiene requisito propio (X06).
Fusionar sigue necesitando la palabra de Pablo.

### Requisitos y evidencia RED → GREEN

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| V09 | La tarjeta arranca con lo que encuentre en su memoria, y el botón del inicio la abre aunque el script de la tarjeta se detenga | sobre 9cd348d, cuatro memorias estropeadas (una comilla en lo elegido, una cadena, una lista, tomas marcadas que son un número): con la comilla, `choose()` lanza `SyntaxError` al armar el selector; con la cadena, «Cannot create property 'done' on string»; con la lista no se guarda la marca siguiente; y en el inicio, «Cannot access 'fcOpener' before initialization»: el botón no abre nada | los cuatro casos en `field_card_qa.py` (dos comprobaciones nuevas, 58/58): la tarjeta arranca, elige la luz y guarda la marca siguiente, y el botón del inicio abre el diálogo. Mutante: si el script de la tarjeta se detiene en su primera línea, el diálogo se abre igual (`{'dialog_visible': True}`). `test_v09_memory_keeps_only_what_the_card_writes` en Node |
| V12 | Ninguna página publicada tiene prosa en inglés fuera de `lang="en"`; cada mecanismo de escena tiene nombre en español | `tests/test_spanish_text.py` sobre 9cd348d: 3 fallan y 75 pasan. Las dos copias de `wiki-tecnicas.html` tienen 11 tramos en inglés (las afirmaciones de los videos); `SCENE_MECHANISMS` no existe y las seis escenas verificadas muestran «Decisive Motion In Designed Ramp» y similares | 78/78. Los seis mecanismos en español (un identificador sin nombre detiene la build); las seis lecciones de video en español, con el inglés guardado en `original_en`; los títulos originales con `lang="en"` |
| X06 | Los toques más usados responden en 200 ms en un teléfono de gama media y nunca pasan de 500 ms en uno de gama baja | con la CPU calibrada como DevTools, abrir la tarjeta desde el inicio en la build de 1f72869, alternando con la nueva sobre la misma calibración (gama media 1.95×, baja 7.09×): gama media 96 ms (88–120), gama baja 440 ms (376–520), una corrida sobre la marca «mala» de INP; en otra calibración, 512 ms de mediana (432–544). Un mutante que ocupa 400 ms en `openFieldCard()` falla en los dos niveles (448 y 592 ms). Tres pruebas unitarias nuevas (búsqueda, presupuesto exacto y justo encima, nada que tocar) | la build nueva en la misma calibración: gama media 56 ms (56–64), gama baja 280 ms (224–360). En `PERF_BUDGET_QA.json` sobre 9d76947, 10/10 (gama media 1.91×, baja 7.44×): abrir la tarjeta 72 y 264 ms, el detalle de una toma 80 y 200, elegir plan 32 y 112, elegir luz 32 y 96, marcar una toma 24 y 104 |

### Cómo se encontró la causa (X06)

Con la CPU 4× más lenta, la apertura costaba 240–264 ms: estilo unos 100 ms sobre 954
elementos y diseño 111–146 ms sobre 613 objetos. Las estadísticas de selectores de Chrome
suman 6.6 ms sin frenar la CPU, así que no eran los selectores (los `:has()` de la tarjeta
incluidos). Quitar `inert` ahorraba unos 40 ms; se queda, porque es lo que deja fuera de
alcance la página de atrás. Tres palancas:

- Las tomas fuera de la pantalla: con `content-visibility:auto` en cada una, el diseño baja
  de 613 a 409 objetos.
- La pila de fuentes: en Linux, cada familia que el navegador busca y no tiene
  (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`) cuesta; con `system-ui`
  primero, el diseño bajaba de unos 120 a 64 ms a 4×. No se quedó: en Linux `system-ui` es
  DejaVu Sans, más ancha que Arial, y la suite de release encontró a 320 px la pestaña
  «Encuadre» cortada (61 px de texto en 58). En un teléfono la pila encuentra su fuente en
  la primera o la segunda familia.
- El primer cuadro: la cabecera de la tarjeta se pinta sola y los paneles un cuadro después
  (`requestAnimationFrame` y luego una tarea).

Un 4× fijo mide la máquina además de la página. Por eso X06 calibra como DevTools
(`devtools-frontend`, `panels/mobile_throttling/CalibrationController.ts`): corre el
BenchmarkIndex de Lighthouse en el navegador y busca por bisección la ralentización con la
que puntúa como el teléfono de gama media de DevTools (1000, un Pixel 5) y el de gama baja
(264, un Moto G Power 2022).

### Cambios visibles

- Abrir la tarjeta desde el inicio: el diálogo aparece con la barra y la cabecera de la
  tarjeta; los planes llegan un cuadro después y las tomas uno más tarde. En un teléfono de
  gama baja, la barra y la cabecera aparecen en 224–360 ms en vez de 376–520; en uno de gama
  media, en unos 56 ms en vez de 96. (Corregido tras R1: eso es la primera pintura. En
  9e2d121 los planes llegaban algo después que antes del PR; con 46f04db llegan a 342 ms en
  vez de 484 en gama baja. Ver «Rechazo del red team».)
- Las tomas que no están en pantalla se dibujan al acercarse. La barra de desplazamiento
  puede ajustarse un poco cuando una toma se dibuja por primera vez.
- Páginas del desafío: subtítulos de escena en español; cada tarjeta de video muestra su
  propia lección (antes, seis textos genéricos iguales bajo «Decisión práctica:
  pkMssQPul9o») y cita el video con su título original; la guía de técnicas, en español.
- La tarjeta ya no se detiene por lo que encuentre guardado.

### Compromisos explícitos

- En el primer cuadro tras el toque, los planes y las tomas no están todavía: un lector de
  pantalla no los encuentra durante ese cuadro. El foco va al botón de cerrar, que sí está.
- `content-visibility:auto` contiene el pintado de cada toma: lo que se saliera de ella se
  recortaría. Los anillos de foco caben (5 px dentro de 12 px de relleno), y al imprimir las
  tomas se dibujan todas (`content-visibility:visible`). Safari lo ignora antes de la 18 y
  dibuja todo, como antes.
- La calibración repite la de DevTools con una diferencia: la mediana de tres corridas por
  tasa, en vez de una, porque una máquina compartida de CI es más ruidosa. Aun así la tasa
  varía entre calibraciones (gama media 1.38–2.09×, gama baja 6.29–7.96× aquí, con
  puntuaciones de 1908 a 2741) y los toques con ella. El BenchmarkIndex mide JavaScript; el
  estilo y el diseño no escalan igual, así que las cifras de gama baja son aproximadas
  (inferido de la variación).
- El presupuesto de gama baja es «nunca malo» (500 ms), no «bueno» (200 ms): ahí abrir la
  tarjeta sigue en 192–280 ms la primera pintura y 273–395 ms los planes (46f04db). Bajarla de
  200 en gama baja pediría dibujar menos de la tarjeta en el primer cuadro.
- No hay teléfono real: todo lo medido es emulación calibrada en Linux, donde buscar las
  fuentes que faltan pesa; que pese menos en un teléfono sigue siendo inferido.
- La detección de inglés cuenta palabras funcionales; una etiqueta corta en inglés (como los
  subtítulos de escena) se le escapa. Eso lo cubre la prueba de los mecanismos, no el
  detector.
- `original_en` se publica en `data/architecture/learning.json`: es material público de las
  lecciones y ninguna página lo muestra.

### Referencia de experto por decisión

- INP y sus marcas (200 ms «bueno», 500 ms «malo») y la Event Timing API: web.dev/articles/inp.
  Dejar que el navegador pinte antes del trabajo pesado: web.dev/articles/optimize-inp.
- Calibración de la CPU: `CalibrationController.ts` de devtools-frontend (puntuaciones 1000 y
  264, bisección hasta 10 puntos) y el BenchmarkIndex de Lighthouse (`page-functions.js`).
- CSS Containment 2: `content-visibility:auto` aplica contención de diseño, estilo y pintado
  siempre, y de tamaño sólo mientras se salta; `contain-intrinsic-size:auto` recuerda la
  última altura.
- WCAG 2.2, 3.1.2 (idioma de las partes): un título en inglés dentro de una página en
  español lleva `lang="en"`.

### Errores propios encontrados en esta ronda

- La primera mejora la medí con un 4× fijo (240 → 168 ms), y buena parte era la búsqueda de
  fuentes en Linux. Calibrado, en gama media la diferencia de esas dos palancas era pequeña
  (112 → 96 ms); lo que mueve a gama baja es pintar primero la cabecera.
- Cambié la pila de fuentes por velocidad sin medir antes el ancho del texto con la fuente que
  resultaba en Linux; la suite de release lo encontró a 320 px en el primer cierre (commit
  local, sin publicar) y lo deshice.
- Una sonda pasó a `page.evaluate` una asignación cuyo valor era una función, y Playwright la
  ejecutó: el diálogo se abría antes del clic y la medición se colgaba. Ahora la envuelve.
- El primer `git add` excluía `.claude` con un pathspec; git se negó porque la carpeta ya está
  ignorada y no se hizo el commit. Lo vi en el log y repetí sin la exclusión.

Escalada de investigación: no se activó; ninguna hipótesis de arreglo falló. La calibración
se tomó de la fuente de DevTools antes de escribir el presupuesto.

### Cierre (comandos, código de salida, resumen)

Sobre el árbol limpio, con las fuentes de CI y el Chromium completo
(`FOCALRUTA_CHROME=/opt/pw-browsers/chromium`), y sirviendo sólo la raíz pública `dist/`:

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en 9d76947 | 0 | release 450/450, axe 80/80, tarjeta 58/58, velocidad 122/122 (112 de carga y 10 toques), visual 37/37, óptica 22/22; reportes en 878ec1b |
| las cinco suites de `tests/architecture/browser_*.py` en 9d76947 | 0 | todas en verde |
| `pytest -q` en 878ec1b | 0 | 896 pasan, 1 omitida (`test_editorial_contracts.py`: `wiki-tecnicas.html` no usa Schlick) |
| `pytest tests/architecture -q` | 0 | 344 pasan, 1 omitida (la misma) |
| `verify_architecture.py` (con el escaneo de privacidad), `verify_release.py` (mínimos: tarjeta 58, velocidad 122) | 0 | `checks_failed: []` |
| `ruff … C901` a 10 | 0 | limpio |
| `regenerate_all.py && git diff --exit-code` | 0 | sin diferencias |

El primer cierre, sobre un commit local que luego se rehízo, falló en la suite de release:
«field_card 320 nothing cut off at the edges: label.fc-tab «▦Encuadre» label runs out 61>58»,
por la pila de fuentes con `system-ui` primero. Se deshizo ese cambio y el cierre de arriba
corrió entero sobre el commit nuevo.

Sin fallos abiertos.

Verificación independiente: el red team revisó 9e2d121 (`qa/FINDINGS_PR22.md`) y reprodujo
V09, V12 y los anillos de foco; rechazó X06 por no medir lo que el PR aplazó (R1, abajo). El hilo de comprobación
en vivo dejó dos notas sobre 9cd348d (`qa/LIVE_CHECK_PR21.md`): los dos botones de lista son de
peso 600, como `.fc-reset` en la tarjeta sola, que es como se diseñaron; y axe marca a 390 px un
aviso de un plan que está bajo `content-visibility:auto` sin pintar, un falso positivo que la
suite de axe no ha dado.

### Rechazo del red team: X06 no medía lo que este PR aplazó (R1, `qa/FINDINGS_PR22.md`)

El red team revisó PR #22 en 9e2d121 y lo dejó en «no listo» por un solo rechazo, R1 (medio).
Todo lo demás lo reprodujo de forma independiente:

- V09: el inicio con una memoria envenenada en cada clave, y con `window.LimaSun` lanzando un
  error. En main el botón muere; en el PR el diálogo se abre.
- V12: ninguna prosa en inglés fuera de `lang="en"`.
- `content-visibility` en las tomas: ningún anillo de foco recortado en 160 paradas de
  tabulador a 320 y 390 px.
- X06 sí ve un manejador lento.

R1: Event Timing termina en la primera pintura tras el toque, y este PR había hecho de esa
pintura la barra y la cabecera; los planes llegaban en una tarea posterior que nadie medía.
Un bucle de 800 ms dentro de esa tarea pasaba X06 (40 ms) con la tarjeta vacía 0.8 s.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X06 (R1) | Lo que cada toque viene a mostrar está en pantalla dentro de las mismas marcas que la respuesta (200 ms en gama media, 500 en gama baja); lo que nunca aparece falla por nombre; el instrumento demuestra antes que ve contenido aplazado | el X06 de 9e2d121 sobre el mutante del red team (800 ms aplazados dentro de `openFieldCard()`): «open the field card answers» pasa con 56 y 288 ms, y no hay nada más que mirar. Sobre una página que responde enseguida y muestra su contenido 300 ms después, ve 16 ms. Con la medición nueva, el contenido de la tarjeta de 9e2d121 llegaba **después** que antes del PR: 525 frente a 484 ms en gama baja, en la misma calibración | el X06 nuevo falla el mutante: los planes en pantalla a 891 y 1087 ms, mientras la respuesta sigue pasando (64 y 200). Su propia comprobación ve 16 y 313 ms en la página de prueba. En `PERF_BUDGET_QA.json` sobre 46f04db: 133/133; los planes de la tarjeta en pantalla a 104 y 392 ms (gama media 2.07×, baja 7.88×), con la respuesta a 72 y 256; el razonamiento de una toma a 77 y 230; el nombre del plan, los ajustes de la luz y la marca, por debajo de 150 ms en gama baja. Una prueba unitaria nueva cubre la respuesta rápida con el contenido tarde y el contenido que nunca llega |

**Cómo se mide lo que el toque viene a mostrar.** Cada toque nombra su objetivo: los planes
de la tarjeta, el razonamiento de la toma, el nombre del plan, los ajustes de esa luz o la
marca. El tiempo lo da Element Timing: la prueba etiqueta con `elementtiming` lo que coincide
con el objetivo, también lo que la página añada después. Su `renderTime` en Chromium coincidió
con Event Timing con 0–6 ms de diferencia cuando los dos caen en el mismo cuadro: 168/172,
96/94 y 144/144.

Una marca cambia algo ya pintado, así que no es primera pintura. Para ella cuenta el primer
cuadro en que el objetivo se ve y, si está en pantalla, se dibuja (`checkVisibility` con
`contentVisibilityAuto`); se mide al terminar ese cuadro.

La primera versión medía así todos los toques, y leía de menos y de más. Por eso se cambió a
Element Timing.

**Dónde se iba el tiempo.** Trazas a gama baja (unas 7×):

- La tarea del toque costaba 213–251 ms. El estilo era de 380 elementos, unos 300 de ellos
  la página de atrás al volverse `inert`, y el diseño de 146 objetos.
- La tarea aplazada hacía dos pasadas de estilo y diseño. La segunda pasada eran las dos
  primeras tomas, que `content-visibility:auto` dibuja por estar cerca de la pantalla
  aunque empiezan debajo (a 931 px en una de 844).
- En Linux, cada nombre de fuente que el sistema no tiene (`-apple-system`,
  `BlinkMacSystemFont`, `Segoe UI`, `Roboto`) cuesta una búsqueda. Con «Arial» sola el
  contenido bajaba de 484 a 352 ms.

Tres cambios:

- **`system-ui` primero en la pila de la tarjeta**, como ya empieza el resto del sitio. En
  un teléfono es la misma fuente; en Linux es DejaVu Sans, más ancha.
- **Las pestañas son iguales salvo que ninguna es más estrecha que su palabra**
  (`repeat(5,1fr)`): a 320 px «Encuadre» ocupa 63 px en vez de cortarse en 58. Así se
  resolvió lo que hizo deshacer el mismo cambio de fuente en el primer cierre de esta ronda.
- **Las tomas se dibujan un cuadro después de los planes** (`fc-modal-later`).

Lado a lado, en una calibración (gama media 2.03×, baja 7.91×), siete visitas
alternadas, los planes de la tarjeta en pantalla:

| Build | Responde (gama media / baja) | Planes en pantalla (gama media / baja) |
|---|---|---|
| antes del PR (1f72869) | 104 / 480 ms | 104 / 484 ms |
| 9e2d121 | 64 / 280 ms | 123 / 525 ms |
| 46f04db | 64 / 248 ms | 100 / 342 ms |

El mensaje del commit 46f04db cita 466 frente a 428 ms, de una calibración anterior; las cifras
de referencia son las de esta tabla.

Después de los planes queda una tarea larga, la de las tomas: 67–112 (de ellos 12–56 de bloqueo) ms en gama baja, contra
153–246 ms de la segunda tarea de 9e2d121. Un toque en ese hueco espera esa tarea (N2 del red
team).

**Notas del red team**

- N1: «la mitad del tiempo» era la primera pintura, no la tarjeta. Está corregido en este
  registro y en el PR; el README nunca lo dijo. El mensaje del commit 9d76947 ya está publicado y no se
  reescribe.
- N2: queda como compromiso, más corto.
- N3: buscar en la página e imprimir no se ejercitaron directamente; lo mismo aquí.

**Compromisos explícitos (R1)**

- La medición del contenido usa Element Timing, que sólo Chromium implementa. Las marcas se
  comprueban en Chromium, como el resto de X06.
- Las marcas para el contenido son las de INP (200/500 ms). Ninguna norma las fija para
  contenido aplazado. RAIL da hasta 1000 ms a un cambio de vista, y el red team propuso 400 y
  1000; aquí se eligieron las marcas más estrictas. En gama baja el margen es de un 22–32 %.
- `system-ui` primero cambia la fuente de la tarjeta en Linux (DejaVu Sans u otra, más ancha
  que Arial) y en un Android cuyo fabricante trae otra fuente de interfaz. El resto del sitio
  ya la usaba.
- En Linux la pestaña «Encuadre» es 6 px más ancha que las otras a 320 px.
- Las tomas tardan un cuadro más que los planes. En una pantalla grande, donde están a la
  vista al abrir, aparecen un cuadro después.
- El arreglo de fuentes ayuda sobre todo a la medición en Linux. Que en un teléfono la
  búsqueda de fuentes no pese es inferido, no medido.
- `inert` sigue costando unos 300 elementos de estilo al abrir. Se queda: es lo que saca la
  página de atrás del alcance del lector de pantalla y del tabulador.

**Referencias**

- Element Timing (MDN `PerformanceElementTiming.renderTime`; WICG).
- RAIL (web.dev/articles/rail): una respuesta se nota inmediata en 100 ms; 100–1000 ms es «un
  flujo natural» para cambiar de vista.
- Ceder el hilo para pintar antes (web.dev/articles/optimize-inp).
- CSS Containment 2: `content-visibility:auto` dibuja lo que está cerca de la pantalla, con
  un margen que fija el navegador.

**Errores propios**

- Medí y anuncié «la mitad del tiempo» con Event Timing sin preguntar qué mostraba ese
  cuadro.
- La primera versión de la medición del contenido medía «dibujado en el hilo principal» y
  leía de menos (sin rasterizar ni presentar) o un cuadro tarde. Se cambió a Element Timing
  antes de usarla.
- Las primeras variantes de fuentes, una corrida de cinco por variante, tenían ±50 ms de
  ruido. Las cifras de arriba son lado a lado con visitas alternadas.

Escalada de investigación: no se activó; ningún arreglo falló. Las referencias de Element
Timing y RAIL se consultaron antes de fijar la medición y las marcas.

**Cierre de R1** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en 46f04db | 0 | release 450/450, axe 80/80, tarjeta 58/58, velocidad 133/133 (112 de carga, la comprobación del instrumento y 20 de toques), visual 37/37, óptica 22/22; reportes en 34af0b2 |
| las cinco suites de `tests/architecture/browser_*.py` en 46f04db | 0 | todas en verde; la de release redibuja su captura sin conexión |
| `pytest -q` en 34af0b2 | 0 | 897 pasan, 1 omitida (la misma) |
| `pytest tests/architecture -q` | 0 | 344 pasan, 1 omitida |
| `verify_architecture.py`, `verify_release.py` (velocidad 133) | 0 | `checks_failed: []` |
| `ruff … C901` a 10 | 0 | limpio |
| `regenerate_all.py && git diff --exit-code` | 0 | sin diferencias |

El CI de 9e2d121 (corrida 39472882922) pasó sus ocho trabajos antes de este arreglo.

Verificación independiente de R1: el red team la repitió sobre 2504c13 con sus propias pruebas
(`qa/FINDINGS_PR22.md`, «Recheck at 2504c13») y cerró R1; el PR pasa.

- Sin mutante, X06 da 40–64 ms la respuesta y 66–93 ms los planes, sin limitar la CPU. Con su
  mutante de R1, 32–40 y 849–854 ms, y falla. Con 800 ms justo antes de mostrar los planes, 40
  y 860 ms, y falla. La comprobación propia da 16 y 318 ms.
- No hay lectura temprana: los planes están dentro del panel aplazado. Retrasar los planes
  mueve «en pantalla» y deja «responde» igual.
- En su calibración (1.69× y 5.92×), los planes llegan a 107–139 ms en gama media y a 289–529
  ms en gama baja, con mediana 345, frente a 352–473 en 9e2d121 y 392–465 en main. Una de cinco
  visitas pasó de 500; X06 juzga la mediana, así que espera un fallo raro en CI, no uno fijo.
- Con `system-ui` (Inter allí) y las pestañas nuevas no hay desplazamiento horizontal ni texto
  cortado a 280, 320 y 360 px. main cortaba «Técnicas» y «Encuadre» a 280. Los anillos de foco
  y «Siguiente toma» siguen bien.

Notas nuevas, no bloqueantes:

- N4: el paso de las tomas no se mide. 800 ms antes de mostrarlas pasa X06 (47–61 ms), porque
  sólo se miden los planes. A 390×844 da igual: la primera toma empieza a 950 px, bajo la
  pantalla. Pero asoma a 412×915 (4 px), 430×932 (78 px), 768×1024 (264 px) y 1440×900 (50 px),
  y allí un paso lento de las tomas no se vería.
- N5: «en pantalla» toma el primer objetivo que se pinta. Si un cambio mostrara un plan antes
  y los demás tarde, pasaría. Hoy los planes se muestran juntos.

### N4 del red team: la primera toma a ancho de tableta, y la página de atrás sin dibujar

N4 decía que el paso de las tomas no se medía: X06 sólo miraba los planes, y 800 ms antes de
mostrar las tomas pasaban. Pablo aún no ha decidido si PR #22 se fusiona antes. Este trabajo
está en commits locales sobre be41f3e (48bfd4d, 11e9484 y los reportes en 892ec8b) y va donde
él decida.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X06 (N4) | Abrir la tarjeta a 768×1024, donde la primera toma ya se ve al abrir, responde y muestra esa toma dentro de las mismas marcas | el X06 de be41f3e sobre el mutante de N4 (800 ms antes de quitar `fc-modal-later`): 9/9 pasan. Las dos pruebas unitarias de X06 que se ampliaron fallan contra el módulo anterior | el X06 nuevo falla ese mutante: la primera toma a 922 ms en gama media y 1270 en gama baja, mientras la respuesta pasa (80 y 264). En el build real, 148 y 384 ms. `PERF_BUDGET_QA.json` sobre 11e9484: 137/137 |
| X06 (página de atrás) | Por debajo de 900 px, con la tarjeta abierta, la página de atrás no se dibuja; vuelve donde estaba, se imprime y a 1280 px sigue dibujada | sobre 46f04db, «no se dibuja y vuelve donde estaba» falla: se dibuja (`[True, 2400]` abierta). Imprimir y 1280 px pasan | 61/61 en `FIELD_CARD_QA.json`. Sin `screen` en la regla, falla «imprimir con la tarjeta abierta imprime la página». Sin `contain-intrinsic-size:auto none`, falla la primera: la página vuelve a 0 en vez de 2400 |

**Por qué se cambió el producto y no sólo la medición.** Con la primera toma medida, en
48bfd4d quedó a 384–477 ms de mediana en gama baja, según la calibración, y 2 o 3 de cada 5–7
visitas pasaban de 500. Así el control habría fallado en CI de vez en cuando.

La traza a 768×1024 y 7.57× dio:

- La tarea del toque costaba 209–239 ms. De ellos, 80–123 eran de estilo para 365 elementos
  (la página al volverse `inert`) y 85–91 de diseño.
- Los planes costaban unos 100 ms.
- Las tomas costaban otros 100 ms, en dos pasadas por `content-visibility:auto`.

Variantes a 7.04×, siete visitas alternadas, primera toma en gama baja:

| Variante | Primera toma |
|---|---|
| tal cual | 477 ms |
| planes y tomas en el mismo paso | 439 ms |
| sin `inert` (diagnóstico, no se envía) | 391 ms |

A 6.83×:

| Variante | Primera toma en tableta | Planes en el teléfono |
|---|---|---|
| tal cual | 404 ms | 318 ms |
| página de atrás oculta | 348 ms | 252 ms |
| oculta, y planes y tomas en el mismo paso | 304 ms | 270 ms |

Se eligió sólo ocultar. Juntar planes y tomas empeora el teléfono y deshace lo que R1 separó.

**El cambio.** La tarjeta cubre toda la pantalla por debajo de 900 px, así que mientras está
abierta los hijos de `body` salvo el diálogo llevan `content-visibility:hidden`. Siguen
`inert`. Las reglas en `scripts/integrate_field_card.py` son:

- `:where(body>*){contain-intrinsic-size:auto none}`: cada parte recuerda su último tamaño, sin
  especificidad para no pisar ninguna regla;
- `@media screen and (max-width:899px)`: imprimir con la tarjeta abierta imprime la página.

**Lado a lado** (46f04db contra 11e9484, una calibración por fila, siete visitas alternadas):

| Toque | Antes (gama media / baja) | Después (gama media / baja) |
|---|---|---|
| abrir la tarjeta en un teléfono: responde | 56 / 240 ms | 48 / 168 ms |
| abrir la tarjeta en un teléfono: planes en pantalla | 91 / 339 ms | 80 / 235 ms |
| abrir a 768×1024: responde | 80 / 248 ms | 64 / 192 ms |
| abrir a 768×1024: primera toma en pantalla | 146 / 405 ms | 107 / 362 ms |
| cerrar en un teléfono | 24 / 80 ms | 24 / 104 ms |
| cerrar a 768×1024 | 32 / 112 ms | 32 / 112 ms |

Las calibraciones fueron de 1.88 a 2.09× y de 7.42 a 7.72×. Tras cerrar, la página siguió
en 2400 en todas las visitas. En `PERF_BUDGET_QA.json` sobre 11e9484, con una calibración más
lenta (1.65× y 8.18×):

- abrir la tarjeta responde a 40 y 176 ms y muestra los planes a 62 y 283;
- a ancho de tableta responde a 48 y 216 y muestra la primera toma a 95 y 409 (como máximo
  480).

**Compromisos explícitos (N4)**

- Cerrar la tarjeta en un teléfono de gama baja cuesta algo más: 104 ms en vez de 80, porque
  la página de atrás se vuelve a dibujar. Sigue dentro de «bueno».
- A ancho de tableta en gama baja, la primera toma queda a 362–409 ms de mediana: un margen
  del 18–28 % hasta 500. Una calibración lenta puede acercarla. El control juzga la mediana.
- La tableta se mide con la CPU de los teléfonos de referencia, no con la de una tableta.
- Por debajo de 900 px, con la tarjeta abierta, la página de atrás no se dibuja. No se ve,
  porque la tarjeta la cubre, y ya era `inert`. Safari anterior a 18 no conoce
  `content-visibility` y se queda como antes.
- N5 no se construye. Que «en pantalla» espere a todos los planes exige saber cuáles
  aparecerán, y eso sólo se sabe esperando una ventana fija en cada toque. Hoy los planes se
  muestran juntos con una sola clase.

**Referencias**

- CSS Containment 2: `content-visibility:hidden` salta el estilo, el diseño y la pintura del
  contenido.
- CSS Box Sizing 4: el «último tamaño recordado» con `contain-intrinsic-size:auto`.
- web.dev, «content-visibility: the new CSS property that boosts your rendering
  performance».

Escalada de investigación: no se activó; ninguna hipótesis de arreglo falló.

**Cierre de N4** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en 11e9484 | 0 | release 450/450, axe 80/80, tarjeta 61/61, velocidad 137/137, visual 37/37, óptica 22/22; reportes en 892ec8b |
| las cinco suites de `tests/architecture/browser_*.py` en 11e9484 | 0 | todas en verde |
| `pytest -q` en 892ec8b | 0 | 897 pasan, 1 omitida (la misma) |
| `verify_release.py` (tarjeta 61, velocidad 137), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10 | 0 | limpio |
| `regenerate_all.py && git diff --exit-code` | 0 | sin diferencias |

Verificación independiente de N4: el red team aplicó los cuatro parches sobre be41f3e y los
pasó (`qa/FINDINGS_PR22.md`, «N4 follow-up»).

- Sin limitar la CPU, a 768×1024, el mutante de N4 da 875–892 ms la primera toma y falla. Sin
  mutante, 87–110 ms.
- Nada de lo que queda sin dibujar tras la tarjeta hace falta por debajo de 900 px: el enlace
  para saltar, la barra de arriba, `main`, el pie con `#diag`, los dos diálogos y la barra de
  abajo. Ningún diálogo contiene un botón que abra la tarjeta.
- Con la tarjeta cerrada, el diseño y la altura del documento son idénticos a 2504c13 a 390 y
  1280 px.
- Al cerrar, la página vuelve exacta desde 2400 y desde 9000.
- En su calibración, los planes en gama baja pasan de 475 ms (2504c13, 8.07×) a 336 (7.14×).

Sus notas: N6 es el compromiso de cerrar, ya declarado. N7 era previa: tras un cambio de ancho
que oculta el botón con que se abrió la tarjeta, el foco volvía al principio de la página.

**N7, arreglada en d40bf8f.** Al cerrar, el foco vuelve al botón que abrió la tarjeta si sigue
a la vista; si no, al primer botón de la página que la abre. Un navegador sin
`checkVisibility` se queda como antes.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| N7 | Abierta desde la barra de abajo a 390 px y cerrada con Escape tras pasar a 1280, el foco cae en un botón que abre la tarjeta y está a la vista | sobre 11e9484: `[None, True]`, el foco no queda en ningún botón de la tarjeta | `['openFieldCard()', True]`; 62/62 en `FIELD_CARD_QA.json` |

**Cierre de N7** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en d40bf8f | 0 | release 450/450, axe 80/80, tarjeta 62/62, velocidad 137/137, visual 37/37, óptica 22/22; reportes en 44b526e |
| las cinco suites de `tests/architecture/browser_*.py` en d40bf8f | 0 | todas en verde |
| `pytest -q` en 44b526e | 0 | 897 pasan, 1 omitida |
| `verify_release.py` (tarjeta 62), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre d40bf8f (2.24× y 7.73×), abrir la tarjeta responde a 48 y 176 ms
y muestra los planes a 76 y 251. A ancho de tableta responde a 64 y 224 y muestra la primera
toma a 131 y 427.

### N8 del red team: el foco de N7 movía la página

El red team revisó N7 en 56c87cb. El foco vuelve, pero el arreglo introdujo N8: al enfocar el
botón de reserva, la página se desplazaba hasta él. Se había abierto en 2400 y, tras cruzar los
900 px, cerraba en 908 o en 1174, y el lector perdía su sitio. La prueba de N7 no lo vio por dos
motivos: no comprobaba el desplazamiento y no esperaba al desplazamiento suave de la página.

Arreglo (ba38fce):

- Al cerrar, si el botón que abrió la tarjeta sigue a la vista, recibe el foco como antes.
- Si no, el foco va a un botón que esté en pantalla, como la barra de abajo del teléfono.
- Si no hay ninguno en pantalla, va al primero de la página, con `preventScroll`, para que la
  página quede donde estaba.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| N8 | Abierta en 2400, cruzando 900 px hacia arriba (390→1280) y hacia abajo (1280→600), al cerrar el foco cae en un botón a la vista que abre la tarjeta y la página no se mueve (tras esperar 1 s al desplazamiento suave) | sobre d40bf8f: de 2530 a 0, y de 2400 a 1805 | 2530 y 2400 se mantienen. A 600 px el foco cae en la barra de abajo, en pantalla. A 1280 px cae en el botón de la barra de arriba, fuera de la pantalla y sin desplazarla. 63/63 en `FIELD_CARD_QA.json` |

Compromiso: a 1280 px, sin ningún botón en pantalla, el foco queda en uno fuera de la vista.
Con el siguiente Tab el navegador lo trae a la vista. Se prefirió a mover la página.

**Cierre de N8** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en ba38fce | 0 | release 450/450, axe 80/80, tarjeta 63/63, velocidad 137/137, visual 37/37, óptica 22/22; reportes en 82a195a |
| las cinco suites de `tests/architecture/browser_*.py` en ba38fce | 0 | todas en verde |
| `pytest -q` en 82a195a | 0 | 897 pasan, 1 omitida |
| `verify_release.py` (tarjeta 63), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre ba38fce (1.94× y 7.45×):

- abrir la tarjeta responde a 48 y 200 ms y muestra los planes a 74 y 285;
- a ancho de tableta responde a 64 y 224 y muestra la primera toma a 109 y 419, con una visita
  de 673 en gama baja.

El CI de 56c87cb pasó sus ocho trabajos (corrida 39503165850).

Verificación independiente de N8: el red team la pasó sobre ce97ab9 («N8 fix at ce97ab9»).
Esperó 1.5 s tras Escape y comprobó lo siguiente:

- De 600 a 1280 px, la página queda en 2400 (en 56c87cb iba a 908) y el foco cae en el botón
  de la barra de arriba.
- De 1280 a 600 px, la página queda en 2400 (en d40bf8f iba a 1808) y el foco cae en la barra
  de abajo, que está en pantalla.
- Sin cambio de ancho, nada cambia.
- Aceptó el compromiso de dejar el foco fuera de la pantalla a 1280 px sin moverla.

Nota nueva, N9, previa y ya en main: la barra de arriba (`nav.glass`, `sticky top-0`) nunca se
queda fija. `<style id="iphone-safe-overrides">` en `index.html` pone `overflow-x:hidden` en
`html` y `body`. Eso hace de `body` un contenedor de desplazamiento que nunca se desplaza, y
anula el `overflow-x:clip` anterior. Con `clip`, la barra se queda arriba sin desplazamiento
horizontal. Antes hay que decidir si en el teléfono debe quedarse fija, porque ya tiene la barra
de abajo; si no, se quita `sticky`.

### Fallo propio en X06: la marca de una toma sólo se encontraba de día

La tarjeta de campo se abre en la luz que dice el reloj de Lima (día, tarde o noche). Cada toma
tiene una marca por luz y sólo se ve la de la luz actual. El toque «tick a shot» de X06 buscaba
la marca del día, así que de 18:00 a 06:00 en Lima no encontraba nada que tocar y la suite de
velocidad fallaba con «nothing to tap» (visto el 2026-10-20 a las 18:40).

Arreglo (630a1df):

- El toque busca la marca visible de la toma visible, sea cual sea la luz.
- El instrumento suma una comprobación: en la tarjeta, elige cada luz y falla si algún toque no
  encuentra en pantalla lo que toca. `PERF_BUDGET_QA.json` pasa de 137 a 138 comprobaciones.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X06 | Cada toque de la tarjeta encuentra lo que toca en las tres luces en que puede abrirse | sobre 74e22c7, `--only field_card.html` a las 18:40 de Lima: «tick a shot: nothing to tap». Con el reloj fijado hora a hora, el selector viejo se ve de 06:17 a 17:30 y no a las 18:00 ni de 18:30 a 05:00. La comprobación nueva con el selector viejo falla en la luz de tarde y en la de noche | el selector nuevo se ve a todas las horas y la comprobación pasa; 138/138 a las 19:00 de Lima sobre 630a1df. La prueba unitaria, con una tarjeta falsa en la que sólo se ve la marca del día, falla por luz con el selector viejo |

Compromisos:

- La luz se elige tocando la tarjeta, no fingiendo el reloj, así que la medición sigue con la
  hora real y lo que mide es la luz en que se abre a esa hora.
- Sólo se comprueban los toques de la tarjeta, la única página que cambia con la hora.

Errores propios: escribí el selector de la marca del día en PR #22, y subí el código (630a1df)
antes del reporte, así que el CI de 630a1df quedó en rojo («137 checks, expected at least 138»)
hasta ba7d315. La escalada de investigación no se activó: la primera hipótesis fue la buena.

**Cierre** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| suite de velocidad en 630a1df | 0 | 138/138; reporte en ba7d315. La marca responde a 24 y 80 ms y se ve a 23 y 82; a ancho de tableta la primera toma, a 119 y 311 |
| `pytest -q` en ba7d315 | 0 | 898 pasan, 1 omitida |
| `verify_release.py` (velocidad 138), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10 | 0 | limpio |

Las demás suites no cambian: el arreglo sólo toca el instrumento de velocidad.

Verificación independiente: el red team pasó 09c44bc (`qa/SPOTCHECK_LOG.md`, 2026-10-21 00:30
UTC). `field_card_qa.py` da 63/63 en las tres luces: a la hora real (19:30 en Lima, noche) y con
el reloj de cada contexto fijado a las 10:00 y a las 17:40 de Lima. Con el selector viejo el
toque de la marca no encuentra nada de noche; con el nuevo responde a 16 ms. Los recuentos del
README coinciden con los seis reportes.

### N9: las barras de arriba se quedan sólo donde caben

Pablo tiene la pregunta de si las barras deben quedarse fijas también en el teléfono. Mientras
responde se construye la opción recomendada: sólo en pantallas grandes.

Qué había:

- En el inicio, `overflow-x:hidden` en `html` y `body` hacía de `body` un contenedor de
  desplazamiento, así que ni la barra del sitio ni la barra Sujeto/Hora se quedaban arriba en
  ningún tamaño.
- En los planes las dos sí se quedaban, también en el teléfono, donde tapaban de un quinto a
  más de un tercio de la pantalla (de 136 a 201 px, en pantallas de 390 a 932 px de alto).

Arreglo (f92bd71, d6733b4 y 7494f49, sobre PR #22):

- `overflow-x:clip` en lugar de `hidden`: no deja que la página se desplace de lado y no crea un
  contenedor. Un navegador sin `clip` recibe `hidden` por `@supports` y se queda como antes.
- Las dos barras se quedan arriba desde 641 px de ancho (donde ya no hay barra de abajo) y
  500 px de alto (no es un teléfono de lado). Por debajo, `top:auto` hace que `sticky` se
  comporte como `relative` sin desplazamiento (MDN), y las barras se quedan en su sitio.
- `scroll-padding` en `html` (técnica C43 de WCAG) deja el foco y los saltos de los enlaces
  internos fuera de lo que se queda: arriba donde están las barras y abajo donde está la barra
  del teléfono. Una sección anterior a la barra Sujeto/Hora sólo tiene encima la del sitio, y
  `:has()` le quita esa diferencia.
- Al cerrar la tarjeta de campo, si el botón que la abrió está en pantalla, recibe el foco con
  `preventScroll`. Con `scroll-padding`, un botón dentro de una barra fija cae en la zona
  reservada, el navegador lo da por fuera de la vista y desplazaba la página
  (csswg-drafts#7930).

Comprobación nueva, X07 (`scripts/fixed_bars.py`, en `CURRENT_BROWSER_QA.json`, de 450 a 484):
en el inicio servido y suelto y en los seis planes, a los siete tamaños, qué se queda y dónde,
Tab y Mayús+Tab por toda la página midiendo lo que el navegador dibuja encima del foco, cada
enlace interno de las barras y, en el inicio, que cerrar un diálogo no mueva la página.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X07 | Las barras se quedan arriba sólo desde 641×500, una bajo la otra; en el teléfono se van y la de abajo se queda; nada que reciba el foco ni el comienzo de una sección enlazada queda detrás; cerrar un diálogo no mueve la página | sobre 74e22c7, el inicio suelto falla a 820×1000 y 1440×1100: «the top bar scrolled away (top −11218)» | 484/484 sobre 7494f49 |

Mutantes (cada uno sobre el arreglo, con una pieza quitada o cambiada):

| Mutante | Qué detecta X07 |
|---|---|
| `relative` en lugar de `top:auto` | la barra pisa la sección siguiente 72 px (inicio) o 64 px (planes) en los cinco tamaños de teléfono, y en los planes tapa un enlace al tabular |
| sólo `clip`, sin límite de tamaño | las barras se quedan en el teléfono |
| sin `scroll-padding` | controles tapados en parte o del todo al tabular hacia delante y hacia atrás, por la barra de abajo en el teléfono y por las de arriba desde 820 px; en los planes, el salto a `#contenido` cae detrás de la barra |
| sin `:has()` | tres secciones del inicio caen 148 px más abajo, con sólo 65 px de barra encima |
| el cierre de la tarjeta de N8 | la página se mueve −256 px a 820×1000 y −581 a 1440×1100 |

En el teléfono la página no cambia: comparando 74e22c7 con el arreglo, ninguna de las 5651
cajas del inicio ni de las 591 de un plan cambia de sitio ni de tamaño a los cinco tamaños de
teléfono.

Compromisos:

- Sólo se probó en Chromium. Safari necesita la versión 16 para `clip`; uno más viejo recibe
  `hidden` y barras que se van.
- En una ventana de portátil de 500 a 650 px de alto las barras se quedan y ocupan de un quinto
  a un cuarto de la pantalla.
- Las páginas del concurso tienen su propia barra fija, más delgada (del 7 al 16 % de la
  pantalla), y no se tocaron.
- Las barras se miden con JavaScript (N11, abajo). Sin JavaScript, el espacio que se reserva
  es el de los valores en `rem`: exacto con el texto de 16 px y, con texto más grande, de 27 a
  42 px de más (el mutante sin el script, abajo).
- El compromiso de N8 («a 1280 px el foco queda en un botón fuera de la vista») casi desaparece:
  desde 641×500 el botón de la barra de arriba está en pantalla. Sigue en ventanas de menos de
  500 px de alto.

Errores propios:

- Primero usé `position:relative` en el teléfono: conservaba el desplazamiento de `top` y la
  barra pisaba lo de abajo de 64 a 72 px. Lo detectó la comprobación por lo que se dibuja
  encima. Como la hipótesis falló, se activó la escalada de investigación: MDN dice que `sticky`
  con todos los lados en `auto` se comporta como `relative` sin desplazamiento.
- Probé un `scroll-margin` negativo para el salto al cerrar la tarjeta. Funcionaba en el inicio
  y no en los planes (+10 o −444 px), así que lo quité y usé `preventScroll`.

Fuentes: WCAG 2.2 SC 2.4.11 y 2.4.12 y la técnica C43; Nielsen Norman Group sobre barras
fijas; MDN sobre `position: sticky` y `overflow: clip`; csswg-drafts#7930.

Revisión del red team (`qa/FINDINGS_PR22.md`, «N9 red team at 8dde4df»): PASS sobre los
parches 0001–0005. Comprobó los saltos a seis tamaños con un mutante sin `scroll-padding` que
falla 12 de 12, la regla `:has()`, los bordes 640/641 y 499/500 y que en el teléfono ninguna caja
cambia. Dejó dos notas:

- N10 (moderada, previa y en main): a 1280–1920 px, «▶ Sesión», «📋 Tarjeta» y «PDF» quedan
  fuera del final de la fila de la barra de arriba, y el foco de teclado cae en Sesión sin que se
  vea. No la causa N9; queda para el PR siguiente.
- N11 (menor, nueva con N9): con el texto del lector más grande, la barra Sujeto/Hora crece y
  el espacio fijo en `rem` no basta.

**N11, arreglada en 94041f4.** Con texto de 20 px, de 641 a unos 660 px de ancho, la barra
Sujeto/Hora pasa a dos líneas (124 px) y un salto o el foco podía quedar 19 px detrás; con 24 px,
hasta 769 px de ancho, 4 px. Además, ninguna de las dos barras crece al mismo ritmo que el texto,
así que con texto grande el espacio reservado quedaba de 27 a 42 px por debajo de ellas.

- El sitio para las barras se mide en `em` (40.0625 por 31.25 em, 641 por 500 px con 16 px).
  Con texto más grande las barras, más altas, sólo se quedan en pantallas más grandes, y ocupan
  la misma parte de la pantalla que con 16 px.
- Un script después de la barra Sujeto/Hora mide las dos barras con `ResizeObserver` y escribe
  `--fr-nav` y `--fr-bar`, que dan el `scroll-padding`, la posición de la barra Sujeto/Hora y el
  margen de las secciones de encima. Sin el script quedan los valores en `rem`.
- X07 suma una pasada con el texto del lector a 20 y 24 px (Chrome «Grande» y «Muy grande»,
  `Page.setFontSizes`) a 650×800, 700×800, 1024×768 y 1280×800, en las ocho páginas.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| N11 | Con texto de 20 y 24 px, las barras se quedan sólo donde caben, nada que reciba el foco queda detrás y cada salto cae a 24 px como mucho bajo ellas | sobre 523ff43: en el inicio, a 20 px y 650×800 y a 24 px y 700×800 las barras se quedan; a 24 px el lienzo de composición queda 4 px detrás al tabular hacia atrás; a 1024×768 y 1280×800 los saltos caen de 27 a 42 px bajo las barras. En los planes, las barras se quedan a 650 y 700 px | las ocho páginas pasan a los cuatro tamaños. `sweep.py` del red team: 0 de 414 casos malos (antes, los de 641–660 px a 20 px y hasta 769 a 24 px) |

Mutante sin el script: con texto grande, los saltos vuelven a caer de 27 a 42 px bajo las barras
a 1024×768 y 1280×800, en el inicio servido y en el suelto.

Fuentes de N11: Tab Atkins, editor de Media Queries, en www-style (agosto de 2012): `em` y `rem`
en una consulta de medios se basan en el tamaño de letra por defecto del lector, no en el del
elemento raíz; el código de Chromium (`appearance_page.ts`): «Grande» es 20 px y «Muy grande»
24 px; el protocolo de DevTools (`Page.setFontSizes`); Resize Observer (W3C).

**«La página no se mueve», medida por lo que se ve (fdca8e7).** Las suites sobre 94041f4
fallaron dos comprobaciones que leían `scrollY`: en X07, cerrar la tarjeta abierta desde la barra
de arriba a 820×1000 «movía» la página 203 px (sólo en el inicio suelto), y en la tarjeta, tras
pasar de 1280 a 600 px, `scrollY` pasaba de 2400 a 2392. La primera hipótesis, que el script de
N11 movía la página, era falsa:

- Al volver a dibujar la página detrás de la tarjeta cambian tamaños de más arriba, y el
  navegador mantiene quieto lo que se ve cambiando `scrollY` (anclaje del desplazamiento, activo
  desde que N9 dejó `body` de ser un contenedor). A 600 px la barra del sitio pasa de 65 a 57 px:
  `scrollY` baja 8 y el párrafo del centro sigue en 1812 px.
- Con `scrollY` la prueba dependía del momento: en la réplica, el mismo build de N9 (7494f49)
  da 2400 o 2392 según pasen o no 100 ms tras el desplazamiento.

Ahora las dos comprobaciones siguen el elemento del centro de la pantalla, elegido 300 ms después
de saltar, cuando las secciones que sólo se dibujan cerca de la pantalla ya tienen su tamaño, y
fallan si se mueve.

| Comprobación | RED | GREEN |
|---|---|---|
| X07, cerrar un diálogo abierto desde la barra | el cierre de N8 (sin `preventScroll` en pantalla): la tarjeta mueve lo que se ve 536 px a 820×1000 y de 586 a 910 a 1440×1100 | 94041f4 y 7494f49: quieto, dos corridas por tamaño, inicio servido y suelto |
| Tarjeta, cerrar tras cruzar 900 px | el cierre de N7 (d40bf8f): lo que se ve se mueve 306 px (390→1280) y 631 (1280→600) | 94041f4 y 7494f49: quieto, tres corridas en cada sentido |

Investigación tras la hipótesis fallida. Fuentes: CSS Scroll Anchoring Module Level 1 (W3C): el
navegador ajusta la posición de desplazamiento para compensar cambios fuera de la vista, con un
nodo ancla cerca del borde de arriba, y salta los elementos `fixed` y `sticky`; MDN y web.dev sobre
`content-visibility:auto`: una sección lejos de la vista ocupa el tamaño de reserva de
`contain-intrinsic-size` hasta que se acerca y se dibuja. Parecido y diferencia: la norma habla de
cualquier caja con desplazamiento; aquí es el documento, que ancla desde que N9 quitó
`overflow-x:hidden` de `body`. Lo que cambió la hipótesis: el build de N9 sin el script (7494f49)
también cambiaba `scrollY`, y el párrafo del centro no se movía. Predicción falsable: si la causa es
el anclaje, seguir el elemento del centro da 0 px con el cierre bueno y cientos con los cierres de
N7 y N8. Se cumplió (tabla de arriba).

Error propio de proceso: la búsqueda en línea se hizo después del arreglo, que salió de las
pruebas locales, y no antes del segundo intento como pide la regla. Las fuentes confirman la causa
y no cambian el arreglo.

Error propio en esta medida: la primera versión elegía el elemento justo después del salto, antes
de que se dibujaran las secciones con `content-visibility:auto`, y daba movimientos falsos de 279
a 824 px en los dos builds. Con la espera de 300 ms desaparecen.

Compromisos de N11:

- La medida exacta depende de JavaScript; sin él quedan los valores en `rem`.
- Con texto más grande, de 641 a 800 px de ancho (20 px) o a 961 px (24 px), ninguna barra se
  queda arriba, ni la de abajo, que sólo existe hasta 640 px.

**Cierre de N9 antes de N11** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo
`dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en 7494f49 | 0 | release 484/484, axe 80/80, tarjeta 63/63, velocidad 138/138, visual 37/37, óptica 22/22; reportes en 47405fe |
| las cinco suites de `tests/architecture/browser_*.py` en 7494f49 | 0 | todas en verde |
| `pytest -q` en 47405fe | 0 | 907 pasan (898 y las 9 de `tests/test_fixed_bars.py`), 1 omitida |
| `verify_release.py` (navegador 484), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre 7494f49 (2.16× y 8.14×), abrir la tarjeta responde a 48 y 160 ms
y muestra los planes a 82 y 239. A ancho de tableta responde a 64 y 208 y muestra la primera
toma a 120 y 343. La barra fija no cambia ningún toque.

Error propio en el cierre: el primer commit de reportes no llevaba
`architectural_photography/state/CURRENT_STATE.json`, que `regenerate_all.py` pone al día con el
número de comprobaciones del navegador (de 450 a 484). `test_regenerating_leaves_the_tree_unchanged`
falló una vez (RED: «after: M architectural_photography/state/CURRENT_STATE.json») y pasó en las
ocho corridas siguientes, también con la CPU cargada. Pasaba sólo porque el archivo ya estaba
modificado antes de regenerar. Con el archivo devuelto a su versión del commit, la prueba vuelve
a fallar. Incluido en 47405fe, pasa (GREEN). El paso de CI `regenerate_all.py && git diff --exit-code` lo
habría detectado.

**Cierre de N9 con N11** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| las seis suites con reporte en fdca8e7 | 0 | release 492/492, axe 80/80, tarjeta 63/63, velocidad 138/138, visual 37/37, óptica 22/22; reportes en 4ff973b |
| las cinco suites de `tests/architecture/browser_*.py` en fdca8e7 | 0 | todas en verde |
| `pytest -q` en 4ff973b | 0 | 909 pasan (898 y las 11 de `tests/test_fixed_bars.py`), 1 omitida |
| `verify_release.py` (navegador 492), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre fdca8e7 (2.13× y 7.56×), abrir la tarjeta responde a 48 y 176 ms
y muestra los planes a 75 y 251. A ancho de tableta responde a 64 y 184 y muestra la primera
toma a 119 y 353. Los 24 toques siguen dentro de su presupuesto.

### N10, N13 y las notas del red team sobre N9 (1e8cbcd, 5532975)

El red team revisó la actualización de N9 (parches 0001–0009): N11 queda arreglada (PASS) y dejó
tres notas más, que se atienden aquí junto con N10 y un problema nuevo, N13, encontrado al
arreglar N10. Las tres notas: el espacio reservado no seguía al relleno de las barras, la prueba
del diálogo no veía un movimiento tardío, y los saltos a «Técnicas» con texto grande caían cortos
(su N12).

Nota sobre los nombres: al principio llamé N12 al problema de Tab en las barras, sin ver que el
red team ya había usado N12 para los saltos. El de Tab pasó a llamarse N13 en el código y aquí.

**N10: las herramientas de la barra de arriba, a la vista (X08, `scripts/top_bar_tools.py`).**
En una computadora la fila de la barra terminaba con «Modo sol», «▶ Sesión», «📋 Tarjeta» y «PDF», y
quedaban más allá del final de la fila: a 1280×800 «▶ Sesión» mostraba 0 de 82 px y a 820×1000 las
cuatro, 0 px. El foco de teclado podía caer en un control cortado por el difuminado del final de la
fila, también en el teléfono.

- Desde 40.0625 em (641 px con 16 px de texto) los enlaces de las secciones van en una fila propia
  que se desplaza de lado, y las herramientas quedan enteras después de ella. Debajo, las dos
  envolturas son `display:contents` y el teléfono queda igual que antes.
- De 641 a 1023 px la marca pierde «· San Isidro» y el subtítulo, y el enlace del concurso dice
  «Arquitectura».
- Cuando el foco entra en una fila, sólo esa fila se desplaza lo justo para mostrar el control
  entero; la página no se mueve. El difuminado del final se quita mientras el control con el foco
  no cabe sin él.
- X08, en los dos inicios: con la página arriba, las cuatro herramientas enteras en pantalla donde
  no hay barra de abajo (más de 640 px), y en cada control de la barra al que llega el foco con Tab,
  el control entero a la vista, sin pasar el final de su fila ni quedar bajo el difuminado.

**Controles encimados, medidos por lo que se dibuja (5532975).** La prueba de que nada queda cortado
en los bordes comparaba la caja entera de cada control. Con N10, un enlace desplazado fuera de la
fila de enlaces, que la fila esconde, contaba como encimado sobre las herramientas de al lado: 6
falsos a 844 px. Ahora cada control cuenta sólo por la parte que dejan dibujada las cajas que
recortan lo que se sale. Sobre 1e8cbcd: la prueba anterior marca 6, 6 y 4 encimados a 844, 1024 y
1280 px, y la nueva ninguno. Con las herramientas corridas 60 px sobre los enlaces, la nueva marca
los enlaces que tapan a los tres tamaños. Como sólo quita partes que no se ven, todo lo que marca
la nueva lo marcaba también la anterior.

**N13: Tab dentro de una barra fija movía la página.** Con `scroll-padding`, Chrome cuenta un control
dentro de una barra que se queda arriba como fuera de la vista. En cada Tab entre dos controles de
la barra desplazaba la página de 143 a 1454 px para centrarlo, y la barra, fija, seguía igual.
Ahora Tab y Mayús+Tab hacia un control de una barra entera en pantalla, desde dentro de la barra o
desde el control de al lado, mueven el foco con `preventScroll` desde `keydown`. Cualquier otro
movimiento, y cualquiera desde un diálogo o un botón de opción, sigue siendo del navegador. Está en
el inicio (`index.html`) y en los planes (`scripts/generate_plan_pages.py`).

Comprobación nueva en X07 (`tab_in_bars_leaves_page_still`): cada barra donde el lector la
encuentra (arriba fija, la Sujeto/Hora también justo bajo la de arriba y entera al pie de la
pantalla) se cruza con Tab y con Mayús+Tab, se sale de ella y se vuelve a entrar. Sólo la tecla que
sale puede desplazar la página. Se hace con el movimiento reducido y, con 16 px de texto, también
con el movimiento activado, que es lo que tiene la mayoría: entonces cada evento de desplazamiento
guarda lo más lejos que llegó lo que está en el centro de la pantalla, así que un movimiento que se
deshace después también cuenta.

**Notas del red team:**

- El espacio reservado sigue a las barras enteras: `ResizeObserver` mira ahora `border-box`. El
  relleno de la barra de arriba guarda el área segura del teléfono. X07 agranda el relleno de las
  dos barras (40 y 48 px) y exige que el espacio reservado lo siga en dos cuadros.
- La prueba del diálogo mira 300 ms después de cerrar y otra vez 900 ms más tarde.
- Saltos (su N12, más amplio de lo que parecía): las secciones lejos de la pantalla usan una medida
  estimada de 1000 px hasta que se dibujan (`content-visibility:auto`, X02). Tras un salto largo, las
  que quedan cerca se dibujan con su tamaño real unos cuadros después y la sección de destino se
  movía con ellas. El anclaje del desplazamiento no lo corrige, porque lo que mantiene quieto es la
  sección que se ve bajo las barras, encima del destino. Ahora el salto se repite en cada cuadro en
  que el destino se mueve, durante 0.8 s, hasta que el lector desplaza, toca o pulsa una tecla, o
  empieza otro salto. Lo mismo al abrir la página en la dirección de una sección
  (`index.html#tecnicas`) en una visita nueva, no al recargar ni al volver. El enlace «Abrir
  detalle» de cada plan usa el mismo salto: antes se desplazaba suave aunque el lector hubiera
  pedido reducir el movimiento.
- X07 juzga un salto 300 ms después del clic, con el enlace de la barra, y abre cada página en la
  dirección de la sección más baja a la que enlazan sus barras.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X08 (N10) | En los dos inicios, las cuatro herramientas enteras en pantalla con la página arriba donde no hay barra de abajo; el foco en la barra de arriba, siempre en un control entero a la vista | sobre 9433ba5, en los dos inicios: las herramientas fallan a 844×390, 820×1000, 1280×800 y 1440×1100 (a 1280×800 «▶ Sesión» 0 de 82 px y «PDF» 0 de 49); el foco cae en controles cortados a los once tamaños, también en el teléfono (a 390×844 «Técnicas», 0 de 73 px) | 88 de 88 tamaños y páginas sobre el arreglo (`run_new.py`) |
| X07, Tab (N13) | Tab y Mayús+Tab a través de cada barra, al salir y al volver a entrar, dejan la página quieta en cada cuadro, con el movimiento reducido y activado | sobre 9433ba5, en las ocho páginas a todos los tamaños donde las barras se quedan (820×1000, 1280×800 y 1440×1100, y con texto grande 1024×768 y 1280×800): por ejemplo «top bar stuck, Tab to ▶ Inicio: the page moved 436 px» a 1280×800; de 143 a 1454 px | 88 de 88 |
| X07, espacio | Con el relleno de las barras agrandado, el espacio reservado las sigue | sobre el árbol con N10 y N13, antes de las notas: falla en las ocho páginas a los siete tamaños con 16 px, por ejemplo «top bar: 105 px tall, room kept 65 px» | 88 de 88 (`run_notes.py`) |
| X07, saltos | Cada enlace interno de las barras y la página abierta en la dirección de una sección dejan la sección a 24 px como mucho bajo lo que se queda, una vez dibujada la página | en los dos inicios, a los once tamaños: «#plan-detail» de 3876 a 9924 px más abajo, «#guide» de 84 a 566 px por encima, «#tecnicas» 86 px más abajo a 820×1000 y 963 y 1950 px con texto de 20 y 24 px | 88 de 88; con el movimiento activado, saltos cortos y largos a cuatro tamaños, ninguno mal |
| X07, diálogo | Lo que está en el centro sigue quieto 300 ms y 1.2 s después de cerrar | los mutantes del red team que desplazan 40 px a los 400 ms y a 1 s pasaban | los dos fallan («the page moved -40 px») a 1024×768 y 641×500 |

Mutantes de N13 (en el inicio servido y en un plan, a los once tamaños):

| Mutante | Qué detecta X07 |
|---|---|
| sólo dentro de la barra (sin el caso de entrar desde el control de al lado) | volver a entrar mueve la página, por ejemplo «top bar stuck, Shift+Tab to PDF: the page moved 71 px» a 1280×800 y de 143 a 497 px con la barra Sujeto/Hora |
| sólo hacia delante (Mayús+Tab sigue siendo del navegador) | Mayús+Tab mueve la página de 71 a 536 px |
| devolver la página a su sitio después del foco, en lugar de evitar el desplazamiento | pasa con el movimiento reducido y falla con el movimiento activado, 8 a 18 px en un cuadro, en todas las barras fijas |

En el teléfono la página no cambia: comparando 9433ba5 con 1e8cbcd, ninguna de las 5640 cajas del
inicio ni de las 587 de un plan cambia de sitio ni de tamaño a 320, 390 y 430 px de ancho. A 844×390,
820×1000, 1280×800 y 1440×1100 cambian de 5 a 21 cajas, todas dentro de la barra de arriba, y ninguna
de los planes.

Investigación de N13 tras la hipótesis fallida. Intentos: (1) traducir el `scroll-padding` a
`scroll-margin` en los controles de las barras. Pasaba en el inicio sólo porque sus controles están
dentro de contenedores con desplazamiento propio, y en la barra de los planes la página se movía de
252 a 443 px: Chrome decide si un control está a la vista con su propia caja y la zona reservada, y
`scroll-margin` sólo cambia cómo lo alinea. (2) Devolver la página a su sitio en `focusin`: falla
porque Chrome desplaza antes del primer evento de foco (registrado: `keydown`, desplazamiento,
`blur`, `focus`, `focusin`). (3) Guardar la posición en `keydown` y devolverla en `focusin`: pasa
con el movimiento reducido, pero con el movimiento activado la vuelta se ve. Fuentes:
csswg-drafts#7931 (un campo en una cabecera fija: cada pulsación desplaza la página; fantasai
propone que lo fijo no use `scroll-padding`; sin resolver; la salida para autores es
`scroll-margin` por elemento) y csswg-drafts#7930. Parecido y diferencia: el mismo motor y la misma
causa, la zona reservada; aquí el `scroll-margin` del arreglo propuesto no basta, porque Chrome lo
usa para alinear y no para decidir. Lo que cambió la hipótesis: el desplazamiento es parte de lo
que hace el navegador al mover el foco con Tab, antes de cualquier evento de foco, así que sólo se
evita impidiendo esa acción y moviendo el foco con `preventScroll`. Predicción falsable: con
`keydown` y `preventScroll`, cada cuadro entre pulsaciones muestra la misma posición, con el
movimiento reducido y activado, y el mutante que sólo devuelve la página falla con el movimiento
activado. Se cumplió (tablas de arriba).

Investigación de los saltos tras la hipótesis fallida. El primer arreglo repetía el salto hasta
tres cuadros quietos y «#tecnicas» seguía 86 px abajo a 820×1000: el registro cuadro a cuadro
mostró que el destino se mueve en el cuarto cuadro. Fuentes: csswg-drafts#9833 (Robert Flack, enero
de 2024): con `contain-intrinsic-size` más chico que lo real, el destino de un desplazamiento se
calcula con las estimaciones y se aleja cuando aparecen los tamaños reales; propone que el destino
también siga el anclaje, sin resolver; csswg-drafts#9337: el elemento de destino cuenta como
visible antes de desplazar, pero no sus vecinos. Parecido: el mismo motor y las mismas
estimaciones. Diferencia: el caso de #9833 es un desplazamiento suave; aquí es instantáneo y lo que
cambia son las secciones de encima del destino. Lo que cambió la hipótesis: los tamaños reales
llegan a lo largo de varios cuadros, no en el siguiente, así que mantener el salto debe durar un
tiempo y no hasta unos cuadros quietos. Predicción falsable: manteniéndolo 0.8 s todos los saltos
caen bien a los once tamaños, y el arreglo de tres cuadros, como mutante, falla en «#tecnicas» a
820×1000. Se cumplió.

Errores propios:

- La comprobación de saltos de N9 medía en la misma tarea que el clic, antes de que la página
  dibujara nada. Por eso pasaba y lo que dije en N9, que cada enlace interno de las barras cae
  libre de ellas, era falso una vez dibujada la página.
- En N13 y en los saltos busqué fuentes después del segundo y del tercer intento, no después del
  primero como pide la regla. Las fuentes confirman la causa y no cambian los arreglos.

Compromisos:

- Sólo se probó en Chromium. El arreglo de N13 depende de JavaScript: sin él, Tab en una barra fija
  vuelve a mover la página como antes. Busca el control siguiente en el orden del documento entre
  una lista amplia de elementos que reciben el foco; ninguna página usa `tabindex` positivo y en las
  barras no hay otro elemento que lo reciba, pero uno que la lista no nombre se saltaría.
- El movimiento activado se prueba sólo con texto de 16 px; con 20 y 24 px, sólo el reducido.
- Con texto más grande, de 641 a 800 px de ancho (20 px) o a 961 px (24 px), la barra de arriba
  queda como en el teléfono: las herramientas al final de la fila que se desplaza, y sin barra de
  abajo, que sólo existe hasta 640 px. X08 mira las herramientas sólo con 16 px.
- De 641 a 1023 px, con 16 px de texto, la marca va sin «· San Isidro» ni subtítulo y el enlace del
  concurso dice «Arquitectura».
- En el teléfono, «Modo sol» y «PDF» siguen al final de la fila que se desplaza, como antes.
- Un salto se mantiene 0.8 s: una sección que se dibuje más tarde, en un teléfono muy lento, aún
  podría mover el destino. X07 lo mide a 300 ms en Chromium de escritorio.
- La prueba del diálogo cubre 1.2 s tras cerrar; un movimiento posterior pasaría.
- `browser_release_qa.py` pasa de 4 min 15 s (fdca8e7) a 21 min 5 s en local, con 4 CPU, por las
  pasadas nuevas de X07: Tab en cada barra, con movimiento reducido y activado, y abrir cada página
  en la dirección de una sección. En CI tardaba 2 min 11 s y el límite del trabajo es 45 min.

**Cierre de N10, N13 y las notas** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo
`dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| `browser_release_qa.py` en 5532975 | 0 | 520/520 en 21 min 5 s |
| las otras cinco suites con reporte en 5532975 | 0 | axe 80/80, tarjeta 63/63, velocidad 138/138, visual 37/37, óptica 22/22; reportes en 1da6977 |
| las cinco suites de `tests/architecture/browser_*.py` en 5532975 | 0 | todas en verde |
| `pytest -q` en 1da6977 | 0 | 922 pasan (898, las 19 de `tests/test_fixed_bars.py` y las 5 de `tests/test_top_bar_tools.py`), 1 omitida |
| `verify_release.py` (navegador 520), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre 5532975, el inicio pesa 132.9 KB (130.3 antes; presupuesto 180)
y bloquea 99.5 ms (51.5 antes; presupuesto 200). Ese tiempo va de 46 a 146 ms en los doce últimos
reportes, con cambios menores en el código, así que no lo atribuyo al código nuevo sin otra
medida. Abrir la tarjeta responde a 40 y 152 ms y muestra los planes a 59 y 231; a ancho de
tableta responde a 56 y 176 y muestra la primera toma a 95 y 345.

### N14 y las preguntas Q1 y Q2 del red team (ecde02c)

El red team revisó N10, N13 y las notas (parches 0001–0013, `qa/FINDINGS_PR22.md`) y los pasó
todos: N10 en 396 casos sin problemas (458 sobre 09c44bc), N13 también con el movimiento activado
y texto de 20 y 24 px, y su N12 en 396 saltos sin ninguno mal. Dejó un hallazgo nuevo, N14, dos
preguntas, Q1 y Q2, y una nota sobre el ratón.

**N14: Tab hacia un control justo bajo la barra de arriba movía la página (error mío, de N9).** N9
reservaba arriba el sitio de las dos barras en toda la página, también en las secciones de encima
de la barra Sujeto/Hora, donde esa barra todavía no está arriba. Chrome contaba un control entero
en pantalla dentro de esa franja como fuera de la vista y desplazaba la página para mostrarlo, de
335 a 511 px (csswg-drafts#7930, la misma causa que N13). Ahora el sitio reservado cuenta la barra
Sujeto/Hora sólo mientras está arriba. Un script marca `html.fr-bar-in-flow` mientras no lo está
(lo comprueba en cada desplazamiento, en cada cambio de tamaño y antes de cada tecla o toque) y,
con esa marca, el sitio reservado es sólo el de la barra del sitio. Para que un salto caiga igual
con la barra arriba o no, el margen de cada sección cambia con la marca: las de encima de la barra
dejan su margen negativo y las de debajo suman el alto de la barra. Está en el inicio
(`index.html`) y en los planes (`scripts/generate_plan_pages.py`).

Comprobación nueva en X07 (`free_spots_leave_page_still`): con las barras arriba, se pone un
control de la página a 1.25 rem bajo lo que se queda arriba, encima y debajo de la barra
Sujeto/Hora, y se llega a él con Tab y con Mayús+Tab desde el control de al lado. La página no
debe moverse.

**Q1: un desplazamiento del lector durante un salto ya no se deshace.** El salto se mantiene 0.8 s
mientras la página dibuja las secciones de alrededor. Un desplazamiento sin evento de entrada, como
el de un lector de pantalla o el de buscar en la página, se deshacía en ese tiempo. Ahora, mientras
se mantiene, el anclaje del desplazamiento está apagado (`overflow-anchor:none` en la raíz), así
que sólo el lector mueve la página, y el salto se detiene en cuanto la página está en una posición
que él no puso. El ajuste al final de una página que se acorta no cuenta como el lector.
Comprobación nueva en X07 (`reader_scroll_kept`): en los dos inicios, tras el salto más largo de
las barras, el lector baja media pantalla en una tarea propia, como llega el desplazamiento de un
lector de pantalla, y la página debe seguir ahí 1 s después.

**Q2: la medida de lo dibujado sigue al bloque contenedor (V18).** La prueba de controles encimados
recortaba cada control por todos los antepasados que recortan lo que se sale. Una caja `absolute`
o `fixed` se sale de los que no son su bloque contenedor (CSS 2.2 §11.1.1), así que un control así
podía tapar a otro y contar como no dibujado. Ahora sólo recortan los antepasados que lo contienen:
para `absolute`, hasta el primero posicionado, y para `fixed`, ninguno salvo uno con
`transform`, `filter` o `contain`. En las páginas reales no cambia nada.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X07 (N14) | Tab y Mayús+Tab hacia un control entero a 1.25 rem bajo lo que se queda arriba, encima y debajo de la barra Sujeto/Hora, dejan la página quieta | sobre a481181, en el inicio, a los ocho tamaños donde las barras se quedan, siempre encima de la barra Sujeto/Hora: por ejemplo «Tab onto Cómo leer y qué no promete … the page moved 361 px» a 1280×800; de 335 a 511 px | 64 de 64 pulsaciones en los dos inicios (`run_free.py`) |
| X07 (N14), prueba del red team | Mayús+Tab hacia `#opt-bg` puesto a 8, 30, 60 y 100 px bajo la barra del sitio (`optbg.py`) | sobre a481181: de −326 a −424 px a 8 y 30 px, de −24 a −42 a 60 | 0 px a 30, 60 y 100; a 8 px, de −4 a −10 (ver compromisos) |
| X07 (Q1) | Tras el salto más largo, un desplazamiento del lector sin evento de entrada se queda | sobre a481181, en los dos inicios a los once tamaños: «after the jump to #guide, a scroll of the reader's own was undone: the page moved 400 px» a 1280×800; de 195 a 550 px | 22 de 22 (`run_kept.py`) |
| V18 (Q2) | Un control `absolute` que se sale de una caja de 10 px con `overflow:hidden` y tapa otro cuenta como encimado | la prueba anterior no lo ve, a 390×844 y 1280×800 | lo marca a los dos tamaños; en el inicio, un plan, la tarjeta y la página del concurso, a seis tamaños, las dos pruebas dan lo mismo (`cut_compare.py`) |

Mutantes (en el inicio servido):

| Mutante | Qué detecta X07 |
|---|---|
| sin el margen de las secciones de debajo de la barra | los saltos y la página abierta en una sección quedan detrás de las barras: «#planes starts at 77 px, what stays ends at 137 px» a 820×1000, 1280×800 y 1440×1100, y con texto de 20 y 24 px |
| la marca siempre puesta (el sitio de la barra Sujeto/Hora nunca cuenta) | con Mayús+Tab el foco cae detrás de la barra a los cinco tamaños, por ejemplo «Canon Camera Museum · EOS 6D: 40 of 50 px behind a bar» a 1280×800 |
| el salto sin apagar el anclaje | el anclaje cambia la posición, el salto cree que fue el lector y se detiene: «#tecnicas» cae 560 px abajo a 430×932 y 1950 px con texto de 24 px a 700×800 |

Sin regresiones en lo de antes: X08 y N13 88 de 88 (`run_new.py`), las notas de N9 88 de 88
(`run_notes.py`) y la vuelta atrás (`run_back.py`) sin fallos.

Investigación de N14. Fuentes: TetraLogical, «Sticky content: focus in view» (2023): el
`scroll-padding` debe corresponder a lo que tapa en cada momento y, si la altura cambia, hace falta
JavaScript; csswg-drafts#7931 (Robert Flack): lo que está bajo una cabecera fija necesita otro
`scroll-padding` que lo que está encima; WCAG, técnica C43. Los `container queries` con
`scroll-state(stuck)` saben si la barra está arriba, pero no pueden dar estilo a `html`, que es
donde vive el `scroll-padding`, así que la marca la pone un script. Parecido y diferencia: el mismo
motor y la misma decisión de Chrome que en N13; aquí el control está en la página, no en una barra.
Predicción falsable: con el sitio reservado sólo para lo que tapa, Tab y Mayús+Tab hacia un control
a 1.25 rem bajo la barra del sitio dejan la página quieta; el mutante con la marca siempre puesta
deja el foco detrás de la barra Sujeto/Hora y el mutante sin el margen de debajo hace caer cortos
los saltos. Se cumplió (tablas de arriba).

Investigación de Q1 tras la hipótesis fallida. La primera prueba de Q1 desplazaba dentro de un
cuadro de animación y hacia arriba, y daba movimientos con el arreglo puesto. Sin buscar antes,
añadí una segunda salida, en el evento de desplazamiento, y no cambió nada. Fuentes después: Chris
Harrelson y csswg-drafts#4239 (orden de un cuadro: eventos de desplazamiento, cuadros de animación,
estilo y diseño) y la norma de anclaje del desplazamiento (`overflow-anchor:none` lo apaga en la
raíz). Lo que cambió la hipótesis: un desplazamiento en su propia tarea llega antes del siguiente
cuadro de animación, así que la comprobación del salto lo ve antes de que la página se dibuje y la
salida en el evento no añade nada; los movimientos venían de la prueba, que subía hacia secciones
sin dibujar (`content-visibility:auto`) que crecían igual con o sin el salto. Quité la segunda
salida y la prueba baja media pantalla en una tarea propia. Predicción falsable: así, sobre
a481181 el salto deshace el desplazamiento a los once tamaños y con el arreglo no a ninguno, y el
mutante sin apagar el anclaje hace fallar los saltos. Se cumplió.

Errores propios:

- N14 lo causé yo en N9: reservé el sitio de la barra Sujeto/Hora en toda la página y mis pruebas
  sólo miraban controles dentro de las barras o detrás de ellas, no controles libres justo debajo.
- En Q1 probé una segunda salida antes de buscar fuentes, contra la regla. La quité: no hacía falta.

Compromisos:

- Sólo se probó en Chromium. El arreglo de N14 depende de JavaScript: sin él la marca no aparece,
  se reserva el sitio de las dos barras en toda la página y vuelve N14, como en N9.
- En cada desplazamiento se leen la posición y el estilo de la barra Sujeto/Hora; la marca sólo se
  cambia cuando cambia el estado. No lo medí aparte.
- Un control a menos de 0.75 rem bajo lo que se queda arriba se mueve de 4 a 10 px (16, 20 y 24 px
  de texto) para dejar ese espacio, el mismo que deja un salto, de modo que el anillo del foco no
  quede pegado a la barra. Antes de N9 no había espacio reservado y no se movía.
- La comprobación de N14 encuentra dónde poner el control sólo en los inicios: en los planes casi
  no hay controles fuera de las barras. Los saltos de X07 en los planes sí pasan por los márgenes
  nuevos.
- Nota del red team sobre el ratón: de 641 a 1023 px, los enlaces de las secciones que quedan fuera
  de su fila sólo se alcanzan con la rueda y Mayús, porque la fila esconde su barra de
  desplazamiento. Lo dejo así: el difuminado indica que hay más y esos enlaces repiten secciones de
  la página. Si hace falta, una barra fina o flechas para el ratón.
- En la página del concurso, la prueba de controles encimados marca los trozos de enlaces que se
  parten en dos líneas a 390 y 844 px, igual con la medida anterior y la nueva. Esa página no pasa
  por esa prueba en la suite.
- `browser_release_qa.py` tarda 22 min 50 s en local con 4 CPU (21 min 5 s antes). El límite del
  trabajo en CI es 45 min.

**Cierre de N14, Q1 y Q2** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| `browser_release_qa.py` en ecde02c | 0 | 530/530 en 22 min 50 s (21 min 5 s antes, con 4 CPU) |
| las otras cinco suites con reporte en ecde02c | 0 | axe 80/80, tarjeta 63/63, velocidad 138/138, visual 37/37, óptica 22/22; reportes en 1f795e0 |
| las cinco suites de `tests/architecture/browser_*.py` en ecde02c | 0 | todas en verde |
| `pytest -q` en 1f795e0 | 0 | 925 pasan (922 y 3 nuevas en `tests/test_fixed_bars.py`), 1 omitida |
| `verify_release.py` (navegador 530), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre ecde02c, el inicio pesa 133.5 KB (132.9 antes; presupuesto 180) y
bloquea 81 ms (presupuesto 200). Abrir la tarjeta responde a 40 y 112 ms y muestra los planes a 59
y 162; a ancho de tableta responde a 48 y 128 y muestra la primera toma a 95 y 220.

### Segunda revisión del red team: N14b y N15 (657ef3e)

El red team revisó los parches 0001–0016 y pasó N14, Q1 y Q2 (`qa/FINDINGS_PR22.md`). Acepta que un
control a menos de 0.75 rem bajo la barra de arriba se mueva de 4 a 10 px: es el espacio que deja
el `scroll-padding` para que el anillo del foco no quede pegado a la barra. Recorriendo el inicio
entero con Tab y Mayús+Tab, las pulsaciones que movían la página hacia un control ya despejado
bajan de 22, 14 y 0 a 6, 1 y 0. Dejó dos notas sobre lo que queda: N14b y N15.

**N14b: pasada la sección de la barra Sujeto/Hora, el sitio reservado todavía la contaba.** Al
final de su sección, la barra sube por debajo de la barra del sitio y desaparece. El script sólo
miraba si la barra había llegado arriba, así que seguía contándola. Pasada la sección, Tab o
Mayús+Tab hacia el primer enlace del pie movía la página: 17 px con 16 px de texto, donde el final
de la página lo limita, y de 335 a 341 px con texto de 20 y 24 px. Ahora la barra cuenta sólo
mientras está arriba y se ve bajo la barra del sitio (`index.html` y
`scripts/generate_plan_pages.py`). La pasada de N14 en X07 prueba ahora también el primer control
pasada la sección de la barra.

El red team propuso dos arreglos: contar la barra sólo mientras está quieta arriba, o mientras su
borde de abajo sigue bajo el de la barra del sitio. Elegí el segundo. Mientras la barra sube, una
parte sigue a la vista. Con el primero, el sitio reservado sería el de la barra del sitio sola, y
un control al final de la sección podría quedar detrás de la parte que se ve, sin que el navegador
desplace la página (WCAG 2.4.11). Con el segundo, lo peor es que la página se mueva un poco hacia
un control justo bajo esa parte. En estas páginas no pasa: el barrido de abajo no encuentra ningún
movimiento.

**N15: no es un error.** Mayús+Tab desde el enlace «Abrir aquí ↘» de una tarjeta de plan hacia el
de la tarjeta anterior movía la página 437 px, aunque la medida decía que el destino estaba entero
a la vista, a 527 px. En la cuadrícula, la tarjeta anterior está en la fila de arriba: con el
enlace de partida a 414 px, el de destino estaba de −7 a 37 px, detrás de las barras, que terminan a
137 px (`probe15.py`). El navegador desplaza la página para mostrarlo, como debe. Mientras subía, se
dibujaron secciones de más arriba (`content-visibility:auto`), y el anclaje del desplazamiento movió
la página otros 534 px. Por eso, medida desde la posición final, la posición de antes salía en
527 px. No cambio nada.

| ID | Qué exige | RED (antes) | GREEN (después) |
|---|---|---|---|
| X07 (N14b) | Tab y Mayús+Tab hacia el primer control pasada la sección de la barra Sujeto/Hora, a 1.25 rem bajo lo que se queda, dejan la página quieta | sobre dc21d0b, en los dos inicios: «Tab onto 6 planes de sesión, 1.25 rem under what stays (past the Sujeto/Hora bar's section): the page moved 335 px» con texto de 20 px a 1024×768, y 341 px con 24 px a 1280×800; con 16 px el control no se puede poner ahí | 72 de 72 pulsaciones en los dos inicios (`run_free.py`) |
| X07 (N14b), barrido | Barriendo de 6 en 6 px el tramo en que la barra sube y desaparece, Tab y Mayús+Tab hacia el primer control del pie no mueven la página si ese control ya estaba despejado, más allá de los 0.75 rem, ni lo dejan detrás de una barra (`sweep_leave.py`, cinco tamaños) | sobre dc21d0b: 60 de 250 pulsaciones mueven la página, hasta 350 px | ninguna de 250 mueve la página ni lo deja detrás |
| X07 (N14b), prueba del red team | `leave.py`: Mayús+Tab hacia «6 planes de sesión» a 8, 30, 60 y 100 px bajo la barra del sitio | sobre dc21d0b: −17 px a 8, 30 y 60 px con 16 px de texto a 1024×768 | 0 en todos los casos |

Errores propios:

- El arreglo de N14 sólo miraba un lado: si la barra había llegado arriba, no si ya se había ido.
  La prueba nueva de N14 ponía controles encima y debajo de la barra, pero no pasada su sección.
- La primera versión del barrido contaba como movimientos los de un control dentro de los 0.75 rem
  bajo la barra del sitio, que el red team y yo aceptamos como espacio para el anillo del foco. La
  medida final empieza a contar pasados esos 0.75 rem.

Compromisos:

- Mientras la barra Sujeto/Hora sube al final de su sección, un recorrido de su propio alto, cuenta
  entera aunque sólo se vea una parte. Un control justo bajo esa parte podría moverse como mucho lo
  que queda oculto de la barra. En estas páginas el barrido no encuentra ninguno: el primer enlace
  del pie queda más abajo.
- La pasada de N14 sólo encuentra dónde poner el control pasada la sección con texto de 20 y 24 px,
  a 1024×768 y 1280×800. Con 16 px el final de la página no deja subirlo tanto. El barrido cubre el
  tramo a cinco tamaños, pero no está en la suite.
- Velocidad: en esta máquina, nueva tras un reinicio del entorno, abrir la tarjeta a ancho de
  tableta en un teléfono de gama baja muestra la primera toma cerca del presupuesto de 500 ms. En la
  corrida completa de las suites dio 506 ms (las cinco vueltas, de 435 a 676) y la suite de
  velocidad falló. El inicio solo, dos veces en 657ef3e y dos en dc21d0b, alternando, dio de 378 a
  430 ms, sin diferencia entre los dos builds, y dos corridas más de la suite completa pasaron, con
  466 y 353 ms. No lo atribuyo al código, pero el margen es poco y CI podría fallar por lo mismo.

Tercera revisión del red team (parches 0001–0019, `qa/FINDINGS_PR22.md`): PASS. `leave.py` da 0 en
todos los casos; en el recorrido entero con Mayús+Tab sólo quedan movimientos de 5 a 6 px dentro de
los 0.75 rem aceptados. Está de acuerdo con la segunda opción por la razón de WCAG 2.4.11, retira N15
porque era su medida, y lee el fallo de velocidad como ruido de una máquina recién arrancada. Da N9
(0001–0019) por listo.

**Cierre de N14b** (árbol limpio, fuentes de CI, Chromium completo, sirviendo sólo `dist/`)

| Comando | Salida | Resumen |
|---|---|---|
| `browser_release_qa.py` en 657ef3e | 0 | 530/530 en 22 min 39 s |
| `perf_budget_qa.py` en 657ef3e, dentro de la corrida completa | 1 | 137/138: la primera toma a ancho de tableta en gama baja, 506 ms con presupuesto de 500 |
| `perf_budget_qa.py --only index.html`, alternando 657ef3e y dc21d0b | 0 | 420 y 427 ms en 657ef3e, 378 y 430 en dc21d0b |
| `perf_budget_qa.py` en 657ef3e, otra vez | 0 | 138/138 (466 ms); el reporte sale de una tercera corrida con el árbol sin otros cambios: 138/138 (353 ms) |
| las otras cuatro suites con reporte en 657ef3e | 0 | axe 80/80, tarjeta 63/63, visual 37/37, óptica 22/22; reportes en 3633d75 |
| las cinco suites de `tests/architecture/browser_*.py` en 657ef3e | 0 | todas en verde |
| `pytest -q` en 3633d75 | 0 | 925 pasan, 1 omitida |
| `verify_release.py` (navegador 530), `verify_architecture.py` | 0 | `checks_failed: []` |
| `ruff … C901` a 10, `regenerate_all.py && git diff --exit-code` | 0 | limpio, sin diferencias |

En `PERF_BUDGET_QA.json` sobre 657ef3e (1.89× y 6.75×), el inicio pesa 133.6 KB y bloquea 90 ms.
Abrir la tarjeta responde a 48 y 184 ms y muestra los planes a 82 y 274; a ancho de tableta
responde a 64 y 184 y muestra la primera toma a 118 y 353.

### Rebase sobre main tras fusionar PR #22

Pablo fusionó PR #22 el 2026-10-27 (40a5203). Los commits de N9 a N14b se rebasaron sobre ese main
para el PR siguiente. Cada commit conserva su árbol: `git diff b8699ea ca51c55` sale vacío, y el
árbol de 40a5203 es el de 09c44bc. Los reportes (`audited_commit`) y estas notas nombran los commits
de antes del rebase. Equivalencias:

| Antes | Después | Commit |
|---|---|---|
| f92bd71 | 7ee7692 | Keep the top bars in place only where there is room (N9) |
| d6733b4 | 4fc41a6 | Give focus back to a fixed bar without moving the page (N9) |
| 7494f49 | 72b02a8 | Say how much of a phone the plan bars would cover: a fifth to over a third |
| 47405fe | c5c88ba | Reports from every browser suite on 7494f49: release 484/484 with X07 |
| 523ff43 | 16bfd25 | Record N9 and X07: the top bars stay only where there is room |
| 94041f4 | 87ff0f0 | Keep room for the bars at the reader's text size (red team N11) |
| fdca8e7 | 967a245 | Judge "the page stays where it was" by what is on screen, not the scroll position |
| 4ff973b | e131c36 | Reports from every browser suite on fdca8e7: release 492/492 |
| 9433ba5 | 5fa3f67 | Record N11 and the on-screen measure: README, inventory and handoff |
| 1e8cbcd | 4d153bb | Top bar tools in view, Tab across a bar, jumps that stay put (N10, N13) |
| 5532975 | 26324e2 | Judge overlapping controls by what is drawn of them (N10) |
| 1da6977 | 6c21117 | Reports from every browser suite on 5532975: release 520/520 |
| a481181 | 8fe5b30 | Notes for N10, N13 and the red team's three notes on N9 |
| ecde02c | f72cf7a | Keep room only for what covers the top; let a reader's scroll end a jump (N14, Q1, Q2) |
| 1f795e0 | d014ed8 | Reports from every browser suite on ecde02c: release 530/530 |
| dc21d0b | bd7d232 | Notes for N14 and the red team's Q1 and Q2 |
| 657ef3e | 69026b8 | Stop counting the Sujeto/Hora bar once it has gone up under the top bar (N14b) |
| 3633d75 | 650b645 | Reports from every browser suite on 657ef3e: release 530/530 |
| dd63a5a | 0c9bb4c | Notes for N14b and the red team's N15 |
| b8699ea | ca51c55 | Record the red team's pass on N14b and N15 |

### Pendiente

- Safari en iOS y Lighthouse en un teléfono real siguen sin comprobarse: no hay ninguno
  aquí ni en el hilo de comprobación en vivo.
- Diez enlaces externos están detrás de controles anti-bots y no se pueden verificar desde
  un centro de datos (pnas.org, interbank.pe, Adobe, casadelaliteratura, urbipedia, w3.org).
- La regla de rama que exige CI verde antes de fusionar la activa el dueño en Settings →
  Branches.
- Los minutos de CI de las suites de navegador se miden en el primer PR que las corre.
- Si el ensayo de la tarjeta vuelve a fallar en CI, el mensaje «never took over in 60 s; the
  active one says …» dice si el worker nuevo llegó a instalarse.
- Abrir la tarjeta de campo desde el inicio en un teléfono de gama baja calibrado: tras N4
  responde a 168–176 ms y muestra los planes a 235–283 ms (11e9484). Los planes siguen sobre
  «bueno» y dentro de «nunca malo».
- Tras los planes queda la tarea de las tomas, 67–112 ms en gama baja: un toque en ese hueco
  la espera (N2 del red team).
- N4, N7 y N8 se fusionaron con PR #22 y el red team los pasó. N5 queda como límite declarado
  de la medición.
- N9 a N14b (barras de arriba que se quedan sólo donde caben): en el PR siguiente a #22, con X07
  y X08; el red team los pasó. Pablo tiene la pregunta de si deben quedarse fijas también en el
  teléfono; si dice que sí, se quita el límite de tamaño y X07 cambia con él.
- De 641 a 1023 px, con un ratón sin rueda lateral, los enlaces de las secciones fuera de la fila
  se alcanzan sólo con Mayús y la rueda. Si hace falta, una barra fina o flechas para el ratón.
- Con texto más grande, de 641 a 800 px (20 px) o a 961 px (24 px), no hay barra de abajo y las
  herramientas quedan al final de la fila que se desplaza. Si hace falta, la barra de abajo podría
  medirse en `em` como las de arriba.
