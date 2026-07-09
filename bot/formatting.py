"""Convert the Markdown the model produces into Telegram-safe HTML.

Telegram's ``parse_mode="HTML"`` renders a small tag set: <b> <i> <u> <s>
<code> <pre> <a>, and <pre><code class="language-xxx"> for syntax-highlighted
code blocks. This module maps the common Markdown that Claude emits onto that
subset and HTML-escapes everything else, so bold text and ```python fenced
blocks display correctly instead of showing raw ``**`` and backticks.

Anything not covered (headings, tables, lists) passes through as escaped plain
text, which reads fine in a chat. If the produced HTML is ever malformed, the
caller should fall back to sending plain text.
"""
from __future__ import annotations
import html as _html
import re

# ```lang\n...\n```  (language optional). DOTALL so blocks span newlines.
_FENCE_RE = re.compile(r"```([^\n`]*)\n?(.*?)```", re.DOTALL)
# `inline code` (single line, no backticks inside)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
# **bold** and __bold__
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_BOLD_ALT_RE = re.compile(r"__(.+?)__", re.DOTALL)
# *italic* / _italic_ (avoid matching bold markers and word-internal underscores)
_ITALIC_STAR_RE = re.compile(r"(?<![\*\w])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\*\w])")
_ITALIC_US_RE = re.compile(r"(?<![_\w])_(?!\s)([^_\n]+?)(?<!\s)_(?![_\w])")
# [text](url)
_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

_SENTINEL = "\x00{}\x00"


def render_html(text: str) -> str:
    """Return Telegram-HTML for ``text`` (Markdown from the model)."""
    stash: list[str] = []

    def _keep(snippet: str) -> str:
        stash.append(snippet)
        return _SENTINEL.format(len(stash) - 1)

    # 1. Pull code out first so its contents are never touched by bold/italic
    #    processing and are escaped literally.
    def _fence(m: re.Match) -> str:
        lang = m.group(1).strip()
        code = m.group(2).strip("\n")
        escaped = _html.escape(code, quote=False)   # keep quotes literal in code
        if lang:
            return _keep(f'<pre><code class="language-{lang}">{escaped}</code></pre>')
        return _keep(f"<pre>{escaped}</pre>")

    text = _FENCE_RE.sub(_fence, text)
    text = _INLINE_CODE_RE.sub(
        lambda m: _keep(f"<code>{_html.escape(m.group(1), quote=False)}</code>"), text)

    # 2. Escape the remaining prose (turns stray < > & into entities).
    text = _html.escape(text)

    # 3. Inline styling on the escaped prose.
    text = _BOLD_RE.sub(r"<b>\1</b>", text)
    text = _BOLD_ALT_RE.sub(r"<b>\1</b>", text)
    text = _ITALIC_STAR_RE.sub(r"<i>\1</i>", text)
    text = _ITALIC_US_RE.sub(r"<i>\1</i>", text)
    text = _LINK_RE.sub(r'<a href="\2">\1</a>', text)

    # 4. Restore the code placeholders.
    for i, snippet in enumerate(stash):
        text = text.replace(_SENTINEL.format(i), snippet)
    return text
