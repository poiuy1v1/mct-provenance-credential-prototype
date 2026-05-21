# Repository release plan

Recommended public repository name: `mct-provenance-credential-prototype`

Recommended release tag: `v0.3.2-alpha`

Recommended repository description:

> Synthetic supplementary software for MCT provenance credentials: contribution-schema design, non-financial reputation-score simulation, metadata-style verification, and a non-transferable credential stub.

## Release logic

1. Use `SupplementarySoftware1/` as the repository root.
2. Create a Git tag `v0.3.2-alpha`.
3. Publish the GitHub release as a pre-release while the paper is under review.
4. Archive the release through Zenodo or another persistent repository.
5. Replace the Zenodo DOI `10.5281/zenodo.20274154` with the minted DOI in README, CITATION metadata, release notes, and manuscript.

## Metadata note

Both `CITATION.cff` and `.zenodo.json` are included. GitHub uses `CITATION.cff` to display citation information. Zenodo prioritizes `.zenodo.json` if both metadata files are present, so `.zenodo.json` should be treated as the authoritative Zenodo-release metadata.


Archived release URL: `https://github.com/poiuy1v1/mct-provenance-credential-prototype/releases/tag/v0.3.2-alpha`
