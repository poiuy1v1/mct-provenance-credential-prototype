# v0.3.4-alpha release finalisation gates

Nothing in this local candidate records an action below as completed.

## 1. Pre-release candidate checks

- Run exact clean-environment schema, policy, unit, negative, notebook,
  snapshot, path, secret, stale-file and package checks.
- Require the `nbclient` acceptance backend and retain its exact environment.
- Obtain an independent audit of the candidate ZIP and reports.

## 2. Human GitHub branch, PR, CI and merge approval

- A responsible human may later approve a branch, pull request, cloud CI and
  merge. This v235.1 task authorises none of those actions.

## 3. GitHub tag and pre-release creation

- Only after human approval may a new `v0.3.4-alpha` tag and pre-release be
  created. The historical `v0.3.3-alpha` tag must remain unchanged.

## 4. Zenodo version creation or synchronisation

- Only after the GitHub release exists may a human create/synchronise a new
  Zenodo software version. The historical record must not be overwritten.

## 5. Post-release DOI and date capture

- Record the actual version DOI, release date, commit and archive hash only
  after they exist. Do not predict or prefill them.

## 6. Later manuscript and SI backfill

- A separately authorised v236 document stage may update Main/SI to the actual
  superseding release and correct the unsupported SI value `26.2855`.
