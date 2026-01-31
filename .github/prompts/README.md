# Content Creation Prompts

This directory contains focused prompts for creating new chapters and pages in the EVE Frontier documentation site. These prompts help maintain consistency with the site's information architecture.

## Available Prompts

| Prompt | Purpose |
| ------ | ------- |
| [new-top-level-chapter.prompt.md](new-top-level-chapter.prompt.md) | Create a new main navigation section |
| [new-technology-subchapter.prompt.md](new-technology-subchapter.prompt.md) | Create mud/ or sui/ subchapters within existing chapters |
| [new-content-page.prompt.md](new-content-page.prompt.md) | Create general documentation pages |
| [new-getting-started-guide.prompt.md](new-getting-started-guide.prompt.md) | Create beginner-friendly onboarding guides |
| [new-debugging-guide.prompt.md](new-debugging-guide.prompt.md) | Create troubleshooting and error resolution guides |
| [new-vulnerability-page.prompt.md](new-vulnerability-page.prompt.md) | Document Sui Move security vulnerabilities |
| [new-primitive-documentation.prompt.md](new-primitive-documentation.prompt.md) | Document world-contracts primitives |
| [new-jargon-buster-entry.prompt.md](new-jargon-buster-entry.prompt.md) | Add terminology definitions |

## Site Information Architecture

```text
content/
├── _index.md                    # Homepage
├── getting-started/             # Onboarding (weight: 1)
│   ├── mud/                     # MUD-specific getting started
│   ├── sui/                     # Sui-specific getting started
│   └── pods/                    # Provable Object Datatypes
├── develop/                     # Development guides (weight: 2)
│   ├── mud/                     # MUD development
│   ├── sui/                     # Sui development
│   └── world-contracts/         # Core contract documentation
│       └── primitives/          # Layer 1 primitives
├── debugging/                   # Troubleshooting (weight: 3)
│   ├── mud/                     # MUD debugging
│   └── sui/                     # Sui debugging
├── devsecops/                   # Security & Operations (weight: 4)
│   ├── mud/                     # MUD deployment
│   └── sui/                     # Sui security
│       └── vulnerabilities/     # Vulnerability catalog
├── links/                       # External resources
└── references/                  # Reference materials
```

## Content Types

### Chapters (`_index.md`)

- Use `type = "chapter"` in front matter
- Include `{{% children sort="weight" %}}` shortcode
- Set `weight` for navigation ordering

### Documentation Pages (`.md`)

- Use descriptive kebab-case filenames
- Include `date`, `title`, and `weight` in front matter
- Structure with H2/H3 headings

## Technology Context

### MUD (Legacy EVM)

- Solidity smart contracts
- MUD framework (Tables, Systems, World)
- Chains: Redstone, Garnet, Pyrope

### Sui (Current)

- Move smart contracts
- Object-centric programming
- Announced October 2025, active development

## Quick Reference

### Front Matter (TOML)

```toml
+++
date = '2026-01-31T00:00:00Z'
title = 'Page Title'
weight = 10
draft = false
+++
```

### Common Shortcodes

- `{{% children sort="weight" %}}` - List child pages
- `{{% tip-menu-search %}}` - Search tip
- `{{% warning-mud %}}` - MUD deprecation notice

### Callouts

```markdown
> [!IMPORTANT]
> Critical information

> [!NOTE]
> Helpful context

> [!WARNING]
> Danger or pitfall
```
