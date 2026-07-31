## 1. Prepare Skill Packages

- [x] 1.1 Inventory every requirement, prerequisite, input, output, and validation step in the three `.github/prompts/*.prompt.md` files
- [x] 1.2 Create matching `.agents/skills/conduct-deepdive/`, `.agents/skills/update-stale-documentation/`, and `.agents/skills/video-summary/` package directories

## 2. Convert Workflows

- [x] 2.1 Create `conduct-deepdive/SKILL.md` with valid frontmatter, explicit source input handling, and the required Sui Move architecture, lifecycle, logic, security, and Mermaid report contract
- [x] 2.2 Create `update-stale-documentation/SKILL.md` with valid frontmatter, prerequisite and freshness checks, repository-relative commands, `./tmp`-scoped caching, source comparison, and site validation
- [x] 2.3 Create `video-summary/SKILL.md` with valid frontmatter, explicit video input handling, selective `ffmpeg` frame extraction, safe output-path derivation, and the timestamped English report contract
- [x] 2.4 Review all three skills against their source prompts and restore any required behavior omitted during conversion

## 3. Validate Replacements

- [x] 3.1 Validate package structure, directory-matched kebab-case names, required descriptions, uniqueness, and referenced repository paths for all skills
- [x] 3.2 Run repository Markdown checks over the new `SKILL.md` files and correct all actionable failures
- [x] 3.3 Smoke-test Pi project discovery and explicit `/skill:<name>` loading for each converted skill without validation warnings or collisions
- [x] 3.4 Exercise representative valid-input, missing-input, missing-prerequisite, and failed-validation paths and confirm each skill fails safely and reports actionable guidance

## 4. Complete Migration

- [x] 4.1 Remove the three superseded `.github/prompts/*.prompt.md` files only after every replacement check succeeds
- [x] 4.2 Re-run structural, Markdown, and Pi discovery validation after prompt removal
- [x] 4.3 Update repository documentation with the new skill invocation path if no existing documentation makes the converted workflows discoverable
