import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).parents[1]


class WorkedExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "mof_research_object_profile.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.instance = json.loads(
            (ROOT / "synthetic_uio66_research_object.json").read_text(
                encoding="utf-8"
            )
        )

    def test_schema(self):
        jsonschema.Draft202012Validator(self.schema).validate(self.instance)

    def test_synthetic_boundary(self):
        self.assertTrue(self.instance["synthetic_example"])
        self.assertEqual(self.instance["profile_version"], "0.3.4-alpha")
        self.assertEqual(
            self.instance["validation"]["scientific_assessment"]["status"],
            "not_reviewed",
        )

    def test_evidence_inventory(self):
        evidence = sorted(path.name for path in (ROOT / "evidence").iterdir())
        self.assertEqual(
            evidence, ["example_pxrd_pattern.xy", "example_synthesis_log.txt"]
        )


if __name__ == "__main__":
    unittest.main()
