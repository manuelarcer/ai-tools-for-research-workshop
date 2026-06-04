# AI Tools for Research — Workshop Presentation

A browser-based HTML presentation for a workshop on using AI tools (Claude / Claude Code)
in research. Invited by Raul Ocampo; target delivery July 2026.

The deck is itself a showcase artifact — built with the `frontend-design` skill in Claude Code,
from notes kept in the intelligent-notes Obsidian vault.

## Run

No build step. Open `index.html` in a browser:

```
xdg-open index.html      # Linux
open index.html          # macOS
```

Web fonts (Fraunces, Newsreader, JetBrains Mono) load from Google Fonts, so an internet
connection gives the intended look. Everything else is self-contained.

## Structure

```
index.html            # Hub / landing — foundations + case-study index
case-study-meta.html  # Case study 01 — "Using Claude to build this workshop"
assets/style.css      # Shared design system (refined technical-editorial)
```

Add a new case study as `case-study-<slug>.html` and link it from the index.

## Design

Refined technical-editorial: typeset scientific-journal feel crossed with a terminal.
Fraunces (display) + Newsreader (body) + JetBrains Mono (tool annotations); warm paper,
deep ink, single vermilion accent; paper grain + ember glow. No Inter, no purple gradients.

## Deploy (later)

Static — GitHub-Pages-ready as-is (`index.html` at repo root). Create a repo, push, enable Pages.

## Source notes

Plan + tool list: `intelligent-notes/ideas/workshop-ai-tools-for-research.md`.
Case-study content: `intelligent-notes/ideas/workshop-case-study-using-claude-to-build-it.md`.
Tracked in `planning/projects/workshop-ai-tools-research.md`.
