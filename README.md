# MOF contribution-credential prototype for AI-ready MOF data

Current version: **`v0.3.6-alpha`**.

This clean-successor source preserves the complete semantic/schema and
reproducibility behaviour of the historical `v0.3.5-alpha` release while
removing internal workflow/conversation material from the public release tree.
It is a packaging-neutrality and historical-document clarity update, not a new
scientific result, scoring design or application-domain expansion.

The historical `v0.3.5-alpha` release is archived as
`10.5281/zenodo.22062669`. In source metadata that DOI appears only as the
previous-version (`isNewVersionOf`) relation. The source metadata does not
embed a version-specific `v0.3.6-alpha` DOI or publication date; those values
are assigned externally by the archive/publication process.

## What v0.3.6-alpha changes

- removes the tracked internal Codex conversation/task log from the public
  source tree;
- moves the old `v0.3.4-alpha` release-finalization instructions under
  `history/` with an explicit historical/superseded warning;
- adds a fail-closed release-neutrality validator and negative tests that reject
  `audit/` directories, conversation/prompt/transcript filenames, internal
  review-result filenames and characteristic internal workflow markers;
- updates release, schema, profile, event and scoring version fields coherently
  to `0.3.6-alpha`;
- preserves all scientific, schema and executable behaviour described below.

## Preserved semantic and execution model

- the top-level contribution API remains an array with generic/MOF
  `research_object` branches, internal definitions, and a portable relative
  reference to the MOF profile inside each array item;
- evidence links, metadata hashes, optional local evidence paths and SHA-256
  values remain non-scoring provenance fields;
- metadata, evidence-file, file-integrity, source-link and
  scientific-assessment states remain separate;
- the detailed standalone synthetic UiO-66 profile remains exactly equal as
  parsed JSON to the first canonical event's inline domain profile;
- local evidence presence and claimed SHA-256 integrity are checked offline,
  while source-link recording remains distinct from remote resolution and file
  integrity remains distinct from scientific review;
- exactly six canonical events, their identifiers/order, frozen formulas and
  weights, default half-life, and executable diagnostic total `23.0324` are
  retained;
- genuine `nbclient` execution, deterministic clean-directory output
  regression, portable-path checks, and package manifest/checksum validation
  are retained.

The value `26.2855` found in an earlier supporting-information draft is not
produced by this version. The executable six-event diagnostic sum remains
`23.0324`.

## Local validation

Use Python 3.11+ and the exact CI requirements in a clean local environment:

```text
python -m pip install -r requirements-ci.txt
python MOF_WorkedExample/validate_mof_worked_example.py
python scripts/check_release_neutrality.py --candidate-root .
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The smoke driver copies the source tree to two clean temporary roots,
regenerates the complete output allow-list, executes the source notebook, runs
schema, worked-example, package-neutrality, policy, unit, negative and snapshot
checks, and compares the two generated runs. The committed executed notebook is
accepted only when generated through the `nbclient` backend.

The repository retains Windows and Ubuntu workflow configuration. Live remote
CI execution status is external evidence: the offline package validator neither
queries nor asserts it.

## Scope and validation boundary

The MOF profile is a **thin synthetic MOF research-object adapter** connecting
evidence-linked records, explicit validation states and non-financial
contribution recognition. It is not presented as a universal MOF metadata
standard. It does not claim MPIF compatibility, compliance or conformance.

All records and chemical values are synthetic. The prototype is non-financial,
non-transferable and non-ranking. Its identifier, schema, evidence-presence and
file-integrity checks do not authenticate people, resolve remote sources,
establish scientific truth or constitute scientific validation. The distinct
contributor/verifier rule is a project policy for the synthetic example when it
claims independent verification, not a universal W3C requirement. Diagnostic
event scores are not prices, token balances, hiring or grant metrics, authorship
criteria, governance entitlements, or researcher rankings. A blockchain is not
required.

## Source and lifecycle boundary

This versioned source tree is stage-neutral: it does not encode whether a live
branch, pull request, GitHub Actions run, tag, release or archive currently
exists. Those lifecycle facts are external evidence. Offline validation of the
source does not itself supply human merge, release, archive, manuscript or
publication authorization.
