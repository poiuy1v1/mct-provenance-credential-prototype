import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.generate_outputs import (
    OUTPUT_ALLOWLIST,
    ROOT,
    clean_output_directory,
    safe_output_path,
)
from scripts.validate_package import inventory


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

    def test_git_directory_is_excluded_from_package_inventory(self):
        with tempfile.TemporaryDirectory(prefix="paper1-package-inventory-") as temporary:
            target = Path(temporary) / "candidate"
            target.mkdir()
            (target / "normal.txt").write_text("normal\n", encoding="utf-8")
            git_object = target / ".git" / "objects" / "aa" / "object-file"
            git_object.parent.mkdir(parents=True)
            git_object.write_text("repository metadata\n", encoding="utf-8")
            files = inventory(target)
            self.assertIn("normal.txt", files)
            self.assertFalse(any(name == ".git" or name.startswith(".git/") for name in files))

    def test_root_git_file_is_excluded_from_package_inventory(self):
        with tempfile.TemporaryDirectory(prefix="paper1-package-inventory-") as temporary:
            target = Path(temporary) / "candidate"
            target.mkdir()
            (target / ".git").write_text(
                "gitdir: "
                + "C"
                + ":"
                + "/"
                + "Users"
                + "/example/"
                + "private/worktree.git\n",
                encoding="utf-8",
            )
            self.assertNotIn(".git", inventory(target))

    def test_normal_hidden_source_file_is_not_excluded(self):
        with tempfile.TemporaryDirectory(prefix="paper1-package-inventory-") as temporary:
            target = Path(temporary) / "candidate"
            target.mkdir()
            (target / ".zenodo.json").write_text("{}\n", encoding="utf-8")
            self.assertIn(".zenodo.json", inventory(target))

    def test_github_directory_is_not_excluded(self):
        with tempfile.TemporaryDirectory(prefix="paper1-package-inventory-") as temporary:
            target = Path(temporary) / "candidate"
            workflow = target / ".github" / "workflows" / "test.yml"
            workflow.parent.mkdir(parents=True, exist_ok=True)
            workflow.write_text("name: test\n", encoding="utf-8")
            self.assertIn(".github/workflows/test.yml", inventory(target))

    def test_forbidden_package_directory_still_fails(self):
        with tempfile.TemporaryDirectory(prefix="paper1-package-inventory-") as temporary:
            target = Path(temporary) / "candidate"
            (target / "__pycache__").mkdir(parents=True, exist_ok=True)
            with self.assertRaisesRegex(ValueError, "Forbidden package directory"):
                inventory(target)

    def test_normal_source_file_appears_in_package_inventory(self):
        with tempfile.TemporaryDirectory(prefix="paper1-package-inventory-") as temporary:
            target = Path(temporary) / "candidate"
            source = target / "docs" / "readme.txt"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("ordinary documentation\n", encoding="utf-8")
            self.assertIn("docs/readme.txt", inventory(target))


if __name__ == "__main__":
    unittest.main()
