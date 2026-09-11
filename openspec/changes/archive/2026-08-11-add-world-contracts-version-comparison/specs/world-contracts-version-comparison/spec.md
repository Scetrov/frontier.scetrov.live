## ADDED Requirements

### Requirement: Version-scoped World Contracts navigation
The documentation site SHALL provide a dedicated multi-page chapter comparing v0/`main` with the v1 architecture on `dev`, and SHALL explicitly identify the existing World Contracts landing material and detailed module pages as v0/`main` documentation.

#### Scenario: Reader enters the World Contracts chapter
- **WHEN** a reader opens the existing World Contracts landing page
- **THEN** the page identifies its assembly-first material as v0/`main` and provides a prominent link to the version-comparison chapter

#### Scenario: Reader opens the comparison chapter
- **WHEN** a reader opens the version-comparison chapter
- **THEN** focused child pages are available for architecture, domain coverage, identity and access, inventory and events, developer experience, migration, and source evidence

### Requirement: Immutable comparison provenance
The comparison SHALL identify the exact upstream repository, reviewed `main` commit, reviewed `dev` commit, merge-base commit, comparison mode, completion status, and review time in one canonical TOML frontmatter block. Factual source links SHALL use immutable commit URLs rather than mutable branch URLs.

#### Scenario: Comparison provenance is inspected
- **WHEN** a maintainer or reader inspects the comparison chapter's canonical page
- **THEN** they can determine exactly which immutable v0 and v1 source trees were reviewed

#### Scenario: A factual claim cites upstream code
- **WHEN** a comparison page links to evidence for a behavior, type, function, event, test, manifest, or deployment artifact
- **THEN** the link identifies the reviewed commit rather than resolving through mutable `main` or `dev`

### Requirement: Honest version and maturity framing
The comparison SHALL explain that v0/`main` and v1-architecture/`dev` are documentation labels for divergent development branches, not a linear changelog or proof of semantic-version 1.0, production readiness, in-game activation, or environment deployment.

#### Scenario: Branch relationship is explained
- **WHEN** a reader reviews the comparison scope
- **THEN** the documentation states that `main` and `dev` diverged and separates tip-to-tip differences from branch-specific maintenance

#### Scenario: Source exists without deployment evidence
- **WHEN** an active v1 package is present in source but reviewed deployment artifacts do not establish that it is published in an environment
- **THEN** the documentation labels implementation and deployment status separately and preserves the deployment uncertainty

### Requirement: Comprehensive comparison taxonomy
The comparison SHALL account for each reviewed v0 gameplay domain and each active v1 package or module using the states active v1 implementation, redesigned equivalent, partially represented, archived legacy only, no active v1 equivalent/not yet ported, active only on v0/main, or deployment unknown/separately evidenced.

#### Scenario: Legacy source is retained under archive
- **WHEN** a v0 module exists only beneath the reviewed dev tree's archive
- **THEN** the coverage matrix identifies it as archived legacy and does not describe it as active, supported, compatible, deployed, or ported

#### Scenario: A generic platform primitive could support a domain
- **WHEN** v1 contains a generic Entity, Module, Action, or Requirement abstraction but no active implementation of a v0 gameplay domain
- **THEN** the documentation does not claim that the gameplay domain has been ported

#### Scenario: A domain is only partially represented
- **WHEN** v1 provides some behavior associated with a v0 domain but not its concrete type, lifecycle, API, or security checks
- **THEN** the domain is classified as partially represented and the missing behavior is described

### Requirement: Changes, continuities, and developer impact
Each substantive comparison topic SHALL explain v0 behavior, v1 behavior, what changed, what remains conceptually or operationally consistent, and the practical impact on Move developers, SDK users, indexers, or operators.

#### Scenario: Architecture is compared
- **WHEN** the chapter explains the move from fixed assemblies to Entity modules and request requirements
- **THEN** it also identifies retained principles such as Sui Move execution, shared objects, deterministic identity, tenant partitioning, on-chain rule enforcement, and atomic transactions where supported by source

#### Scenario: A security boundary changes
- **WHEN** the chapter compares capabilities, sponsors, owners, callers, location proofs, bridge authorization, or module access
- **THEN** it describes the observed validation and trust-boundary difference without making unsupported security-quality claims

### Requirement: Domain and integration detail
The chapter SHALL cover package topology, object and lifecycle models, identity and deterministic IDs, authorization and capabilities, location handling, item and inventory semantics, event/indexer impact, extension seams, gameplay-domain coverage, SDK/PTB integration, MVR and deployment artifacts, localnet and Docker behavior, CI/tooling divergence, and migration compatibility.

#### Scenario: Inventory behavior is compared
- **WHEN** a reader consults the inventory and events page
- **THEN** it explains item-layout compatibility, storage topology, capacities, requirement-based rules, authorization differences, and event-field/indexer consequences

#### Scenario: Developer tooling is compared
- **WHEN** a reader consults the developer-experience page
- **THEN** architectural SDK and deployment changes are distinguished from unrelated main-only or dev-only maintenance differences

#### Scenario: Migration guidance is consulted
- **WHEN** a developer plans to port a v0 integration or extension
- **THEN** the chapter identifies incompatible package/type identities, capability models, object layouts, event contracts, extension seams, and any unimplemented migration path

### Requirement: Evidence hierarchy and caveats
The comparison SHALL treat pinned source and tests as implementation evidence, manifests and deployment artifacts as limited operational evidence, and upstream prose as contextual evidence that may be stale. Contradictions and unverified runtime behavior SHALL be disclosed.

#### Scenario: Upstream prose contradicts active source
- **WHEN** upstream documentation labels a module as planned but the pinned source contains an active implementation and tests
- **THEN** the comparison reports the contradiction and grounds its implementation claim in the pinned source

#### Scenario: Runtime validation is unavailable
- **WHEN** the reviewed upstream packages cannot be executed with the available compatible toolchain
- **THEN** the chapter identifies the validation limitation and does not present source review as runtime verification

### Requirement: Rendered documentation quality
The chapter SHALL use valid Hugo frontmatter and links, lint-clean Markdown, renderable Mermaid diagrams, repository spelling conventions, and stable existing v0 URLs.

#### Scenario: Documentation validation runs
- **WHEN** the comparison chapter and v0 scope notice are complete
- **THEN** Hugo build, Markdown lint, Mermaid validation, frontmatter validation, spelling, and built-site link checks pass

#### Scenario: Existing v0 documentation is linked externally
- **WHEN** the new chapter is introduced
- **THEN** existing v0 module page URLs remain available and the change adds version context rather than relocating those pages
