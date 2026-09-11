## Why

The site currently documents the `evefrontier/world-contracts` `main` branch's assembly-first model without clearly identifying it as v0, while the divergent `dev` branch introduces an incompatible modular architecture that is easy to misread as either a linear upgrade or a complete gameplay port. Developers need a source-pinned, mid-level-friendly comparison that explains both changes and continuities, and maintainers need a repeatable way to keep that comparison accurate as either branch evolves or is rewritten.

## What Changes

- Add a dedicated multi-page World Contracts version-comparison chapter covering architecture, lifecycle, identity and access control, inventory and events, gameplay-domain coverage, extension seams, SDK/deployment/tooling changes, migration implications, continuities, and evidence limitations.
- Label the existing World Contracts landing material as v0/`main` and link prominently to the comparison chapter.
- Pin factual claims to immutable upstream commits while recording the reviewed `main`, `dev`, and merge-base commits in one canonical page's TOML frontmatter.
- Clearly distinguish active v1 implementations, redesigned equivalents, partial representations, archived-only legacy code, absent/not-yet-ported domains, and deployment status.
- Add a repository skill that reviews changes to both divergent branches, updates only verified stale comparison content, handles rewritten history through a controlled full rebaseline, and advances review cursors only after complete validation.
- Add deterministic support and validation for frontmatter parsing, commit ancestry, changed-file coverage, module/domain completeness, immutable evidence links, no-op reviews, and scoped cleanup.

## Capabilities

### New Capabilities

- `world-contracts-version-comparison`: Provides the source-pinned, multi-page v0/`main` versus v1-architecture/`dev` comparison and version-scopes the existing World Contracts documentation.
- `world-contracts-comparison-maintenance`: Provides the reusable skill and deterministic checks for incrementally reviewing, safely rebaselining, validating, and updating the comparison chapter.

### Modified Capabilities

None.

## Impact

- Documentation under `content/develop/world-contracts/`, including its landing page and a new version-comparison chapter.
- A new project skill under `.agents/skills/` and supporting deterministic review/validation tooling.
- Hugo navigation, frontmatter metadata, immutable GitHub evidence links, Mermaid diagrams, and built-site link validation.
- Documentation contributors reviewing the divergent `evefrontier/world-contracts` `main` and `dev` branches.
- No production application API, deployed contract, or runtime behavior is changed by this documentation-focused work.
