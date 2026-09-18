"""
cheap_talk_engine.py

Core, reusable engine for the Cheap-Talk Audit.

STEP 1 (classic benchmark): apply the standard Harsanyi / Crawford-Sobel
cheap-talk model directly -- Trust or Verify, given a type with a known
keep-probability. No similarity variable exists in this step.

STEP 2 (similarity extension): add a payoff-irrelevant SAME/DIFF profile
cue and test whether trusting based on similarity alone tracks the
classic benchmark, or diverges from it.

Honesty note on reproducibility
--------------------------------
The original PS1 proposal used a JavaScript mulberry32 pseudo-random
generator ported to Python for exact cross-language number matching.
This module instead uses Python's standard `random.Random(seed)` for
simplicity, per the author's instruction to keep this GitHub version
basic rather than cross-language-exact. The seed 206 is kept the same
as the paper for continuity, but the specific per-round draws --
and therefore the exact totals -- will NOT bit-match the original
mulberry32 engine. What DOES carry over and is the important,
reproducible claim is the qualitative and threshold result:
  - p* = 0.6 indifference threshold (exact, derived algebraically)
  - the benchmark (Trust iff aligned) outperforms a similarity-only
    rule on average
  - similarity, by construction, carries no real information about
    type (P(aligned | SAME) should sit near 0.5 on average over many
    seeds)
"""

import random
import json
import os

# ---------- Payoffs (from the PS1 proposal) ----------
TRUST_KEEP = 6
TRUST_BREAK = -4
VERIFY = 2
KEEP_PROB = {"aligned": 0.85, "misaligned": 0.25}

POLICIES = ["benchmark", "always_verify", "always_trust", "similarity"]


# ---------- Step 1: classic Bayesian (Harsanyi) benchmark ----------

def expected_utility_trust(keep_prob):
    """EU(Trust) = keep_prob * 6 + (1-keep_prob) * (-4)"""
    return keep_prob * TRUST_KEEP + (1 - keep_prob) * TRUST_BREAK


def classic_best_response(keep_prob):
    """Textbook Bayesian Nash best response: Trust if EU(Trust) > EU(Verify)."""
    eu_trust = expected_utility_trust(keep_prob)
    return ("Trust" if eu_trust > VERIFY else "Verify"), eu_trust


def p_star():
    """Indifference keep-probability: 6p - 4(1-p) = 2 -> p = 0.6"""
    return (VERIFY - TRUST_BREAK) / (TRUST_KEEP - TRUST_BREAK)


# ---------- Step 2: similarity extension ----------

def make_schedule(seed, n_rounds=12):
    """
    Build one session: n_rounds rounds, half aligned/half misaligned,
    half SAME profile/half DIFF profile, independently shuffled so
    that profile carries no real information about type by construction.
    """
    rng = random.Random(seed)
    types = ["aligned", "misaligned"] * (n_rounds // 2)
    profiles = ["SAME", "DIFF"] * (n_rounds // 2)
    rng.shuffle(types)
    rng.shuffle(profiles)
    rounds = []
    for t, prof in zip(types, profiles):
        kept = rng.random() < KEEP_PROB[t]
        rounds.append({"type": t, "profile": prof, "kept": kept})
    return rounds


def score_policy(rounds, policy):
    total = 0
    for r in rounds:
        if policy == "benchmark":
            action = "Trust" if r["type"] == "aligned" else "Verify"
        elif policy == "always_verify":
            action = "Verify"
        elif policy == "always_trust":
            action = "Trust"
        elif policy == "similarity":
            action = "Trust" if r["profile"] == "SAME" else "Verify"
        else:
            raise ValueError(f"unknown policy: {policy}")

        if action == "Verify":
            total += VERIFY
        else:
            total += TRUST_KEEP if r["kept"] else TRUST_BREAK
    return total


def similarity_gap(rounds):
    """P(aligned | profile == SAME). Should sit near 0.5 if similarity
    carries no real information about type."""
    same_rounds = [r for r in rounds if r["profile"] == "SAME"]
    if not same_rounds:
        return None
    aligned_and_same = sum(1 for r in same_rounds if r["type"] == "aligned")
    return aligned_and_same / len(same_rounds)


def run_seed(seed, n_rounds=12):
    rounds = make_schedule(seed, n_rounds)
    scores = {p: score_policy(rounds, p) for p in POLICIES}
    gap = similarity_gap(rounds)
    return rounds, scores, gap


def monte_carlo(n_seeds=1000, n_rounds=12, start_seed=0):
    totals = {p: [] for p in POLICIES}
    gaps = []
    for s in range(start_seed, start_seed + n_seeds):
        rounds, scores, gap = run_seed(s, n_rounds)
        for p in POLICIES:
            totals[p].append(scores[p])
        if gap is not None:
            gaps.append(gap)
    means = {p: sum(v) / len(v) for p, v in totals.items()}
    mean_gap = sum(gaps) / len(gaps)
    share_similarity_below_verify = sum(
        1 for a, b in zip(totals["similarity"], totals["always_verify"]) if a < b
    ) / n_seeds
    return means, mean_gap, share_similarity_below_verify


if __name__ == "__main__":
    print("=== STEP 1: Classic Harsanyi/Crawford-Sobel benchmark ===\n")
    pstar = p_star()
    print(f"Indifference threshold p* = {pstar}")
    for label, kp in [("aligned", 0.85), ("misaligned", 0.25)]:
        action, eu = classic_best_response(kp)
        print(f"  type={label:10s} keep_prob={kp:.2f}  EU(Trust)={eu:+.2f}  "
              f"EU(Verify)={VERIFY:+.2f}  -> {action}")

    print("\n=== STEP 2: Similarity extension, seed=206 ===\n")
    rounds, scores, gap = run_seed(206)
    for i, r in enumerate(rounds, 1):
        print(f"  round {i:2d}: type={r['type']:10s} profile={r['profile']:4s} "
              f"kept={r['kept']}")
    print("\nPolicy totals (seed 206, this Python engine):")
    for p in POLICIES:
        print(f"  {p:<15s}: {scores[p]:+d}")
    print(f"\nP(aligned | SAME) on seed 206: {gap:.2f}")

    print("\n=== Monte Carlo over 1000 seeds ===\n")
    means, mean_gap, share_below = monte_carlo(1000)
    for p in POLICIES:
        print(f"  {p:<15s} mean: {means[p]:+.2f}")
    print(f"  mean P(aligned | SAME) across seeds: {mean_gap:.3f}")
    print(f"  share of seeds where similarity < always_verify: {share_below:.3f}")

    # write JSON validation record
    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    record = {
        "p_star": pstar,
        "seed_206": {
            "policy_totals": scores,
            "p_aligned_given_same": gap,
        },
        "monte_carlo_1000_seeds": {
            "policy_means": means,
            "mean_p_aligned_given_same": mean_gap,
            "share_similarity_below_always_verify": share_below,
        },
        "note": (
            "This engine uses Python's standard random module seeded "
            "independently of the original JavaScript mulberry32 engine "
            "described in the PS1 proposal. Numbers here are internally "
            "reproducible (same seed -> same output) but are not "
            "bit-identical to the original JS/Python cross-checked totals "
            "reported in the paper. The qualitative claims (p*=0.6; "
            "benchmark outperforms similarity-only rule; similarity "
            "carries no real information about type) are the reproducible "
            "evidence this repository supports."
        ),
    }
    out_path = os.path.join(out_dir, "ps1_validation.json")
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"\nWrote validation record to {out_path}")
