+++
title = "Developer experience and operations"
weight = 50
+++

v0 exposes direct, domain-specific TypeScript scripts around the `world` package. v1 adds [`world-sdk`](https://github.com/evefrontier/world-contracts/tree/485740eae181638f494bd574e18a10ba0c991303/sdk/world-sdk), whose PTB builders resolve MVR package names or local overrides and compose Entity creation, cap verification, actions, requests, identity, and inventory. That is an architectural integration change: applications build modular request flows.

[`package.json`](https://github.com/evefrontier/world-contracts/blob/485740eae181638f494bd574e18a10ba0c991303/package.json) excludes archive packages from active Move build/lint/test and adds SDK checks. Its pnpm version, Biome/Husky choices, workflow triggers, and cache mechanics are branch-maintenance divergence unless a consumer relies on them.

The [`Docker documentation`](https://github.com/evefrontier/world-contracts/blob/485740eae181638f494bd574e18a10ba0c991303/docker/README.md) describes localnet, deterministic test accounts, snapshots, and integration images. This supports local development; it is not production or in-game deployment evidence. The reviewed dev manifest names core and character artifacts but not inventory. The error-decoder README still refers to the moved `contracts/world` path, a source/prose contradiction that should be resolved before claiming active v1 decoder coverage.
