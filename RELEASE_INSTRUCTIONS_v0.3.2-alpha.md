# v0.3.2-alpha metadata-cleanup release instructions

Purpose: trigger a Zenodo archive whose public title is safer and clearer:

```text
MCT provenance credential prototype for AI-ready MOF data
```

## Files to update on GitHub

Copy the contents of this folder into the GitHub repository root:

```text
https://github.com/poiuy1v1/mct-provenance-credential-prototype
```

Commit message:

```text
Prepare v0.3.2-alpha metadata cleanup release
```

## GitHub release fields

Tag:

```text
v0.3.2-alpha
```

Target:

```text
main
```

Release title:

```text
v0.3.2-alpha: Metadata cleanup for MCT provenance credential prototype
```

Release notes: paste the contents of `RELEASE_NOTES_v0.3.2-alpha.md`.

Tick:

```text
Set as a pre-release
```

Then click `Publish release`.

## After Zenodo processing

Zenodo should mint/display a DOI for the v0.3.2-alpha release. Send that DOI back if you want the manuscript Data availability statement to cite the metadata-cleanup release instead of the prior v0.3.1-alpha DOI `10.5281/zenodo.20274154`.
