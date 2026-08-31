# Design Brief — Workshop Slide Deck

This is an instruction document for a design agent (Claude Design, or the local `/design`
skill as a fallback — see §7). It is **not** attendee material: it is written in English,
and it contains **no workshop content**. Every fact about the workshop — what an LLM is,
what the exercise teaches, any number, any command — lives in `content/`, not here. This
file only tells the design agent what to build and how it should look.

Feed the design agent this file together with the `content/*.md` files named in §2. Do not
paraphrase or summarize their content into this brief; point the agent at the files
themselves.

## 1. What to generate

A slide deck for a hands-on workshop, covering the Day-1 concepts session and the Day-2
exercise session. Slide body text is Spanish — the source files are already written in
Spanish with English technical terms kept inline; do not translate anything, and do not
add English prose beyond what the source already contains.

The deck is delivered live from a presenter's laptop, projected onto a screen. Type must
stay legible from the back of a room — this constrains minimum font size and contrast, not
just palette choice.

## 2. Where the content comes from

Source: the files under `content/` whose YAML front-matter sets `deck: true`. As of this
writing that is `content/01-conceptos.md` (`dia: 1`) and `content/02-ejercicio.md`
(`dia: 2`). `content/03-instalacion.md` has `deck: false` — it is handout/setup material,
not slide material, and must not be turned into slides. Re-check the front-matter each time
this brief is used; the set of `deck: true` files may grow.

**Mapping rule — apply exactly, one file at a time, top to bottom:**

| Markdown element | Becomes |
|---|---|
| `##` heading | one slide |
| the first **bold** line directly under that heading | the slide's headline claim |
| the bullet list under that | the slide's bullets |
| a `> blockquote` | a note callout (visually set apart — see §3) |
| ordinary paragraphs (not bold, not bulleted, not a blockquote) | speaker context — **do not print these on the slide** |

One `##` produces exactly one slide: do not split a section across two slides, do not
merge two sections into one, do not add a slide that has no corresponding `##`. Do not
reorder sections. Do not invent, paraphrase, or summarize wording that is not present in
the source file — the slide's headline claim and bullets are the bold line and bullets
verbatim (trimmed of markdown syntax only), not a rewrite of them.

## 3. Visual direction

**Inspired by the terminal aesthetic of `taller-ia-alt3-terminal.html`, not a copy of it.**
That file is the reference point for the visual language, not a template to reproduce
pixel for pixel. Carry the language forward:

- Dark IDE ground.
- Monospace-forward typography throughout.
- Command-line motifs: a shell prompt line per slide, `>` list bullets, `#` eyebrows,
  faux code-window cards (with a small red/yellow/green traffic-light dot cluster, in the
  style of a terminal window's title bar).
- Restrained motion: a brief reveal on entry, a short transition between slides, a
  blinking cursor accent — nothing busy, nothing that fights legibility.

**Improve within that language rather than reproduce the reference.** The design agent
should treat what follows as a starting palette and a set of motifs to draw on, not a
specification to match exactly. Deviations that serve legibility — a bigger type scale, a
higher-contrast accent, a calmer transition — are welcome and encouraged.

Starting design tokens (carried from the superseded brief, `slide-deck-handoff.md` §5):

| Role | Value |
|---|---|
| Base background | `#0D1117` |
| Raised panel / code surface | `#11151C` / `#161B22` |
| Status/title bar | `#0A0D12` |
| Hairline / stronger border | `#21262D` / `#30363D` |
| Text primary | `#E6EDF3` |
| Muted / faint | `#8B949E` / `#5A636E` |
| Green accent (primary) | `#3FB950` |
| Amber / blue accents | `#D29922` / `#58A6FF` |
| Purple / coral / teal accents | `#BC8CFF` / `#FF7B72` / `#56D4BC` |
| Window dots (r/y/g) | `#FF5F56` / `#FFBD2E` / `#27C93F` |
| Typeface | JetBrains Mono → IBM Plex Mono → Fira Code → system mono fallbacks |
| Slide transition duration | ~360ms |

Note callouts (the `> blockquote` mapping from §2): every source file uses a single kind
of callout (`> Nota:`), so one consistent treatment is enough — pick one accent from the
table above (green is a reasonable default, matching its role as the primary accent) and
apply it uniformly. Do not invent a taxonomy of callout severities (tip/warning/danger)
that the source content does not express.

## 4. Format constraints

- Keyboard navigation (next/previous, first/last slide) and click navigation.
- A slide counter (current / total).
- A progress indicator.
- Deep-linking by URL hash, so any slide is directly bookmarkable and shareable.
- Honour `prefers-reduced-motion`: when set, fall back instantly to the static end-state of
  every transition and reveal — no typewriter effects, no flicker, no blink.
- Two-column grids collapse to a single column below roughly 960px viewport width.
- A single, standalone file that opens directly in a browser with no build step.

## 5. Placeholders to leave unfilled

The following are not yet known and must **not** be invented or guessed — leave them as
clearly marked placeholders (e.g. `[Presenter Name]`, `[Date]`) for the presenter to fill
in later:

- Presenter name.
- Exact date of the workshop.
- University name.
- Contact address.
- Links (any URL to slides, resources, or contact — including a placeholder link rather
  than a real or invented one).

## 6. Evaluation checklist

Adapted from `slide-deck-handoff.md` §9:

- Opens clean in a browser: zero console errors, no build step.
- Every section from the `deck: true` content files is present as a slide, per the
  mapping rule in §2 — nothing dropped, nothing added.
- The Spanish-body / English-term convention is respected exactly as written in the source
  files — no translation, no rewriting.
- Every control from §4 works: keyboard nav, click nav, counter, progress indicator,
  deep-linking.
- The reduced-motion fallback works and is instant, with no residual animation.
- Every placeholder from §5 is still a placeholder, not an invented value.

## 7. Tooling note

The `claude-design` MCP server needs `/design-login`; it returned
`FIRST_PARTY_AUTH_REJECTED` (HTTP 403) on 2026-08-30. Until that is resolved, the local
`/design` skill — which publishes a canvas as an Artifact — is a working alternative path
to generate the deck from this brief.
