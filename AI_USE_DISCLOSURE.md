# AI-Use Disclosure

This disclosure covers the code in this repository, following the
Human-first protocol described in the course's Three-Lens Studio and
the AI-use disclosure in the PS1 proposal, Appendix A.1.

## What was Human-Only

- The original research questions (Q1 economics, Q2 computation,
  Q3 behavior) in the PS1 proposal.
- The payoff structure (+6 / -4 / +2), the keep-probability
  placeholders (0.85 / 0.25), and the derivation of the indifference
  threshold p* = 0.6.
- The decision to extend the classic Harsanyi / Crawford-Sobel
  benchmark with a payoff-irrelevant similarity variable, based on
  DeBruine (2002).
- The identification of the gap: the classic model has no variable
  for a resemblance cue, so it cannot be used to test whether
  similarity moves trust independent of incentives.

## What AI assistance was used for

- Drafting the Python implementation (`cheap_talk_engine.py`) of the
  model specified above: the benchmark best-response rule, the
  session schedule generator, the four comparison policies, and the
  Monte Carlo loop.
- Drafting the `unittest` test suite (`tests/test_cheap_talk.py`)
  that checks the structural properties of the model (threshold
  value, balanced schedule, reproducibility, benchmark outperforming
  the similarity-only rule on average).
- Drafting this README, LICENSE boilerplate, and disclosure text.

## What was verified by the human author

- All code was run and its output inspected by the author.
- The qualitative claims (p* = 0.6; benchmark outperforms a
  similarity-only rule on average; similarity carries no real
  information about type) were checked against the numbers actually
  produced by running the scripts in this repository.
- The author confirms this Python engine uses the standard library
  `random` module and is **not** a byte-for-byte port of the original
  JavaScript `mulberry32` engine described in the PS1 proposal. Exact
  per-round totals will differ between the two engines; the
  qualitative pattern does not.

## Tool used

Claude (Anthropic), September 2026, for code drafting and file
organization based on the author's own model specification.
