from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "challenges" / "arquitectura-en-foco" / "index.html"


def test_generated_page_contains_critical_no_js_rules_and_firewall():
    text = PAGE.read_text(encoding="utf-8")
    assert "5–25 MB" in text
    assert "30 de agosto de 2026 · 23:59" in text
    assert "Cristián Aninat" in text and "Hans Stoll" in text and "Camilo Monzón" in text
    assert "<noscript>" in text
    assert text.count('id="ai-firewall"') == 1


def test_generated_page_has_local_preflight_controls_without_upload_endpoint():
    text = PAGE.read_text(encoding="utf-8")
    assert 'type="file"' in text
    assert "architecture-preflight" in text
    assert "fetch(" not in text
    assert "XMLHttpRequest" not in text
