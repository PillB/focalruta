#!/usr/bin/env python3
"""Fetch reviewable OSM geocoding candidates; never publishes them directly."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/architecture/candidates.json"
OUTPUT = ROOT / "architectural_photography/research/route_inputs/nominatim_candidates.json"
ENDPOINT = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "FocalRuta architecture research/1.0 (public repository route verification)"
ANCHORS = {
    "parque-3-de-octubre-skatepark-muros-libres": "Parque 3 de Octubre",
    "torres-de-limatambo-supermanzana": "Torres de Limatambo",
    "museo-de-la-electricidad-tranvia": "Museo de la Electricidad",
    "quinta-de-los-libertadores-mnaahp": "Museo Nacional de Arqueología Antropología e Historia del Perú",
    "plaza-a-la-bandera": "Plaza de la Bandera",
    "parque-virginia-candamo": "Parque Candamo",
    "unidad-vecinal-matute-complejo-deportivo": "Unidad Vecinal Matute",
    "quinta-leuro-y-quintas-historicas": "Quinta Leuro",
    "reducto-2-casa-museo-caceres": "Parque Reducto 2",
    "lugar-de-la-memoria-lum": "Lugar de la Memoria",
    "plaza-de-los-libertadores-santa-maria-magdalena": "Iglesia Santa María Magdalena",
    "centro-de-convenciones-estacion-la-cultura": "Estación La Cultura",
    "biblioteca-municipal-y-borde-lagunas-del-olivar": "Biblioteca Municipal de San Isidro",
    "centro-financiero-canaval-y-moreyra-rivera-navarrete": "Avenida Canaval y Moreyra",
    "parque-municipal-y-entorno-civico": "Parque Municipal de Barranco",
    "mac-lima-parque-espejo-de-agua": "Museo de Arte Contemporáneo de Lima",
    "puente-villena-bajada-balta-costa-verde": "Puente Eduardo Villena Rey",
    "casa-raul-porras-barrenechea": "Instituto Raúl Porras Barrenechea",
    "palacio-municipal-y-de-la-cultura-san-isidro": "Municipalidad de San Isidro",
    "museo-larco-jardines": "Museo Larco",
    "bosque-el-olivar": "Bosque El Olivar",
    "ministerio-de-cultura-museo-de-la-nacion": "Museo de la Nación",
    "museo-pedro-de-osma-y-av-pedro-de-osma": "Museo Pedro de Osma",
    "torre-banco-de-la-nacion": "Banco de la Nación sede San Borja",
    "parroquia-nuestra-senora-del-pilar": "Iglesia Nuestra Señora del Pilar",
    "puente-de-los-suspiros-bajada-de-banos": "Puente de los Suspiros",
    "pentagonito-y-bordes-civicos": "Pentagonito",
    "faro-la-marina-parque-antonio-raimondi": "Faro La Marina",
    "palacio-municipal-virgen-milagrosa": "Municipalidad de Miraflores",
    "parque-kennedy-gatos-civic-core": "Parque Kennedy",
    "parque-del-amor-el-beso": "Parque del Amor",
    "larcomar-acantilado": "Larcomar",
    "centro-civico-de-lima-real-plaza": "Centro Cívico de Lima",
    "quinta-heeren-restauracion-2026": "Quinta Heeren",
    "jiron-trujillo-puente-de-piedra": "Jirón Trujillo Rímac",
    "puente-de-la-paz-quebrada-de-armendariz": "Puente de la Paz Miraflores",
    "aulario-104-universidad-ricardo-palma": "Universidad Ricardo Palma",
    "cantagallo-comunidad-shipibo-konibo": "Cantagallo Rímac",
}


def fetch(query: str) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "format": "jsonv2", "limit": 3, "addressdetails": 1})
    request = urllib.request.Request(f"{ENDPOINT}?{params}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def compact(item: dict) -> dict:
    address = item.get("address", {})
    return {
        "osm_type": item.get("osm_type"),
        "osm_id": item.get("osm_id"),
        "latitude": float(item["lat"]),
        "longitude": float(item["lon"]),
        "display_name": item.get("display_name"),
        "category": item.get("category"),
        "type": item.get("type"),
        "district_tokens": [address.get(key) for key in ("city_district", "suburb", "municipality", "city") if address.get(key)],
    }


def query_variants(candidate: dict) -> list[str]:
    anchor = ANCHORS.get(candidate["canonical_id"], candidate["name"])
    first_clause = re.split(r"\s+(?:\+|/|&|·|y)\s+|\s*\([^)]*\)", candidate["name"], maxsplit=1)[0]
    names = list(dict.fromkeys((anchor, first_clause, candidate["name"])))
    return [f'{name}, {candidate["district"]}, Lima, Perú' for name in names]


def collect_results(candidate: dict) -> tuple[str, list[dict]]:
    for query in query_variants(candidate):
        results = fetch(query)
        if results:
            return query, [compact(item) for item in results]
        time.sleep(1.1)
    return query_variants(candidate)[0], []


def main() -> None:
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    records = []
    for index, candidate in enumerate(candidates):
        query, results = collect_results(candidate)
        records.append({
            "canonical_id": candidate["canonical_id"],
            "expected_district": candidate["district"],
            "query": query,
            "status": "REVIEW_REQUIRED",
            "results": results,
        })
        if index + 1 < len(candidates):
            time.sleep(1.1)
    payload = {
        "source": ENDPOINT,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "publication_gate": "Human review plus district polygon containment required",
        "records": records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} review records to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
