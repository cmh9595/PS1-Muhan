"""
classic_benchmark.py

STEP 1: Apply the CLASSIC Harsanyi / Crawford-Sobel cheap-talk benchmark
to the trust game, with NO similarity variable.

This is the "off-the-shelf" model applied directly to my research question,
before I add anything new.

Game:
    Nature picks Agent's type: aligned (prob 0.5) or misaligned (prob 0.5)
    - aligned type keeps promise with probability 0.85
    - misaligned type keeps promise with probability 0.25
    Principal does NOT observe the type directly (only the public payoff table).
    Principal chooses: Trust or Verify
        Trust:  +6 if Agent keeps, -4 if Agent breaks
        Verify: +2 for sure

Question: does the classic model, by itself, explain WHO gets trusted,
or does it only tell us WHEN trust is rational given a KNOWN type?
"""

import random

# ---------- Step 1: classic Bayesian (Harsanyi) benchmark ----------

def expected_utility_trust(keep_prob):
    """EU(Trust) = keep_prob * 6 + (1-keep_prob) * (-4)"""
    return keep_prob * 6 + (1 - keep_prob) * (-4)

EU_VERIFY = 2  # certain payoff

def classic_best_response(keep_prob):
    """The textbook Bayesian Nash best response: Trust if EU(Trust) > EU(Verify)."""
    eu_trust = expected_utility_trust(keep_prob)
    return "Trust" if eu_trust > EU_VERIFY else "Verify", eu_trust


def p_star():
    """Solve EU(Trust) = EU(Verify) for the indifference keep-probability."""
    # 6p - 4(1-p) = 2  ->  10p - 4 = 2  ->  p = 0.6
    return (2 - (-4)) / (6 - (-4))


if __name__ == "__main__":
    print("=== STEP 1: Classic Harsanyi/Crawford-Sobel benchmark (no similarity) ===\n")

    pstar = p_star()
    print(f"Indifference threshold p* = {pstar}")

    for label, keep_prob in [("aligned", 0.85), ("misaligned", 0.25)]:
        action, eu = classic_best_response(keep_prob)
        print(f"  type={label:10s} keep_prob={keep_prob:.2f}  EU(Trust)={eu:+.2f}  "
              f"EU(Verify)={EU_VERIFY:+.2f}  -> best response: {action}")

    print("\nClassic prediction: Trust iff aligned. Verify iff misaligned.")
    print("This is the FULL prediction of the classic model.")
    print("It says NOTHING about whether an unrelated cue (e.g. similarity)")
    print("could also move trust up or down. That is the open gap.\n")
