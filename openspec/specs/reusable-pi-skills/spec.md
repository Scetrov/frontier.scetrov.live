# reusable-pi-skills Specification

## Purpose
TBD - created by archiving change convert-github-prompts-to-pi-skills. Update Purpose after archive.
## Requirements
### Requirement: Standards-compliant skill packages
The repository SHALL provide one Agent Skills package for each workflow currently represented by a file in `.github/prompts/`. Each package SHALL be located at `.agents/skills/<skill-name>/SKILL.md`, and its frontmatter name SHALL be valid lowercase kebab-case and match the package directory.

#### Scenario: All prompt workflows have skill packages
- **WHEN** the repository skill directories are enumerated after conversion
- **THEN** packages named `conduct-deepdive`, `update-stale-documentation`, and `video-summary` are present with a `SKILL.md` entry file

#### Scenario: Skill metadata is portable
- **WHEN** a converted `SKILL.md` is validated against the Agent Skills frontmatter rules
- **THEN** it contains a valid `name` and a non-empty task-specific `description` without relying on Pi-only metadata

### Requirement: Pi discovery and invocation
Each converted skill SHALL be discoverable by Pi from the project skill location, and its description SHALL identify what the skill does and the situations in which Pi should load it.

#### Scenario: Pi discovers converted skills
- **WHEN** Pi starts in the trusted repository with project skill discovery enabled
- **THEN** all three converted skills are available without missing-description errors or name collisions

#### Scenario: User explicitly invokes a skill
- **WHEN** a user invokes `/skill:<skill-name>` with the input required by that workflow
- **THEN** Pi loads the corresponding instructions and applies the supplied input to the workflow

### Requirement: Technical deep-dive workflow
The `conduct-deepdive` skill SHALL accept one or more source files or URLs and direct Pi to produce a concise Sui Move technical report covering learning objectives, component architecture, lifecycle, core logic, security and access patterns, and relevant visual diagrams.

#### Scenario: Deep dive receives valid sources
- **WHEN** a user requests a deep dive and supplies accessible Sui Move source files or URLs
- **THEN** the generated report includes the required architectural, lifecycle, logic, security, and Mermaid sections supported by the supplied source

#### Scenario: Deep dive lacks source input
- **WHEN** the skill is invoked without a source file or URL
- **THEN** Pi requests the missing source rather than analyzing an unrelated default URL

### Requirement: Stale-documentation workflow
The `update-stale-documentation` skill SHALL guide Pi through prerequisite checks, the repository freshness report, source comparison, scoped documentation updates, site validation, and cleanup using repository-relative paths.

#### Scenario: Documentation is stale
- **WHEN** the freshness report identifies one or more stale pages
- **THEN** Pi compares each page with its current upstream source, updates only verified stale content and metadata, and validates the resulting documentation and diagrams

#### Scenario: Documentation is already fresh
- **WHEN** the freshness check reports no stale pages
- **THEN** Pi makes no documentation edits and reports that no update is required

#### Scenario: Temporary repository data is needed
- **WHEN** upstream repositories or intermediate reports must be cached
- **THEN** the workflow uses a scoped path beneath the repository's `./tmp` directory and never instructs Pi to use shared `/tmp`

### Requirement: Video-summary workflow
The `video-summary` skill SHALL accept a video input, synthesize its transcript and visuals, selectively extract informative PNG frames with `ffmpeg`, and write an English Markdown report beneath `content/references/` using a path derived safely from the video filename.

#### Scenario: Video contains informative visuals
- **WHEN** a supplied video contains slides, diagrams, charts, code, or other information-bearing frames
- **THEN** the report embeds selectively extracted screenshots with descriptive filenames and corresponding timestamps in the topics section

#### Scenario: Video has no useful visual evidence
- **WHEN** the video contains no unique information-bearing visuals beyond talking-head footage
- **THEN** the report omits screenshots rather than capturing low-value images

#### Scenario: Output path is derived from untrusted filename text
- **WHEN** the skill derives an output directory from the video filename
- **THEN** it sanitizes the derived name and keeps all output within `content/references/`

### Requirement: Safe and explicit execution
Converted skills SHALL state required inputs and tool prerequisites, use repository-relative paths, quote variable inputs in command examples, and define actionable behavior for unavailable tools, inaccessible inputs, and failed validation.

#### Scenario: Required prerequisite is unavailable
- **WHEN** a workflow requires a command that is not installed or authenticated
- **THEN** Pi stops before dependent actions and reports the prerequisite and a safe remediation step

#### Scenario: A validation command fails
- **WHEN** Markdown, Mermaid, Hugo, skill-structure, or Pi-discovery validation fails
- **THEN** Pi reports the failing check and does not claim successful completion or remove the only working workflow representation

### Requirement: Superseded prompt removal
The original `.github/prompts/*.prompt.md` files SHALL be removed only after all corresponding skills have passed structural validation, Pi discovery checks, and a workflow-equivalence review.

#### Scenario: Replacements pass validation
- **WHEN** every converted skill passes all required checks and covers its source prompt's required behavior
- **THEN** the three superseded prompt files are removed from `.github/prompts/`

#### Scenario: A replacement is incomplete
- **WHEN** any converted skill fails validation or omits required source behavior
- **THEN** its source prompt remains present until the replacement is corrected
