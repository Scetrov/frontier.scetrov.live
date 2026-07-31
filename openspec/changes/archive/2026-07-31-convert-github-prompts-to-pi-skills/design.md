## Context

The repository currently stores three reusable workflows as GitHub prompt files: a Sui Move technical deep dive, stale-documentation maintenance, and evidence-backed video summarization. Pi discovers Agent Skills from project `.agents/skills/` directories, while skills.sh distributes skills that follow the same `SKILL.md` convention. The conversion must retain each workflow's useful domain guidance without carrying over GitHub-specific input syntax, absolute workstation paths, or contradictory temporary-directory examples.

## Goals / Non-Goals

**Goals:**

- Provide one portable, standards-compliant skill for each existing prompt.
- Make each skill discoverable and invocable by Pi through accurate metadata.
- Preserve the workflows' outputs, prerequisites, and validation expectations.
- Use repository-relative operations and explicit input/error handling.
- Remove the old prompt files only after replacement skills pass structural and loading checks.

**Non-Goals:**

- Redesign the underlying freshness-check script, Hugo site, or content model.
- Bundle or install external tools such as `gh`, Hugo, Python, or `ffmpeg`.
- Publish the repository to the skills.sh catalog as part of this change.
- Add compatibility shims for GitHub prompt-file invocation.

## Decisions

### Use `.agents/skills/` as the canonical location

Each skill will live at `.agents/skills/<name>/SKILL.md`, with the frontmatter `name` matching its parent directory. This location follows the cross-agent convention and is discovered recursively by Pi, avoiding a Pi-only `.pi/skills/` layout.

Alternative considered: `.pi/skills/`. It is valid for Pi but less portable for skills.sh and other Agent Skills consumers.

### Convert prompts one-to-one

The conversion will create `conduct-deepdive`, `update-stale-documentation`, and `video-summary` skills. Keeping separate skills gives each a precise activation description and prevents unrelated instructions and prerequisites from entering context.

Alternative considered: one combined repository-workflows skill. It would reduce files but weaken progressive disclosure and skill selection.

### Preserve intent while normalizing execution contracts

Each `SKILL.md` will define required user input, prerequisites, ordered steps, outputs, validation, and exceptional conditions. GitHub `${input:...}` syntax will become a plain skill argument/input requirement. Absolute repository paths will become repository-root-relative paths. Temporary work will stay under `./tmp`, and examples will not use shared `/tmp`.

The deep-dive skill will retain Sui Move architecture, lifecycle, Mermaid, and security analysis requirements. The stale-documentation skill will retain freshness checking, source comparison, Hugo validation, and cleanup. The video skill will retain transcript analysis, selective `ffmpeg` screenshots, timestamped reporting, and output under `content/references/`.

Alternative considered: literal file renaming with frontmatter added. That would preserve GitHub-specific assumptions and produce brittle or unsafe skills.

### Keep skill packages instruction-only unless supporting files add value

The initial conversion will place the complete workflow in each `SKILL.md`. No helper scripts will be duplicated because the repository already owns the freshness script and the other workflows primarily orchestrate existing tools. Relative links may point to repository files only when the skill's operation depends on them.

Alternative considered: moving most content into `references/`. The prompts are small enough that this would add navigation without meaningful context savings.

### Validate both structure and Pi usability

Validation will check that every package contains `SKILL.md`; required frontmatter is present; names are lowercase kebab-case, unique, and directory-matched; descriptions state both capability and trigger; referenced repository paths exist; and the files satisfy repository Markdown checks. A Pi smoke check will confirm all three skills are discovered without validation warnings or name collisions.

Old prompt files will be deleted only after these checks succeed and a content-equivalence review confirms that no required workflow was dropped.

## Risks / Trade-offs

- [Skill descriptions are too vague, causing missed or incorrect activation] → Use task-specific descriptions that include concrete trigger phrases and inputs.
- [Prompt behavior is lost during adaptation] → Map every source prompt requirement to a corresponding skill section and review the replacements before deletion.
- [Environment-dependent tools are unavailable] → Declare prerequisites, check them before work, and stop with actionable errors rather than partially producing output.
- [Commands modify or delete unintended paths] → Resolve paths from the repository root, quote user-provided values, keep temporary data under `./tmp`, and scope cleanup narrowly.
- [Pi accepts a construct that another Agent Skills consumer rejects] → Follow the stricter standard, including matching skill and directory names, even where Pi is lenient.

## Migration Plan

1. Create the three `.agents/skills/<name>/SKILL.md` packages alongside the existing prompts.
2. Validate structure, metadata, referenced paths, Markdown, and Pi discovery.
3. Compare each replacement against its source prompt and perform representative smoke checks.
4. Delete the superseded `.github/prompts/*.prompt.md` files.
5. Re-run validation and document the new invocation path if repository documentation needs updating.

Rollback consists of restoring the three prompt files and removing the new skill directories; no application data or runtime migration is involved.

## Open Questions

None. The implementation can use the current three prompt files as the behavioral baseline and the Agent Skills specification plus Pi skill documentation as the format contract.
