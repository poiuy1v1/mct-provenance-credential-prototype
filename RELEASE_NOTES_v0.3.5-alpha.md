# v0.3.5-alpha

This version restores the useful semantic/schema layer represented in
`v0.3.3-alpha` and integrates it with the hardened execution and reproducibility
baseline retained from `v0.3.4-alpha`. It is a restoration-and-integration
version, not a rollback, greenfield rewrite or scoring expansion.

## Restored semantic layer

- The top-level contribution API remains an array. Generic and MOF
  `research_object` branches, internal definitions and the portable relative
  MOF-profile reference are restored inside each item.
- Evidence links, metadata hashes, optional local evidence paths/SHA-256 values
  and separate metadata, evidence-file, file-integrity, source-link and
  scientific-assessment states are restored as non-scoring provenance fields.
- The detailed standalone synthetic UiO-66 object covers material and sample
  identity, synthesis/activation lineage, characterisation evidence, reported
  outcome, source anchoring and validation state. The first canonical event
  embeds exactly the same parsed domain-profile JSON value.
- Bounded offline validation covers schema composition, profile identity,
  required local evidence presence, claimed SHA-256 integrity, source-link
  state boundaries and the example's project-level distinct-verifier policy.

## Retained execution baseline

- The canonical dataset remains exactly six events with unchanged identifiers
  and ordering.
- Scoring logic, weights, diagnostic labels and the default half-life remain
  unchanged; the authoritative executable diagnostic total remains `23.0324`.
- Genuine `nbclient` execution, committed/fresh notebook comparison,
  deterministic clean-directory output regeneration, portable-path checks,
  package manifest/checksum validation and Ubuntu/Windows workflow
  configuration are retained.

## Scope and source-metadata boundary

The MOF profile is a thin synthetic research-object adapter. It is not a
universal MOF metadata/reporting standard, and no MPIF compatibility,
compliance or conformance is claimed. All records and chemical values remain
synthetic, non-financial, non-transferable and non-ranking. File existence and
SHA-256 integrity do not establish scientific truth; remote source resolution
is not performed, and scientific assessment remains `not_reviewed`.

`10.5281/zenodo.21826427` is identified solely as the historical
previous-version DOI. Source metadata deliberately does not embed a current
`v0.3.5-alpha` DOI or publication date; the archive/publication process assigns
those externally. Live GitHub Actions, release and archive status are external
to the offline validator and are not asserted by this source package.
