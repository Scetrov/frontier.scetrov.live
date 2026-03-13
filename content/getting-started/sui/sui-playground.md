+++
date = '2026-02-23T18:13:00+00:00'
title = 'Sui Playground'
weight = 10
codebase = "https://github.com/evefrontier/world-contracts"
+++

This guide provides step-by-step instructions to manually set up a local Sui development environment, deploy the EVE Frontier `world-contracts`, and initialize a Smart Gate infrastructure. Credit to [[WOLF] Lacal](https://ef-map.com/) for the original walkthrough posted in Discord.

> [!TIP]
> For comprehensive documentation on the builder-scaffold repository — including the Docker environment, Move contracts, the dApp template, and more — see the [Builder Scaffold](/develop/builder-scaffold/) section.

{{< efctl action="the entire playground setup, deployment, and gate configuration" command="efctl env up" >}}
See the <a href="https://github.com/scetrov/efctl/blob/main/USAGE.md">efctl usage guide</a> for all available commands.
{{< /efctl >}}

---

## 1. Prerequisites

- **Docker** or **Podman** installed, if you use Podman ensure that `alias docker=podman` is set up for seamless command usage.
  - **Windows Users**: Docker Desktop is recommended, however you can use WSL2 with Podman if you prefer.
  - **Linux Users**: Either Podman or Docker works well.
  - **Mac Users**: Docker Desktop is recommended, but Podman is also supported.
- **Git** installed to clone repositories.
- **Terminal Emulator** installed (e.g. Windows Terminal, iTerm2, Ghostty, etc.).
- **Text Editor** installed (e.g. VSCode, Notepad++, Sublime, NeoVim, etc.).
- **Sui CLI** (optional on host, but required if you want to interact without `docker exec`).

> [!IMPORTANT]
> Windows users should ensure that they are using Docker Desktop with the WSL2 backend for best compatibility. Additionally avoid using `cmd.exe` or `Windows PowerShell` for running commands, instead use Windows Terminal and PowerShell as these are less likely to mangle command output.
>
> If you don't have these installed use the following commands:
>
> ```powershell
> winget install --id Microsoft.WindowsTerminal --source winget
> winget install --id Microsoft.PowerShell --source winget
> ```

The below has been tested in the following configurations:

| OS                 | Container Runtime | Terminal         | Editor |
| ------------------ | ----------------- | ---------------- | ------ |
| Windows            | Docker Desktop    | Windows Terminal | VSCode |
| Debian 13 (WSL)    | Podman            | Windows Terminal | NeoVim |
| Debian 12 (Native) | Docker Engine     | Ghostty          | Vim    |
| Ubuntu 24.04 (WSL) | Podman            | Windows Terminal | NeoVim |
| NixOS 25.11        | Podman            | Ghostty          | NeoVim |

---

## 2. Repository Setup

Clone the core world contracts and the builder scaffold repositories into the same parent directory to ensure the Docker volume mounts work correctly.

### 2.1 Create a workspace directory

> [!NOTE]
> Windows users using WSL, should ensure that they `cd ~` before running the following `mkdir` command to ensure the workspace is created within the Linux filesystem and not on the Windows filesystem. This is because Docker Desktop with WSL2 backend has better performance when accessing files within the Linux filesystem compared to the Windows filesystem.

```bash
mkdir sui-frontier && cd sui-frontier
```

### 2.2 Clone world-contracts and builder-scaffold

```bash
git clone -b v0.0.18 https://github.com/evefrontier/world-contracts.git
```

```bash
git clone https://github.com/evefrontier/builder-scaffold.git
```

Your directory structure should look like this:

```text
sui-frontier/
├── world-contracts/
└── builder-scaffold/
```

---

## 3. Environment Setup

### 3.1 Verify Volume Mounts

Ensure `builder-scaffold/docker/compose.yml` correctly points to the `world-contracts` directory. It should look like this:

```yaml
volumes:
  - sui-config:/root/.sui
  - ../:/workspace/builder-scaffold
  - ../../world-contracts:/workspace/world-contracts
```

### 3.2 Start the Playground

Change into the `docker` directory of the builder scaffold to access the Docker Compose configuration:

```bash
cd builder-scaffold/docker
```

Start the container in the foreground with service ports exposed:

```bash
docker compose run --rm --service-ports sui-dev
```

On first run the container creates three funded keys and starts a fresh local Sui node. Wait until the terminal shows `Sui dev environment ready` before continuing.

If you want to interact with the local node from your host instead of from inside the container, configure a localnet RPC endpoint in another terminal:

```bash
sui client new-env --alias localnet --rpc http://127.0.0.1:9000
sui client switch --env localnet
```

---

## 4. World Contracts Configuration

### 4.1 Initialize `.env`

Run the following command inside the container shell to populate `world-contracts/.env` from the generated Docker keys:

```bash
/workspace/scripts/generate-world-env.sh
```

This script will:

1. Read the keys from `docker/.env.sui` created via the container initialization.
2. Populate the necessary variables in `world-contracts/.env`.

### 4.2 Example `.env`

If you need to manually edit or verify the `.env` files, they should contain the following variables (with actual values filled in):

```env
SUI_NETWORK=localnet
SUI_RPC_URL=http://127.0.0.1:9000

# Use ADMIN_PRIVATE_KEY for GOVERNOR
GOVERNOR_PRIVATE_KEY=<ADMIN_PRIVATE_KEY>
ADMIN_ADDRESS=<ADMIN_ADDRESS>
SPONSOR_ADDRESSES=<ADMIN_ADDRESS>

# Private keys for TS scripts
ADMIN_PRIVATE_KEY=<ADMIN_PRIVATE_KEY>
PLAYER_A_PRIVATE_KEY=<PLAYER_A_PRIVATE_KEY>
PLAYER_B_PRIVATE_KEY=<PLAYER_B_PRIVATE_KEY>

TENANT=dev

# Default configs for seeding
FUEL_TYPE_IDS=78437,78515,78516,84868,88319,88335
FUEL_EFFICIENCIES=90,80,40,40,15,10
ASSEMBLY_TYPE_IDS=77917,84556,84955,87119,87120,88063,88064,88067,88068,88069,88070,88071,88082,88083,90184,91978
ENERGY_REQUIRED_VALUES=500,10,950,50,250,100,200,100,200,100,200,300,50,100,1,100
GATE_TYPE_IDS=88086,84955
MAX_DISTANCES=520340175991902420,1040680351983804840
```

---

## 5. Deployment

### 5.1 Deploy World Package

Inside the container shell, move to the `world-contracts` repository:

```bash
cd /workspace/world-contracts
```

Finally deploy the world package:

```bash
pnpm install
pnpm deploy-world localnet
```

Stay in the container for the next steps.

### 5.2 Configure World State

Initialize the global registries and configurations:

```bash
pnpm configure-world localnet
```

### 5.3 Spawn Test Resources

Run the automated seeding script to create a working Smart Gate environment:

```bash
pnpm create-test-resources localnet
```

### 5.4 Optional: Copy World Artifacts Into builder-scaffold

If you plan to publish builder-scaffold example extensions against this local world, copy the deployment artifacts into the `builder-scaffold` repository instead of renaming publication files:

```bash
mkdir -p /workspace/builder-scaffold/deployments/localnet
cp -r deployments/* /workspace/builder-scaffold/deployments/
cp test-resources.json /workspace/builder-scaffold/test-resources.json
cp contracts/world/Pub.localnet.toml /workspace/builder-scaffold/deployments/localnet/Pub.localnet.toml
```

---

## 6. Spawning Structures (Gate Setup)

This script performs the following operations:

1. Creates two **Character** objects.
2. Anchors and fuels a **Network Node** (NWN).
3. Brings the NWN **online**.
4. Creates and brings online a **Smart Storage Unit** and deposits test items.
5. Creates and brings online two **Smart Gates**.
6. **Links** the two gates together.

---

## 7. Verification

### 7.1 Check Objects

You can verify the deployment by inspecting the shared objects:

#### 7.1.1 List all objects owned by ADMIN

Import the environment:

```bash
source /workspace/builder-scaffold/docker/.env.sui
```

Then list objects for the admin address:

```bash
sui client objects $ADMIN_ADDRESS
```

#### 7.1.2 Check the status of the Gate

Extract ID from `deployments/localnet/extracted-object-ids.json`:

```bash
GATE_ID=$(cat /workspace/world-contracts/deployments/localnet/extracted-object-ids.json | jq -r '.world.gateConfig')
```

Then use this in the next step to check the object:

```bash
sui client object $GATE_ID
```

### 7.2 Test Jumps

Once the gates are linked and online, you can test the jump functionality:

```bash
pnpm tsx ts-scripts/gate/jump.ts
```

---

## 8. Troubleshooting

- **"Unpublished dependencies: World"**: If you are publishing a builder-scaffold extension on localnet, ensure you copied `contracts/world/Pub.localnet.toml` into `builder-scaffold/deployments/localnet/Pub.localnet.toml` as shown in Step 5.4.
- **RPC connection refused**: Ensure the container is running and port 9000 is mapped. On Linux, if you are running TS scripts from the host, ensure `.env` uses `http://127.0.0.1:9000`.
- **Faucet Failure**: If the container fails to fund accounts on startup, ensure you have an internet connection (the local faucet inside the container is self-contained but initial `suiup` installation requires it).
- **Error: rootlessport listen tcp 0.0.0.0:9000: bind: address already in use**: This means another process is using port 9000 on your host. Stop the process and try again.
- **Error: line 47: 57 Illegal instruction (core dumped)**: This means the Sui binaries are not compatible with your CPU architecture, add `platform: linux/amd64` to the `sui-dev` service in `compose.yml` to force it to use the correct architecture.

## 9. Cleanup

Exit the container shell with `exit` or `Ctrl+D`, then from `builder-scaffold/docker` on your host run:

```bash
docker compose down
```

To force a fresh rebuild of the environment:

```bash
docker compose down
docker compose build
docker compose run --rm --service-ports sui-dev
```

To do a full prune of all unused Docker resources and volumes (be careful, this will remove all stopped containers, unused networks, dangling images, build cache, and unused volumes):

```bash
docker compose down
docker system prune -a --volumes
```
