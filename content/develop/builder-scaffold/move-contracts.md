+++
date = '2026-02-28T12:00:00Z'
title = 'Move Contracts'
weight = 8
description = "Building, testing, and publishing custom Move extension contracts with builder-scaffold — smart gates, storage units, and more."
+++

The `move-contracts/` directory contains custom Smart Assembly extension examples. You build contracts here that change the default behavior of programmable assemblies by defining a typed witness struct and calling the extendable world functions.

<!--more-->

---

## Extension Examples

| Package | Purpose |
|---------|---------|
| [`smart_gate`](https://github.com/evefrontier/builder-scaffold/tree/main/move-contracts/smart_gate) | Custom rules for space travel — toll gates, tribe-only access, corpse bounty collection. Issues `JumpPermit`s based on arbitrary logic. |
| [`storage_unit`](https://github.com/evefrontier/builder-scaffold/tree/main/move-contracts/storage_unit) | Custom rules for item deposits and withdrawals — vending machines, trade hubs, item gating. |
| [`tokens`](https://github.com/evefrontier/builder-scaffold/tree/main/move-contracts/tokens) | Standalone token contracts (e.g. for use with gates or storage units). |

More standalone contracts (multisig, DAO, etc.) will be added over time.

> [!TIP]
> To understand how extensions work, read the [typed witness pattern](https://github.com/evefrontier/world-contracts/blob/main/docs/architechture.md#layer-3-player-extensions-moddability) documentation and the [Smart Assemblies Overview](/develop/smart-assemblies-intro/) page.

---

## Prerequisites

- Sui CLI or [Docker environment](../docker-environment/)
- A [deployed world](/develop/builder-scaffold/docker-flow/#5-deploy-world-and-create-test-resources) with artifacts copied into `builder-scaffold/deployments/`

---

## Build and Publish

Custom contracts depend on the world contract being published on either localnet or testnet.

### Testnet

On testnet the published world package is automatically resolved when deploying the custom contract:

```bash
cd move-contracts/smart_gate
sui move build -e testnet
sui client publish -e testnet
```

### Localnet

Since the local network is short-lived, you need to manually resolve to the published world package address by providing the path to the published ephemeral file:

```bash
cd move-contracts/smart_gate
sui client test-publish --build-env testnet --pubfile-path ../../deployments/localnet/Pub.localnet.toml
```

> [!NOTE]
> This assumes `Pub.localnet.toml` was copied to `deployments/localnet/` during the artifact copy step. See the [Docker Flow](../docker-flow/#6-copy-world-artifacts-into-builder-scaffold) or [Host Flow](../host-flow/#5-copy-world-artifacts-into-builder-scaffold) for details.

### In Docker

Contracts are at `/workspace/builder-scaffold/move-contracts/`. From inside the container you can publish the same way on either localnet or testnet.

---

## After Publishing

From the publish output, set two environment variables in your `.env`:

| Variable | Source |
|----------|--------|
| `BUILDER_PACKAGE_ID` | The package ID from the publish transaction output |
| `EXTENSION_CONFIG_ID` | The `ExtensionConfig` object ID from the publish output |

Then run the [TypeScript scripts](https://github.com/evefrontier/builder-scaffold/blob/main/ts-scripts/readme.md) in order. Full step-by-step instructions are in the [Docker Flow](../docker-flow/#9-run-scripts) or [Host Flow](../host-flow/#8-run-scripts).

### Smart Gate Script Order

```bash
cd /workspace/builder-scaffold   # or the builder-scaffold root on host
pnpm install
pnpm configure-rules
pnpm authorise-gate
pnpm authorise-storage-unit
pnpm issue-tribe-jump-permit
pnpm jump-with-permit
pnpm collect-corpse-bounty
```

---

## Formatting and Linting

From the repo root:

```bash
pnpm fmt          # format Move files
pnpm fmt:check    # check formatting (CI)
pnpm lint         # build + Move linter
```

---

## Related Resources

- [Smart Assemblies Overview](/develop/smart-assemblies-intro/) — Programmable assemblies and the typed witness extension pattern
- [Extension Examples](/develop/world-contracts/extension-examples/) — World-contracts extension code walkthroughs
- [Package Management](https://docs.sui.io/guides/developer/packages/move-package-management) — Sui Move dependency resolution, including ephemeral `test-publish`
