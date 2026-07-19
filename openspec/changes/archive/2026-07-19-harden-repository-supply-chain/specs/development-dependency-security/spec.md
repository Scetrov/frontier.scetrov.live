## ADDED Requirements

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
