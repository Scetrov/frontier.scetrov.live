## Why

The public repository has fourteen OpenSSF Scorecard findings. Several identify concrete, low-cost supply-chain and governance gaps: mutable build inputs, overly broad workflow permission placement, no security disclosure policy, an unprotected default branch, and a known-vulnerable transitive development dependency. Addressing the actionable findings now improves reproducibility and reduces repository-administration risk without imposing unsuitable controls on a sole-maintainer project.

## What Changes

- Protect `main` against destructive changes and require the existing validation workflows before merging, with rules enforced for administrators.
- Narrow CodeQL's `security-events: write` permission to its analysis job.
- Add a repository security policy with a private vulnerability-reporting path and response expectations.
- Make development-container and CI-installed tooling deterministic by pinning the base image and package/module versions; replace implicit `npx` invocations with lockfile-backed project scripts.
- Resolve the vulnerable transitive `basic-ftp` development dependency to a version patched for both known denial-of-service advisories.
- Document intentional Scorecard exceptions for peer review, fuzzing, certification badge, and historical SAST coverage.

## Capabilities

### New Capabilities
- `repository-security-governance`: Defines protected-branch controls, vulnerability reporting, and documented exceptions appropriate to this repository's maintainer model.
- `reproducible-development-tooling`: Defines deterministic source and version selection for development-container and documentation-validation tooling.
- `development-dependency-security`: Defines remediation requirements for known vulnerable development dependencies.

### Modified Capabilities
- None.

## Impact

- Affects GitHub branch rules and `.github/workflows/codeql.yml`, `.github/workflows/docs-validation.yml`, and associated repository documentation.
- Affects `.devcontainer/Dockerfile`, `package.json`, and `package-lock.json`.
- Adds a security policy and a documented Scorecard-triage record.
- No public site API, content format, or runtime visitor behavior changes.
