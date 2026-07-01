# AI Tools for Research — Workshop

A **hands-on workshop** on using AI tools in research: attendees build a small, reproducible,
**self-verifying** research skill on their own machine — in [opencode](https://opencode.ai), on a
free-model path. Not a survey, not a tour of the presenter's stack. Invited by Raul Ocampo; target
delivery July 2026.

**The plan is [docs/workshop-plan.md](docs/workshop-plan.md)** — the authoritative design (3 days ×
2 hours, remote; self-paced with milestones; verification as the through-line). Read that first.

This repo also holds the **presentation deck** — a browser-based HTML deck used for the Day-1
concepts and framing. The deck is itself a showcase artifact — built with the `frontend-design`
skill in Claude Code, from notes kept in the intelligent-notes Obsidian vault. *(The deck's hero
framing is being reconciled to the plan — see §11 of the plan.)*

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
