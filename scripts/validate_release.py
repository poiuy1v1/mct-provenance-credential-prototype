#!/usr/bin/env python3
"""Validate the complete v0.3.3-alpha release candidate offline."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker, RefResolver

ROOT = Path(__file__).resolve().parents[1]
MOF_DIR = ROOT / "MOF_WorkedExample"
ORCID_RE = re.compile(r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$')
DOI_RE = re.compile(r'^10\.[^\s/]+/.+')

def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))

def orcid_checksum_valid(value: str) -> bool:
    if not ORCID_RE.fullmatch(value): return False
    compact=value.replace('-',''); total=0
    for char in compact[:15]: total=(total+int(char))*2
    result=(12-total%11)%11; expected='X' if result==10 else str(result)
    return compact[-1]==expected

def build_validator():
    contribution_schema=load(ROOT/'contribution_schema.json')
    mof_schema=load(MOF_DIR/'mof_research_object_profile.schema.json')
    base=(ROOT/'contribution_schema.json').resolve().as_uri()
    mof_uri=(MOF_DIR/'mof_research_object_profile.schema.json').resolve().as_uri()
    resolver=RefResolver(base_uri=base, referrer=contribution_schema, store={mof_uri:mof_schema})
    return Draft202012Validator(contribution_schema, resolver=resolver, format_checker=FormatChecker())

def validate_evidence(event):
    v=event['validation']; files=event['evidence'].get('files',[])
    claims_local=(v['evidence_file_status']=='evidence_file_present' or v['file_integrity_status']=='file_integrity_confirmed')
    if claims_local and not files:
        raise ValueError(f"{event['event_id']} claims local evidence without evidence.files")
    for item in files:
        path=ROOT/item['path']
        if not path.is_file(): raise ValueError(f"Missing evidence file for {event['event_id']}: {item['path']}")
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=item['sha256']: raise ValueError(f"Evidence hash mismatch for {event['event_id']}: {item['path']}")
    if not files and v['file_integrity_status']=='file_integrity_confirmed':
        raise ValueError(f"{event['event_id']} confirms integrity without packaged bytes")

def validate_release():
    validator=build_validator(); events=load(ROOT/'data/example_contributions.json'); worked=load(MOF_DIR/'synthetic_uio66_research_object.json')
    seen_events=set(); seen_credentials=set()
    for event in events:
        validator.validate(event)
        if event['event_id'] in seen_events: raise ValueError(f"Duplicate event_id: {event['event_id']}")
        seen_events.add(event['event_id'])
        cid=event['issued_credential']['credential_id']
        if cid in seen_credentials: raise ValueError(f"Duplicate credential_id: {cid}")
        seen_credentials.add(cid)
        oid=event['contributor']['orcid']
        if not orcid_checksum_valid(oid): raise ValueError(f"Invalid ORCID checksum: {oid}")
        if event['contributor']['orcid_validation_scope']!='format_and_checksum_only': raise ValueError('ORCID scope overclaim')
        doi=event['research_object'].get('doi','')
        if doi and not DOI_RE.fullmatch(doi): raise ValueError(f"Invalid DOI format: {doi}")
        v=event['validation']
        if v['scientific_assessment']['status']!='not_reviewed': raise ValueError(f"Synthetic event {event['event_id']} overclaims scientific review")
        verifier=v['verifier']
        if verifier['type']=='person':
            if verifier['identifier_scheme']!='orcid_format_only' or not orcid_checksum_valid(verifier['identifier']): raise ValueError(f"Invalid verifier ORCID-format identifier: {event['event_id']}")
            if verifier['identifier']==oid: raise ValueError(f"Self-verification detected: {event['event_id']}")
        if v['source_link_status']=='source_link_resolved': raise ValueError(f"Offline release cannot claim remote source resolution: {event['event_id']}")
        validate_evidence(event)
    if events[0]['research_object'].get('domain_profile')!=worked: raise ValueError('Inline MOF domain_profile is not identical to standalone worked example')
    result=subprocess.run([sys.executable,str(MOF_DIR/'validate_mof_worked_example.py'),'--json'],cwd=MOF_DIR,capture_output=True,text=True,check=True)
    return {
      'contribution_events':len(events),'contribution_schema':'PASS','portable_relative_mof_schema_ref':'PASS',
      'inline_standalone_profile_identity':'PASS','orcid_format_and_checksum_policy':'PASS','doi_format_policy':'PASS',
      'self_verification_policy':'PASS','packaged_evidence_grounding':'PASS','offline_source_link_policy':'PASS',
      'synthetic_scientific_boundary':'PASS','mof_worked_example':json.loads(result.stdout)}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--json',action='store_true'); a=p.parse_args(); r=validate_release()
    print(json.dumps(r,indent=2) if a.json else 'PASS: complete v0.3.3-alpha release validation'); return 0
if __name__=='__main__': raise SystemExit(main())
