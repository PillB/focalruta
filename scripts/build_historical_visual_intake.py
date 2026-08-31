#!/usr/bin/env python3
"""Extract historical image leads without treating them as verified visual evidence."""
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "architectural_photography/FocalRuta_Arquitectura_en_Foco_2026_Bonilla_Urban_Lens_OS.html"
CANDIDATES = ROOT / "data/architecture/candidates.json"
OUTPUT = ROOT / "architectural_photography/research/visual_forensics/historical_visual_intake.json"

ALIASES = {
    "malecon de miraflores larcomar": "larcomar-acantilado",
    "palacio municipal de miraflores": "palacio-municipal-virgen-milagrosa",
    "puente de los suspiros": "puente-de-los-suspiros-bajada-de-banos",
    "centro cultural de la nacion complex": "ministerio-de-cultura-museo-de-la-nacion",
    "cuartel general del ejercito pentagonito": "pentagonito-y-bordes-civicos",
    "museo de arte contemporaneo mac": "mac-lima-parque-espejo-de-agua",
    "faro la marina miraflores lighthouse": "faro-la-marina-parque-antonio-raimondi",
    "iglesia virgen milagrosa": "palacio-municipal-virgen-milagrosa",
    "torres de camino real": "torres-centro-empresarial-camino-real",
    "parque kennedy parque de los gatos": "parque-kennedy-gatos-civic-core",
    "bajada de banos": "puente-de-los-suspiros-bajada-de-banos",
    "parque reducto n 2 museo andres avelino caceres": "reducto-2-casa-museo-caceres",
    "parque tradiciones ricardo palma park": "parque-tradiciones-ricardo-palma",
    "museo de la electricidad tranvia de barranco": "museo-de-la-electricidad-tranvia",
    "puente villena rey": "puente-villena-bajada-balta-costa-verde",
}

def normalized(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

def json_variable(source, name):
    match = re.search(rf"const {name}=", source)
    if not match:
        raise ValueError(f"missing historical variable: {name}")
    return json.JSONDecoder().raw_decode(source[match.end():])[0]

def candidate_lookup(candidates):
    lookup = {normalized(item["name"]): item["canonical_id"] for item in candidates}
    lookup.update(ALIASES)
    return lookup

def reference(row, name, image_key, dataset):
    url = row.get(image_key, "")
    host = urlparse(url).hostname or ""
    return {
        "historical_dataset": dataset,
        "historical_name": name,
        "image_url": url,
        "host": host,
        "provenance_status": "PROXY_UNRESOLVED" if host == "pplx-res.cloudinary.com" else "DIRECT_HOST_UNVERIFIED",
        "rights_status": "UNRESOLVED",
        "visual_evidence_eligible": False,
        "reason": "Historical image lead lacks verified author/page/date/rights and viewpoint analysis.",
    }

def main():
    source = HTML.read_text(encoding="utf-8")
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    lookup = candidate_lookup(candidates)
    grouped = {item["canonical_id"]: [] for item in candidates}
    unmatched = []
    datasets = [("deep40Data", "name", "img"), ("storyData", "title", "image")]
    for dataset, name_key, image_key in datasets:
        for row in json_variable(source, dataset):
            if not row.get(image_key):
                continue
            name = row[name_key]
            canonical_id = lookup.get(normalized(name))
            item = reference(row, name, image_key, dataset)
            if canonical_id:
                grouped[canonical_id].append(item)
            else:
                unmatched.append(item)
    payload = {
        "ledger_id": "HISTORICAL-VISUAL-INTAKE-2026-08-28",
        "status": "DISCOVERY_ONLY_NOT_VERIFICATION_EVIDENCE",
        "candidate_count": len(candidates),
        "records": [{"canonical_id": key, "references": value} for key, value in grouped.items()],
        "unmatched_or_out_of_scope": unmatched,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": len(grouped), "leads": sum(map(len, grouped.values())), "unmatched": len(unmatched)}))

if __name__ == "__main__":
    main()
