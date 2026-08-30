#!/usr/bin/env python3
"""Fetch reviewable OSM geocoding candidates; never publishes them directly."""
from __future__ import annotations

import json
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


def main() -> None:
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    records = []
    for index, candidate in enumerate(candidates):
        query = f'{candidate["name"]}, {candidate["district"]}, Lima, Perú'
        results = fetch(query)
        records.append({
            "canonical_id": candidate["canonical_id"],
            "expected_district": candidate["district"],
            "query": query,
            "status": "REVIEW_REQUIRED",
            "results": [compact(item) for item in results],
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
