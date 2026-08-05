import itertools
import unittest
from pathlib import Path

import mct_reward_simulation as scoring


ROOT = Path(__file__).parents[1]
INPUT_PATH = ROOT / "data" / "example_contributions.json"


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = scoring.load_events("data/example_contributions.json", ROOT)

    def test_authoritative_rows_and_aggregate(self):
        rows = scoring.score_events(self.events)
        self.assertEqual(
            [row["event_id"] for row in rows],
            [f"MCT-EVT-{index:04d}" for index in range(1, 7)],
        )
        self.assertEqual(
            [row["diagnostic_event_score"] for row in rows],
            [6.9382, 3.9481, 6.6150, 1.5279, 3.3479, 0.6553],
        )
        run_summary = scoring.summary(rows, "data/example_contributions.json", 365.0)
        self.assertEqual(run_summary["diagnostic_score_sum"], 23.0324)
        self.assertEqual(run_summary["num_events"], 6)

    def test_all_input_permutations_are_order_invariant(self):
        totals = {
            scoring.summary(
                scoring.score_events(permutation),
                "data/example_contributions.json",
                365.0,
            )["diagnostic_score_sum"]
            for permutation in itertools.permutations(self.events)
        }
        self.assertEqual(totals, {23.0324})

    def test_quality_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(scoring.QUALITY_WEIGHTS.values()), 1.0)

    def test_absolute_in_root_input_path_is_rejected(self):
        rows = scoring.score_events(self.events)
        with self.assertRaises(ValueError):
            scoring.summary(rows, INPUT_PATH.resolve(), 365.0)

    def test_absolute_outside_root_input_path_is_rejected(self):
        rows = scoring.score_events(self.events)
        with self.assertRaises(ValueError):
            scoring.summary(
                rows,
                "C:" + "/Users/example/private/example_contributions.json",
                365.0,
            )

    def test_boundary_language_is_preserved(self):
        self.assertIn("not prices", scoring.DISCLAIMER)
        self.assertIn("not", scoring.DISCLAIMER)
        self.assertNotIn("leaderboard", scoring.summary(
            scoring.score_events(self.events),
            "data/example_contributions.json",
            365.0,
        ))

    def test_invalid_half_life_fails(self):
        with self.assertRaises(ValueError):
            scoring.score_events(self.events, 0.0)


if __name__ == "__main__":
    unittest.main()
