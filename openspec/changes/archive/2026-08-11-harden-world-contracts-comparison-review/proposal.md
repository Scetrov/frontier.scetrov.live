## Why

The initial World Contracts comparison can report a completed, source-pinned review without proving that the reviewed repository, commits, evidence links, changed files, or module/domain dispositions match the canonical cursor. The current unstaged implementation also overstates v1 inventory provenance, provides an incomplete maintenance command, and has validation tests that can hang locally and are not run in CI, so the comparison is not yet safe to treat as authoritative or maintainable.

## What Changes

- Make comparison validation fail closed: require the upstream repository, reviewed-candidate plan, inventory, and coverage inputs for a completed review.
- Verify the canonical upstream remote identity, resolve freshly fetched remote-tracking refs rather than possibly stale local branches, prove cursor objects and merge-base correctness, restrict evidence URLs to the canonical reviewed commits, and detect branch movement before finalization.
- Replace broad prefix-only coverage with explicit, machine-checkable dispositions for every relevant changed path, v0 domain, active v1 source module, and archived module; keep machine data outside the published content tree unless intentionally documented.
- Correct the inventory comparison so it distinguishes tenant-scoped entity/event identity from the v0 transit item's parent, location, tenant, and provenance fields that the reviewed v1 `Item` does not retain.
- Make the maintenance skill directly executable with explicit scoped clone/fetch, repository-variable setup, inventory generation, complete validation, no-op, rebaseline, final-ref-check, and cleanup commands.
- Make helper failures actionable and bounded for malformed JSON/TOML, missing keys, invalid types, Git failures, and interrupted validation rather than emitting uncaught tracebacks.
- Make Git fixture tests independent of user signing/editor configuration, add regression cases for every fail-closed boundary, and run the focused suite in CI.
- Remove the unrelated global Goldmark block-attribute setting unless a documented rendering requirement and test justify it.

## Capabilities

### New Capabilities

- `world-contracts-comparison-review-integrity`: Defines the provenance, completeness, factual-accuracy, workflow, error-handling, and regression-test gates required before a World Contracts comparison review may be marked complete.

### Modified Capabilities

None.

## Impact

- `scripts/update-world-contracts-version-comparison.py` and `scripts/tests/test_update_world_contracts_version_comparison.py`
- `.agents/skills/update-world-contracts-version-comparison/`
- `content/develop/world-contracts/version-comparison/`, especially inventory prose and coverage data placement/schema
- `.github/workflows/docs-validation.yml` or an equivalent focused validation workflow
- `hugo.toml`
- The active `add-world-contracts-version-comparison` change must be corrected and revalidated before it is archived or shipped.
