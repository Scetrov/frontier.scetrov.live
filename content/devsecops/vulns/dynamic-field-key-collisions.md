+++
title = '14. Dynamic Field Key Collisions'
date = '2025-11-26T00:00:00Z'
weight = 14
+++

## Overview

Dynamic fields in Sui use keys to store and retrieve values. When user-controlled or predictable keys are used, attackers can cause collisions that overwrite existing data, inject malicious values, or break protocol invariants.

## Risk Level

**High** — Can lead to data corruption, asset theft, or protocol takeover.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE |
 | -------------- | ----------- |
 | A01 (Broken Access Control), A05 (Security Misconfiguration) | CWE-653 (Improper Isolation), CWE-706 (Use of Incorrectly-Resolved Name) |

## The Problem

### How Dynamic Field Keys Work

```move
// Keys can be any type with `copy + drop + store`
df::add(&mut uid, key, value);

// Same key retrieves the same slot
let val = df::borrow(&uid, key);

// Different key types create different namespaces
df::add(&mut uid, string_key, value1);
df::add(&mut uid, u64_key, value2);  // Different namespace
```

### Collision Scenarios

1. **User-controlled string keys** — Attacker chooses key to collide with system data
2. **Predictable numeric keys** — Sequential IDs can be predicted and front-run
3. **Type confusion** — Same key value in different types might be expected to differ
4. **Namespace pollution** — Attacker fills namespace with garbage data

## Vulnerable Example

```move
module vulnerable::storage {
    use sui::object::UID;
    use sui::dynamic_field as df;
    use sui::tx_context::{Self, TxContext};

    public struct Storage has key {
        id: UID,
    }

    public struct UserData has store {
        balance: u64,
        is_admin: bool,
    }

    /// VULNERABLE: User-controlled key allows collision attacks
    public entry fun store_user_data(
        storage: &mut Storage,
        username: vector<u8>,  // User-controlled key!
        balance: u64,
        ctx: &mut TxContext
    ) {
        // Attacker can choose username = "admin" and overwrite admin data
        df::add(&mut storage.id, username, UserData {
            balance,
            is_admin: false,
        });
    }

    /// VULNERABLE: System uses same key namespace
    public entry fun set_admin(
        storage: &mut Storage,
        admin_name: vector<u8>,
    ) {
        df::add(&mut storage.id, admin_name, UserData {
            balance: 0,
            is_admin: true,
        });
    }

    /// VULNERABLE: No existence check before add
    public entry fun update_balance(
        storage: &mut Storage,
        username: vector<u8>,
        amount: u64,
    ) {
        // Will abort if key doesn't exist
        // But attacker might have already added their own entry
        let data: &mut UserData = df::borrow_mut(&mut storage.id, username);
        data.balance = data.balance + amount;
    }
}

module vulnerable::vault {
    use sui::dynamic_field as df;

    public struct Vault has key {
        id: UID,
        next_slot_id: u64,  // Sequential, predictable
    }

    /// VULNERABLE: Predictable slot IDs can be front-run
    public entry fun create_deposit_slot(
        vault: &mut Vault,
        ctx: &mut TxContext
    ): u64 {
        let slot_id = vault.next_slot_id;
        vault.next_slot_id = slot_id + 1;

        // Attacker predicts next slot_id and front-runs
        df::add(&mut vault.id, slot_id, DepositSlot {
            owner: tx_context::sender(ctx),
            amount: 0,
        });

        slot_id
    }
}
```

### Attack: Key Collision

```move
// Attacker observes admin_name = "superadmin" was used
module attack::collision {
    use vulnerable::storage;

    public entry fun become_admin(
        storage: &mut storage::Storage,
        ctx: &mut TxContext
    ) {
        // Use same key as admin to inject data
        // If store_user_data doesn't check existence, this might work
        storage::store_user_data(
            storage,
            b"superadmin",  // Collide with admin key
            999999,
            ctx
        );
    }
}
```

## Secure Example

```move
module secure::storage {
    use sui::object::{Self, UID, ID};
    use sui::dynamic_field as df;
    use sui::tx_context::{Self, TxContext};
    use std::type_name::{Self, TypeName};

    const E_KEY_EXISTS: u64 = 0;
    const E_KEY_NOT_FOUND: u64 = 1;
    const E_NOT_OWNER: u64 = 2;

    public struct Storage has key {
        id: UID,
    }

    /// SECURE: Type-safe key for user data
    public struct UserDataKey has copy, drop, store {
        user_address: address,
    }

    /// SECURE: Separate type for admin keys
    public struct AdminKey has copy, drop, store {
        admin_address: address,
    }

    public struct UserData has store {
        balance: u64,
    }

    public struct AdminData has store {
        permissions: u64,
    }

    /// SECURE: Key is derived from sender address (unique)
    public entry fun store_user_data(
        storage: &mut Storage,
        balance: u64,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        let key = UserDataKey { user_address: sender };

        // Check if already exists
        assert!(!df::exists_(&storage.id, key), E_KEY_EXISTS);

        df::add(&mut storage.id, key, UserData { balance });
    }

    /// SECURE: Admin uses different key type
    public entry fun set_admin(
        storage: &mut Storage,
        admin_cap: &AdminCap,
        admin_address: address,
        permissions: u64,
    ) {
        let key = AdminKey { admin_address };

        // Remove existing if present
        if (df::exists_(&storage.id, key)) {
            let _: AdminData = df::remove(&mut storage.id, key);
        };

        df::add(&mut storage.id, key, AdminData { permissions });
    }

    /// SECURE: Verify ownership before update
    public entry fun update_balance(
        storage: &mut Storage,
        amount: u64,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        let key = UserDataKey { user_address: sender };

        assert!(df::exists_(&storage.id, key), E_KEY_NOT_FOUND);

        let data: &mut UserData = df::borrow_mut(&mut storage.id, key);
        data.balance = data.balance + amount;
    }
}

module secure::vault {
    use sui::object::{Self, UID, ID};
    use sui::dynamic_field as df;
    use sui::tx_context::{Self, TxContext};
    use sui::hash;

    public struct Vault has key {
        id: UID,
    }

    /// SECURE: Unpredictable slot key using object ID
    public struct SlotKey has copy, drop, store {
        slot_id: ID,
    }

    public struct DepositSlot has store {
        owner: address,
        amount: u64,
    }

    /// SECURE: Slot ID is unpredictable object ID
    public entry fun create_deposit_slot(
        vault: &mut Vault,
        ctx: &mut TxContext
    ): ID {
        // Create a temporary object just for its unique ID
        let temp_uid = object::new(ctx);
        let slot_id = object::uid_to_inner(&temp_uid);

        let key = SlotKey { slot_id };

        df::add(&mut vault.id, key, DepositSlot {
            owner: tx_context::sender(ctx),
            amount: 0,
        });

        object::delete(temp_uid);

        slot_id
    }
}
```

## Key Design Patterns

### Pattern 1: Type-Safe Key Namespaces

```move
/// Each data type has its own key type
public struct UserBalanceKey has copy, drop, store { user: address }
public struct UserProfileKey has copy, drop, store { user: address }
public struct ConfigKey has copy, drop, store { name: vector<u8> }

/// Compiler ensures different key types = different namespaces
df::add(&mut uid, UserBalanceKey { user }, balance);
df::add(&mut uid, UserProfileKey { user }, profile);
// These cannot collide even with same `user` value
```

### Pattern 2: Sender-Derived Keys

```move
/// Only sender can create their own key
public fun user_key(ctx: &TxContext): UserKey {
    UserKey { address: tx_context::sender(ctx) }
}

public entry fun store(container: &mut Container, data: Data, ctx: &mut TxContext) {
    let key = user_key(ctx);  // Key derived from sender
    df::add(&mut container.id, key, data);
}
```

### Pattern 3: Composite Keys

```move
/// Combine multiple factors for unique keys
public struct CompositeKey has copy, drop, store {
    owner: address,
    category: u8,
    index: u64,
}

/// Uniqueness across multiple dimensions
public fun make_key(owner: address, category: u8, index: u64): CompositeKey {
    CompositeKey { owner, category, index }
}
```

### Pattern 4: Existence Checks

```move
/// Always check before add/remove
public fun safe_add<K: copy + drop + store, V: store>(
    uid: &mut UID,
    key: K,
    value: V,
) {
    assert!(!df::exists_(uid, key), E_ALREADY_EXISTS);
    df::add(uid, key, value);
}

public fun safe_get<K: copy + drop + store, V: store>(
    uid: &UID,
    key: K,
): &V {
    assert!(df::exists_(uid, key), E_NOT_FOUND);
    df::borrow(uid, key)
}
```

## Recommended Mitigations

### 1. Never Use User-Controlled Strings as Keys

```move
// BAD
public fun store(uid: &mut UID, user_key: vector<u8>, value: Data) {
    df::add(uid, user_key, value);
}

// GOOD
public fun store(uid: &mut UID, value: Data, ctx: &TxContext) {
    let key = TypeSafeKey { owner: tx_context::sender(ctx) };
    df::add(uid, key, value);
}
```

### 2. Use Object IDs for Unpredictable Keys

```move
let uid = object::new(ctx);
let unique_key = object::uid_to_inner(&uid);
object::delete(uid);
// unique_key is cryptographically random
```

### 3. Separate Key Types for Different Data

```move
// Different structs = different namespaces
public struct UserKey has copy, drop, store { ... }
public struct AdminKey has copy, drop, store { ... }
public struct ConfigKey has copy, drop, store { ... }
```

### 4. Always Check Existence

```move
// Before add
assert!(!df::exists_(uid, key), E_EXISTS);

// Before borrow/remove
assert!(df::exists_(uid, key), E_NOT_FOUND);
```

## Testing Checklist

- [ ] Test that different users cannot access each other's data
- [ ] Verify key collisions are properly rejected
- [ ] Test admin and user key namespaces are isolated
- [ ] Confirm unpredictable keys cannot be front-run
- [ ] Test existence checks prevent overwrites

## Related Vulnerabilities

- [Dynamic Field Misuse](../dynamic-field-misuse/)
- [Access-Control Mistakes](../access-control-mistakes/)
- [Unbounded Child Growth](../unbounded-child-growth/)
