# Workshop Content Structure — Design

**Date:** 2026-08-30
**Feature:** A single Spanish source of truth under `content/` that both drives slide generation in Claude Design and grounds the Telegram Q&A bot, so the two never disagree.

## Goal

The repo currently holds two incompatible versions of the workshop. `docs/workshop-plan.md` (authoritative, 2026-07-01) describes a hands-on build: three days of two hours, the whole room on opencode, attendees authoring a self-verifying Beer-Lambert skill. `slide-deck-handoff.md` and `taller-ia-alt*.html` describe a twelve-slide generic survey of third-party AI tools. The plan's §11 says the deck must be reframed; §8 of the handoff flags the same conflict and leaves it open. The bot, meanwhile, has been grounding on documents from both versions at once.

This design closes that. One body of Spanish content becomes the source both consumers read, and the contradicting documents leave the bot's grounding list.

## Decisions locked

| Decision | Why |
|---|---|
| **The workshop is the hands-on build** in `docs/workshop-plan.md` | It is the version that was pressure-tested in a design grilling, and the exercise is already half-built. The survey decks become salvage material, not the spine. |
| **Attendee-facing content is stored in Spanish**, English technical terms inline | It is what attendees read on screen and what the bot answers in. Storing English and translating at render time guarantees drift, and would make the bot quote text that does not match the slides. |
| **Planning documents stay in English** | `docs/workshop-plan.md` and the specs are for the presenter, not the room. No reason to translate them, and no reader is disadvantaged. |
| **One `content/` tree read by both consumers** | Any layout that gives the deck and the bot their own copy of the same facts reproduces the exact failure this repo already has. |
| **The M4 twist is declared, not ambushed** | The presenter's call: what matters is that attendees understand the concepts and question their results, not that they are surprised. This is also more robust — plan §7.2 already worried the free model might baseline-correct on its own and defuse the surprise. |
| **No spoiler machinery in the bot** | Follows from the decision above. `bot/grounding.py:29` already carries the verification thread in the system prompt, so no rules file is needed either. |
| **The terminal aesthetic is inspiration, not a template** | `taller-ia-alt3-terminal.html` is the chosen direction, but Claude Design should improve within that language rather than clone the reference. |

## Layout

```
content/                     # single source of truth, Spanish
  01-conceptos.md            # Day-1 concepts (plan §5)
  02-ejercicio.md            # attendee guide, milestones M0–M6
  03-instalacion.md          # opencode setup, Mac + Windows
slides/
  design-brief.md            # aesthetics and format rules only, zero content
```

Existing HTML decks (`index.html`, `case-study-meta.html`, `taller-ia-alt1..5.html`) stay where they are. Retiring them is a separate decision, to be taken once a new deck exists and the presenter is satisfied with it; `index.html` is the GitHub Pages entry point and must not be moved as a side effect of this work. `slide-deck-handoff.md` gets a header line marking it superseded by `slides/design-brief.md`, the same pattern `docs/workshop-plan.md` already uses for the seed note.

## The file contract

This is the mechanism that lets one text serve both consumers. Each file in `content/` carries YAML front-matter:

```yaml
---
title: Conceptos fundamentales
dia: 1
deck: true          # does this file produce slides
last_reviewed: 2026-08-30
---
```

There is deliberately no `bot:` field. `bot/grounding_files.txt` is the single authority on what the bot reads; a second flag in front-matter would be a second source of truth that can disagree with it.

The body follows a fixed markdown rhythm:

| Markdown element | Slide element | Read by the bot |
|---|---|---|
| `##` heading | one slide | yes |
| first **bold** line under the heading | the slide's headline claim | yes |
| bullet list | the slide's bullets | yes |
| `> blockquote` | the coloured note callout | yes |
| ordinary paragraphs | ignored by the deck | yes |

The deck consumes the structured elements; the bot consumes the whole file, including explanatory prose that would never fit on a slide. The result reads as a normal document, so there is no markup convention to memorise.

## Content to write

**`01-conceptos.md`** covers the nine concepts of plan §5, one `##` each: what an LLM is and is not (tokens, context window); the agent loop; context layering (`CLAUDE.md` → opencode `AGENTS.md`); skills as reusable instructions; subagents and per-agent model selection, with the cost story; hooks as lifecycle triggers, taught as a concept and shown, never hand-authored live; MCP and tools; safeguards, permissions and staying in the loop; and the trust thread that sets up everything after it.

**`02-ejercicio.md`** is the attendee-facing self-paced guide for the Beer-Lambert exercise, milestones M0 through M6, in Spanish. It states the objective at M0: you will reach a result that looks perfect and is roughly 20% wrong, and your job is to build the check that catches it. The milestones themselves are unchanged from plan §7.3. This is the deliverable plan §9 item 2 calls the remote TA and the recovery path for anyone who falls behind or misses a day.

**`03-instalacion.md`** covers installing the opencode CLI and desktop app, configuring the free model, and installing a skill, for both Mac and Windows (plan §9 item 5). It is drafted from opencode's documentation and remains **unverified** until tested on both platforms.

## Consumer 1 — Claude Design

`slides/design-brief.md` holds only design direction and format constraints, never content: the terminal aesthetic as inspiration (dark IDE surface, monospace, shell-prompt motifs, restrained motion) drawn from `taller-ia-alt3-terminal.html`; the mapping rule that one `##` is one slide; the placeholders to leave unfilled (presenter name, date, university, contact, links); and the evaluation checklist adapted from `slide-deck-handoff.md` §9.

Generating a deck therefore means pointing Claude Design at the brief plus the `content/` files whose front-matter says `deck: true`.

Note: the `claude-design` MCP server failed to connect on 2026-08-30 (`FIRST_PARTY_AUTH_REJECTED`, HTTP 403) and needs `/design-login`. The local `/design` skill, which builds a canvas as a published Artifact, is a working alternative path.

## Consumer 2 — the bot

`bot/grounding_files.txt` lists the `content/` files as they land. Two documents were removed from that list on 2026-08-30 because they contradict the locked direction: `docs/workshop-ai-tools-for-research.md` (the seed note the plan supersedes) and `index.html` (the old "tour of my stack" hub deck). The list now keeps `README.md`, `docs/workshop-plan.md`, `exercise/beer-lambert/README.md`, and `exercise/beer-lambert/SKILL.md.template`.

That removal alone took grounding from 14,405 to 10,414 input tokens per question. The three new content files will push it back up; the figure is worth re-measuring once they exist, because it sets the per-question cost of the live workshop.

## Verification

- A test asserting every active path in `bot/grounding_files.txt` resolves, added to the existing suite. `load_grounding` skips a missing file with a warning, so a typo degrades the bot silently — exactly the failure mode that should not surface mid-workshop.
- Re-measure grounding tokens with `messages.count_tokens` after the content lands, and record the number.
- The full suite (75 tests at the time of writing) keeps passing.

## Out of scope

Logistics, glossary and FAQ content (deferred; needs dates, university name and contact that only the presenter has). Day-3 bring-your-own material. Retiring or archiving the existing HTML decks. Testing the free-model path end to end, which is plan §10 and stays with the presenter.

## Open items

- The opencode setup guide is unverified on both platforms until the presenter tests it.
- Plan §10's free-model risk is untouched by this work: the whole Day-2 exercise still needs a run in opencode on the actual free model before it goes on a slide.
- The workshop date is still "July 2026, TBC with Raul Ocampo" in the plan front-matter, and today is 2026-08-30. The date needs confirming, and the plan's front-matter updating.
