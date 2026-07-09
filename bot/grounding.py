from __future__ import annotations
import html as html_lib
import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

# Plain-text list (one path per line, relative to repo root) of the files the
# bot loads as grounding. Edit that file to choose documents — no code change.
GROUNDING_LIST_FILE = "bot/grounding_files.txt"

# Used only if bot/grounding_files.txt is missing, so the bot still has context.
_DEFAULT_FILES = [
    "README.md",
    "docs/workshop-plan.md",
    "docs/workshop-ai-tools-for-research.md",
    "exercise/beer-lambert/README.md",
    "exercise/beer-lambert/SKILL.md.template",
    "index.html",
]

SPANISH_INSTRUCTIONS = (
    "Eres un asistente del taller 'Inteligencia Artificial para la Investigación'. "
    "Respondes preguntas de estudiantes y personal de investigación durante el taller en vivo.\n"
    "Reglas:\n"
    "- Responde en ESPAÑOL, conservando términos técnicos en inglés cuando corresponda.\n"
    "- Sé conciso: respuestas de tamaño chat, directas y accionables.\n"
    "- Mantén el hilo del taller: la IA amplifica el juicio del investigador, no lo reemplaza; "
    "recuerda verificar fuentes y resultados.\n"
    "- Basa tus respuestas en el material del taller que aparece abajo; si algo no está cubierto, dilo.\n"
    "- Si te comparten una captura de pantalla (error, terminal, UI), interprétala y ayuda a resolver.\n"
    "- Comienza SIEMPRE tu respuesta con el nombre de quien pregunta (te lo indican en el mensaje)."
)

_TAG_RE = re.compile(r"<[^>]+>")
_DROP_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_WS_RE = re.compile(r"\s+")


def extract_slide_text(html: str) -> str:
    no_blocks = _DROP_RE.sub(" ", html)
    no_tags = _TAG_RE.sub(" ", no_blocks)
    unescaped = html_lib.unescape(no_tags)
    return _WS_RE.sub(" ", unescaped).strip()


def read_grounding_list(repo_root: Path) -> list[str]:
    """Return the grounding file paths from bot/grounding_files.txt.

    Strips ``#`` comments and blank lines. Falls back to a built-in default
    list (with a warning) if the list file is absent.
    """
    list_path = repo_root / GROUNDING_LIST_FILE
    if not list_path.exists():
        log.warning("Grounding list %s not found; using built-in defaults.", GROUNDING_LIST_FILE)
        return list(_DEFAULT_FILES)
    files: list[str] = []
    for raw in list_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            files.append(line)
    return files


def load_grounding(repo_root: Path) -> str:
    parts: list[str] = []
    for rel in read_grounding_list(repo_root):
        p = repo_root / rel
        if not p.exists():
            log.warning("Grounding file not found, skipping: %s", rel)
            continue
        content = p.read_text(encoding="utf-8")
        if rel.lower().endswith((".html", ".htm")):
            parts.append(f"## {rel} (texto)\n{extract_slide_text(content)}")
        else:
            parts.append(f"## {rel}\n{content}")
    return "\n\n".join(parts)


def build_system(grounding_text: str) -> list[dict]:
    return [
        {"type": "text", "text": SPANISH_INSTRUCTIONS},
        {"type": "text", "text": grounding_text, "cache_control": {"type": "ephemeral"}},
    ]
