import copy, json, unittest
from pathlib import Path
from jsonschema import ValidationError
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_release import build_validator, load, orcid_checksum_valid, validate_evidence

class ReleaseSchemaTests(unittest.TestCase):
    def setUp(self): self.validator=build_validator(); self.events=load(ROOT/'data/example_contributions.json')
    def test_all_events_validate(self):
        for event in self.events: self.validator.validate(event)
    def test_generic_and_mof_oneof_paths(self):
        self.validator.validate(self.events[1]); self.validator.validate(self.events[0]); self.assertIn('domain_profile',self.events[0]['research_object'])
    def test_missing_validation_field_fails(self):
        event=copy.deepcopy(self.events[0]); del event['validation']['file_integrity_status']
        with self.assertRaises(ValidationError): self.validator.validate(event)
    def test_orcid_checksums(self):
        for event in self.events:
            self.assertTrue(orcid_checksum_valid(event['contributor']['orcid']))
            v=event['validation']['verifier']
            if v['type']=='person': self.assertTrue(orcid_checksum_valid(v['identifier']))
    def test_confirmed_evidence_requires_real_file_and_hash(self):
        validate_evidence(self.events[0])
        bad=copy.deepcopy(self.events[1]); bad['validation']['evidence_file_status']='evidence_file_present'; bad['validation']['file_integrity_status']='file_integrity_confirmed'
        with self.assertRaises(ValueError): validate_evidence(bad)
    def test_relative_ref_not_future_tag_url(self):
        schema=load(ROOT/'contribution_schema.json'); ref=schema['$defs']['mofResearchObject']['properties']['domain_profile']['$ref']
        self.assertEqual(ref,'MOF_WorkedExample/mof_research_object_profile.schema.json')
if __name__=='__main__': unittest.main()
