# Reproducibility guide

## Local-candidate acceptance route

Use Python 3.11 or newer from a clean environment:

```text
python -m pip install -r requirements-ci.txt
python MOF_WorkedExample/validate_mof_worked_example.py
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The exact candidate CI requirements are pinned in `requirements-ci.txt`.
`requirements.txt` separately records supported direct-dependency ranges. The
bounded Windows environment recorded in `requirements-tested-local.txt` uses
CPython 3.14.4 with pinned `jsonschema`, `nbclient`, `nbformat` and `ipykernel`
direct dependencies. The repository retains its Ubuntu/Windows workflow
configuration, but no local POSIX run or GitHub Actions cloud PASS is claimed
for this `v0.3.5-alpha` local candidate.

## Restored schema and worked-example checks

The contribution schema keeps the v0.3.4 top-level array API. Its item schema
contains generic and MOF research-object branches; the MOF branch resolves the
relative profile reference offline. The first canonical event embeds the same
parsed JSON value as
`MOF_WorkedExample/synthetic_uio66_research_object.json`.

The worked-example validator and smoke suite check schema validity, inline and
standalone identity, required local evidence-file presence, claimed SHA-256
integrity, source-link state boundaries, and the project-level distinct-verifier
policy for the independently verified synthetic example. They do not contact
remote sources. A recorded source link is not a resolved link, file integrity
is not scientific validation, and `scientific_assessment.status` remains
`not_reviewed` independently of successful metadata/file checks.

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

The canonical dataset remains exactly six events in the v0.3.4 order and with
the same identifiers. The default six-event score is `23.0324`; scoring weights,
the default half-life and diagnostic labels are unchanged. Input labels must be
safe project-relative paths. Windows drive/UNC paths, POSIX absolute paths,
parent traversal, empty/NUL paths and symlink escape are rejected on every
host; accepted labels are normalised to POSIX separators.

## Notebook boundary

`verification_workflow_demo.ipynb` is deliberately unexecuted. The committed
snapshot must be produced by:

```text
python scripts/execute_notebook.py verification_workflow_demo.ipynb generated/verification_workflow_demo_executed.ipynb --backend nbclient --acceptance --workdir .
```

The fallback backend is diagnostic only and cannot create the committed
snapshot or satisfy release acceptance. No cloud GitHub Actions execution is
claimed by this local candidate.

## Candidate boundary

The profile is a thin synthetic MOF research-object adapter, not a universal
MOF reporting standard. No MPIF compatibility, compliance or conformance is
claimed. Successful local acceptance can authorise only independent
`v0.3.5-alpha` software audit; it does not authorise a remote push, pull request,
tag, release, Zenodo action, DOI/date insertion or manuscript change.
