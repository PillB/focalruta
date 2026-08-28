import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "data" / "architecture" / "scene_dossier_schema.json"


def test_scene_dossier_schema_requires_all_ten_substantive_passes():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = schema["properties"]["passes"]["required"]
    assert required == [
        "source_truth",
        "original_spatial_contract",
        "current_life",
        "human_verbs_or_meaningful_absence",
        "architectural_causality",
        "visual_forensic_saturation",
        "light_material_geometry",
        "position_then_optics",
        "moment_logistics_ethics",
        "one_frame_contest_test",
    ]


def test_each_abcde_proof_requires_field_execution_and_kill_information():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    proof = schema["$defs"]["proof"]
    assert proof["required"] == [
        "proof_type", "position", "camera_height", "orientation", "focal",
        "exposure_intent", "expected_action", "light_condition", "edge_guards",
        "wait_trigger", "kill_trigger", "access_ethics", "fallback",
    ]
    proofs = schema["properties"]["proofs"]
    assert proofs["minItems"] == proofs["maxItems"] == 5


def test_schema_keeps_research_queue_separate_from_ranking_and_route():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = schema["required"]
    assert "evidence_status" in required
    assert "ranking_eligible" in required
    assert "route_eligible" in required
    assert schema["properties"]["ranking_eligible"]["const"] is False
    assert schema["properties"]["route_eligible"]["const"] is False
    assert "current_source_ids" in required
    assert "access_last_verified_at" in required


def test_schema_forbids_uncontrolled_extra_fields_and_placeholder_statuses():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["evidence_status"]["enum"] == [
        "RESEARCH_QUEUE", "DOSSIER_PARTIAL", "DOSSIER_VERIFIED"
    ]
