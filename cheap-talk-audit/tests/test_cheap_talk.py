import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cheap_talk import (  # noqa: E402
    INDIFFERENCE_P,
    expected_trust,
    evaluate_seed,
    indifference_check,
)


class TestCheapTalk(unittest.TestCase):
    def test_seed206_matches_deployed_space(self):
        ev = evaluate_seed(206)
        self.assertEqual(ev["benchmark"]["total"], 48)
        self.assertEqual(ev["always_verify"]["total"], 24)
        self.assertEqual(ev["always_trust"]["total"], 22)
        self.assertEqual(ev["similarity"]["total"], 18)
        self.assertEqual(ev["benchmark"]["gap_overall"], "4/11")
        self.assertEqual(ev["benchmark"]["gap_aligned"], "0/6")
        self.assertEqual(ev["benchmark"]["gap_misaligned"], "4/5")
        self.assertEqual(ev["benchmark"]["similarity_bias_pp"], 0)
        self.assertEqual(ev["similarity"]["similarity_bias_pp"], 100)
        self.assertEqual(ev["benchmark"]["benchmark_match"], 12)

    def test_indifference_threshold(self):
        self.assertAlmostEqual(INDIFFERENCE_P, 0.6)
        self.assertAlmostEqual(expected_trust(0.6), 2.0)
        self.assertTrue(indifference_check()["modified_aligned_equals_verify"])


if __name__ == "__main__":
    unittest.main()
