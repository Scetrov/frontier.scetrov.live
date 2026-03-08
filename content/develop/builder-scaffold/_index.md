+++
title = "Builder Scaffold"
type = "chapter"
weight = 10
description = "Templates and tools for building on EVE Frontier — Docker and host flows, Move contract examples, dApp template, and zkLogin CLI."
codebase = "https://github.com/evefrontier/builder-scaffold"
+++

> [!NOTE]
> The [builder-scaffold](https://github.com/evefrontier/builder-scaffold) repository is under active development. Some workflows (e.g. world deployment) are being simplified into single-command operations. Check the repo for the latest changes.

Templates and tools for building on EVE Frontier. The **builder-scaffold** repository provides everything you need to deploy a world, write custom Move contracts (extensions), publish them, and interact with them via TypeScript scripts — all locally or on testnet.

## What's in the Repo

| Directory         | Purpose                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| `docker/`         | Dev container (Sui CLI + Node.js) — used by the Docker flow.                                   |
| `move-contracts/` | Custom Smart Assembly extension examples (e.g. `smart_gate`, `storage_unit`); build & publish. |
| `ts-scripts/`     | TypeScript scripts to call your contracts; run after publishing.                               |
| `setup-world/`    | What "deploy world" does and what gets created.                                                |
| `dapps/`          | Reference dApp template (optional next step).                                                  |
| `zklogin/`        | zkLogin CLI for OAuth-based signing (optional).                                                |

---

## Prerequisites

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/get-docker/) (for the Docker flow) **or** [Sui CLI](https://docs.sui.io/guides/developer/getting-started) + Node.js (for the Host flow)

---

## Quick Start

Clone the repo:

```bash
mkdir -p workspace && cd workspace
git clone https://github.com/evefrontier/builder-scaffold.git
cd builder-scaffold
```

Then choose a flow:

| Flow                        | When to Use                                                            |
| --------------------------- | ---------------------------------------------------------------------- |
| [Docker Flow](docker-flow/) | No Sui/Node on host; run everything in a container (local or testnet). |
| [Host Flow](host-flow/)     | Sui CLI + Node.js installed on your machine; target local or testnet.  |

By the end you'll have a deployed world, a published custom contract (e.g. `smart_gate`), and scripts that call it.

---

## Related Resources

- [Smart Assemblies Overview](/develop/smart-assemblies-intro/) — Programmable assemblies and the extension pattern
- [Extension Examples](/develop/world-contracts/extension-examples/) — World-contracts extension code walkthroughs
- [Sui Playground](/getting-started/sui/sui-playground/) — Step-by-step quick tutorial for local setup
- [efctl](/links/efctl/) — CLI that automates builder-scaffold workflows

{{% children sort="weight" %}}

{{% tip-menu-search %}}
