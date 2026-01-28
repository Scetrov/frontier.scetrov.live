+++
title = '8. Dynamic Field Misuse'
date = '2025-11-26T00:00:00Z'
weight = 8
+++

## Overview

Dynamic fields and child objects in Sui allow flexible, runtime-determined storage attached to objects. Incorrect usage leads to unbounded growth, key collisions, invariant violations, and data corruption.

## Risk Level

**High** — Can cause state corruption, gas exhaustion, or security bypasses.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control), A05 (Security Misconfiguration) | CWE-710 (Improper Adherence to Coding Standards), CWE-915 (Improperly Controlled Modification of Dynamically-Determined Object Attributes) |

## The Problem

### Dynamic Fields vs Regular Fields

| Aspect | Regular Fields | Dynamic Fields |
|--------|---------------|----------------|
| Defined at | Compile time | Runtime |
| Type safety | Full | Partial (key type determines value type) |
| Enumeration | Yes | No (must know keys) |
| Growth | Fixed | Unbounded |

### Common Mistakes

1. **Unbounded growth** — No limit on dynamic field additions
2. **Key collisions** — User-controlled keys overwrite existing data
3. **Type confusion** — Same key used for different value types
4. **Orphaned data** — Parent deleted without removing dynamic fields
5. **Access control bypass** — Dynamic fields circumvent intended restrictions

## Vulnerable Example

```move
module vulnerable::inventory {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::dynamic_field as df;

    public struct Inventory has key {
        id: UID,
        owner: address,
    }

    public struct Item has store {
        name: vector<u8>,
        value: u64,
    }

    /// VULNERABLE: User-controlled key allows overwriting
    public entry fun add_item(
        inventory: &mut Inventory,
        item_name: vector<u8>,  // User-controlled key!
        value: u64,
        ctx: &mut TxContext
    ) {
        // Attacker can overwrite existing items!
        df::add(&mut inventory.id, item_name, Item { name: item_name, value });
    }

    /// VULNERABLE: No ownership check for item modification
    public entry fun update_item_value(
        inventory: &mut Inventory,
        item_name: vector<u8>,
        new_value: u64,
    ) {
        // Anyone can modify any item if they know the key
        let item: &mut Item = df::borrow_mut(&mut inventory.id, item_name);
        item.value = new_value;
    }

    /// VULNERABLE: No limit on items — gas exhaustion attack
    public entry fun bulk_add(
        inventory: &mut Inventory,
        count: u64,
        ctx: &mut TxContext
    ) {
        let i = 0;
        while (i < count) {
            let key = i;  // Sequential keys
            df::add(&mut inventory.id, key, Item { 
                name: b"spam", 
                value: 0 
            });
            i = i + 1;
        }
        // Inventory now has unbounded number of items
    }
}

module vulnerable::storage {
    use sui::dynamic_field as df;
    use sui::dynamic_object_field as dof;

    public struct Container has key {
        id: UID,
    }

    /// VULNERABLE: Same key used for different types
    public entry fun store_string(
        container: &mut Container,
        key: vector<u8>,
        value: vector<u8>,
    ) {
        df::add(&mut container.id, key, value);
    }

    public entry fun store_number(
        container: &mut Container,
        key: vector<u8>,
        value: u64,
    ) {
        // If key already exists with string value, this will fail
        // OR worse — type confusion if not properly checked
        df::add(&mut container.id, key, value);
    }
}
```

### Attack Scenarios

**Key Collision Attack:**
```move
// Legitimate user creates an item
add_item(inventory, b"valuable_sword", 1000000, ctx);

// Attacker overwrites it (if add doesn't check existence)
add_item(inventory, b"valuable_sword", 0, ctx);
// Original item's value is now corrupted
```

**State Bloat Attack:**
```move
// Attacker adds millions of items
bulk_add(inventory, 1000000, ctx);
// Future operations on this inventory become expensive
```

## Secure Example

```move
module secure::inventory {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::dynamic_field as df;
    use sui::dynamic_object_field as dof;

    const E_ITEM_EXISTS: u64 = 0;
    const E_ITEM_NOT_FOUND: u64 = 1;
    const E_NOT_OWNER: u64 = 2;
    const E_MAX_ITEMS: u64 = 3;

    const MAX_ITEMS: u64 = 1000;

    public struct Inventory has key {
        id: UID,
        owner: address,
        item_count: u64,  // Track count for limits
    }

    /// SECURE: Item is an object, not just stored data
    public struct Item has key, store {
        id: UID,
        inventory_id: ID,  // Link back to parent
        name: vector<u8>,
        value: u64,
        creator: address,
    }

    /// Key type ensures type safety
    public struct ItemKey has copy, drop, store {
        item_id: ID,
    }

    /// SECURE: Module-controlled keys, existence checks, limits
    public entry fun add_item(
        inventory: &mut Inventory,
        name: vector<u8>,
        value: u64,
        ctx: &mut TxContext
    ) {
        // Ownership check
        assert!(tx_context::sender(ctx) == inventory.owner, E_NOT_OWNER);
        
        // Limit check
        assert!(inventory.item_count < MAX_ITEMS, E_MAX_ITEMS);
        
        let item = Item {
            id: object::new(ctx),
            inventory_id: object::id(inventory),
            name,
            value,
            creator: tx_context::sender(ctx),
        };
        
        let item_id = object::id(&item);
        let key = ItemKey { item_id };
        
        // Use object ID as key — guaranteed unique
        dof::add(&mut inventory.id, key, item);
        inventory.item_count = inventory.item_count + 1;
    }

    /// SECURE: Ownership and existence checks
    public entry fun update_item_value(
        inventory: &mut Inventory,
        item_key: ItemKey,
        new_value: u64,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == inventory.owner, E_NOT_OWNER);
        assert!(dof::exists_(&inventory.id, item_key), E_ITEM_NOT_FOUND);
        
        let item: &mut Item = dof::borrow_mut(&mut inventory.id, item_key);
        item.value = new_value;
    }

    /// SECURE: Proper cleanup with count update
    public entry fun remove_item(
        inventory: &mut Inventory,
        item_key: ItemKey,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == inventory.owner, E_NOT_OWNER);
        assert!(dof::exists_(&inventory.id, item_key), E_ITEM_NOT_FOUND);
        
        let item: Item = dof::remove(&mut inventory.id, item_key);
        
        // Verify item belongs to this inventory
        assert!(item.inventory_id == object::id(inventory), E_ITEM_NOT_FOUND);
        
        inventory.item_count = inventory.item_count - 1;
        
        // Properly delete the item
        let Item { id, inventory_id: _, name: _, value: _, creator: _ } = item;
        object::delete(id);
    }
}
```

## Safe Dynamic Field Patterns

### Pattern 1: Type-Safe Keys

```move
/// Different key types for different value types
public struct StringKey has copy, drop, store { name: vector<u8> }
public struct NumberKey has copy, drop, store { index: u64 }
public struct ObjectKey has copy, drop, store { id: ID }

/// Compiler enforces correct value types
public fun store_string(container: &mut Container, key: StringKey, value: vector<u8>) {
    df::add(&mut container.id, key, value);
}

public fun store_number(container: &mut Container, key: NumberKey, value: u64) {
    df::add(&mut container.id, key, value);
}
```

### Pattern 2: Module-Controlled Keys

```move
/// Key is only constructable within this module
public struct InternalKey has copy, drop, store {
    prefix: vector<u8>,
    index: u64,
}

/// Users cannot create arbitrary keys
fun make_key(index: u64): InternalKey {
    InternalKey { prefix: b"internal_", index }
}
```

### Pattern 3: Registry Pattern

```move
/// Track all keys in a separate structure
public struct Registry has key {
    id: UID,
    keys: vector<ID>,  // All known keys
    max_entries: u64,
}

public fun add_entry(registry: &mut Registry, key: ID, value: Entry) {
    assert!(vector::length(&registry.keys) < registry.max_entries, E_FULL);
    assert!(!vector::contains(&registry.keys, &key), E_EXISTS);
    
    vector::push_back(&mut registry.keys, key);
    df::add(&mut registry.id, key, value);
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
    assert!(!df::exists_(uid, key), E_KEY_EXISTS);
    df::add(uid, key, value);
}

public fun safe_remove<K: copy + drop + store, V: store>(
    uid: &mut UID,
    key: K,
): V {
    assert!(df::exists_(uid, key), E_KEY_NOT_FOUND);
    df::remove(uid, key)
}
```

## Recommended Mitigations

### 1. Limit Dynamic Field Count

```move
public struct Container has key {
    id: UID,
    field_count: u64,
}

const MAX_FIELDS: u64 = 10000;

public fun add_checked(container: &mut Container, ...) {
    assert!(container.field_count < MAX_FIELDS, E_LIMIT_REACHED);
    // ... add field
    container.field_count = container.field_count + 1;
}
```

### 2. Use Object IDs as Keys

```move
// Object IDs are globally unique — no collisions
let key = object::id(&item);
df::add(&mut parent.id, key, item);
```

### 3. Clean Up Before Deletion

```move
public fun delete_container(container: Container) {
    let Container { id, keys } = container;
    
    // Remove all dynamic fields first
    while (!vector::is_empty(&keys)) {
        let key = vector::pop_back(&mut keys);
        let _: Value = df::remove(&mut id, key);
    };
    
    vector::destroy_empty(keys);
    object::delete(id);
}
```

## Testing Checklist

- [ ] Test dynamic field addition with duplicate keys
- [ ] Test removal of non-existent keys
- [ ] Verify count limits are enforced
- [ ] Test parent deletion with existing dynamic fields
- [ ] Verify access control on all dynamic field operations
- [ ] Test with maximum number of allowed dynamic fields

## Related Vulnerabilities

- [Dynamic Field Key Collisions](../dynamic-field-key-collisions/)
- [Unbounded Child Growth](../unbounded-child-growth/)
- [Ownership Model Confusion](../ownership-model-confusion/)
