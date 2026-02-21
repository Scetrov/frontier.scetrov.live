+++
title = '29. Unsafe BCS Parsing'
date = '2025-11-26T21:42:46Z'
weight = 29
+++

## Overview

Unsafe BCS (Binary Canonical Serialization) parsing occurs when smart contracts or off-chain systems improperly deserialize BCS-encoded data, leading to type confusion, buffer overflows, or malformed data acceptance. BCS is Sui's standard serialization format, used for transaction data, object serialization, and cross-module communication. Improper parsing can lead to security vulnerabilities both on-chain and in off-chain indexers.

## Risk Level

**High** — Can lead to type confusion attacks, data corruption, or off-chain system compromise.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE |
 | -------------- | ----------- |
 | A08 (Software and Data Integrity Failures) | CWE-502 (Deserialization of Untrusted Data), CWE-116 (Improper Encoding or Escaping of Output) |

## The Problem

### Common BCS Parsing Issues

 | Issue | Risk | Description |
 | ------- | ------ | ------------- |
 | No length validation | Critical | Buffer overrun on malformed data |
 | Type confusion | High | Deserializing as wrong type |
 | Trusting external BCS data | High | Accepting unvalidated serialized input |
 | Incomplete deserialization | Medium | Ignoring trailing bytes |
 | Off-chain parsing errors | Medium | Indexer crashes or corruption |

## BCS Format Basics

``` move
BCS Encoding Rules:
- Integers: Little-endian, fixed width
- Booleans: Single byte (0 or 1)
- Vectors: Length prefix (ULEB128) + elements
- Structs: Fields in declaration order
- Options: 0 for None, 1 + value for Some
- Strings: Length-prefixed UTF-8 bytes
```

## Vulnerable Example

```move
module vulnerable::parser {
    use sui::bcs;
    use std::vector;

    public struct UserData has drop {
        name: vector<u8>,
        balance: u64,
        is_admin: bool,
    }

    /// VULNERABLE: Trusts external BCS data without validation
    public entry fun process_external_data(
        raw_data: vector<u8>,
        ctx: &mut TxContext
    ) {
        // VULNERABLE: Deserializing untrusted external data
        let mut bcs_data = bcs::new(raw_data);

        // VULNERABLE: No try/catch - will abort on malformed data
        let name = bcs::peel_vec_u8(&mut bcs_data);
        let balance = bcs::peel_u64(&mut bcs_data);
        let is_admin = bcs::peel_bool(&mut bcs_data);

        // VULNERABLE: No validation of deserialized values
        // Attacker could set is_admin = true

        if (is_admin) {
            // Grant admin privileges based on untrusted data!
        };
    }

    /// VULNERABLE: No length bounds on vectors
    public fun deserialize_list(data: vector<u8>): vector<u64> {
        let mut bcs_data = bcs::new(data);

        // VULNERABLE: Vector could be arbitrarily large
        // Attacker sends vector with length = MAX_U64
        let length = bcs::peel_vec_length(&mut bcs_data);

        let mut result = vector::empty();
        let mut i = 0;
        while (i < length) {
            // This loop could run forever or exhaust gas
            vector::push_back(&mut result, bcs::peel_u64(&mut bcs_data));
            i = i + 1;
        };

        result
    }

    /// VULNERABLE: Ignores remaining bytes
    public fun parse_partial(data: vector<u8>): u64 {
        let mut bcs_data = bcs::new(data);
        let value = bcs::peel_u64(&mut bcs_data);

        // VULNERABLE: Doesn't check if there's remaining data
        // Attacker could append malicious trailing data

        value
    }
}

module vulnerable::oracle {
    use sui::bcs;

    public struct PriceUpdate has drop {
        asset: vector<u8>,
        price: u64,
        timestamp: u64,
    }

    /// VULNERABLE: Accepts any BCS data as oracle update
    public entry fun update_price(
        oracle: &mut Oracle,
        price_data: vector<u8>,
        _ctx: &mut TxContext
    ) {
        let mut bcs = bcs::new(price_data);

        // VULNERABLE: No signature verification
        // Anyone can submit fake price data
        let asset = bcs::peel_vec_u8(&mut bcs);
        let price = bcs::peel_u64(&mut bcs);
        let timestamp = bcs::peel_u64(&mut bcs);

        // Directly use unverified data
        update_oracle_internal(oracle, asset, price, timestamp);
    }
}

module vulnerable::bridge {
    use sui::bcs;

    /// VULNERABLE: Cross-chain message parsing without validation
    public entry fun receive_message(
        bridge: &mut Bridge,
        message_bytes: vector<u8>,
        ctx: &mut TxContext
    ) {
        let mut bcs = bcs::new(message_bytes);

        // VULNERABLE: Type field controls execution
        let message_type = bcs::peel_u8(&mut bcs);

        if (message_type == 0) {
            // Transfer
            let recipient = bcs::peel_address(&mut bcs);
            let amount = bcs::peel_u64(&mut bcs);
            // Execute transfer without verifying message source
            execute_transfer(bridge, recipient, amount, ctx);
        } else if (message_type == 1) {
            // Admin command - CRITICAL vulnerability
            let new_admin = bcs::peel_address(&mut bcs);
            bridge.admin = new_admin;  // Attacker becomes admin!
        };
    }
}
```

### Off-Chain Vulnerability (TypeScript)

```typescript
// VULNERABLE: Off-chain BCS parsing
function parseUserData(bcsBytes: Uint8Array): UserData {
    const reader = new BcsReader(bcsBytes);

    // VULNERABLE: No bounds checking
    const nameLength = reader.readULEB128();
    const name = reader.readBytes(nameLength);  // Could overflow

    const balance = reader.readU64();
    const isAdmin = reader.readBool();

    // VULNERABLE: Type coercion issues
    return {
        name: new TextDecoder().decode(name),
        balance: Number(balance),  // Loses precision for large values!
        isAdmin: isAdmin
    };
}

// VULNERABLE: Indexer trusts on-chain data
async function indexEvents(events: SuiEvent[]) {
    for (const event of events) {
        // VULNERABLE: Assumes well-formed BCS
        const parsed = bcs.de('EventStruct', event.bcs);

        // VULNERABLE: No validation before database insert
        await db.insert('events', parsed);
    }
}
```

## Secure Example

```move
module secure::parser {
    use sui::bcs::{Self, BCS};
    use std::vector;

    const E_INVALID_DATA: u64 = 1;
    const E_NAME_TOO_LONG: u64 = 2;
    const E_TRAILING_DATA: u64 = 3;
    const E_INVALID_BOOL: u64 = 4;
    const E_LIST_TOO_LONG: u64 = 5;

    const MAX_NAME_LENGTH: u64 = 256;
    const MAX_LIST_LENGTH: u64 = 1000;

    public struct UserData has drop {
        name: vector<u8>,
        balance: u64,
        is_admin: bool,
    }

    /// SECURE: Validates BCS data with bounds checking
    public fun deserialize_user_data(data: vector<u8>): UserData {
        let data_len = vector::length(&data);

        // Minimum size: 1 byte name length + 8 bytes balance + 1 byte bool
        assert!(data_len >= 10, E_INVALID_DATA);

        let mut bcs = bcs::new(data);

        // Parse with validation
        let name = peel_bounded_vec_u8(&mut bcs, MAX_NAME_LENGTH);
        let balance = bcs::peel_u64(&mut bcs);
        let is_admin = peel_validated_bool(&mut bcs);

        // SECURE: Verify no trailing data
        assert!(bcs::into_remainder_bytes(bcs) == vector::empty(), E_TRAILING_DATA);

        UserData { name, balance, is_admin }
    }

    /// SECURE: Bounded vector deserialization
    fun peel_bounded_vec_u8(bcs: &mut BCS, max_len: u64): vector<u8> {
        let length = bcs::peel_vec_length(bcs);
        assert!(length <= max_len, E_NAME_TOO_LONG);

        let mut result = vector::empty();
        let mut i = 0;
        while (i < length) {
            vector::push_back(&mut result, bcs::peel_u8(bcs));
            i = i + 1;
        };

        result
    }

    /// SECURE: Validate boolean is 0 or 1
    fun peel_validated_bool(bcs: &mut BCS): bool {
        let byte = bcs::peel_u8(bcs);
        assert!(byte == 0 || byte == 1, E_INVALID_BOOL);
        byte == 1
    }

    /// SECURE: Bounded list deserialization
    public fun deserialize_bounded_list(
        data: vector<u8>,
        max_length: u64
    ): vector<u64> {
        let mut bcs = bcs::new(data);
        let length = bcs::peel_vec_length(&mut bcs);

        // SECURE: Enforce maximum length
        assert!(length <= max_length, E_LIST_TOO_LONG);
        assert!(length <= MAX_LIST_LENGTH, E_LIST_TOO_LONG);

        let mut result = vector::empty();
        let mut i = 0;
        while (i < length) {
            vector::push_back(&mut result, bcs::peel_u64(&mut bcs));
            i = i + 1;
        };

        // SECURE: Check no trailing data
        assert!(bcs::into_remainder_bytes(bcs) == vector::empty(), E_TRAILING_DATA);

        result
    }
}

module secure::oracle {
    use sui::bcs;
    use sui::ed25519;
    use sui::clock::{Self, Clock};

    const E_INVALID_SIGNATURE: u64 = 1;
    const E_STALE_DATA: u64 = 2;
    const E_INVALID_ASSET: u64 = 3;
    const E_TRAILING_DATA: u64 = 4;

    const MAX_STALENESS_MS: u64 = 60_000;
    const MAX_ASSET_NAME: u64 = 32;

    public struct SignedPriceUpdate has drop {
        asset: vector<u8>,
        price: u64,
        timestamp: u64,
        signature: vector<u8>,
    }

    /// SECURE: Validates signature and data before use
    public entry fun update_price(
        oracle: &mut Oracle,
        price_data: vector<u8>,
        clock: &Clock,
        _ctx: &mut TxContext
    ) {
        // Parse the signed message
        let update = parse_signed_update(price_data);

        // SECURE: Verify signature from trusted oracle
        let message = create_price_message(&update.asset, update.price, update.timestamp);
        let valid = ed25519::ed25519_verify(
            &update.signature,
            &oracle.oracle_pubkey,
            &message
        );
        assert!(valid, E_INVALID_SIGNATURE);

        // SECURE: Check timestamp freshness
        let current_time = clock::timestamp_ms(clock);
        assert!(current_time - update.timestamp <= MAX_STALENESS_MS, E_STALE_DATA);

        // SECURE: Validate asset name
        assert!(is_valid_asset(&update.asset), E_INVALID_ASSET);

        // Now safe to update
        update_oracle_internal(oracle, update.asset, update.price, update.timestamp);
    }

    fun parse_signed_update(data: vector<u8>): SignedPriceUpdate {
        let mut bcs = bcs::new(data);

        let asset = peel_bounded_vec(&mut bcs, MAX_ASSET_NAME);
        let price = bcs::peel_u64(&mut bcs);
        let timestamp = bcs::peel_u64(&mut bcs);
        let signature = peel_fixed_vec(&mut bcs, 64);  // Ed25519 sig is 64 bytes

        // Check no trailing data
        assert!(bcs::into_remainder_bytes(bcs) == vector::empty(), E_TRAILING_DATA);

        SignedPriceUpdate { asset, price, timestamp, signature }
    }

    fun peel_bounded_vec(bcs: &mut BCS, max_len: u64): vector<u8> {
        let len = bcs::peel_vec_length(bcs);
        assert!(len <= max_len, E_INVALID_ASSET);

        let mut result = vector::empty();
        let mut i = 0;
        while (i < len) {
            vector::push_back(&mut result, bcs::peel_u8(bcs));
            i = i + 1;
        };
        result
    }

    fun peel_fixed_vec(bcs: &mut BCS, expected_len: u64): vector<u8> {
        let mut result = vector::empty();
        let mut i = 0;
        while (i < expected_len) {
            vector::push_back(&mut result, bcs::peel_u8(bcs));
            i = i + 1;
        };
        result
    }

    fun is_valid_asset(asset: &vector<u8>): bool {
        // Validate asset name format
        let len = vector::length(asset);
        if (len == 0 || len > MAX_ASSET_NAME) {
            return false
        };
        // Additional validation (alphanumeric, etc.)
        true
    }

    fun create_price_message(asset: &vector<u8>, price: u64, timestamp: u64): vector<u8> {
        let mut msg = vector::empty();
        vector::append(&mut msg, *asset);
        vector::append(&mut msg, bcs::to_bytes(&price));
        vector::append(&mut msg, bcs::to_bytes(&timestamp));
        msg
    }
}

module secure::bridge {
    use sui::bcs;
    use sui::hash;

    const E_INVALID_MESSAGE_TYPE: u64 = 1;
    const E_INVALID_PROOF: u64 = 2;
    const E_MESSAGE_ALREADY_PROCESSED: u64 = 3;
    const E_TRAILING_DATA: u64 = 4;

    /// SECURE: Validated cross-chain message
    public entry fun receive_message(
        bridge: &mut Bridge,
        message_bytes: vector<u8>,
        merkle_proof: vector<vector<u8>>,
        ctx: &mut TxContext
    ) {
        // SECURE: Verify message is in merkle tree from trusted source
        let message_hash = hash::keccak256(&message_bytes);
        assert!(verify_merkle_proof(bridge, message_hash, merkle_proof), E_INVALID_PROOF);

        // SECURE: Check message not already processed
        assert!(!is_processed(bridge, message_hash), E_MESSAGE_ALREADY_PROCESSED);
        mark_processed(bridge, message_hash);

        // Now safe to parse
        let mut bcs = bcs::new(message_bytes);
        let message_type = bcs::peel_u8(&mut bcs);

        // SECURE: Only allow expected message types
        assert!(message_type == 0, E_INVALID_MESSAGE_TYPE);  // Only transfers allowed

        let recipient = bcs::peel_address(&mut bcs);
        let amount = bcs::peel_u64(&mut bcs);

        // Check no trailing data
        assert!(bcs::into_remainder_bytes(bcs) == vector::empty(), E_TRAILING_DATA);

        // Execute validated transfer
        execute_transfer(bridge, recipient, amount, ctx);

        // No admin commands accepted via external messages!
    }
}
```

### Secure Off-Chain Parsing (TypeScript)

```typescript
import { bcs } from '@mysten/sui/bcs';

const MAX_NAME_LENGTH = 256;
const MAX_BALANCE = BigInt("18446744073709551615"); // u64 max

interface UserData {
    name: string;
    balance: bigint;  // Use bigint for u64
    isAdmin: boolean;
}

// SECURE: Validated BCS parsing
function parseUserDataSafe(bcsBytes: Uint8Array): UserData {
    // Define schema explicitly
    const UserDataSchema = bcs.struct('UserData', {
        name: bcs.vector(bcs.u8()),
        balance: bcs.u64(),
        isAdmin: bcs.bool(),
    });

    let parsed;
    try {
        parsed = UserDataSchema.parse(bcsBytes);
    } catch (e) {
        throw new Error(`Invalid BCS data: ${e.message}`);
    }

    // SECURE: Validate parsed values
    if (parsed.name.length > MAX_NAME_LENGTH) {
        throw new Error('Name too long');
    }

    // SECURE: Keep as bigint to avoid precision loss
    const balance = BigInt(parsed.balance);
    if (balance > MAX_BALANCE) {
        throw new Error('Invalid balance');
    }

    // SECURE: Validate UTF-8
    let name: string;
    try {
        name = new TextDecoder('utf-8', { fatal: true }).decode(
            new Uint8Array(parsed.name)
        );
    } catch {
        throw new Error('Invalid UTF-8 in name');
    }

    return {
        name,
        balance,
        isAdmin: parsed.isAdmin
    };
}

// SECURE: Indexer with validation
async function indexEventsSafe(events: SuiEvent[]) {
    for (const event of events) {
        try {
            // Validate event structure
            if (!event.bcs || !event.type) {
                console.warn('Malformed event, skipping');
                continue;
            }

            // Parse with schema validation
            const schema = getSchemaForEventType(event.type);
            const parsed = schema.parse(
                Uint8Array.from(Buffer.from(event.bcs, 'base64'))
            );

            // Validate parsed data
            const validated = validateEventData(parsed, event.type);

            // Safe to insert
            await db.insert('events', {
                ...validated,
                raw_bcs: event.bcs,  // Keep original for debugging
                indexed_at: new Date()
            });
        } catch (e) {
            console.error(`Failed to index event: ${e.message}`);
            // Don't crash indexer, log and continue
            await db.insert('failed_events', {
                event_bcs: event.bcs,
                error: e.message,
                timestamp: new Date()
            });
        }
    }
}
```

## BCS Parsing Patterns

### Pattern 1: Schema Definition

```move
/// Define expected schema clearly
public struct Message has drop {
    version: u8,      // 1 byte
    msg_type: u8,     // 1 byte
    payload_len: u64, // 8 bytes
    payload: vector<u8>,
}

/// Parse according to schema
fun parse_message(data: vector<u8>): Message {
    assert!(vector::length(&data) >= 10, E_TOO_SHORT);

    let mut bcs = bcs::new(data);
    let version = bcs::peel_u8(&mut bcs);
    let msg_type = bcs::peel_u8(&mut bcs);
    let payload_len = bcs::peel_u64(&mut bcs);

    // Validate payload length matches actual
    let payload = peel_fixed_vec(&mut bcs, payload_len);

    assert!(bcs::into_remainder_bytes(bcs) == vector::empty(), E_TRAILING);

    Message { version, msg_type, payload_len, payload }
}
```

### Pattern 2: Version Checking

```move
const CURRENT_VERSION: u8 = 2;
const MIN_SUPPORTED_VERSION: u8 = 1;

fun parse_versioned(data: vector<u8>): ParsedData {
    let mut bcs = bcs::new(data);
    let version = bcs::peel_u8(&mut bcs);

    assert!(version >= MIN_SUPPORTED_VERSION, E_VERSION_TOO_OLD);
    assert!(version <= CURRENT_VERSION, E_VERSION_TOO_NEW);

    if (version == 1) {
        parse_v1(&mut bcs)
    } else {
        parse_v2(&mut bcs)
    }
}
```

### Pattern 3: Safe Wrapper Functions

```move
/// Safe u64 with bounds
fun peel_bounded_u64(bcs: &mut BCS, max: u64): u64 {
    let value = bcs::peel_u64(bcs);
    assert!(value <= max, E_VALUE_TOO_LARGE);
    value
}

/// Safe address with validation
fun peel_valid_address(bcs: &mut BCS): address {
    let addr = bcs::peel_address(bcs);
    assert!(addr != @0x0, E_ZERO_ADDRESS);
    addr
}

/// Safe string (UTF-8 validated)
fun peel_utf8_string(bcs: &mut BCS, max_len: u64): String {
    let bytes = peel_bounded_vec_u8(bcs, max_len);
    // std::string::utf8 validates UTF-8
    std::string::utf8(bytes)
}
```

## Recommended Mitigations

### 1. Always Bound Vector Lengths

```move
let length = bcs::peel_vec_length(&mut bcs);
assert!(length <= MAX_ALLOWED, E_TOO_LONG);
```

### 2. Check for Trailing Data

```move
let remainder = bcs::into_remainder_bytes(bcs);
assert!(remainder == vector::empty(), E_TRAILING_DATA);
```

### 3. Validate After Deserialization

```move
let data = deserialize(bytes);
assert!(data.amount > 0, E_INVALID_AMOUNT);
assert!(data.recipient != @0x0, E_INVALID_RECIPIENT);
```

### 4. Use Cryptographic Verification

```move
// Don't trust BCS data without proof
assert!(verify_signature(data, signature, pubkey), E_INVALID_SIG);
```

### 5. Handle Parsing Failures Gracefully

```typescript
try {
    const parsed = schema.parse(bytes);
} catch (e) {
    // Log error, don't crash
    handleParseError(e, bytes);
}
```

## Testing Checklist

- [ ] Test with malformed BCS data (truncated, extra bytes)
- [ ] Test with maximum length vectors
- [ ] Test with invalid boolean values (not 0 or 1)
- [ ] Verify trailing data is rejected
- [ ] Test version compatibility
- [ ] Verify signature validation cannot be bypassed
- [ ] Test off-chain parsers with fuzzed input
- [ ] Check u64 values don't lose precision in JavaScript

## Related Vulnerabilities

- [Oracle Validation Failures](../oracle-validation-failures/)
- [Unvalidated Struct Fields](../unvalidated-struct-fields/)
- [General Move Logic Errors](../general-move-logic-errors/)
- [Access-Control Mistakes](../access-control-mistakes/)
