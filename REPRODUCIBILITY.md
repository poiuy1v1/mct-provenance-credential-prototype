# Reproducibility guide - Supplementary Software 1

Release candidate: `v0.3.0-alpha`  
Repository name: `mct-provenance-credential-prototype`  
DOI placeholder: `10.5281/zenodo.TBD`

## Purpose

This package is a synthetic, reviewer-inspectable prototype for the MOF Chain Token (MCT) manuscript. It demonstrates contribution-event schemas, non-financial reputation-score simulation, metadata-style verification, and non-transferable credential representation.

It is **not** a deployed blockchain, production smart contract, cryptocurrency, investment product, tradable token, or governance system.

## Environment

- Python: 3.10 or later recommended; tested with Python 3.13.5.
- Python dependencies: none beyond the standard library.
- Solidity file: provided for static inspection only; not compiled, audited, or deployed.
- Notebook: JSON notebook for explanatory inspection; code cells use Python standard-library modules only.

## Reproduce the generated outputs

From the repository root:

```bash
python3 --version
python3 mct_reward_simulation.py --help
python3 mct_reward_simulation.py --input data/example_contributions.json --output-dir outputs
python3 mct_reward_simulation.py --dry-run
```

Expected generated files:

- `outputs/mct_scores.csv`
- `outputs/summary.json`
- `outputs/reward_sensitivity.csv`

The verification notebook writes:

- `outputs/verification_results.csv`

## Smoke-test commands

```bash
python3 mct_reward_simulation.py --dry-run > outputs/simulation_dry_run_stdout.json
python3 mct_reward_simulation.py --input data/example_contributions.json --output-dir outputs --half-life-days 365
python3 -m json.tool contribution_schema.json > /dev/null
python3 -m json.tool data/example_contributions.json > /dev/null
```

## Expected interpretation of outputs

The synthetic demo records six contribution events. The total synthetic non-financial reputation score should remain approximately `28.3064` when the default inputs and default half-life are used. This number is a test output only; it is not a token balance, price, market value, grant decision, or author-ranking metric.

## Limitations

The package uses synthetic records. Passing the checks does not authenticate an actual DOI, ORCID, repository, journal decision, curator action, or institutional claim. A real implementation would require authenticated APIs, governance processes, privacy rules, and legal review.

## Archival plan

For journal submission, the final version can be released through a GitHub repository and archived through Zenodo or another persistent repository. Replace `10.5281/zenodo.TBD`, `https://github.com/poiuy1v1/mct-provenance-credential-prototype`, Zenodo DOI metadata before public archiving.
