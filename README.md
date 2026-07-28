# MOF contribution-credential prototype for AI-ready MOF data

Release: `v0.3.3-alpha`  
Publication date: `2026-07-28`  
Version-specific Zenodo DOI: [`10.5281/zenodo.21643012`](https://doi.org/10.5281/zenodo.21643012)

This synthetic, non-financial companion implements a modular contribution-event schema, an inline MOF domain profile, layered validation states, an executable notebook, deterministic validators and diagnostic event scoring. A blockchain is not required.

## Run the complete validation

```bash
python3 -m pip install -r requirements.txt
bash scripts/run_smoke_tests.sh
```

The smoke test validates both JSON Schemas, rejects self-verification, checks the worked-example hashes, executes the notebook, regenerates outputs and scans for stale validation vocabulary.

## Interpretation boundary

- `file_integrity_confirmed` means that committed bytes match a recorded SHA-256 hash.
- `source_link_recorded` means a URL is recorded; it does not mean the URL was resolved.
- `scientific_assessment.status = not_reviewed` means no domain-expert review is claimed.
- `diagnostic_event_score` is a synthetic software-test output, not a researcher ranking or allocation metric.

## Identifier boundary

ORCID-like strings are checked only for canonical format and ISO/IEC 7064 MOD 11-2 checksum. No live ORCID or DOI registry lookup is made.

## Archived versions

- Current release: `v0.3.3-alpha`, DOI [`10.5281/zenodo.21643012`](https://doi.org/10.5281/zenodo.21643012), published 28 July 2026.
- Historical release: `v0.3.2-alpha`, DOI [`10.5281/zenodo.20324761`](https://doi.org/10.5281/zenodo.20324761).
