+++
date = '2026-02-28T12:00:00Z'
title = 'Docker Environment'
weight = 7
description = "Details on the builder-scaffold Docker dev container — workspace layout, testnet switching, key management, and troubleshooting."
codebase = "https://github.com/evefrontier/builder-scaffold"
+++

The builder-scaffold Docker container provides a self-contained Sui development environment with Sui CLI, Node.js, and pnpm pre-installed. No host tooling is needed — you edit files on your host and run commands in the container.

<!--more-->

---

## Quick Start

```bash
cd docker
docker compose run --rm --service-ports sui-dev
```

On first run the container creates three ed25519 keypairs (`ADMIN`, `PLAYER_A`, `PLAYER_B`). Keys persist across container restarts via a Docker volume.

Every start spins up a fresh local Sui node and funds the accounts from the faucet.

---

## Workspace Layout

```text
/workspace/
├── builder-scaffold/    # full repo (syncs with host)
└── world-contracts/     # bind mount — clone here on host, visible inside container
```

Edit files on your host, run commands in the container:

```bash
cd /workspace/builder-scaffold/move-contracts/smart_gate_extension
sui move build -e testnet
```

> [!TIP]
> Why `-e testnet` even for local builds? The localnet chain ID changes on every restart, so you can't pin it in `Move.toml`. Using testnet as the build environment resolves dependencies correctly while publishing to your local node via [ephemeral publication](https://docs.sui.io/guides/developer/packages/move-package-management#test-publish).

---

## Using Testnet

The container starts on localnet, but you can switch to testnet at any time:

```bash
sui client switch --env testnet
```

Fund your local keys on testnet by requesting gas from [https://faucet.sui.io/](https://faucet.sui.io/), or use the CLI:

```bash
sui client faucet
```

---

## Bring Your Own Keys

If you want to use existing keys instead of the auto-generated ones:

```bash
sui keytool import <your-private-key> ed25519 --alias my-key
sui client switch --env testnet
sui client switch --address <your-address>
```

For TS scripts and `world-contracts`, manually fill in the `.env` files with your own keys and addresses instead of using `generate-world-env.sh`.

---

## Useful Commands

| Task                            | Command                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------------------- |
| View keys                       | `cat /workspace/builder-scaffold/docker/.env.sui`                                                 |
| List addresses                  | `sui client addresses`                                                                            |
| Switch network                  | `sui client switch --env testnet`                                                                 |
| Import a key                    | `sui keytool import <key> ed25519`                                                                |
| Stop local node                 | `pkill -f "sui start"`                                                                            |
| Generate world-contracts `.env` | `/workspace/scripts/generate-world-env.sh`                                                        |
| Build a contract                | `cd /workspace/builder-scaffold/move-contracts/smart_gate_extension && sui move build -e testnet` |
| Run TS scripts                  | `cd /workspace/builder-scaffold && pnpm configure-rules`                                          |

---

## Connect to Local Node from Host

Port 9000 is published. On your host:

```bash
sui client new-env --alias localnet --rpc http://127.0.0.1:9000
sui client switch --env localnet
```

Wait until the container logs `RPC ready` before connecting. Import keys from `docker/.env.sui` if needed.

---

## Clean Up / Fresh Start

To wipe all state and start from scratch:

```bash
docker volume rm docker_sui-config 2>/dev/null || true
docker compose build
docker compose run --rm --service-ports sui-dev
```

### Troubleshooting (Windows PowerShell)

If you encounter issues on Windows, ensure you're using PowerShell (not `cmd.exe`) and that Docker Desktop is running with the WSL2 backend. See the [Windows setup guide](/getting-started/windows/) for additional tips.
