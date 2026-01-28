+++
title = '15. Event Design Vulnerabilities'
date = '2025-11-26T00:00:00Z'
weight = 15
+++

## Overview

Events in Sui are the primary mechanism for off-chain systems to observe on-chain state changes. Poor event design leads to missed state changes, ambiguous interpretations, replay vulnerabilities, and off-chain system failures.

## Risk Level

**Medium** — Can cause off-chain desync, incorrect UI state, or indexer failures.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A04 (Insecure Design), A09 (Security Logging and Monitoring Failures) | CWE-223 (Omission of Security-relevant Information), CWE-778 (Insufficient Logging) | 

## The Problem

### Event Design Issues

1. **Missing events** — State changes without corresponding events
2. **Ambiguous events** — Events that don't clearly indicate what happened
3. **Incomplete events** — Missing critical context (who, what, when)
4. **Duplicate events** — Same event for different operations
5. **No event versioning** — Breaking changes affect off-chain systems

## Vulnerable Example

```move
module vulnerable::trading {
    use sui::object::{Self, UID};
    use sui::event;
    use sui::tx_context::TxContext;

    /// VULNERABLE: Ambiguous event — which operation?
    public struct TradeEvent has copy, drop {
        amount: u64,
    }

    /// VULNERABLE: Missing critical context
    public struct TransferEvent has copy, drop {
        amount: u64,
        // Missing: from, to, timestamp, tx_digest, token_type
    }

    public struct Order has key {
        id: UID,
        amount: u64,
        status: u8,
    }

    /// VULNERABLE: State change without event
    public entry fun cancel_order(order: &mut Order) {
        order.status = 2; // Cancelled
        // NO EVENT! Off-chain systems don't know about this
    }

    /// VULNERABLE: Same event for different operations
    public entry fun buy(amount: u64) {
        // ... execute buy
        event::emit(TradeEvent { amount });  // Was this a buy?
    }

    public entry fun sell(amount: u64) {
        // ... execute sell
        event::emit(TradeEvent { amount });  // Or a sell?
    }

    /// VULNERABLE: Event emitted before operation might fail
    public entry fun risky_transfer(
        amount: u64,
        ctx: &mut TxContext
    ) {
        event::emit(TransferEvent { amount });
        
        // This might abort! But event already emitted
        assert!(amount > 0, E_ZERO_AMOUNT);
        // ... transfer logic that might also fail
    }
}
```

### Impact on Off-Chain Systems

```javascript
// Off-chain indexer can't determine:
// 1. Was TradeEvent a buy or sell?
// 2. Who initiated the trade?
// 3. What was the token involved?
// 4. What was the order status before change?

async function processEvent(event) {
    if (event.type === 'TradeEvent') {
        // Ambiguous! Can't update state correctly
    }
}
```

## Secure Example

```move
module secure::trading {
    use sui::object::{Self, UID, ID};
    use sui::event;
    use sui::tx_context::{Self, TxContext};
    use sui::clock::{Self, Clock};
    use std::type_name::{Self, TypeName};

    // Event version for future compatibility
    const EVENT_VERSION: u8 = 1;

    /// SECURE: Specific, complete event for each operation
    public struct OrderCreatedEvent has copy, drop {
        version: u8,
        order_id: ID,
        creator: address,
        token_type: TypeName,
        amount: u64,
        price: u64,
        side: u8,  // 0 = buy, 1 = sell
        timestamp_ms: u64,
    }

    public struct OrderFilledEvent has copy, drop {
        version: u8,
        order_id: ID,
        filler: address,
        fill_amount: u64,
        fill_price: u64,
        remaining_amount: u64,
        timestamp_ms: u64,
    }

    public struct OrderCancelledEvent has copy, drop {
        version: u8,
        order_id: ID,
        canceller: address,
        unfilled_amount: u64,
        reason: u8,  // 0 = user, 1 = expired, 2 = admin
        timestamp_ms: u64,
    }

    public struct TransferEvent has copy, drop {
        version: u8,
        token_type: TypeName,
        from: address,
        to: address,
        amount: u64,
        memo: vector<u8>,
        timestamp_ms: u64,
    }

    public struct Order has key {
        id: UID,
        creator: address,
        amount: u64,
        filled: u64,
        price: u64,
        side: u8,
        status: u8,
    }

    /// SECURE: Event emitted only after successful state change
    public entry fun create_order<T>(
        amount: u64,
        price: u64,
        side: u8,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // Validate first
        assert!(amount > 0, E_ZERO_AMOUNT);
        assert!(price > 0, E_ZERO_PRICE);
        assert!(side <= 1, E_INVALID_SIDE);
        
        // Create order
        let order = Order {
            id: object::new(ctx),
            creator: tx_context::sender(ctx),
            amount,
            filled: 0,
            price,
            side,
            status: 0, // Active
        };
        
        let order_id = object::id(&order);
        
        // Transfer order to creator
        transfer::transfer(order, tx_context::sender(ctx));
        
        // Emit event AFTER successful creation
        event::emit(OrderCreatedEvent {
            version: EVENT_VERSION,
            order_id,
            creator: tx_context::sender(ctx),
            token_type: type_name::get<T>(),
            amount,
            price,
            side,
            timestamp_ms: clock::timestamp_ms(clock),
        });
    }

    /// SECURE: Event includes before/after state
    public entry fun cancel_order(
        order: Order,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        assert!(tx_context::sender(ctx) == order.creator, E_NOT_CREATOR);
        
        let unfilled = order.amount - order.filled;
        let order_id = object::id(&order);
        
        // Clean up order
        let Order { id, creator: _, amount: _, filled: _, price: _, side: _, status: _ } = order;
        object::delete(id);
        
        // Emit cancellation event
        event::emit(OrderCancelledEvent {
            version: EVENT_VERSION,
            order_id,
            canceller: tx_context::sender(ctx),
            unfilled_amount: unfilled,
            reason: 0, // User-initiated
            timestamp_ms: clock::timestamp_ms(clock),
        });
    }

    /// SECURE: Fill event includes all relevant details
    public entry fun fill_order(
        order: &mut Order,
        fill_amount: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        assert!(order.status == 0, E_ORDER_NOT_ACTIVE);
        assert!(fill_amount <= order.amount - order.filled, E_OVERFILL);
        
        order.filled = order.filled + fill_amount;
        
        if (order.filled == order.amount) {
            order.status = 1; // Filled
        };
        
        event::emit(OrderFilledEvent {
            version: EVENT_VERSION,
            order_id: object::id(order),
            filler: tx_context::sender(ctx),
            fill_amount,
            fill_price: order.price,
            remaining_amount: order.amount - order.filled,
            timestamp_ms: clock::timestamp_ms(clock),
        });
    }
}
```

## Event Design Guidelines

### 1. Event Naming Convention

```move
/// Use past tense — events describe completed actions
public struct OrderCreated has copy, drop { }   // Good
public struct CreateOrder has copy, drop { }    // Bad

/// Specific names for specific operations
public struct TokensMinted has copy, drop { }
public struct TokensBurned has copy, drop { }
public struct TokensTransferred has copy, drop { }
```

### 2. Essential Event Fields

```move
public struct CompleteEvent has copy, drop {
    // Version for forward compatibility
    version: u8,
    
    // WHO
    actor: address,
    
    // WHAT
    object_id: ID,
    operation_type: u8,
    
    // WHEN
    timestamp_ms: u64,
    
    // CONTEXT
    old_value: u64,
    new_value: u64,
    
    // OPTIONAL: Additional context
    metadata: vector<u8>,
}
```

### 3. Event Ordering

```move
public entry fun complex_operation(...) {
    // 1. Validate inputs
    assert!(valid_input, E_INVALID);
    
    // 2. Perform state changes
    state.value = new_value;
    
    // 3. Emit events AFTER success
    event::emit(StateChangedEvent { ... });
}
```

### 4. Event Versioning

```move
const EVENT_VERSION_V1: u8 = 1;
const EVENT_VERSION_V2: u8 = 2;

/// V1: Original event
public struct TransferEventV1 has copy, drop {
    version: u8,
    from: address,
    to: address,
    amount: u64,
}

/// V2: Added fields (backward compatible)
public struct TransferEventV2 has copy, drop {
    version: u8,
    from: address,
    to: address,
    amount: u64,
    // New fields
    token_type: TypeName,
    memo: vector<u8>,
}
```

## Recommended Mitigations

### 1. Every State Change Gets an Event

```move
public entry fun update_config(config: &mut Config, new_value: u64) {
    let old_value = config.value;
    config.value = new_value;
    
    event::emit(ConfigUpdatedEvent {
        old_value,
        new_value,
        updater: tx_context::sender(ctx),
    });
}
```

### 2. Use Specific Events for Each Operation

```move
// Instead of generic "TradeEvent"
public struct BuyOrderExecuted has copy, drop { ... }
public struct SellOrderExecuted has copy, drop { ... }
public struct OrderMatched has copy, drop { ... }
```

### 3. Include Sufficient Context

```move
// Bad: Missing context
event::emit(Transfer { amount: 100 });

// Good: Complete context
event::emit(TransferEvent {
    version: 1,
    from: sender,
    to: recipient,
    amount: 100,
    token_type: type_name::get<T>(),
    timestamp_ms: clock::timestamp_ms(clock),
});
```

### 4. Emit After Successful Completion

```move
// Bad: Emit before potential failure
event::emit(ActionEvent { ... });
assert!(condition, E_FAILED);  // If this fails, event was false

// Good: Emit after success
assert!(condition, E_FAILED);
// ... all operations succeed
event::emit(ActionEvent { ... });
```

## Testing Checklist

- [ ] Every state-changing function emits an event
- [ ] Events include who, what, when, and relevant context
- [ ] No events are emitted before potential abort points
- [ ] Different operations emit distinguishable events
- [ ] Events are versioned for future compatibility
- [ ] Off-chain systems can reconstruct state from events

## Related Vulnerabilities

- [Event State Inconsistency](../event-state-inconsistency/)
- [General Move Logic Errors](../general-move-logic-errors/)
- [Clock Time Misuse](../clock-time-misuse/)