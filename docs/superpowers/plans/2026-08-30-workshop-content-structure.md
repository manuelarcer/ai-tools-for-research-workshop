# Workshop Content Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create one Spanish source of truth under `content/` that both drives slide generation in Claude Design and grounds the Telegram Q&A bot, plus a design brief that carries aesthetics without content.

**Architecture:** Three Spanish markdown documents in `content/`, each following a fixed contract (`##` heading = one slide, bold first line = the slide's claim, bullets = slide bullets, blockquote = note callout, plain paragraphs = guide prose the deck ignores). A machine-checkable test enforces that contract. `slides/design-brief.md` holds design direction only. `bot/grounding_files.txt` remains the single authority on what the bot reads, and each content file is added to it in the same task that creates it.

**Tech Stack:** Markdown with YAML front-matter; Python 3.12 + pytest for the contract test; the existing `bot/` package; venv at `.venv`.

**Spec:** `docs/superpowers/specs/2026-08-30-workshop-content-structure-design.md`

## Global Constraints

- Everything in `content/` is written in **Spanish**, keeping English technical terms inline and glossed in parentheses on first use (LLM, prompt, output, skill, harness, agent loop, hooks, baseline).
- Planning and instruction documents stay in **English**: `docs/workshop-plan.md`, the specs, the plans, and `slides/design-brief.md`.
- The content contract is: `##` heading = one slide; the first non-blank line under it is a **bold** claim; bullet lists become slide bullets; `> blockquote` becomes the note callout; ordinary paragraphs are guide prose that the deck ignores and the bot reads.
- Front-matter keys required on every `content/*.md`: `title`, `dia`, `deck`, `last_reviewed`. There is deliberately **no** `bot:` key — `bot/grounding_files.txt` is the only authority on what the bot reads.
- The workshop is the hands-on opencode build described in `docs/workshop-plan.md`, not the tool survey in `slide-deck-handoff.md`.
- The M4 result is **declared up front, not ambushed**. State at M0 that the pipeline will produce a confident answer that is roughly 20% wrong.
- Placeholders that must be left unfilled, never invented: presenter name, exact date, university name, contact address, slide/guide links.
- Existing HTML decks (`index.html`, `case-study-meta.html`, `taller-ia-alt1..5.html`) are **not** moved, renamed, or deleted by this plan.
- Run the suite with `.venv/bin/python -m pytest bot/tests -q` from the repo root. It must stay green after every task.
- Target delivery is **September 2026**, exact day TBC. Content that is unverified on real hardware must say so in the document itself.

---

### Task 1: Machine-checkable content contract

Guards every later task. Written first so the content documents are validated the moment they land.

**Files:**
- Create: `bot/tests/test_content_contract.py`
- Modify: `bot/tests/test_grounding.py` (append one test)

**Interfaces:**
- Consumes: `bot.grounding.read_grounding_list(repo_root) -> list[str]` (exists).
- Produces: `_problems(text: str) -> list[str]` in `bot/tests/test_content_contract.py`, returning a list of human-readable contract violations for one document's full text, empty when the document conforms. Later tasks rely on `test_all_content_documents_conform` catching their mistakes.

The contract test lives in `bot/tests/` because that is the repo's only suite and one command runs everything. The bot is a genuine consumer of these files, so the placement is not arbitrary.

Known limitation, accepted deliberately: the section splitter is a line-anchored regex, so a line beginning `## ` inside a fenced code block would be counted as a slide. Keep shell comments in code blocks to a single `#`. Teaching the splitter about fences is not worth the complexity for three documents.

- [ ] **Step 1: Write the failing tests**

Create `bot/tests/test_content_contract.py`:

```python
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
```

Append to `bot/tests/test_grounding.py`:

```python
def test_grounding_files_list_paths_all_exist():
    """A typo here degrades the bot silently — load_grounding only warns."""
    repo_root = Path(__file__).resolve().parents[2]
    missing = [rel for rel in read_grounding_list(repo_root)
               if not (repo_root / rel).exists()]
    assert missing == [], f"grounding_files.txt lists missing paths: {missing}"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest bot/tests/test_content_contract.py -v`
Expected: collection succeeds, and the `_problems` tests fail only if the helper is wrong. If every test passes on the first run, deliberately break `_BOLD_LINE_RE` (e.g. match `^X`) and confirm `test_problems_accepts_a_conforming_document` fails, then restore it. This proves the assertions have teeth rather than passing vacuously.

- [ ] **Step 3: Run the full suite**

Run: `.venv/bin/python -m pytest bot/tests -q`
Expected: PASS, 75 prior tests plus 7 new ones.

- [ ] **Step 4: Commit**

```bash
git add bot/tests/test_content_contract.py bot/tests/test_grounding.py
git commit -m "test: enforce the content/ contract and grounding path resolution"
```

---

### Task 2: `content/01-conceptos.md` — the Day-1 concepts

**Files:**
- Create: `content/01-conceptos.md`
- Modify: `bot/grounding_files.txt`

**Interfaces:**
- Consumes: the contract enforced by `test_all_content_documents_conform` (Task 1).
- Produces: nine `##` sections that Claude Design turns into the Day-1 concept slides. Later tasks add sibling files to the same directory and the same grounding list.

Source material is `docs/workshop-plan.md` §5, which lists nine concepts. Write them out in Spanish; do not invent additional ones.

- [ ] **Step 1: Write the document**

Front-matter exactly:

```yaml
---
title: Conceptos fundamentales
dia: 1
deck: true
last_reviewed: 2026-08-30
---
```

Then nine `##` sections, in this order, each with a bold claim line, two to four bullets, and an optional `> Nota:` callout. The claim in each is the point the slide must make:

1. `## Qué es (y qué no es) un LLM` — claim: an LLM predicts text, it does not look facts up. Bullets: tokens rather than words; the context window is finite and is why context management matters; it has no memory between sessions unless you give it one.
2. `## El bucle del agente (agent loop)` — claim: an agent is not a chat box; it is a loop of system prompt, tools, and repetition. Bullets: the model chooses a tool, the tool runs, the result comes back, the loop continues; it stops when the task is done or you stop it.
3. `## Capas de contexto` — claim: what the agent knows comes in layers you control. Bullets: global rules, project rules, session context; the translation `CLAUDE.md` → opencode `AGENTS.md` / rules.
4. `## Skills: instrucciones reutilizables` — claim: a skill is a written procedure the agent loads when it is relevant. Bullets: progressive disclosure, so the agent reads it only when needed; a skill is plain text, which is why you can write one. Note that Day 2 is where they author one.
5. `## Subagentes y elección de modelo` — claim: you can send a cheap model to explore and a capable model to build, in the same session. Bullets: per-agent model selection is opencode's real strength; the cost story; this is the signature pattern of the workshop.
6. `## Hooks: disparadores del ciclo de vida` — claim: hooks run your code automatically at points in the agent's life. Bullets: in opencode they are JS/TS plugins keyed to lifecycle events such as `tool.execute.before`; higher ceremony than Claude Code's file/shell hooks, and be honest about that. Taught as a concept and shown running, never hand-authored live.
7. `## MCP y herramientas` — claim: tools are how the agent stops being a text box and touches the real world. Bullets: MCP is the standard way to plug in a capability; the agent can only do what its tools allow.
8. `## Salvaguardas y control` — claim: you stay in the loop by deciding what the agent may do without asking. Bullets: permissions (allow / ask); what the agent should always pause on; never hand it credentials or sensitive data.
9. `## El hilo de confianza` — claim: for science, verification is not optional. Bullets: models fabricate citations, DOIs and numbers with total confidence; a result you did not check is not a result; this thread runs through every remaining slide and the whole Day-2 exercise. This is the slide that sets up the exercise, so it closes the file.

- [ ] **Step 2: Add it to the bot's grounding list**

Append to `bot/grounding_files.txt`, above the trailing comment block:

```
content/01-conceptos.md
```

- [ ] **Step 3: Run the suite**

Run: `.venv/bin/python -m pytest bot/tests -q`
Expected: PASS. A failure names the offending section, e.g. `01-conceptos.md: ["section 'MCP y herramientas': first line must be a bold claim"]`.

- [ ] **Step 4: Commit**

```bash
git add content/01-conceptos.md bot/grounding_files.txt
git commit -m "content: Day-1 concepts in Spanish (plan §5)"
```

---

### Task 3: `content/02-ejercicio.md` — the attendee guide, M0 to M6

**Files:**
- Create: `content/02-ejercicio.md`
- Modify: `bot/grounding_files.txt`

**Interfaces:**
- Consumes: the contract from Task 1; the milestone definitions in `docs/workshop-plan.md` §7.3; the dataset facts in `exercise/beer-lambert/README.md`.
- Produces: the self-paced guide that plan §9 item 2 calls the remote TA and the recovery path for anyone who falls behind.

This is the largest document. It is attendee-facing, so it must work for someone who has never opened a terminal, while giving a fast attendee somewhere to run.

- [ ] **Step 1: Write the document**

Front-matter exactly:

```yaml
---
title: Ejercicio — calibración Beer-Lambert que se verifica a sí misma
dia: 2
deck: true
last_reviewed: 2026-08-30
---
```

Sections, each with a bold claim, in this order:

1. `## El objetivo, dicho de frente` — claim: you are going to build a pipeline that gives a confident answer that is about 20% wrong, and then build the check that catches it. State plainly that R² will be 0.9998 and the answer will still be wrong, and that this is the point. Nothing is hidden in this guide.
2. `## Los datos` — claim: the data is synthetic, so the true answer is exact arithmetic. Bullets: methylene blue, λmax ≈ 664 nm, ε ≈ 95,000 M⁻¹cm⁻¹, path length 1 cm; six calibration spectra at known concentrations; one unknown; `calibration_*.csv`, `calibration_index.csv`, `unknown.csv`, columns `wavelength_nm,absorbance`. Say that the unknown's baseline differs from the calibration set, as it would on a different day with a different cuvette.
3. `## M0 — Carga y grafica un espectro` — claim: if you can plot one spectrum, you are in. Everyone reaches this milestone.
4. `## M1 — Lee un pico por concentración` — claim: read the peak absorbance from every calibration spectrum and pair it with its known concentration.
5. `## M2 — Ajusta la recta de calibración` — claim: slope, intercept, R² = 0.9998. Warn in the note that this number is about to mislead them.
6. `## M3 — Predice la incógnita` — claim: the pipeline now returns a confident number, near 10.78 µM.
7. `## M4 — Compara contra la verdad` — claim: the true value is 9.00 µM, so the answer is 19.8% wrong while the fit is nearly perfect. The lesson in one line: a perfect fit is not a correct answer.
8. `## M5 — Diagnostica, corrige y verifica` — claim: the cause is the baseline, and the fix belongs inside the skill, not in your head. Bullets: subtract the baseline before reading the peak; re-run and land near 9.03 µM; add an assertion to the skill that fails loudly when a control deviates by more than a set tolerance.
9. `## M6 — Endurece (vía rápida)` — claim: for anyone who arrives early, there is more to do. Bullets: residual plot; extrapolation guard flagging an unknown outside the calibration range; uncertainty propagation.
10. `## La lección que se lleva a casa` — claim: a research skill you can trust is one that checks itself. State that verification is not overhead; it is the difference between a demo and an instrument.

Numeric values must match `exercise/beer-lambert/README.md` exactly: naive 10.78 µM (+19.8%), corrected 9.03 µM (+0.3%), truth 9.00 µM, R² 0.9998, seed 42. Do not round them differently.

- [ ] **Step 2: Add it to the bot's grounding list**

Append to `bot/grounding_files.txt`, above the trailing comment block:

```
content/02-ejercicio.md
```

- [ ] **Step 3: Verify the numbers against the generator**

Run: `.venv/bin/python exercise/beer-lambert/generate_data.py`
Expected: the printed instructor benchmark table matches the numbers written into the guide. If it does not, the generator wins — correct the guide, not the generator.

- [ ] **Step 4: Run the suite**

Run: `.venv/bin/python -m pytest bot/tests -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add content/02-ejercicio.md bot/grounding_files.txt
git commit -m "content: attendee guide for the Beer-Lambert exercise, M0-M6"
```

---

### Task 4: `content/03-instalacion.md` — opencode setup for Mac and Windows

**Files:**
- Create: `content/03-instalacion.md`
- Modify: `bot/grounding_files.txt`

**Interfaces:**
- Consumes: the contract from Task 1.
- Produces: the document the bot will lean on hardest in the first fifteen minutes of Day 1, when setup questions arrive.

- [ ] **Step 1: Write the document**

Front-matter exactly:

```yaml
---
title: Instalación y configuración de opencode
dia: 1
deck: false
last_reviewed: 2026-08-30
---
```

`deck: false` because this is handout material, not slides.

**Platform policy, decided with the presenter.** He will test and verify the macOS path himself, so write macOS as precise, followable steps. He has **no Windows machine**, so the Windows section describes the *shape* of the process and defers to opencode's own install page as the authority. **Do not invent Windows commands.** Only two Windows commands are sourced and may be written as such: `choco install opencode` and `npm install -g opencode-ai`. Anything beyond those is a link, not an instruction — an attendee following a fabricated command loses fifteen minutes and stops trusting the guide.

Facts sourced from `https://opencode.ai/docs/` and `https://opencode.ai/docs/providers/` on 2026-08-30. Use these verbatim; do not paraphrase a command into a different one:

| Fact | Value |
|---|---|
| macOS install | `brew install anomalyco/tap/opencode` |
| Windows install | `choco install opencode` |
| Cross-platform install (needs Node) | `npm install -g opencode-ai` |
| Config file | `~/.config/opencode/opencode.json` |
| Connect a provider | `/connect` inside opencode, then paste the key |
| Choose a model | `/models` |
| Create project instructions | `/init`, which writes `AGENTS.md` in the project root |
| Docs home / providers | `https://opencode.ai/docs/` · `https://opencode.ai/docs/providers/` |

Sections, each with a bold claim:

1. `## Antes de empezar` — claim: you need three things before the workshop starts. Bullets: a laptop with permission to install software, Python 3.11 or newer, and an internet connection.
2. `## Instalar opencode en macOS` — claim: one command installs it. Give the Homebrew command, the `npm` alternative, and the config file location.
3. `## Instalar opencode en Windows` — claim: the same tool, installed through Chocolatey or npm. Give only the two sourced commands, then link to `https://opencode.ai/docs/` as the authority. Include a `> Nota:` saying plainly that these steps have **not** been verified on Windows and that the official page is definitive if they differ.
4. `## Configurar el modelo` — claim: opencode is bring-your-own-model, and the workshop uses the **OpenCode Zen free tier**, chosen by the presenter on 2026-08-30 because it needs no local model download and works on a weak laptop. Show `/connect` and `/models`, and name the config file.
5. `## Instalar una skill` — claim: a skill is a folder with a `SKILL.md`; installing one is copying it where opencode looks. Point at `exercise/beer-lambert/SKILL.md.template`.
6. `## Comprobar que funciona` — claim: one check tells you the install is good. Give the command and the expected output; if the exact output cannot be sourced, describe what a healthy result looks like rather than inventing a string.
7. `## Problemas comunes` — claim: three failures account for most setup trouble. Cover a missing PATH entry after install, a corporate proxy blocking the model endpoint, and a Python version below 3.11.

Every command that was not sourced from the table above must carry a `> Nota:` marking it unverified. Writing a plausible-looking flag that does not exist is a plan failure, not a shortcut.

- [ ] **Step 2: Add it to the bot's grounding list**

Append to `bot/grounding_files.txt`, above the trailing comment block:

```
content/03-instalacion.md
```

- [ ] **Step 3: Run the suite**

Run: `.venv/bin/python -m pytest bot/tests -q`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add content/03-instalacion.md bot/grounding_files.txt
git commit -m "content: opencode setup guide for Mac and Windows (unverified)"
```

---

### Task 5: `slides/design-brief.md` and superseding the old handoff

**Files:**
- Create: `slides/design-brief.md`
- Modify: `slide-deck-handoff.md` (header line only)

**Interfaces:**
- Consumes: the content contract from Task 1, which it documents for the design agent; the visual language of `taller-ia-alt3-terminal.html`.
- Produces: the single document handed to Claude Design alongside the `deck: true` content files.

Written in English: it is an instruction to a design agent, not attendee material. It contains **no workshop content** — if a fact about the workshop appears in this file, it belongs in `content/` instead.

- [ ] **Step 1: Write the brief**

Cover these sections:

- **What to generate** — a slide deck for the Day-1 concepts and the Day-2 exercise of a hands-on workshop, in Spanish, projected from a laptop, type legible from the back of a room.
- **Where the content comes from** — the `content/*.md` files whose front-matter says `deck: true`. State the mapping explicitly: one `##` is one slide; the bold line under the heading is the slide's headline claim; bullets are the slide's bullets; a `> blockquote` is a note callout; ordinary paragraphs are speaker context and must **not** be printed on the slide.
- **Visual direction** — inspired by the terminal aesthetic of `taller-ia-alt3-terminal.html`, not a copy of it. Dark IDE ground, monospace-forward typography, command-line motifs (a shell prompt line, `>` bullets, `#` eyebrows, faux code-window cards), restrained motion. State plainly that the design agent should improve within that language rather than reproduce the reference, and that deviations that serve legibility are welcome.
- **Format constraints** — keyboard and click navigation, a slide counter, a progress indicator, deep-linking by URL hash, `prefers-reduced-motion` honoured with an instant fallback, two-column grids collapsing below ~960px.
- **Placeholders to leave unfilled** — presenter name, date, university name, contact address, links. List them explicitly and say they must not be invented.
- **Evaluation checklist** — adapted from `slide-deck-handoff.md` §9: opens clean with no console errors, every content section present, the Spanish-body/English-term convention respected, controls all work, reduced-motion fallback works, placeholders still placeholders.
- **Tooling note** — the `claude-design` MCP server needs `/design-login`; it returned `FIRST_PARTY_AUTH_REJECTED` (HTTP 403) on 2026-08-30. The local `/design` skill, which publishes a canvas as an Artifact, is a working alternative.

- [ ] **Step 2: Mark the old handoff superseded**

Insert immediately under the `# Handoff — Slide Deck Generation` heading of `slide-deck-handoff.md`:

```markdown
> **Superseded (2026-08-30).** This brief describes the generic tool-survey deck.
> The workshop is the hands-on opencode build in `docs/workshop-plan.md`; the current
> deck brief is `slides/design-brief.md` and its content source is `content/`.
> Kept for its design tokens and its evaluation checklist.
```

Change nothing else in that file.

- [ ] **Step 3: Confirm no content leaked into the brief**

Run: `grep -niE "beer|lambert|methylene|664|opencode|milestone|M[0-6]\b" slides/design-brief.md`
Expected: matches only where the brief refers to `content/` files or names the harness in passing. Any sentence that *teaches* something belongs in `content/`; move it there.

- [ ] **Step 4: Run the suite**

Run: `.venv/bin/python -m pytest bot/tests -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add slides/design-brief.md slide-deck-handoff.md
git commit -m "docs: design brief for the new deck; supersede the survey handoff"
```

---

### Task 6: Final verification and cost measurement

**Files:**
- Modify: `docs/superpowers/specs/2026-08-30-workshop-content-structure-design.md` (record the measured token count)

**Interfaces:**
- Consumes: everything created in Tasks 1 to 5.
- Produces: the recorded per-question grounding cost for the live workshop.

- [ ] **Step 1: Confirm every grounding path resolves**

```bash
cd /Users/juar/github/ai-tools-for-research-workshop
grep -vE '^\s*(#|$)' bot/grounding_files.txt | while read -r f; do
  [ -e "$f" ] && echo "OK      $f" || echo "MISSING $f"
done
```
Expected: seven `OK` lines, no `MISSING`.

- [ ] **Step 2: Measure the new grounding cost**

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from dotenv import dotenv_values
import anthropic
from bot.config import Config
from bot.grounding import load_grounding, build_system
cfg = Config.from_env(dotenv_values(".env"))
n = anthropic.Anthropic(api_key=cfg.anthropic_api_key).messages.count_tokens(
    model=cfg.model_default, system=build_system(load_grounding(Path(".").resolve())),
    messages=[{"role": "user", "content": "hola"}]).input_tokens
print(f"grounding: {n:,} input tokens per question")
PY
```
Expected: a number materially above 10,414, since three documents were added. Record it.

- [ ] **Step 3: Write the measurement into the spec**

Replace the sentence "The three new content files will push it back up; the figure is worth re-measuring once they exist" in the spec's *Consumer 2* section with the measured figure and its date.

- [ ] **Step 4: Run the full suite**

Run: `.venv/bin/python -m pytest bot/tests -q`
Expected: PASS.

- [ ] **Step 5: Commit and push**

```bash
git add docs/superpowers/specs/2026-08-30-workshop-content-structure-design.md
git commit -m "docs: record measured grounding cost after the content tree landed"
git push origin main
```

---

## What this plan deliberately does not do

- No logistics, glossary or FAQ content: deferred, and it needs the date, university name and contact that only the presenter has.
- No Day-3 material.
- No moving, renaming or deleting the existing HTML decks.
- No end-to-end test of the free-model path. That is `docs/workshop-plan.md` §10 and it stays with the presenter; nothing in this plan substitutes for running the whole Day-2 exercise in opencode on the actual free model before it goes on a slide.
