# MCT provenance credential prototype for AI-ready MOF data

Repository name: `mct-provenance-credential-prototype`  
Metadata-cleanup release: `v0.3.2-alpha`  
Manuscript linkage: Paper 1, Supplementary Software 1

This repository contains a minimal, synthetic prototype package for **MCT** contribution recording and non-financial reputation scoring. It is designed as a reviewable research-software companion to the manuscript *The Virtual Attributes of MOFs: Provenance Credentials and Incentive Design for AI-Ready Materials Science*.

**Scope:** synthetic research-infrastructure demonstration only.  
**Not:** a deployed blockchain, production smart contract, ERC-20 token, cryptocurrency, investment product, governance product, or tradable asset.

## Repository contents

```text
mct-provenance-credential-prototype/
├── contribution_schema.json
├── data/
│   └── example_contributions.json
├── mct_reward_simulation.py
├── verification_workflow_demo.ipynb
├── non_transferable_token_stub.sol
├── outputs/
│   ├── mct_scores.csv
│   ├── reward_sensitivity.csv
│   ├── simulation_stdout.json
│   ├── simulation_dry_run_stdout.json
│   ├── summary.json
│   └── verification_results.csv
├── requirements.txt
├── REPRODUCIBILITY.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE
├── CHANGELOG.md
├── RELEASE_NOTES_v0.3.2-alpha.md
├── RELEASE_CHECKLIST.md
└── docs/
    ├── manuscript-links.md
    ├── repository-release-plan.md
    └── data-code-availability-final-sentence.md
```

## Quick start

From the repository root:

```bash
python3 --version
python3 mct_reward_simulation.py --help
python3 mct_reward_simulation.py --input data/example_contributions.json --output-dir outputs
python3 mct_reward_simulation.py --dry-run
```

Expected outputs:

- `outputs/mct_scores.csv`
- `outputs/summary.json`
- `outputs/reward_sensitivity.csv`

The Python script uses only the Python standard library.

## Suggested citation

Cite the accompanying manuscript and the archived software release as:

> Wei, J. *MCT provenance credential prototype for AI-ready MOF data*, v0.3.2-alpha, Supplementary Software 1 for *The Virtual Attributes of MOFs: Provenance Credentials and Incentive Design for AI-Ready Materials Science*. DOI: `10.5281/zenodo.20274154` (archived Zenodo DOI).

## Scientific interpretation

The generated `mct_reputation_score` is a **research-recognition score** for synthetic contribution events. It has no price, market value, transferability, investment value, or financial claim. Its role is to make under-recognized research work - dataset deposition, negative results, replication, peer validation, sample sharing, model provenance, and metadata curation - visible in a structured provenance system.

## Verification model

The notebook and script use synthetic metadata checks only. In a real implementation, ORCID, DOI, repository, curator, journal, and institutional checks would require authenticated APIs, repository-specific metadata policies, and governance agreements.

## Solidity stub

`non_transferable_token_stub.sol` demonstrates the shape of a locked credential. It deliberately avoids ERC-20-like transferability and reverts on transfer-like functions. It is not audited, not ERC-721-complete, and must not be deployed as production infrastructure.

## Release status

This v0.3.2-alpha package is a metadata-cleanup release. It preserves the same synthetic prototype as v0.3.1-alpha while aligning public GitHub/Zenodo-facing wording with non-financial MCT provenance-credential language. The prior manuscript-linked DOI is listed above; Zenodo will mint/display a new DOI after this tag is published.

## Release preparation quick commands

Run the local smoke tests before pushing to GitHub:

```bash
bash scripts/run_smoke_tests.sh
```

The public repository is:

```text
https://github.com/poiuy1v1/mct-provenance-credential-prototype
```

The archived Zenodo-triggered release tag is:

```text
v0.3.2-alpha
```

Detailed GitHub and Zenodo instructions are provided in `docs/github-release-commands.md` and `docs/zenodo-archive-steps.md`.


Metadata-cleanup release URL: `https://github.com/poiuy1v1/mct-provenance-credential-prototype/releases/tag/v0.3.2-alpha`
