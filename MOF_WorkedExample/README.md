# Synthetic MOF worked example

This directory contains the `v0.3.6-alpha` synthetic UiO-66 worked example:

- `mof_research_object_profile.schema.json` defines material identity;
  sample/batch/specimen identity; synthesis and activation lineage;
  characterisation evidence; reported outcome; source anchoring; and separate
  validation states.
- `synthetic_uio66_research_object.json` is the standalone profile. The same
  parsed JSON value is embedded as the first canonical contribution event's
  `research_object.domain_profile`.
- `evidence/` contains the retained synthetic evidence bytes. SHA-256 values in
  the profile are computed from those local files.
- `validate_mof_worked_example.py` performs bounded offline schema, local-file,
  hash, source-state and project-policy checks. It does not resolve remote
  sources or make a scientific assessment.

This profile is a **thin synthetic MOF research-object adapter** connecting
evidence-linked records, explicit validation states and non-financial
contribution recognition. It is not a universal MOF reporting standard, and no
MPIF compatibility, compliance or conformance is claimed.

All records, evidence files and chemical values are synthetic. A successful
schema check, evidence-presence check or SHA-256 match establishes only the
corresponding metadata/file-integrity state; it does not establish synthesis
validity, phase identity or any other scientific truth. The example therefore
keeps `scientific_assessment.status` as `not_reviewed`.

The requirement that contributor and verifier identities differ applies only
as this project's policy when the synthetic example claims independent
verification. It is not stated as a universal W3C Verifiable Credentials rule,
and the example is not represented as a secured/conforming W3C credential.
