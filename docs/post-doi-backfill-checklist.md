# Post-Zenodo DOI backfill checklist

After Zenodo archiving, update:

- [ ] `paper1_v212_CodexGitHubReleasePrep.tex` Data availability DOI placeholder
- [ ] `README.md` citation section
- [ ] `CITATION.cff` DOI field
- [ ] `.zenodo.json` notes or related identifiers, if needed
- [ ] `docs/data-code-availability-final-sentence.md`
- [ ] `submission/cover_letter_DigitalDiscovery_draft.md`, if the DOI is mentioned
- [ ] `submission/submission_checklist_RSC.md`
- [ ] Package README and Cambridge QC summary

Then rerun:

```bash
bash scripts/run_smoke_tests.sh
```

and recompile the PDF.
