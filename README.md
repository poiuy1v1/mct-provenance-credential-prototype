# MOF Chain Token provenance credential prototype

Repository name: `mct-provenance-credential-prototype`  
Release candidate: `v0.3.0-alpha`  
Manuscript linkage: Paper 1, Supplementary Software 1

This repository contains a minimal, synthetic prototype package for **MOF Chain Token (MCT)** contribution recording and non-financial reputation scoring. It is designed as a reviewable research-software companion to the manuscript *The Virtual Attributes of MOFs: Provenance Credentials and Incentive Design for AI-Ready Materials Science*.

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
├── RELEASE_NOTES_v0.3.0-alpha.md
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

Until the final DOI is minted, cite the accompanying manuscript and this release candidate:

> Wei, J. *MOF Chain Token provenance credential prototype*, v0.3.0-alpha, Supplementary Software 1 for *The Virtual Attributes of MOFs: Provenance Credentials and Incentive Design for AI-Ready Materials Science*. DOI: `10.5281/zenodo.TBD` (placeholder to be replaced after Zenodo archiving).

## Scientific interpretation

The generated `mct_reputation_score` is a **research-recognition score** for synthetic contribution events. It has no price, market value, transferability, investment value, or financial claim. Its role is to make under-recognized research work - dataset deposition, negative results, replication, peer validation, sample sharing, model provenance, and metadata curation - visible in a structured provenance system.

## Verification model

The notebook and script use synthetic metadata checks only. In a real implementation, ORCID, DOI, repository, curator, journal, and institutional checks would require authenticated APIs, repository-specific metadata policies, and governance agreements.

## Solidity stub

`non_transferable_token_stub.sol` demonstrates the shape of a locked credential. It deliberately avoids ERC-20-like transferability and reverts on transfer-like functions. It is not audited, not ERC-721-complete, and must not be deployed as production infrastructure.

## Release status

This v212 Codex/GitHub release-preparation version is suitable for Codex-assisted repository finalization, local smoke testing, GitHub upload, GitHub release creation, and Zenodo archiving. The DOI placeholder remains until Zenodo archives the tagged release.

## Release preparation quick commands

Run the local smoke tests before pushing to GitHub:

```bash
bash scripts/run_smoke_tests.sh
```

The intended public repository is:

```text
https://github.com/poiuy1v1/mct-provenance-credential-prototype
```

The intended first release tag remains:

```text
v0.3.0-alpha
```

Detailed GitHub and Zenodo instructions are provided in `docs/github-release-commands.md` and `docs/zenodo-archive-steps.md`.
