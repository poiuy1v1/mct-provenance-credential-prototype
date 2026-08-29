# v0.3.6-alpha

This clean-successor version removes internal workflow artifacts from the public
source tree and adds fail-closed release-neutrality validation. It preserves the
semantic/schema, synthetic scientific scope and deterministic executable truth
of `v0.3.5-alpha`.

## Public-artifact neutrality correction

- Removes the tracked visible Codex conversation/task log from the release tree.
- Historicalizes the superseded `v0.3.4-alpha` release-finalization note under
  `history/` with an explicit warning that it is not current release guidance.
- Adds a reusable neutrality validator that rejects `audit/` directories,
  conversation/prompt/transcript filenames, internal-review result filenames
  and characteristic workflow prompt/status markers.
- Adds negative tests and invokes the neutrality check from package and release
  validation.

## Preserved semantic and executable truth

- Generic/MOF `research_object` branches and the portable relative MOF-profile
  reference are unchanged in meaning.
- The standalone and inline synthetic UiO-66 profiles remain JSON-value
  identical, and retained evidence bytes/hashes are unchanged.
- The canonical dataset remains exactly six events in the same order.
- Scoring constants, default half-life and per-event diagnostic scores remain
  unchanged; the total remains `23.0324`.
- Genuine `nbclient` execution, deterministic output regeneration, path
  security, package manifests/checksums and Ubuntu/Windows workflow
  configuration are retained.
- Scientific assessment remains `not_reviewed`; no MPIF compatibility,
  compliance or conformance is claimed.

## Metadata boundary

`10.5281/zenodo.22062669` is identified solely as the historical
`v0.3.5-alpha` previous-version DOI. Source metadata deliberately does not embed
a current `v0.3.6-alpha` DOI or publication date; those are assigned externally
if and when an independently audited successor is published. Live remote CI,
release and archive status remain external to the offline validator.
