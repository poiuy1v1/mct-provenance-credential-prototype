# Changelog

## v0.3.3-alpha - executable artifact alignment release candidate

- Composed generic and MOF research-object schemas using `oneOf` and `$ref`.
- Standardised validation vocabulary across JSON, notebook, outputs, manuscript and SI.
- Separated metadata, file-presence, integrity, source-link and scientific-assessment multipliers.
- Set all distributed synthetic event records to `scientific_assessment.status = not_reviewed`.
- Added complete release validation, negative tests and notebook execution to CI.
- Renamed scalar outputs as diagnostic event scores and removed contributor aggregates from the default summary.
- Removed release-date and archived-version claims until GitHub and Zenodo publication are complete.
