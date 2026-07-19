# repository-security-governance Specification

## Purpose
TBD - created by archiving change harden-repository-supply-chain. Update Purpose after archive.
## Requirements
### Requirement: Default branch integrity
The repository SHALL protect `main` from deletion and force pushes, SHALL require a pull request and successful designated validation checks before merge, and SHALL enforce those controls for administrators.

#### Scenario: Normal change reaches main
- **WHEN** a pull request targets `main`
- **THEN** it cannot merge until all designated required checks have succeeded

#### Scenario: Destructive branch operation is attempted
- **WHEN** any actor attempts to delete or force-push `main`
- **THEN** GitHub rejects the operation

### Requirement: Sole-maintainer review exception
The repository SHALL NOT require an approving peer review while it has only one trusted maintainer with merge access, and SHALL document that exception and its reconsideration trigger.

#### Scenario: Maintainer model changes
- **WHEN** a second trusted maintainer receives merge access
- **THEN** the repository governance documentation identifies required peer-review enforcement as requiring review

### Requirement: Vulnerability reporting policy
The repository SHALL publish a `SECURITY.md` that defines supported scope, a private reporting channel, expected acknowledgement expectations, and a prohibition on public disclosure before coordination.

#### Scenario: Researcher reports a vulnerability
- **WHEN** a researcher opens the repository security policy
- **THEN** they can identify a private reporting route and the expected response process

### Requirement: Intentional Scorecard exception record
The repository SHALL version-control the rationale and reconsideration conditions for intentionally unaddressed Scorecard findings covering fuzzing, the OpenSSF Best Practices badge, historical-commit SAST coverage, and the sole-maintainer review exception.

#### Scenario: Contributor reviews an open Scorecard finding
- **WHEN** a contributor reads the triage record
- **THEN** they can distinguish intentional exceptions from findings that require remediation

