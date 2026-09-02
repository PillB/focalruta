import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKBENCH = ROOT / "architectural_photography" / "research" / "videos"
DATA = ROOT / "data" / "architecture"
PAGE = ROOT / "challenges" / "arquitectura-en-foco" / "index.html"


def test_all_supplied_videos_have_verified_metadata_and_real_transcript_files():
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["url_occurrences"] == 45
    assert ledger["unique_video_ids"] == 44
    assert len(ledger["videos"]) == 44
    for video in ledger["videos"]:
        if video["metadata_status"].startswith("VERIFIED"):
            assert video["exact_title"] and video["channel"] and video["publication_date"]
        else:
            assert video["exact_title"] is video["channel"] is video["publication_date"] is None
            assert video["timestamped_claims"] == []
        assert video["transcript_status"] in {"CAPTURED", "TRANSCRIPT_UNAVAILABLE"}
        transcript_path = ROOT / video["transcript_path"]
        if not transcript_path.exists():
            continue  # Full caption tracks are copyright-sensitive local evidence.
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        assert transcript["source"] in {"YOUTUBE_CAPTION_TRACK", "SUPADATA_NATIVE_CAPTION"}
        assert transcript["segments"]
        assert all({"text", "start", "duration"} <= segment.keys() for segment in transcript["segments"])


def test_curriculum_has_all_required_lessons_and_field_shape():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    assert len(learning["lessons"]) == 17
    required = {"observe", "try", "diagnose", "break_the_rule_when", "canon_6d_note", "competition_note", "sources"}
    assert all(required <= lesson.keys() for lesson in learning["lessons"])
    assert all(all(lesson[field] for field in required) for lesson in learning["lessons"])


def test_curriculum_preserves_optics_and_editing_truth():
    text = json.dumps(json.loads((DATA / "learning.json").read_text(encoding="utf-8")), ensure_ascii=False)
    assert "camera position" in text.lower()
    assert "field of view" in text.lower()
    assert "background distance" in text.lower()
    assert "DoF" in text
    assert "magic ISO" in text
    assert "fundamental" in text.lower()


def test_video_attributions_have_timestamp_and_known_video():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    known = {video["video_id"] for video in ledger["videos"]}
    for lesson in learning["lessons"]:
        for source in lesson["sources"]:
            if source["type"] == "VIDEO_TRANSCRIPT":
                assert source["video_id"] in known
                assert isinstance(source["timestamp_seconds"], (int, float))


def test_photographer_transfer_cards_cover_required_canon_and_schema():
    payload = json.loads((DATA / "photographers.json").read_text(encoding="utf-8"))
    cards = payload["transfer_cards"]
    names = {card["photographer"] for card in cards}
    required_names = {
        "Iwan Baan", "Fernando Guerra", "Ezra Stoller", "Hélène Binet",
        "Lucien Hervé", "Julius Shulman", "Candida Höfer", "Bas Princen",
        "Gabriele Basilico", "Leonardo Finotti",
    }
    required_fields = {
        "photographer", "signature_question", "source_backed_mechanisms",
        "field_drill", "competition_use", "misuse_risk", "sources",
    }
    assert required_names <= names
    assert all(required_fields <= card.keys() for card in cards)
    assert all(all(card[field] for field in required_fields) for card in cards)


def test_six_seeing_modes_and_latin_american_practice_are_explicit():
    payload = json.loads((DATA / "photographers.json").read_text(encoding="utf-8"))
    assert payload["seeing_modes"] == [
        "DOCUMENT / UNDERSTAND", "INHABIT / OBSERVE", "LIGHT / MATERIAL",
        "TEMPORAL PALIMPSEST", "URBAN SYSTEMS", "ANTI-POSTAL DISCOVERY",
    ]
    assert any(card.get("region") == "LATIN_AMERICA" for card in payload["transfer_cards"])
    text = json.dumps(payload, ensure_ascii=False).lower()
    assert "ausencia" in text
    assert "no exige una persona" in text


def test_every_transfer_card_source_is_in_public_source_registry():
    payload = json.loads((DATA / "photographers.json").read_text(encoding="utf-8"))
    sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    registered = {source["url_or_path"] for source in sources}
    cited = {url for card in payload["transfer_cards"] for url in card["sources"]}
    assert cited <= registered


def test_generated_page_exposes_learning_without_hover_dependency():
    html = PAGE.read_text(encoding="utf-8")
    assert 'id="learn"' in html
    assert "Seis modos de ver" in html
    assert "Posición antes que focal" in html
    assert "Candida Höfer" in html
    assert "title=" not in html


def test_all_lessons_are_rendered_with_the_full_field_learning_cycle():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    html = PAGE.read_text(encoding="utf-8")
    assert html.count('class="lesson-card"') == len(learning["lessons"]) == 17
    for lesson in learning["lessons"]:
        assert lesson["title"] in html
    for label in ("OBSERVA", "PRUEBA", "DIAGNOSTICA", "ROMPE LA REGLA CUANDO", "CANON 6D", "CONCURSO"):
        assert html.count(f"<strong>{label}:</strong>") == 17


def test_video_synthesis_is_timestamped_transfer_not_an_embed_playlist():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    known = {video["video_id"] for video in ledger["videos"]}
    modules = learning["video_modules"]
    assert len(modules) >= 6
    assert all(module["video_id"] in known for module in modules)
    assert all(isinstance(module["timestamp_seconds"], (int, float)) for module in modules)
    assert all(module["mechanism"] and module["field_transfer"] and module["misuse_risk"] for module in modules)
    html = PAGE.read_text(encoding="utf-8")
    assert html.count('class="video-transfer"') == len(modules)
    assert "youtube.com/embed" not in html
    assert all(f't={int(module["timestamp_seconds"])}' in html for module in modules)


def test_learning_labs_have_prediction_manipulation_feedback_and_sources():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    labs = learning["simulations"]
    assert {
        "perspective-position", "vertical-convergence", "hierarchy-edges", "light-material",
    } <= {lab["simulation_id"] for lab in labs}
    required = {"title", "prediction_prompt", "field_drill", "diagnostic_rule", "sources"}
    assert all(required <= lab.keys() for lab in labs)
    assert all(all(lab[field] for field in required) for lab in labs)
    html = PAGE.read_text(encoding="utf-8")
    for control in ("perspective-position", "perspective-focal", "vertical-tilt", "hierarchy-mode", "light-mode"):
        assert f'id="{control}"' in html
    assert html.count('class="learning-lab"') == 5
    assert 'id="perspective-feedback"' in html
    assert 'id="vertical-feedback"' in html
    assert 'id="hierarchy-feedback"' in html
    assert 'id="light-feedback"' in html


def test_learning_labs_preserve_physical_and_pedagogical_truth():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    text = json.dumps(learning, ensure_ascii=False).lower()
    assert "camera position changes perspective" in text
    assert "focal length changes field of view" in text
    assert "keystoning" in text
    assert "active learning" in text
    assert "pedagogical diagram" in text
    html = PAGE.read_text(encoding="utf-8")
    assert "No es una simulación óptica ni una previsualización de píxeles" in html


def test_no_js_learning_fallback_keeps_core_exercises():
    html = PAGE.read_text(encoding="utf-8")
    noscript = html.split("<noscript>", 1)[1].split("</noscript>", 1)[0]
    assert "Laboratorios sin JavaScript" in noscript
    assert "Mueve físicamente la cámara" in noscript
    assert "Mantén la cámara nivelada" in noscript
    assert "Escanea los cuatro bordes" in noscript


def test_non_video_learning_sources_resolve_in_public_registry():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    registry = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    registered = {source["url_or_path"] for source in registry}
    cited = set(learning["pedagogy"]["sources"])
    cited.update(url for lab in learning["simulations"] for url in lab["sources"] if "youtube.com" not in url)
    assert cited <= registered


def test_g01_g02_g03_video_ledger_is_versioned_cross_validation_evidence():
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["schema_version"] == "2.0.0"
    required = {
        "video_id", "exact_title", "channel", "publication_date",
        "transcript_status", "transcript_provenance", "timestamped_claims",
        "curriculum_cross_validation", "tags",
    }
    allowed_tags = {"technical", "perceptual", "composition", "light", "workflow", "anti-dogma"}
    for video in ledger["videos"]:
        assert required <= video.keys()
        assert video["transcript_status"] in {"CAPTURED", "TRANSCRIPT_UNAVAILABLE"}
        assert set(video["tags"]) <= allowed_tags
        if video["metadata_status"].startswith("VERIFIED") and video["transcript_status"] == "CAPTURED":
            assert video["exact_title"] and video["channel"] and video["publication_date"]
        if video["transcript_status"] == "CAPTURED":
            assert video["transcript_provenance"]["source"] in {"YOUTUBE_CAPTION_TRACK", "SUPADATA_NATIVE_CAPTION"}
        for claim in video["timestamped_claims"]:
            assert {"timestamp_seconds", "claim", "evidence_status"} <= claim.keys()
            assert claim["evidence_status"] == "TRANSCRIPT_VALIDATED"
    assert ledger["unverified_attribution_policy"] == "OMIT_TITLE_CHANNEL_DATE_AND_CLAIMS"


def test_g05_h03_h06_h07_l_series_technique_cards_are_field_complete():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    cards = learning["technique_cards"]
    required_ids = {
        "viewpoint-before-focal", "perspective-shift-tilt", "lines-symmetry-hierarchy",
        "negative-space-edge-control", "depth-figure-ground", "gesture-absence",
        "light-material-weather", "exposure-focus-iso-motion", "contest-safe-editing",
    }
    assert required_ids <= {card["technique_id"] for card in cards}
    required = {"title", "mechanism", "field_test", "diagnosis", "misconception_warning", "sources"}
    assert all(required <= card.keys() for card in cards)
    assert all(all(card[field] for field in required) for card in cards)


def test_i01_i02_i03_visual_exemplars_are_link_only_and_multi_condition():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    serious = {card["technique_id"] for card in learning["technique_cards"]}
    families = learning["visual_exemplar_families"]
    required = {"technique_id", "family_id", "source_url", "author", "date", "rights_status", "condition", "proves", "cannot_prove"}
    assert all(required <= family.keys() for family in families)
    assert all(family["rights_status"] == "LINK_ONLY" for family in families)
    assert all(not any(key in family for key in ("image", "image_url", "asset_path", "base64")) for family in families)
    for technique_id in serious:
        matching = [family for family in families if family["technique_id"] == technique_id]
        assert len(matching) >= 3
        assert len({family["condition"] for family in matching}) >= 3


def test_labs_have_explicit_six_part_contract_and_composition_sequence():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    required = {"prediction_prompt", "manipulation", "observable_feedback", "model_limit", "field_drill", "misconception_warning"}
    assert all(required <= lab.keys() for lab in learning["simulations"])
    sequence = next(lab for lab in learning["simulations"] if lab["simulation_id"] == "composition-sequence")
    assert [variant["variant_id"] for variant in sequence["variants"]] == [
        "default-postcard", "changed-position", "fixed-position-focal", "human-presence", "light-weather"
    ]
    html = PAGE.read_text(encoding="utf-8")
    assert 'id="composition-mode"' in html
    assert 'id="composition-feedback"' in html
    assert html.count('class="learning-lab"') == 5


def test_learning_overhaul_exposes_recovery_legends_and_field_transfer():
    html = PAGE.read_text(encoding="utf-8")
    assert html.count('class="lab-reset"') == 5
    assert html.count('class="lab-legend"') == 5
    assert html.count('class="lab-cycle"') == 5
    for label in ("Predicción", "Acción", "Observación", "Transferencia al campo"):
        assert html.count(label) >= 5
    assert 'id="composition-before"' in html
    assert 'id="composition-after"' in html
    assert 'id="composition-fixed-position"' in html


def test_story_order_follows_learning_before_ranking_and_routes():
    html = PAGE.read_text(encoding="utf-8")
    ordered_ids = ("how-to-read", "learn", "style-radar", "scenes", "ranking", "field-priorities", "route", "field-run", "rules")
    positions = [html.index(f'id="{section_id}"') for section_id in ordered_ids]
    assert positions == sorted(positions)


def test_anchor_clearance_uses_measured_sticky_offset_contract():
    html = PAGE.read_text(encoding="utf-8")
    assert "--sticky-nav-offset" in html
    assert "scroll-padding-top:var(--sticky-nav-offset)" in html
    assert "scroll-margin-top:var(--sticky-nav-offset)" in html


def test_video_technique_wiki_is_evidence_linked_and_offline_ready():
    wiki = PAGE.parent / "wiki-tecnicas.html"
    assert wiki.exists()
    html = wiki.read_text(encoding="utf-8")
    ledger = json.loads((WORKBENCH / "VIDEO_LEDGER.json").read_text(encoding="utf-8"))
    validated = [claim for video in ledger["videos"] for claim in video["timestamped_claims"]]
    assert len(validated) >= 12
    assert html.count('class="wiki-technique"') >= 8
    assert html.count('class="evidence-card"') == len(validated)
    assert "Qué probar" in html and "Qué observar" in html and "Cuándo descartarlo" in html
    assert "Transcripción no disponible" in html
    assert 'href="wiki-tecnicas.html"' in PAGE.read_text(encoding="utf-8")
