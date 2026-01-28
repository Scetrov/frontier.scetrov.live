+++
title = '16. Unbounded Child Growth'
date = '2025-11-26T20:16:13Z'
weight = 16
+++

## Overview

Parent objects can accumulate unlimited child objects through dynamic fields or dynamic object fields. This unbounded growth causes gas exhaustion, state bloat, and can make critical operations prohibitively expensive or impossible.

## Risk Level

**High** — Can cause denial of service and gas exhaustion.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A06 (Vulnerable Components), A05 (Security Misconfiguration) | CWE-400 (Uncontrolled Resource Consumption), CWE-770 (Allocation of Resources Without Limits) | 

## The Problem

### Gas Implications

While Sui charges gas per byte, objects with many children:

- Require more time to process
- Can hit transaction gas limits
- Make enumeration impractical
- Increase storage costs indefinitely

### Attack Vectors

1. **Spam attacks** — Attacker adds millions of children
2. **State bloat** — Legitimate use causes uncontrolled growth
3. **Frozen operations** — Operations become too expensive

## Vulnerable Example

```move
module vulnerable::collection {
    use sui::object::{Self, UID};
    use sui::dynamic_field as df;
    use sui::dynamic_object_field as dof;
    use sui::tx_context::TxContext;

    public struct Collection has key {
        id: UID,
        item_count: u64,
        // No limit on items!
    }

    public struct Item has key, store {
        id: UID,
        data: vector<u8>,
    }

    /// VULNERABLE: No limit on child additions
    public entry fun add_item(
        collection: &mut Collection,
        data: vector<u8>,
        ctx: &mut TxContext
    ) {
        let item = Item {
            id: object::new(ctx),
            data,
        };
        
        let item_id = collection.item_count;
        collection.item_count = item_id + 1;
        
        // Unlimited additions possible
        dof::add(&mut collection.id, item_id, item);
    }

    /// VULNERABLE: Iteration over unbounded collection
    public fun sum_all_values(collection: &Collection): u64 {
        let mut sum = 0u64;
        let mut i = 0u64;
        
        // If item_count is huge, this runs out of gas
        while (i < collection.item_count) {
            let item: &Item = dof::borrow(&collection.id, i);
            sum = sum + vector::length(&item.data);
            i = i + 1;
        };
        
        sum
    }

    /// VULNERABLE: Bulk operations on large collections
    public entry fun clear_all(
        collection: &mut Collection,
    ) {
        // Removing millions of items will fail
        while (collection.item_count > 0) {
            collection.item_count = collection.item_count - 1;
            let item: Item = dof::remove(&mut collection.id, collection.item_count);
            let Item { id, data: _ } = item;
            object::delete(id);
        }
    }
}
```

### Attack Scenario

```move
// Attacker floods the collection
public entry fun spam_attack(
    collection: &mut vulnerable::collection::Collection,
    ctx: &mut TxContext
) {
    let i = 0;
    while (i < 10000) {  // Add 10k items per tx
        vulnerable::collection::add_item(
            collection,
            b"spam data that costs gas to store",
            ctx
        );
        i = i + 1;
    };
    // Repeat until collection is unusable
}
```

## Secure Example

```move
module secure::collection {
    use sui::object::{Self, UID, ID};
    use sui::dynamic_object_field as dof;
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::table::{Self, Table};

    const E_COLLECTION_FULL: u64 = 0;
    const E_BATCH_TOO_LARGE: u64 = 1;
    const E_NOT_OWNER: u64 = 2;

    const MAX_ITEMS: u64 = 10000;
    const MAX_BATCH_SIZE: u64 = 100;

    public struct Collection has key {
        id: UID,
        owner: address,
        item_count: u64,
        max_items: u64,
    }

    /// Separate page for pagination
    public struct CollectionPage has key {
        id: UID,
        collection_id: ID,
        page_number: u64,
        items: Table<u64, Item>,
        item_count: u64,
    }

    public struct Item has store {
        data: vector<u8>,
        created_at: u64,
    }

    const ITEMS_PER_PAGE: u64 = 1000;

    /// SECURE: Enforces maximum items
    public entry fun add_item(
        collection: &mut Collection,
        data: vector<u8>,
        ctx: &mut TxContext
    ) {
        // Check global limit
        assert!(collection.item_count < collection.max_items, E_COLLECTION_FULL);
        
        // Optional: Charge fee for storage
        // let fee = calculate_storage_fee(vector::length(&data));
        // collect_fee(fee, ctx);
        
        let item_index = collection.item_count;
        collection.item_count = item_index + 1;
        
        let page_number = item_index / ITEMS_PER_PAGE;
        let index_in_page = item_index % ITEMS_PER_PAGE;
        
        // Get or create page
        if (!dof::exists_(&collection.id, page_number)) {
            let page = CollectionPage {
                id: object::new(ctx),
                collection_id: object::id(collection),
                page_number,
                items: table::new(ctx),
                item_count: 0,
            };
            dof::add(&mut collection.id, page_number, page);
        };
        
        let page: &mut CollectionPage = dof::borrow_mut(&mut collection.id, page_number);
        table::add(&mut page.items, index_in_page, Item {
            data,
            created_at: tx_context::epoch(ctx),
        });
        page.item_count = page.item_count + 1;
    }

    /// SECURE: Paginated retrieval
    public fun get_page(
        collection: &Collection,
        page_number: u64,
    ): &CollectionPage {
        dof::borrow(&collection.id, page_number)
    }

    /// SECURE: Bounded batch removal
    public entry fun remove_batch(
        collection: &mut Collection,
        page_number: u64,
        indices: vector<u64>,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == collection.owner, E_NOT_OWNER);
        assert!(vector::length(&indices) <= MAX_BATCH_SIZE, E_BATCH_TOO_LARGE);
        
        let page: &mut CollectionPage = dof::borrow_mut(&mut collection.id, page_number);
        
        let i = 0;
        while (i < vector::length(&indices)) {
            let idx = *vector::borrow(&indices, i);
            if (table::contains(&page.items, idx)) {
                let _item = table::remove(&mut page.items, idx);
                page.item_count = page.item_count - 1;
                collection.item_count = collection.item_count - 1;
            };
            i = i + 1;
        }
    }

    /// SECURE: Per-item removal (no iteration needed)
    public entry fun remove_item(
        collection: &mut Collection,
        page_number: u64,
        index: u64,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == collection.owner, E_NOT_OWNER);
        
        let page: &mut CollectionPage = dof::borrow_mut(&mut collection.id, page_number);
        assert!(table::contains(&page.items, index), E_ITEM_NOT_FOUND);
        
        let _item = table::remove(&mut page.items, index);
        page.item_count = page.item_count - 1;
        collection.item_count = collection.item_count - 1;
    }
}
```

## Growth Control Patterns

### Pattern 1: Hard Limits

```move
const MAX_CHILDREN: u64 = 1000;

public entry fun add_child(parent: &mut Parent, ...) {
    assert!(parent.child_count < MAX_CHILDREN, E_LIMIT_REACHED);
    parent.child_count = parent.child_count + 1;
    // ... add child
}
```

### Pattern 2: Per-User Limits

```move
public struct UserQuota has key {
    id: UID,
    max_items: u64,
    current_items: u64,
}

public entry fun add_item(
    quota: &mut UserQuota,
    parent: &mut Parent,
    ...
) {
    assert!(quota.current_items < quota.max_items, E_QUOTA_EXCEEDED);
    quota.current_items = quota.current_items + 1;
    // ... add item
}
```

### Pattern 3: Pagination/Sharding

```move
const SHARD_SIZE: u64 = 1000;

public struct ShardedCollection has key {
    id: UID,
    total_items: u64,
    shard_count: u64,
}

public struct Shard has key {
    id: UID,
    shard_index: u64,
    items: Table<u64, Item>,
}

public fun get_shard_for_index(index: u64): u64 {
    index / SHARD_SIZE
}
```

### Pattern 4: Garbage Collection

```move
public struct CollectionWithGC has key {
    id: UID,
    active_count: u64,
    deleted_count: u64,
    items: Table<u64, Option<Item>>,
}

/// Lazy deletion — mark as None
public entry fun delete_item(collection: &mut CollectionWithGC, index: u64) {
    let item_opt = table::borrow_mut(&mut collection.items, index);
    if (option::is_some(item_opt)) {
        let _item = option::extract(item_opt);
        collection.active_count = collection.active_count - 1;
        collection.deleted_count = collection.deleted_count + 1;
    }
}

/// Periodic compaction
public entry fun compact(collection: &mut CollectionWithGC, batch_size: u64) {
    // Remove None entries in batches
    // Reindex remaining items
}
```

### Pattern 5: Storage Fees

```move
const STORAGE_FEE_PER_BYTE: u64 = 100;

public entry fun add_item(
    collection: &mut Collection,
    data: vector<u8>,
    payment: Coin<SUI>,
    ctx: &mut TxContext
) {
    let data_size = vector::length(&data);
    let required_fee = data_size * STORAGE_FEE_PER_BYTE;
    
    assert!(coin::value(&payment) >= required_fee, E_INSUFFICIENT_FEE);
    
    // Store fee, add item
    // Fee makes spam attacks expensive
}
```

## Recommended Mitigations

### 1. Always Set Maximum Limits

```move
public struct Config {
    max_items_per_collection: u64,
    max_items_per_user: u64,
    max_data_size: u64,
}
```

### 2. Use Pagination for Large Collections

```move
// Instead of iterating all items
public fun get_items_page(
    collection: &Collection,
    offset: u64,
    limit: u64,
): vector<&Item> {
    // Return only limit items starting at offset
}
```

### 3. Avoid Unbounded Loops

```move
// BAD
while (i < collection.count) { ... }

// GOOD
let batch_end = min(i + BATCH_SIZE, collection.count);
while (i < batch_end) { ... }
```

### 4. Charge for Storage

```move
// Make spam attacks economically unfeasible
public entry fun add_item(
    payment: Coin<SUI>,  // Must pay for storage
    ...
) {
    let fee = calculate_storage_fee();
    assert!(coin::value(&payment) >= fee, E_INSUFFICIENT_PAYMENT);
}
```

## Testing Checklist

- [ ] Test that maximum limits are enforced
- [ ] Verify operations work at limit boundaries
- [ ] Test pagination with various collection sizes
- [ ] Measure gas costs at different collection sizes
- [ ] Test batch operations don't exceed gas limits
- [ ] Verify cleanup/removal operations scale properly

## Related Vulnerabilities

- [Dynamic Field Misuse](../dynamic-field-misuse/)
- [Shared Object DoS](../shared-object-dos/)
- [Inefficient PTB Composition](../inefficient-ptb-composition/)