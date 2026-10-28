"""Authoritative release/parity checks for every PhotoPlanner delivery target."""
from __future__ import annotations

import base64
import json
import re
import sys
import zipfile
from pathlib import Path
import artifact_diff
import hashlib
import qa_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/plans.json").read_text(encoding="utf-8"))
failures: list[str] = []


def check_equal(expected, actual, label: str) -> None:
    """Compare artifacts and, on mismatch, say where they diverge."""
    difference = artifact_diff.describe(expected, actual, label)
    if difference is not None:
        failures.append(difference)


def check(condition: bool, label: str) -> None:
    if not condition:
        failures.append(label)


DIAGRAM_MAP = re.compile(r"const DIAGRAMS = (\{.*?\});\n", re.S)
WARM_SCRIPT = re.compile(r"<script>window\.addEventListener\('load',\(\)=>\{const c=navigator\.connection;.*?</script>\n", re.S)


def check_hosted_plan(offline: Path, hosted_page: Path) -> None:
    """The hosted plan page is the offline page with its diagrams as files.

    Hosted pages point the diagram map at diagrams-webp/ and add one script
    that asks the service worker to cache them (U05); everything else must be
    byte-identical, and every file must hold the same image the offline page
    inlines.
    """
    offline_html = offline.read_text(encoding="utf-8")
    hosted_html = hosted_page.read_text(encoding="utf-8")
    inline = json.loads(DIAGRAM_MAP.search(offline_html).group(1))
    linked = json.loads(DIAGRAM_MAP.search(hosted_html).group(1)) if DIAGRAM_MAP.search(hosted_html) else {}
    check(set(inline) == set(linked), f"hosted {offline.name} links every inline diagram")
    for key in set(inline) & set(linked):
        target = (hosted_page.parent / linked[key]).resolve()
        same = target.is_file() and target.read_bytes() == base64.b64decode(inline[key].split(",", 1)[1])
        check(same, f"hosted {offline.name} {key} is the inlined image")
    blank = lambda html: DIAGRAM_MAP.sub("const DIAGRAMS = {};\n", html, count=1)
    check_equal(blank(offline_html).encode(), blank(WARM_SCRIPT.sub("", hosted_html, count=1)).encode(),
                f"hosted {offline.name} parity outside its diagram map")


plans = DATA["plans"]
check(len(plans) == 6, "canonical data has 6 plans")
required = {
    "mucha_pdc": 2,
    "poca_pdc": 2,
    "congelado": 1,
    "barrido": 1,
    "fantasma": 1,
    "lightpainting": 1,
    "larga_exp": 1,
    "zooming": 1,
}
for plan in plans:
    counts = {key: 0 for key in required}
    for shot in plan["shots"]:
        counts[shot["technique"]] += 1
        check(set(shot["settings_by_time"]) == {"day", "afternoon", "night"}, f"{shot['id']} has 3 time states")
        check(set(shot["subjects"]) == {"human", "dog"}, f"{shot['id']} has human/dog content")
        if shot["technique"] == "fantasma":
            check("Perro fuera" in shot["subjects"]["dog"]["action"], f"{shot['id']} ghost dog safety")
        if shot["technique"] == "larga_exp":
            check("Perro fuera" in shot["subjects"]["dog"]["action"], f"{shot['id']} long exposure dog safety")
    check(counts == required, f"{plan['id']} exact 10-shot assignment matrix")

gear = json.dumps(DATA["gear"], ensure_ascii=False)
for fact in (
    "Canon EOS 6D Mark I",
    "35.8 × 23.9",
    "Canon EF 35mm f/2 IS USM",
    "Canon EF 50mm f/1.8 STM",
    "Canon EF 85mm f/1.8 USM",
    "Canon EF 35–80mm f/4–5.6 III",
):
    check(fact in gear, f"canonical gear: {fact}")
check("hacia arriba" in DATA["camera_angles"]["nadir"]["effect"], "nadir points up")
check("hacia abajo" in DATA["camera_angles"]["cenital"]["effect"], "cenital points down")
check("MOVER la cámara" in DATA["composition_rules"]["perspectiva"]["tip"], "perspective correction")
check("cámara fija" in DATA["field_baselines"]["zooming"]["geometry"], "zooming fixed camera")

index = (ROOT / "index.html").read_text(encoding="utf-8")
for marker in (
    "Laboratorio óptico",
    "Laboratorio de movimiento",
    "Laboratorio de composición",
    "MODO SESIÓN",
    "Guía de poses",
    'id="field-card-modal"',
    'id="shot-modal"',
    "Casa / Laboratorio",
    "Abtao/Distrito Financiero",
):
    check(marker in index, f"master feature: {marker}")
check("18*Math.log2(1+raw)" in index, "non-saturating motion calibration shipped")
check("relative*t*28" not in index, "obsolete saturated motion calibration removed")
check("distance_from_home\":\"0 m" not in index, "home-relative origin absent from master")
check('href="downloads/canon6d_photo_planner_assets.zip"' in index, "master exposes ZIP download")
for plan_id in qa_matrix.PLAN_LETTERS:
    check(f'href="plans/plan_{plan_id}.html"' in index, f"master exposes Plan {plan_id.upper()} download")

correction_phrases = (
    "35.8 × 23.9 mm",
    "EF 35mm f/2 IS USM",
    "EF 50mm f/1.8 STM",
    "EF 85mm f/1.8 USM",
    "EF 35–80mm f/4–5.6 III",
    "nadir = cámara debajo",
    "cenital = cámara encima",
    "cámara fija",
    "tarjeta de campo es el punto de partida",
)
for page in sorted((ROOT / "plans").glob("plan_*.html")):
    text = page.read_text(encoding="utf-8")
    for phrase in correction_phrases:
        check(phrase in text, f"{page.name} correction parity: {phrase}")
    check("Distancia desde casa" not in text, f"home-relative route label absent from {page.name}")

hosted = ROOT / "dist/canon6d_sota_hosted"
if hosted.is_dir():
    hosted_index = (hosted / "index.html").read_text(encoding="utf-8")
    check("18*Math.log2(1+raw)" in hosted_index, "hosted motion calibration parity")
    check("serviceWorker.register('./sw.js',{scope:'./'})" in hosted_index, "hosted service worker is registered")
    check_equal((ROOT / "data/plans.json").read_bytes(), (hosted / "data/plans.json").read_bytes(), "hosted canonical data byte parity")
    check_equal((ROOT / "index.html").read_bytes(), (hosted / "FocalRuta_STANDALONE.html").read_bytes(), "built standalone byte parity")
    check((hosted / "downloads/canon6d_photo_planner_assets.zip").is_file(), "hosted ZIP download exists")
    for page in sorted((ROOT / "plans").glob("plan_*.html")):
        check_hosted_plan(page, hosted / "plans" / page.name)

diagrams = list((ROOT / "diagrams").glob("plan_*_*.png"))
check(len(diagrams) == 120, "120 plan diagrams")
for plan in plans:
    for shot in plan["shots"]:
        for subject in ("human", "dog"):
            check((ROOT / "diagrams" / f"{plan['id']}_{shot['id']}_{subject}.png").is_file(), f"diagram {plan['id']}/{shot['id']}/{subject}")

bundle = ROOT / "downloads/canon6d_photo_planner_assets.zip"
check(bundle.is_file(), "download bundle exists")
if bundle.is_file():
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
        for page in sorted((ROOT / "plans").glob("plan_*.html")):
            member = f"plans/{page.name}"
            check(member in names, f"bundle contains {member}")
            if member in names:
                check_equal(page.read_bytes(), archive.read(member), f"bundle current parity: {member}")
        for member, source in (("field_card.html", ROOT / "field_card.html"), ("data/plans.json", ROOT / "data/plans.json")):
            check(member in names, f"bundle contains {member}")
            if member in names:
                check_equal(source.read_bytes(), archive.read(member), f"bundle current parity: {member}")

def check_evidence(report_name: str, minimum_checks: int) -> None:
    """A QA report is evidence only while it still matches what it audited."""
    report_path = ROOT / report_name
    check(report_path.is_file(), f"{report_name} exists")
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    check(report.get("passed") is True, f"{report_name} passes")
    check(report.get("checks", 0) >= minimum_checks,
          f"{report_name} scope shrank: {report.get('checks')} checks, expected at least {minimum_checks}")
    audited = report.get("audited_artifacts")
    check(bool(audited), f"{report_name} records which artefacts it audited")
    for path, recorded in (audited or {}).items():
        current = ROOT / path
        check(current.is_file(), f"{report_name} audited {path}, which no longer exists")
        if current.is_file():
            digest = hashlib.sha256(current.read_bytes()).hexdigest()
            check(digest == recorded,
                  f"{report_name} is stale: {path} changed since it was audited at "
                  f"{report.get('audited_at', 'an unrecorded time')}; re-run its generator")


for report_name, minimum_checks in (
    # 249 before step 3, plus the reading floor (V10-V12) and dialogs at six viewports on two targets (315),
    # plus 320 px and nothing cut off (V18) and dialogs giving focus back (V19) (360), plus V18 with long lens names
    # (371), plus the on-device error log (X04) (377), plus dialogs keeping the rest out of reach (V19) and
    # numbers written the Peruvian way (V20) (414), plus the offline notice for a page never kept (V21) (421),
    # plus «Copiar» without a clipboard (red team on PR #21, F7) (422), plus each dialog holding focus in
    # the task that opens it (V19, CI on 518b9a3) (428), plus every stylesheet the site ships kept whole by the
    # browser (16 distinct sheets) and the home page's card drawn like the card's page in three palettes on
    # both home pages (X05) (450), plus what stays at the top while the home pages and the six plan pages
    # scroll, at every size: only bars with room, focus going forward and back, links in the bars, and on
    # the home pages the dialogs a bar opens closing with the page still (X07) (484), plus the same with the
    # reader's text at 20 and 24 px, where the bars grow (red team N11) (492), plus on every page Tab and
    # Shift+Tab across a bar leaving the page still (N13), the page opened at a section's address and the
    # room kept following the bars' padding (red team notes), and on the home pages the top bar's tools
    # whole on screen and focus in it whole in view (N10) (520), plus on every page Tab and Shift+Tab onto
    # a control just under what stays leaving the page still (red team N14), and on the home pages a
    # reader's own scroll during a jump kept (red team Q1) (530).
    ("CURRENT_BROWSER_QA.json", 530),
    # 22 for the optical matrix and accessibility, plus the labs held to the camera (Y01-Y04): presets that
    # expose the scene they set, the dial's own speeds, the label clear of the subject and toggles that say
    # which is on, 36 per viewport at 320 and 1280 px (72) (94).
    ("OPTICS_ACCESSIBILITY_QA.json", 94),
    ("VISUAL_RESOURCE_QA.json", 37),
    # Every shipped page, light phone and dark desktop: 39 pages x 2 passes, plus the home
    # page's offline notice (M7).
    ("AXE_ACCESSIBILITY_QA.json", 80),
    # 38 for the card itself (V02-V09), 10 for your own gear (V13-V15), and the deploy
    # rehearsals for V16-V17 in place of the single simulated deploy, plus a damaged saved
    # state on the card and in the home page's dialog (V09), and the page behind that dialog:
    # undrawn while the card covers it, back where it was, printed, and drawn at 1280 px (X06),
    # and focus back on an opener on the page, the page unmoved, after a resize either way
    # across 900 px hides the one used.
    ("FIELD_CARD_QA.json", 63),
    # X02: 14 pages x 8 budgets (score, five timings, bytes, no other origin); X06: six taps
    # on two phone tiers, each timed to its answer and to what it was for, after the
    # instrument's own checks that it sees content put off and that every tap on the field
    # card finds its target in every light the card opens in.
    ("PERF_BUDGET_QA.json", 138),
):
    check_evidence(report_name, minimum_checks)

# Coverage, not an opaque total: the browser matrix must span every viewport N01
# mandates. Two scripts previously tested three sizes, one of which N01 does not
# name, and the shortfall was invisible behind a check count.
browser_qa = json.loads((ROOT / "CURRENT_BROWSER_QA.json").read_text(encoding="utf-8"))
covered = {tuple(viewport) for viewport in browser_qa.get("viewports", [])}
check(covered == set(qa_matrix.REQUIRED_VIEWPORTS),
      f"browser QA must cover the N01 matrix; missing "
      f"{sorted(set(qa_matrix.REQUIRED_VIEWPORTS) - covered)}, extra {sorted(covered - set(qa_matrix.REQUIRED_VIEWPORTS))}")

hosted_metrics = ROOT / "dist/canon6d_sota_hosted/BUILD_METRICS.json"
check(hosted_metrics.is_file(), "hosted build metrics exist")
if hosted_metrics.is_file():
    metrics = json.loads(hosted_metrics.read_text(encoding="utf-8"))
    for key, source in (
        ("hosted_html_sha256", hosted / "index.html"),
        ("standalone_sha256", hosted / "FocalRuta_STANDALONE.html"),
    ):
        check(metrics.get(key) == hashlib.sha256(source.read_bytes()).hexdigest(),
              f"BUILD_METRICS {key} matches the shipped file; rebuild dist/")

print(json.dumps({"passed": not failures, "checks_failed": failures}, ensure_ascii=False, indent=2))
sys.exit(1 if failures else 0)
