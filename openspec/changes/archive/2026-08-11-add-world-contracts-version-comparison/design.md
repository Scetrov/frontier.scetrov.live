## Context

The current World Contracts chapter at `content/develop/world-contracts/` describes the `evefrontier/world-contracts` `main` branch's assembly-first design as a general overview. The upstream `dev` branch now contains a different, modular architecture based on `core::Entity`, installed modules, named actions, hot-potato requests, and typed requirements. Most v0 code also appears beneath `dev`'s `contracts/archive/`, which can misleadingly suggest that archived gameplay domains are active v1 implementations.

The reviewed upstream snapshots were `main` at `843f706efe74b0c5b818d4282587f4a58893107c`, `dev` at `485740eae181638f494bd574e18a10ba0c991303`, and merge base `db577cf9fd85c2310f6449a1cf42a4a84ba9d20b`. The branches had 16 main-only and 28 dev-only commits, so maintenance must treat them as divergent histories rather than a linear migration range. Implementation must resolve the branch heads again because these snapshots are evidence for the proposal, not permanently fixed targets.

The comparison serves mid-level Move and application developers. It must be readable as narrative guidance while remaining exhaustive enough to account for each gameplay domain, active package, important public surface, trust boundary, event/indexer impact, deployment claim, and operational difference. Documentation maintainers need a repeatable skill that can update this material without silently advancing past unreviewed commits.

## Goals / Non-Goals

**Goals:**

- Add a clearly navigable, multi-page v0/`main` versus v1-architecture/`dev` comparison beneath the existing World Contracts chapter.
- Version-scope the existing World Contracts landing page as v0 and direct readers to the comparison.
- Explain changes and continuities together, with practical developer and migration impact.
- Distinguish active v1 code, redesigned equivalents, partial representations, archived-only legacy code, absent/not-yet-ported domains, and separately evidenced deployment status.
- Ground factual claims in immutable upstream commit URLs and record one canonical pair of reviewed branch commits.
- Provide a repository skill and deterministic helper that support incremental reviews and automatic, controlled full rebaselines after rewritten history.
- Prevent review cursors from advancing after partial analysis, unresolved errors, or failed validation.

**Non-Goals:**

- Change, deploy, or validate the upstream Move contracts themselves.
- Claim that either upstream branch is production-ready or currently active in game.
- Rewrite every existing v0 module deep dive as part of the comparison.
- Produce a raw dump of every ABI symbol without explanatory context.
- Infer runtime deployment from source presence alone.
- Automatically commit, push, or publish documentation changes.

## Decisions

### Use a nested multi-page chapter and version-scope the existing landing page

Create `content/develop/world-contracts/version-comparison/` with an `_index.md` landing page and focused child pages for architecture, domain coverage, identity/access, inventory/events, developer experience, migration, and evidence. Update `content/develop/world-contracts/_index.md` with an explicit v0/`main` scope notice and a prominent link.

A single long page was rejected because it would mix architectural explanation, an exhaustive coverage matrix, operational divergence, and source evidence into an unmaintainable document. Replacing the existing World Contracts landing route was rejected because the detailed v0 pages remain useful and already have stable URLs.

### Keep one canonical provenance cursor

The comparison chapter `_index.md` SHALL be the only page containing the review cursor:

```toml
comparison_schema = 1
upstream_repository = "evefrontier/world-contracts"
comparison_mode = "tip-to-tip"
v0_ref = "main"
v0_reviewed_commit = "<40-hex SHA>"
v1_ref = "dev"
v1_reviewed_commit = "<40-hex SHA>"
merge_base_commit = "<40-hex SHA>"
reviewed_at = "<UTC ISO-8601>"
review_status = "complete"
```

Child pages shall link back to the canonical scope instead of duplicating cursors. Per-page commit fields were rejected because they allow pages to drift to inconsistent snapshots. Date-only freshness was rejected because it cannot represent divergent refs, ancestry, force-pushes, or the exact reviewed tree.

The normal page `date` changes only when reader-facing content changes. `reviewed_at` and commit cursors may advance after a complete review that finds no narrative change.

### Compare three relationships, not one diff

Each maintenance run SHALL inspect:

1. recorded v0 commit to the pinned current `main` candidate;
2. recorded v1 commit to the pinned current `dev` candidate; and
3. the pinned current `main` and `dev` candidates tip-to-tip, including their merge base.

This prevents main-only fixes or new v0 behavior from being omitted merely because the user-facing workflow is described as reviewing `dev`. A simple `main..dev` review was rejected because it conflates divergent branch maintenance with v1 architectural work.

### Use an explicit comparison taxonomy

The coverage matrix and narrative shall use these states consistently:

- **Active v1 implementation**
- **Redesigned equivalent**
- **Partially represented**
- **Archived legacy only**
- **No active v1 equivalent / not yet ported**
- **Active only on v0/main**
- **Deployment unknown or separately evidenced**

Generic platform support must not be treated as proof that a gameplay domain was ported. Archived code must not be described as active, supported, compatible, or deployed.

### Pair every difference with continuity and impact

Narrative pages shall compare v0 behavior, v1 behavior, what changed, what remains, developer impact, maturity/deployment status, and immutable evidence. A single isolated “unchanged” appendix was rejected because it would make the main comparison change-biased and force readers to reconcile separate claims.

### Separate architectural migration from branch maintenance

Contract/package/API changes belong in the main comparison. SDK, MVR, deployment, localnet, Docker, CI, package-manager, and error-decoder differences also belong in the chapter, but main-only or dev-only maintenance that is not architecturally required must be labelled as branch divergence. This avoids presenting every missed cherry-pick as an intentional v1 design decision.

### Treat source, tests, and deployment evidence as different authorities

Pinned source and tests establish implemented behavior. Manifests and deployment artifacts establish only what they explicitly contain. Upstream prose is supporting context and may be stale. The documentation shall identify contradictions rather than silently choosing the most convenient source, and shall distinguish implementation from confirmed deployment.

### Provide a specific reusable skill with deterministic support

Add `.agents/skills/update-world-contracts-version-comparison/SKILL.md`, a workflow-specific completeness reference, and a deterministic Python helper under `scripts/`. The helper shall use `tomllib`, fixed argument arrays for subprocesses, and a repository-scoped work directory under `./tmp/update-world-contracts-version-comparison/`.

The helper's responsibilities include validating frontmatter, resolving immutable refs, checking commit availability and ancestry, selecting incremental versus rebaseline mode, producing changed-file and active-module inventories, detecting uncategorized coverage, and validating the final cursor/evidence contract. Human-readable source interpretation and prose updates remain skill responsibilities.

A prose-only skill was rejected because branch ancestry, cursor correctness, complete file accounting, and frontmatter validation are deterministic concerns that should be repeatable and testable.

### Handle rewritten history with an automatic controlled rebaseline

If a recorded commit is no longer an ancestor of its declared branch, the skill shall preserve the existing cursor, report the rewrite, and switch to full rebaseline mode. It shall rebuild inventories from both pinned current trees, re-evaluate every coverage row and factual claim, regenerate tip-to-tip evidence, and advance the cursor only after the same full validation required for an ordinary review.

If the recorded commit remains retrievable, it may be used as additional historical context but not as a valid incremental range. If current refs cannot be resolved, repository identity changes, or source evidence is unavailable, the skill stops without changing the cursor. Treating non-ancestry as an ordinary incremental diff was rejected because it can silently omit rewritten changes; always requiring manual approval was rejected because rewritten development history should be recoverable by the defined full rebaseline.

### Review immutable candidates even if branch heads move

Resolve and pin candidate SHAs at the start. Re-fetch before finalization. If a branch advanced during the review, record only the candidate actually reviewed and report the newer head as pending work for the next run. Never record an unreviewed SHA. Restarting indefinitely on a busy development branch was rejected because it can prevent useful progress; silently advancing to the latest head was rejected as dishonest.

### Make cursor advancement transactional

The old canonical cursor remains intact during research and drafting. After content, completeness, and site checks pass, update the cursor to the reviewed candidates and run the cursor/frontmatter and site checks again. If validation then fails, restore the previous cursor and do not claim completion. Reader-facing edits may remain for diagnosis, but they are not represented as a completed review.

### Validate both content quality and review completeness

Validation shall cover Hugo, Markdown, Mermaid, TOML frontmatter, spelling, and built-site links. It shall also verify 40-hex commits, declared refs, canonical cursor uniqueness, immutable evidence URLs, active package/module accounting, domain-matrix accounting, changed-file classification, and no cursor advancement on errors. The final diff must be restricted to the comparison chapter, the agreed v0 landing-page notice, the new skill/helper/tests, and directly required validation configuration.

## Risks / Trade-offs

- **[Mutable upstream development]** The comparison can become stale immediately after review → Pin immutable candidates, expose reviewed commits, and report newer heads as pending.
- **[“Comprehensive” becomes unreadable]** Exhaustive detail can overwhelm a mid-level reader → Split narrative pages by concern and place dense source accounting in the coverage/evidence pages.
- **[Archive mistaken for active functionality]** Retained v0 files can appear to be v1 coverage → Use the explicit taxonomy and exclude `contracts/archive/` from active-module inventories.
- **[Source mistaken for deployment]** Active packages may not be published in every environment → Keep implementation and deployment evidence in separate fields and prose.
- **[Rewritten history loses incremental context]** Non-ancestor cursors invalidate ordinary ranges → Automatically perform a complete rebaseline while preserving the old cursor until success.
- **[Automated checks imply semantic correctness]** A helper can account for files but cannot fully understand behavior → Keep source interpretation in the skill and require immutable evidence for narrative claims.
- **[Existing v0 pages remain misleading]** A new chapter alone does not scope the current landing page → Add an explicit v0 notice and comparison link to the existing landing page.
- **[Toolchain mismatch blocks local upstream execution]** Upstream Move packages may require a different Sui version → Report unexecuted validation and do not convert source analysis into runtime claims.

## Migration Plan

1. Resolve fresh immutable `main` and `dev` candidates and generate the initial full comparison inventory.
2. Add the comparison chapter and canonical cursor using the actually reviewed candidates.
3. Add the v0 scope notice and chapter link without changing existing v0 page URLs.
4. Add the skill, deterministic helper, completeness reference, and focused tests.
5. Run completeness checks and the repository's full documentation validation surface.
6. Review the rendered chapter and final scoped diff.

Rollback is documentation-only: remove the new chapter and skill/helper changes and restore the previous World Contracts landing page. No upstream or deployed state is migrated.

## Open Questions

No blocking product decisions remain. Implementation must re-resolve upstream branch heads and may adjust page weights or filenames to fit the existing Hugo navigation without changing the agreed chapter structure.
