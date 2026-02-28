+++
date = '2026-02-28T12:00:00Z'
title = 'dApp Starter Template'
weight = 9
description = "Reference React dApp template for building EVE Frontier frontends — wallet connection, assembly data, sponsored transactions."
+++

The `dapps/` directory contains a reference dApp starter template built with React, TypeScript, and Vite. It demonstrates how to connect to wallets, query Smart Assembly data, and interact with the EVE Frontier world from a web frontend.

<!--more-->

- **Source**: [`dapps/`](https://github.com/evefrontier/builder-scaffold/tree/main/dapps)

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [React](https://react.dev/) | UI framework |
| [TypeScript](https://www.typescriptlang.org/) | Type checking |
| [Vite](https://vitejs.dev/) | Build tooling |
| [Radix UI](https://www.radix-ui.com/) | Pre-built UI components |
| [ESLint](https://eslint.org/) | Linting |
| [@mysten/dapp-kit](https://sdk.mystenlabs.com/dapp-kit) | Wallet connection and data loading |
| [pnpm](https://pnpm.io/) | Package management |

---

## Features

| # | Feature | Description | File |
|---|---------|-------------|------|
| 1 | Provider setup | `EveFrontierProvider(queryClient)` wraps the app. Composes: `QueryClientProvider` (React Query), `DAppKitProvider` (Mysten Sui client + wallet), `VaultProvider` (EVE wallet/connection), `SmartObjectProvider` (GraphQL assembly/context), `NotificationProvider` (toasts). | `src/main.tsx` |
| 2 | Wallet connection | `useConnection()` from `@evefrontier/dapp-kit` — `handleConnect`, `handleDisconnect`, `isConnected`, `walletAddress`, `hasEveVault`. `useCurrentAccount()` from `@mysten/dapp-kit-react` for UI. `abbreviateAddress()` for display. | `src/App.tsx` |
| 3 | Wallet status | Same hooks (`useConnection`, `useCurrentAccount`) drive both header and status block; state stays in sync. | `src/App.tsx`, `src/WalletStatus.tsx` |
| 4 | Smart Object / Assembly | `useSmartObject()` from `@evefrontier/dapp-kit` uses `VITE_ITEM_ID` / URL params and GraphQL. Returns `assembly`, `character`, `loading`, `error`, `refetch`, optional `setSelectedObjectId`. | `src/AssemblyInfo.tsx` |
| 5 | GraphQL helpers (optional) | `getAssemblyWithOwner()`, `getOwnedObjectsByType()`, `executeGraphQLQuery()`, `transformToAssembly()`, `getObjectWithJson()`, etc. from `@evefrontier/dapp-kit`. | `src/queries.ts` |
| 6 | Sponsored transactions (optional) | `useSponsoredTransaction()` from `@evefrontier/dapp-kit`. Only supported by wallets that implement the EVE Frontier feature (e.g. EVE Vault). | Add when needed |
| 7 | Mysten layer | `useDAppKit()` from `@mysten/dapp-kit-react` — `signAndExecuteTransaction`, `signTransaction`, `signPersonalMessage`. For raw RPC or network: `useCurrentClient()`, `useCurrentNetwork()`. | `src/WalletStatus.tsx` |

---

## Getting Started

Install dependencies:

```bash
cd dapps
pnpm install
```

Start the development server:

```bash
pnpm dev
```

This launches Vite on `http://localhost:5173` by default.

---

## Building for Deployment

```bash
pnpm build
```

The production output is written to `dapps/dist/`.

---

## Key Packages

| Package | Purpose |
|---------|---------|
| `@evefrontier/dapp-kit` | EVE Frontier-specific hooks — wallet connection, smart object queries, sponsored transactions |
| `@mysten/dapp-kit-react` | Mysten's React hooks for Sui wallet interaction and transaction signing |

> [!TIP]
> Prefer `@evefrontier/dapp-kit` for connection and EVE data. Use `@mysten/dapp-kit-react` when you need raw RPC or lower-level transaction control.
