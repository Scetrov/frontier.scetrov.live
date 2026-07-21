# development-dependency-security Specification

## Purpose
TBD - created by archiving change harden-repository-supply-chain. Update Purpose after archive.
## Requirements
### Requirement: Patched basic-ftp development resolution
The committed Node dependency resolution SHALL use `basic-ftp` version 5.3.1 or later whenever the Mermaid CLI development dependency graph is installed.

#### Scenario: Development dependencies are installed
- **WHEN** a contributor or CI runs the lockfile-based Node installation
- **THEN** the resolved `basic-ftp` version is 5.3.1 or later

### Requirement: Advisory remediation verification
The dependency remediation SHALL be verified against GHSA-rp42-5vxx-qpwr and GHSA-rpmf-866q-6p89, and the project SHALL retain its existing Mermaid CLI functionality.

#### Scenario: Dependency security validation runs
- **WHEN** the updated lockfile is audited and its dependency tree is inspected
- **THEN** neither advisory is satisfied by a `basic-ftp` version at or below 5.3.0

#### Scenario: Mermaid tooling is invoked
- **WHEN** the existing Mermaid validation or rendering tooling runs after the dependency update
- **THEN** it completes using the updated dependency resolution

### Requirement: Patched brace-expansion development resolution
The committed Node dependency resolution SHALL use `brace-expansion` version 5.0.7 or later whenever the Markdown lint development dependency graph is installed.

#### Scenario: Development dependencies are installed
- **WHEN** a contributor or CI runs the lockfile-based Node installation
- **THEN** the resolved `brace-expansion` version is 5.0.7 or later

### Requirement: Brace-expansion advisory remediation verification
The dependency remediation SHALL be verified against GHSA-3jxr-9vmj-r5cp and CVE-2026-13149, and the project SHALL retain its existing Markdown lint functionality.

#### Scenario: Dependency security validation runs
- **WHEN** the updated lockfile is audited and its dependency tree is inspected
- **THEN** the resolved `brace-expansion` version is not within any vulnerable range identified by GHSA-3jxr-9vmj-r5cp

#### Scenario: Markdown lint tooling is invoked
- **WHEN** the existing Markdown lint npm script runs after the dependency update
- **THEN** it completes using the updated dependency resolution

