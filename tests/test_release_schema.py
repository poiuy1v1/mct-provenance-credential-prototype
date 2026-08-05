import json
import re
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).parents[1]


class ReleaseSchemaAndPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = json.loads(
            (ROOT / "data" / "example_contributions.json").read_text(
                encoding="utf-8"
            )
        )
        cls.schema = json.loads(
            (ROOT / "contribution_schema.json").read_text(encoding="utf-8")
        )

    def test_contribution_schema(self):
        jsonschema.Draft202012Validator(self.schema).validate(self.events)

    def test_candidate_version(self):
        self.assertEqual(len(self.events), 6)
        self.assertTrue(
            all(event["schema_version"] == "0.3.4-alpha" for event in self.events)
        )

    def test_synthetic_nontransferable_boundary(self):
        self.assertTrue(
            all(event["issued_credential"]["non_transferable"] for event in self.events)
        )
        self.assertTrue(all(event["issued_credential"]["locked"] for event in self.events))
        self.assertTrue(
            all(
                event["validation"]["scientific_assessment"]["status"]
                == "not_reviewed"
                for event in self.events
            )
        )

    def test_no_self_verification(self):
        for event in self.events:
            self.assertNotEqual(
                event["contributor"]["orcid"],
                event["validation"]["verifier"]["identifier"],
            )

    def test_release_metadata_has_no_prefilled_doi_or_date(self):
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn('version: "0.3.4-alpha"', citation)
        self.assertNotRegex(citation, re.compile(r"(?m)^doi:"))
        self.assertNotRegex(citation, re.compile(r"(?m)^date-released:"))
        zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
        self.assertEqual(zenodo["version"], "0.3.4-alpha")
        self.assertNotIn("doi", zenodo)
        self.assertNotIn("publication_date", zenodo)

    def test_release_facing_metadata_has_no_candidate_language(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        notes = (ROOT / "RELEASE_NOTES_v0.3.4-alpha.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Current software version: **`v0.3.4-alpha`**.",
            readme,
        )
        self.assertTrue(notes.startswith("# v0.3.4-alpha\n"))
        for marker in (
            "local unpublished",
            "has not been pushed, tagged, released, or archived",
            "Unpublished draft",
        ):
            self.assertNotIn(marker, readme)
            self.assertNotIn(marker, notes)


if __name__ == "__main__":
    unittest.main()
