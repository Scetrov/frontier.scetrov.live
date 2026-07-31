## Why

The reusable workflows in `.github/prompts/` are tied to GitHub prompt-file conventions, so Pi cannot discover and load them through its project skill mechanism. Converting them to the Agent Skills format used by skills.sh will make the workflows portable, progressively discoverable, and directly usable by Pi while preserving their intent.

## What Changes

- Replace each existing `.github/prompts/*.prompt.md` workflow with a dedicated portable project skill under `.agents/skills/<skill-name>/SKILL.md`, a location Pi discovers natively.
- Add standards-compliant skill metadata and task-focused descriptions so Pi can discover each skill automatically.
- Adapt prompt-specific inputs, fixed local paths, tool assumptions, and unsafe temporary-directory examples into portable Pi skill instructions.
- Preserve the deep-dive, stale-documentation, and video-summary workflows while making required inputs, outputs, validation, and failure handling explicit.
- Validate every converted skill against Agent Skills/skills.sh structural rules and Pi's skill loader.
- Remove the superseded GitHub prompt files after equivalent skills are available.

## Capabilities

### New Capabilities
- `reusable-pi-skills`: Standards-compliant, Pi-discoverable skills that provide the existing deep-dive, stale-documentation, and video-summary workflows.

### Modified Capabilities

None.

## Impact

- Affects `.github/prompts/` and introduces project-local skill packages under `.agents/skills/`.
- Changes how contributors invoke reusable workflows: Pi skill discovery or `/skill:<name>` replaces GitHub prompt-file invocation.
- Adds no runtime application dependency, but the skills retain documented tool prerequisites such as `gh`, Python, Hugo, and `ffmpeg` where applicable.
- Requires validation of frontmatter, directory naming, relative paths, and instructions against both the Agent Skills standard and Pi behavior.
