# Reproducibility guide

Install `jsonschema` and `nbconvert` through `requirements.txt`, then run:

```bash
python3 -m pip install -r requirements.txt
bash scripts/run_smoke_tests.sh
```

The scoring script itself uses only the Python standard library. Schema validation and notebook execution additionally require the packages declared in `requirements.txt`. No network access is required. `source_link_recorded` does not mean `source_link_resolved`, and file-integrity checks do not establish scientific truth.

Regression snapshots compare regenerated CSV/JSON outputs byte-for-byte with the committed outputs; executed notebooks are compared after removal of volatile execution metadata.
