# GitHub release commands for v0.3.2-alpha

Repository URL:

```text
https://github.com/poiuy1v1/mct-provenance-credential-prototype
```

Recommended local workflow after creating an empty GitHub repository:

```bash
cd mct-provenance-credential-prototype
git init
git branch -M main
git status
bash scripts/run_smoke_tests.sh
git add .
git commit -m "Prepare v0.3.2-alpha supplementary software prototype"
git remote add origin https://github.com/poiuy1v1/mct-provenance-credential-prototype.git
git push -u origin main
git tag -a v0.3.2-alpha -m "v0.3.2-alpha: synthetic MOF provenance credential prototype"
git push origin v0.3.2-alpha
```

Then create a GitHub Release from tag `v0.3.2-alpha` and paste the contents of `RELEASE_NOTES_v0.3.2-alpha.md` into the release notes.
