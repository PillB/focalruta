from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "challenges" / "arquitectura-en-foco" / "index.html"


def test_generated_page_is_evergreen_and_keeps_a_brief_firewall():
    text = PAGE.read_text(encoding="utf-8")
    assert "30 de agosto de 2026" not in text
    assert "DECODIFICADOR DEL ENCARGO" in text
    assert all(token in text for token in ("Elegibilidad", "Tema", "edición/IA", "zona horaria"))
    assert "<noscript>" in text
    assert text.count('id="ai-firewall"') == 1


def test_generated_page_has_local_brief_controls_without_upload_endpoint():
    text = PAGE.read_text(encoding="utf-8")
    for control in ("brief-source", "brief-theme", "brief-files", "brief-editing", "brief-rights", "brief-deadline"):
        assert f'id="{control}"' in text
    assert "architecture-preflight" in text
    assert "fetch(" not in text
    assert "XMLHttpRequest" not in text
