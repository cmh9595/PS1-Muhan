"""
tests/test_cheap_talk.py

Run with:
    python -m unittest tests.test_cheap_talk -v

These tests check the structural properties claimed in the PS1 proposal:
  - the derived indifference threshold p* = 0.6
  - every strategy/policy is well-defined and produces a valid score
  - the benchmark policy outperforms the similarity-only policy on average
  - similarity carries no real information about type (P(aligned|SAME) ~ 0.5)
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cheap_talk_engine import (
    p_star,
    expected_utility_trust,
    classic_best_response,
    make_schedule,
    score_policy,
    similarity_gap,
    run_seed,
    monte_carlo,
    POLICIES,
    VERIFY,
)


class TestClassicBenchmark(unittest.TestCase):

    def test_p_star_is_point_six(self):
        self.assertAlmostEqual(p_star(), 0.6)

    def test_aligned_type_trusts(self):
        action, eu = classic_best_response(0.85)
        self.assertEqual(action, "Trust")
        self.assertGreater(eu, VERIFY)

    def test_misaligned_type_verifies(self):
        action, eu = classic_best_response(0.25)
        self.assertEqual(action, "Verify")
        self.assertLess(eu, VERIFY)

    def test_indifference_at_p_star(self):
        eu = expected_utility_trust(p_star())
        self.assertAlmostEqual(eu, VERIFY)


class TestScheduleAndPolicies(unittest.TestCase):

    def test_schedule_has_correct_length(self):
        rounds = make_schedule(seed=206, n_rounds=12)
        self.assertEqual(len(rounds), 12)

    def test_schedule_is_balanced(self):
        rounds = make_schedule(seed=206, n_rounds=12)
        aligned_count = sum(1 for r in rounds if r["type"] == "aligned")
        same_count = sum(1 for r in rounds if r["profile"] == "SAME")
        self.assertEqual(aligned_count, 6)
        self.assertEqual(same_count, 6)

    def test_same_seed_is_reproducible(self):
        r1 = make_schedule(seed=206)
        r2 = make_schedule(seed=206)
        self.assertEqual(r1, r2)

    def test_all_policies_produce_a_score(self):
        rounds = make_schedule(seed=206)
        for p in POLICIES:
            score = score_policy(rounds, p)
            self.assertIsInstance(score, int)

    def test_always_verify_score_is_fixed(self):
        # always_verify never depends on the random draws: 12 rounds * 2 = 24
        rounds = make_schedule(seed=206)
        self.assertEqual(score_policy(rounds, "always_verify"), 24)


class TestSimilarityGap(unittest.TestCase):

    def test_gap_is_between_zero_and_one(self):
        rounds = make_schedule(seed=206)
        gap = similarity_gap(rounds)
        self.assertGreaterEqual(gap, 0.0)
        self.assertLessEqual(gap, 1.0)

    def test_gap_is_near_half_on_average(self):
        # Over many seeds, similarity should carry ~no information
        # about the true type by construction.
        means, mean_gap, _ = monte_carlo(n_seeds=500)
        self.assertAlmostEqual(mean_gap, 0.5, delta=0.05)


class TestBenchmarkBeatsSimilarity(unittest.TestCase):

    def test_benchmark_outperforms_similarity_on_average(self):
        means, _, _ = monte_carlo(n_seeds=500)
        self.assertGreater(means["benchmark"], means["similarity"])

    def test_similarity_often_loses_to_always_verify(self):
        _, _, share_below = monte_carlo(n_seeds=500)
        # Majority of seeds should show similarity underperforming
        # always_verify, matching the qualitative claim in the paper.
        self.assertGreater(share_below, 0.5)


if __name__ == "__main__":
    unittest.main()
