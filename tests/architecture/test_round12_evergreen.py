"""The site outlives the Arquitectura en Foco 2026 contest.

Requirements:
T01  No published page treats the closed contest as the reader's goal: no
     "CONCURSO:" guidance, no instruction about "el concurso" or "las bases",
     no "reto" framing, and no name taken from the archived edition.
T02  The architecture ranking scores places for the photographer, not for a
     jury: no criterion reads the contest-brief fit or the jurors' public work,
     and the remaining weights keep the ratios the user elicited.
T03  The hosted build publishes no contest research, and its service worker
     precaches only files the build actually ships.
T04  The closed edition stays in the repository as a dated archive.
"""
from __future__ import annotations

import copy
import html
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "canon6d_sota_hosted"
ARCHIVE = ROOT / "architectural_photography" / "archive" / "arquitectura-en-foco-2026"
MODEL = ROOT / "architectural_photography" / "ranking" / "scoring_model.json"
PUBLIC_RANKING = ROOT / "data" / "architecture" / "ranking.json"
CONTEST_FILES = ("competition_rules.json", "judges.json", "organizer_history.json")

sys.path.insert(0, str(ROOT / "scripts"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def visible_text(page: str) -> str:
    """What a reader sees or a screen reader announces, including meta descriptions."""
    metas = re.findall(r'<meta[^>]+(?:name|property)="(?:description|og:description|twitter:description)"[^>]+content="([^"]*)"', page)
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    labels = re.findall(r'aria-label="([^"]*)"', body)
    body = re.sub(r"<[^>]+>", " ", body)
    return html.unescape(" ".join([*metas, *labels, body]))


def published_pages() -> list[Path]:
    pages = sorted(DIST.rglob("*.html"))
    assert pages, "build the hosted site first: python3 scripts/regenerate_all.py"
    return pages


def archived_edition_names() -> list[str]:
    rules = load(ARCHIVE / "competition_rules.json")
    return [rules["title"], *rules["jurors"]]


# A reference to one specific contest, as opposed to "un concurso" or "una convocatoria" in general.
CONTEST_FRAMING = (
    re.compile(r"\bCONCURSO\s*:"),
    re.compile(r"\b(?:el|del|al)\s+concurso\b", re.I),
    re.compile(r"\blas\s+bases\b", re.I),
    re.compile(r"\breto\b", re.I),
)


@pytest.mark.parametrize("page", published_pages(), ids=lambda p: str(p.relative_to(DIST)))
def test_t01_published_pages_do_not_frame_the_reader_around_the_closed_contest(page):
    text = visible_text(page.read_text(encoding="utf-8"))
    hits = [match.group(0) for pattern in CONTEST_FRAMING for match in pattern.finditer(text)]
    hits += [name for name in archived_edition_names() if name in text]
    assert not hits, f"{page.relative_to(DIST)} still speaks to the closed contest: {sorted(set(hits))}"


def test_t01_lessons_carry_a_general_editorial_note_instead_of_a_contest_note():
    learning = load(ROOT / "data" / "architecture" / "learning.json")
    for lesson in learning["lessons"]:
        assert "competition_note" not in lesson, lesson["lesson_id"]
        assert lesson.get("editorial_note"), lesson["lesson_id"]


def test_t02_ranking_model_has_no_jury_or_contest_brief_criterion():
    model = load(MODEL)
    layers = {spec["layer"] for spec in model["criteria"].values()}
    assert not layers & {"OFFICIAL_PROXY", "LOW_WEIGHT_ROBUSTNESS_ONLY"}, layers
    weighted = set(model["field_weights"]).union(*(s["weights"] for s in model["scenarios"].values()))
    assert weighted <= set(model["criteria"])
    assert not any("juror" in key or "official" in key or "contest" in key for key in weighted)


def legacy_row_inputs():
    import build_architecture_ranking as br

    candidates = {item["canonical_id"]: item for item in load(br.CANONICAL_PATH)}
    verified = {item["canonical_id"]: item for item in load(br.VERIFICATION_PATH)["records"]}
    record = load(br.LEGACY_ASSESSMENTS_PATH)["records"][0]
    canonical_id = record["canonical_id"]
    return br, candidates[canonical_id], verified[canonical_id], record["attributes"]


@pytest.mark.parametrize("attribute", ["brief", "judge"])
def test_t02_scores_do_not_move_with_contest_brief_fit_or_juror_overlap(attribute):
    br, candidate, verified, base = legacy_row_inputs()
    low, high = copy.deepcopy(base), copy.deepcopy(base)
    low[attribute], high[attribute] = 0.0, 10.0
    assert br.matrix_row(candidate, verified, low)["criteria"] == br.matrix_row(candidate, verified, high)["criteria"]


def test_t02_remaining_weights_keep_the_elicited_ratios():
    model = load(MODEL)
    origin = model["derived_from"]
    renamed = origin["renamed_criteria"]
    removed = set(origin["removed_criteria"])
    assert removed, "the derivation must name what it removed"

    def derive(weights: dict) -> dict:
        kept = {renamed.get(key, key): value for key, value in weights.items() if key not in removed}
        total = sum(kept.values())
        return {key: value / total for key, value in kept.items()}

    for scenario, weights in origin["scenarios"].items():
        expected = derive(weights)
        actual = model["scenarios"][scenario]["weights"]
        assert set(actual) == set(expected), scenario
        assert all(actual[key] == pytest.approx(expected[key], abs=1e-9) for key in expected), scenario
    assert model["field_weights"] == pytest.approx(derive(origin["field_weights"]), abs=1e-9)


def test_t02_public_ranking_comes_from_the_general_model():
    model, public = load(MODEL), load(PUBLIC_RANKING)
    assert public["model_version"] == model["model_version"]
    assert not {key for key in public if "official" in key or "winning" in key}


def test_t03_hosted_build_publishes_no_contest_research():
    shipped = [path for path in DIST.rglob("*") if path.is_file()]
    assert not [p.relative_to(DIST) for p in shipped if p.name in CONTEST_FILES]
    jurors = load(ARCHIVE / "competition_rules.json")["jurors"]
    leaks = [
        str(path.relative_to(DIST)) for path in shipped
        if path.suffix in {".html", ".json", ".js", ".xml", ".txt"}
        and any(name in path.read_text(encoding="utf-8", errors="ignore") for name in jurors)
    ]
    assert not leaks, leaks


def test_t03_published_source_registry_cites_no_contest_material():
    published = load(DIST / "data" / "architecture" / "sources.json")
    archived = {item["source_id"] for item in load(ARCHIVE / "sources.json")}
    assert archived, "the edition's sources belong in the archive"
    assert not archived & {item["source_id"] for item in published}


def test_t03_service_worker_precaches_only_files_the_build_ships():
    # cache.addAll() rejects the whole install if one URL 404s, which silently disables offline use.
    sw = (DIST / "sw.js").read_text(encoding="utf-8")
    core = json.loads(re.search(r"const CORE=(\[[^\]]*\])", sw).group(1).replace("'", '"'))
    missing = [url for url in core if url != "./" and not (DIST / url.removeprefix("./")).is_file()]
    assert not missing, missing


def test_t03_service_worker_precaches_every_manifest_icon():
    # An install prompt or home-screen launch offline asks for these icons.
    sw = (DIST / "sw.js").read_text(encoding="utf-8")
    core = set(json.loads(re.search(r"const CORE=(\[[^\]]*\])", sw).group(1).replace("'", '"')))
    icons = {"./" + icon["src"] for icon in load(DIST / "manifest.webmanifest")["icons"]}
    assert icons <= core, sorted(icons - core)


def test_t04_closed_edition_is_archived_outside_the_published_data():
    for name in CONTEST_FILES:
        assert (ARCHIVE / name).is_file(), name
        assert not (ROOT / "data" / "architecture" / name).exists(), name
    assert load(ARCHIVE / "competition_rules.json")["edition_state"] == "CLOSED"
