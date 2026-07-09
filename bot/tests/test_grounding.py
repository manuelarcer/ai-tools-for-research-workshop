from pathlib import Path
from bot.grounding import extract_slide_text, load_grounding, build_system, SPANISH_INSTRUCTIONS


def test_extract_slide_text_strips_tags_and_scripts():
    html = "<html><head><style>.x{color:red}</style><script>var a=1</script>"\
           "</head><body><h1>Hola</h1><p>Mundo  &amp; más</p></body></html>"
    out = extract_slide_text(html)
    assert "Hola" in out
    assert "Mundo & más" in out
    assert "color:red" not in out
    assert "var a=1" not in out
    assert "<" not in out

def test_load_grounding_concatenates_existing_and_skips_missing(tmp_path):
    (tmp_path / "README.md").write_text("readme body", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "workshop-plan.md").write_text("plan body", encoding="utf-8")
    text = load_grounding(tmp_path)
    assert "readme body" in text
    assert "plan body" in text
    assert "## README.md" in text          # header present
    # missing files (exercise, deck) simply absent, no crash
    assert "exercise" not in text or "beer" not in text

def test_build_system_marks_grounding_cacheable():
    blocks = build_system("GROUNDING")
    assert blocks[0]["text"] == SPANISH_INSTRUCTIONS
    assert blocks[1]["text"] == "GROUNDING"
    assert blocks[1]["cache_control"] == {"type": "ephemeral"}
