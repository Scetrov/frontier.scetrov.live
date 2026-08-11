## 1. Establish the implementation baseline

- [x] 1.1 Confirm the repository worktree state, preserve any unrelated user changes, and inventory the existing World Contracts navigation, frontmatter, validation commands, and reusable skill conventions.
- [x] 1.2 Resolve fresh immutable `evefrontier/world-contracts` `main` and `dev` candidates, their merge base, tags, ancestry, and branch-specific commit ranges; record whether the review is an ordinary initial baseline or requires rebaseline handling.
- [x] 1.3 Generate and review complete active/archive Move-module, changed-file, public-surface, event, test, SDK, manifest, deployment, and operational inventories for the pinned candidates before drafting documentation.

## 2. Build deterministic comparison tooling

- [x] 2.1 Implement a Python helper that parses the canonical comparison TOML with `tomllib` and validates schema, repository, refs, unique cursor location, review status, UTC timestamp, and 40-hex commits.
- [x] 2.2 Implement immutable ref resolution, commit-availability and ancestry checks, ordinary incremental planning, automatic rewritten-history rebaseline planning, merge-base calculation, and final branch-movement detection using fixed subprocess argument arrays.
- [x] 2.3 Implement machine-readable changed-file and active/archive module inventories plus final checks for uncategorized relevant files, missing domain/module coverage, mutable evidence URLs, and invalid cursor advancement.
- [x] 2.4 Add focused standard-library tests for valid and malformed metadata, duplicate cursors, incremental branch movement, non-ancestor rebaseline selection, unavailable current refs, archive exclusion, uncategorized files, and reviewed-candidate cursor validation.

## 3. Add the version-comparison chapter

- [x] 3.1 Create the chapter scaffold and canonical `_index.md` with the actually reviewed immutable candidates, scope and maturity warnings, comparison method, executive summary, navigation, and the single provenance cursor.
- [x] 3.2 Update the existing World Contracts landing page to identify its assembly-first material as v0/`main` and link prominently to the comparison without moving or breaking existing module pages.
- [x] 3.3 Write the architecture and lifecycle page comparing package topology, fixed assemblies, Entity/Module/Action/Request/Requirement flow, initialization, upgrade strategy, retained principles, and developer impact with verified Mermaid diagrams.
- [x] 3.4 Write the exhaustive domain-coverage page classifying every reviewed v0 domain and active v1 module as active, redesigned, partial, archived-only, absent/not-yet-ported, main-only, or deployment-unknown with immutable evidence.
- [x] 3.5 Write the identity and access page covering character representation, deterministic IDs, GovernorCap/AdminACL/OwnerCap versus AdminService/AccessCap requirements, sponsor/caller flows, location proofs, events, continuities, and security-significant caveats.
- [x] 3.6 Write the inventory and events page covering item-layout compatibility, provenance and tenant checks, storage topology, capacities, requirement rules, bridge trust boundaries, public APIs, event/indexer changes, tests, and retained concepts.
- [x] 3.7 Write the developer-experience page covering SDK/PTB builders, environment configuration, MVR and deployment manifests, localnet/accounts/sponsors/resources, Docker, CI, package management, error decoding, and clearly separated branch-maintenance divergence.
- [x] 3.8 Write the migration and evidence pages covering incompatible types and capabilities, extension-seam changes, unimplemented gameplay domains and migration paths, source-versus-deployment authority, upstream documentation contradictions, runtime-validation limits, immutable source links, and practical porting guidance.

## 4. Add the comparison-maintenance skill

- [x] 4.1 Create `.agents/skills/update-world-contracts-version-comparison/SKILL.md` with portable metadata, prerequisites, scoped workspace rules, immutable candidate review, three-way divergent-branch analysis, source-backed update rules, no-op behavior, transactional cursor advancement, validation, reporting, and cleanup.
- [x] 4.2 Document the controlled full-rebaseline workflow for rewritten history, including preservation of the prior cursor, complete claim and coverage re-evaluation, non-destructive failure behavior, and handling of branch movement during review.
- [x] 4.3 Add a workflow-specific completeness reference covering comparison taxonomy, active-versus-archive rules, source/test/manifest/deployment evidence hierarchy, public surface and event checks, changed-file disposition, continuities, migration impact, and residual-uncertainty reporting.
- [x] 4.4 Verify project skill discovery, the absence of a name or trigger collision with `update-stale-documentation`, safe fixed-path/argument handling, and actionable behavior for every prerequisite or validation failure.

## 5. Validate the complete change

- [x] 5.1 Run the helper against the completed chapter and pinned upstream candidates; resolve every missing module/domain row, uncategorized relevant file, mutable factual source link, invalid cursor field, or incomplete-review finding.
- [x] 5.2 Run Hugo build, Markdown lint, Mermaid validation, TOML frontmatter validation, spelling, and built-site link checking, and fix all failures without weakening existing validation.
- [x] 5.3 Review the rendered chapter for navigation, readable mid-level explanations, diagram accuracy, balanced change/continuity treatment, explicit archive and deployment caveats, and stable existing v0 URLs.
- [x] 5.4 Re-fetch upstream refs immediately before finalization; ensure the cursor records only the candidates actually reviewed and report any newer head as pending follow-up work.
- [x] 5.5 Inspect the final diff and confirm it is limited to the agreed comparison chapter, v0 landing-page notice, skill/helper/tests, and directly required validation configuration; report commands, evidence, contradictions, and residual risks.

## Review-integrity reconciliation

The checked baseline tasks are superseded by the fail-closed controls in `harden-world-contracts-comparison-review`. Do not archive this change or represent its cursor as validated until that change's complete validation, focused tests, documentation checks, and final scoped review have all passed.
