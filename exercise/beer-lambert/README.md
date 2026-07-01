# Day-2 exercise — "Trust, but benchmark": a Beer-Lambert calibration skill

The core hands-on exercise. Attendees **author** an opencode skill that builds a
UV-Vis calibration, predicts an unknown concentration, discovers via a benchmark
that their beautiful pipeline is confidently *wrong*, and fixes it with a
verification step. See §7 of [../../docs/workshop-plan.md](../../docs/workshop-plan.md)
for the full design.

## Files

| File | Role |
|---|---|
| `generate_data.py` | Generates the synthetic dataset + hidden ground truth. Deterministic (seed 42). |
| `SKILL.md.template` | The fill-in-the-blank scaffold attendees complete, milestone by milestone. |
| `data/` | Generated output (git-ignored). Calibration spectra, index, unknown, and `ground_truth.txt`. |

## Generate the data

```
python generate_data.py     # needs numpy
```

Prints the instructor benchmark numbers and writes everything to `data/`.

**Expected result (seed 42):**

| Pipeline | Predicts | Error | Calibration R² |
|---|---|---|---|
| Naive (raw peak, no baseline correction) | 10.78 µM | **+19.8 %** | **0.9998** |
| Baseline-corrected | 9.03 µM | +0.3 % | 0.9998 |
| **Truth** | **9.00 µM** | — | — |

That's the lesson in one table: a near-perfect fit (R² = 0.9998) with a 20%-wrong
answer. Only the benchmark against the known value exposes it.

## Handout hygiene

- `data/ground_truth.txt` holds the answer — **do not distribute before milestone M4.**
  It's git-ignored; when you package the handout, ship `data/` *without* it.
- The unknown's concentration appears nowhere in the handed-out files.

## Still to test before this is on a slide (see plan §10)

Run the **whole** exercise in **opencode on the actual free model**, as a slow
attendee would, and confirm: (1) the free model writes a working calibration fit
without hand-holding, (2) whether it commits or skips the baseline error on its
own — either is fine, but you need to know which so your live narration matches,
(3) M0–M4 fit inside ~40 minutes at slow-typing pace.
