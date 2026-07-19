# OpenSSF Scorecard triage

This record distinguishes Scorecard findings that require remediation from intentional exceptions suited to this repository's current scope and maintainer model. It supplements, but does not replace, GitHub's recorded alert dismissals.

## Implemented controls

- The `main` ruleset blocks deletion and force pushes, applies to administrators, requires a pull request, and requires the documented validation checks to pass.
- GitHub private vulnerability reporting is enabled; see [`SECURITY.md`](../SECURITY.md).
- CodeQL grants `security-events: write` only to its analysis job.
- Development-container and documentation-validation executable inputs are pinned, and the Node lockfile resolves patched development dependencies.

## Intentional exceptions

| Scorecard area | Rationale | Reconsideration trigger |
| --- | --- | --- |
| Code review | The repository has one trusted maintainer with merge access. Requiring an approving peer review would make normal maintenance impossible without creating a nominal reviewer. Automated validation remains required. | Require an approving peer review when a second trusted maintainer receives merge access, or when governance changes to provide an independent reviewer. |
| Fuzzing | This is a static Hugo documentation site; it does not contain a parser, network service, or other untrusted-input application component for which new fuzzing infrastructure would be proportionate. | Reassess if the repository adds untrusted-input processing, service code, or a custom parser. |
| OpenSSF Best Practices badge | Earning and maintaining the external badge is not a project goal. Concrete security controls are tracked and improved independently of badge status. | Reassess if users, contributors, or the project governance model require external certification. |
| SAST coverage of historical commits | CodeQL analyzes the current tree on pushes and pull requests. Retrospective scanning of every historical commit would not improve protection for the deployed static site proportionately. | Reassess after a security incident, a significant codebase expansion, or a governance requirement for historical analysis. |

## Scanner limitations

Scorecard alerts **#4** and **#5** both identify `npmCommand not pinned by hash` at the same devcontainer instruction. The Dockerfile installs `npm@12.0.1` and `markdownlint-cli@0.49.1` by explicit reviewed versions, which satisfies the repository reproducibility requirement. Scorecard's Dockerfile heuristic treats npm package versions as mutable unless the command itself includes a hash, even though npm package installation does not support a practical package-content hash form in this command. The alerts are dismissed as duplicate scanner limitations and must be reconsidered if Scorecard adds support for version-pinned npm installs or the devcontainer installation method changes.

## Branch ruleset verification

The effective GitHub ruleset for `main` is verified after configuration through the GitHub API. Required status checks: `Dependency review`, `Analyze (python)`, and `Validate documentation (Hugo, linters, spellcheck, linkcheck)`. No approving peer review is required while the sole-maintainer exception applies.
