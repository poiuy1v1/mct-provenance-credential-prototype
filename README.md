# MOF contribution-credential prototype for AI-ready MOF data

Current status: **local unpublished `v0.3.4-alpha` candidate**.

This candidate has not been pushed, tagged, released, or archived. It has no
candidate DOI and no release date. The last published historical version is
`v0.3.3-alpha`, archived as `10.5281/zenodo.21643012`; that identifier is
historical provenance only and is not the DOI of this candidate.

## What this candidate repairs

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
  unpublished-candidate metadata.

The frozen SI value `26.2855` has no bundled executable provenance. Main and SI
are outside this software-repair candidate and were not edited; a later v236
document stage must address the SI wording.

## Validation

Release acceptance requires Python 3.11+ and the exact candidate CI
requirements:

```text
python -m pip install -r requirements-ci.txt
python scripts/run_smoke_tests.py --notebook-backend nbclient
```

The smoke driver copies the candidate to two clean temporary roots, removes and
regenerates the allow-listed outputs, executes the source notebook, runs schema,
policy, unit, negative and snapshot checks, and compares the two generated runs.
The committed executed notebook is acceptable only when generated through the
`nbclient` backend. A standard-library execution route may be used for offline
diagnosis but is not release-acceptance evidence.

## Boundary

All records and chemical values are synthetic. The prototype is non-financial,
non-transferable and non-ranking. Its identifier, schema, evidence-presence and
file-integrity checks do not authenticate people, resolve scientific truth or
constitute scientific validation. Diagnostic event scores are not prices,
token balances, hiring or grant metrics, authorship criteria, governance
entitlements, or researcher rankings. A blockchain is not required.
