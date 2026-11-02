## ADDED Requirements

### Requirement: Patched DOMPurify development resolution
The committed Node lockfile SHALL resolve DOMPurify to version 3.4.17 or later with cryptographic integrity metadata in the Mermaid CLI development dependency graph.

#### Scenario: Development dependencies are installed
- **WHEN** a contributor or CI performs a lockfile-based Node installation
- **THEN** every resolved DOMPurify version is 3.4.17 or later and has npm integrity metadata

### Requirement: DOMPurify advisory remediation verification
The dependency remediation SHALL address GHSA-c6gr-qvv4-5v3f, GHSA-mrv2-3pqr-j5jr, and GHSA-cg2g-xh64-v4q7 while preserving existing documentation tooling functionality.

#### Scenario: Dependency security validation runs
- **WHEN** the updated dependency graph is audited
- **THEN** none of the three DOMPurify advisories applies to the resolved dependency

#### Scenario: Documentation tooling runs
- **WHEN** the configured pre-commit gates run after installing the updated dependency graph
- **THEN** documentation validation and Mermaid rendering complete successfully
