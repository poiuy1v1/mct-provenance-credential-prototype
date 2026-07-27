#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from urllib.parse import urlparse
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parent
ID_RE=re.compile(r"^(did:[a-z0-9]+:[A-Za-z0-9._:%-]+|https://orcid.org/\d{4}-\d{4}-\d{4}-\d{3}[0-9X])$")
class ValidationPolicyError(ValueError): pass
def load_json(p): return json.loads(Path(p).read_text())
def validate_instance(x,root=ROOT,allow_network_resolved=False):
    Draft202012Validator(load_json(root/'mof_research_object_profile.schema.json'),format_checker=FormatChecker()).validate(x)
    v=x['validation']
    if not ID_RE.fullmatch(v['contributor_id']) or not ID_RE.fullmatch(v['verifier_id']): raise ValidationPolicyError('invalid contributor/verifier identifier')
    if v['contributor_id']==v['verifier_id']: raise ValidationPolicyError('self-verification is not allowed')
    if not v['independent_verifier']: raise ValidationPolicyError('independent_verifier must be true')
    c=v['conflict_declaration']
    if not c['declared'] and not re.search(r'\b(no|none|not)\b',c['details'],re.I): raise ValidationPolicyError('explicit no-conflict wording required')
    u=urlparse(x['source_anchoring']['repository_url'])
    if u.scheme!='https' or not u.netloc: raise ValidationPolicyError('repository_url must be absolute HTTPS')
    if v['source_link_status']=='source_link_resolved' and not allow_network_resolved: raise ValidationPolicyError('offline validator cannot claim source resolution')
    files=[]; hashes=[]
    for e in x['characterisation_evidence']:
        if e['file'] in files: raise ValidationPolicyError('duplicate evidence file path')
        if e['sha256'] in hashes: raise ValidationPolicyError('duplicate evidence hash')
        files.append(e['file']); hashes.append(e['sha256'])
        p=root/e['file']
        if e['file_status']=='evidence_file_present' and not p.exists(): raise ValidationPolicyError(f'missing evidence file: {p}')
        if p.exists() and e['integrity_status']=='file_integrity_confirmed' and hashlib.sha256(p.read_bytes()).hexdigest()!=e['sha256']: raise ValidationPolicyError(f'hash mismatch: {p}')
        if e['source_link_status']=='source_link_resolved' and not allow_network_resolved: raise ValidationPolicyError('offline validator cannot claim evidence source resolution')
    if v['scientific_assessment']['status']=='not_reviewed' and not x['reported_outcome']['state'].startswith('reported_'): raise ValidationPolicyError('unreviewed outcomes must use reported_* state')
    return {'schema':'PASS','identity':'PASS','conflict':'PASS','source_link_policy':'PASS','evidence':'PASS','hashes':'PASS','scientific_boundary':'PASS'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--instance',default='synthetic_uio66_research_object.json'); ap.add_argument('--json',action='store_true'); a=ap.parse_args(); r=validate_instance(load_json(ROOT/a.instance)); print(json.dumps(r,indent=2) if a.json else 'PASS: hardened MOF worked-example validation'); return 0
if __name__=='__main__': raise SystemExit(main())
