import tempfile
import unittest
from pathlib import Path

from scripts.check_release_neutrality import (
    ReleaseNeutralityError,
    validate_public_release_tree,
)


ROOT = Path(__file__).parents[1]


class PublicReleaseNeutralityTests(unittest.TestCase):
    def test_current_candidate_passes(self):
        result = validate_public_release_tree(ROOT)
        self.assertEqual(result["overall_status"], "PASS")
        self.assertEqual(result["forbidden_artifacts"], 0)

    def test_audit_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "audit").mkdir()
            (root / "audit" / "log.txt").write_text("visible log\n", encoding="utf-8")
            with self.assertRaisesRegex(ReleaseNeutralityError, "forbidden-directory"):
                validate_public_release_tree(root)

    def test_conversation_filename_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VISIBLE_CONVERSATION_LOG.txt").write_text("log\n", encoding="utf-8")
            with self.assertRaisesRegex(ReleaseNeutralityError, "forbidden-filename"):
                validate_public_release_tree(root)

    def test_internal_prompt_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "notes.md").write_text(
                "COMPLETE USER-VISIBLE TASK PROMPT\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ReleaseNeutralityError, "internal-content"):
                validate_public_release_tree(root)

    def test_internal_gate_result_filename_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "01_EXECUTIVE_STATUS.md").write_text("status\n", encoding="utf-8")
            with self.assertRaisesRegex(ReleaseNeutralityError, "forbidden-filename"):
                validate_public_release_tree(root)

    def test_normal_release_documentation_is_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "history").mkdir()
            (root / "README.md").write_text("Public software documentation.\n", encoding="utf-8")
            (root / "history" / "v0.3.4-alpha_RELEASE_FINALIZATION.md").write_text(
                "Historical and superseded.\n", encoding="utf-8"
            )
            result = validate_public_release_tree(root)
            self.assertEqual(result["overall_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
