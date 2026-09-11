## 1. Lock regression evidence

- [x] 1.1 Preserve the current cursor, plan, inventory, coverage, and pinned-source snippets needed as deterministic regression fixtures.
- [x] 1.2 Make temporary Git repositories configure test-only noninteractive identity, hooks/editor behavior, and `commit.gpgSign=false` without changing project or user signing policy.
- [x] 1.3 Add failing tests for stale local refs, mismatched remote identity, missing complete-validation inputs, malformed structures, invalid field types, nonexistent objects, incorrect merge bases, unrelated evidence commits, missing evidence paths, unmapped modules/paths, branch movement, and no-op reviews.

## 2. Enforce canonical provenance

- [x] 2.1 Normalize supported GitHub SSH/HTTPS remote forms and reject repositories that are not `evefrontier/world-contracts`.
- [x] 2.2 Fetch declared refs and resolve candidates only from freshly fetched canonical remote-tracking refs, never local branch names.
- [x] 2.3 Verify reviewed cursor objects exist as commits, recompute the merge base, and require exact cursor/candidate equality.
- [x] 2.4 Parse every factual upstream URL, restrict it to the cursor's permitted commits, and verify the cited path exists at that commit.
- [x] 2.5 Add a final-ref verification operation that reports stable heads or newer pending commits without substituting unreviewed SHAs.

## 3. Make completeness explicit

- [x] 3.1 Separate Move source modules from tests and archive paths in generated inventories and retain deterministic ordering.
- [x] 3.2 Replace broad prefix allowlisting with structured records that give every relevant changed path a meaningful disposition.
- [x] 3.3 Add exact coverage mappings for every required v0 domain/module, active v1 source module, and archived module, and reject missing, duplicate, conflicting, or archive-as-active mappings.
- [x] 3.4 Move internal coverage data outside `content/` unless publication is explicitly intended, and update helper, skill, and documentation references.

## 4. Correct content and workflow clarity

- [x] 4.1 Correct `inventory-and-events.md` to distinguish entity/event tenant identity from item-carried provenance and document the v0 parent/location/tenant fields absent from the reviewed v1 `Item`.
- [x] 4.2 Rewrite the maintenance skill with explicit repository root, workflow directory, `$repo` assignment, clone/fetch, plan, inventory, incremental/rebaseline, complete validation, final-ref check, rollback, report, no-op, and scoped cleanup commands.
- [x] 4.3 Make the completed-review command require repository, candidate plan, inventory, coverage, and chapter inputs while keeping any partial checks clearly diagnostic and non-authoritative.
- [x] 4.4 Convert malformed JSON/TOML, missing keys, wrong types, Git failures, and interrupted checks into actionable controlled non-zero errors without tracebacks.

## 5. Integrate validation and minimize scope

- [x] 5.1 Add the focused standard-library comparison test suite to CI and ensure it runs for relevant helper, skill, coverage, and content changes.
- [x] 5.2 Remove the global Goldmark block-attribute setting unless an actual content requirement and rendering test justify it.
- [x] 5.3 Reconcile the active `add-world-contracts-version-comparison` task claims with the corrected implementation and do not archive either change while review-integrity gates fail.

## 6. Verify the remediated change

- [x] 6.1 Run the focused tests under ordinary configuration and with inherited commit signing enabled; confirm both runs complete noninteractively.
- [x] 6.2 Run canonical plan, inventory, complete validation, evidence-path, coverage, no-op, rewritten-history, and final-branch-movement scenarios against controlled repositories.
- [x] 6.3 Run Hugo build, Markdown lint, Mermaid validation, TOML frontmatter validation, spelling, and built-site link checking.
- [x] 6.4 Inspect the rendered inventory and coverage pages plus the final scoped diff for factual accuracy, clarity, maintainability, and unrelated configuration.
- [x] 6.5 Archive the completed OpenSpec changes before the final signed conventional commit or pull request.
