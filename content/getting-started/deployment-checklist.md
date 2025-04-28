+++
date = '2025-04-28T16:22:00+01:00'
title = 'Deployment Runbook'
weight = 40
+++

These are the things I am checking when doing a deployment:

1. Is the namespace updated in both `constants.sol` and `mud.config.ts`?
2. Have the `PRIVATE_KEY`, `WORLD_ADDRESS`, `RPC_URL` and `CHAIN_ID` been set in `.env`?
3. Do all unit tests pass when the `.env` is set to local?

## Local `.env`

```ini
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 # Well Known Private Key
WORLD_ADDRESS=0x8a791620dd6260079bf849dc5567adc3f2fdc318 # Local World Address
RPC_URL=http://127.0.0.1:8545 # Forked Anvil Local RPC URL
CHAIN_ID=31337 # Local Chain ID
```

## Stillness `.env'`

```ini
PRIVATE_KEY={{Private Key}}
WORLD_ADDRESS=0x90373cf89e73168cdf90e99d0a7fa9c4b5625c6a # Stillness Cycle 3
RPC_URL=https://pyrope-external-rpc.live.tech.evefrontier.com
CHAIN_ID=695569
```
