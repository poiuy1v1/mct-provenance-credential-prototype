# MOF contribution-credential prototype for AI-ready MOF data

Release candidate: `v0.3.3-alpha`  
Repository: `https://github.com/poiuy1v1/mct-provenance-credential-prototype`

This repository contains a synthetic, non-financial research-software prototype accompanying the Perspective *Provenance and contribution credentials for AI-ready MOF research*. The historical repository name and some file names retain `MCT`, but the manuscript frames the system neutrally as a MOF contribution credential. A blockchain is not required.

## v0.3.3-alpha artifact alignment

- adds a hardened MOF research-object JSON Schema;
- adds a synthetic UiO-66 worked example, evidence hashes, validator and negative tests;
- replaces a single `verified` state with layered metadata, evidence and scientific-assessment fields;
- rejects self-verification in executable checks;
- records source links without falsely claiming that the offline validator resolved them;
- updates manuscript title, citation metadata and release documentation.

## Quick start

```bash
python3 -m pip install -r requirements.txt
bash scripts/run_smoke_tests.sh
```

## Scope boundary

The generated scalar event values are diagnostic software-test outputs only. They are not prices, token balances, researcher rankings, hiring or grant metrics, authorship criteria, or governance entitlements. All records are synthetic.

## Archived history

The prior archived release is `v0.3.2-alpha`, DOI `10.5281/zenodo.20324761`. A v0.3.3 DOI should be added only after the GitHub tag is published and Zenodo archives that release.
