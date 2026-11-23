+++
title = "Developer experience and operations"
weight = 50
+++

v0 exposes direct, domain-specific TypeScript scripts around the `world` package. v1 adds [`world-sdk`](https://github.com/evefrontier/world-contracts/tree/acb0a16cd4b754bd9c41c058007932f131a7f258/sdk/world-sdk), whose PTB builders resolve MVR package names or local overrides and compose Entity creation, cap verification, actions, requests, identity, inventory, metadata, generic components, currency, creation layouts, killmails, and power grids. Components use numeric IDs; names are optional display labels. Applications build modular request flows rather than calling a fixed assembly API.

[`package.json`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/package.json) excludes archive packages from active Move build/lint/test and adds SDK checks. Its pnpm version, Biome/Husky choices, workflow triggers, and cache mechanics are branch-maintenance divergence unless a consumer relies on them.

The [`Docker documentation`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/docker/README.md) describes localnet and test tooling, not production or in-game deployment. The [`dev` manifest](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/deployments/dev/world.json) lists package and MVR entries for all nine active packages. [`live`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/deployments/live/world.json) records only MVR app capabilities; test and UAT manifests likewise provide environment-specific facts, not proof of currently deployed code.

The [error-decoder README](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/tools/error-decoder/README.md) still refers to the moved `contracts/world` path, a source/prose contradiction that should be resolved before claiming active v1 decoder coverage.
