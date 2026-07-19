## Context

The repository is a public, predominantly static Hugo documentation site maintained by one primary owner. Its current security controls include Dependabot, dependency review, CodeQL on push and pull request, secret scanning with push protection, and a weekly Scorecard workflow. The Scorecard results identify mutable tool installation inputs, an unprotected `main` branch, a missing security disclosure policy, broad placement of CodeQL upload permission, and a vulnerable transitive development dependency.

The repository does not run an application service or expose a public API. Its development tooling executes in contributor workstations and GitHub Actions, so supply-chain reproducibility and the integrity of automation are the principal concerns.

## Goals / Non-Goals

**Goals:**
- Prevent destructive or unvalidated changes to `main` while keeping the repository workable for its sole maintainer.
- Ensure each CI and development-container tool is selected from a deterministic version or immutable image digest.
- Keep privileged GitHub token access limited to the CodeQL upload job.
- Provide a clear, private vulnerability-reporting route.
- Remove the known vulnerable `basic-ftp` resolution from the development dependency graph.
- Preserve an auditable rationale for intentionally unaddressed Scorecard criteria.

**Non-Goals:**
- Achieving a perfect Scorecard score or earning an OpenSSF Best Practices badge.
- Requiring an independent approving review before every merge while there is only one trusted maintainer.
- Adding fuzzing infrastructure to static-site tooling.
- Changing public website functionality, content, or API behavior.
- Backfilling static analysis for historical commits when the current tree is analyzed on every push and pull request.

## Decisions

### Use a protected-branch ruleset with required checks, but no required peer approval

`main` will disallow deletion and force pushes, require pull requests and the existing successful validation checks, and apply the rules to administrators. Required checks protect deployed content and automation inputs without needing a second account. The ruleset will not require an approving review while the repository has a sole trusted maintainer.

**Alternative considered:** Require one approving review to satisfy Scorecard's code-review check completely. This would block the only maintainer from merging ordinary work and invites a nominal rather than independent review.

### Scope CodeQL upload permission to the analysis job

`security-events: write` is required to upload CodeQL SARIF results. It will be declared only in the CodeQL analysis job; all other workflow and default permissions remain read-only.

**Alternative considered:** Remove the permission. This would prevent CodeQL from publishing findings and is therefore not acceptable.

### Pin executable build inputs at their selection point

The devcontainer base image will use a tag plus immutable digest. Global npm packages and `go install` modules will use explicit versions. Documentation validation will use project `npm run` commands after `npm ci`, keeping execution tied to the committed lockfile.

**Alternative considered:** Keep `latest` values and rely on Dependabot. Dependabot updates declared dependencies but cannot make a mutable build reproduce exactly or prevent a changed upstream artifact from executing during the next build.

### Resolve `basic-ftp` through the lockfile with a compatible patched version

The `basic-ftp` transitive resolution will be raised to at least 5.3.1, using the package manager's supported override mechanism if the immediate parent does not update first. The lockfile will be regenerated and verified. This addresses both known denial-of-service advisories while retaining the existing Mermaid CLI tooling.

**Alternative considered:** Dismiss because the dependency is development-only and no repository code invokes FTP. The exposure is low, but a known patched resolution is available and developer/CI tooling still executes the dependency graph.

### Record intentional Scorecard exceptions in repository documentation

A concise triage record will explain why peer-review enforcement, fuzzing, the external certification badge, and historical-commit SAST coverage are not adopted. It will name the condition that triggers reconsideration: adding another maintainer, introducing untrusted-input service code, or changing the project governance model.

**Alternative considered:** Dismiss findings only in GitHub's UI. That rationale is not version-controlled, discoverable to contributors, or reviewable alongside governance changes.

## Risks / Trade-offs

- [Pinned versions can age or acquire vulnerabilities] → Continue Dependabot updates and periodically refresh pins through reviewed changes.
- [Branch requirements can slow urgent corrections] → Retain the owner's administrator access while enforcing rules; document an emergency exception process in the security policy/ruleset administration.
- [A sole maintainer lacks independent review] → Require passing automated checks now and revisit required approvals when a second trusted maintainer is available.
- [Package overrides can conceal upstream dependency lag] → Keep the override narrowly scoped, remove it once the parent package resolves a patched version naturally, and verify the dependency tree in CI/local validation.
- [Documentation may drift from GitHub settings] → Treat branch-rule configuration as a task with post-change API verification and record the expected settings in the triage document.

## Migration Plan

1. Add version-controlled policy and triage documentation, then update workflow and container configuration.
2. Regenerate the lockfile and run the affected documentation validation commands and dependency audit.
3. Configure the `main` branch ruleset in GitHub and verify its effective settings through the GitHub API/UI.
4. Allow Scorecard and CodeQL to run on the resulting `main` commit; verify actionable findings have cleared or have a documented intentional exception.

Rollback consists of reverting the configuration commit for workflow/container/dependency regressions, or temporarily relaxing only the affected branch-rule requirement through GitHub administration. The security policy and triage record should remain published during rollback.

## Open Questions

- Which existing workflow check names must be selected in the GitHub ruleset after their next successful runs?
- What private reporting channel (GitHub private vulnerability reporting, a monitored email address, or both) will the maintainer commit to in `SECURITY.md`?
- Does the current npm release graph allow `basic-ftp` 5.3.1 through a normal lockfile refresh, or is a temporary root override required?
