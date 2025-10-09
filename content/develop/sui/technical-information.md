+++
date = '2025-10-09T20:50:00+01:00'
title = 'Basics and Keys'
weight = 10
+++

## Introduction

The [Sui Blockchain](https://sui.io/) is a Layer-1 smart contract platform developed by [Mysten Labs](https://www.mystenlabs.com/), designed to deliver low-latency, horizontally scalable transaction processing. Unlike the majority of blockchains that rely on total ordering of all transactions, Sui introduces an object-centric data model built around a [directed acyclic graph, or DAG](https://blog.sui.io/all-about-directed-acyclic-graphs/), combined with [Byzantine-Fault-Tolerant (BFT)](https://www.usenix.org/conference/nsdi24/presentation/amiri) consensus mechanisms. This architectural shift allows the network to execute independent transactions in parallel without consensus bottlenecks, improving throughput and responsiveness especially suited to games. Sui is built in Rust and leveraging the Move programming language, Sui offers strong safety guarantees through Move’s resource-oriented type system, ensuring exactly one of an object exists - i.e. preventing inadvertent duping or loss.

Sui organizes on-chain state as a collection of objects, each with globally unique IDs and explicit ownership semantics (owned, shared, or immutable). This allows fine-grained concurrency: owned objects can be modified independently, while shared objects require consensus. The consensus protocol itself uses [Mysticeti](https://sui.io/mysticeti) which integrates data dissemination and ordering into a single fast path, The result is a system capable of handling thousands of transactions per second with deterministic execution and sub-second confirmation times.

Sui’s design is particularly suited for applications requiring rich asset logic and interactive, user-centric experiences such as gaming, digital collectibles, and DeFi protocols. Its on-chain object model and programmable transaction blocks allow developers to represent complex state transitions directly in Move, enabling secure composability without the overhead of smart contract accounts or global locks. Combined with built-in support for multiple signature schemes (`Ed25519`, `secp256k1`, `secp256r1`), flexible key management, and native integration with passkey-based authentication, Sui represents one of the most advanced evolutions of blockchain execution architecture in the post-EVM era.

## Key Types and Schemes

Many blockchains only support a single, or sometimes two signature schemes, Sui however supports three with three separate purposes:

- `ed25519` - the EdDSA signature scheme using SHA-512 and an elliptic curve related to `Curve25519`, yes that one used in SSH. This is the default signature scheme for Sui, however not the only one.
- `secp256k1` - the signature scheme initially used in Bitcoin's Public Key Cryptography, and subsequently adopted by Ethereum, Litecoin and many others, due to it's widespread adoption Sui includes support for this curve as it can ease transition into the Sui ecosystem.
- `secp256r1` - use in FIDO and WebAuthN (PassKeys) offers native enterprise-level security and the use of YubiKey style hardware security tokens to sign transactions, albeit with a bit of a technical kludge as FIDO was not initially designed to support signing transactions, predominantly being an authentication protocol.

You can generate a new key from the command line with the [Sui CLI](https://docs.sui.io/references/cli):

### `ed25519`

Entering the command:

```sh
sui keytool generate ed25519
```

Results in:

```table
╭─────────────────┬──────────────────────────────────────────────────────────────────────╮
│ alias           │                                                                      │
│ suiAddress      │  0xb25ce38fd70d0d3bddd748adac7d6c13d3be9c296feb414c8069ca1f796f5d87  │
│ publicBase64Key │  AFAuqVpLsVsQRLvv8D9vL9InWJZo/rpS3aWLley8Fjim                        │
│ keyScheme       │  ed25519                                                             │
│ flag            │  0                                                                   │
│ mnemonic        │  junk junk junk junk junk junk junk junk junk junk junk test         │
│ peerId          │  502ea95a4bb15b1044bbeff03f6f2fd227589668feba52dda58b95ecbc1638a6    │
╰─────────────────┴──────────────────────────────────────────────────────────────────────╯
```

> [!NOTE]
> The `peerId` appears to be used as a network level identity for node peers and is a hash based identity of the account, i.e. both the public key / address and the `peerId` are derived from teh same data.


### `secp256k1`

Running:

```sh
sui keytool generate secp256k1
```

Results in:

```text
╭─────────────────┬───────────────────────────────────────────────────────────────────────╮
│ alias           │                                                                       │
│ suiAddress      │  0xa659515aaed4459c72e867113bbd6c0a6883d9e6f231f13aabcc0052f4428ed0   │
│ publicBase64Key │  AQJfjD1toXER/xzUAMf+EhdsWJasN52awO4VvIN8nFN+8A==                     │
│ keyScheme       │  secp256k1                                                            │
│ flag            │  1                                                                    │
│ mnemonic        │  junk junk junk junk junk junk junk junk junk junk junk test          │
│ peerId          │                                                                       │
╰─────────────────┴───────────────────────────────────────────────────────────────────────╯
```

### `secp256r1`

Running:

```sh
sui keytool generate secp256r1
```

Results in:

```text
╭─────────────────┬──────────────────────────────────────────────────────────────────────╮
│ alias           │                                                                      │
│ suiAddress      │  0x51faf472582aca72e60ceef9e28fa02c91728eec6e1eccd28f45885ecc746517  │
│ publicBase64Key │  AgK99SUHMRsCbG+pCIH8x86oXmC7bRZlS4pEfKyBrrqGtw==                    │
│ keyScheme       │  secp256r1                                                           │
│ flag            │  2                                                                   │
│ mnemonic        │  junk junk junk junk junk junk junk junk junk junk junk test         │
│ peerId          │                                                                      │
╰─────────────────┴──────────────────────────────────────────────────────────────────────╯
```

### Notes

In each case the mnemonic is shown in the output, this assumes a default derivation path, i.e. `m/44'/784'/0'/0'/0'` for ed25519. Most Sui wallet's don't however provide much support for modifying the derivation path or account index effectively meaning it's one account per mnemonic. For Example:

```
m/44'/784'/0'/0'/0' → 0xfadda168a7526781256a8d199ee4c8400cf313a814c01667cb0f2d2b25e32ef1
m/44'/784'/0'/0'/1' → 0xc812e35e609136ab14560d0823357e9f331f91e987833db0dac858ccdfdbd397
m/44'/784'/0'/0'/2' → 0xac7dcad9cf5af97df11bd0b4c52b32216717b3466fc6fede88daa8adeda8db0b
m/44'/784'/0'/0'/3' → 0x80569f1c51673d26da075e798f9a440e88f93f282f0538b4b53cc62b29305817
m/44'/784'/0'/0'/4' → 0x0eb7398ac5f74445b20360233bb250e3fb6c6cd6098621640b801f5746c81127
```

Unlike Ethereum Sui expects private keys to be in a specific format, specifically `suiprivkey1...` which is a `Bech32` encoded string, similar to Bitcoin's Segwit `bc1` private keys.

Even if the same mnemonic or private key is used with different signature schemes, the public address will differ because it's composed of the scheme `flag` byte and the raw public key.
