# Create New Top-Level Chapter

Create a new top-level chapter for the EVE Frontier documentation site.

## Context

This site uses Hugo with the Relearn theme. Top-level chapters appear in the main navigation sidebar and serve as primary content sections. Current chapters include:

- `getting-started/` (weight: 1) - Introduction and onboarding
- `develop/` (weight: 2) - Development guides and references
- `debugging/` (weight: 3) - Troubleshooting and error resolution
- `devsecops/` (weight: 4) - Security, operations, and deployment
- `links/` - External resources and tools
- `references/` - Reference materials like roadmaps

## Instructions

1. Create an `_index.md` file in `content/{chapter-name}/` with:
   - Front matter using TOML (`+++`)
   - `title` - Human-readable chapter name
   - `type = "chapter"`
   - `weight` - Integer for menu ordering (lower = higher in nav)

2. Include:
   - A 1-2 sentence introduction explaining the chapter's purpose
   - The `{{% children sort="weight" %}}` shortcode to list child pages
   - The `{{% tip-menu-search %}}` shortcode for search hints

## Template

```markdown
+++
title = "Chapter Title"
type = "chapter"
weight = 5
+++

Brief introduction explaining what this chapter covers and who it's for.

{{% children sort="weight" %}}

{{% tip-menu-search %}}
```

## Naming Conventions

- Use lowercase kebab-case for directory names (e.g., `advanced-topics/`)
- Keep names concise but descriptive
- Avoid abbreviations unless widely understood (e.g., `devsecops`)

## User Input Required

- **Chapter name**: What should this chapter be called?
- **Purpose**: What content will this chapter contain?
- **Weight**: Where should it appear in navigation order?
- **Technology scope**: Should it have `mud/` and `sui/` subchapters?
