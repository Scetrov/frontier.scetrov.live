+++
title = '25. Unbounded Vector Growth'
date = '2025-11-26T21:06:01Z'
weight = 25
+++

## Overview

Unbounded vector growth occurs when smart contracts allow vectors to grow without limits, leading to gas exhaustion attacks, denial of service, or excessive storage costs. In Sui Move, vectors stored in objects consume gas for both storage and iteration. Attackers can exploit unbounded vectors to make operations prohibitively expensive or cause transactions to fail.

## Risk Level

**High** — Can lead to denial of service or protocol unavailability.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A05 (Security Misconfiguration) | CWE-770 (Allocation of Resources Without Limits or Throttling) | 

## The Problem

### Common Unbounded Vector Issues

 | Issue | Risk | Description | 
 | ------- | ------ | ------------- | 
 | No size limit on push | Critical | Vector grows until gas exhaustion | 
 | Iteration over large vectors | High | O(n) operations become too expensive | 
 | Vector as primary storage | High | Should use Table or dynamic fields | 
 | No cleanup mechanism | Medium | Data accumulates forever | 
 | Copying large vectors | High | Unnecessary gas consumption | 

## Vulnerable Example

```move
module vulnerable::registry {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use std::vector;

    const E_ALREADY_REGISTERED: u64 = 1;

    public struct Registry has key {
        id: UID,
        /// VULNERABLE: No limit on vector size
        members: vector<address>,
        /// VULNERABLE: Grows with every action
        action_log: vector<ActionEntry>,
    }

    public struct ActionEntry has store, copy, drop {
        actor: address,
        action_type: u8,
        timestamp: u64,
    }

    /// VULNERABLE: Vector grows without bound
    public entry fun register(
        registry: &mut Registry,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        // O(n) check - gets slower as registry grows
        let mut i = 0;
        let len = vector::length(&registry.members);
        while (i < len) {
            assert!(*vector::borrow(&registry.members, i) != sender, E_ALREADY_REGISTERED);
            i = i + 1;
        };
        
        // Unbounded growth
        vector::push_back(&mut registry.members, sender);
    }

    /// VULNERABLE: Logs accumulate forever
    public entry fun log_action(
        registry: &mut Registry,
        action_type: u8,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let entry = ActionEntry {
            actor: tx_context::sender(ctx),
            action_type,
            timestamp: clock::timestamp_ms(clock),
        };
        
        // Never cleaned up - grows forever
        vector::push_back(&mut registry.action_log, entry);
    }

    /// VULNERABLE: O(n) iteration becomes impossible
    public fun get_total_members(registry: &Registry): u64 {
        vector::length(&registry.members)
    }

    /// VULNERABLE: Will fail for large registries
    public fun is_member(registry: &Registry, addr: address): bool {
        let mut i = 0;
        let len = vector::length(&registry.members);
        while (i < len) {
            if (*vector::borrow(&registry.members, i) == addr) {
                return true
            };
            i = i + 1;
        };
        false
    }
}

module vulnerable::marketplace {
    use sui::object::{Self, UID};
    use std::vector;

    public struct Marketplace has key {
        id: UID,
        /// VULNERABLE: All listings in one vector
        listings: vector<Listing>,
    }

    public struct Listing has store, drop {
        seller: address,
        price: u64,
        item_id: ID,
        active: bool,
    }

    /// VULNERABLE: Searching listings is O(n)
    public fun find_listing(
        market: &Marketplace,
        item_id: ID
    ): Option<&Listing> {
        let mut i = 0;
        let len = vector::length(&market.listings);
        while (i < len) {
            let listing = vector::borrow(&market.listings, i);
            if (listing.item_id == item_id) {
                return option::some(listing)
            };
            i = i + 1;
        };
        option::none()
    }

    /// VULNERABLE: Removal leaves gaps or requires O(n) shift
    public fun cancel_listing(
        market: &mut Marketplace,
        item_id: ID,
    ) {
        let mut i = 0;
        let len = vector::length(&market.listings);
        while (i < len) {
            let listing = vector::borrow(&market.listings, i);
            if (listing.item_id == item_id) {
                // swap_remove is O(1) but changes indices
                // remove is O(n) due to shifting
                vector::remove(&mut market.listings, i);
                return
            };
            i = i + 1;
        };
    }
}

module vulnerable::voting {
    use std::vector;

    public struct Proposal has key {
        id: UID,
        /// VULNERABLE: All votes stored in vector
        votes: vector<Vote>,
    }

    public struct Vote has store, drop {
        voter: address,
        choice: u8,
        weight: u64,
    }

    /// VULNERABLE: Counting votes is O(n)
    public fun count_votes(proposal: &Proposal): (u64, u64) {
        let mut yes_votes = 0u64;
        let mut no_votes = 0u64;
        
        let mut i = 0;
        let len = vector::length(&proposal.votes);
        while (i < len) {
            let vote = vector::borrow(&proposal.votes, i);
            if (vote.choice == 1) {
                yes_votes = yes_votes + vote.weight;
            } else {
                no_votes = no_votes + vote.weight;
            };
            i = i + 1;
        };
        
        (yes_votes, no_votes)
    }
}
```

### Attack Scenario

```move
module attack::dos_registry {
    use vulnerable::registry::{Self, Registry};
    use sui::tx_context::TxContext;

    /// Attacker registers many addresses to bloat the registry
    public entry fun bloat_registry(
        registry: &mut Registry,
        count: u64,
        ctx: &mut TxContext
    ) {
        // In practice, attacker would use multiple transactions
        // and addresses to avoid duplicate checks
        
        // After thousands of entries:
        // - is_member() becomes too expensive
        // - register() duplicate check times out
        // - Legitimate users can't interact
    }
}
```

## Secure Example

```move
module secure::registry {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::table::{Self, Table};
    use sui::vec_set::{Self, VecSet};

    const E_ALREADY_REGISTERED: u64 = 1;
    const E_MAX_MEMBERS_REACHED: u64 = 2;
    const E_NOT_MEMBER: u64 = 3;

    const MAX_MEMBERS: u64 = 10_000;

    public struct Registry has key {
        id: UID,
        /// SECURE: O(1) lookups with Table
        members: Table<address, MemberInfo>,
        member_count: u64,
    }

    public struct MemberInfo has store {
        joined_at: u64,
        active: bool,
    }

    /// SECURE: Bounded membership with O(1) operations
    public entry fun register(
        registry: &mut Registry,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        // O(1) existence check
        assert!(!table::contains(&registry.members, sender), E_ALREADY_REGISTERED);
        
        // Enforce maximum
        assert!(registry.member_count < MAX_MEMBERS, E_MAX_MEMBERS_REACHED);
        
        let info = MemberInfo {
            joined_at: clock::timestamp_ms(clock),
            active: true,
        };
        
        table::add(&mut registry.members, sender, info);
        registry.member_count = registry.member_count + 1;
    }

    /// SECURE: O(1) membership check
    public fun is_member(registry: &Registry, addr: address): bool {
        if (table::contains(&registry.members, addr)) {
            let info = table::borrow(&registry.members, addr);
            info.active
        } else {
            false
        }
    }

    /// SECURE: O(1) removal
    public entry fun unregister(
        registry: &mut Registry,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        assert!(table::contains(&registry.members, sender), E_NOT_MEMBER);
        
        let _info = table::remove(&mut registry.members, sender);
        registry.member_count = registry.member_count - 1;
    }
}

module secure::action_log {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::table::{Self, Table};
    use sui::clock::{Self, Clock};

    const MAX_LOG_ENTRIES: u64 = 1000;

    public struct ActionLog has key {
        id: UID,
        /// SECURE: Circular buffer pattern
        entries: Table<u64, ActionEntry>,
        next_index: u64,
        total_entries: u64,
    }

    public struct ActionEntry has store, drop {
        actor: address,
        action_type: u8,
        timestamp: u64,
    }

    /// SECURE: Bounded log with circular overwrite
    public entry fun log_action(
        log: &mut ActionLog,
        action_type: u8,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let entry = ActionEntry {
            actor: tx_context::sender(ctx),
            action_type,
            timestamp: clock::timestamp_ms(clock),
        };
        
        // Calculate index in circular buffer
        let index = log.next_index % MAX_LOG_ENTRIES;
        
        // Remove old entry if exists
        if (table::contains(&log.entries, index)) {
            table::remove(&mut log.entries, index);
        };
        
        // Add new entry
        table::add(&mut log.entries, index, entry);
        
        log.next_index = log.next_index + 1;
        if (log.total_entries < MAX_LOG_ENTRIES) {
            log.total_entries = log.total_entries + 1;
        };
    }
}

module secure::marketplace {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::table::{Self, Table};
    use sui::dynamic_object_field as dof;

    const E_LISTING_EXISTS: u64 = 1;
    const E_LISTING_NOT_FOUND: u64 = 2;
    const E_NOT_SELLER: u64 = 3;

    public struct Marketplace has key {
        id: UID,
        /// SECURE: O(1) lookups by item ID
        listings: Table<ID, ListingInfo>,
        listing_count: u64,
    }

    public struct ListingInfo has store {
        seller: address,
        price: u64,
        listed_at: u64,
    }

    /// Items stored as dynamic fields, not in vector
    public entry fun list_item<T: key + store>(
        market: &mut Marketplace,
        item: T,
        price: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let item_id = object::id(&item);
        
        assert!(!table::contains(&market.listings, item_id), E_LISTING_EXISTS);
        
        let info = ListingInfo {
            seller: tx_context::sender(ctx),
            price,
            listed_at: clock::timestamp_ms(clock),
        };
        
        // Store listing info in table (O(1))
        table::add(&mut market.listings, item_id, info);
        
        // Store item as dynamic field
        dof::add(&mut market.id, item_id, item);
        
        market.listing_count = market.listing_count + 1;
    }

    /// SECURE: O(1) lookup
    public fun get_listing(
        market: &Marketplace,
        item_id: ID
    ): &ListingInfo {
        assert!(table::contains(&market.listings, item_id), E_LISTING_NOT_FOUND);
        table::borrow(&market.listings, item_id)
    }

    /// SECURE: O(1) removal
    public entry fun cancel_listing<T: key + store>(
        market: &mut Marketplace,
        item_id: ID,
        ctx: &mut TxContext
    ) {
        assert!(table::contains(&market.listings, item_id), E_LISTING_NOT_FOUND);
        
        let info = table::borrow(&market.listings, item_id);
        assert!(info.seller == tx_context::sender(ctx), E_NOT_SELLER);
        
        // Remove listing info
        let _info = table::remove(&mut market.listings, item_id);
        
        // Return item to seller
        let item: T = dof::remove(&mut market.id, item_id);
        transfer::public_transfer(item, tx_context::sender(ctx));
        
        market.listing_count = market.listing_count - 1;
    }
}

module secure::voting {
    use sui::object::{Self, UID};
    use sui::table::{Self, Table};

    const E_ALREADY_VOTED: u64 = 1;

    public struct Proposal has key {
        id: UID,
        /// SECURE: Track votes per address (O(1) check)
        votes: Table<address, Vote>,
        /// SECURE: Pre-aggregated totals
        yes_votes: u64,
        no_votes: u64,
        total_weight: u64,
    }

    public struct Vote has store, drop {
        choice: u8,
        weight: u64,
    }

    /// SECURE: O(1) vote with pre-aggregation
    public entry fun cast_vote(
        proposal: &mut Proposal,
        choice: u8,
        weight: u64,
        ctx: &mut TxContext
    ) {
        let voter = tx_context::sender(ctx);
        
        // O(1) duplicate check
        assert!(!table::contains(&proposal.votes, voter), E_ALREADY_VOTED);
        
        // Store vote
        let vote = Vote { choice, weight };
        table::add(&mut proposal.votes, voter, vote);
        
        // Update aggregates (no need to iterate later)
        if (choice == 1) {
            proposal.yes_votes = proposal.yes_votes + weight;
        } else {
            proposal.no_votes = proposal.no_votes + weight;
        };
        proposal.total_weight = proposal.total_weight + weight;
    }

    /// SECURE: O(1) result retrieval
    public fun get_results(proposal: &Proposal): (u64, u64, u64) {
        (proposal.yes_votes, proposal.no_votes, proposal.total_weight)
    }
}
```

## Vector Usage Guidelines

### When to Use Vectors

```move
// GOOD: Small, bounded collections
public struct Config has key {
    admins: vector<address>,  // Max 5 admins
    tags: vector<vector<u8>>,  // Max 10 tags
}

const MAX_ADMINS: u64 = 5;

public fun add_admin(config: &mut Config, admin: address) {
    assert!(vector::length(&config.admins) < MAX_ADMINS, E_MAX_ADMINS);
    vector::push_back(&mut config.admins, admin);
}
```

### When to Use Table/VecMap

```move
// GOOD: Large or unbounded collections with key lookups
public struct UserRegistry has key {
    users: Table<address, UserInfo>,  // Unlimited users, O(1) lookup
}

// GOOD: When you need to iterate occasionally but lookup often
public struct TokenRegistry has key {
    tokens: VecMap<ID, TokenInfo>,  // Ordered, iterable, O(n) lookup
}
```

### When to Use Dynamic Fields

```move
// GOOD: Heterogeneous or large object storage
public struct Wallet has key {
    id: UID,
    // Items stored as dynamic fields
    // - No vector bloat
    // - O(1) access by key
    // - Items can be different types
}

public fun store_item<T: key + store>(wallet: &mut Wallet, item: T) {
    let item_id = object::id(&item);
    dof::add(&mut wallet.id, item_id, item);
}
```

## Recommended Mitigations

### 1. Set Maximum Sizes

```move
const MAX_ENTRIES: u64 = 1000;

public fun add_entry(collection: &mut Collection, entry: Entry) {
    assert!(vector::length(&collection.entries) < MAX_ENTRIES, E_MAX_SIZE);
    vector::push_back(&mut collection.entries, entry);
}
```

### 2. Use Tables for Large Collections

```move
// Replace vector with Table for O(1) operations
members: Table<address, MemberInfo>,  // Not vector<address>
```

### 3. Pre-aggregate Data

```move
// Don't iterate to count - maintain running totals
public struct Stats has key {
    total_votes: u64,  // Updated on each vote
    total_value: u64,  // Updated on each deposit
}
```

### 4. Implement Cleanup Mechanisms

```move
// Circular buffer for logs
let index = next_index % MAX_SIZE;
// Old entries automatically overwritten
```

### 5. Use Pagination for Reads

```move
public fun get_entries_paginated(
    collection: &Collection,
    offset: u64,
    limit: u64
): vector<Entry> {
    // Return only a subset
}
```

## Testing Checklist

- [ ] Verify all vectors have maximum size limits
- [ ] Test behavior at maximum capacity
- [ ] Confirm O(n) operations are avoided or bounded
- [ ] Test gas consumption with large data sets
- [ ] Verify cleanup mechanisms work correctly
- [ ] Check that Tables are used for key-based lookups
- [ ] Test pagination for large result sets

## Related Vulnerabilities

- [Unbounded Child Growth](../unbounded-child-growth/)
- [Shared Object DoS](../shared-object-dos/)
- [Inefficient PTB Composition](../inefficient-ptb-composition/)
- [General Move Logic Errors](../general-move-logic-errors/)