+++
title = '19. Ownership Model Confusion'
date = '2025-11-26T00:00:00Z'
weight = 19
+++

## Overview

Sui has multiple ownership models: address-owned, shared, immutable, and object-owned (wrapped/child). Incorrect transitions between these models or confusion about which model applies can break invariants and security assumptions.

## Risk Level

**High** — Can lead to complete access control bypass.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-266 (Incorrect Privilege Assignment) | 

## The Problem

### Ownership Models

 | Model | Created By | Access | Mutability | Reversible | 
 | ------- | ----------- | -------- | ------------ | ------------ | 
| Address-owned | `transfer()` | Owner only | Yes | Yes (transfer) |
| Shared | `share_object()` | Anyone | Yes | **No** |
| Immutable | `freeze_object()` | Anyone (read) | **No** | **No** |
| Object-owned | `transfer_to_object()` | Parent object | Yes | Yes |

### Common Confusion

1. **Shared → Address-owned** — Not possible after sharing
2. **Immutable → Mutable** — Not possible after freezing
3. **Object-owned access** — Parent owner doesn't automatically control child
4. **Wrapped objects** — UID changes behavior

## Vulnerable Example

```move
module vulnerable::ownership {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;

    public struct Vault has key, store {
        id: UID,
        balance: u64,
        owner: address,
    }

    public struct VaultController has key {
        id: UID,
    }

    /// VULNERABLE: Attempts to "unshare" an object
    public entry fun make_private(
        vault: Vault,  // Taking by value from shared object
        new_owner: address,
    ) {
        // This doesn't work as expected!
        // Once shared, always shared
        // This just moves the shared object, it's still shared
        transfer::transfer(vault, new_owner);
    }

    /// VULNERABLE: Assumes object ownership = child access
    public entry fun access_child_vault(
        controller: &VaultController,
        // Can't actually access object-owned objects this way
        // The vault would need to be passed separately
    ) {
        // This function signature is fundamentally broken
        // Object ownership doesn't give direct access to children
    }

    /// VULNERABLE: Wrong ownership transition
    public entry fun setup_vault(
        ctx: &mut TxContext
    ) {
        let vault = Vault {
            id: object::new(ctx),
            balance: 1000,
            owner: tx_context::sender(ctx),
        };
        
        // Bug: sharing when should be transferring to owner
        // Now anyone can access the vault!
        transfer::share_object(vault);
    }

    /// VULNERABLE: Freezing breaks protocol
    public entry fun publish_vault(
        vault: Vault,
    ) {
        // Freezing makes it immutable forever
        // Can never update balance again!
        transfer::freeze_object(vault);
    }
}
```

## Secure Example

```move
module secure::ownership {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::dynamic_object_field as dof;

    /// Private vault — only owner can access
    public struct PrivateVault has key {
        id: UID,
        balance: u64,
    }

    /// Shared pool — anyone can interact (with proper checks)
    public struct SharedPool has key {
        id: UID,
        balance: u64,
        admin_cap_id: ID,
    }

    /// Admin capability — controls the shared pool
    public struct PoolAdminCap has key {
        id: UID,
        pool_id: ID,
    }

    /// Published config — immutable by design
    public struct PublishedConfig has key {
        id: UID,
        version: u64,
        // Only immutable data here
        fee_bps: u64,
        name: vector<u8>,
    }

    /// SECURE: Clear ownership from the start
    public entry fun create_private_vault(
        initial_balance: u64,
        ctx: &mut TxContext
    ) {
        let vault = PrivateVault {
            id: object::new(ctx),
            balance: initial_balance,
        };
        
        // Private — only creator can access
        transfer::transfer(vault, tx_context::sender(ctx));
    }

    /// SECURE: Shared with proper access control
    public entry fun create_shared_pool(
        ctx: &mut TxContext
    ) {
        let pool = SharedPool {
            id: object::new(ctx),
            balance: 0,
            admin_cap_id: object::id_from_address(@0x0), // Placeholder
        };
        
        let pool_id = object::id(&pool);
        
        let cap = PoolAdminCap {
            id: object::new(ctx),
            pool_id,
        };
        
        pool.admin_cap_id = object::id(&cap);
        
        // Pool is shared, but admin actions require cap
        transfer::share_object(pool);
        transfer::transfer(cap, tx_context::sender(ctx));
    }

    /// SECURE: Admin action requires capability
    public entry fun admin_withdraw(
        cap: &PoolAdminCap,
        pool: &mut SharedPool,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // Verify cap is for this pool
        assert!(cap.pool_id == object::id(pool), E_WRONG_POOL);
        
        pool.balance = pool.balance - amount;
        // ... transfer
    }

    /// SECURE: Published config is intentionally immutable
    public entry fun publish_config(
        version: u64,
        fee_bps: u64,
        name: vector<u8>,
        ctx: &mut TxContext
    ) {
        let config = PublishedConfig {
            id: object::new(ctx),
            version,
            fee_bps,
            name,
        };
        
        // Intentionally immutable — this is the design
        transfer::freeze_object(config);
    }

    /// SECURE: Use dynamic fields for parent-child relationships
    public struct Parent has key {
        id: UID,
    }

    public struct Child has key, store {
        id: UID,
        value: u64,
    }

    public entry fun add_child_to_parent(
        parent: &mut Parent,
        child: Child,
    ) {
        dof::add(&mut parent.id, b"child", child);
    }

    public fun access_child(parent: &Parent): &Child {
        dof::borrow(&parent.id, b"child")
    }

    public fun access_child_mut(parent: &mut Parent): &mut Child {
        dof::borrow_mut(&mut parent.id, b"child")
    }
}
```

## Ownership Decision Guide

### When to Use Address-Owned

```move
// User-specific assets
public struct UserWallet has key { }

// Individual NFTs
public struct NFT has key { }

// Capabilities (usually)
public struct AdminCap has key { }

transfer::transfer(obj, owner);
```

### When to Use Shared

```move
// Global registries
public struct Registry has key { }

// Liquidity pools
public struct Pool has key { }

// Order books
public struct OrderBook has key { }

transfer::share_object(obj);
```

### When to Use Immutable

```move
// Published configurations
public struct Config has key { }

// Static data
public struct Metadata has key { }

// Verified credentials
public struct Credential has key { }

transfer::freeze_object(obj);
```

### When to Use Object-Owned/Dynamic Fields

```move
// Parent-child relationships
public struct Parent has key {
    id: UID,
    // Children via dynamic fields
}

// Encapsulated components
dof::add(&mut parent.id, key, child);
```

## Recommended Mitigations

### 1. Document Ownership Intent

```move
/// This object is SHARED because:
/// - Multiple users need to interact
/// - Admin actions protected by AdminCap
/// NEVER attempt to unshare
public struct SharedProtocol has key { }
```

### 2. Use Type System to Enforce Ownership

```move
/// No `store` = cannot be wrapped or transferred publicly
public struct MustBeOwned has key {
    id: UID,
}

/// Has `store` = can be wrapped in other objects
public struct CanBeWrapped has key, store {
    id: UID,
}
```

### 3. Validate Ownership Before Operations

```move
public entry fun owner_only_action(
    obj: &mut MyObject,
    ctx: &TxContext
) {
    // For address-owned: ownership enforced by Sui
    // For shared: explicit check required
    assert!(tx_context::sender(ctx) == obj.owner, E_NOT_OWNER);
}
```

### 4. Create Clear Ownership Transitions

```move
/// Explicit transition from private to shared
public entry fun make_shared(
    obj: PrivateObject,
    ctx: &TxContext
) {
    assert!(tx_context::sender(ctx) == obj.owner, E_NOT_OWNER);
    
    // Convert to shared form
    let shared = SharedObject {
        id: obj.id,
        data: obj.data,
        original_owner: obj.owner,
    };
    
    transfer::share_object(shared);
}
```

## Testing Checklist

- [ ] Verify ownership model matches intended access pattern
- [ ] Test that shared objects cannot be "unshared"
- [ ] Confirm immutable objects are truly immutable
- [ ] Test parent-child access patterns with dynamic fields
- [ ] Verify ownership transitions are intentional and documented

## Related Vulnerabilities

- [Object Transfer Misuse](../object-transfer-misuse/)
- [Improper Object Sharing](../improper-object-sharing/)
- [Object Freezing Misuse](../object-freezing-misuse/)