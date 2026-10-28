"""Y20: every architecture card says something about its own place, and no number pretends to be a probability.

The red team on PR #24 read the 87 ranking cards and found the same four paragraphs on every
one: the research for each place (why it survives, the strongest counterargument, the scene,
the view, the light, the fallback) sat in ranking.json in English and never reached the page.
The status line printed the evidence score as "confianza 80%" although ranking.json says
calibrated_probability is false. Two route stops were named "150" and "Viettel Perú" (the
first token of a geocoder hit), the offline maps drew straight lines between stops under a
caption that says they show the walked path, a single-stop map put its pin in a corner, and
the masters' questions read as quotes. These checks read the published page and map files.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from html import unescape
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "challenges/arquitectura-en-foco"
PAGE = (GUIDE / "index.html").read_text(encoding="utf-8")
RANKING = json.loads((ROOT / "data/architecture/ranking.json").read_text(encoding="utf-8"))
SPANISH = json.loads((ROOT / "data/architecture/ranking_es.json").read_text(encoding="utf-8")) \
    if (ROOT / "data/architecture/ranking_es.json").exists() else {"places": {}, "light": {}}
ROUTES = json.loads((ROOT / "data/architecture/routes.json").read_text(encoding="utf-8"))
NAMES = {item["canonical_id"]: item["name"]
         for item in json.loads((ROOT / "data/architecture/candidates.json").read_text(encoding="utf-8"))}
LIGHTS = {text[0].upper() + text[1:] for text in SPANISH["light"].values()}
CARD_SECTIONS = ("ranking", "field-priorities", "scenes", "style-radar")
MOST_CARDS_PER_SENTENCE = 4


def section(anchor: str) -> str:
    match = re.search(rf'<section id="{anchor}"[^>]*>(.*?)</section>', PAGE, re.S)
    assert match, f"no section #{anchor}"
    return match.group(1)


def cards(anchor: str) -> list[str]:
    return re.findall(r'<article class="scene".*?</article>', section(anchor), re.S)


def sentences(card: str) -> set[str]:
    paragraphs = re.findall(r'<p(?! class="(?:status|eyebrow|source-links)")[^>]*>(.*?)</p>', card, re.S)
    text = " ".join(unescape(re.sub(r"<strong>[^<]*</strong>|<[^>]+>", " ", p)) for p in paragraphs)
    found = {s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if len(s.strip()) > 12}
    # The light is a category (34 kinds for 87 places): sharing one is data, not boilerplate.
    return {s for s in found if s.rstrip(".") not in LIGHTS}


def test_y20_no_sentence_repeats_across_the_place_cards():
    repeated = {}
    for anchor in CARD_SECTIONS:
        counts = Counter(s for card in cards(anchor) for s in sentences(card))
        repeated.update({f"#{anchor}: {s[:60]}": n for s, n in counts.items() if n > MOST_CARDS_PER_SENTENCE})
    assert not repeated, repeated


def test_y20_each_ranking_card_carries_its_own_research_and_light():
    by_name = {re.search(r"<h3>(.*?)</h3>", card).group(1): card for card in cards("ranking")}
    missing = []
    for item in RANKING["results"]:
        card = unescape(by_name[item["name"].replace("&", "&amp;")])
        spanish = SPANISH["places"].get(item["canonical_id"], {})
        wanted = [spanish.get("entra"), spanish.get("refuta"), spanish.get("escena"), SPANISH["light"].get(item["exact_light"])]
        if not all(wanted) or not all(text in card for text in wanted) or item["exact_light"] in card:
            missing.append(item["canonical_id"])
    assert len(by_name) == 87 and not missing, missing[:10]


def test_y20_the_evidence_score_is_not_shown_as_a_probability():
    percent = re.findall(r"confianza[^<]{0,40}?\d+\s*%", PAGE)
    statuses = [re.search(r'<p class="status">(.*?)</p>', card).group(1) for a in ("ranking", "field-priorities") for card in cards(a)]
    scored = [s for s in statuses if re.search(r"evidencia \d{1,3}/100", s)]
    explained = "no es una probabilidad" in section("ranking")
    assert not percent and len(scored) == len(statuses) == 92 and explained, (percent[:3], len(scored), explained)


def test_y20_every_route_stop_is_named_after_its_place():
    listed = re.findall(r'<li><strong>\d+\. (.*?)</strong><br>[^<]*<br><code>(-?[\d.]+, -?[\d.]+)</code>', section("route"))
    shown = {coordinates: name for name, coordinates in listed}
    wrong = []
    for layer in ROUTES["district_layers"]:
        offline = (ROOT / layer["offline_map_path"]).read_text(encoding="utf-8")
        kml = ElementTree.parse(ROOT / layer["kml_path"]).getroot()
        kml_names = {p.findtext("{http://www.opengis.net/kml/2.2}name") for p in kml.iter("{http://www.opengis.net/kml/2.2}Placemark")}
        geojson = json.loads((ROOT / layer["geojson_path"]).read_text(encoding="utf-8"))
        geo_names = {f["properties"].get("name") for f in geojson["features"] if f["geometry"]["type"] == "Point"}
        for index, stop in enumerate(layer["stops"], 1):
            name = NAMES[stop["canonical_id"]]
            label = f"{index}. {name}".replace("&", "&amp;")
            if label not in offline or name not in kml_names or name not in geo_names or stop["address"].startswith("Viettel") or \
                    unescape(shown.get(f'{stop["latitude"]}, {stop["longitude"]}', "")) != name:
                wrong.append((layer["layer_id"], stop["name"], name))
    assert not wrong, wrong[:10]


def polyline_points(page: str) -> int:
    return sum(len(points.split()) for points in re.findall(r'<polyline points="([^"]*)"', page))


def test_y20_offline_maps_draw_the_walked_path_and_centre_a_lone_stop():
    wrong = []
    for layer in ROUTES["district_layers"]:
        page = (ROOT / layer["offline_map_path"]).read_text(encoding="utf-8")
        walked = sum(len(leg["geometry"]["coordinates"]) for leg in layer["legs"])
        if layer["legs"] and polyline_points(page) != walked:
            wrong.append((layer["layer_id"], polyline_points(page), walked))
        if not layer["legs"]:
            centred = re.search(r'<circle cx="400\.0" cy="200\.0"', page)
            if not centred or "la línea muestra" in page or "<polyline" in page:
                wrong.append((layer["layer_id"], "lone stop"))
    assert not wrong, wrong[:10]


def test_y20_the_masters_questions_are_not_presented_as_quotes():
    learn = section("learn")
    block = learn[learn.index("Preguntas"):]
    masters = re.findall(r'<article class="scene"><h3>.*?</article>', block, re.S)
    assert "no son citas" in block[:600] and len(masters) == 10 and all('<a href="http' in card for card in masters)
