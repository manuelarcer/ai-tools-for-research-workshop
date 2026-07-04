# Handoff — Slide Deck Generation

**Project:** "Inteligencia Artificial para la Investigación" — workshop for students and research staff at a university in Mexico.
**Deliverable being handed off:** the slide deck (the main deliverable of the project).
**Purpose of this document:** a self-contained brief for a design-focused agent to generate the deck from scratch, so its output can be evaluated against the existing reference deck `taller-ia-alt3-terminal.html`. Do not just copy the reference — regenerate, then we compare.

---

## 1. The deliverable in one line

A single, standalone `.html` file — 12 slides, Spanish body with English technical terms preserved, "Terminal / código" (dark IDE) aesthetic, opens in a browser with no build step.

## 2. Audience & framing

- University in Mexico; mixed audience of grad students and research staff, mixed technical background.
- Topic: using AI tools for research tasks (literature, reading, writing, data/code, prompting, ethics).
- Through-line: **AI amplifies the researcher's productivity; it does not replace judgment.** A trust/verification thread runs through every slide — appropriate for a scientific audience.
- Delivered live from a laptop, projected. Type must be legible from the back of a room.

## 3. Language conventions

- Body prose in **Spanish**.
- Keep **English technical terms** inline, usually glossed in parentheses on first use: LLMs, prompt, output, hallucinations (alucinaciones), few-shot, bias (sesgos), primary source (fuente primaria), drafts (borradores), findings, Code Interpreter.

## 4. Technical constraints (hard requirements)

- One standalone HTML file. No external JS dependencies. Web fonts from Google Fonts are acceptable; everything else self-contained.
- Structure: 12 `<section class="slide">` blocks, each clearly commented and independently editable/duplicable.
- Navigation: `→` / `Space` / `PageDown` = next; `←` / `PageUp` = prev; `Home`/`End` = first/last; `F` = fullscreen toggle; click right ~60% = next, left ~40% = prev; touch swipe left/right; clickable bottom progress segments jump to any slide.
- Chrome: slide counter (`03 / 12`), top status/tab bar showing a per-slide filename, bottom progress bar, small keyboard-hint glyph.
- Deep-linking: keep URL hash in sync (`#3`) so any slide is bookmarkable.
- Motion: typewriter / decode reveal on each slide's heading; quick upward slide (~360ms) plus a brief scanline flicker on slide change; blinking block cursor.
- Accessibility: honor `prefers-reduced-motion` (instant fallback — no typewriter, no flicker, no blink); aria labels on nav controls; maintain readable contrast.
- Responsive: collapse two-column grids to one column below ~960px.

## 5. Design direction — "Terminal / código"

Dark developer terminal / IDE aesthetic. Monospace throughout. Command-line motifs: a shell prompt line per slide (`investigador@taller:~$ <command>`), `>` list bullets, `#` eyebrows, line numbers, blinking cursor, faux code-block "window" cards with red/yellow/green dots, faint persistent CRT scanlines + vignette.

**Design tokens (match these, or improve within the same language):**

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

Accent usage: green is the primary accent (headings' highlighted word, prompts, `>` bullets, "good practice" callouts); amber for tips/cautions; coral for danger/strings; blue for identifiers/links; purple sparingly for keywords.

## 6. Content — slide by slide

Each slide opens with a shell prompt command (shown in `mono`) and carries an eyebrow (`# NN · Topic`), a heading with one highlighted word, and the body below. Tab filename in brackets is what the top bar shows.

1. **Portada** `[portada.md]` — prompt `./iniciar-taller.sh --modo presentacion`. Eyebrow `# Taller · [Universidad]`. Title: *Inteligencia Artificial para la Investigación.* Subtitle: *Herramientas y flujos de trabajo para estudiantes e investigadores.* Footer: `Ponente: [Nombre] · [Fecha]` + nav hint.
2. **Agenda del día** `[agenda.md]` — prompt `cat agenda.md`. Two-column numbered list (01–10): ¿Por qué IA en la investigación? · Panorama de herramientas · Búsqueda y revisión de literatura · Lectura y síntesis de fuentes · Escritura académica asistida · Análisis de datos y código · Prompting efectivo · Ética e integridad académica · Ejercicio práctico · Recursos y cierre.
3. **¿Por qué IA en la investigación?** `[por-que.md]` — prompt `echo "¿por qué IA?"`. Lead: la IA generativa (LLMs) no reemplaza el criterio del investigador: amplifica su productividad. Bullets: acelera tareas repetitivas · explora la literatura más rápido · itera ideas y borradores (drafts). Note (green): *Siempre con verificación humana.*
4. **Panorama de herramientas** `[panorama.md]` — prompt `ls -la ./herramientas`. Four category cards with tool tags: **Búsqueda & literatura** (Elicit, Consensus, Semantic Scholar, Perplexity) · **Lectura & síntesis** (NotebookLM, ChatPDF, SciSpace) · **Escritura & edición** (ChatGPT, Claude, Paperpal) · **Datos & código** (Claude, ChatGPT Code Interpreter, Julius AI).
5. **Búsqueda y revisión de literatura** `[literatura.md]` — prompt `grep -r "evidencia" ./papers`. Objetivo: encontrar y filtrar literatura relevante. Bullets: Elicit (formula la pregunta, extrae findings) · Consensus (respuestas basadas en evidencia). Note (tip): *Verifica siempre la fuente primaria (primary source).*
6. **Lectura y síntesis de fuentes** `[sintesis.md]` — prompt `notebooklm --upload ./fuentes/*.pdf`. Bullets: NotebookLM (sube PDFs, pregunta con citas a tus propios documentos) · genera resúmenes, líneas de tiempo, mapas conceptuales. Note (warn): *Cuidado con las alucinaciones (hallucinations): verifica cada cita.*
7. **Escritura académica asistida** `[escritura.md]` — prompt `vim manuscrito.tex`. Use tags: estructurar · parafrasear · mejorar la claridad · traducir. Lead: el borrador puede ser de la IA; la voz y las ideas son tuyas. Note (integrity): *Declara el uso de IA según la política de tu institución.*
8. **Análisis de datos y código** `[datos.py]` — prompt `python analisis.py`. Left: bullet on pasting data / describing the problem; IA genera y explica código (Python / R); case tags (limpieza de datos, estadística descriptiva, visualización). Right: faux code-block card with a small pandas `read_csv`/`describe`/`plot` snippet. Note (tip): *Pide que explique cada paso; no ejecutes código que no entiendas.*
9. **Prompting efectivo** `[prompting.md]` — prompt `man prompting`. Four principle cards: 01 Rol (asigna un rol) · 02 Contexto (objetivo y audiencia) · 03 Ejemplos (few-shot) · 04 Formato (estructura y longitud del output).
10. **Ética e integridad académica** `[etica.md]` — prompt `cat --warnings etica.md`. Four warning cards: Verificación (la IA puede inventar datos y referencias) · Transparencia (cita el uso de IA) · Privacidad (no subas datos sensibles) · Sesgos / bias (los modelos reflejan los sesgos de sus datos).
11. **Ejercicio práctico** `[ejercicio.sh]` — prompt `./ejercicio.sh --start`. Instrucción: elige un paper de tu área. Steps: 1) resume su contribución con una herramienta · 2) formula 3 preguntas críticas · 3) verifica una afirmación contra la fuente. Meta (green): *15 minutos · en parejas.*
12. **Recursos y cierre** `[cierre.md]` — prompt `git commit -m "gracias :)"`. Resource list: diapositivas y guía de prompts `[enlace]` · Preguntas / Q&A · Gracias `[correo de contacto]`. Closing prompt line with blinking cursor.

## 7. Placeholders to leave unfilled

`[Nombre]` (presenter), `[Fecha]`, real university name (currently the literal "Universidad"), `[enlace]` (slides + prompt guide), `[correo de contacto]`.

## 8. Open content decision (flag for evaluation)

The reference deck above is a **generic survey** of third-party AI research tools. The project's planning notes describe a more original alternative: a narrative built on the presenter's **real Claude Code agent stack and live case studies** (parallel literature review, deep-research with adversarial fact-checking, an autonomous weekly pipeline, an agent building its own memory, HPC job submission). That version is more credible and "meta" but is narrower, more advanced, and requires scrubbing private repo paths and credentials. The generic survey is the current baseline; note which direction any generated deck assumes.

## 9. How to evaluate the generated deck

- Single file, opens clean in a browser, zero console errors, no build step.
- All 12 slides present; content faithful to Section 6; Spanish-body / English-term convention respected.
- Design tokens (Section 5) honored; terminal aesthetic coherent; type legible from the back of a room.
- Every control in Section 4 works; reduced-motion fallback works; two-column grids collapse on narrow widths.
- Placeholders (Section 7) left as placeholders, not invented.
- Bonus: measurably improves on the reference — typographic rhythm, motion restraint, hierarchy — without breaking the aesthetic.

## 10. Reference files

- Target / chosen direction: `taller-ia-alt3-terminal.html`.
- Deprioritized alternates (kept for reference, not the target): `taller-ia-alt1-editorial.html`, `taller-ia-alt2-swiss.html`, `taller-ia-alt4-color-mexicano.html`, `taller-ia-alt5-minimal.html`.
- Earlier, separate "technical-editorial hub" exploration (Fraunces / Newsreader, `index.html` + `case-study-meta.html`): **not** the target for this handoff.
