# v0.3.4-alpha release provenance and publication policy

## 1. Completed executable evidence

- The bounded software candidate underwent independent executable regression
  audit before repository integration.
- Pull request #3 merged the audited implementation into `main` as commit
  `8182e30cdd790a99d7cb80b4416b6ee095aad9a2`, preserving tree
  `d3e03909ed60b43a07ceb1ba36334dd6e83b43d6`.
- GitHub Actions run #38 passed on both Ubuntu and Windows with the real
  `nbclient` acceptance backend.
- The authoritative synthetic six-event diagnostic sum is `23.0324`.

## 2. Release creation rule

- Create tag `v0.3.4-alpha` only from a metadata-finalised, green-validated
  `main` commit.
- Publish the GitHub release as a pre-release.
- Preserve the historical `v0.3.3-alpha` tag and release unchanged.

## 3. Zenodo version rule

- Synchronise a new Zenodo software version only after the GitHub pre-release
  exists.
- Do not overwrite the historical record `10.5281/zenodo.21643012`.
- Treat the DOI assigned to the new Zenodo version as the authoritative
  version-specific identifier.

## 4. DOI, date and archive capture

- Record the actual DOI, publication date, release commit and archive checksum
  only after GitHub and Zenodo have created them.
- Do not predict or prefill identifiers or dates in repository metadata.

## 5. Manuscript and supporting-information alignment

- A separately authorised document stage may cite the final archived
  `v0.3.4-alpha` release and its version-specific DOI.
- The value `26.2855` in an earlier supporting-information draft is unsupported
  by the executable evidence and must be corrected to the reproducible value
  `23.0324` in that later document stage.
