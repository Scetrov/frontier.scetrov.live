+++
date = '2026-11-23T00:00:00Z'
title = 'sig_verify.move'
weight = 1
codebase = "https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/crypto/sig_verify.move"
+++

The `sig_verify.move` module provides cryptographic signature verification functionality for validating off-chain signed messages on the Sui blockchain. It supports Ed25519 digital signature verification, enabling secure authentication of messages signed by external key pairs.

## 1. Core Component Architecture

The module is a stateless utility — it defines no structs or stored objects. Instead, it exposes pure functions for address derivation and signature verification.

```mermaid
flowchart LR
    subgraph Inputs
        PK[Public Key - 32 bytes]
        MSG[Message bytes]
        SIG[Signature - flag + sig + pk]
        ADDR[Expected Address]
    end

    subgraph sig_verify
        DERIVE[derive_address_from_public_key]
        VERIFY[verify_signature]
    end

    PK --> DERIVE --> DerivedAddr[Sui Address]
    MSG --> VERIFY
    SIG --> VERIFY
    ADDR --> VERIFY
    VERIFY --> Result[bool]
```

### Key Functions

* **`derive_address_from_public_key(public_key): address`** — Derives a Sui address from a raw Ed25519 public key by prepending the Ed25519 scheme flag (`0x00`) and hashing with Blake2b-256.
* **`verify_signature(message, signature, expected_address): bool`** — Verifies an Ed25519 signature against an expected Sui address. Handles the full Sui signature format (flag + signature bytes + public key bytes).

### Constants

| Constant           | Value  | Purpose                               |
| ------------------ | ------ | ------------------------------------- |
| `ED25519_FLAG`     | `0x00` | Sui signature scheme flag for Ed25519 |
| `ED25519_SIG_LEN`  | `64`   | Expected Ed25519 signature length     |
| `ED25519_PK_LEN`   | `32`   | Expected Ed25519 public key length    |

---

## 2. Signature Verification Flow

The `verify_signature` function follows a strict validation pipeline:

```mermaid
flowchart TD
    Start([verify_signature called]) --> Nonempty{At least one byte?}
    Nonempty -- No --> InvalidLen[abort EInvalidLen]
    Nonempty -- Yes --> ParseFlag[Extract scheme flag - byte 0]
    ParseFlag --> MatchScheme{Scheme?}
    MatchScheme -- Ed25519 --> CheckLength{Exactly 97 bytes?}
    MatchScheme -- Other --> Abort[abort EUnsupportedScheme]
    CheckLength -- No --> InvalidLen
    CheckLength -- Yes --> ExtractSig[Extract signature bytes 1 through 64]
    ExtractSig --> ExtractPK[Extract public key bytes 65 through 96]
    ExtractPK --> HashMsg[Hash intent prefix and message with Blake2b-256]
    HashMsg --> DeriveAddr[Derive address from public key]
    DeriveAddr --> CheckAddr{Address matches?}
    CheckAddr -- No --> ReturnFalse[return false]
    CheckAddr -- Yes --> Ed25519Verify[ed25519::ed25519_verify]
    Ed25519Verify --> Result([return bool])
```

### PersonalMessage Intent Protocol

The module uses Sui's `PersonalMessage` intent prefix (`0x030000`) when hashing messages:

* `0x03` — `IntentScope::PersonalMessage`
* `0x00` — `IntentVersion::V0`
* `0x00` — `AppId::Sui`

> [!NOTE]
> The verifier appends the supplied bytes directly, without adding a BCS encoding step. This matches the Go backend's `SignPersonalMessage` implementation. Callers can still supply bytes they have already serialized, as `location.move` does for proof messages.

---

## 3. Use Cases in EVE Frontier

This module is essential for scenarios requiring proof of ownership or authorization:

* **Location proofs** — `location.move` verifies signatures against the server address in the proof. The caller checks server authorization separately through `ServerAddressRegistry`.
* **Distance verification** — Gate linking uses a server-signed distance proof and checks the maximum distance configured for the gate type.

---

## 4. Security Patterns

* **Input validation** — Address derivation aborts unless the public key is 32 bytes. Signature verification aborts on an empty input, an unsupported scheme, or an Ed25519 envelope whose length is not 97 bytes. A mismatched address or a failed Ed25519 verification returns `false`.
* **Scheme Extensibility** — The `match` pattern on the flag byte is designed for future extension to additional signature schemes, though currently only Ed25519 is supported.
* **No State Side Effects** — As a pure utility module with no stored objects, there is no risk of state corruption or reentrancy.

{{% tip-menu-search %}}
