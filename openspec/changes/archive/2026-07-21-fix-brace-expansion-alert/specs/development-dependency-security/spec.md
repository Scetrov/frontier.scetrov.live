## ADDED Requirements

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
