# Repository release plan

Recommended public repository name: `mct-provenance-credential-prototype`

Recommended release tag: `v0.3.0-alpha`

Recommended repository description:

> Synthetic supplementary software for MOF Chain Token provenance credentials: contribution-schema design, non-financial reputation-score simulation, metadata-style verification, and a non-transferable credential stub.

## Release logic

1. Use `SupplementarySoftware1/` as the repository root.
2. Create a Git tag `v0.3.0-alpha`.
3. Publish the GitHub release as a pre-release while the paper is under review.
4. Archive the release through Zenodo or another persistent repository.
5. Replace the DOI placeholder `10.5281/zenodo.TBD` with the minted DOI in README, CITATION metadata, release notes, and manuscript.

## Metadata note

Both `CITATION.cff` and `.zenodo.json` are included. GitHub uses `CITATION.cff` to display citation information. Zenodo prioritizes `.zenodo.json` if both metadata files are present, so `.zenodo.json` should be treated as the authoritative Zenodo-release metadata.
