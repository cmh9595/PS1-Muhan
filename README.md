# Cheap-Talk Audit: From Classic Benchmark to Similarity Extension

Supplementary code for the PS1 proposal *"Pricing a Promise: When
Similarity, Not Incentives, Buys Trust in AI Negotiation."*

## What this shows

**Step 1.** Apply the classic Harsanyi / Crawford-Sobel cheap-talk
model directly to a Trust-or-Verify game with a known agent type.

**Step 2.** Extend the game with a payoff-irrelevant SAME/DIFF
"similarity" cue and show that the classic model has no room to even
pose the question of whether that cue moves trust independent of
incentives -- which is the gap this project studies.

## Files

| File | Purpose |
|---|---|
| `classic_benchmark.py` | Minimal standalone script for Step 1 only. Run it first to see the p*=0.6 threshold in isolation. |
| `similarity_extension.py` | Minimal standalone script for Step 2 only, one illustrative seed (42) and a 30-seed check. |
| `cheap_talk_engine.py` | Consolidated, reusable engine (both steps), used by the test suite. Uses seed 206 to stay consistent with the paper's chosen seed, and runs a full 1,000-seed Monte Carlo. Writes `outputs/ps1_validation.json`. |
| `tests/test_cheap_talk.py` | Unit tests for the engine's structural claims (p*, balanced schedule, reproducibility, benchmark beats similarity on average). |
| `outputs/ps1_validation.json` | Generated validation record (see below). |
| `AI_USE_DISCLOSURE.md` | What was human-authored vs. AI-assisted. |
| `LICENSE` | MIT. |
| `requirements.txt` | None -- standard library only. |

## How to run

```bash
# Step 1 only
python3 classic_benchmark.py

# Step 2 only
python3 similarity_extension.py

# Full engine: benchmark, seed 206, and 1,000-seed Monte Carlo
python3 cheap_talk_engine.py

# Test suite
python -m unittest tests.test_cheap_talk -v
```

## Key results (this engine, seed 206 and 1,000-seed Monte Carlo)

- Indifference threshold: **p\* = 0.6** (exact, algebraic)
- Seed 206 policy totals: benchmark **+38**, always-Verify **+24**,
  always-Trust **+22**, similarity **+28**
- 1,000-seed means: benchmark **+38.74**, always-Verify **+24.00**,
  always-Trust **+17.56**, similarity **+20.50**
- Similarity underperforms always-Verify in **58.7%** of seeds
- **P(aligned \| profile = SAME) ≈ 0.497** across 1,000 seeds --
  confirming similarity carries essentially no real information about
  an agent's true type

These numbers are qualitatively consistent with the totals reported
in the PS1 proposal (e.g. mean order: benchmark > always-Verify >
similarity > always-Trust; similarity below always-Verify in roughly
59% of seeds), even though this is an independently written engine
(see the reproducibility note below).

## Reproducibility note: this engine vs. the original JS/Python pair

The PS1 proposal used a JavaScript `mulberry32` pseudo-random number
generator, cross-checked against a Python port, for exact bit-level
agreement between the two languages. This repository instead uses
Python's standard `random.Random(seed)` for simplicity, per project
scope. That means:

- Exact per-round schedules and exact totals will **not** match the
  original JS engine's numbers one-for-one.
- What **does** reproduce is the qualitative claim structure: the
  p\*=0.6 threshold (derived algebraically, not simulated, so it is
  identical either way), and the ranking/behavior of the four
  policies under Monte Carlo averaging.
- A future version could port `mulberry32` to Python for exact
  cross-language matching, following the original design; this was
  intentionally out of scope for this basic version.

## The gap this motivates

The classic Harsanyi / Crawford-Sobel model, applied on its own,
predicts *only* "Trust iff aligned." It has no variable for a
resemblance cue and therefore cannot even pose -- let alone answer --
the question of whether an AI agent's similarity to the principal
moves trust independent of incentives. That is the interdisciplinary
gap (economics + computation + behavioral science) this project is
designed to fill.
