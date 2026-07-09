from pathlib import Path
from bot.grounding import (
    extract_slide_text, load_grounding, build_system, SPANISH_INSTRUCTIONS,
    read_grounding_list,
)


def _write_list(repo_root: Path, body: str) -> None:
    (repo_root / "bot").mkdir(exist_ok=True)
    (repo_root / "bot" / "grounding_files.txt").write_text(body, encoding="utf-8")


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

def test_load_grounding_warns_on_missing_file(tmp_path, caplog):
    import logging
    (tmp_path / "README.md").write_text("body", encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        load_grounding(tmp_path)
    assert any("README.md" not in r.getMessage() and "not found" in r.getMessage()
               for r in caplog.records)   # e.g. docs/workshop-plan.md missing warned


def test_read_grounding_list_parses_comments_and_blanks(tmp_path):
    _write_list(tmp_path, "# a comment\n\nREADME.md\n  docs/x.md  # trailing comment\n")
    assert read_grounding_list(tmp_path) == ["README.md", "docs/x.md"]


def test_read_grounding_list_falls_back_when_absent(tmp_path):
    # no bot/grounding_files.txt -> non-empty built-in defaults
    files = read_grounding_list(tmp_path)
    assert "README.md" in files and len(files) > 1


def test_load_grounding_uses_list_file_and_ignores_unlisted(tmp_path):
    _write_list(tmp_path, "notes.md\n")
    (tmp_path / "notes.md").write_text("listed body", encoding="utf-8")
    (tmp_path / "README.md").write_text("unlisted body", encoding="utf-8")
    text = load_grounding(tmp_path)
    assert "listed body" in text
    assert "unlisted body" not in text        # only files in the list are read


def test_load_grounding_strips_html_from_list(tmp_path):
    _write_list(tmp_path, "deck.html\n")
    (tmp_path / "deck.html").write_text("<h1>Titulo</h1><p>cuerpo</p>", encoding="utf-8")
    text = load_grounding(tmp_path)
    assert "Titulo" in text and "cuerpo" in text
    assert "<" not in text                     # tags stripped
