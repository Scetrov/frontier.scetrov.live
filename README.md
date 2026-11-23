# Readme

This repository represents my notes from nearly two years of learning about [EVE Frontier](https://evefrontier.com/en) and Sui. In February 2026 I removed all of the content about Mud and Solidity given Fenris’s move to the Sui Blockchain. I publish it here under a Creative Commons (CC BY-NC-SA 4.0) License in the hope that new developers can get up to speed with developing for this game as quickly as possible.

## Reusable Pi Skills

Pi discovers the project skills in `.agents/skills/` after the repository is trusted. Invoke them explicitly when needed:

- `/skill:conduct-deepdive <Sui Move file or URL> [additional sources...]`
- `/skill:update-stale-documentation`
- `/skill:video-summary <local video path or video URL>`

Each skill checks its required inputs and tool prerequisites before making changes.

## Typography

Body text uses self-hosted [Source Sans 3 (3.052R)](https://github.com/adobe-fonts/source-sans/releases/tag/3.052R) under the [SIL Open Font License 1.1](static/fonts/source-sans-3/OFL.txt).

The site uses [Confinium Mono v0.2.1](https://github.com/Scetrov/confinium-mono/releases/tag/0.2.1) under the [SIL Open Font License 1.1](static/fonts/confinium-mono/OFL.txt). The variable webfont is self-hosted, and Hugo uses Full Grid Bold to render social preview images.

## Contributing

I am happy to accept pull requests to this repository under the same CC BY-NC-SA 4.0 license. Install the project’s pinned Hugo version with `mise install hugo`, then preview the site with `mise exec hugo -- hugo server`. If you don’t use mise, [install the version pinned in `mise.toml`](https://gohugo.io/installation/) and run `hugo server`.
