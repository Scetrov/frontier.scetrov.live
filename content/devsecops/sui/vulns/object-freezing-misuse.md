+++
title = '2. Object Freezing Misuse'
date = '2025-11-26T00:00:00Z'
weight = 2
+++

## Overview

Objects with `key + store` abilities can be frozen by any holder using `sui::transfer::public_freeze_object`. Once frozen, an object becomes **immutable** and **globally readable**. This can be exploited to permanently disable critical protocol functionality or expose sensitive data.

## Risk Level

**High** — Can permanently break protocol functionality with no recovery path.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-732 (Incorrect Permission Assignment) |

## The Problem

When you expose an object by value (returning it from a function), the caller gains full control including the ability to freeze it. If that object is your protocol's treasury, configuration, or any mutable state, freezing it permanently disables all mutations.

### Frozen Object Characteristics

- **Immutable forever** — No function can ever mutate the object again
- **Globally accessible** — Anyone can read the frozen object's data
- **No recovery** — There is no "unfreeze" operation in Sui

## Vulnerable Example

```move
module vulnerable::treasury {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    public struct Treasury has key, store {
        id: UID,
        funds: Coin<SUI>,
        fee_bps: u64,
    }

    public struct State has key {
        id: UID,
        treasury: Treasury,  // Treasury stored inline
    }

    /// VULNERABLE: Returns treasury by value!
    /// Caller can freeze it, permanently breaking the protocol
    public fun take_treasury(state: &mut State): Treasury {
        let treasury = state.treasury;  // Move out
        // ... some logic
        treasury  // Returns by value — caller now owns it!
    }

    /// VULNERABLE: Exposes treasury for "temporary" use
    public fun borrow_treasury_unsafe(state: &mut State): Treasury {
        state.treasury  // Caller gets ownership!
    }

    /// Deposit funds — will fail if treasury is frozen
    public entry fun deposit(
        state: &mut State, 
        payment: Coin<SUI>
    ) {
        coin::join(&mut state.treasury.funds, payment);
    }
}
```

### Attack Scenario

```move
// Attacker's transaction
module attack::freeze_treasury {
    use vulnerable::treasury;
    use sui::transfer;

    public entry fun attack(state: &mut treasury::State) {
        // Step 1: Extract treasury by value
        let treasury = treasury::take_treasury(state);
        
        // Step 2: Freeze it permanently
        transfer::public_freeze_object(treasury);
        
        // Protocol is now permanently broken!
        // No deposits, withdrawals, or fee changes possible
    }
}
```

## Secure Example

```move
module secure::treasury {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    /// SECURE: No `store` ability — cannot be frozen by external callers
    public struct Treasury has key {
        id: UID,
        funds: Coin<SUI>,
        fee_bps: u64,
    }

    public struct AdminCap has key {
        id: UID,
    }

    public struct State has key {
        id: UID,
        treasury_id: object::ID,  // Store reference, not object
    }

    /// SECURE: Only exposes immutable reference
    public fun get_balance(treasury: &Treasury): u64 {
        coin::value(&treasury.funds)
    }

    /// SECURE: Only exposes mutable reference, not ownership
    public fun deposit(
        treasury: &mut Treasury,
        payment: Coin<SUI>
    ) {
        coin::join(&mut treasury.funds, payment);
    }

    /// SECURE: Withdrawal requires capability and returns Coin, not Treasury
    public fun withdraw(
        _cap: &AdminCap,
        treasury: &mut Treasury,
        amount: u64,
        ctx: &mut TxContext
    ): Coin<SUI> {
        coin::split(&mut treasury.funds, amount, ctx)
    }

    /// If freezing is intentional, make it explicit and controlled
    public entry fun intentional_freeze(
        _cap: AdminCap,  // Consume the cap
        treasury: Treasury
    ) {
        // Only admin can freeze, and it's a deliberate action
        sui::transfer::freeze_object(treasury);
    }
}
```

## Recommended Mitigations

### 1. Remove `store` from Critical Objects

```move
/// Without `store`, public_freeze_object cannot be called
public struct Treasury has key {
    id: UID,
    // ...
}
```

### 2. Never Return Critical Objects by Value

```move
/// BAD: Returns ownership
public fun get_treasury(state: &mut State): Treasury { ... }

/// GOOD: Returns immutable reference
public fun get_treasury(state: &State): &Treasury { ... }

/// GOOD: Returns mutable reference
public fun get_treasury_mut(state: &mut State): &mut Treasury { ... }
```

### 3. Use Dynamic Fields for Encapsulation

```move
use sui::dynamic_field as df;

public struct State has key {
    id: UID,
}

/// Treasury is stored as dynamic field — not directly accessible
fun init(ctx: &mut TxContext) {
    let state = State { id: object::new(ctx) };
    df::add(&mut state.id, b"treasury", Treasury { 
        id: object::new(ctx),
        funds: coin::zero(ctx),
        fee_bps: 100,
    });
    transfer::share_object(state);
}

/// Access only via controlled functions
public fun deposit(state: &mut State, payment: Coin<SUI>) {
    let treasury: &mut Treasury = df::borrow_mut(&mut state.id, b"treasury");
    coin::join(&mut treasury.funds, payment);
}
```

### 4. Separate Data from Control

```move
/// Freeze-safe pattern: separate mutable data from immutable config
public struct TreasuryConfig has key {
    id: UID,
    fee_bps: u64,
    admin: address,
}

/// This can be shared and is safe to freeze (config becomes permanent)
public struct TreasuryVault has key {
    id: UID,
    config_id: object::ID,
    funds: Coin<SUI>,
}
```

## Testing Checklist

- [ ] Verify no functions return critical objects by value
- [ ] Confirm all state objects lack `store` ability unless necessary
- [ ] Test that `public_freeze_object` cannot be called on protocol-critical objects
- [ ] Audit all places where objects are moved out of storage

## Related Vulnerabilities

- [Object Transfer Misuse](../object-transfer-misuse/)
- [Ability Misconfiguration](../ability-misconfiguration/)
- [Read API Leakage](../read-api-leakage/)
