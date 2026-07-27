import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from validate_mof_worked_example import *
class T(unittest.TestCase):
 def setUp(self): self.x=load_json(ROOT/'synthetic_uio66_research_object.json')
 def test_ok(self): self.assertEqual(validate_instance(copy.deepcopy(self.x),ROOT)['schema'],'PASS')
 def test_self(self):
  x=copy.deepcopy(self.x); x['validation']['verifier_id']=x['validation']['contributor_id']
  with self.assertRaises(ValidationPolicyError): validate_instance(x,ROOT)
 def test_hash(self):
  x=copy.deepcopy(self.x); x['characterisation_evidence'][0]['sha256']='0'*64
  with self.assertRaises(ValidationPolicyError): validate_instance(x,ROOT)
 def test_resolved(self):
  x=copy.deepcopy(self.x); x['validation']['source_link_status']='source_link_resolved'
  with self.assertRaises(ValidationPolicyError): validate_instance(x,ROOT)
 def test_conflict(self):
  x=copy.deepcopy(self.x); x['validation']['conflict_declaration']={'declared':False,'details':'synthetic'}
  with self.assertRaises(ValidationPolicyError): validate_instance(x,ROOT)
if __name__=='__main__': unittest.main()
