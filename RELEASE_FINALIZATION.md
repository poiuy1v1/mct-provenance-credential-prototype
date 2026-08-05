# v0.3.4-alpha release provenance and publication policy

## Completed gates

- The executable candidate passed independent review of its score provenance,
  real `nbclient` notebook execution, deterministic outputs and package checks.
- The audited candidate was integrated through a pull request.
- Pull-request CI passed on `ubuntu-latest` and `windows-latest`.
- The pull request was squash-merged into `main` as commit
  `8182e30cdd790a99d7cb80b4416b6ee095aad9a2` with tree
  `d3e03909ed60b43a07ceb1ba36334dd6e83b43d6`.
- Post-merge CI Run #38 passed on `ubuntu-latest` and `windows-latest`.

## Publication gates still requiring real external events

1. Create the `v0.3.4-alpha` Git tag from the final metadata commit on `main`.
2. Publish the corresponding GitHub pre-release.
3. Allow Zenodo to create or synchronise a new software version without
   overwriting the historical `v0.3.3-alpha` record.
4. Capture the actual version-specific DOI, publication date, final commit and
   archive hash only after they exist.
5. Update citation metadata and the manuscript/SI only in a separately
   authorised post-release backfill stage.

No DOI, release date, tag, GitHub Release or Zenodo archive is predicted or
prefilled by this file.

## Scientific and usage boundary

The authoritative executable diagnostic sum is `23.0324`. The frozen SI value
`26.2855` has no bundled executable provenance and must be handled in the later
document stage. All records remain synthetic; the software is non-financial,
non-transferable and non-ranking, and it does not establish scientific truth.
