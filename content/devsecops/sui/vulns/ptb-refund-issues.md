+++
title = '18. PTB Refund Issues'
date = '2025-11-26T00:00:00Z'
weight = 18
+++

## Overview

Improper refund or undo patterns in Programmable Transaction Blocks (PTBs) can leave state inconsistent when partial execution occurs. Write-then-undo patterns are particularly dangerous as they can be exploited.

## Risk Level

**Medium** — Can lead to inconsistent state and protocol manipulation.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A04 (Insecure Design) | CWE-841 (Improper Enforcement of Behavioral Workflow), CWE-662 (Improper Synchronization) |

## The Problem

In PTBs, if a later operation fails, earlier operations are NOT rolled back within custom logic. Sui's atomicity ensures the transaction fails entirely, but if your code has a "refund" or "undo" function, partial execution becomes possible.

### Dangerous Pattern

```
1. debit(account, 100)    // Subtract from balance
2. credit(other, 100)     // Add to other (might fail)
3. If step 2 fails, state is inconsistent
```

## Vulnerable Example

```move
module vulnerable::escrow {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    public struct Escrow has key {
        id: UID,
        deposited: u64,
        refund_pending: bool,
    }

    public struct UserBalance has key {
        id: UID,
        balance: u64,
    }

    /// VULNERABLE: Debit before credit confirmed
    public entry fun deposit_to_escrow(
        user: &mut UserBalance,
        escrow: &mut Escrow,
        amount: u64,
    ) {
        // Debit happens first
        assert!(user.balance >= amount, E_INSUFFICIENT);
        user.balance = user.balance - amount;
        
        // Credit to escrow
        // If this somehow fails (e.g., invariant check), 
        // user lost funds with no escrow increase
        escrow.deposited = escrow.deposited + amount;
    }

    /// VULNERABLE: Refund can be called independently
    public entry fun request_refund(escrow: &mut Escrow) {
        escrow.refund_pending = true;
    }

    /// VULNERABLE: Process refund without proper state checks
    public entry fun process_refund(
        user: &mut UserBalance,
        escrow: &mut Escrow,
        amount: u64,
    ) {
        assert!(escrow.refund_pending, E_NO_REFUND);
        
        // Credit user first
        user.balance = user.balance + amount;
        
        // Then debit escrow — what if this fails?
        assert!(escrow.deposited >= amount, E_INSUFFICIENT_ESCROW);
        escrow.deposited = escrow.deposited - amount;
    }
}

module vulnerable::trading {
    /// VULNERABLE: Partial fill can leave orders in bad state
    public entry fun fill_order(
        order: &mut Order,
        fill_amount: u64,
        payment: Coin<SUI>,
    ) {
        // Update order first
        order.filled = order.filled + fill_amount;
        order.status = if (order.filled == order.amount) { 1 } else { 0 };
        
        // Process payment — might fail
        let required = fill_amount * order.price;
        assert!(coin::value(&payment) >= required, E_INSUFFICIENT);
        
        // If payment assertion fails, order.filled is already updated!
    }

    /// VULNERABLE: Undo function can be called in PTB
    public entry fun undo_fill(
        order: &mut Order,
        undo_amount: u64,
    ) {
        // Attacker can call fill() then undo() in same PTB
        // Getting the goods without actually paying
        order.filled = order.filled - undo_amount;
    }
}
```

### Attack: PTB Partial Execution

```
// Attacker's PTB
Transaction {
    commands: [
        // Fill order without proper payment
        Call(trading::fill_order, [order, 1000, insufficient_payment]),
        // If above fails, no problem — atomic rollback
        
        // Or: Fill then immediately undo
        Call(trading::fill_order, [order, 1000, payment]),
        Call(trading::undo_fill, [order, 1000]),
        // Attacker got something for nothing
    ]
}
```

## Secure Example

```move
module secure::escrow {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    public struct Escrow has key {
        id: UID,
        depositor: address,
        beneficiary: address,
        coins: Coin<SUI>,
        state: u8,  // 0 = active, 1 = released, 2 = refunded
    }

    /// SECURE: Check-then-write, all in one atomic operation
    public entry fun deposit(
        depositor_coins: Coin<SUI>,
        beneficiary: address,
        ctx: &mut TxContext
    ) {
        // All validation first
        let amount = coin::value(&depositor_coins);
        assert!(amount > 0, E_ZERO_AMOUNT);
        
        // Single atomic state creation
        let escrow = Escrow {
            id: object::new(ctx),
            depositor: tx_context::sender(ctx),
            beneficiary,
            coins: depositor_coins,
            state: 0,
        };
        
        transfer::share_object(escrow);
    }

    /// SECURE: Atomic release — all or nothing
    public entry fun release(
        escrow: Escrow,
        ctx: &TxContext
    ) {
        let Escrow { id, depositor, beneficiary, coins, state } = escrow;
        
        // All checks before any state change
        assert!(tx_context::sender(ctx) == depositor, E_NOT_DEPOSITOR);
        assert!(state == 0, E_ALREADY_PROCESSED);
        
        // Atomic: destroy escrow and transfer coins
        object::delete(id);
        transfer::public_transfer(coins, beneficiary);
    }

    /// SECURE: Atomic refund
    public entry fun refund(
        escrow: Escrow,
        ctx: &TxContext
    ) {
        let Escrow { id, depositor, beneficiary: _, coins, state } = escrow;
        
        assert!(tx_context::sender(ctx) == depositor, E_NOT_DEPOSITOR);
        assert!(state == 0, E_ALREADY_PROCESSED);
        
        object::delete(id);
        transfer::public_transfer(coins, depositor);
    }
}

module secure::trading {
    use sui::object::{Self, UID, ID};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    public struct Order has key {
        id: UID,
        maker: address,
        amount: u64,
        price: u64,
        coins_escrowed: Coin<SUI>,
    }

    /// Hot potato ensures fill completes
    public struct FillReceipt {
        order_id: ID,
        fill_amount: u64,
        payment_required: u64,
    }

    /// SECURE: Start fill, get receipt
    public fun start_fill(
        order: &Order,
        fill_amount: u64,
    ): FillReceipt {
        assert!(fill_amount <= order.amount, E_OVERFILL);
        
        FillReceipt {
            order_id: object::id(order),
            fill_amount,
            payment_required: fill_amount * order.price,
        }
    }

    /// SECURE: Complete fill with receipt and payment
    public fun complete_fill(
        order: &mut Order,
        receipt: FillReceipt,
        payment: Coin<SUI>,
        ctx: &mut TxContext
    ): Coin<SUI> {
        let FillReceipt { order_id, fill_amount, payment_required } = receipt;
        
        // Verify receipt matches order
        assert!(order_id == object::id(order), E_WRONG_ORDER);
        
        // Verify payment
        assert!(coin::value(&payment) >= payment_required, E_INSUFFICIENT);
        
        // All validated — now update state
        order.amount = order.amount - fill_amount;
        
        // Return escrowed coins to taker
        let filled_coins = coin::split(&mut order.coins_escrowed, fill_amount, ctx);
        
        // Payment to maker
        transfer::public_transfer(payment, order.maker);
        
        filled_coins
    }

    // NO undo_fill function — fills are final
}
```

## Safe State Update Patterns

### Pattern 1: Check-Effects-Interactions

```move
public entry fun operation(state: &mut State, input: u64, payment: Coin<SUI>) {
    // 1. CHECKS - All validation
    assert!(input > 0, E_ZERO_INPUT);
    assert!(coin::value(&payment) >= calculate_cost(input), E_INSUFFICIENT);
    
    // 2. EFFECTS - Update state
    state.processed = state.processed + input;
    
    // 3. INTERACTIONS - External transfers last
    coin::join(&mut state.treasury, payment);
}
```

### Pattern 2: Hot Potato for Multi-Step

```move
/// Receipt ensures operation completes
public struct OperationReceipt {
    required_payment: u64,
}

public fun start(amount: u64): OperationReceipt {
    OperationReceipt { required_payment: amount * PRICE }
}

public fun finish(receipt: OperationReceipt, payment: Coin<SUI>) {
    let OperationReceipt { required_payment } = receipt;
    assert!(coin::value(&payment) >= required_payment, E_INSUFFICIENT);
    // Operation guaranteed to complete
}
```

### Pattern 3: No External Undo Functions

```move
// BAD: Undo can be called by attacker
public entry fun undo_action(state: &mut State, ...) { }

// GOOD: Undo is internal only
fun internal_undo(state: &mut State, ...) { }

// GOOD: Or use hot potato that must be consumed
public struct Action { }
public fun commit_action(action: Action) { let Action {} = action; }
```

### Pattern 4: Atomic Object Operations

```move
/// Use object lifecycle for atomicity
public entry fun process(
    item: Item,  // Consume object
    payment: Coin<SUI>,
    ctx: &mut TxContext
) {
    // Validate payment
    assert!(coin::value(&payment) >= item.price, E_INSUFFICIENT);
    
    // Destroy old object, create new
    let Item { id, data, price: _ } = item;
    object::delete(id);
    
    // Create result
    let result = ProcessedItem { id: object::new(ctx), data };
    transfer::transfer(result, tx_context::sender(ctx));
}
```

## Recommended Mitigations

### 1. Use Check-Then-Write Pattern

```move
// All checks before any writes
assert!(condition1, E1);
assert!(condition2, E2);
assert!(condition3, E3);
// Now safe to modify state
state.value = new_value;
```

### 2. Use Hot Potatoes for Finalization

```move
// Start returns receipt that must be consumed
public fun start(): Receipt { }
// Finish consumes receipt — cannot skip
public fun finish(receipt: Receipt, payment: Coin) { }
```

### 3. Never Provide Public Undo Functions

```move
// If undo is needed, make it internal and time-locked
fun internal_undo(...) { }

// Or require admin capability
public entry fun emergency_undo(admin_cap: &AdminCap, ...) { }
```

### 4. Make Operations Atomic

```move
// Instead of debit() then credit()
public entry fun transfer(from: &mut Balance, to: &mut Balance, amount: u64) {
    // Single function, single transaction
    assert!(from.value >= amount, E_INSUFFICIENT);
    from.value = from.value - amount;
    to.value = to.value + amount;
}
```

## Testing Checklist

- [ ] Test what happens if a function aborts mid-execution
- [ ] Verify no "undo" functions can be called in PTBs
- [ ] Test that hot potatoes cannot be dropped
- [ ] Verify state remains consistent after any abort
- [ ] Test PTBs with reordered operations

## Related Vulnerabilities

- [PTB Ordering Issues](../ptb-ordering-issues/)
- [General Move Logic Errors](../general-move-logic-errors/)
- [Event State Inconsistency](../event-state-inconsistency/)
