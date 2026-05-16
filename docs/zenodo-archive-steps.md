# Zenodo archiving steps

1. Log in to Zenodo.
2. Enable the GitHub integration.
3. Toggle archiving on for `poiuy1v1/mct-provenance-credential-prototype`.
4. Create the GitHub release `v0.3.0-alpha`.
5. Wait for Zenodo to archive the release.
6. Copy the resulting DOI.
7. Replace all `10.5281/zenodo.TBD` placeholders in:
   - manuscript Data availability section
   - `README.md`
   - `CITATION.cff`
   - `.zenodo.json`
   - `docs/data-code-availability-final-sentence.md`
   - cover letter / submission files if used
8. Recompile the manuscript and run a final QC pass.

Do not replace the placeholder before Zenodo creates the archived release DOI.
