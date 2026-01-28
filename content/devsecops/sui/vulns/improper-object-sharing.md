+++
title = '7. Improper Object Sharing'
date = '2025-11-26T00:00:00Z'
weight = 7
+++

## Overview

Accidentally exposing objects as shared via `transfer::share_object` enables global mutation by anyone. Once an object is shared, it **cannot be unshared** — this is a permanent, irreversible change to the object's ownership model.

## Risk Level

**High** — Shared objects are accessible to all, potentially exposing sensitive operations.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-277 (Insecure Inherited Permissions) | 

## The Problem

### Ownership Models in Sui

 | Type | Created By | Who Can Use | Can Be Changed | 
 | ------ | ----------- | ------------- | ---------------- | 
| **Address-owned** | `transfer::transfer` | Only owner | Yes (transfer) |
| **Shared** | `transfer::share_object` | Anyone | No (permanent) |
| **Immutable** | `transfer::freeze_object` | Anyone (read) | No (permanent) |

### Why Sharing is Dangerous

1. **Global access** — Any transaction can reference the shared object
2. **No revocation** — Cannot convert back to address-owned
3. **Mutation exposure** — All `&mut` entry functions become callable by anyone
4. **Contention** — Performance issues from concurrent access

## Vulnerable Example

```move
module vulnerable::wallet {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    public struct Wallet has key {
        id: UID,
        funds: Coin<SUI>,
        owner: address,
    }

    /// VULNERABLE: Wallet is shared instead of transferred!
    fun init(ctx: &mut TxContext) {
        let wallet = Wallet {
            id: object::new(ctx),
            funds: coin::zero(ctx),
            owner: tx_context::sender(ctx),
        };
        
        // WRONG: This should be transfer(), not share_object()!
        transfer::share_object(wallet);
    }

    /// Because wallet is shared, ANYONE can call this!
    public entry fun withdraw(
        wallet: &mut Wallet,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // This check is useless — attacker just passes their address
        let recipient = tx_context::sender(ctx);
        
        // Wait, the owner check is missing entirely!
        let withdrawn = coin::split(&mut wallet.funds, amount, ctx);
        transfer::public_transfer(withdrawn, recipient);
    }

    /// VULNERABLE: Even with owner check, sharing was wrong
    public entry fun withdraw_checked(
        wallet: &mut Wallet,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // Owner check exists but...
        assert!(tx_context::sender(ctx) == wallet.owner, E_NOT_OWNER);
        
        // If owner's key is compromised, wallet is drained
        // With address-owned, owner could at least try to transfer first
        let withdrawn = coin::split(&mut wallet.funds, amount, ctx);
        transfer::public_transfer(withdrawn, wallet.owner);
    }
}
```

### Attack Scenario

```move
// Attacker finds the shared wallet object
module attack::drain_wallet {
    use vulnerable::wallet;
    use sui::tx_context::TxContext;

    public entry fun steal(
        wallet: &mut wallet::Wallet,
        ctx: &mut TxContext
    ) {
        // Because wallet is shared, attacker can reference it directly
        // If withdraw() lacks owner check, funds are gone
        wallet::withdraw(wallet, 1000000, ctx);
    }
}
```

## Secure Example

```move
module secure::wallet {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    /// Wallet is address-owned — only owner can use it
    public struct Wallet has key {
        id: UID,
        funds: Coin<SUI>,
    }

    /// SECURE: Transfer to user, not share
    fun init(ctx: &mut TxContext) {
        transfer::transfer(
            Wallet {
                id: object::new(ctx),
                funds: coin::zero(ctx),
            },
            tx_context::sender(ctx)
        );
    }

    /// Owner must possess the wallet to call this
    public entry fun withdraw(
        wallet: &mut Wallet,
        amount: u64,
        recipient: address,
        ctx: &mut TxContext
    ) {
        let withdrawn = coin::split(&mut wallet.funds, amount, ctx);
        transfer::public_transfer(withdrawn, recipient);
    }

    /// Only owner can transfer their wallet
    public entry fun transfer_wallet(
        wallet: Wallet,
        new_owner: address,
    ) {
        transfer::transfer(wallet, new_owner);
    }
}
```

## When Sharing IS Appropriate

```move
module appropriate_sharing::examples {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;

    /// APPROPRIATE: Global configuration that needs to be readable by all
    public struct GlobalConfig has key {
        id: UID,
        fee_bps: u64,
        paused: bool,
    }

    /// APPROPRIATE: Order book that multiple parties interact with
    public struct OrderBook has key {
        id: UID,
        bids: vector<Order>,
        asks: vector<Order>,
    }

    /// APPROPRIATE: Liquidity pool for AMM
    public struct LiquidityPool has key {
        id: UID,
        reserve_a: Coin<A>,
        reserve_b: Coin<B>,
    }

    /// For shared objects, use capability-based access control
    public struct AdminCap has key {
        id: UID,
        config_id: ID,
    }

    public entry fun update_config(
        cap: &AdminCap,
        config: &mut GlobalConfig,
        new_fee: u64,
    ) {
        assert!(cap.config_id == object::id(config), E_WRONG_CONFIG);
        config.fee_bps = new_fee;
    }
}
```

## Sharing Decision Checklist

Ask these questions before using `share_object`:

1. **Must multiple unrelated parties access this object?**
   - Yes → Consider sharing
   - No → Use `transfer()` for address-owned

2. **Does the object contain funds or valuable assets?**
   - Yes → Prefer address-owned or use strict capability controls
   - No → Sharing may be acceptable

3. **Can operations be separated into read-only vs write?**
   - Yes → Consider immutable config + mutable state pattern
   - No → Ensure all write paths have access control

4. **Is contention expected?**
   - Yes → Consider sharding or owned-object patterns
   - No → Sharing may be acceptable

## Recommended Mitigations

### 1. Default to Address-Owned

```move
// Unless you have a specific reason, use transfer()
fun init(ctx: &mut TxContext) {
    transfer::transfer(MyObject { ... }, tx_context::sender(ctx));
}
```

### 2. Separate Shared and Owned State

```move
/// Shared: Global registry (read-heavy)
public struct Registry has key {
    id: UID,
    // Immutable or admin-only mutable state
}

/// Owned: User-specific state
public struct UserAccount has key {
    id: UID,
    // User's private state
}
```

### 3. Use Capabilities for Shared Object Mutations

```move
/// Any mutation of shared objects requires a capability
public entry fun modify_shared(
    cap: &ModifyCap,
    shared: &mut SharedObject,
    ...
) {
    assert!(cap.shared_id == object::id(shared), E_WRONG_CAP);
    // Now safe to modify
}
```

### 4. Document Sharing Decisions

```move
/// SHARED: This object is intentionally shared because:
/// 1. Multiple parties need to interact (buyers/sellers)
/// 2. All mutations require OrderCap
/// 3. Contention is managed via order sharding
public struct OrderBook has key { ... }
```

## Testing Checklist

- [ ] Review all `share_object` calls and justify each one
- [ ] Verify shared objects have proper access control on all mutations
- [ ] Test that address-owned objects cannot be accessed by non-owners
- [ ] Confirm no sensitive operations are exposed on shared objects without capability checks
- [ ] Document the ownership model for each object type

## Related Vulnerabilities

- [Shared Object DoS](../shared-object-dos/)
- [Object Transfer Misuse](../object-transfer-misuse/)
- [Overuse of Shared Objects](../overuse-of-shared-objects/)