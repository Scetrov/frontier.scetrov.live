## 1. Repository governance

- [x] 1.1 Enable or identify the GitHub private vulnerability-reporting channel and add `SECURITY.md` with supported scope, reporting process, acknowledgement target, and coordinated-disclosure guidance.
- [x] 1.2 Add a version-controlled Scorecard triage record documenting intentional exceptions for sole-maintainer reviews, fuzzing, the OpenSSF badge, and historical SAST coverage, including reconsideration triggers.
- [x] 1.3 Configure a `main` branch ruleset that blocks deletion and force pushes, applies to administrators, requires pull requests, and requires the existing successful validation checks without requiring a peer approval.
- [x] 1.4 Verify the effective branch ruleset through the GitHub API or repository settings and record the selected required check names.

## 2. Workflow least privilege and reproducibility

- [x] 2.1 Move `security-events: write` from CodeQL workflow scope to the CodeQL analysis job and preserve successful SARIF publication.
- [x] 2.2 Pin the devcontainer base image by digest while retaining its readable tag.
- [x] 2.3 Replace devcontainer `latest` npm and Go tool installs with explicit reviewed versions.
- [x] 2.4 Add or use project npm scripts for Markdown linting and spellchecking, and update documentation validation to invoke those scripts after `npm ci`.
- [x] 2.5 Pin the htmltest installation in documentation validation to an explicit Go module version.

## 3. Dependency remediation

- [x] 3.1 Update the Node dependency resolution so `basic-ftp` is at least 5.3.1, using a narrow root override only if a normal compatible refresh cannot select the patched release.
- [x] 3.2 Regenerate and inspect `package-lock.json` to verify the patched `basic-ftp` resolution and preserve Mermaid CLI compatibility.

## 4. Validation and alert follow-up

- [x] 4.1 Run the affected documentation validation, Mermaid validation, dependency-tree inspection, and dependency audit commands.
- [x] 4.2 Confirm CodeQL can upload results with the narrowed job permission.
- [ ] 4.3 Confirm the next Scorecard run clears the actionable workflow/container/dependency findings or record any scanner limitation.
- [x] 4.4 Dismiss the intentional Scorecard findings in GitHub with the version-controlled triage rationale.
