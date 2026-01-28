+++
title = '27. Event State Inconsistency'
date = '2025-11-26T00:00:00Z'
weight = 27
+++

## Overview

Event state inconsistency occurs when emitted events don't accurately reflect the actual on-chain state changes. In Sui Move, events are the primary mechanism for off-chain systems (indexers, frontends, analytics) to track what happened on-chain. When events are missing, duplicated, emitted before state changes, or contain incorrect data, off-chain systems build an incorrect view of the protocol state.

## Risk Level

**Medium to High** — Can lead to incorrect off-chain state, failed integrations, or user confusion.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A09 (Security Logging and Monitoring Failures) | CWE-778 (Insufficient Logging), CWE-223 (Omission of Security-relevant Information) |

## The Problem

### Common Event State Issues

| Issue | Risk | Description |
|-------|------|-------------|
| Event before state change | High | Event emitted but state change aborts |
| Missing events | High | State changes without corresponding events |
| Incorrect event data | High | Event values don't match actual changes |
| Duplicate events | Medium | Same event emitted multiple times |
| Event ordering issues | Medium | Events don't reflect execution order |

## Vulnerable Example

```move
module vulnerable::exchange {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::event;
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};

    const E_INSUFFICIENT_BALANCE: u64 = 1;
    const E_INVALID_AMOUNT: u64 = 2;

    public struct Pool<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        total_swaps: u64,
    }

    public struct SwapEvent has copy, drop {
        pool_id: ID,
        user: address,
        amount_in: u64,
        amount_out: u64,
    }

    /// VULNERABLE: Event emitted BEFORE state changes
    public entry fun swap<T, U>(
        pool_in: &mut Pool<T>,
        pool_out: &mut Pool<U>,
        coin_in: Coin<T>,
        min_out: u64,
        ctx: &mut TxContext
    ) {
        let amount_in = coin::value(&coin_in);
        let amount_out = calculate_output(amount_in);
        
        // VULNERABLE: Event emitted before validation and state change
        event::emit(SwapEvent {
            pool_id: object::id(pool_in),
            user: tx_context::sender(ctx),
            amount_in,
            amount_out,
        });
        
        // These assertions might fail AFTER event was emitted!
        assert!(amount_out >= min_out, E_INVALID_AMOUNT);
        assert!(balance::value(&pool_out.balance) >= amount_out, E_INSUFFICIENT_BALANCE);
        
        // State changes happen after event
        balance::join(&mut pool_in.balance, coin::into_balance(coin_in));
        let out_balance = balance::split(&mut pool_out.balance, amount_out);
        let coin_out = coin::from_balance(out_balance, ctx);
        
        transfer::public_transfer(coin_out, tx_context::sender(ctx));
    }
}

module vulnerable::auction {
    use sui::event;

    public struct BidEvent has copy, drop {
        auction_id: ID,
        bidder: address,
        amount: u64,
        is_winning: bool,  // VULNERABLE: May be wrong
    }

    /// VULNERABLE: Event data may not reflect final state
    public entry fun place_bid(
        auction: &mut Auction,
        amount: u64,
        ctx: &mut TxContext
    ) {
        let bidder = tx_context::sender(ctx);
        
        // Emit with current assumption
        let is_winning = amount > auction.highest_bid;
        
        event::emit(BidEvent {
            auction_id: object::id(auction),
            bidder,
            amount,
            is_winning,  // Could be wrong if concurrent bids
        });
        
        // State update
        if (amount > auction.highest_bid) {
            auction.highest_bid = amount;
            auction.highest_bidder = bidder;
        };
        // is_winning in event might not match actual outcome!
    }
}

module vulnerable::vault {
    use sui::event;

    public struct DepositEvent has copy, drop {
        vault_id: ID,
        user: address,
        amount: u64,
        new_balance: u64,
    }

    /// VULNERABLE: Missing event on some code paths
    public entry fun deposit(
        vault: &mut Vault,
        coins: Coin<SUI>,
        ctx: &mut TxContext
    ) {
        let amount = coin::value(&coins);
        
        // Early return without event!
        if (amount == 0) {
            coin::destroy_zero(coins);
            return  // No event emitted for zero deposit
        };
        
        balance::join(&mut vault.balance, coin::into_balance(coins));
        
        // Only emit for non-zero deposits
        event::emit(DepositEvent {
            vault_id: object::id(vault),
            user: tx_context::sender(ctx),
            amount,
            new_balance: balance::value(&vault.balance),
        });
    }

    /// VULNERABLE: No event at all
    public entry fun withdraw(
        vault: &mut Vault,
        amount: u64,
        ctx: &mut TxContext
    ) {
        let coins = coin::take(&mut vault.balance, amount, ctx);
        transfer::public_transfer(coins, tx_context::sender(ctx));
        // No WithdrawEvent emitted!
        // Off-chain systems won't know about withdrawals
    }
}

module vulnerable::token {
    use sui::event;

    /// VULNERABLE: Event doesn't include all relevant data
    public struct TransferEvent has copy, drop {
        token_id: ID,
        to: address,
        // Missing: from address, amount, timestamp
    }

    /// VULNERABLE: Duplicate events in loops
    public entry fun batch_transfer(
        tokens: vector<Token>,
        recipients: vector<address>,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&tokens);
        let mut i = 0;
        
        while (i < len) {
            let token = vector::pop_back(&mut tokens);
            let recipient = *vector::borrow(&recipients, i);
            
            // Emitting inside loop - potential duplicate if same token transferred twice
            event::emit(TransferEvent {
                token_id: object::id(&token),
                to: recipient,
            });
            
            transfer::public_transfer(token, recipient);
            i = i + 1;
        };
        
        vector::destroy_empty(tokens);
    }
}
```

## Secure Example

```move
module secure::exchange {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::event;
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};
    use sui::clock::{Self, Clock};

    const E_INSUFFICIENT_BALANCE: u64 = 1;
    const E_INVALID_AMOUNT: u64 = 2;
    const E_SLIPPAGE_EXCEEDED: u64 = 3;

    public struct Pool<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        total_swaps: u64,
    }

    /// SECURE: Comprehensive event with all relevant data
    public struct SwapExecuted has copy, drop {
        pool_in_id: ID,
        pool_out_id: ID,
        user: address,
        amount_in: u64,
        amount_out: u64,
        fee_amount: u64,
        pool_in_balance_after: u64,
        pool_out_balance_after: u64,
        timestamp_ms: u64,
        tx_digest: vector<u8>,
    }

    /// SECURE: Event emitted AFTER all state changes succeed
    public entry fun swap<T, U>(
        pool_in: &mut Pool<T>,
        pool_out: &mut Pool<U>,
        coin_in: Coin<T>,
        min_out: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let amount_in = coin::value(&coin_in);
        let fee_amount = calculate_fee(amount_in);
        let amount_out = calculate_output(amount_in - fee_amount);
        
        // Validate BEFORE any changes
        assert!(amount_out >= min_out, E_SLIPPAGE_EXCEEDED);
        assert!(balance::value(&pool_out.balance) >= amount_out, E_INSUFFICIENT_BALANCE);
        
        // Perform state changes
        balance::join(&mut pool_in.balance, coin::into_balance(coin_in));
        let out_balance = balance::split(&mut pool_out.balance, amount_out);
        let coin_out = coin::from_balance(out_balance, ctx);
        
        pool_in.total_swaps = pool_in.total_swaps + 1;
        
        // Transfer output
        let user = tx_context::sender(ctx);
        transfer::public_transfer(coin_out, user);
        
        // SECURE: Event emitted AFTER all changes complete
        // Event data reflects actual final state
        event::emit(SwapExecuted {
            pool_in_id: object::id(pool_in),
            pool_out_id: object::id(pool_out),
            user,
            amount_in,
            amount_out,
            fee_amount,
            pool_in_balance_after: balance::value(&pool_in.balance),
            pool_out_balance_after: balance::value(&pool_out.balance),
            timestamp_ms: clock::timestamp_ms(clock),
            tx_digest: tx_context::digest(ctx),
        });
    }
}

module secure::auction {
    use sui::event;
    use sui::clock::{Self, Clock};

    /// SECURE: Event reflects actual outcome
    public struct BidPlaced has copy, drop {
        auction_id: ID,
        bidder: address,
        bid_amount: u64,
        previous_highest: u64,
        is_new_highest: bool,
        timestamp_ms: u64,
    }

    public struct BidOutbid has copy, drop {
        auction_id: ID,
        outbid_bidder: address,
        outbid_amount: u64,
        new_highest_bidder: address,
        new_highest_amount: u64,
    }

    /// SECURE: Emit events that accurately reflect what happened
    public entry fun place_bid(
        auction: &mut Auction,
        bid_coin: Coin<SUI>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let bid_amount = coin::value(&bid_coin);
        let bidder = tx_context::sender(ctx);
        let previous_highest = auction.highest_bid;
        let previous_bidder = auction.highest_bidder;
        
        // Determine outcome first
        let is_new_highest = bid_amount > previous_highest;
        
        // Update state
        if (is_new_highest) {
            // Refund previous highest bidder
            if (previous_highest > 0) {
                let refund = coin::take(&mut auction.escrow, previous_highest, ctx);
                transfer::public_transfer(refund, previous_bidder);
                
                // Emit outbid event for previous leader
                event::emit(BidOutbid {
                    auction_id: object::id(auction),
                    outbid_bidder: previous_bidder,
                    outbid_amount: previous_highest,
                    new_highest_bidder: bidder,
                    new_highest_amount: bid_amount,
                });
            };
            
            auction.highest_bid = bid_amount;
            auction.highest_bidder = bidder;
            balance::join(&mut auction.escrow, coin::into_balance(bid_coin));
        } else {
            // Return bid to sender (not high enough)
            transfer::public_transfer(bid_coin, bidder);
        };
        
        // SECURE: Event emitted after state finalized
        event::emit(BidPlaced {
            auction_id: object::id(auction),
            bidder,
            bid_amount,
            previous_highest,
            is_new_highest,  // Now accurately reflects outcome
            timestamp_ms: clock::timestamp_ms(clock),
        });
    }
}

module secure::vault {
    use sui::event;
    use sui::clock::{Self, Clock};

    public struct DepositExecuted has copy, drop {
        vault_id: ID,
        user: address,
        amount: u64,
        balance_before: u64,
        balance_after: u64,
        timestamp_ms: u64,
    }

    public struct WithdrawExecuted has copy, drop {
        vault_id: ID,
        user: address,
        amount: u64,
        balance_before: u64,
        balance_after: u64,
        timestamp_ms: u64,
    }

    /// SECURE: Events on ALL code paths
    public entry fun deposit(
        vault: &mut Vault,
        coins: Coin<SUI>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let amount = coin::value(&coins);
        let balance_before = balance::value(&vault.balance);
        
        // Handle zero deposits consistently
        if (amount == 0) {
            coin::destroy_zero(coins);
            // Still emit event for zero deposit (for consistency)
            event::emit(DepositExecuted {
                vault_id: object::id(vault),
                user: tx_context::sender(ctx),
                amount: 0,
                balance_before,
                balance_after: balance_before,  // Unchanged
                timestamp_ms: clock::timestamp_ms(clock),
            });
            return
        };
        
        balance::join(&mut vault.balance, coin::into_balance(coins));
        let balance_after = balance::value(&vault.balance);
        
        event::emit(DepositExecuted {
            vault_id: object::id(vault),
            user: tx_context::sender(ctx),
            amount,
            balance_before,
            balance_after,
            timestamp_ms: clock::timestamp_ms(clock),
        });
    }

    /// SECURE: Withdraw has corresponding event
    public entry fun withdraw(
        vault: &mut Vault,
        amount: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let balance_before = balance::value(&vault.balance);
        
        let coins = coin::take(&mut vault.balance, amount, ctx);
        let user = tx_context::sender(ctx);
        
        transfer::public_transfer(coins, user);
        
        let balance_after = balance::value(&vault.balance);
        
        // SECURE: Withdrawal event emitted
        event::emit(WithdrawExecuted {
            vault_id: object::id(vault),
            user,
            amount,
            balance_before,
            balance_after,
            timestamp_ms: clock::timestamp_ms(clock),
        });
    }
}

module secure::token {
    use sui::event;

    /// SECURE: Comprehensive transfer event
    public struct TokenTransferred has copy, drop {
        token_id: ID,
        from: address,
        to: address,
        timestamp_ms: u64,
    }

    /// SECURE: Batch event for batch operations
    public struct BatchTransferCompleted has copy, drop {
        transfer_count: u64,
        from: address,
        timestamp_ms: u64,
    }

    /// SECURE: Efficient batch event handling
    public entry fun batch_transfer(
        tokens: vector<Token>,
        recipients: vector<address>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&tokens);
        assert!(len == vector::length(&recipients), E_LENGTH_MISMATCH);
        
        let from = tx_context::sender(ctx);
        let timestamp = clock::timestamp_ms(clock);
        let mut i = 0;
        
        while (i < len) {
            let token = vector::pop_back(&mut tokens);
            let recipient = *vector::borrow(&recipients, i);
            
            // Individual transfer event
            event::emit(TokenTransferred {
                token_id: object::id(&token),
                from,
                to: recipient,
                timestamp_ms: timestamp,
            });
            
            transfer::public_transfer(token, recipient);
            i = i + 1;
        };
        
        vector::destroy_empty(tokens);
        
        // Summary event for batch
        event::emit(BatchTransferCompleted {
            transfer_count: len,
            from,
            timestamp_ms: timestamp,
        });
    }
}
```

## Event Design Patterns

### Pattern 1: Before/After State in Events

```move
public struct StateChangeEvent has copy, drop {
    object_id: ID,
    field_name: vector<u8>,
    value_before: u64,
    value_after: u64,
    changed_by: address,
}

public fun update_with_event(obj: &mut MyObject, new_value: u64, ctx: &TxContext) {
    let before = obj.value;
    obj.value = new_value;
    
    event::emit(StateChangeEvent {
        object_id: object::id(obj),
        field_name: b"value",
        value_before: before,
        value_after: new_value,
        changed_by: tx_context::sender(ctx),
    });
}
```

### Pattern 2: Event Versioning

```move
const EVENT_VERSION: u8 = 2;

public struct DepositEventV2 has copy, drop {
    version: u8,  // For indexer compatibility
    vault_id: ID,
    user: address,
    amount: u64,
    // V2 additions
    deposit_type: u8,
    referrer: Option<address>,
}

public fun emit_deposit_event(/* ... */) {
    event::emit(DepositEventV2 {
        version: EVENT_VERSION,
        // ...
    });
}
```

### Pattern 3: Failure Events

```move
public struct OperationFailed has copy, drop {
    operation: vector<u8>,
    user: address,
    reason: u64,
    timestamp_ms: u64,
}

public fun try_operation(/* ... */): bool {
    if (!validate_preconditions()) {
        event::emit(OperationFailed {
            operation: b"swap",
            user: tx_context::sender(ctx),
            reason: E_VALIDATION_FAILED,
            timestamp_ms: clock::timestamp_ms(clock),
        });
        return false
    };
    
    // Proceed with operation...
    true
}
```

### Pattern 4: Correlation IDs

```move
public struct OrderCreated has copy, drop {
    order_id: ID,
    correlation_id: vector<u8>,  // Link related events
    user: address,
}

public struct OrderFilled has copy, drop {
    order_id: ID,
    correlation_id: vector<u8>,  // Same correlation ID
    fill_amount: u64,
}

public struct OrderCancelled has copy, drop {
    order_id: ID,
    correlation_id: vector<u8>,  // Same correlation ID
    reason: u8,
}
```

## Recommended Mitigations

### 1. Emit Events After State Changes

```move
// Do all state changes first
state.value = new_value;
balance::join(&mut state.balance, deposit);

// Then emit event reflecting final state
event::emit(StateChanged { /* final values */ });
```

### 2. Include Before/After Values

```move
event::emit(BalanceChanged {
    balance_before: old_balance,
    balance_after: new_balance,
    delta: new_balance - old_balance,
});
```

### 3. Emit Events on All Code Paths

```move
if (condition) {
    // path A
    event::emit(PathAEvent { /* ... */ });
} else {
    // path B
    event::emit(PathBEvent { /* ... */ });
};
// No silent paths!
```

### 4. Include Timestamps and Transaction Info

```move
event::emit(MyEvent {
    timestamp_ms: clock::timestamp_ms(clock),
    tx_digest: tx_context::digest(ctx),
    epoch: tx_context::epoch(ctx),
});
```

### 5. Use Structured Event Types

```move
// Good: Specific event types
public struct DepositExecuted has copy, drop { /* ... */ }
public struct WithdrawExecuted has copy, drop { /* ... */ }

// Bad: Generic event with type field
public struct GenericEvent has copy, drop {
    event_type: u8,  // Harder to index/filter
}
```

## Testing Checklist

- [ ] Verify events are emitted after state changes complete
- [ ] Confirm events on all code paths (including error paths)
- [ ] Check event data matches actual state changes
- [ ] Test that aborted transactions don't emit events
- [ ] Verify no duplicate events in loops
- [ ] Confirm events include sufficient context (IDs, timestamps)
- [ ] Test event ordering matches execution order
- [ ] Verify before/after values are accurate

## Related Vulnerabilities

- [Event Design Vulnerabilities](../event-design-vulnerabilities/)
- [General Move Logic Errors](../general-move-logic-errors/)
- [PTB Ordering Issues](../ptb-ordering-issues/)
- [Access-Control Mistakes](../access-control-mistakes/)
