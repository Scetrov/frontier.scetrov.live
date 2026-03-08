+++
date = '2026-02-28T12:00:00Z'
title = 'Host Flow'
weight = 6
description = "End-to-end builder-scaffold workflow running on your host machine with Sui CLI and Node.js — targeting testnet or a local network."
codebase = "https://github.com/evefrontier/builder-scaffold"
+++

Run the builder-scaffold flow on your host machine, targeting testnet or a local Sui network. The same steps work for any extension example (`smart_gate`, `storage_unit`, or your own); this guide uses `smart_gate` for the publish and scripts steps.

<!--more-->

> [!TIP]
> Prefer Docker? See [Docker Flow](../docker-flow/) to run the full flow inside a container with no host tooling required.

---

## 1. Prerequisites

- **Sui CLI**, **Node.js**, and **pnpm** installed on your host
- For **testnet**: funded accounts (e.g. from [Sui testnet faucet](https://faucet.sui.io/))
- For **local**: a running Sui local node (see below)

### Starting a Local Node

```bash
sui start --with-faucet
```

This starts a local Sui node on port 9000 with a faucet on port 9123.

---

## 2. Clone the Repo

If you haven't already:

```bash
mkdir -p workspace && cd workspace
git clone https://github.com/evefrontier/builder-scaffold.git
cd builder-scaffold
```

---

## 3. Choose Your Network

**Testnet** — no extra setup, just set your CLI to the right environment:

```bash
sui client switch --env testnet
```

**Localnet** — you need a local Sui node running on port 9000:

```bash
sui client switch --env localnet
```

---

## 4. Deploy World and Create Test Resources

> [!NOTE]
> These manual steps will be simplified into a single setup command in a future release. See [`setup-world/readme.md`](https://github.com/evefrontier/builder-scaffold/blob/main/setup-world/readme.md) for details.

From your workspace directory (parent of `builder-scaffold`), clone `world-contracts` as a sibling and deploy:

```bash
cd ..   # workspace (parent of builder-scaffold)
git clone https://github.com/evefrontier/world-contracts.git
cd world-contracts
cp env.example .env
```

Edit `.env` with your keys and addresses:

```env
SUI_NETWORK=testnet       # or localnet
ADMIN_PRIVATE_KEY=<your-admin-key>
ADMIN_ADDRESS=<your-admin-address>
SPONSOR_ADDRESS=<your-admin-address>    # can be the same as ADMIN for dev
GOVERNOR_PRIVATE_KEY=<your-admin-key>   # optional, can match ADMIN
```

Then deploy:

```bash
pnpm install
pnpm deploy-world testnet       # or localnet
pnpm configure-world testnet    # or localnet
pnpm create-test-resources testnet   # or localnet
```

---

## 5. Copy World Artifacts into Builder Scaffold

```bash
NETWORK=localnet   # or testnet
mkdir -p ../builder-scaffold/deployments/$NETWORK/
cp -r deployments/* ../builder-scaffold/deployments/
cp test-resources.json ../builder-scaffold/test-resources.json
cp "contracts/world/Pub.localnet.toml" "../builder-scaffold/deployments/localnet/Pub.localnet.toml"
```

---

## 6. Configure `.env`

```bash
cd ../builder-scaffold
cp .env.example .env
```

Set the following in `.env`:

- Same keys/addresses as `world-contracts`
- `SUI_NETWORK=testnet` (or `localnet`)
- `WORLD_PACKAGE_ID` — from `deployments/<network>/extracted-object-ids.json` (`world.packageId`)

---

## 7. Publish a Custom Contract

Pick an example (e.g. `smart_gate` or `storage_unit`); use its folder in `move-contracts/`:

```bash
cd move-contracts/smart_gate   # or storage_unit, or your package
```

**Testnet** — publish directly:

```bash
sui client publish --build-env testnet
```

**Localnet** — use ephemeral publication:

```bash
sui client test-publish --build-env testnet --pubfile-path ../../deployments/localnet/Pub.localnet.toml
```

Set `BUILDER_PACKAGE_ID` and `EXTENSION_CONFIG_ID` in `.env` from the publish output.

For more details see the [Move Contracts](../move-contracts/) page.

---

## 8. Run Scripts

For the `smart_gate` example (scripts are in the repo root):

```bash
cd ../..   # builder-scaffold root
pnpm install
pnpm configure-rules
pnpm authorise-gate
pnpm authorise-storage-unit
pnpm issue-tribe-jump-permit
pnpm jump-with-permit
pnpm collect-corpse-bounty
```

---

## Directory Layout

After completing all steps, your workspace should look like:

```text
workspace/
├── builder-scaffold/
│   ├── .env                          # configured with keys and package IDs
│   ├── deployments/
│   │   └── <network>/               # world artifacts copied from world-contracts
│   ├── move-contracts/
│   │   ├── smart_gate/               # your published extension
│   │   └── storage_unit/
│   └── ts-scripts/                   # TypeScript interaction scripts
└── world-contracts/
    ├── .env                          # keys and network config
    ├── contracts/
    └── deployments/                  # source of world artifacts
```
