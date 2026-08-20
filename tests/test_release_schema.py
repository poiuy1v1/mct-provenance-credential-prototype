import copy
import json
import re
import unittest
from pathlib import Path

from jsonschema import ValidationError

from scripts.validate_release import (
    CANONICAL_EVENT_IDS,
    CANDIDATE_VERSION,
    build_contribution_validator,
    check_metadata,
    load_json,
    validate_event_policy,
)


ROOT = Path(__file__).parents[1]


class ReleaseSchemaAndPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = load_json("data/example_contributions.json")
        cls.schema = load_json("contribution_schema.json")
        cls.profile = load_json(
            "MOF_WorkedExample/synthetic_uio66_research_object.json"
        )
        cls.validator = build_contribution_validator()

    def test_top_level_array_schema_and_all_events_validate(self):
        self.assertEqual(self.schema["type"], "array")
        self.validator.validate(self.events)

    def test_generic_and_mof_oneof_paths_validate_offline(self):
        self.validator.validate([self.events[0]])
        self.validator.validate([self.events[1]])
        self.assertIn("domain_profile", self.events[0]["research_object"])
        self.assertNotIn("domain_profile", self.events[1]["research_object"])
        reference = self.schema["$defs"]["mofResearchObject"]["properties"][
            "domain_profile"
        ]["$ref"]
        self.assertEqual(
            reference,
            "MOF_WorkedExample/mof_research_object_profile.schema.json",
        )

    def test_inline_and_standalone_profiles_are_json_value_identical(self):
        self.assertEqual(
            self.events[0]["research_object"]["domain_profile"],
            self.profile,
        )

    def test_candidate_version_and_canonical_order(self):
        self.assertEqual(len(self.events), 6)
        self.assertEqual(
            [event["event_id"] for event in self.events],
            CANONICAL_EVENT_IDS,
        )
        self.assertTrue(
            all(
                event["schema_version"] == CANDIDATE_VERSION
                for event in self.events
            )
        )

    def test_stale_event_version_is_rejected(self):
        event = copy.deepcopy(self.events[1])
        event["schema_version"] = "0.3.4-alpha"
        with self.assertRaises(ValidationError):
            self.validator.validate([event])

    def test_missing_evidence_file_is_rejected_when_presence_is_claimed(self):
        event = copy.deepcopy(self.events[0])
        event["evidence"]["files"][0]["path"] = (
            "MOF_WorkedExample/evidence/missing.xy"
        )
        with self.assertRaisesRegex(ValueError, "Missing evidence file"):
            validate_event_policy(event)

    def test_evidence_hash_mismatch_is_rejected_when_integrity_is_claimed(self):
        event = copy.deepcopy(self.events[0])
        event["evidence"]["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Evidence hash mismatch"):
            validate_event_policy(event)

    def test_offline_source_resolution_claim_is_rejected(self):
        event = copy.deepcopy(self.events[1])
        event["validation"]["source_link_status"] = "source_link_resolved"
        with self.assertRaisesRegex(ValueError, "cannot claim source resolution"):
            validate_event_policy(event)

    def test_file_integrity_does_not_change_scientific_assessment(self):
        event = copy.deepcopy(self.events[0])
        result = validate_event_policy(event)
        self.assertGreater(result["evidence_hashes_checked"], 0)
        self.assertFalse(result["file_integrity_is_scientific_review"])
        self.assertEqual(
            event["validation"]["scientific_assessment"]["status"],
            "not_reviewed",
        )

    def test_synthetic_nontransferable_boundary(self):
        self.assertTrue(
            all(event["issued_credential"]["non_transferable"] for event in self.events)
        )
        self.assertTrue(
            all(event["issued_credential"]["locked"] for event in self.events)
        )
        self.assertTrue(
            all(
                event["validation"]["scientific_assessment"]["status"]
                == "not_reviewed"
                for event in self.events
            )
        )

    def test_release_metadata_is_local_candidate_without_invented_doi_or_date(self):
        result = check_metadata()
        self.assertEqual(result["metadata_state"], "LOCAL_CANDIDATE_ONLY")
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn('version: "0.3.5-alpha"', citation)
        self.assertNotRegex(citation, re.compile(r"(?m)^doi:"))
        self.assertNotRegex(citation, re.compile(r"(?m)^date-released:"))
        zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
        self.assertEqual(zenodo["version"], "0.3.5-alpha")
        self.assertNotIn("doi", zenodo)
        self.assertNotIn("publication_date", zenodo)


if __name__ == "__main__":
    unittest.main()
