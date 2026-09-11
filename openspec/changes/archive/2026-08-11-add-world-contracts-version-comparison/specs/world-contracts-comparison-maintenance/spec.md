## ADDED Requirements

### Requirement: Discoverable comparison-maintenance skill
The repository SHALL provide a standards-compliant Agent Skills package named `update-world-contracts-version-comparison` whose description identifies both incremental dev review and full comparison refresh use cases.

#### Scenario: Pi discovers project skills
- **WHEN** Pi starts in the trusted repository with project skill discovery enabled
- **THEN** the comparison-maintenance skill is available without an invalid name, missing description, or collision with the general stale-documentation skill

#### Scenario: User requests a comparison refresh
- **WHEN** a user asks to review new `dev` changes or update the v0/v1 World Contracts comparison
- **THEN** the skill loads the comparison-specific workflow rather than relying on date-only documentation freshness

### Requirement: Safe prerequisites and scoped workspace
The skill SHALL verify required commands, repository paths, upstream access, canonical comparison metadata, and target-file state before editing. Clones, inventories, and reports SHALL use a workflow-specific directory beneath `./tmp/update-world-contracts-version-comparison/` and SHALL be cleaned without touching unrelated temporary data.

#### Scenario: A prerequisite is unavailable
- **WHEN** Git, Python, required repository files, upstream access, or a validation command required for safe completion is unavailable
- **THEN** the skill reports an actionable failure and does not make partial documentation edits or advance review cursors

#### Scenario: Temporary review data is needed
- **WHEN** the skill clones upstream history or generates intermediate reports
- **THEN** it uses only its repository-scoped workflow directory and removes only data owned by that workflow during cleanup

#### Scenario: Target comparison files already contain unrelated edits
- **WHEN** the skill detects pre-existing changes that could be overwritten or confused with its update
- **THEN** it stops or requests an explicit scope decision before editing those files

### Requirement: Deterministic canonical metadata validation
A deterministic helper SHALL parse canonical TOML with `tomllib` and SHALL validate the comparison schema, repository identity, declared refs, unique cursor location, complete review status, UTC review timestamp, and 40-hex reviewed and merge-base commits.

#### Scenario: Canonical metadata is valid
- **WHEN** the helper reads the comparison chapter's canonical page
- **THEN** it returns a structured baseline containing the exact repository, refs, reviewed commits, merge base, and review status

#### Scenario: Metadata is malformed or duplicated
- **WHEN** a required field is invalid or review cursor fields appear on more than one comparison page
- **THEN** validation fails before upstream analysis or cursor modification

### Requirement: Immutable candidate resolution
The maintenance workflow SHALL resolve and pin immutable candidate commits for both declared refs at the start of each review and SHALL analyze only those candidates. It SHALL re-fetch refs before finalization and SHALL never record a commit that was not reviewed.

#### Scenario: Branch heads remain stable
- **WHEN** final ref resolution matches the pinned candidates
- **THEN** a successful review may record those candidate commits

#### Scenario: A branch advances during review
- **WHEN** final ref resolution finds a newer head than the pinned candidate
- **THEN** the workflow records at most the reviewed candidate, reports the newer commit as pending, and leaves it for a subsequent review

### Requirement: Divergent-branch review
For an ordinary update, the workflow SHALL review recorded v0 to candidate `main`, recorded v1 to candidate `dev`, and candidate `main` versus candidate `dev` tip-to-tip, including the current merge base.

#### Scenario: Only dev changed
- **WHEN** `dev` advances while `main` remains at its recorded commit
- **THEN** the workflow reviews the dev range and recomputes tip-to-tip conclusions without incorrectly advancing or changing v0 evidence

#### Scenario: Main changes independently
- **WHEN** `main` advances while `dev` does not
- **THEN** the workflow reviews the main range and updates affected v0/v1 conclusions even though no new dev commit exists

#### Scenario: Both branches changed
- **WHEN** both refs advance
- **THEN** the workflow analyzes each branch-specific range and the resulting tip-to-tip comparison without conflating the three relationships

### Requirement: Graceful rewritten-history rebaseline
If a recorded reviewed commit is not an ancestor of its declared current ref, the workflow SHALL automatically enter controlled full-rebaseline mode. It SHALL preserve the previous cursor until success, report the rewrite, rebuild both source inventories, re-evaluate every comparison claim and coverage row, and apply the same validation and cursor rules as an initial full review.

#### Scenario: Dev history is force-pushed
- **WHEN** the recorded v1 commit is no longer an ancestor of the pinned `dev` candidate
- **THEN** the workflow performs a full rebaseline rather than treating the rewritten history as an ordinary incremental range

#### Scenario: Recorded commit remains retrievable
- **WHEN** a rewritten branch no longer contains the recorded commit but the commit can still be fetched
- **THEN** the workflow may use it as historical context but does not treat it as a valid incremental base

#### Scenario: Current source cannot be resolved safely
- **WHEN** current refs are unavailable, repository identity changed, or required current source cannot be obtained
- **THEN** the workflow stops non-destructively and retains the last completed cursor

### Requirement: Exhaustive review inventory
The deterministic helper and skill SHALL account for changed files, active Move packages and modules, archived modules, public and package-visible functions, structs and abilities, events, abort conditions, tests, manifests, SDK surfaces, deployment artifacts, and operational tooling relevant to the comparison. Every v0 domain and active v1 module SHALL map to a documented coverage state.

#### Scenario: A changed file has no documented category
- **WHEN** the generated review inventory contains an uncategorized relevant file or module
- **THEN** the workflow treats the review as incomplete and does not advance the cursor

#### Scenario: Archived source is inventoried
- **WHEN** a legacy module exists beneath `contracts/archive/`
- **THEN** the inventory records it separately from active v1 packages and prevents it from satisfying active-module coverage

#### Scenario: Generic support exists without a domain implementation
- **WHEN** v1 platform primitives could support a gameplay domain but no active domain module exists
- **THEN** completeness validation requires an explicit partial or not-yet-ported classification rather than a ported classification

### Requirement: Source-backed scoped updates
The skill SHALL update only claims proven stale by pinned source, tests, manifests, deployment evidence, or branch history. It SHALL preserve explicit facts, inferences, contradictions, and unknowns as distinct categories and SHALL use immutable evidence links.

#### Scenario: Review finds a substantive behavior change
- **WHEN** pinned evidence changes a documented API, lifecycle, trust boundary, event, domain status, deployment claim, or developer workflow
- **THEN** the affected comparison pages, cross-references, diagrams, and migration guidance are updated consistently

#### Scenario: Review finds no narrative change
- **WHEN** branch commits were completely reviewed but do not change reader-facing conclusions
- **THEN** the workflow may advance the reviewed cursors and `reviewed_at` without changing the page `date`

#### Scenario: No branch has advanced
- **WHEN** both resolved heads equal their recorded reviewed commits and metadata is valid
- **THEN** the workflow makes no documentation edits and reports a no-op result

### Requirement: Transactional cursor advancement
The workflow SHALL retain the previous completed cursor throughout research and drafting. It SHALL advance the cursor only after content, completeness, and repository validation pass, and SHALL restore the previous cursor if post-update validation fails.

#### Scenario: Content validation fails
- **WHEN** any required documentation or completeness check fails
- **THEN** the workflow reports the failure, does not claim completion, and does not leave the canonical cursor advanced

#### Scenario: Review is interrupted or partial
- **WHEN** analysis stops before all relevant files, modules, domain rows, and contradictions are dispositioned
- **THEN** the last completed cursor remains authoritative

#### Scenario: Full review succeeds
- **WHEN** all relevant evidence is accounted for and all validation passes
- **THEN** the canonical cursor records exactly the pinned candidates that were reviewed and sets a completed UTC review time

### Requirement: Complete validation and reporting
Before reporting success, the workflow SHALL run deterministic comparison validation plus Hugo build, Markdown lint, Mermaid validation, TOML frontmatter validation, spelling, built-site link checking, and a scoped final diff review. The completion report SHALL identify review mode, old and new cursors, branch movement detected during review, changed pages, commands and outcomes, contradictions, and residual uncertainties.

#### Scenario: Validation succeeds
- **WHEN** an incremental review or full rebaseline completes without unresolved findings
- **THEN** the workflow reports the exact reviewed snapshots, affected files, successful checks, and any newer pending branch heads

#### Scenario: Validation fails
- **WHEN** any required check returns an error
- **THEN** the workflow identifies the failing command and relevant output and does not claim that the comparison is current

#### Scenario: Final diff exceeds agreed scope
- **WHEN** final review finds changes outside the comparison chapter, v0 landing-page notice, skill/helper/tests, or directly required validation configuration
- **THEN** the workflow explains and obtains approval for the extra scope or removes it before completion
