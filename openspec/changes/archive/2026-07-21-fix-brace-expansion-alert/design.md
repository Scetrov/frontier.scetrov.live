## Context

Dependabot alert #44 identifies vulnerable `brace-expansion@5.0.6` in the committed npm development dependency graph. The package is reached through `markdownlint-cli@0.49.1` → `minimatch@10.2.5`, and is installed by the documentation-validation workflow through `npm ci`. `minimatch` already declares `brace-expansion@^5.0.5`, which accepts the patched 5.0.7 release. The repository also installs `markdownlint-cli@0.49.1` globally in the development container, but that installation is independent of the committed lockfile.

The change must remediate the recorded lockfile resolution while preserving reproducible, lockfile-backed CI behavior. The requester also requires a pull request, successful required checks, and a final completion notification.

## Goals / Non-Goals

**Goals:**
- Resolve `brace-expansion` to 5.0.7 or later in the committed npm lockfile.
- Preserve the existing direct development dependencies and Markdown lint command.
- Verify the resolved dependency tree and affected lint command before submitting a pull request.
- Create a pull request, wait for required checks to succeed, then notify the requester of completion.

**Non-Goals:**
- Upgrade `markdownlint-cli`, `minimatch`, or unrelated dependencies.
- Change production site behavior or add runtime input handling.
- Treat the devcontainer's global npm installation as lockfile-controlled.
- Merge the pull request unless separately requested.

## Decisions

### Refresh only the compatible transitive lockfile resolution
Use npm's lockfile update path to select `brace-expansion@5.0.7` under the existing `^5.0.5` constraint from `minimatch`. This produces the smallest remediation and retains the existing direct dependency contract.

**Alternative considered:** Add a root-level `overrides` entry. This would force the version but changes `package.json` and is unnecessary because the existing transitive semver range already accepts the patched release.

### Validate the dependency graph and affected tooling
Confirm the installed dependency tree resolves `brace-expansion` to a patched version, then run the repository's Markdown lint npm script. This directly checks the remediation and the only consumer path in this repository.

**Alternative considered:** Rely solely on Dependabot's eventual closure. That does not prove the lockfile update preserves the lint command before opening a pull request.

### Use a PR as the integration gate
Commit the minimal lockfile change on a dedicated branch, create a pull request targeting `main`, and use GitHub's required checks as the final integration signal. Notify only after the PR reports a successful state; report a failing or incomplete check rather than claiming completion.

**Alternative considered:** Merge immediately after local checks. This bypasses the repository's branch-protection and CI validation model, and exceeds the requester’s stated green-PR completion point.

## Risks / Trade-offs

- [The lockfile refresh updates unrelated packages] → Inspect the diff and constrain the change to the `brace-expansion` resolution; stop and reassess if unrelated upgrades appear.
- [Local dependencies differ from a clean CI install] → Use a clean lockfile-based installation before validation where practical and rely on the pull request’s `npm ci` CI job as the final check.
- [A PR check is queued, fails, or is not required] → Monitor check status to completion and notify the requester with the PR URL and actual status rather than assuming success.
- [The development container’s global install remains a separate resolution] → Keep the scope explicit: alert #44 identifies the repository lockfile. Evaluate a devcontainer tool-version update separately if a scanner later reports it.
