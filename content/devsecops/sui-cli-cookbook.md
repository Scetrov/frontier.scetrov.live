+++
date = '2025-10-09T20:50:00+01:00'
title = 'Sui CLI Cookbook'
weight = 20
+++

The [`sui` CLI](https://docs.sui.io/guides/developer/getting-started) is the primary command-line interface for interacting with Sui nodes, wallets, and developer tools. This cookbook provides quick, copy-paste examples for common tasks.

## Install

### Homebrew (macOS / Linux / WSL)

```sh
brew install sui
```

### Chocolatey (Windows)

```pwsh
choco install sui
```

### Install with suiup

[`suiup`](https://github.com/MystenLabs/suiup) is a tool similar to `rustup`. Install it and then install `sui`:

```sh
curl -sSfL https://raw.githubusercontent.com/Mystenlabs/suiup/main/install.sh | sh
suiup install sui
```

Alternatively, download releases from the [Sui GitHub Releases](https://github.com/MystenLabs/sui/releases).

## Cookbook

Below are practical commands you can copy and paste, organized by task. For many commands, you may need to run `sui client` once and accept prompts to create the configuration and an initial keypair.

> [!NOTE]
> Sui's documentation is sometimes inconsistent about RPC endpoints. The canonical fullnode RPC endpoints are:
>
> - Devnet: `https://fullnode.devnet.sui.io:443`
> - Testnet: `https://fullnode.testnet.sui.io:443`
> - Mainnet: `https://fullnode.mainnet.sui.io:443`
>
> [!INFORMATION]
> Many commands accept `--help` for usage (for example `sui client --help`). To get JSON output for scripting, append `--json`.

## Creating Accounts

Create an ed25519 account (alias `alice`):

```sh
sui client new-address ed25519 alice
```

Create secp256k1 and secp256r1 accounts:

```sh
sui client new-address secp256k1 bob
sui client new-address secp256r1 charlie
```

List all addresses:

```sh
sui client addresses
```

Switch the active address:

```sh
sui client switch --address alice
```

Request faucet funds (testnet/devnet or local faucet):

```sh
sui client faucet --address alice
```

Check an account balance:

```sh
sui client balance alice
```

Check balance for a specific coin type:

```sh
sui client balance alice --with-coins
```

## Key Management

### Generate a new keypair

Generate an ed25519 keypair (mnemonic + keypair file):

```sh
sui keytool generate ed25519
```

Generate a secp256k1 or secp256r1 keypair:

```sh
sui keytool generate secp256k1
sui keytool generate secp256r1
```

### List keys in the keystore

```sh
sui keytool list
```

Sort by alias for readability:

```sh
sui keytool list --sort-by-alias
```

### Import an existing key

Import a mnemonic phrase:

```sh
sui keytool import "your twelve word mnemonic phrase goes here" ed25519 --alias my-key
```

Import a bech32 private key (`suiprivkey...`):

```sh
sui keytool import suiprivkey1q... ed25519 --alias my-key
```

### Export a private key

```sh
sui keytool export --key-identity alice
```

### Convert key formats

Convert a hex or base64 private key to bech32 `suiprivkey` format:

```sh
sui keytool convert <HEX_OR_BASE64_KEY>
```

## Environment Management

### List environments

```sh
sui client envs
```

### Add a new environment

```sh
sui client new-env --alias testnet --rpc https://fullnode.testnet.sui.io:443
sui client new-env --alias mainnet --rpc https://fullnode.mainnet.sui.io:443
sui client new-env --alias devnet  --rpc https://fullnode.devnet.sui.io:443
```

### Switch active environment

```sh
sui client switch --env testnet
```

### Check active environment and address

```sh
sui client active-env
sui client active-address
```

## Working with Objects

### View all objects owned by active address

```sh
sui client objects
```

### Inspect a specific object

```sh
sui client object <OBJECT_ID>
```

Get raw BCS bytes:

```sh
sui client object <OBJECT_ID> --bcs
```

### List dynamic fields on an object

```sh
sui client dynamic-field <OBJECT_ID> --limit 10
```

### View gas coins

```sh
sui client gas
```

## Coin Operations

### Transfer SUI

```sh
sui client transfer-sui --to <RECIPIENT_ADDRESS> --sui-coin-object-id <COIN_ID> --amount 1000000000
```

### Transfer an object

```sh
sui client transfer --to <RECIPIENT_ADDRESS> --object-id <OBJECT_ID>
```

### Split a coin

Split a coin into multiple coins with specific amounts:

```sh
sui client split-coin --coin-id <COIN_ID> --amounts 1000000000 2000000000
```

### Merge coins

```sh
sui client merge-coin --primary-coin <COIN_ID_1> --coin-to-merge <COIN_ID_2>
```

### Pay (multi-input, multi-output)

Send specific amounts from one or more input coins to one or more recipients:

```sh
sui client pay --input-coins <COIN_1> <COIN_2> --recipients <ADDR_1> <ADDR_2> --amounts 500 1000
```

### Send all SUI from one coin to a recipient

```sh
sui client pay-all-sui --input-coins <COIN_ID> --recipient <RECIPIENT_ADDRESS>
```

## Move Package Development

### Create a new Move package

```sh
sui move new my_package
```

### Build a package

```sh
sui move build -p ./my_package
```

Build in dev mode (enables `#[test_only]` code):

```sh
sui move build -p ./my_package -d
```

### Run tests

```sh
sui move test -p ./my_package
```

Run tests with coverage and multiple threads:

```sh
sui move test -p ./my_package --coverage --threads 4
```

Run a specific test by name filter:

```sh
sui move test -p ./my_package my_test_function
```

### View test coverage

After running tests with `--coverage`:

```sh
sui move coverage summary -p ./my_package
sui move coverage source -p ./my_package --module my_module
```

Generate lcov output for CI integration:

```sh
sui move coverage lcov -p ./my_package
```

### Dump bytecode as base64

Useful for publishing automation and CI pipelines:

```sh
sui move build -p ./my_package --dump-bytecode-as-base64
```

## Publishing and Upgrading Packages

### Publish a package

```sh
sui client publish --path ./my_package --gas-budget 100000000
```

Dry-run to preview effects without executing:

```sh
sui client publish --path ./my_package --dry-run
```

### Upgrade a package

```sh
sui client upgrade --upgrade-capability <CAP_ID> --path ./my_package --gas-budget 100000000
```

## Calling Move Functions

### Call a function on-chain

```sh
sui client call \
  --package <PACKAGE_ID> \
  --module my_module \
  --function my_function \
  --args <ARG1> <ARG2> \
  --gas-budget 10000000
```

Dry-run a call (no on-chain execution):

```sh
sui client call \
  --package <PACKAGE_ID> \
  --module my_module \
  --function my_function \
  --args <ARG1> \
  --dry-run
```

Dev-inspect a call (simulated, no gas needed):

```sh
sui client call \
  --package <PACKAGE_ID> \
  --module my_module \
  --function my_function \
  --args <ARG1> \
  --dev-inspect
```

## Programmable Transaction Blocks (PTBs)

PTBs let you compose multiple operations into a single atomic transaction. Use `sui client ptb` to build them.

### Basic PTB with variable assignment

```sh
sui client ptb \
  --assign amt 1000 \
  --split-coins gas "[amt]" \
  --assign coins \
  --transfer-objects "[coins]" @<RECIPIENT_ADDRESS>
```

### Split coins and transfer in one transaction

```sh
sui client ptb \
  --split-coins @<COIN_ID> "[1000, 2000, 3000]" \
  --assign new_coins \
  --transfer-objects "[new_coins.0, new_coins.1]" @<ADDR_1> \
  --transfer-objects "[new_coins.2]" @<ADDR_2>
```

### Move call inside a PTB

```sh
sui client ptb \
  --move-call <PACKAGE>::my_module::create_thing \
  --assign result \
  --transfer-objects "[result]" @<RECIPIENT_ADDRESS> \
  --gas-budget 10000000
```

### Publish a package inside a PTB

```sh
sui client ptb \
  --publish ./my_package \
  --assign publish_result \
  --gas-budget 100000000 \
  --preview
```

### Preview and dry-run PTBs

Always preview complex PTBs before submitting:

```sh
# Preview (shows the PTB structure without executing)
sui client ptb \
  --split-coins gas "[5000]" \
  --assign coins \
  --transfer-objects "[coins]" @<RECIPIENT_ADDRESS> \
  --preview

# Dry-run (simulates execution and shows effects)
sui client ptb \
  --split-coins gas "[5000]" \
  --assign coins \
  --transfer-objects "[coins]" @<RECIPIENT_ADDRESS> \
  --dry-run
```

### Serialize a PTB for offline signing

```sh
sui client ptb \
  --move-call <PACKAGE>::mod::fn \
  --serialize-unsigned-transaction > unsigned_tx.b64
```

Execute the signed transaction later:

```sh
sui client execute-signed-tx \
  --tx-bytes "$(cat unsigned_tx.b64)" \
  --signatures '<BASE64_SIGNATURE>'
```

## Starting a Local Network

Start a local network (example with faucet):

```sh
RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis
```

Start with indexer and GraphQL (requires Postgres):

```sh
sui start --force-regenesis --with-faucet --with-indexer --with-graphql \
  --pg-host localhost --pg-port 5432 --pg-user postgres --pg-password postgres --pg-db-name sui_indexer
```

Add a local RPC endpoint and switch the CLI to it:

```sh
sui client new-env --alias localnet --rpc http://localhost:9000
sui client switch --env localnet
```

Request funds from the local faucet:

```sh
sui client faucet --address alice
```

## Using dApps with Localnet

Nightly App and other wallets (e.g., Surf) can connect to a local network. In Nightly, add `https://localhost:9000` (or `http://localhost:9000` if the dApp supports it) as a custom RPC endpoint.

## Chaining Commands Together

These examples show how to combine `sui` commands with shell scripting to automate common developer workflows.

### Bootstrap a fresh local environment

Set up a complete local dev environment from scratch — create accounts, fund them, and verify:

```sh
# Start fresh local network in the background
RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis &
sleep 5

# Add localnet and switch to it
sui client new-env --alias localnet --rpc http://localhost:9000
sui client switch --env localnet

# Create dev accounts and fund them
sui client new-address ed25519 deployer
sui client new-address ed25519 user1
sui client faucet --address deployer
sui client faucet --address user1

# Verify balances
sui client balance deployer
sui client balance user1
```

### Build, test, and publish a package

Complete workflow from source to on-chain deployment:

```sh
# Build and run tests first
sui move build -p ./my_package && \
sui move test -p ./my_package --coverage --threads 4 && \
sui move coverage summary -p ./my_package

# If tests pass, publish (switch to deployer address first)
sui client switch --address deployer && \
sui client publish --path ./my_package --gas-budget 100000000 --json
```

### Extract package ID after publishing and call a function

Use `--json` output and `jq` to script interactions:

```sh
# Publish and capture the package ID
PUBLISH_OUTPUT=$(sui client publish --path ./my_package --gas-budget 100000000 --json)
PACKAGE_ID=$(echo "$PUBLISH_OUTPUT" | jq -r '.objectChanges[] | select(.type == "published") | .packageId')

echo "Published package: $PACKAGE_ID"

# Call an init-style function on the new package
sui client call \
  --package "$PACKAGE_ID" \
  --module my_module \
  --function initialize \
  --gas-budget 10000000 \
  --json
```

### Create, fund, and transfer between accounts

Multi-step account management:

```sh
# Create two accounts
sui client new-address ed25519 sender
sui client new-address ed25519 receiver

# Fund the sender
sui client faucet --address sender

# Get the sender's first gas coin ID
sui client switch --address sender
COIN_ID=$(sui client gas --json | jq -r '.[0].gasCoinId')

# Transfer some SUI to receiver
RECEIVER_ADDR=$(sui client addresses --json | jq -r '.addresses[] | select(.[1] == "receiver") | .[0]')
sui client transfer-sui \
  --to "$RECEIVER_ADDR" \
  --sui-coin-object-id "$COIN_ID" \
  --amount 500000000

# Verify both balances
sui client balance sender
sui client balance receiver
```

### Dry-run before committing on-chain

Safe pattern for validating transactions before executing:

```sh
# First: dry-run to inspect effects
sui client call \
  --package "$PACKAGE_ID" \
  --module game \
  --function attack \
  --args "$PLAYER_OBJ" "$TARGET_OBJ" \
  --dry-run

# If satisfied, execute for real
sui client call \
  --package "$PACKAGE_ID" \
  --module game \
  --function attack \
  --args "$PLAYER_OBJ" "$TARGET_OBJ" \
  --gas-budget 10000000
```

### Serialize, sign offline, and execute

For secure workflows where signing happens on an air-gapped machine:

```sh
# On the online machine: serialize the transaction
sui client ptb \
  --move-call "$PACKAGE"::vault::withdraw "$VAULT_OBJ" \
  --assign result \
  --transfer-objects "[result]" @"$RECIPIENT" \
  --serialize-unsigned-transaction > unsigned_tx.b64

# Transfer unsigned_tx.b64 to the air-gapped machine and sign there
# Then bring the signature back and execute:
sui client execute-signed-tx \
  --tx-bytes "$(cat unsigned_tx.b64)" \
  --signatures "$(cat signature.b64)"
```

### Query object state in a loop (polling)

Monitor an object for changes (useful for testing event-driven contracts):

```sh
OBJECT_ID="0x..."
while true; do
  echo "--- $(date) ---"
  sui client object "$OBJECT_ID" --json | jq '.content.fields'
  sleep 5
done
```

### Full local development cycle

End-to-end: start network, create package, build, test, publish, interact:

```sh
#!/usr/bin/env bash
set -euo pipefail

# 1. Start local network
RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis &
SUI_PID=$!
sleep 5

# 2. Configure client
sui client new-env --alias localnet --rpc http://localhost:9000
sui client switch --env localnet

# 3. Create and fund deployer
sui client new-address ed25519 deployer
sui client switch --address deployer
sui client faucet --address deployer
sleep 2

# 4. Create and test the Move package
sui move new my_game
sui move build -p ./my_game
sui move test  -p ./my_game

# 5. Publish
RESULT=$(sui client publish --path ./my_game --gas-budget 100000000 --json)
PKG=$(echo "$RESULT" | jq -r '.objectChanges[] | select(.type == "published") | .packageId')
echo "Package ID: $PKG"

# 6. Interact with the published package
sui client call --package "$PKG" --module my_game --function start --gas-budget 10000000

# 7. Cleanup
kill $SUI_PID
```

## Troubleshooting

| Problem | Cause | Fix |
| --- | --- | --- |
| `address already in use` on start | Port conflict (9000, 9123, etc.) | `lsof -i :<PORT>` to find the process, kill it, or change the port |
| Indexer can't connect to Postgres | Wrong `--pg-*` flags or DB not running | Verify Postgres is running and flags match connection params |
| `no genesis found` | Missing or wrong `--network.config` path | Re-run `sui genesis --write-config` or use `--force-regenesis` |
| Transaction gas errors | Budget too low | Increase `--gas-budget` or try `--dry-run` first to see required gas |
| Key import errors | Wrong format or missing alias | Use `sui keytool import` with `--alias`; check format (mnemonic vs bech32) |
| Faucet returns error | Wrong network or faucet not running | Verify `sui client active-env` and that `--with-faucet` was set on start |

## Quick tips

- Use `--help` on any `sui` subcommand for details (for example, `sui start --help`).
- Use `--json` where available to integrate `sui` output into scripts.
- Use `--dry-run` or `--dev-inspect` before committing transactions on-chain.
- Use `--preview` on PTBs to see the structure without executing.
- Pipe `--json` output to `jq` for reliable scripting (for example, extracting object IDs).
