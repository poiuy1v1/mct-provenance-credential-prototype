import shutil
import unittest
from pathlib import Path

from scripts.generate_outputs import (
    OUTPUT_ALLOWLIST,
    ROOT,
    clean_output_directory,
    safe_output_path,
)


class OutputPipelineTests(unittest.TestCase):
    def test_generated_output_allowlist_is_complete(self):
        self.assertEqual(
            set(OUTPUT_ALLOWLIST),
            {
                "diagnostic_event_scores.csv",
                "diagnostic_sensitivity.csv",
                "release_validation.json",
                "simulation_dry_run_stdout.json",
                "simulation_stdout.json",
                "summary.json",
                "verification_results.csv",
                "verification_workflow_demo_executed.ipynb",
            },
        )

    def test_cleaning_removes_stale_expected_and_unexpected_files(self):
        target = ROOT / "build" / "unit-output-cleaning"
        try:
            target.mkdir(parents=True, exist_ok=True)
            (target / "summary.json").write_text("stale\n", encoding="utf-8")
            (target / "unexpected.txt").write_text("stale\n", encoding="utf-8")
            cleaned = clean_output_directory(target)
            self.assertEqual(cleaned, target.resolve())
            self.assertEqual(list(cleaned.iterdir()), [])
        finally:
            if target.exists():
                shutil.rmtree(target)
            build = ROOT / "build"
            if build.exists() and not any(build.iterdir()):
                build.rmdir()

    def test_candidate_root_cannot_be_cleaned(self):
        with self.assertRaises(ValueError):
            safe_output_path(ROOT)


if __name__ == "__main__":
    unittest.main()
