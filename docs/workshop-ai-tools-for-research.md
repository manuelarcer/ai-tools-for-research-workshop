---
title: "Workshop — AI Tools for Research (Raul Ocampo invite)"
type: idea
created: 2026-06-04T19:05:00+08:00
modified: 2026-06-04T19:05:00+08:00
tags:
  - workshop
  - teaching
  - AI-tools
  - claude-code
  - research-workflow
status: seed
origin: user
summary: "Plan for a research-AI-tools workshop (invited by Raul Ocampo at Juan's PhD university), built from Juan's own working stack — foundational LLM/Claude-Code concepts plus live demos of the tools he actually uses."
---

# Workshop — AI Tools for Research (Raul Ocampo invite)

## Core Insight

The strongest version of this workshop isn't a survey of AI tools in the abstract — it's a guided tour of [[Claude Code]] and the agent stack Juan *already runs* for real research work, so attendees see a working system rather than a feature list. It needs two layers: a short conceptual foundation (how LLMs and agents actually work — [[context]], [[skills]], system vs global vs project context, safeguards) so the demos aren't magic, then live examples drawn from Juan's literature, writing, and automation workflows.

---

## Details

### Origin & context
- **Invited by Raul Ocampo** — ex-colleague from Juan's PhD, now a professor at Juan's PhD university. Proposed earlier in 2026 that Juan give a workshop on using AI tools in research.
- **Angle:** build it from the tools Juan has been using in his own work — credibility comes from showing a real, running setup, not slideware.
- **Status:** early planning. This note is the living plan; grow the two lists below.
- **Target:** deliver in **July 2026** (exact date TBC with Raul).
- **Tracked in planning repo:** `projects/workshop-ai-tools-research.md` (active, P2, deadline 2026-07-31) — surfaces in the morning briefing for biweekly momentum nudges.

### Audience & framing (to confirm)
- Likely grad students / researchers at the PhD university — mixed technical background.
- Decide the through-line: e.g. "from asking a chatbot questions → to running autonomous research agents you can trust." The trust/rigor thread (verifiable, fact-checked output) is a differentiator worth foregrounding for a scientific audience.

### Part 1 — Foundational concepts to teach
So the demos land as understandable, not magic:
- What an LLM is / isn't; tokens, the [[context]] window, why context management matters.
- **Claude Code** as an agent (not just chat): the system prompt, tools, and the agent loop.
- **Context layering:** global context (`~/.claude/CLAUDE.md`) vs project context (`CLAUDE.md` in a repo) vs session context — and how each shapes behavior.
- **[[skills]]:** reusable, invokable capabilities (e.g. `/linkedin-scan`, `/lit-review`); progressive disclosure.
- **Subagents & multi-agent work:** fan-out for parallel reading, independent verification.
- **MCP connectors:** giving the agent real tools (Calendar, Gmail, Drive, search).
- **Safeguards & control:** `settings.local.json` / permissions (allow/ask lists), why a researcher stays in the loop, what the agent should pause on.
- **Memory & persistence:** how the agent remembers project state across sessions.

### Part 2 — Tools / examples to showcase (seed list — to curate)
Grouped by research activity; pick the 4–6 that demo best live.

**Literature & discovery**
- `lit-review` — parallel multi-source review (OpenAlex, Semantic Scholar, arXiv, Crossref) → clustered narrative.
- `deep-research` — fan-out web search + **adversarial fact-checking** + cited report.
- Weekly **autonomous literature → LinkedIn post pipeline** (`linkedin-scan` / `linkedin-publish`): scan → triangle → draft → **two-agent full-text fact-check** → publish-log. Strong showcase of agents + rigor; runs unattended as a scheduled **cloud routine**.

**Knowledge management**
- **intelligent-notes** (this vault): Obsidian + semantic search + auto-wikilinking + Git-backed. Meta but compelling — the agent curating a researcher's second brain.

**Writing**
- `manuscript-style` / `manuscript-revisions` — academic-writing style enforcement and structured OLD→NEW edit docs.

**Automation & agents**
- **Scheduled cloud agents / routines** — recurring autonomous tasks (the weekly scans; a morning planning briefing).
- Telegram as a chat interface to the whole agent (how Juan actually drives it day-to-day).

**Domain / HPC**
- `aspire2a` — SSH + job submission to a supercomputer from the agent.
- Whisper transcription (`/mnt/ssd/whisper-venv`) — voice notes → text in the workflow.

**⭐ Meta — self-referential case study (Juan's idea, refined 2026-06-04)**
- The centerpiece is **the preparation of this very workshop**: "how I used Claude to plan and build this presentation." Self-referential and concrete — the demo material *is* the planning conversation itself, not a separate task.
- Captured live in [[workshop-case-study-using-claude-to-build-it]] — an **annotated interaction log**: per turn, *what Juan asked → what the agent did → which tools it used → outcome*. NOT raw transcripts (per Juan: summarize, don't dump).
- Already a strong arc in just the first few turns: a voice note → Whisper transcription → an auto-filed vault note → a tracked planning project → a custom biweekly reminder coded into the morning briefing on the fly. Each maps directly to a Part-1 concept (skills, tools, context, automation).
- ⚠️ **Scrub before any public showing:** private-repo paths/contents, tokens, personal calendar entries, `chat_id`, channel/security (`access.json`) material.
- Juan may later ask the agent to **prepare slides** off this curated log.

### Candidate case studies (pick the strongest 3–5)
Each is a real, self-contained arc the agent has actually done; the deck links one HTML page per study.
1. **Using Claude to build this workshop** (meta / self-referential) — [[workshop-case-study-using-claude-to-build-it]]. *Live (case 01).*
2. **Autonomous weekly LinkedIn pipeline** — scan → cross-paper synthesis → multi-agent full-text fact-check → draft; runs unattended as a cloud routine, gated for rigor. *(Strong second; build next.)*
3. **Literature review & deep research** — parallel agents across OpenAlex / Semantic Scholar / arXiv, clustered and adversarially verified.
4. **The agent extending itself — building its own persistent memory** *(added 2026-06-07)* — on request, designed and built a `CONTEXT.md` state file + a `SessionStart` hook + a `/checkpoint` skill with a background distiller, dry-running each piece before relying on it. Demonstrates self-modification, hooks, skills, background agents, and verification-before-claiming. Meta and memorable.
5. **From the bench to the cluster** — notes, manuscripts, and HPC jobs across the daily research workflow.

### Deliverable — browser-based HTML presentation (decided 2026-06-04)
- The talk is delivered as an **HTML presentation in the browser** (not PPT/PDF), styled with the official **`frontend-design`** plugin for a professional, non-generic look. The deck being an AI-built artifact is itself part of the showcase (meta).
- **Proposed architecture:** a `reveal.js` deck as the spine (keyboard nav, code highlighting, speaker notes) whose slides **link out to per-case-study HTML pages** rendered from the vault markdown — so content stays in sync with the notes and the private vault is never exposed directly.
- **Runs locally** in a browser during the workshop (no internet dependency); optionally publish to GitHub Pages later.
- Open choice: pure slide-deck (linear) vs. presentation *hub*/site (landing page + clickable case studies, more exploratory) vs. the hybrid above (recommended).

### Open questions / next steps
- Confirm with Raul: date, format (hands-on vs demo-only?), duration, audience size, university name (fill in). **Aiming for July 2026.**
- Decide the narrative spine and the 4–6 headline demos.
- Hands-on component? (attendees install Claude Code and run a starter skill) vs live-demo-only.
- What to open-source / share as a starter kit afterward.
- Pick which workflows are safe to show publicly (avoid exposing private repo content / credentials).

### References & inspiration
- 📺 [YouTube — Claude Code basics primer](https://youtu.be/tuY2ChJIx48) (Juan, 2026-06-05) — a presentation explaining the basics of Claude Code; reference for the Part-1 foundational-concepts section. *(Title not auto-fetched — JS-rendered page; confirm/annotate on next view.)*

## Sources
- Verbal proposal from Raul Ocampo (ex-PhD colleague, professor at Juan's PhD university), early 2026.
