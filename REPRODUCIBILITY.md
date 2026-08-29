# Reproducibility guide

## Acceptance route

Use Python 3.11 or newer from a clean environment:

```text
python -m pip install -r requirements-ci.txt
python MOF_WorkedExample/validate_mof_worked_example.py
python scripts/check_release_neutrality.py --candidate-root .
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The exact acceptance requirements are pinned in `requirements-ci.txt`.
`requirements.txt` separately records supported direct-dependency ranges. The
bounded Windows environment recorded in `requirements-tested-local.txt` uses
CPython 3.14.4 with pinned direct dependencies. The repository retains its
Ubuntu/Windows workflow configuration. Live remote CI execution status is
external evidence and is neither queried nor asserted by the offline package
validator.

## Public-release neutrality

`scripts/check_release_neutrality.py` rejects public candidates containing an
`audit/` directory, conversation/prompt/transcript filenames, internal
review-result filenames, or characteristic workflow-status/prompt markers. The
package validator and release validator both invoke this check, and negative
unit tests prove that representative forbidden artifacts fail closed.

The historical v0.3.4 release-finalization note is stored only as
`history/v0.3.4-alpha_RELEASE_FINALIZATION.md` with an explicit superseded
warning. It is provenance history, not a current release instruction.

## Schema and worked-example checks

The contribution schema keeps the established top-level array API. Its item
schema contains generic and MOF research-object branches; the MOF branch
resolves the relative profile reference offline. The first canonical event
embeds the same parsed JSON value as
`MOF_WorkedExample/synthetic_uio66_research_object.json`.

The worked-example validator and smoke suite check schema validity, inline and
standalone identity, required local evidence-file presence, claimed SHA-256
integrity, source-link state boundaries, and the project-level distinct-verifier
policy. They do not contact remote sources. A recorded source link is not a
resolved link, file integrity is not scientific validation, and
`scientific_assessment.status` remains `not_reviewed`.

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
manifest/checksums and release-neutrality policy, repeats the run and compares
generated hashes.

## Direct diagnostic score command

```text
python -B mct_reward_simulation.py --input data/example_contributions.json --output-dir generated
```

The canonical dataset remains exactly six events in the established order and
with the same identifiers. The default six-event score is `23.0324`; scoring
weights, default half-life and diagnostic labels are unchanged. Input labels
must be safe project-relative paths. Windows drive/UNC paths, POSIX absolute
paths, parent traversal, empty/NUL paths and symlink escape are rejected on
every host.

## Notebook boundary

`verification_workflow_demo.ipynb` is deliberately unexecuted. The committed
snapshot must be produced by:

```text
python scripts/execute_notebook.py verification_workflow_demo.ipynb generated/verification_workflow_demo_executed.ipynb --backend nbclient --acceptance --workdir .
```

The fallback backend is diagnostic only and cannot create the committed
snapshot or satisfy release acceptance. Live GitHub Actions execution remains
external to this offline acceptance route.

## Release and scientific boundary

The profile is a thin synthetic MOF research-object adapter, not a universal MOF
reporting standard. No MPIF compatibility, compliance or conformance is claimed.
Successful acceptance establishes only the technical properties checked by this
offline route. It does not claim live branch, pull-request, CI, tag, release or
archive state and cannot supply human merge, release, DOI/date insertion or
manuscript authorization.
