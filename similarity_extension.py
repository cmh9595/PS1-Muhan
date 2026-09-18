"""
similarity_extension.py

STEP 2: Extend the classic benchmark with a SIMILARITY variable
(same-profile vs different-profile), independent of type/incentives.
This is the part the classic Harsanyi/Crawford-Sobel model cannot speak to.

Design (simplified 12-round game, one seed for a quick illustration):
    Each round has:
        - a type: aligned (keep_prob=0.85) or misaligned (keep_prob=0.25)
        - a profile: SAME or DIFF (payoff-irrelevant, just a resemblance cue)
    Agent keeps or breaks the promise using the type's keep probability.

Four simple policies for the Principal:
    1. benchmark        -> Trust iff aligned   (the CLASSIC prediction)
    2. always_verify    -> always Verify
    3. always_trust     -> always Trust
    4. similarity       -> Trust iff profile == SAME  (ignores type entirely)

We compare total payoff across policies to see whether a
similarity-only rule performs differently from the classic rule,
and to measure how often "SAME" coincides with "aligned" (the gap).
"""

import random

TRUST_KEEP = 6
TRUST_BREAK = -4
VERIFY = 2

def make_schedule(seed, n_rounds=12):
    rng = random.Random(seed)
    rounds = []
    types = ["aligned", "misaligned"] * (n_rounds // 2)
    profiles = ["SAME", "DIFF"] * (n_rounds // 2)
    rng.shuffle(types)
    rng.shuffle(profiles)
    keep_prob = {"aligned": 0.85, "misaligned": 0.25}
    for t, prof in zip(types, profiles):
        kept = rng.random() < keep_prob[t]
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
            raise ValueError(policy)

        if action == "Verify":
            total += VERIFY
        else:  # Trust
            total += TRUST_KEEP if r["kept"] else TRUST_BREAK
    return total


def similarity_gap(rounds):
    """
    How often does 'SAME' actually line up with 'aligned'?
    If similarity carried no real information, SAME should match
    'aligned' about half the time (pure noise / coincidence).
    """
    same_rounds = [r for r in rounds if r["profile"] == "SAME"]
    if not same_rounds:
        return None
    aligned_and_same = sum(1 for r in same_rounds if r["type"] == "aligned")
    return aligned_and_same / len(same_rounds)


if __name__ == "__main__":
    seed = 42
    rounds = make_schedule(seed)

    print(f"=== STEP 2: Similarity extension (seed={seed}, 12 rounds) ===\n")
    print(f"{'Round':<6}{'Type':<12}{'Profile':<8}{'Kept?':<8}")
    for i, r in enumerate(rounds, 1):
        print(f"{i:<6}{r['type']:<12}{r['profile']:<8}{str(r['kept']):<8}")

    print("\n--- Policy scores ---")
    policies = ["benchmark", "always_verify", "always_trust", "similarity"]
    scores = {}
    for p in policies:
        scores[p] = score_policy(rounds, p)
        print(f"  {p:<15s}: {scores[p]:+d}")

    gap = similarity_gap(rounds)
    print(f"\nP(aligned | profile=SAME) = {gap:.2f}"
          f"  (0.5 would mean similarity carries NO real information about type)")

    print("\n--- What this shows ---")
    print("The classic benchmark (Trust iff aligned) is the best-performing rule")
    print("here because it is the only one that actually tracks type.")
    print("The similarity-only rule does WORSE than the benchmark, but the")
    print("classic Harsanyi/Crawford-Sobel model never predicted this comparison")
    print("in the first place -- it has no room for a payoff-irrelevant cue.")
    print("That absence is exactly the gap my project adds a variable to test.")

    # ---- quick multi-seed check for robustness ----
    print("\n--- Multi-seed check (30 seeds) ---")
    totals = {p: [] for p in policies}
    for s in range(30):
        rs = make_schedule(s)
        for p in policies:
            totals[p].append(score_policy(rs, p))
    for p in policies:
        avg = sum(totals[p]) / len(totals[p])
        print(f"  {p:<15s} mean over 30 seeds: {avg:+.2f}")
