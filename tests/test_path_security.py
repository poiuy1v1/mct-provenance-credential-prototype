import json
import sys
import tempfile
import unittest
from pathlib import Path

import mct_reward_simulation as scoring


SCRIPTS_ROOT = Path(__file__).parents[1] / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from run_smoke_tests import scan_tree


class PortableInputPathTests(unittest.TestCase):
    def assert_rejected(self, value, root=None):
        with self.assertRaises((TypeError, ValueError)):
            scoring.stable_input_label(value, root)

    def test_unsafe_path_matrix_is_rejected_on_every_host(self):
        cases = {
            "windows_absolute_backslash": r"C:\Users\example\private\example_contributions.json",
            "windows_absolute_forward_slash": "C:/Users/example/private/example_contributions.json",
            "unc_backslash": r"\\server\share\private\example_contributions.json",
            "unc_forward_slash": "//server/share/private/example_contributions.json",
            "posix_absolute": "/home/example/private/example_contributions.json",
            "parent_traversal": "../private/example_contributions.json",
            "nested_traversal": "data/../../private/example_contributions.json",
            "mixed_separator_traversal": r"data\..\..\private\example_contributions.json",
            "windows_drive_relative": r"C:private\example_contributions.json",
            "empty": "",
            "nul": "data/example\x00_contributions.json",
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(value)

    def test_safe_forward_slash_relative_path_is_accepted(self):
        self.assertEqual(
            scoring.stable_input_label("data/example_contributions.json"),
            "data/example_contributions.json",
        )

    def test_safe_backslash_relative_path_is_normalised(self):
        self.assertEqual(
            scoring.stable_input_label(r"data\nested\example_contributions.json"),
            "data/nested/example_contributions.json",
        )

    def test_safe_nested_and_dot_relative_paths_are_accepted(self):
        self.assertEqual(
            scoring.stable_input_label("./data/nested/example_contributions.json"),
            "data/nested/example_contributions.json",
        )

    def test_existing_relative_file_inside_authorised_root_is_accepted(self):
        with tempfile.TemporaryDirectory(prefix="paper1-path-root-") as temporary:
            root = Path(temporary)
            target = root / "data" / "example.json"
            target.parent.mkdir()
            target.write_text("[]\n", encoding="utf-8")
            self.assertEqual(
                scoring.stable_input_label("data/example.json", root),
                "data/example.json",
            )
            self.assertEqual(scoring.load_events("data/example.json", root), [])

    def test_existing_symlink_escape_is_rejected_when_supported(self):
        with tempfile.TemporaryDirectory(prefix="paper1-path-root-") as root_name:
            with tempfile.TemporaryDirectory(prefix="paper1-path-outside-") as outside_name:
                root = Path(root_name)
                outside = Path(outside_name) / "private.json"
                outside.write_text(json.dumps([]), encoding="utf-8")
                link = root / "escape.json"
                try:
                    link.symlink_to(outside)
                except (NotImplementedError, OSError) as error:
                    self.skipTest(f"Host does not permit symlink creation: {error}")
                self.assert_rejected("escape.json", root)

    def test_absolute_path_inside_root_is_still_rejected(self):
        with tempfile.TemporaryDirectory(prefix="paper1-path-root-") as temporary:
            root = Path(temporary)
            target = root / "data.json"
            target.write_text("[]\n", encoding="utf-8")
            self.assert_rejected(target.resolve(), root)

    def test_rooted_windows_path_is_rejected(self):
        self.assert_rejected(r"\private\example_contributions.json")


class SmokeScanTreeTests(unittest.TestCase):
    def write_file(self, root: Path, relative: str, content: str) -> None:
        path = root / Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_git_object_directory_is_ignored(self):
        with tempfile.TemporaryDirectory(prefix="paper1-scan-tree-") as temporary:
            root = Path(temporary) / "candidate"
            root.mkdir()
            self.write_file(root, "normal.txt", "ordinary candidate content\n")
            self.write_file(
                root,
                ".git/objects/aa/object-file",
                "/" + "home/runner/private/file\n",
            )

            self.assertEqual(scan_tree(root)["private_path_scan"], "PASS")

    def test_root_git_file_is_ignored(self):
        with tempfile.TemporaryDirectory(prefix="paper1-scan-tree-") as temporary:
            root = Path(temporary) / "candidate"
            root.mkdir()
            self.write_file(
                root,
                ".git",
                "gitdir: " + "C" + ":" + "/" + "Users/example/private/worktree.git\n",
            )

            self.assertEqual(scan_tree(root)["private_path_scan"], "PASS")

    def test_real_source_private_path_still_fails(self):
        with tempfile.TemporaryDirectory(prefix="paper1-scan-tree-") as temporary:
            root = Path(temporary) / "candidate"
            root.mkdir()
            self.write_file(
                root,
                "docs/bad.txt",
                "/" + "home/example/private/data.json\n",
            )

            with self.assertRaisesRegex(RuntimeError, "Private absolute path present"):
                scan_tree(root)

    def test_real_source_windows_private_path_still_fails(self):
        with tempfile.TemporaryDirectory(prefix="paper1-scan-tree-") as temporary:
            root = Path(temporary) / "candidate"
            root.mkdir()
            self.write_file(
                root,
                "docs/bad.txt",
                "C" + ":" + "/" + "Users/example/private/data.json\n",
            )

            with self.assertRaisesRegex(RuntimeError, "Private absolute path present"):
                scan_tree(root)

    def test_real_source_secret_pattern_still_fails(self):
        with tempfile.TemporaryDirectory(prefix="paper1-scan-tree-") as temporary:
            root = Path(temporary) / "candidate"
            root.mkdir()
            self.write_file(root, "docs/bad.txt", "ghp_" + "A" * 20 + "\n")

            with self.assertRaisesRegex(RuntimeError, "Credential-like secret present"):
                scan_tree(root)

    def test_normal_source_tree_still_passes(self):
        with tempfile.TemporaryDirectory(prefix="paper1-scan-tree-") as temporary:
            root = Path(temporary) / "candidate"
            root.mkdir()
            self.write_file(root, "docs/readme.txt", "ordinary candidate content\n")
            self.write_file(root, "data/example.json", "{\"ok\": true}\n")

            self.assertEqual(
                scan_tree(root),
                {
                    "cache_scan": "PASS",
                    "private_path_scan": "PASS",
                    "secret_scan": "PASS",
                    "stale_vocabulary_scan": "PASS",
                },
            )


if __name__ == "__main__":
    unittest.main()
