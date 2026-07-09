from __future__ import annotations
import html as html_lib
import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

# Files pulled into the grounding context, relative to repo root.
GROUNDING_FILES = [
    "README.md",
    "docs/workshop-plan.md",
    "docs/workshop-ai-tools-for-research.md",
    "exercise/beer-lambert/README.md",
    "exercise/beer-lambert/SKILL.md.template",
]
SLIDE_HTML = "index.html"

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


def load_grounding(repo_root: Path) -> str:
    parts: list[str] = []
    for rel in GROUNDING_FILES:
        p = repo_root / rel
        if p.exists():
            parts.append(f"## {rel}\n{p.read_text(encoding='utf-8')}")
        else:
            log.warning("Grounding file not found, skipping: %s", rel)
    deck = repo_root / SLIDE_HTML
    if deck.exists():
        parts.append(f"## {SLIDE_HTML} (texto de las diapositivas)\n"
                     + extract_slide_text(deck.read_text(encoding="utf-8")))
    else:
        log.warning("Grounding file not found, skipping: %s", SLIDE_HTML)
    return "\n\n".join(parts)


def build_system(grounding_text: str) -> list[dict]:
    return [
        {"type": "text", "text": SPANISH_INSTRUCTIONS},
        {"type": "text", "text": grounding_text, "cache_control": {"type": "ephemeral"}},
    ]
