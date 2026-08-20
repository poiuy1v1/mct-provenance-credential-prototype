# MOF contribution-credential prototype for AI-ready MOF data

Current local candidate version: **`v0.3.5-alpha`**. This is a local
implementation candidate only.

This candidate restores the useful semantic/schema layer represented in the
historical `v0.3.3-alpha` software and integrates it with the hardened execution
and reproducibility baseline of the historical `v0.3.4-alpha` release. It is
not a rollback or a new scoring design.

The historical `v0.3.4-alpha` release is archived as
`10.5281/zenodo.21826427`. In candidate metadata that DOI appears only as the
previous-version (`isNewVersionOf`) relation. No version-specific
`v0.3.5-alpha` DOI or publication date has been assigned.

## What v0.3.5-alpha restores and retains

- keeps the top-level contribution API as an array and restores generic/MOF
  `research_object` branches, internal definitions, and a portable relative
  reference to the MOF profile inside each array item;
- restores evidence links, metadata hashes, optional local evidence paths and
  SHA-256 values without making those provenance fields part of scoring;
- represents metadata, evidence-file, file-integrity, source-link and
  scientific-assessment states separately;
- uses the detailed standalone synthetic UiO-66 profile as the first canonical
  event's inline domain profile, with exact parsed-JSON equality between the
  two representations;
- checks local evidence presence and claimed SHA-256 integrity offline, while
  keeping source-link recording distinct from remote resolution and file
  integrity distinct from scientific review;
- retains exactly six canonical events, their identifiers and ordering, the
  frozen formulas and weights, the default half-life, and the authoritative
  executable diagnostic total `23.0324`;
- retains genuine `nbclient` notebook execution, deterministic clean-directory
  output regression, portable path checks, and package manifest/checksum
  validation from the v0.3.4 execution baseline.

The value `26.2855` found in an earlier supporting-information draft is not
produced by this candidate. The executable six-event diagnostic sum remains
`23.0324`.

## Local validation

Use Python 3.11+ and the exact CI requirements in a clean local environment:

```text
python -m pip install -r requirements-ci.txt
python MOF_WorkedExample/validate_mof_worked_example.py
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The smoke driver copies the candidate tree to two clean temporary roots,
removes and regenerates the allow-listed outputs, executes the source notebook,
runs schema, worked-example, policy, unit, negative and snapshot checks, and
compares the two generated runs. The committed executed notebook is accepted
only when generated through the `nbclient` backend. A standard-library
execution route may be used for offline diagnosis but is not acceptance
evidence.

The repository retains Windows and Ubuntu workflow configuration, but no remote
CI result is claimed for this local candidate.

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

## Candidate status

This tree is prepared only for local implementation and independent software
audit. No remote branch, pull request, tag, GitHub Release, GitHub Actions run,
Zenodo archive, DOI backfill, manuscript change or publication action is
authorised by this candidate.
