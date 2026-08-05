# Changelog

## v0.3.4-alpha - Unreleased local candidate

- Reconciled score provenance to the executable `23.0324` diagnostic value.
- Added genuine execution-state and deterministic-output notebook regression.
- Added mandatory notebook negative cases and output snapshot hardening.
- Added cross-platform clean-directory generation and reproducibility checks.
- Hardened project-relative input labels across Windows, UNC and POSIX syntax,
  including traversal and symlink-containment checks before file reads.
- Replaced the diagnostic notebook snapshot with real `nbclient` output and
  added committed-versus-regenerated semantic comparison.
- Added Windows/Ubuntu matrix validation of package manifests and checksums.
- Aligned candidate metadata without inventing a DOI or release date.

## v0.3.3-alpha - Historical published release

- Historical release archived as DOI `10.5281/zenodo.21643012`.
- Its score and notebook-snapshot defects are retained as historical provenance
  and are not rewritten by this candidate.
