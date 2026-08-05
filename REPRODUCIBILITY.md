# Reproducibility guide

## Release-acceptance route

Use Python 3.11 or newer from a clean environment:

```text
python -m pip install -r requirements-ci.txt
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The exact candidate CI requirements are pinned in `requirements-ci.txt`.
`requirements.txt` separately records supported direct-dependency ranges. The
v235.1 Windows acceptance used Python 3.14.4 with the pinned `jsonschema`,
`nbclient`, `nbformat` and `ipykernel` direct dependencies. No local POSIX run or
GitHub Actions cloud PASS is claimed by this candidate.

## Deterministic generated-output allow-list

```text
diagnostic_event_scores.csv
diagnostic_sensitivity.csv
release_validation.json
simulation_dry_run_stdout.json
simulation_stdout.json
summary.json
verification_results.csv
verification_workflow_demo_executed.ipynb
```

The smoke driver creates fresh copies, pre-seeds then removes stale output,
regenerates the complete allow-list, rejects extras/missing files, compares the
fresh nbclient notebook semantically with the committed snapshot, validates the
manifest and checksums, repeats the run and compares generated hashes.

## Direct diagnostic score command

```text
python -B mct_reward_simulation.py --input data/example_contributions.json --output-dir generated
```

The default six-event score is `23.0324`. Input labels must be safe
project-relative paths. Windows drive/UNC paths, POSIX absolute paths, parent
traversal, empty/NUL paths and symlink escape are rejected on every host;
accepted labels are normalised to POSIX separators.

## Notebook boundary

`verification_workflow_demo.ipynb` is deliberately unexecuted. The committed
snapshot must be produced by:

```text
python scripts/execute_notebook.py verification_workflow_demo.ipynb generated/verification_workflow_demo_executed.ipynb --backend nbclient --acceptance --workdir .
```

The fallback backend is diagnostic only and cannot create the committed
snapshot or satisfy release acceptance. No cloud GitHub Actions execution is
claimed by this local candidate.
