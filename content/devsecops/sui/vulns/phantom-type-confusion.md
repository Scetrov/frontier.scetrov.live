+++
title = '12. Phantom Type Confusion'
date = '2025-11-26T00:00:00Z'
weight = 12
+++

## Overview

Phantom type parameters in Move are type parameters that don't affect the runtime representation of a struct. Attackers can inject structurally-identical types with different phantom parameters, bypassing type-based security checks.

## Risk Level

**High** — Can bypass type-based access control and asset isolation.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A04 (Insecure Design) | CWE-693 (Protection Mechanism Failure), CWE-704 (Incorrect Type Conversion) |

## The Problem

### Phantom Types Explained

```move
/// `phantom` means T doesn't appear in any field
public struct Coin<phantom T> has key, store {
    id: UID,
    value: u64,
}

/// At runtime, Coin<SUI> and Coin<USDC> have identical layouts
/// Only the type parameter differs
```

### The Vulnerability

If your code doesn't verify the phantom type parameter, attackers can:
1. Create their own type that "looks like" the expected type
2. Pass objects with fake phantom types
3. Bypass type-based security or asset separation

## Vulnerable Example

```move
module vulnerable::pool {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::coin::{Self, Coin};

    /// Pool for any coin type
    public struct Pool<phantom T> has key {
        id: UID,
        balance: u64,
        coin_store: Coin<T>,
    }

    /// VULNERABLE: No verification that T is the expected type
    public entry fun deposit<T>(
        pool: &mut Pool<T>,
        coin: Coin<T>,
    ) {
        let amount = coin::value(&coin);
        pool.balance = pool.balance + amount;
        coin::join(&mut pool.coin_store, coin);
    }

    /// VULNERABLE: Anyone can create a Pool with a fake type
    public fun create_pool<T>(
        initial_coin: Coin<T>,
        ctx: &mut TxContext
    ): Pool<T> {
        Pool {
            id: object::new(ctx),
            balance: coin::value(&initial_coin),
            coin_store: initial_coin,
        }
    }
}

module vulnerable::lending {
    use sui::coin::Coin;

    public struct PriceOracle<phantom T> has key {
        id: UID,
        price_usd: u64,
    }

    /// VULNERABLE: Trusts any oracle with matching phantom type
    public entry fun borrow<T>(
        oracle: &PriceOracle<T>,
        collateral: Coin<T>,
        borrow_amount: u64,
    ) {
        // Attacker creates fake oracle with inflated price
        let collateral_value = coin::value(&collateral) * oracle.price_usd;
        
        // Borrow against inflated value
        assert!(borrow_amount <= collateral_value / 2, E_UNDERCOLLATERALIZED);
        // ...
    }
}
```

### Attack Scenario

```move
/// Attacker's fake token that mimics SUI
module attacker::fake_sui {
    public struct FAKE_SUI has drop {}
}

module attack::exploit {
    use vulnerable::lending::{Self, PriceOracle};
    use attacker::fake_sui::FAKE_SUI;
    use sui::coin;

    public entry fun exploit(ctx: &mut TxContext) {
        // Create a fake oracle with inflated price
        let fake_oracle = PriceOracle<FAKE_SUI> {
            id: object::new(ctx),
            price_usd: 1_000_000_000,  // Fake $1B price
        };
        
        // Create worthless fake coins
        let fake_coins = coin::zero<FAKE_SUI>(ctx);
        
        // Borrow against "valuable" fake collateral
        lending::borrow<FAKE_SUI>(
            &fake_oracle,
            fake_coins,
            999_999_999,  // Borrow almost a billion
        );
    }
}
```

## Secure Example

```move
module secure::pool {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::TxContext;
    use sui::coin::{Self, Coin, CoinMetadata};
    use sui::transfer;
    use std::type_name::{Self, TypeName};

    /// Registry of approved coin types
    public struct CoinRegistry has key {
        id: UID,
        approved_types: vector<TypeName>,
    }

    /// Pool with verified coin type
    public struct Pool<phantom T> has key {
        id: UID,
        coin_type: TypeName,  // Store the actual type for verification
        balance: u64,
        coin_store: Coin<T>,
    }

    /// SECURE: Verify coin type is approved
    public entry fun create_pool<T>(
        registry: &CoinRegistry,
        metadata: &CoinMetadata<T>,  // Requires official metadata
        initial_coin: Coin<T>,
        ctx: &mut TxContext
    ) {
        let coin_type = type_name::get<T>();
        
        // Verify type is in approved registry
        assert!(
            vector::contains(&registry.approved_types, &coin_type),
            E_UNAPPROVED_COIN
        );
        
        transfer::share_object(Pool<T> {
            id: object::new(ctx),
            coin_type,
            balance: coin::value(&initial_coin),
            coin_store: initial_coin,
        });
    }

    /// SECURE: Verify pool's coin type matches
    public entry fun deposit<T>(
        pool: &mut Pool<T>,
        coin: Coin<T>,
    ) {
        // Type T is enforced by the borrow checker
        // But we can add extra verification
        assert!(pool.coin_type == type_name::get<T>(), E_TYPE_MISMATCH);
        
        let amount = coin::value(&coin);
        pool.balance = pool.balance + amount;
        coin::join(&mut pool.coin_store, coin);
    }
}

module secure::lending {
    use sui::object::{Self, UID, ID};
    use sui::coin::{Self, Coin};
    use std::type_name::{Self, TypeName};

    /// Oracle with verified type and trusted source
    public struct TrustedOracle has key {
        id: UID,
        /// Maps type name to price
        prices: Table<TypeName, PriceData>,
        /// Only this address can update prices
        oracle_admin: address,
    }

    public struct PriceData has store {
        price_usd: u64,
        last_update: u64,
        decimals: u8,
    }

    /// SECURE: Oracle verifies types internally
    public entry fun borrow<T>(
        oracle: &TrustedOracle,
        collateral: Coin<T>,
        borrow_amount: u64,
        ctx: &TxContext
    ) {
        let coin_type = type_name::get<T>();
        
        // Get price from trusted oracle
        assert!(table::contains(&oracle.prices, coin_type), E_UNKNOWN_ASSET);
        let price_data = table::borrow(&oracle.prices, coin_type);
        
        // Check freshness
        assert!(
            clock::timestamp_ms(clock) - price_data.last_update < MAX_STALENESS,
            E_STALE_PRICE
        );
        
        let collateral_value = coin::value(&collateral) * price_data.price_usd;
        assert!(borrow_amount <= collateral_value / 2, E_UNDERCOLLATERALIZED);
        
        // ... proceed with borrow
    }
}
```

## Type Verification Patterns

### Pattern 1: Type Name Registry

```move
use std::type_name::{Self, TypeName};

public struct TypeRegistry has key {
    id: UID,
    allowed_types: vector<TypeName>,
}

public fun verify_type<T>(registry: &TypeRegistry) {
    let t = type_name::get<T>();
    assert!(vector::contains(&registry.allowed_types, &t), E_INVALID_TYPE);
}
```

### Pattern 2: Witness-Based Type Verification

```move
/// Only the module defining T can create this witness
public struct TypeWitness<phantom T> has drop {}

/// Require witness to prove type authenticity
public fun verified_action<T>(
    _witness: TypeWitness<T>,
    ...
) {
    // Only code with access to T's module can call this
}
```

### Pattern 3: Coin Metadata Verification

```move
use sui::coin::CoinMetadata;

/// Require CoinMetadata proves the type is a real coin
public fun deposit_verified<T>(
    _metadata: &CoinMetadata<T>,
    coin: Coin<T>,
    ...
) {
    // CoinMetadata only exists for properly created coins
}
```

### Pattern 4: Store Type Information

```move
public struct TypedContainer<phantom T> has key {
    id: UID,
    stored_type: TypeName,  // Remember what T was
    data: vector<u8>,
}

public fun verify_container<T>(container: &TypedContainer<T>) {
    assert!(container.stored_type == type_name::get<T>(), E_TYPE_MISMATCH);
}
```

## Recommended Mitigations

### 1. Use Type Name for Verification

```move
use std::type_name;

public fun operation<T>(...) {
    let type_name = type_name::get<T>();
    // Compare against expected types
}
```

### 2. Require Official Artifacts

```move
/// For coins, require CoinMetadata
public fun coin_operation<T>(
    metadata: &CoinMetadata<T>,  // Proves T is a real coin
    coin: Coin<T>,
) { }
```

### 3. Maintain Type Whitelists

```move
public struct Config has key {
    id: UID,
    allowed_types: vector<TypeName>,
}

public fun add_allowed_type(cap: &AdminCap, config: &mut Config, type_name: TypeName) {
    vector::push_back(&mut config.allowed_types, type_name);
}
```

### 4. Use One-Time-Witness Pattern

```move
/// OTW guarantees type uniqueness
public struct MY_TOKEN has drop {}

public fun init(witness: MY_TOKEN, ctx: &mut TxContext) {
    // Only called once, witness proves authenticity
}
```

## Testing Checklist

- [ ] Test with attacker-created types that mimic expected types
- [ ] Verify type registry correctly rejects unknown types
- [ ] Test that phantom type verification catches mismatches
- [ ] Confirm OTW pattern is used for critical type creation
- [ ] Audit all generic functions for phantom type assumptions

## Related Vulnerabilities

- [Access-Control Mistakes](../access-control-mistakes/)
- [Oracle Validation Failures](../oracle-validation-failures/)
- [Capability Leakage](../capability-leakage/)
