## Why

Dependabot alert #44 reports a high-severity denial-of-service vulnerability (GHSA-3jxr-9vmj-r5cp / CVE-2026-13149) in the development-only `brace-expansion` resolution currently committed in `package-lock.json`. The current transitive version is 5.0.6; a compatible patched release is available and should be recorded in the lockfile so CI and contributors install the safe dependency tree.

## What Changes

- Refresh the committed npm lockfile so the transitive `brace-expansion` dependency resolves to patched version 5.0.7 or later without changing the direct development-tooling contract.
- Validate the updated dependency tree against Dependabot alert #44 and run the affected documentation lint workflow locally.
- Submit the remediation as a pull request, monitor its required validation, and notify the requester after the pull request is green.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `development-dependency-security`: Extend development-dependency remediation requirements to cover the patched `brace-expansion` resolution and its advisory verification.

## Impact

- `package-lock.json` will change; `package.json` is not expected to change.
- The `markdownlint-cli` → `minimatch` development-tooling path used by documentation linting will receive the patched transitive package.
- Pull-request automation and the existing documentation-validation CI workflow will be used to verify the remediation.
