"""Authoritative release/parity checks for every PhotoPlanner delivery target."""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
import artifact_diff
import hashlib

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
    "Optical Decision Lab",
    "Motion Lab",
    "Composition Sandbox",
    "SESSION RUN",
    "Pose Coach",
    'id="field-card-modal"',
    'id="shot-modal"',
    "Home/Building Lab",
    "Abtao/Distrito Financiero",
):
    check(marker in index, f"master feature: {marker}")
check("18*Math.log2(1+raw)" in index, "non-saturating motion calibration shipped")
check("relative*t*28" not in index, "obsolete saturated motion calibration removed")
check("distance_from_home\":\"0 m" not in index, "home-relative origin absent from master")
check('href="downloads/canon6d_photo_planner_assets.zip"' in index, "master exposes ZIP download")
for plan_id in "abcdef":
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
    "Field Card es el punto de partida",
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
        check_equal(page.read_bytes(), (hosted / "plans" / page.name).read_bytes(), f"hosted {page.name} byte parity")

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

def check_evidence(report_name: str, expected_checks: int) -> None:
    """A QA report is evidence only while it still matches what it audited."""
    report_path = ROOT / report_name
    check(report_path.is_file(), f"{report_name} exists")
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    check(report.get("passed") is True, f"{report_name} passes")
    check(report.get("checks") == expected_checks, f"{report_name} has full {expected_checks}-check scope")
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


for report_name, expected_checks in (
    ("CURRENT_BROWSER_QA.json", 234),
    ("OPTICS_ACCESSIBILITY_QA.json", 22),
    ("VISUAL_RESOURCE_QA.json", 37),
):
    check_evidence(report_name, expected_checks)

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
