"""The content/ contract: one '##' is one slide, and every slide states a claim.

Both consumers depend on this shape — Claude Design turns each '##' into a
slide, and the bot reads the whole file including the prose between them.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"
REQUIRED_KEYS = ("title", "dia", "deck", "last_reviewed")

_FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_BOLD_LINE_RE = re.compile(r"^\*\*.+\*\*$")


def _problems(text: str) -> list[str]:
    """Return contract violations for one content document, empty if it conforms."""
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return ["missing YAML front-matter"]
    out: list[str] = []
    front = match.group(1)
    for key in REQUIRED_KEYS:
        if not re.search(rf"^{key}:", front, re.MULTILINE):
            out.append(f"front-matter missing '{key}'")
    sections = re.split(r"^## ", text[match.end():], flags=re.MULTILINE)[1:]
    if not sections:
        out.append("no '##' slide sections")
    for section in sections:
        lines = section.splitlines()
        heading = lines[0].strip()
        body = [ln.strip() for ln in lines[1:] if ln.strip()]
        if not body or not _BOLD_LINE_RE.match(body[0]):
            out.append(f"section '{heading}': first line must be a bold claim")
    return out


_GOOD = """---
title: Ejemplo
dia: 1
deck: true
last_reviewed: 2026-08-30
---

## Qué es un LLM

**Un LLM predice texto; no consulta una base de datos de hechos.**

- Trabaja con tokens, no con palabras.
- La ventana de contexto (context window) es finita.

> Nota: por eso hay que verificar cada dato.
"""


def test_problems_accepts_a_conforming_document():
    assert _problems(_GOOD) == []


def test_problems_flags_missing_front_matter():
    assert _problems("## Sin front-matter\n\n**Claim.**\n") == ["missing YAML front-matter"]


def test_problems_flags_missing_front_matter_key():
    text = _GOOD.replace("dia: 1\n", "")
    assert "front-matter missing 'dia'" in _problems(text)


def test_problems_flags_section_without_a_bold_claim():
    text = _GOOD.replace("**Un LLM predice texto; no consulta una base de datos de hechos.**",
                         "Un LLM predice texto.")
    assert any("must be a bold claim" in p for p in _problems(text))


def test_problems_flags_document_with_no_sections():
    text = _GOOD.split("## ")[0]
    assert "no '##' slide sections" in _problems(text)


def test_all_content_documents_conform():
    """Passes vacuously until content/ exists; guards every document once it does."""
    for path in sorted(CONTENT_DIR.glob("*.md")) if CONTENT_DIR.is_dir() else []:
        found = _problems(path.read_text(encoding="utf-8"))
        assert found == [], f"{path.name}: {found}"
