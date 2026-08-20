import copy
import hashlib
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

from validate_mof_worked_example import (  # noqa: E402
    ValidationPolicyError,
    load_json,
    validate_instance,
)


class WorkedExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile_schema = load_json(
            ROOT / "mof_research_object_profile.schema.json"
        )
        cls.instance = load_json(ROOT / "synthetic_uio66_research_object.json")
        cls.contribution_schema = load_json(REPO_ROOT / "contribution_schema.json")
        cls.events = load_json(REPO_ROOT / "data" / "example_contributions.json")

        def retrieve(uri):
            if uri == "MOF_WorkedExample/mof_research_object_profile.schema.json":
                return Resource.from_contents(cls.profile_schema)
            raise LookupError(f"offline schema resource not found: {uri}")

        cls.contribution_validator = Draft202012Validator(
            cls.contribution_schema,
            registry=Registry(retrieve=retrieve),
            format_checker=FormatChecker(),
        )

    def test_worked_example_passes_bounded_offline_policy(self):
        result = validate_instance(copy.deepcopy(self.instance), ROOT)
        self.assertEqual(result["schema"], "PASS")
        self.assertEqual(result["source_link_offline_policy"], "PASS")
        self.assertEqual(result["scientific_boundary"], "PASS")

    def test_schemas_are_valid_draft202012(self):
        Draft202012Validator.check_schema(self.profile_schema)
        Draft202012Validator.check_schema(self.contribution_schema)

    def test_canonical_six_event_dataset_validates(self):
        self.contribution_validator.validate(copy.deepcopy(self.events))
        self.assertEqual(
            [event["event_id"] for event in self.events],
            [f"MCT-EVT-{number:04d}" for number in range(1, 7)],
        )

    def test_generic_branch_validates(self):
        self.contribution_validator.validate([copy.deepcopy(self.events[1])])

    def test_mof_branch_and_relative_ref_validate_offline(self):
        self.contribution_validator.validate([copy.deepcopy(self.events[0])])

    def test_inline_profile_equals_standalone_as_parsed_json(self):
        self.assertEqual(
            self.events[0]["research_object"]["domain_profile"],
            self.instance,
        )

    def test_evidence_paths_and_hashes_match_at_both_levels(self):
        expected = {
            "MOF_WorkedExample/" + evidence["file"]: evidence["sha256"]
            for evidence in self.instance["characterisation_evidence"]
        }
        event_files = {
            evidence["path"]: evidence["sha256"]
            for evidence in self.events[0]["evidence"]["files"]
        }
        self.assertEqual(event_files, expected)
        for relative_path, expected_hash in expected.items():
            actual_hash = hashlib.sha256(
                (REPO_ROOT / relative_path).read_bytes()
            ).hexdigest()
            self.assertEqual(actual_hash, expected_hash)

    def test_missing_evidence_file_rejected(self):
        instance = copy.deepcopy(self.instance)
        instance["characterisation_evidence"][0]["file"] = (
            "evidence/missing_pxrd_pattern.xy"
        )
        with self.assertRaisesRegex(ValidationPolicyError, "missing evidence file"):
            validate_instance(instance, ROOT)

    def test_hash_mismatch_rejected(self):
        instance = copy.deepcopy(self.instance)
        instance["characterisation_evidence"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValidationPolicyError, "hash mismatch"):
            validate_instance(instance, ROOT)

    def test_duplicate_evidence_path_rejected(self):
        instance = copy.deepcopy(self.instance)
        instance["characterisation_evidence"][1]["file"] = instance[
            "characterisation_evidence"
        ][0]["file"]
        with self.assertRaisesRegex(ValidationPolicyError, "duplicate evidence file"):
            validate_instance(instance, ROOT)

    def test_duplicate_evidence_hash_rejected(self):
        instance = copy.deepcopy(self.instance)
        instance["characterisation_evidence"][1]["sha256"] = instance[
            "characterisation_evidence"
        ][0]["sha256"]
        with self.assertRaisesRegex(ValidationPolicyError, "duplicate evidence hash"):
            validate_instance(instance, ROOT)

    def test_source_link_recorded_allowed_but_resolved_rejected_offline(self):
        self.assertEqual(
            self.instance["validation"]["source_link_status"],
            "source_link_recorded",
        )
        validate_instance(copy.deepcopy(self.instance), ROOT)
        instance = copy.deepcopy(self.instance)
        instance["validation"]["source_link_status"] = "source_link_resolved"
        with self.assertRaisesRegex(ValidationPolicyError, "cannot claim.*resolution"):
            validate_instance(instance, ROOT)

    def test_evidence_source_resolution_rejected_offline(self):
        instance = copy.deepcopy(self.instance)
        instance["characterisation_evidence"][0][
            "source_link_status"
        ] = "source_link_resolved"
        with self.assertRaisesRegex(ValidationPolicyError, "cannot claim.*resolution"):
            validate_instance(instance, ROOT)

    def test_same_contributor_and_verifier_rejected_by_project_policy(self):
        instance = copy.deepcopy(self.instance)
        instance["validation"]["verifier_id"] = instance["validation"][
            "contributor_id"
        ]
        with self.assertRaisesRegex(ValidationPolicyError, "project policy"):
            validate_instance(instance, ROOT)

    def test_scientific_assessment_is_independent_of_file_check_states(self):
        instance = copy.deepcopy(self.instance)
        instance["validation"]["evidence_file_status"] = "not_checked"
        instance["validation"]["file_integrity_status"] = "not_checked"
        for evidence in instance["characterisation_evidence"]:
            evidence["file_status"] = "not_checked"
            evidence["integrity_status"] = "not_checked"
        result = validate_instance(instance, ROOT)
        self.assertEqual(
            instance["validation"]["scientific_assessment"]["status"],
            "not_reviewed",
        )
        self.assertEqual(result["scientific_boundary"], "PASS")

    def test_scientific_review_claim_rejected_for_synthetic_example(self):
        instance = copy.deepcopy(self.instance)
        instance["validation"]["scientific_assessment"][
            "status"
        ] = "scientifically_reviewed"
        with self.assertRaisesRegex(ValidationPolicyError, "scientifically not_reviewed"):
            validate_instance(instance, ROOT)

    def test_stale_profile_version_rejected(self):
        instance = copy.deepcopy(self.instance)
        instance["profile_version"] = "0.3.4-alpha"
        with self.assertRaises(ValidationError):
            validate_instance(instance, ROOT)

    def test_stale_profile_schema_vocabulary_rejected(self):
        instance = copy.deepcopy(self.instance)
        instance["$schema"] = "mof_research_object_profile-v0.3.4-alpha.schema.json"
        with self.assertRaises(ValidationError):
            validate_instance(instance, ROOT)

    def test_stale_contribution_version_rejected(self):
        event = copy.deepcopy(self.events[1])
        event["schema_version"] = "0.3.4-alpha"
        with self.assertRaises(ValidationError):
            self.contribution_validator.validate([event])

    def test_stable_repository_root_and_relative_path_conventions(self):
        self.assertEqual(
            self.instance["source_anchoring"]["repository_url"],
            "https://github.com/poiuy1v1/mct-provenance-credential-prototype",
        )
        self.assertTrue(
            all(
                evidence["file"].startswith("evidence/")
                for evidence in self.instance["characterisation_evidence"]
            )
        )
        self.assertTrue(
            all(
                evidence["path"].startswith("MOF_WorkedExample/evidence/")
                for evidence in self.events[0]["evidence"]["files"]
            )
        )


if __name__ == "__main__":
    unittest.main()
