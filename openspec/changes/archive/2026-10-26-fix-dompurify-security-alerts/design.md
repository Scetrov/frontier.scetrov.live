# Design

Use the existing Mermaid dependency ranges to resolve DOMPurify 3.4.17 without introducing overrides or a direct dependency. npm confirms 3.4.17 is the latest released version, and upstream release notes identify fixes for all three findings.

## Verification

Containerized npm audit reproduced GHSA-c6gr-qvv4-5v3f, GHSA-mrv2-3pqr-j5jr, and GHSA-cg2g-xh64-v4q7 before the update. Afterward DOMPurify is absent from the audit report. The full audit still reports unrelated KaTeX and Zod advisories and their dependent packages.

A disposable Chromium harness exercises split template expressions inside shadow roots, hook-detached parent/sibling handlers, and XHTML SVG attributeName sanitization. All three unsafe behaviors reproduce with 3.4.16 and are absent with 3.4.17. No upstream library test harness is added to this documentation repository.

Run a clean npm installation, dependency-tree inspection, and the complete configured pre-commit gate. The host lacks htmltest and Chromium shared libraries; use a checksum-verified htmltest 0.17.0 binary and digest-pinned Playwright Chromium through an external wrapper without changing repository gates.
