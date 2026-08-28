# FocalRuta agent contract

Repository root: `/Users/pabloillescas/Documents/GitHub/focalruta`

For Arquitectura en Foco work, read these files at the start and end of every major round:

1. `architectural_photography/EXECUTION_PROMPT.md`
2. `architectural_photography/REQUIREMENTS_INVENTORY.md`
3. `architectural_photography/state/CURRENT_STATE.json`
4. `architectural_photography/state/OPEN_QUESTIONS.json`
5. the previous round checkpoint and every source touched in the round

Raw chats, exports, prompt archives, and unredacted historical conversations are private local inputs. Never stage, commit, package, cache, or deploy them.

## Test contract

Every implementation task must name its requirement IDs and have executable RED and GREEN evidence. A round cannot close until its task tests, the architecture verifier, privacy scan, and existing FocalRuta release gate pass. Browser-facing rounds must also execute the required viewport, keyboard, focus, reduced-motion, offline, save/reload, resource, console, and overflow checks.

| Round | Required executable evidence |
|---|---|
| 0 Bootstrap | source manifest/hash/privacy tests; baseline release/browser/optics/resource/PWA evidence |
| 1 Competition | official-rules schema/source-discrepancy/preflight tests; organizer/jury provenance tests |
| 2 Learning | video/transcript provenance and lesson-shape tests; optics/ISO/sharpness/edit-safety tests |
| 3 Places | candidate admission, ten-pass dossier, A/B/C/D/E, access/currentity/ethics, visual-forensics and W01-W20 snapshot tests |
| 4 Ranking | alias/dedupe, historical-rank isolation, four scenarios, fixed-seed sensitivity, Pareto and field-rank separation tests |
| 5 Route | time-window feasibility, access/staleness, fallback/kill/replan, ETA provenance, offline state and deterministic file-preflight tests |
| 6 Integration | source/generated/hosted/standalone parity, nav discovery, service worker, regression, browser/accessibility and privacy-build tests |

Tests must fail for the intended missing behavior before implementation. Do not use comments, fixture-only assertions, placeholder data, fabricated transcripts, or generated PASS files as proof.

## Debugging research escalation

After the **first failed fix hypothesis**, stop iterative guessing and **research the error online** before the next fix attempt. Search for the exact error first, then materially similar failures in the same runtime, framework, browser, dependency, or deployment environment.

Prefer primary documentation, maintainers' issue trackers, specifications, release notes, and reproducible upstream examples. Community discussions may supplement those sources when primary evidence is incomplete, but copying an unverified workaround is not sufficient.

Before applying the next fix, record the sources consulted, the environmental similarities and differences, what evidence changed the hypothesis, and the new falsifiable prediction or RED test. If network access is unavailable, record that blocker and continue only with local primary documentation or repository evidence; do not claim the research gate passed.

## Complexity lint

Python production and verification code must stay at cyclomatic complexity 10 or lower per function. Run this required chore before closing every coding task and round:

```bash
python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'
```

If Ruff is unavailable, record that exact blocker; do not silently skip the chore. Refactor complexity rather than raising the ceiling.

Minimum closeout command set after architecture implementation exists:

```bash
python3 -m pytest tests/architecture -q
python3 scripts/verify_architecture.py
python3 scripts/verify_release.py
python3 -m ruff check scripts tests --select C901 --config 'lint.mccabe.max-complexity=10'
```

Each round checkpoint must store commands, exit codes, output summaries, artifacts, unresolved failures, and the independent verification result in `architectural_photography/state/SESSION_HANDOFF.md`.
