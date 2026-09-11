## Context

The active `add-world-contracts-version-comparison` change introduces a source-pinned chapter, maintenance skill, Python helper, coverage data, and tests. Review reproduced several fail-open paths:

- `validate --chapter ...` exits successfully without candidates, inventory, coverage, or repository input.
- Ref resolution selects a stale local branch before a newer `origin/<ref>`.
- Any repository with `main`/`dev` refs can be analyzed while metadata still names `evefrontier/world-contracts`.
- Coverage checks accept six aggregate rows and broad path prefixes without mapping the 13 active v1 source modules or every v0 domain/module.
- Any syntactically immutable 40-hex GitHub URL is accepted even when its commit is outside the canonical cursor.
- The skill references an undefined `$repo`, focused Git tests inherit interactive signing configuration, and CI does not run them.
- The inventory narrative claims retained provenance that the reviewed v1 `Item` layout does not contain.

Documentation rendering, Markdown, Mermaid, spelling, frontmatter, and built-site links pass. Twenty-five cited GitHub paths also exist at their stated commits. The remediation therefore preserves the useful chapter structure while fixing provenance, completeness, factual wording, and maintenance gates.

## Goals / Non-Goals

**Goals:**

- Make a completed review cryptographically and structurally traceable to the canonical upstream repository and exact reviewed objects.
- Make completeness validation impossible to bypass through omitted optional arguments or broad catch-all prefixes.
- Represent every relevant path/module/domain disposition in deterministic machine data without publishing internal validation data unintentionally.
- Correct the reviewed inventory/provenance explanation.
- Provide a runnable, failure-safe maintenance skill and reliable automated regression tests.
- Keep the final change minimal by removing unrelated global rendering configuration.

**Non-Goals:**

- Automatically interpret Move semantics or generate reader-facing prose without human review.
- Execute or deploy upstream Sui packages.
- Claim runtime, production, or in-game status from source presence.
- Change the comparison's chapter routes or the existing v0 documentation routes.
- Disable signing for repository commits; only isolated test-fixture repositories may explicitly disable signing.

## Decisions

### Treat the fetched canonical remote as the only candidate authority

The helper will normalize and verify the configured `origin` fetch URL against `evefrontier/world-contracts`, fetch the declared refs, and resolve only `refs/remotes/origin/main` and `refs/remotes/origin/dev`. Local branch names are never candidate inputs. Finalization will fetch and resolve again, compare current remote heads with the reviewed candidates, and report advanced heads without changing the reviewed cursor.

Accepting local refs was rejected because local branches can be stale, rewritten, or unrelated. Trusting only the metadata repository string was rejected because it does not identify the Git objects actually analyzed.

### Make completed-review validation one fail-closed contract

A completed review validation command will require the repository, reviewed-candidate plan, inventory, and coverage data together. It will verify repository identity; object existence and commit type; the actual merge base; exact cursor/candidate equality; canonical evidence-link commit membership and path existence; inventory schema; coverage completeness; and branch-movement status. Missing inputs, fields, wrong types, malformed JSON/TOML, Git failures, or interrupted checks return a controlled non-zero validation error.

Keeping optional validation layers was rejected because the shortest invocation currently gives a misleading `valid: true`. Separate diagnostic subcommands may remain, but only the complete contract can authorize cursor advancement.

### Use explicit coverage records instead of prefix allowlisting

Move machine data outside `content/` (for example under a script-support or data directory) unless it is intentionally documented for readers. Give each record a stable identifier, source kind, exact path or narrowly defined pattern, comparison state, relevance/disposition, and evidence/narrative reference. Validation will derive source-module inventories separately from test files, require every active v1 source module and required v0 domain/module to map exactly once, keep archived modules distinct, and require every relevant changed path to have a meaningful disposition.

Broad prefixes such as `contracts/`, `sdk/`, and `scripts/` were rejected because they prove only that a path begins with a common directory, not that anyone reviewed its effect.

### Validate evidence against the cursor, not only URL shape

Every factual upstream URL will be parsed into repository, commit, and path. Its commit must be the canonical v0 or v1 reviewed commit appropriate to the claim (or the recorded merge base when explicitly used for branch-history evidence), and its path must exist at that object. Mutable refs, unrelated 40-hex commits, nonexistent objects, and nonexistent paths fail validation.

Syntax-only immutability was rejected because a permanent link can still cite the wrong or nonexistent source tree.

### Describe v1 inventory identity without claiming retained item provenance

The inventory page will distinguish tenant-scoped identity derived from the enclosing `EntityKey` and emitted event keys from item-carried provenance. It will state that the reviewed v1 `Item` holds ID, type, quantity, and volume and does not retain the v0 transit item's parent, location, or tenant fields. Any remaining provenance or authorization statement must identify the exact check and source location.

### Make the skill an executable runbook

The skill will define repository root, workflow directory, repository path, clone/fetch commands, prerequisite checks, plan and inventory output paths, review-mode branches, complete validation commands, final-ref verification, no-op behavior, cursor rollback, reporting, and scoped cleanup. Shell variables will be assigned before use and all paths quoted.

A prose instruction to “resolve and fetch” was rejected because it leaves critical identity and workspace choices to each operator and currently invokes an undefined variable.

### Isolate Git fixtures and enforce the suite in CI

Temporary test repositories will set local test-only identity, editor, hooks, and `commit.gpgSign=false` before creating fixture commits. This does not alter project or user signing policy. Tests will cover stale-local precedence, wrong remote identity, missing required inputs, wrong/nonexistent cursor objects, merge-base mismatch, unrelated evidence commits, missing evidence paths, unmapped coverage, malformed data, final branch movement, and no-op behavior. CI will run the focused standard-library suite.

### Remove unrelated rendering scope

Revert global Goldmark block-attribute parsing unless an actual page uses the feature and a rendering test requires it. The comparison builds successfully without the setting, so retaining it would broaden site-wide parsing behavior without benefit.

## Risks / Trade-offs

- **[Explicit coverage data is larger]** Complete records take more maintenance effort → generate deterministic inventories, require concise dispositions, and keep narrative links rather than duplicating prose.
- **[Remote URL normalization can reject valid clone forms]** HTTPS and SSH forms differ → normalize approved GitHub HTTPS and SSH forms to one repository identity before comparison.
- **[Fresh fetch requires network access]** Offline validation cannot authorize a new cursor → allow local diagnostic checks but reserve completed-review status for the online fail-closed command.
- **[Evidence-path validation may expose old link mistakes]** Existing links can begin failing → report every failing page/URL together and do not advance the cursor until corrected.
- **[CI adds a small runtime cost]** Temporary Git repositories add seconds → keep the focused suite standard-library-only and deterministic.

## Migration Plan

1. Preserve the existing comparison cursor and capture the current plan/inventory for regression fixtures.
2. Correct inventory/provenance prose and relocate/restructure coverage data.
3. Implement canonical remote resolution, complete validation, evidence/path checks, coverage mapping, final-ref checking, and controlled errors.
4. Expand tests, make fixture commits noninteractive, and add the suite to CI.
5. Rewrite the maintenance skill as an executable runbook using the new commands.
6. Remove the unnecessary Goldmark setting.
7. Run the focused tests, complete helper validation, Hugo, Markdown, Mermaid, frontmatter, spelling, and built-site link checks.
8. Re-review all original comparison claims and only then retain `review_status = "complete"`.

Rollback restores the previous helper, skill, and coverage layout, but the cursor must not be represented as newly validated if any fail-closed gate is unavailable.

## Open Questions

None. The exact non-content location and filename for coverage data may follow existing repository conventions as long as it is deterministic and not unintentionally published.
