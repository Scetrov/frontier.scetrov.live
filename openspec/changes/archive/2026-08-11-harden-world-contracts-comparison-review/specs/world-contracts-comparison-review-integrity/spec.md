## ADDED Requirements

### Requirement: Canonical upstream candidate authority
The comparison review tooling SHALL verify that its Git repository is the canonical `evefrontier/world-contracts` repository, SHALL fetch the declared refs, and SHALL resolve review candidates only from the freshly fetched canonical remote-tracking refs.

#### Scenario: Local branch is stale
- **WHEN** a local `main` or `dev` branch differs from the corresponding freshly fetched canonical remote-tracking ref
- **THEN** the helper selects the remote-tracking commit and does not use the local branch as a review candidate

#### Scenario: Repository identity is wrong
- **WHEN** the supplied repository's normalized canonical remote does not identify `evefrontier/world-contracts`
- **THEN** planning and completed-review validation fail before source analysis or cursor advancement

### Requirement: Fail-closed completed-review validation
A completed comparison review SHALL require the canonical repository, reviewed-candidate plan, generated inventory, explicit coverage data, and canonical chapter together. Validation SHALL reject omitted inputs, malformed structures, invalid types, unavailable Git objects, cursor/candidate mismatches, and an incorrect recorded merge base with a controlled non-zero error.

#### Scenario: Completeness input is omitted
- **WHEN** completed-review validation is invoked without the repository, candidate plan, inventory, or coverage data
- **THEN** validation fails and does not return `valid: true`

#### Scenario: Candidate data is malformed
- **WHEN** candidate or inventory JSON is malformed, incomplete, or has an invalid field type
- **THEN** validation reports an actionable bounded error without an uncaught traceback

#### Scenario: Merge base is incorrect
- **WHEN** the cursor's merge-base commit differs from the merge base computed from the reviewed v0 and v1 commits
- **THEN** completed-review validation fails

### Requirement: Cursor-bound evidence validation
Every factual upstream source URL in the comparison SHALL identify the canonical upstream repository, an allowed commit from the canonical cursor, and a path that exists at that commit.

#### Scenario: Immutable URL uses an unrelated commit
- **WHEN** a factual link contains a syntactically valid 40-hex commit that is not the applicable reviewed v0 commit, reviewed v1 commit, or explicitly permitted merge-base commit
- **THEN** completed-review validation rejects the link

#### Scenario: Evidence path does not exist
- **WHEN** an immutable factual link names a path absent from its allowed reviewed commit
- **THEN** completed-review validation identifies the page and URL and fails

### Requirement: Exhaustive explicit coverage mapping
The review inventory SHALL separate source modules from tests and archived files. Coverage data SHALL map every required v0 domain/module, every active v1 source module, every archived module required by the comparison, and every relevant changed path to an explicit state and meaningful disposition without relying on broad catch-all prefixes.

#### Scenario: Active module is omitted
- **WHEN** an active v1 source module has no exact coverage mapping
- **THEN** the review is incomplete and the cursor cannot advance

#### Scenario: Changed path is hidden by a broad prefix
- **WHEN** a relevant changed path matches a directory prefix but has no explicit review disposition
- **THEN** completeness validation rejects the coverage data

#### Scenario: Archived source is mapped as active
- **WHEN** a source path beneath `contracts/archive/` is used to satisfy active v1 coverage
- **THEN** completeness validation fails

### Requirement: Accurate inventory provenance comparison
The inventory comparison SHALL distinguish tenant-scoped entity or event identity from item-carried provenance and SHALL accurately state which v0 parent, location, tenant, and provenance fields are absent from the reviewed v1 `Item` representation.

#### Scenario: Reader compares item provenance
- **WHEN** the inventory and events page describes retained and changed inventory properties
- **THEN** it does not claim that v1 items retain v0 transit-item provenance fields unless the pinned source contains and validates those fields

### Requirement: Executable and transactional maintenance workflow
The comparison-maintenance skill SHALL provide complete quoted commands for scoped workspace setup, canonical clone/fetch, variable assignment, planning, inventory generation, review-mode handling, complete validation, final ref verification, cursor rollback, reporting, and owned cleanup.

#### Scenario: Maintainer follows the skill verbatim
- **WHEN** prerequisites are available and a maintainer executes the documented commands from the repository root
- **THEN** every referenced variable and artifact path is defined before use and the workflow reaches either a validated result or an actionable non-destructive stop

#### Scenario: Branch advances during review
- **WHEN** a final fetch resolves a newer canonical remote head than the reviewed candidate
- **THEN** the workflow preserves the reviewed candidate in the cursor, reports the newer head as pending, and does not record the unreviewed commit

#### Scenario: Post-cursor validation fails
- **WHEN** validation fails after a proposed cursor update
- **THEN** the previous completed cursor is restored and the workflow does not claim completion

### Requirement: Portable regression tests and CI enforcement
Focused comparison-helper tests SHALL be noninteractive, independent of user Git signing/editor/hook configuration, and SHALL run in CI for changes affecting the helper, coverage contract, skill, or comparison content.

#### Scenario: User requires signed commits
- **WHEN** the test process inherits user configuration with commit signing enabled
- **THEN** temporary fixture repositories use isolated test-only Git configuration and the suite completes without a signing prompt

#### Scenario: Regression reaches CI
- **WHEN** comparison maintenance changes are proposed in a pull request
- **THEN** CI runs the focused suite and blocks success on any failed provenance, completeness, workflow, or error-handling case

### Requirement: Minimal rendering configuration
The comparison change SHALL NOT enable site-wide Markdown parser behavior that its content does not require and validate.

#### Scenario: Block attributes are unused
- **WHEN** the comparison pages build and render without Goldmark block-attribute parsing
- **THEN** the global block-attribute setting is absent from the final scoped change
