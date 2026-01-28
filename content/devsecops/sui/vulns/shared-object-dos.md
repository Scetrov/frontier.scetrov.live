+++
title = '6. Shared Object DoS'
date = '2025-11-26T00:00:00Z'
weight = 6
+++

## Overview

Shared objects in Sui can be mutated by any transaction, leading to contention when many actors try to modify the same object simultaneously. This can cause performance degradation or complete denial of service (DoS) for protocols that rely heavily on shared state.

## Risk Level

**High** — Can make protocols unusable during high-demand periods.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A05 (Security Misconfiguration), A06 (Vulnerable Components) | CWE-400 (Uncontrolled Resource Consumption), CWE-834 (Excessive Iteration) | 

## The Problem

Sui processes transactions that touch the same shared object **sequentially** to maintain consistency. When many transactions contend for the same shared object:

1. **Throughput drops** — Transactions queue up waiting for access
2. **Latency increases** — Users experience long confirmation times
3. **Transactions fail** — Timeouts and gas exhaustion become common

### DoS Attack Vectors

- **Spam transactions** — Attacker floods the network with transactions touching critical shared objects
- **Lock contention** — Deliberate operations that hold shared objects for extended processing
- **State bloat** — Growing shared object data to increase mutation costs

## Vulnerable Example

```move
module vulnerable::exchange {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::table::{Self, Table};

    /// VULNERABLE: Single shared object for entire exchange
    /// All trades must go through this one object
    public struct Exchange has key {
        id: UID,
        /// Every order stored in one table
        orders: Table<u64, Order>,
        order_counter: u64,
        /// Global fee accumulator
        total_fees: u64,
        /// All trading pairs in one vector
        pairs: vector<TradingPair>,
    }

    public struct Order has store {
        maker: address,
        amount: u64,
        price: u64,
    }

    public struct TradingPair has store {
        base: TypeName,
        quote: TypeName,
        volume: u64,
    }

    /// VULNERABLE: Every trade touches the same shared object
    public entry fun place_order(
        exchange: &mut Exchange,
        amount: u64,
        price: u64,
        ctx: &mut TxContext
    ) {
        let order_id = exchange.order_counter;
        exchange.order_counter = order_id + 1;
        
        table::add(&mut exchange.orders, order_id, Order {
            maker: tx_context::sender(ctx),
            amount,
            price,
        });
    }

    /// VULNERABLE: Matching iterates through potentially large order book
    public entry fun match_orders(
        exchange: &mut Exchange,
        buy_order_id: u64,
        sell_order_id: u64,
    ) {
        // Long-running operation on shared object
        // Blocks all other trades
        let buy = table::borrow(&exchange.orders, buy_order_id);
        let sell = table::borrow(&exchange.orders, sell_order_id);
        // ... complex matching logic
    }
}
```

### Attack Scenario

```move
// Attacker spams the exchange with orders
module attack::dos_exchange {
    public entry fun spam(exchange: &mut Exchange, ctx: &mut TxContext) {
        let i = 0;
        while (i < 100) {
            // Each call contends for the same Exchange object
            vulnerable::exchange::place_order(exchange, 1, 1, ctx);
            i = i + 1;
        }
    }
}
```

## Secure Example

```move
module secure::exchange {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::table::{Self, Table};
    use sui::dynamic_field as df;

    /// SECURE: Minimal shared state — just configuration and routing
    public struct ExchangeConfig has key {
        id: UID,
        fee_bps: u64,
        paused: bool,
    }

    /// SECURE: Separate shared object per trading pair
    public struct OrderBook has key {
        id: UID,
        pair_id: ID,
        /// Sharded order storage
        buy_orders: Table<u64, Order>,
        sell_orders: Table<u64, Order>,
        next_order_id: u64,
    }

    /// SECURE: Orders are user-owned objects, not stored in shared state
    public struct UserOrder has key {
        id: UID,
        order_book_id: ID,
        maker: address,
        amount: u64,
        price: u64,
        is_buy: bool,
    }

    /// Create separate order book for each trading pair
    public entry fun create_order_book(
        config: &ExchangeConfig,
        pair_id: ID,
        ctx: &mut TxContext
    ) {
        transfer::share_object(OrderBook {
            id: object::new(ctx),
            pair_id,
            buy_orders: table::new(ctx),
            sell_orders: table::new(ctx),
            next_order_id: 0,
        });
    }

    /// SECURE: User creates their own order object
    /// Reduces contention on order book
    public entry fun create_order(
        book: &mut OrderBook,
        amount: u64,
        price: u64,
        is_buy: bool,
        ctx: &mut TxContext
    ) {
        let order_id = book.next_order_id;
        book.next_order_id = order_id + 1;
        
        // Order is owned by user, not stored in shared object
        transfer::transfer(
            UserOrder {
                id: object::new(ctx),
                order_book_id: object::id(book),
                maker: tx_context::sender(ctx),
                amount,
                price,
                is_buy,
            },
            tx_context::sender(ctx)
        );
    }

    /// SECURE: Matching happens with user-owned orders
    /// Only briefly touches order book for settlement
    public entry fun match_orders(
        book: &mut OrderBook,
        buy_order: UserOrder,
        sell_order: UserOrder,
        ctx: &mut TxContext
    ) {
        // Verify orders belong to this book
        assert!(buy_order.order_book_id == object::id(book), E_WRONG_BOOK);
        assert!(sell_order.order_book_id == object::id(book), E_WRONG_BOOK);
        assert!(buy_order.is_buy && !sell_order.is_buy, E_INVALID_MATCH);
        assert!(buy_order.price >= sell_order.price, E_PRICE_MISMATCH);
        
        // Quick settlement — minimal time holding shared object
        // ... transfer assets
        
        // Clean up orders
        let UserOrder { id: id1, .. } = buy_order;
        let UserOrder { id: id2, .. } = sell_order;
        object::delete(id1);
        object::delete(id2);
    }
}
```

## Sharding Strategies

### Strategy 1: Per-Entity Shared Objects

```move
/// Instead of one global registry
public struct GlobalRegistry has key { ... }

/// Create per-user or per-entity objects
public struct UserAccount has key {
    id: UID,
    owner: address,
    balances: Table<TypeName, u64>,
}
```

### Strategy 2: Time-Based Sharding

```move
/// Shard by time period (hour, day, epoch)
public struct HourlyBucket has key {
    id: UID,
    hour: u64,  // Unix hour
    entries: vector<Entry>,
}

public fun get_current_bucket_id(clock: &Clock): u64 {
    clock::timestamp_ms(clock) / 3600000  // Hours since epoch
}
```

### Strategy 3: Hash-Based Sharding

```move
/// Shard by hash of key
const NUM_SHARDS: u64 = 256;

public struct Shard has key {
    id: UID,
    shard_index: u64,
    data: Table<vector<u8>, Value>,
}

public fun get_shard_index(key: &vector<u8>): u64 {
    let hash = std::hash::sha3_256(*key);
    let first_byte = *vector::borrow(&hash, 0);
    (first_byte as u64) % NUM_SHARDS
}
```

### Strategy 4: Owned Object Patterns

```move
/// Move state to user-owned objects where possible
public struct UserPosition has key {
    id: UID,
    // User's individual state — no contention
    balance: u64,
    orders: vector<Order>,
}

/// Shared object only for global coordination
public struct GlobalState has key {
    id: UID,
    total_supply: u64,  // Updated infrequently
}
```

## Recommended Mitigations

### 1. Minimize Shared Object Scope

```move
// BAD: Everything in one shared object
public struct Protocol has key {
    users: Table<address, User>,
    orders: Table<u64, Order>,
    config: Config,
    stats: Stats,
}

// GOOD: Separate concerns
public struct Config has key { ... }      // Rarely modified
public struct OrderBook has key { ... }   // Per-pair
// Users and orders as owned objects
```

### 2. Use Read-Only Access When Possible

```move
/// Immutable reference reduces contention
public fun get_price(book: &OrderBook): u64 {
    // Read-only access can be parallelized
    book.last_price
}
```

### 3. Batch Operations

```move
/// Allow batching to reduce transaction count
public entry fun batch_place_orders(
    book: &mut OrderBook,
    amounts: vector<u64>,
    prices: vector<u64>,
    ctx: &mut TxContext
) {
    // One transaction for multiple orders
}
```

### 4. Rate Limiting

```move
public struct RateLimiter has key {
    id: UID,
    window_start: u64,
    count: u64,
    max_per_window: u64,
}

public fun check_rate_limit(
    limiter: &mut RateLimiter,
    clock: &Clock
) {
    let now = clock::timestamp_ms(clock);
    if (now - limiter.window_start > 60000) {
        // New window
        limiter.window_start = now;
        limiter.count = 0;
    };
    assert!(limiter.count < limiter.max_per_window, E_RATE_LIMITED);
    limiter.count = limiter.count + 1;
}
```

## Testing Checklist

- [ ] Identify all shared objects and their access patterns
- [ ] Measure throughput under concurrent access
- [ ] Test behavior under spam attack conditions
- [ ] Verify sharding strategy effectiveness
- [ ] Test graceful degradation under high load

## Related Vulnerabilities

- [Improper Object Sharing](../improper-object-sharing/)
- [Unbounded Child Growth](../unbounded-child-growth/)
- [Overuse of Shared Objects](../overuse-of-shared-objects/)