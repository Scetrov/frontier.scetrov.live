+++
date = '2026-02-28T12:00:00Z'
title = 'Docker Flow'
weight = 5
description = "End-to-end builder-scaffold workflow running entirely inside Docker — no Sui tools needed on your host."
codebase = "https://github.com/evefrontier/builder-scaffold"
+++

Run the full builder-scaffold flow inside a Docker container — no Sui CLI or Node.js required on your host. The same steps work for any extension example (`smart_gate`, `storage_unit`, or your own); this guide uses `smart_gate` for the publish and scripts steps.

<!--more-->

> [!TIP]
> Prefer working on your host? See [Host Flow](../host-flow/) to run with Sui CLI and Node.js installed locally.

{{< efctl action="the entire Docker flow (container start, world deploy, extension publish, and script execution)" command="efctl env up" />}}

---

## 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed

---

## 2. Clone the Repo

If you haven't already:

```bash
mkdir -p workspace && cd workspace
git clone https://github.com/evefrontier/builder-scaffold.git
cd builder-scaffold
```

---

## 3. Start the Container

```bash
cd docker
docker compose run --rm --service-ports sui-dev
```

On first run the container creates three funded accounts (`ADMIN`, `PLAYER_A`, `PLAYER_B`). Keys persist across container restarts via a Docker volume. Every start spins up a fresh local Sui node and funds the accounts from the faucet.

Inside the container you get:

```text
/workspace/
├── builder-scaffold/    # full repo (syncs with host)
└── world-contracts/     # bind mount — clone here (syncs with host)
```

For full container details (workspace layout, testnet switching, cleanup) see the [Docker Environment](../docker-environment/) page.

---

## 4. Switch to Testnet (Optional)

You can switch to testnet from inside the container the same way you would on your host:

```bash
sui client switch --env testnet
sui keytool import <your-private-key> ed25519
sui client faucet
```

---

## 5. Deploy World and Create Test Resources

> [!NOTE]
> These manual steps (clone, deploy, configure, seed, copy artifacts) will be simplified into a single setup command in a future release. Move package dependencies will resolve automatically using [MVR](https://docs.sui.io/guides/developer/packages/move-package-management).

```bash
cd /workspace/world-contracts
git clone https://github.com/evefrontier/world-contracts.git .
/workspace/scripts/generate-world-env.sh   # creates .env from docker/.env.sui keys
pnpm install
pnpm deploy-world localnet       # or testnet
pnpm configure-world localnet    # or testnet
pnpm create-test-resources localnet   # or testnet
```

> [!TIP]
> The `/workspace/world-contracts/` directory is a bind mount at `docker/world-contracts/` on your host, so files persist across restarts and are editable from your IDE.

---

## 6. Copy World Artifacts into Builder Scaffold

```bash
NETWORK=localnet   # or testnet
mkdir -p /workspace/builder-scaffold/deployments/$NETWORK/
cp -r deployments/* /workspace/builder-scaffold/deployments/
cp test-resources.json /workspace/builder-scaffold/test-resources.json
cp "contracts/world/Pub.localnet.toml" "/workspace/builder-scaffold/deployments/localnet/Pub.localnet.toml"
```

---

## 7. Configure `.env`

```bash
cd /workspace/builder-scaffold
cp .env.example .env
```

Set the following in `.env`:

- Same keys/addresses used during world deployment
- `SUI_NETWORK=testnet` (or `localnet`)
- `WORLD_PACKAGE_ID` — from `deployments/<network>/extracted-object-ids.json` (`world.packageId`)

---

## 8. Publish a Custom Contract

Pick an example (e.g. `smart_gate` or `storage_unit`); use its folder in `move-contracts/`:

```bash
cd /workspace/builder-scaffold/move-contracts/smart_gate   # or storage_unit, or your package
```

**Localnet** — use ephemeral publication:

```bash
sui client test-publish --build-env testnet --pubfile-path ../../deployments/localnet/Pub.localnet.toml
```

**Testnet** — publish directly:

```bash
sui client publish --build-env testnet
```

Set `BUILDER_PACKAGE_ID` and `EXTENSION_CONFIG_ID` in `/workspace/builder-scaffold/.env` from the publish output.

> [!TIP]
> Why `--build-env testnet` even for localnet? The local chain ID changes on every restart, so you can't pin it in `Move.toml`. Using testnet as the build environment resolves dependencies correctly while publishing to your local node via [ephemeral publication](https://docs.sui.io/guides/developer/packages/move-package-management#test-publish).

For more details see the [Move Contracts](../move-contracts/) page.

---

## 9. Run Scripts

For the `smart_gate` example (scripts are in the repo root):

```bash
cd /workspace/builder-scaffold
pnpm install
pnpm configure-rules
pnpm authorise-gate
pnpm authorise-storage-unit
pnpm issue-tribe-jump-permit
pnpm jump-with-permit
pnpm collect-corpse-bounty
```

---

## Useful Commands

| Task             | Command                                                                                |
| ---------------- | -------------------------------------------------------------------------------------- |
| View keys        | `cat /workspace/builder-scaffold/docker/.env.sui`                                      |
| List addresses   | `sui client addresses`                                                                 |
| Switch network   | `sui client switch --env testnet`                                                      |
| Import a key     | `sui keytool import <key> ed25519`                                                     |
| Build a contract | `cd /workspace/builder-scaffold/move-contracts/<example> && sui move build -e testnet` |

See [Docker Environment](../docker-environment/) for container rebuild, cleanup, and troubleshooting details.
