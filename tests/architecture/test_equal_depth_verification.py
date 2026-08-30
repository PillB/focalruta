import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
EVIDENCE_DIR = ROOT / "architectural_photography/research/locations"
PUBLIC_SOURCES = ROOT / "data/architecture/sources.json"

def evidence_batches():
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(EVIDENCE_DIR.glob("equal_depth_evidence*.json"))]

def records():
    return json.loads(LEDGER.read_text(encoding="utf-8"))["records"]

def test_all_81_candidates_have_identical_verification_shape():
    items = records()
    assert len(items) == 81
    assert len({item["canonical_id"] for item in items}) == 81
    shapes = {(tuple(item["passes"]), tuple(item["proofs"])) for item in items}
    assert len(shapes) == 1
    passes, proofs = next(iter(shapes))
    assert len(passes) == 10
    assert proofs == ("A_STRUCTURE", "B_HABITAR", "C_ANTI_POSTAL", "D_LIGHT_MATERIAL", "E_ONE_FRAME_STORY")

def test_historical_detail_alone_never_promotes_a_candidate():
    for item in records():
        assert item["ranking_eligible"] is False
        assert item["route_eligible"] is False


def test_newer_dated_evidence_overrides_earlier_partial_updates():
    by_id = {item["canonical_id"]: item for item in records()}
    for canonical_id in (
        "pentagonito-y-bordes-civicos",
        "casa-museo-ricardo-palma",
        "ovalo-de-miraflores",
    ):
        item = by_id[canonical_id]
        assert item["verification_complete"] is True
        assert all(check.get("answer") for check in item["passes"].values())
        assert all(check["status"] in {"NOT_STARTED", "PARTIAL", "CORROBORATED", "VERIFIED"} for check in item["passes"].values())
        assert all(check["status"] in {"NOT_STARTED", "HYPOTHESIS", "READY_FOR_FIELD"} for check in item["proofs"].values())
        if item["verification_complete"]:
            assert all(check["status"] in {"CORROBORATED", "VERIFIED"} for check in item["passes"].values())
            assert all(check["status"] == "READY_FOR_FIELD" for check in item["proofs"].values())

def test_partial_evidence_updates_are_source_linked_without_promotion():
    items = {item["canonical_id"]: item for item in records()}
    updates = []
    for batch in evidence_batches():
        updates.extend(batch["candidate_updates"])
    updated_ids = {update["canonical_id"] for update in updates}
    assert updated_ids == set(items)
    assert sum(
        item["verification_status"] in {"IN_PROGRESS", "DESK_VERIFIED_FIELD_PENDING"}
        for item in items.values()
    ) == len(updated_ids)
    for item in items.values():
        for check in item["passes"].values():
            if check["status"] != "NOT_STARTED":
                assert check["source_ids"]
        assert item["ranking_eligible"] is False

def test_every_equal_depth_source_reference_resolves():
    batches = evidence_batches()
    source_ids = {source["source_id"] for source in json.loads(PUBLIC_SOURCES.read_text(encoding="utf-8"))}
    source_ids.update(source["source_id"] for batch in batches for source in batch["sources"])
    referenced = {
        source_id
        for batch in batches
        for update in batch["candidate_updates"]
        for source_id in update["current_source_ids"]
    }
    referenced.update(
        source_id
        for batch in batches
        for update in batch["candidate_updates"]
        for pass_update in update["passes"].values()
        for source_id in pass_update["source_ids"]
    )
    assert referenced <= source_ids

def test_all_candidates_retain_equal_depth_historical_context_without_promotion():
    depths = []
    for item in records():
        context = item["historical_hypothesis"]
        assert context["status"] == "HISTORICAL_ONLY"
        assert len(context["ten_pass_hypotheses"]) == 10
        depths.append(context["depth"])
        if context["depth"] == "SUBSTANTIVE":
            assert all(context[field] for field in ("purpose", "friction", "verbs", "cliche", "moment", "lens", "light", "kill"))
        else:
            assert context["depth"] == "EMPTY_HISTORICAL_SHELL"
        assert len(item["composition_questions"]) == 3
        assert all(question for question in item["composition_questions"])
        assert all(proof["status"] in {"HYPOTHESIS", "READY_FOR_FIELD"} for proof in item["proofs"].values())
        assert item["ranking_eligible"] is False
    assert depths.count("SUBSTANTIVE") > 0
    assert depths.count("EMPTY_HISTORICAL_SHELL") > 0
    assert len(depths) == 81


def test_completed_dossiers_are_substantive_and_still_fail_closed_for_field_use():
    complete = [item for item in records() if item["verification_complete"]]
    assert {item["canonical_id"] for item in complete} >= {
        "lugar-de-la-memoria-lum",
        "centro-cultural-ccori-wasi",
        "puente-de-la-paz-quebrada-de-armendariz",
    }
    for item in complete:
        assert item["verification_status"] == "DESK_VERIFIED_FIELD_PENDING"
        assert len(item["visual_reference_families"]) >= 3
        assert len(item["composition_questions"]) == 3
        assert all(check.get("answer") for check in item["passes"].values())
        for proof in item["proofs"].values():
            assert proof["status"] == "READY_FOR_FIELD"
            assert all(proof.get(field) for field in (
                "position", "camera_height", "orientation", "lens", "exposure_intent",
                "expected_action", "light", "edge_guards", "wait_trigger", "kill_trigger",
                "access_ethics", "fallback",
            ))
        assert item["ranking_eligible"] is False
        assert item["route_eligible"] is False
