+++
date = '2026-02-28T12:00:00Z'
title = 'zkLogin CLI'
weight = 10
description = "Interactive CLI for executing Sui transactions with zkLogin via EVE Frontier OAuth — no private key management required."
+++

The `zklogin/` directory contains an interactive CLI tool for executing Sui transactions using [zkLogin](https://docs.sui.io/concepts/cryptography/zklogin) — Sui's OAuth-based signing mechanism. Instead of managing private keys directly, you authenticate with an OAuth provider (e.g. Google, Twitch) and sign transactions with zero-knowledge proofs derived from your login.

<!--more-->

- **Source**: [`zklogin/`](https://github.com/evefrontier/builder-scaffold/tree/main/zklogin)

---

## Usage

```bash
cd zklogin
pnpm install
pnpm zklogin
```

---

## Flow

1. The script generates ephemeral credentials and displays a login URL.
2. Open the URL in your browser and log in with your OAuth provider.
3. Copy the `id_token` from the redirect URL (`https://sui.io/#id_token=eyJ...`).
4. Paste the JWT when prompted.
5. Optionally provide transaction bytes, or press Enter for a test transaction.

```text
┌─────────────────────────────────────────────────┐
│  1. Generate ephemeral key                      │
│  2. Open login URL in browser                   │
│  3. Copy id_token from redirect                 │
│  4. Paste JWT → zkLogin proves your identity    │
│  5. Sign and execute transaction on-chain       │
└─────────────────────────────────────────────────┘
```

---

## Configuration

Edit `zkLoginTransaction.ts` to change:

| Setting           | Default             | Description                              |
| ----------------- | ------------------- | ---------------------------------------- |
| `AUTH_URL`        | EVE Frontier OAuth  | OAuth provider authorization endpoint    |
| `CLIENT_ID`       | EVE Frontier client | OAuth client ID                          |
| `SUI_NETWORK_URL` | devnet              | Target Sui network RPC URL               |
| `PROVER_URL`      | Mysten prover       | ZK prover endpoint for generating proofs |

---

## When to Use zkLogin

zkLogin is useful when you want to:

- Let end users sign transactions without exposing or managing private keys
- Integrate OAuth login flows (Google, Twitch, etc.) into your dApp
- Prototype transaction signing without setting up a full wallet

> [!TIP]
> For production dApps, consider using the [dApp Starter Template](../dapps/) with `@evefrontier/dapp-kit` which provides wallet connection via EVE Vault and supports sponsored transactions.
