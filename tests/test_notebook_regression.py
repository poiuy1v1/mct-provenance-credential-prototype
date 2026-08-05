import copy
import json
import unittest
from pathlib import Path

from scripts.compare_notebook_semantics import (
    NotebookRegressionError,
    load_notebook,
    validate_notebooks,
)


ROOT = Path(__file__).parents[1]
SOURCE_PATH = ROOT / "verification_workflow_demo.ipynb"
EXECUTED_PATH = ROOT / "outputs" / "verification_workflow_demo_executed.ipynb"


def parsed_output(cell):
    text = cell["outputs"][0]["text"]
    return json.loads("".join(text) if isinstance(text, list) else text)


class NotebookRegressionTests(unittest.TestCase):
    def setUp(self):
        self.source = load_notebook(SOURCE_PATH)
        self.executed = load_notebook(EXECUTED_PATH)

    def assert_rejected(self, notebook):
        with self.assertRaises(NotebookRegressionError):
            validate_notebooks(self.source, notebook)

    def test_committed_executed_snapshot_passes(self):
        validate_notebooks(self.source, self.executed)
        self.assertNotEqual(SOURCE_PATH.read_bytes(), EXECUTED_PATH.read_bytes())

    def test_copied_unexecuted_notebook_fails(self):
        self.assert_rejected(copy.deepcopy(self.source))

    def test_null_execution_count_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        code_cells[0]["execution_count"] = None
        self.assert_rejected(changed)

    def test_out_of_order_execution_count_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        code_cells[1]["execution_count"] = 3
        self.assert_rejected(changed)

    def test_boolean_execution_count_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        code_cells[0]["execution_count"] = True
        self.assert_rejected(changed)

    def test_cleared_mandatory_output_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        code_cells[1]["outputs"] = []
        self.assert_rejected(changed)

    def test_changed_deterministic_score_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[1])
        value["diagnostic_score_sum"] = 26.2855
        code_cells[1]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_changed_deterministic_row_count_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[2])
        value["verification_row_count"] = 5
        code_cells[2]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_changed_summary_row_count_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[1])
        value["row_count"] = 5
        code_cells[1]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_error_output_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        code_cells[0]["outputs"].append(
            {
                "ename": "RuntimeError",
                "evalue": "synthetic failure",
                "output_type": "error",
                "traceback": ["RuntimeError: synthetic failure"],
            }
        )
        self.assert_rejected(changed)

    def test_private_absolute_path_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[2])
        value["debug_path"] = "C:" + "\\Users\\example\\secret.txt"
        code_cells[2]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_posix_private_absolute_path_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[2])
        value["debug_path"] = "/home/example/private/example_contributions.json"
        code_cells[2]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_host_temporary_path_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[2])
        value["debug_path"] = "/tmp/paper1-notebook/runtime.json"
        code_cells[2]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_stale_validation_vocabulary_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[2])
        value["observed_validation_states"]["scientific_assessment_status"] = [
            "NOT_ESTABLISHED" + "_BY_FROZEN_SNAPSHOT"
        ]
        code_cells[2]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)

    def test_secret_token_fails(self):
        changed = copy.deepcopy(self.executed)
        code_cells = [cell for cell in changed["cells"] if cell["cell_type"] == "code"]
        value = parsed_output(code_cells[2])
        value["credential"] = "ghp_" + "1" * 30
        code_cells[2]["outputs"][0]["text"] = json.dumps(value, sort_keys=True) + "\n"
        self.assert_rejected(changed)


if __name__ == "__main__":
    unittest.main()
