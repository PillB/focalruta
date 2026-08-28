# Preproduction expert-rejection audit

Status: **NOT PRODUCTION-READY**
Audited: 2026-08-27

This is a fail-closed audit. A feature remains blocked when a competent specialist could reject the current choice using authoritative evidence or a feasible higher-quality benchmark. Passing a local test does not imply user validation, standards conformance, deployed correctness, or strategic validity.

| Feature / decision | Current evidence | Strongest expert rejection | Benchmark required before acceptance | Trade-off currently exposed |
|---|---|---|---|---|
| Competition rules | Official PDF, article and form verified; discrepancy retained | A release three days before closing can still be wrong if the live form or organizer clarification changes | Reverify all three official sources immediately before release and submission | Current truth is date-stamped, not permanently true |
| Geographic scope | 43 Lima Province districts; user priorities; fail-closed classifier | A district label does not prove coordinates lie inside that district, especially around unresolved boundaries | Validate coordinates against an authoritative district geometry or record a manual boundary verification | Callao is excluded even though some older statistical uses include it in the metropolitan area |
| Historical candidates | Master82 reconciled 82→81; UV3 merged | Identity cleanup does not establish present access, condition, ethics, visual potential, or scene distinctness | Current primary-source verification and ten substantive passes before `ranking_eligible=true` | Breadth is retained as historical memory at the cost of no current shortlist yet |
| Candidate ranking | No current ranking run | Historical scores are circular evidence; arbitrary normalization/weights can reverse ordering | Explicit value model, scale definitions, four scenarios, deterministic perturbation, method/normalization sensitivity, Pareto report | No “Top 15” is shown until robustness exists |
| Route planning | Not implemented | Geodesic distance or invented ETA would misallocate a deadline-constrained field session | Provenance-tagged travel matrix, time-window feasibility, access freshness, fallbacks and manual overrides | Without a reliable matrix the product may show only conservative estimates |
| Learning curriculum | 17 lessons; 20 video records; 12 timestamps semantically audited | Timestamp validity does not establish that every derived technical claim is correct or contest-safe | Claim-level source mapping, physics vectors, misconception tests and expert review of field usability | Full caption files remain private/local for copyright; clean CI can verify metadata but not reproduce local transcript capture |
| Photographer/award references | Ten transfer cards; current award research started | Canon formation can import cultural bias or turn descriptive work into prescriptive imitation | Counterexamples, Latin American balance, current award examples and explicit non-transfer/misuse analysis | International work informs learning only; it cannot enter the Lima candidate universe |
| Architecture challenge UI | Rules, learning cards and deterministic file checks generated | A readable shell is not the promised command/ranking/route/field/reshoot/final-selector system | Complete task journey, no-JS critical fallback, state persistence, export/import and field usability tests | Dependency-free static HTML favors reliability but currently lacks requested interaction depth |
| Accessibility | Six viewport smoke tests; visible focus styles | Smoke tests and CSS intentions do not establish WCAG 2.2 AA; an inherited 1.05:1 inactive-control contrast defect is known | WCAG 2.2 AA audit covering keyboard, focus not obscured, names/roles/states, target size, reflow, contrast, errors and reduced motion | Existing FocalRuta visual regression must change to fix the known contrast defect |
| Offline/PWA | Existing shell has service-worker evidence; architecture page not yet natively shipped in all targets | A registered worker does not prove correct scope, cache freshness, update behavior, or iOS standalone reliability | Hosted and standalone parity, offline cold/warm starts, update recovery and real Safari/iOS testing | Static/offline reliability may rule out heavy libraries such as React/XYFlow unless bundling proves parity |
| Privacy | Raw archives ignored; public marker scans pass | String scanning does not model harmful data actions, derived disclosures, exports, browser storage or field-note sensitivity | Data-action inventory, NIST-style privacy risk assessment, retention/export/deletion policy and build artifact inspection | Local-only state reduces server exposure but shifts protection responsibility to the device/user |
| Performance | Static shell is small | No measured budgets exist for the complete challenge, deep research data or offline cache | Define and measure transfer, parse, interaction and cache budgets on representative mobile hardware | Lazy-loading deep research may reduce offline completeness unless the core boundary is explicit |
| Testing / CI | 30 tests; C901 ≤10; local verifiers pass; CI workflow committed | Tests may encode the implementation rather than user outcomes; remote CI has not run on a PR | Independent negative tests, mutation/property checks where valuable, browser matrix, two quiet rounds and successful protected-branch CI | More exhaustive tests increase runtime and maintenance; they are justified only for meaningful state invariants |
| Native integration / deployment | Challenge page exists on a feature branch | It is not discoverable and verified across canonical source, generated hosted build, standalone bundle and live Pages | Main navigation, generator parity, service-worker assets, bundle privacy scan, PR/CI, merge, deployment and live verification | No live URL or integration claim until deployment is observed |

## Evidence benchmarks

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) is the accessibility conformance target; new AA criteria include focus not obscured and minimum target size. W3C also states that guidelines do not meet every user need, so conformance is a floor rather than a usability guarantee.
- W3C [non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) requires visible control boundaries and focus indicators to meet applicable contrast requirements; the known 1.05:1 inactive-toggle result is therefore not acceptable evidence of readiness.
- web.dev PWA guidance requires [offline testing](https://web.dev/codelabs/pwa-training) and states that [testing on every release platform is mandatory](https://web.dev/learn/pwa/progressive-web-apps). Service-worker registration alone is insufficient.
- [NIST privacy engineering](https://csrc.nist.gov/pubs/ir/8062/final) frames privacy assessment around discrete data actions and problematic consequences. Gitignore and marker scans cover only a subset of those actions.
- The UK government [multi-criteria analysis manual](https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/7612/1132618.pdf) demonstrates varying criterion weights to find rank reversals. A single weighted score is not robust decision evidence.

## Release rule

Do not use `perfect`, `production-ready`, `integrated`, `best route`, `winning strategy`, or a new `Master N` label until every applicable rejection above has either:

1. been disproved by executable/current evidence;
2. been resolved by a stronger design; or
3. been accepted explicitly by the user as a named trade-off.

Constraints are not quality evidence. When the feasible ideal cannot be reached, report the gap, consequence and reversible fallback instead of silently lowering the benchmark.
