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

Below are unordered, practical commands you can copy and paste. For many commands, you may need to run `sui client` once and accept prompts to create the configuration and an initial keypair.

> [!NOTE]
> Sui's documentation is sometimes inconsistent about RPC endpoints. The canonical fullnode RPC endpoints are:
>
> - Devnet: `https://fullnode.devnet.sui.io:443`
> - Testnet: `https://fullnode.testnet.sui.io:443`
> - Mainnet: `https://fullnode.mainnet.sui.io:443`
>
> [!INFORMATION]
> Many commands accept `--help` for usage (for example `sui client --help`). To get JSON output for scripting, append `--json`.

### Creating Accounts

Create an ed25519 account (alias `alice`):

```sh
sui client new-address ed25519 alice
```

Create secp256k1 and secp256r1 accounts:

```sh
sui client new-address secp256k1 bob
sui client new-address secp256r1 charlie
```

Request faucet funds (testnet/devnet or local faucet):

```sh
sui client faucet --address alice
```

Check an account balance:

```sh
sui client balance alice
```

## Starting a Local Network

Start a local network (example with faucet):

```sh
RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis
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

## Quick tips

- Use `--help` on any `sui` subcommand for details (for example, `sui start --help`).
- Use `--json` where available to integrate `sui` output into scripts.
