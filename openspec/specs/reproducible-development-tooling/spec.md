# Reproducible Development Tooling

## Purpose
Define deterministic source and version selection for development-container and documentation-validation tooling.

## Requirements

### Requirement: Immutable development-container base image
The development-container Dockerfile SHALL select its base image by immutable digest while retaining a readable version tag.

#### Scenario: Base tag is republished upstream
- **WHEN** the upstream base-image tag changes after this change is merged
- **THEN** a build using the committed Dockerfile resolves the originally reviewed image digest

### Requirement: Pinned development-container tool installs
The development-container Dockerfile SHALL install npm packages and Go modules using explicit versions and SHALL NOT use `latest` for executable tooling.

#### Scenario: Devcontainer rebuild occurs later
- **WHEN** a contributor rebuilds the development container from the committed Dockerfile
- **THEN** the installed npm and Go tools match the versions declared in the Dockerfile

### Requirement: Lockfile-backed documentation validation commands
The documentation-validation workflow SHALL install Node dependencies from the committed lockfile and SHALL invoke project-defined npm scripts for Node-based validation commands.

#### Scenario: Documentation validation runs in CI
- **WHEN** the documentation-validation workflow executes after `npm ci`
- **THEN** Node validation commands use the versions resolved by the committed lockfile without fetching an undeclared command package

### Requirement: Pinned CI Go tool installation
The documentation-validation workflow SHALL install htmltest at an explicit Go module version and SHALL NOT request its `latest` version.

#### Scenario: CI runs link validation
- **WHEN** the documentation-validation workflow installs htmltest
- **THEN** it installs the explicit declared version before running link validation

### Requirement: Least-privilege CodeQL upload permission
The CodeQL workflow SHALL grant `security-events: write` only to the job that uploads CodeQL analysis results.

#### Scenario: CodeQL analysis publishes results
- **WHEN** the CodeQL analysis job completes successfully
- **THEN** it can upload security results to GitHub code scanning

#### Scenario: Other workflow jobs execute
- **WHEN** a non-CodeQL job runs
- **THEN** it does not receive CodeQL's security-events write permission
