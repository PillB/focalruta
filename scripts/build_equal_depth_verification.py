#!/usr/bin/env python3
"""Build the fail-closed equal-depth verification ledger for every candidate."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/architecture/candidates.json"
OUTPUT = ROOT / "architectural_photography/research/locations/equal_depth_verification.json"
EVIDENCE_DIR = ROOT / "architectural_photography/research/locations"
EVIDENCE_GLOB = "equal_depth_evidence*.json"
VISUAL_EVIDENCE_GLOB = "visual_reference_evidence*.json"
MASTER82 = ROOT / "architectural_photography/FocalRuta_Bonilla_Master82_Ranking.json"
PASSES = [
    "source_truth", "original_spatial_contract", "current_life",
    "human_verbs_or_meaningful_absence", "architectural_causality",
    "visual_forensic_saturation", "light_material_geometry",
    "position_then_optics", "moment_logistics_ethics", "one_frame_contest_test",
]
PROOFS = ["A_STRUCTURE", "B_HABITAR", "C_ANTI_POSTAL", "D_LIGHT_MATERIAL", "E_ONE_FRAME_STORY"]

def empty_checklist(names):
    return {name: {"status": "NOT_STARTED", "source_ids": []} for name in names}

def record(candidate):
    return {
        "canonical_id": candidate["canonical_id"], "name": candidate["name"],
        "district": candidate["district"], "verification_status": "NOT_STARTED",
        "passes": empty_checklist(PASSES), "proofs": empty_checklist(PROOFS),
        "visual_reference_families": [], "composition_questions": [],
        "historical_hypothesis": {},
        "current_source_ids": [], "contradictions": [],
        "verification_complete": False, "ranking_eligible": False, "route_eligible": False,
    }

def normalized(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

def historical_by_name():
    rows = json.loads(MASTER82.read_text(encoding="utf-8"))
    return {normalized(row["name"]): row for row in rows}

def proof_hypotheses(row):
    authored = {shot["label"][0]: shot for shot in row.get("shots", [])}
    fallback = {
        "A": {"label": "A · ESTRUCTURA", "lens": row.get("lens", ""), "plan": row.get("purpose", ""), "gate": "¿La estructura se entiende sin depender del evento humano?"},
        "B": {"label": "B · HABITAR", "lens": row.get("lens", ""), "plan": row.get("moment", ""), "gate": "¿El verbo humano cambia el significado y no solo aporta escala?"},
        "C": {"label": "C · ANTI-POSTAL", "lens": row.get("lens", ""), "plan": row.get("cliche", ""), "gate": row.get("question", "")},
        "D": {"label": "D · LUZ / MATERIAL", "lens": row.get("lens", ""), "plan": row.get("light", ""), "gate": "¿La luz o el material revela arquitectura y no solo atmósfera?"},
        "E": {"label": "E · HISTORIA EN UN CUADRO", "lens": row.get("lens", ""), "plan": row.get("moment", ""), "gate": row.get("question", "")},
    }
    fallback.update(authored)
    keys = dict(zip("ABCDE", PROOFS))
    return {keys[key]: {"status": "HYPOTHESIS", "source_ids": row.get("sourceIds", []), **fallback[key]} for key in keys}

def ten_pass_hypotheses(row):
    authored = row.get("passes", [])
    if authored:
        return authored
    values = [
        ("01", "Contrato original", row.get("purpose", "")),
        ("02", "Vida actual", row.get("currentLife", "")),
        ("03", "Fricción", row.get("friction", "")),
        ("04", "Verbos humanos", row.get("verbs", "")),
        ("05", "Cliché dominante", row.get("cliche", "")),
        ("06", "Pregunta ganable", row.get("question", "")),
        ("07", "Momento decisivo", row.get("moment", "")),
        ("08", "Óptica real", row.get("lens", "")),
        ("09", "Luz", row.get("light", "")),
        ("10", "Kill condition", row.get("kill", "")),
    ]
    return [{"n": number, "label": label, "text": value, "status": "HISTORICAL_ONLY" if value else "NOT_STARTED"} for number, label, value in values]

def historical_depth(row):
    fields = ("purpose", "friction", "verbs", "cliche", "moment", "lens", "light", "kill")
    return "SUBSTANTIVE" if all(row.get(field) for field in fields) else "EMPTY_HISTORICAL_SHELL"

def apply_historical_hypotheses(records):
    rows = historical_by_name()
    for target in records:
        keys = [normalized(target["name"])]
        if target["canonical_id"] == "unidad-vecinal-3":
            keys = [normalized("Unidad Vecinal Nº3"), normalized("Unidad Vecinal N.º 3")]
        row = next((rows[key] for key in keys if key in rows), None)
        if row is None:
            continue
        target["historical_hypothesis"] = {
            "status": "HISTORICAL_ONLY", "depth": historical_depth(row), "purpose": row.get("purpose", ""),
            "current_life_claim": row.get("currentLife", ""), "friction": row.get("friction", ""),
            "verbs": row.get("verbs", ""), "cliche": row.get("cliche", ""),
            "moment": row.get("moment", ""), "lens": row.get("lens", ""),
            "light": row.get("light", ""), "kill": row.get("kill", ""),
            "ten_pass_hypotheses": ten_pass_hypotheses(row),
        }
        target["composition_questions"] = [
            row.get("question") or f"¿Qué relación arquitectónica específica en {target['name']} puede leerse sin pie de foto?",
            "¿Qué borde, fondo o superposición destruiría la lectura principal?",
            "¿Qué cambia realmente al mover la cámara antes de cambiar focal?",
        ]
        target["proofs"] = proof_hypotheses(row)

def apply_evidence(records):
    by_id = {item["canonical_id"]: item for item in records}
    for evidence_path in sorted(EVIDENCE_DIR.glob(EVIDENCE_GLOB)):
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        for update in evidence["candidate_updates"]:
            target = by_id[update["canonical_id"]]
            target["verification_status"] = "IN_PROGRESS"
            target["current_source_ids"] = sorted(set(target["current_source_ids"] + update["current_source_ids"]))
            target["contradictions"] = sorted(set(target["contradictions"] + update.get("contradictions", [])))
            for pass_name, pass_update in update["passes"].items():
                target["passes"][pass_name] = pass_update

def apply_visual_evidence(records):
    by_id = {item["canonical_id"]: item for item in records}
    for evidence_path in sorted(EVIDENCE_DIR.glob(VISUAL_EVIDENCE_GLOB)):
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        for update in evidence["candidate_updates"]:
            target = by_id[update["canonical_id"]]
            target["visual_reference_families"] = update["reference_families"]

def main():
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    records = [record(candidate) for candidate in candidates]
    apply_historical_hypotheses(records)
    apply_evidence(records)
    apply_visual_evidence(records)
    payload = {
        "ledger_id": "EQUAL-DEPTH-81-2026-08-28", "candidate_count": len(candidates),
        "completion_rule": "All ten passes, five proofs, current sources, visual families and composition questions must be VERIFIED or CORROBORATED.",
        "records": records,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(payload["records"]), "complete": 0}))

if __name__ == "__main__":
    main()
