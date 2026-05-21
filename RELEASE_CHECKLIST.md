# GitHub / Zenodo release checklist

Target repository name: `mct-provenance-credential-prototype`  
Target release tag: `v0.3.2-alpha`  
Archived Zenodo DOI: `10.5281/zenodo.20274154`

## Before GitHub release

- [x] Create a clean GitHub repository named `mct-provenance-credential-prototype`.
- [ ] Move the contents of `SupplementarySoftware1/` to the repository root.
- [ ] Confirm that `README.md`, `REPRODUCIBILITY.md`, `requirements.txt`, `CITATION.cff`, `.zenodo.json`, and `LICENSE` are present at repository root.
- [ ] Confirm `repository-code: https://github.com/poiuy1v1/mct-provenance-credential-prototype` in `CITATION.cff`.
- [ ] Replace repository URL fields in `.zenodo.json`.
- [ ] Add the final ORCID if desired.
- [ ] Confirm the final affiliation spelling.
- [ ] Run all smoke-test commands in `REPRODUCIBILITY.md`.
- [ ] Confirm that all data are synthetic and that no personal data, private keys, wallets, unpublished third-party datasets, API tokens, production endpoints, or financial claims are included.
- [ ] Confirm that `non_transferable_token_stub.sol` remains clearly labelled as non-production and unaudited.

## GitHub release

- [x] Create the tag `v0.3.2-alpha`.
- [x] Draft release notes using `RELEASE_NOTES_v0.3.2-alpha.md`.
- [ ] Mark the release as a pre-release if the journal submission is still under review.
- [ ] Confirm that the release archive contains the same files as the submitted Supplementary Software package.

## Zenodo archival

- [x] Enable GitHub-Zenodo archiving for the repository.
- [ ] Confirm that `.zenodo.json` is valid JSON.
- [ ] Confirm that `CITATION.cff` is valid CFF/YAML for GitHub citation display.
- [x] Archive the GitHub release through Zenodo.
- [x] Replace the DOI placeholder in the manuscript, README, CITATION, and release notes with the minted DOI.
- [ ] Add the final Zenodo DOI to the Data and code availability statement.
