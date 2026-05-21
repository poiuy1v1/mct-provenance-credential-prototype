# Post-Zenodo DOI backfill checklist

After Zenodo archiving, update:

- [x] v219 manuscript Data availability Zenodo DOI
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


## v219 completed backfill

- DOI: `10.5281/zenodo.20274154`
- Release URL: `https://github.com/poiuy1v1/mct-provenance-credential-prototype/releases/tag/v0.3.2-alpha`
- GitHub URL: `https://github.com/poiuy1v1/mct-provenance-credential-prototype`
