+++
title = '1. Object Transfer Misuse'
date = '2025-11-26T00:00:00Z'
weight = 1
+++

## Overview

Any **address-owned object with `key`** (especially combined with `store`) can be freely transferred using `sui::transfer::transfer` or `public_transfer`. This breaks assumptions about invariants, capability possession, and ownership that your contract may depend on.

## Risk Level

**High** — Can lead to complete bypass of access control mechanisms.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-275 (Permission Issues) | 

## The Problem

In Sui, objects with `key + store` abilities can be transferred by their owner to any address. If your contract issues capability objects or admin tokens and assumes they will remain with the original recipient, an attacker can transfer these objects to themselves or others, bypassing your intended access control.

### Common Mistakes

1. **Mixing authority models** — Using `sender()` checks in some functions and capability-based checks in others
2. **Assuming capability possession** — Expecting that whoever received a capability still holds it
3. **Transferable admin tokens** — Creating admin capabilities with `store` that can be freely moved

## Vulnerable Example

```move
module vulnerable::admin {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    /// VULNERABLE: This capability has `store`, allowing it to be transferred
    public struct AdminCap has key, store {
        id: UID,
    }

    public struct Treasury has key {
        id: UID,
        balance: u64,
    }

    /// Issue an admin cap to the deployer
    fun init(ctx: &mut TxContext) {
        transfer::transfer(
            AdminCap { id: object::new(ctx) },
            tx_context::sender(ctx)
        );
    }

    /// VULNERABLE: Mixing sender check with capability-based system
    /// An attacker can transfer the AdminCap to themselves and bypass this
    public entry fun set_fee(new_fee: u64, ctx: &mut TxContext) {
        // This check is useless if AdminCap can be transferred!
        assert!(tx_context::sender(ctx) == @0xADMIN, 0);
        // ... set fee logic
    }

    /// Anyone with the cap can drain the treasury
    public entry fun withdraw(
        _cap: &AdminCap,
        treasury: &mut Treasury,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // Attacker obtains AdminCap via transfer and drains funds
        treasury.balance = treasury.balance - amount;
    }
}
```

### Attack Scenario

1. Admin deploys contract and receives `AdminCap`
2. Attacker social-engineers admin or exploits another vulnerability to get `AdminCap` transferred
3. Attacker now has full admin access, can drain treasury
4. Original `sender()` checks are bypassed because the cap was transferred

## Secure Example

```move
module secure::admin {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    /// SECURE: No `store` ability prevents unauthorized transfers
    /// Only this module can transfer this capability
    public struct AdminCap has key {
        id: UID,
        authorized_address: address,
    }

    public struct Treasury has key {
        id: UID,
        balance: u64,
    }

    fun init(ctx: &mut TxContext) {
        let sender = tx_context::sender(ctx);
        transfer::transfer(
            AdminCap { 
                id: object::new(ctx),
                authorized_address: sender,
            },
            sender
        );
    }

    /// SECURE: Verify the capability is held by the authorized address
    public entry fun withdraw(
        cap: &AdminCap,
        treasury: &mut Treasury,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // Double-check: capability holder must match authorized address
        assert!(tx_context::sender(ctx) == cap.authorized_address, 0);
        
        treasury.balance = treasury.balance - amount;
    }

    /// Explicit transfer function with additional checks
    public entry fun transfer_admin(
        cap: AdminCap,
        new_admin: address,
        ctx: &mut TxContext
    ) {
        // Only current authorized address can transfer
        assert!(tx_context::sender(ctx) == cap.authorized_address, 0);
        
        // Create new cap with updated authorization
        let AdminCap { id, authorized_address: _ } = cap;
        object::delete(id);
        
        transfer::transfer(
            AdminCap {
                id: object::new(ctx),
                authorized_address: new_admin,
            },
            new_admin
        );
    }
}
```

## Recommended Mitigations

### 1. Remove `store` from Capability Objects

```move
/// Without `store`, only your module can transfer this object
public struct AdminCap has key {
    id: UID,
}
```

### 2. Use Consistent Authority Models

Choose **one** authority model and stick to it:

- **Capability-based**: All authorization via capability objects (recommended)
- **Address-based**: All authorization via `sender()` checks

Don't mix them — it creates confusion and security gaps.

### 3. Embed Authorization in Capabilities

```move
public struct AdminCap has key {
    id: UID,
    authorized_address: address,  // Track who should hold this
    permissions: u64,             // Bitmask of allowed operations
}
```

### 4. Use Non-Transferable Patterns

```move
/// Soul-bound capability — cannot be transferred at all
public struct SoulBoundCap has key {
    id: UID,
    owner: address,
}

/// Verify ownership in every function
public fun use_cap(cap: &SoulBoundCap, ctx: &TxContext) {
    assert!(tx_context::sender(ctx) == cap.owner, E_NOT_OWNER);
}
```

## Testing Checklist

- [ ] Verify all capability objects lack `store` ability unless intentionally transferable
- [ ] Confirm no mixing of `sender()` checks with capability-based authorization
- [ ] Test that transferred capabilities cannot bypass access controls
- [ ] Audit all `public_transfer` and `transfer` calls for sensitive objects

## Related Vulnerabilities

- [Ability Misconfiguration](../ability-misconfiguration/)
- [Access-Control Mistakes](../access-control-mistakes/)
- [Capability Leakage](../capability-leakage/)