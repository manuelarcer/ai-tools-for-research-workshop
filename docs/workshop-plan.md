---
title: "Workshop Plan — AI Tools for Research"
type: plan
status: active
supersedes: docs/workshop-ai-tools-for-research.md
target: "July 2026 (exact date TBC with Raul Ocampo)"
harness: opencode
delivery: remote / online
format: "3 days × 2 hours — self-paced hands-on"
last_reviewed: 2026-07-01
---

# Workshop Plan — AI Tools for Research

**This is the authoritative plan.** It is the output of a design grilling that pressure-tested
every load-bearing assumption. Where the earlier seed note
([workshop-ai-tools-for-research.md](workshop-ai-tools-for-research.md)) or the HTML deck
contradicts anything here, this document wins — see §12 for the diff.

---

## 1. The verdict — what this is, and what it is not

It is a **hands-on workshop**, not a keynote. Attendees do not watch a tour of the presenter's
personal agent stack — they **build a small, reproducible, self-verifying research tool on their
own machine**, and leave able to do one concrete thing Monday they couldn't do Friday.

- **The one concrete takeaway:** *author a small, self-verifying skill in opencode, on your own
  machine, and know why you can trust its output.*
- **Success metric (set by the presenter):** attendees leave **motivated to explore** — and with
  a working artifact and a mental model, not just admiration.
- **Through-line:** *"From asking a chatbot questions → to building research tools you can
  trust."* Verification / benchmarking is the spine of the whole workshop, present from the first
  demo to the last exercise.

Why this framing: the presenter's real stack (Telegram interface, Whisper venv, private Obsidian
vault, HPC access, bespoke skills) is **not reproducible by a remote attendee**. Admiring it is a
keynote. So the workshop is rebuilt around what an attendee can actually reproduce.

---

## 2. Audience & format

- **Audience:** grad students + research staff / professors at the PhD university. **Mixed
  technical background** — including people who have never opened a terminal. Remote / online.
- **Format:** **3 days × 2 hours.** Teaches concepts *and* leaves room to practice without a
  single remote-fatigue death march.
- **Hands-on model:** **self-paced, guided.** A written **guide with mini-milestones** is shared
  to everyone. The presenter follows it live, slowly, answering questions, and will likely *not*
  reach the end goal on screen — that is by design. Advanced attendees race ahead independently;
  slower attendees still bank a real win at an early milestone. **The guide is the remote TA**
  (you cannot walk a Zoom room; the guide walks it for you), and it is the recovery path for
  anyone who falls behind or misses a day.

---

## 3. Non-negotiables — the decisions locked in the grilling

A ledger so these are not relitigated later. Each has a reason attached.

| Decision | Why |
|---|---|
| **Workshop, not keynote** — they build | Attendees can't reproduce the presenter's private stack; admiration ≠ capability |
| **Reproducible without any private stack** — no vault, Telegram, Whisper, HPC | Everything shown must run on an attendee's laptop |
| **Whole room on opencode** (CLI + cross-platform desktop app) | Cross-platform (Mac/Windows), a genuinely free model path, per-agent model selection. **Not** Claude Code, **not** a split room |
| **Free-model default path** | Academic budgets. opencode is BYO-model; the free model is the default, a paid model is opt-in |
| **Signature pattern: strong model plans → free model executes → *always benchmark the output*** | Real cost architecture *and* the core trust lesson in one move |
| **Verify-everything is the through-line** | A skeptical scientific audience dismisses any happy-path demo. Coherent from opener to final exercise |
| **Hands-on = author, not run** | The thesis is "make your own." Running the presenter's skill teaches driving, not building |
| **Synthetic data with known ground truth** | You *define* the correct answer, so verification becomes arithmetic, not hand-waving |
| **Self-paced guide + mini-milestones** | Solves the mixed-background spread, the remote no-walking problem, attrition recovery, and the "40 min from scratch is too much" problem — all at once |
| **Engineered silent error + benchmark catch** | Turns the biggest liability (silent data errors) into the core lesson (build verification) |

---

## 4. The three-day arc

Each day is **~2 hours**, realistically: ~15 min settle/setup, ~40 min concept, ~40 min hands-on,
~15 min Q&A/wrap. That budget allows **one** hands-on block per day — and it *will* overrun
remotely, so the milestone model (not "finish everything") is what makes it fit.

| Day | Goal | Spine | Outcome |
|---|---|---|---|
| **Day 1 — Foundations + a reproducible wow** | Make the demos land as understandable, not magic; hook them | Concepts (§5) + the **lit-review-with-checkers** opener (§6) | Everyone installed, oriented, and has seen a *verified* agent do real research work |
| **Day 2 — Build a tool you can trust** | The core hour: author a self-verifying skill | The **Beer-Lambert exercise** (§7), self-paced to milestones, culminating in the benchmark twist | Everyone reaches at least an early milestone; the "verify everything" lesson is felt, not told |
| **Day 3 — Your own problem** | Transfer the pattern to their real work | Bring-your-own data/problem, scaffolded; or extend the skill; or explore the public skills repo (§9) | They start their *own* self-verifying workflow, and leave motivated to keep going |

**Day 3 pre-scoping (important):** an open-ended "build your own thing" day, remote, mixed
audience, is either magic or 20 people stuck in silence. So attendees are asked *at the end of
Day 2* to bring a **pre-scoped** small problem to Day 3 (a dataset, a paper, a repetitive task).
No blank-page day.

---

## 5. Foundational concepts (Day 1) — taught harness-agnostic, shown in opencode

Teach the **pattern**; point each attendee at their tool's docs for exact syntax. Where Claude
Code and opencode differ, name the translation so nobody is lost.

- **What an LLM is / isn't** — tokens, the context window, why context management matters.
- **The agent loop** — system prompt, tools, the loop. An agent is not a chat box.
- **Context layering** — global rules vs project rules vs session context. *(Translation:
  `CLAUDE.md` → opencode `AGENTS.md` / rules.)*
- **Skills = reusable instructions** with progressive disclosure. Demo *running* one.
- **Subagents & per-agent model selection** — opencode's real strength and the **cost story**:
  cheap/fast model to explore, capable model to build, in one session.
- **Hooks = lifecycle triggers.** *(Translation: Claude Code file/shell hooks → opencode JS/TS
  **plugins** keyed to lifecycle events, e.g. `tool.execute.before`.)* **Taught as a concept and
  shown** — not hand-authored live by non-coders. Higher ceremony in opencode; be honest about it.
- **MCP / tools** — giving the agent real capabilities.
- **Safeguards & control** — permissions (allow/ask), why a researcher stays in the loop, what
  the agent should pause on.
- **The trust thread** — hallucination and fabrication; why, for science, verification is *not
  optional*. This slide sets up everything that follows.

---

## 6. The opener — `lit-review` **with checkers** (Day 1 wow)

The motivating "oh, *wow*" demo. Two hard constraints, both self-imposed by the design so the
opener does not contradict the workshop's own thesis:

1. **Reproducible in the student environment.** `lit-review` is a Claude Code skill that fans out
   parallel subagents. It **must be run in opencode on the free model beforehand** and adjusted /
   ported as needed. If it only sings on the presenter's machine in Claude Code on a strong model,
   it is a bait-and-switch — a keynote demo in the first 20 minutes. **Test it in the exact
   environment attendees will use.**
2. **Shown *with* verification.** `lit-review` lives in the fabricated-citation domain (fake DOIs,
   plausible-but-nonexistent papers). An unverified happy-path opener would detonate the
   presenter's credibility *before* the "always verify" thesis is even stated. So the opener shows
   lit-review **and a checker that verifies/flags its citations** — making "verify everything" the
   through-line from minute one. The failure mode is not hidden; it is the point.

---

## 7. The core exercise (Day 2) — "Trust, but benchmark": a Beer-Lambert calibration skill

Attendees **author** an opencode skill that takes a UV-Vis calibration series, builds the
calibration curve, and predicts an unknown concentration — then **discover, via a benchmark, that
their beautiful pipeline is confidently wrong**, and fix it with a verification step.

UV-Vis / Beer-Lambert was chosen because every experimentalist has done it by hand, the math is a
straight line, and the ground truth is *definitional*.

### 7.1 The synthetic data (generated → ground truth is exact)

Built on real physics so it is honest — e.g. **methylene blue, λmax ≈ 664 nm, ε ≈ 95,000
M⁻¹cm⁻¹, path length 1 cm.** Generate absorbance-vs-wavelength CSVs (400–700 nm):

- **Calibration series:** 6 spectra at known concentrations (e.g. 2, 4, 6, 8, 10, 12 µM). Each is
  a Gaussian peak at 664 nm with height `A = ε·l·c`, **plus** (a) small Gaussian noise and (b) **a
  sloping/offset baseline that varies slightly per spectrum** (scattering, lamp drift, cuvette —
  utterly realistic).
- **One "unknown"** at a concentration you know but do not reveal — e.g. **9.0 µM** — with a
  baseline offset *different* from the calibration set (different day, different cuvette).
- A hidden `ground_truth.txt`, not shared until milestone M4.

It is synthetic, so truth is arithmetic; it *looks* like real messy lab output; it is credible
because methylene blue's ε is real. This dissolves the real-vs-synthetic tension. Show one
**downloaded real spectrum** alongside for street credibility.

### 7.2 The engineered silent error (the heart of it)

The obvious first-pass code for "find the peak absorbance" is `A_peak = spectrum.max()` — **the
single most common real Beer-Lambert mistake: reading the peak without baseline-correcting
first.** It is not contrived; it is *the* mistake. Because the unknown's baseline differs from the
calibration's, the predicted concentration comes out ~20% off (9.0 → ~10.9 µM).

**The gold:** R² is still **0.999**. The calibration line is gorgeous; every instinct says
"done." This teaches the deepest lesson these tools can offer a scientist — **a perfect fit is not
a correct answer** — and only the benchmark against known truth exposes it.

**Robustness (important):** if the free model is smart enough to baseline-correct *on its own*,
the exercise **still works** — because the point is not "the model erred," it is *"you had no way
to know it was right until you checked."* The benchmark is the hero whether or not the bug
appears. This makes the lesson bulletproof against model behavior.

### 7.3 The milestones (the arc *is* the lesson)

| # | Milestone | What they feel |
|---|---|---|
| **M0** | Setup: load & plot one spectrum in opencode | "I'm in." (everyone reaches this) |
| **M1** | Skill loads all calibration spectra, extracts a peak per concentration, plots A vs c | first real win |
| **M2** | Fit the calibration line — slope, intercept, **R² = 0.999** | *false summit — feels finished* |
| **M3** | Predict the unknown's concentration → a confident number | *feels like victory* |
| **M4** | **Reveal ground truth. It's ~20% off. Record scratch.** *"But R² was perfect — how?"* | the twist |
| **M5** | Diagnose (baseline!), add the correction, re-run → within tolerance. **Bake an assertion into the skill** that fails loudly if a control deviates > X% | redemption via verification |
| **M6** (racers) | Residual plot, extrapolation guard (flag if the unknown is outside the calibration range), uncertainty propagation | the advanced never run out of runway |

M2–M3 seduce, M4 detonates, M5 redeems. The narrative is *inside* the exercise.

### 7.4 What they author, and the transferable lesson

A skill (`SKILL.md` + a ~40-line Python script it drives — pure numpy/scipy/matplotlib, trivial
for the free model) that calibrates, predicts, **and self-verifies against a control.** The
one-slide lesson:

> **A research skill you can trust is one that checks itself.** The verification step isn't
> overhead — it's the difference between a demo and an instrument.

This also lands the signature pattern (§3): **strong model plans the skill, free model executes
on the data — and you always benchmark the executor's output**, because M4 just showed why.

---

## 8. Day 3 — your own problem + explore

- **Bring-your-own:** attendees arrive with a pre-scoped small problem (see §4). Options:
  (a) apply the Beer-Lambert pattern to their own data; (b) extend the skill; (c) explore the
  public skills repo (§9) and adapt one.
- **Scaffolded, not blank.** The presenter and the guide provide the frame; attendees fill their
  own content. Goal is momentum and motivation, not a finished product.

---

## 9. Pre-workshop build backlog (the deliverables to make first)

1. **Synthetic-data generator** — produces the calibration CSVs + the hidden `ground_truth.txt`,
   with realistic baseline/noise; parameters tunable.
2. **The guide document** — self-paced, milestones M0–M6, written so a slow attendee and a racer
   both use it.
3. **`SKILL.md` template scaffold** — fill-in-the-blanks (achievable) rather than a blank file
   (strands half the room). Enough structure to reach M1 without copying the answer.
4. **Public "skills to explore" repo** — only general-audience-relevant skills, **scrubbed** of
   private paths, tokens, calendar entries, `chat_id`, `access.json`. Handed out for after the
   workshop; motivation to keep exploring.
5. **opencode setup guide** — install CLI + desktop app, connect a skill, connect a hook/plugin,
   configure the model — for **Mac and Windows**, tested on both.
6. **Deck rebuild** — reframe the existing HTML per §11.

---

## 10. Open risks / must-test before it's on a slide

- ⚠️ **Free-model competence, end to end.** The entire free path rests on the free model writing
  working numpy without hand-holding. **Run the whole Day-2 exercise in opencode on the actual
  free model, as a slow attendee would**, and confirm: (1) it writes a working calibration fit,
  (2) whether it commits *or* skips the baseline error (either is fine — but you must know which,
  so your live narration matches reality), (3) M0–M4 fit inside ~40 minutes at slow-typing pace.
  If the free model can't cleanly write the fit, the free-path premise cracks *here*.
- ⚠️ **`lit-review`-with-checkers in opencode on the free model** — test end to end (§6).
- ⚠️ **Hooks/plugins for non-coders** — opencode hooks are JS/TS plugins. Teach as concept, show,
  do **not** make professors hand-author TypeScript live.
- ⚠️ **Timing** — 2 h/day is tight; assume one hands-on block/day and expect overrun. Milestones,
  not completion, are the bar.
- ⚠️ **Attrition across 3 days** — the guide is the recovery path; keep each day standalone-ish.
- ⚠️ **Scrubbing** — the public repo and every on-screen artifact must exclude private paths,
  tokens, calendar, `chat_id`, channel/security (`access.json`) material.
- ⚠️ **Schedule crunch** — target is July 2026 and today is 2026-07-01. The backlog in §9 is
  substantial. Confirm the date with Raul and size the prep against it honestly.

---

## 11. Deck changes required (reconcile the existing HTML)

The current deck frames the workshop as *"a guided tour of the agent stack I actually run"* with
case studies as the centerpiece. That now contradicts §1. Required changes:

- **Hero:** reframe from "tour of my stack / case studies you read" → **"concepts + you build a
  research tool you can trust and reproduce."** *(Partially applied — see the updated hero lede.)*
- **Case studies → "what's possible / explore after."** Keep the meta case study as *one*
  illustration of what the tools can do, **not** the spine.
- **Add the hands-on exercise as the spine** — the Beer-Lambert build is the workshop's center.
- **Harness:** present the ideas as shown in **opencode**, not Claude Code (the deck itself was
  built with Claude Code — that meta-fact is fine to keep in the footer, but the *taught* tool is
  opencode).

---

## 12. What changed from the seed note (superseded decisions)

Explicit diff against [workshop-ai-tools-for-research.md](workshop-ai-tools-for-research.md):

| Seed note said | Now |
|---|---|
| Deliverable = browser HTML deck showcasing case studies | Hands-on **build** workshop; the deck merely *supports* Day-1 concepts |
| Centerpiece = meta case study / tour of the presenter's stack | Centerpiece = attendees **author a self-verifying skill** (Beer-Lambert) |
| Harness = Claude Code | Harness = **opencode**, whole room, free-model default |
| "Hands-on vs demo-only?" left open | **Hands-on**, self-paced, with mini-milestones |
| Case studies (lit pipeline, deep research, bench-to-cluster) as headline content | Repositioned as **"explore after"** motivation; a public scrubbed skills repo |
| Format / duration TBC | **3 days × 2 hours**, remote |

The seed note remains valuable as origin and as a source for the concept list and the "explore
after" material — but it no longer describes the design.
