# Fix DOMPurify security alerts

## Why

GitHub Dependabot alerts #68, #69, and #70 identify three DOMPurify vulnerabilities in the Mermaid CLI development dependency graph. CodeQL has no open alerts.

## What Changes

- Update only the locked DOMPurify resolution from 3.4.16 to 3.4.17, retaining npm SHA-512 integrity verification.
- Verify the three advisory behaviors in containerized Chromium and preserve documentation tooling functionality.

## Capabilities

### Modified Capabilities

- `development-dependency-security`: require a patched DOMPurify development dependency resolution.

## Impact

Only the transitive development lockfile resolution changes; no application code, direct dependency ranges, or rendered site behavior is intentionally changed. Unrelated KaTeX and Zod audit advisories are outside this change.
