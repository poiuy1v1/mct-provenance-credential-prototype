# MOF contribution-credential prototype for AI-ready MOF data

Current software version: **`v0.3.4-alpha`**.

Version-specific citation metadata are provided by the corresponding GitHub
Release and Zenodo record. The previously published `v0.3.3-alpha` release is
archived as `10.5281/zenodo.21643012`; that identifier applies only to the
historical release and is not the DOI of `v0.3.4-alpha`.

## What v0.3.4-alpha changes

- freezes the uniquely executable six-event diagnostic sum at `23.0324` while
  retaining the frozen formulas and illustrative constants;
- defines canonical timestamp/event-ID ordering so equivalent input
  permutations serialize identically;
- preserves an unexecuted source notebook and adds an execution/output-aware
  regression with mandatory negative cases;
- validates input labels with both Windows and POSIX path flavours, accepts
  only contained project-relative files, and normalises labels to POSIX form;
- commits the sanitised snapshot produced by the real `nbclient` acceptance
  backend with sequential execution counts and retained outputs;
- regenerates deterministic CSV/JSON/notebook artifacts in clean directories;
- provides a Windows/Ubuntu CI matrix, package-integrity validation and
  release-facing metadata.

The value `26.2855` found in an earlier supporting-information draft is not
produced by this release. The executable six-event diagnostic sum is `23.0324`.

## Validation

Release validation requires Python 3.11+ and the exact CI requirements:

```text
python -m pip install -r requirements-ci.txt
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The smoke driver copies the release tree to two clean temporary roots, removes
and regenerates the allow-listed outputs, executes the source notebook, runs
schema, policy, unit, negative and snapshot checks, and compares the two
generated runs. The committed executed notebook is accepted only when generated
through the `nbclient` backend. A standard-library execution route may be used
for offline diagnosis but is not release-acceptance evidence.

## Boundary

All records and chemical values are synthetic. The prototype is non-financial,
non-transferable and non-ranking. Its identifier, schema, evidence-presence and
file-integrity checks do not authenticate people, resolve scientific truth or
constitute scientific validation. Diagnostic event scores are not prices,
token balances, hiring or grant metrics, authorship criteria, governance
entitlements, or researcher rankings. A blockchain is not required.
