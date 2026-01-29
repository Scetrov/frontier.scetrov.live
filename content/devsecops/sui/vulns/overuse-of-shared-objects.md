+++
title = '33. Overuse of Shared Objects'
date = 2025-05-15T00:00:00+00:00
draft = false
weight = 33
+++

## Overview

**Overuse of Shared Objects** occurs when developers unnecessarily use shared objects where owned objects would suffice, or when they design systems with excessive sharing that creates contention, reduces throughput, and introduces security risks. In Sui, shared objects require consensus ordering while owned objects can be processed in parallel without consensus. Overusing shared objects not only degrades performance but can also introduce access control vulnerabilities and state manipulation risks.

## Risk Level

**Severity**: Medium to High

**OWASP Classification**: A01:2021 – Broken Access Control

**CWE Reference**: CWE-284: Improper Access Control

## Vulnerable Example

```move
module game::player_registry {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::table::{Self, Table};

    /// VULNERABLE: All player data stored in a single shared object
    /// This creates massive contention and unnecessary sharing
    public struct PlayerRegistry has key {
        id: UID,
        // Every player action requires accessing this shared object
        players: Table<address, PlayerData>,
        total_players: u64,
        total_experience: u64,
    }

    public struct PlayerData has store {
        name: vector<u8>,
        level: u64,
        experience: u64,
        inventory: vector<u64>,
        gold: u64,
        last_action: u64,
    }

    /// VULNERABLE: Every player action touches the shared registry
    public fun gain_experience(
        registry: &mut PlayerRegistry,
        amount: u64,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        let player = table::borrow_mut(&mut registry.players, sender);

        // Individual player action requires shared object lock
        player.experience = player.experience + amount;
        registry.total_experience = registry.total_experience + amount;

        // Level up check
        if (player.experience >= player.level * 100) {
            player.level = player.level + 1;
        }
    }

    /// VULNERABLE: Simple inventory update requires shared access
    public fun add_to_inventory(
        registry: &mut PlayerRegistry,
        item_id: u64,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        let player = table::borrow_mut(&mut registry.players, sender);
        vector::push_back(&mut player.inventory, item_id);
    }

    /// VULNERABLE: Gold transfer between players uses shared state
    public fun transfer_gold(
        registry: &mut PlayerRegistry,
        recipient: address,
        amount: u64,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);

        // Both sender and recipient data in shared object
        let sender_data = table::borrow_mut(&mut registry.players, sender);
        assert!(sender_data.gold >= amount, 0);
        sender_data.gold = sender_data.gold - amount;

        let recipient_data = table::borrow_mut(&mut registry.players, recipient);
        recipient_data.gold = recipient_data.gold + amount;
    }
}
```

```move
module defi::token_vault {
    use sui::object::{Self, UID};
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::table::{Self, Table};

    /// VULNERABLE: Single shared vault for all user deposits
    /// Creates contention and potential front-running opportunities
    public struct GlobalVault<phantom T> has key {
        id: UID,
        // All deposits in one place
        total_balance: Balance<T>,
        // User balances tracked in shared state
        user_balances: Table<address, u64>,
        // Global parameters everyone competes to read
        interest_rate: u64,
        last_update: u64,
    }

    /// VULNERABLE: Deposit requires shared object access
    public fun deposit<T>(
        vault: &mut GlobalVault<T>,
        coin: Coin<T>,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        let amount = coin::value(&coin);

        // All deposits serialize through this shared object
        balance::join(&mut vault.total_balance, coin::into_balance(coin));

        if (table::contains(&vault.user_balances, sender)) {
            let current = table::borrow_mut(&mut vault.user_balances, sender);
            *current = *current + amount;
        } else {
            table::add(&mut vault.user_balances, sender, amount);
        }
    }

    /// VULNERABLE: Withdrawal also requires shared access
    /// Creates ordering dependencies and potential MEV
    public fun withdraw<T>(
        vault: &mut GlobalVault<T>,
        amount: u64,
        ctx: &mut TxContext
    ): Coin<T> {
        let sender = tx_context::sender(ctx);

        let user_balance = table::borrow_mut(&mut vault.user_balances, sender);
        assert!(*user_balance >= amount, 0);
        *user_balance = *user_balance - amount;

        coin::from_balance(
            balance::split(&mut vault.total_balance, amount),
            ctx
        )
    }
}
```

```move
module marketplace::listings {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::table::{Self, Table};
    use sui::dynamic_field;

    /// VULNERABLE: All marketplace listings in one shared object
    /// Every listing/purchase creates contention
    public struct Marketplace has key {
        id: UID,
        listings: Table<u64, Listing>,
        next_listing_id: u64,
        total_volume: u64,
        fee_percentage: u64,
    }

    public struct Listing has store {
        seller: address,
        price: u64,
        item_type: vector<u8>,
        created_at: u64,
    }

    /// VULNERABLE: Creating a listing touches shared state
    public fun create_listing(
        marketplace: &mut Marketplace,
        price: u64,
        item_type: vector<u8>,
        ctx: &mut TxContext
    ): u64 {
        let listing_id = marketplace.next_listing_id;
        marketplace.next_listing_id = listing_id + 1;

        let listing = Listing {
            seller: tx_context::sender(ctx),
            price,
            item_type,
            created_at: 0, // Simplified
        };

        table::add(&mut marketplace.listings, listing_id, listing);
        listing_id
    }

    /// VULNERABLE: Every purchase serializes through shared object
    public fun purchase(
        marketplace: &mut Marketplace,
        listing_id: u64,
        ctx: &mut TxContext
    ) {
        let listing = table::remove(&mut marketplace.listings, listing_id);
        marketplace.total_volume = marketplace.total_volume + listing.price;

        // Process purchase...
        let Listing { seller: _, price: _, item_type: _, created_at: _ } = listing;
    }
}
```

## Secure Example

```move
module game::player_system {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::event;

    /// SECURE: Each player has their own owned object
    /// No contention - parallel processing possible
    public struct Player has key, store {
        id: UID,
        owner: address,
        name: vector<u8>,
        level: u64,
        experience: u64,
        inventory: vector<u64>,
        gold: u64,
        last_action: u64,
    }

    /// SECURE: Minimal shared state for global aggregates only
    /// Updated rarely, not on every action
    public struct GameStats has key {
        id: UID,
        total_players: u64,
        // Updated periodically, not per-action
    }

    /// Event for off-chain aggregation instead of on-chain state
    public struct ExperienceGained has copy, drop {
        player: address,
        amount: u64,
        new_total: u64,
    }

    /// SECURE: Create owned player object
    public fun create_player(
        name: vector<u8>,
        ctx: &mut TxContext
    ) {
        let player = Player {
            id: object::new(ctx),
            owner: tx_context::sender(ctx),
            name,
            level: 1,
            experience: 0,
            inventory: vector::empty(),
            gold: 0,
            last_action: 0,
        };

        transfer::transfer(player, tx_context::sender(ctx));
    }

    /// SECURE: Player actions use owned object - no contention
    public fun gain_experience(
        player: &mut Player,
        amount: u64,
        ctx: &TxContext
    ) {
        // Only the player's owned object is modified
        player.experience = player.experience + amount;

        if (player.experience >= player.level * 100) {
            player.level = player.level + 1;
        }

        // Emit event for off-chain tracking
        event::emit(ExperienceGained {
            player: tx_context::sender(ctx),
            amount,
            new_total: player.experience,
        });
    }

    /// SECURE: Inventory updates are isolated to owned object
    public fun add_to_inventory(
        player: &mut Player,
        item_id: u64,
    ) {
        vector::push_back(&mut player.inventory, item_id);
    }

    /// SECURE: Gold transfer using owned objects
    /// Both players pass their owned objects
    public fun transfer_gold(
        from_player: &mut Player,
        to_player: &mut Player,
        amount: u64,
    ) {
        assert!(from_player.gold >= amount, 0);
        from_player.gold = from_player.gold - amount;
        to_player.gold = to_player.gold + amount;
    }
}
```

```move
module defi::user_vault {
    use sui::object::{Self, UID};
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::event;

    /// SECURE: Each user has their own vault - owned object
    public struct UserVault<phantom T> has key, store {
        id: UID,
        owner: address,
        balance: Balance<T>,
        // User-specific settings
        auto_compound: bool,
    }

    /// SECURE: Shared config only for protocol-wide parameters
    /// Immutable or rarely updated
    public struct ProtocolConfig has key {
        id: UID,
        interest_rate: u64,
        fee_percentage: u64,
        admin: address,
    }

    /// Events for off-chain aggregation
    public struct DepositEvent has copy, drop {
        user: address,
        amount: u64,
    }

    public struct WithdrawEvent has copy, drop {
        user: address,
        amount: u64,
    }

    /// SECURE: Create user's own vault
    public fun create_vault<T>(ctx: &mut TxContext) {
        let vault = UserVault<T> {
            id: object::new(ctx),
            owner: tx_context::sender(ctx),
            balance: balance::zero(),
            auto_compound: false,
        };

        transfer::transfer(vault, tx_context::sender(ctx));
    }

    /// SECURE: Deposit to owned vault - no contention
    public fun deposit<T>(
        vault: &mut UserVault<T>,
        coin: Coin<T>,
        ctx: &TxContext
    ) {
        let amount = coin::value(&coin);
        balance::join(&mut vault.balance, coin::into_balance(coin));

        event::emit(DepositEvent {
            user: tx_context::sender(ctx),
            amount,
        });
    }

    /// SECURE: Withdraw from owned vault
    public fun withdraw<T>(
        vault: &mut UserVault<T>,
        amount: u64,
        ctx: &mut TxContext
    ): Coin<T> {
        assert!(balance::value(&vault.balance) >= amount, 0);

        event::emit(WithdrawEvent {
            user: tx_context::sender(ctx),
            amount,
        });

        coin::from_balance(
            balance::split(&mut vault.balance, amount),
            ctx
        )
    }

    /// SECURE: Read protocol config (shared but immutable reference)
    public fun get_interest_rate(config: &ProtocolConfig): u64 {
        config.interest_rate
    }
}
```

```move
module marketplace::distributed_listings {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::event;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    /// SECURE: Each listing is its own object
    /// Listings are independent - no contention
    public struct Listing<T: key + store> has key {
        id: UID,
        seller: address,
        price: u64,
        item: T,
    }

    /// SECURE: Minimal shared state for fee collection
    /// Could also be owned by admin
    public struct FeeCollector has key {
        id: UID,
        admin: address,
        fee_basis_points: u64, // e.g., 250 = 2.5%
    }

    /// Events for off-chain indexing
    public struct ListingCreated has copy, drop {
        listing_id: address,
        seller: address,
        price: u64,
    }

    public struct ListingSold has copy, drop {
        listing_id: address,
        seller: address,
        buyer: address,
        price: u64,
    }

    /// SECURE: Create listing as independent object
    public fun create_listing<T: key + store>(
        item: T,
        price: u64,
        ctx: &mut TxContext
    ) {
        let listing = Listing {
            id: object::new(ctx),
            seller: tx_context::sender(ctx),
            price,
            item,
        };

        let listing_id = object::uid_to_address(&listing.id);

        event::emit(ListingCreated {
            listing_id,
            seller: tx_context::sender(ctx),
            price,
        });

        // Share the listing so anyone can purchase
        transfer::share_object(listing);
    }

    /// SECURE: Purchase touches only the specific listing
    /// No global state contention
    public fun purchase<T: key + store>(
        listing: Listing<T>,
        payment: Coin<SUI>,
        fee_collector: &FeeCollector,
        ctx: &mut TxContext
    ): T {
        let Listing { id, seller, price, item } = listing;

        assert!(coin::value(&payment) >= price, 0);

        let listing_id = object::uid_to_address(&id);
        object::delete(id);

        // Calculate fee
        let fee_amount = (price * fee_collector.fee_basis_points) / 10000;
        let seller_amount = price - fee_amount;

        // Split payment
        let seller_coin = coin::split(&mut payment, seller_amount, ctx);
        transfer::public_transfer(seller_coin, seller);

        // Remaining goes to fee collector admin
        transfer::public_transfer(payment, fee_collector.admin);

        event::emit(ListingSold {
            listing_id,
            seller,
            buyer: tx_context::sender(ctx),
            price,
        });

        item
    }

    /// SECURE: Cancel only touches own listing
    public fun cancel_listing<T: key + store>(
        listing: Listing<T>,
        ctx: &TxContext
    ): T {
        let Listing { id, seller, price: _, item } = listing;

        assert!(seller == tx_context::sender(ctx), 0);
        object::delete(id);

        item
    }
}
```

```move
module patterns::hybrid_approach {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::table::{Self, Table};
    use sui::vec_set::{Self, VecSet};

    /// SECURE: Hybrid pattern - shared registry with owned data
    /// Registry only tracks existence, not data
    public struct PlayerRegistry has key {
        id: UID,
        // Only track which players exist (for enumeration)
        // Actual data is in owned objects
        registered_players: VecSet<address>,
    }

    /// Owned player data
    public struct PlayerData has key, store {
        id: UID,
        owner: address,
        stats: Stats,
    }

    public struct Stats has store {
        level: u64,
        experience: u64,
    }

    /// Register touches shared state once
    public fun register_player(
        registry: &mut PlayerRegistry,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);

        // One-time shared state update
        vec_set::insert(&mut registry.registered_players, sender);

        // Create owned data object
        let player_data = PlayerData {
            id: object::new(ctx),
            owner: sender,
            stats: Stats {
                level: 1,
                experience: 0,
            },
        };

        transfer::transfer(player_data, sender);
    }

    /// Regular gameplay uses owned objects only
    public fun play_game(
        player_data: &mut PlayerData,
        experience_gained: u64,
    ) {
        // No shared state touched
        player_data.stats.experience =
            player_data.stats.experience + experience_gained;

        if (player_data.stats.experience >= player_data.stats.level * 100) {
            player_data.stats.level = player_data.stats.level + 1;
        }
    }

    /// Check registration uses immutable reference
    public fun is_registered(
        registry: &PlayerRegistry,
        player: address
    ): bool {
        vec_set::contains(&registry.registered_players, &player)
    }
}
```

## Vulnerable Patterns

### Pattern 1: God Object Anti-Pattern

```move
/// VULNERABLE: Single shared object containing everything
public struct GameWorld has key {
    id: UID,
    players: Table<address, PlayerData>,
    items: Table<u64, Item>,
    quests: Table<u64, Quest>,
    guilds: Table<u64, Guild>,
    marketplace: Table<u64, Listing>,
    leaderboard: vector<address>,
    // Every game action touches this object
}
```

### Pattern 2: Unnecessary Global Counters

```move
/// VULNERABLE: Shared counter for IDs
public struct IdGenerator has key {
    id: UID,
    next_id: u64, // Every creation requires this shared object
}

/// Better: Use object::new(ctx) for unique IDs
```

### Pattern 3: Shared State for Per-User Data

```move
/// VULNERABLE: User balances in shared object
public struct Balances has key {
    id: UID,
    user_balances: Table<address, u64>, // Should be owned
}

/// SECURE: Each user has owned balance
public struct UserBalance has key {
    id: UID,
    balance: u64,
}
```

### Pattern 4: Premature Sharing for Future Features

```move
/// VULNERABLE: Sharing "just in case" someone else needs access
public fun create_user_profile(ctx: &mut TxContext) {
    let profile = UserProfile { /* ... */ };
    // Shared unnecessarily - only owner will modify
    transfer::share_object(profile);
}

/// SECURE: Use owned, convert to shared only when needed
public fun create_user_profile(ctx: &mut TxContext) {
    let profile = UserProfile { /* ... */ };
    transfer::transfer(profile, tx_context::sender(ctx));
}
```

### Pattern 5: Aggregating Stats On-Chain

```move
/// VULNERABLE: Updating global stats on every action
public fun record_action(
    global_stats: &mut GlobalStats,
    action_type: u8,
) {
    // Every user action updates shared state
    global_stats.total_actions = global_stats.total_actions + 1;
    if (action_type == 1) {
        global_stats.type_1_count = global_stats.type_1_count + 1;
    }
}

/// SECURE: Use events, aggregate off-chain
public fun record_action(action_type: u8, ctx: &TxContext) {
    event::emit(ActionRecorded {
        user: tx_context::sender(ctx),
        action_type,
    });
}
```

## Mitigation Strategies

1. **Default to Owned Objects**: Start with owned objects and only share when there's a clear requirement for multiple parties to write to the same object.

2. **Use Events for Aggregation**: Instead of on-chain counters and statistics, emit events and aggregate data off-chain using indexers.

3. **Separate Read and Write Paths**: Use immutable references (`&`) to shared objects for reads when possible, avoiding write contention.

4. **Shard Shared State**: If sharing is necessary, partition data across multiple shared objects to reduce contention.

5. **Hybrid Patterns**: Use shared objects for registry/discovery and owned objects for actual data.

6. **Lazy Initialization**: Don't create shared state upfront; create it on-demand when actually needed.

7. **Consider Object Wrapping**: Wrap items in owned objects that can be passed between parties rather than sharing.

8. **Use Capabilities Instead of Registries**: Instead of checking a shared registry, pass capability objects that prove authorization.

## When Sharing IS Appropriate

```move
/// APPROPRIATE: AMM liquidity pool - multiple parties deposit/withdraw
public struct Pool<phantom A, phantom B> has key {
    id: UID,
    reserve_a: Balance<A>,
    reserve_b: Balance<B>,
    lp_supply: Supply<LP<A, B>>,
}

/// APPROPRIATE: Auction - multiple bidders compete
public struct Auction has key {
    id: UID,
    item: Option<Item>,
    highest_bid: u64,
    highest_bidder: Option<address>,
    end_time: u64,
}

/// APPROPRIATE: Governance - multiple voters participate
public struct Proposal has key {
    id: UID,
    description: vector<u8>,
    votes_for: u64,
    votes_against: u64,
    voters: VecSet<address>,
}
```

## Testing Checklist

- [ ] Review each shared object and document why sharing is necessary
- [ ] Identify objects that could be converted to owned objects
- [ ] Measure transaction throughput with current sharing patterns
- [ ] Test for contention under concurrent transaction load
- [ ] Verify events are emitted for off-chain aggregation needs
- [ ] Check for "god objects" containing unrelated data
- [ ] Validate that shared state updates are minimized per transaction
- [ ] Review capability patterns as alternatives to shared registries
- [ ] Test object creation paths for unnecessary ID generators
- [ ] Analyze transaction dependencies caused by shared objects

## Related Vulnerabilities

- [Upgrade Boundary Errors](../upgrade-boundary-errors/) - Shared objects complicate upgrades
- [Inefficient PTB Composition](../inefficient-ptb-composition/) - Shared objects limit PTB parallelism
- [Clock Time Misuse](../clock-time-misuse/) - Clock is a shared object requiring careful use
- [Event State Inconsistency](../event-state-inconsistency/) - Events as alternative to shared state
