+++
date = '2026-02-21T12:23:00Z'
title = "Crypto"
type = "chapter"
weight = 5
codebase = "https://github.com/evefrontier/world-contracts/tree/main/contracts/world/sources/crypto"
+++

The `contracts/world/sources/crypto/` folder contains cryptographic utility modules used across the EVE Frontier world contracts. These modules provide signature verification and address derivation functionality essential for validating off-chain proofs on-chain.

## Folder Overview

| File                  | Description                                                                                                          |
| --------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **`sig_verify.move`** | Ed25519 signature verification and Sui address derivation for validating off-chain signed messages (e.g., location proofs). |

{{% children sort="weight" %}}

{{% tip-menu-search %}}
