# Changelog

## v0.3.2-alpha / metadata-cleanup release

- Prepared a Zenodo-facing metadata cleanup release after the v0.3.1-alpha archive.
- Kept the title as `MCT provenance credential prototype for AI-ready MOF data`.
- Removed residual high-risk legacy full-name MCT wording from software-facing metadata where possible without changing the manuscript concept.
- Preserved all prototype functionality, synthetic data, outputs, and smoke-test behaviour.
- Retained the prior manuscript-linked DOI `10.5281/zenodo.20274154` until Zenodo mints the v0.3.2-alpha DOI.

## v0.3.2-alpha / manuscript v219 - post-Zenodo DOI backfill

- Archived the public GitHub release through Zenodo.
- Backfilled Zenodo DOI `10.5281/zenodo.20274154` into manuscript and software metadata.
- Updated `CITATION.cff`, `.zenodo.json`, README, release notes, and documentation to use the archived release tag `v0.3.2-alpha`.
- Aligned repository metadata title to `MCT provenance credential prototype for AI-ready MOF data` to reduce ambiguity around financial-token interpretation.
- Preserved the synthetic-only, non-financial, non-transferable credential boundary.

## Manuscript v210 figure-polish and human metadata QC (no software-version change)
- Inserted confirmed ORCID, full Cambridge affiliation, GitHub owner, funding statement, and compact AI-tool statement.
- Polished manuscript Figure 1 and regenerated the 8 cm x 4 cm TOC graphic.
- Updated repository URL metadata to https://github.com/poiuy1v1/mct-provenance-credential-prototype.
- Retained Zenodo DOI until Zenodo archiving.


## Manuscript v209 human-fill-in QC (no software-version change)
- Added final human metadata checklist for ORCID, funding, repository owner, Zenodo DOI, and co-author/supervisor decision.
- No changes to reward simulation or credential-stub functionality.

## v207 - final submission language QC

- Harmonized manuscript-facing wording around MCT credential, reputation score, and provenance record.
- Confirmed no new software functionality was added in v207.
- Updated documentation references from Paper 1 v206 to Paper 1 v207 where relevant.

## v0.3.2-alpha - repository release preparation

- Prepared `SupplementarySoftware1/` for a clean GitHub/Zenodo repository release.
- Set recommended repository name to `mct-provenance-credential-prototype`.
- Standardized release tag, version metadata, citation metadata, and Zenodo DOIs.
- Updated `README.md`, `REPRODUCIBILITY.md`, `CITATION.cff`, `.zenodo.json`, and `RELEASE_CHECKLIST.md`.
- Added release notes, repository-structure guidance, and final Data/code availability wording.
- Preserved the v205 synthetic prototype functionality without adding new scientific claims.

## v0.2.0 - supplementary software polish

- Added command-line help, dry-run mode, reproducibility instructions, and release metadata templates.
- Added schema example block and stronger non-deployment warnings.

## v0.1.0 - minimal synthetic prototype

- Added initial contribution schema, reward simulation, verification notebook, non-transferable credential stub, and generated synthetic outputs.


## v208 - RSC submission-compliance QC
- Aligned manuscript statement order with RSC/Digital Discovery conventions.
- Added TOC graphic assets, cover-letter draft, reviewer-template file and submission checklist to the package.
- No new algorithmic functionality added; repository and synthetic prototype remain at v0.3.2-alpha.

## v212 manuscript release-preparation update

- Added GitHub Actions smoke-test workflow.
- Added `scripts/run_smoke_tests.sh` for local reproducibility checks.
- Added GitHub release commands and Zenodo archiving guidance.
- Added post-DOI manuscript backfill checklist.
- Preserved v0.3.2-alpha software functionality and non-financial credential framing.
