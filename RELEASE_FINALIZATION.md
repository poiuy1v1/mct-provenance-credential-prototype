# v0.3.3-alpha release finalization

1. Push this complete tree to `release/v0.3.3-alpha-artifact-alignment`.
2. Confirm the GitHub Actions end-to-end validation job passes.
3. Merge the reviewed branch to `main`.
4. Create pre-release tag `v0.3.3-alpha` from the tested commit.
5. Publish the GitHub pre-release.
6. In Zenodo GitHub integration, sync the repository and wait for the version-specific DOI.
7. Backfill the real release date and DOI into `CITATION.cff`, README, SI and manuscript Data availability.

Do not invent or pre-reserve a version DOI in these files.
