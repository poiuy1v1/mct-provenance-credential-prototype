#!/usr/bin/env python3
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).parent
schema = json.loads(
    (ROOT / "mof_research_object_profile.schema.json").read_text(encoding="utf-8")
)
instance = json.loads(
    (ROOT / "synthetic_uio66_research_object.json").read_text(encoding="utf-8")
)
jsonschema.Draft202012Validator(schema).validate(instance)
assert instance["synthetic_example"] is True
assert instance["profile_version"] == "0.3.4-alpha"
assert instance["validation"]["scientific_assessment"]["status"] == "not_reviewed"
print("PASS: synthetic v0.3.4-alpha worked example")
