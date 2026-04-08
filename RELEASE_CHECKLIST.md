# Release Checklist

## Status
- [x] README present
- [x] LICENSE present
- [x] Citation metadata present (`CITATION.cff`, `.zenodo.json`)
- [x] Primary application or generation assets present
- [x] Smoke or validation entry point present
- [x] Release note generator present
- [ ] Working tree cleaned for release
- [ ] Tagged release created

## Before Publishing
1. Open the main browser application locally, or regenerate the emitted output if this repo is a generator.
2. Run the repo's smoke or validation checks.
3. Confirm generated artifacts are intentionally included or moved out of the release diff.
4. Generate or review the release notes under `release/`.
5. Create and publish the release tag.
6. Mint or update the Zenodo DOI if archival citation is required.
