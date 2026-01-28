+++
title = '17. PTB Ordering Issues'
date = '2025-11-26T00:00:00Z'
weight = 17
+++

## Overview

Programmable Transaction Blocks (PTBs) in Sui allow multiple operations in a single transaction. Attackers can reorder or interleave calls in unexpected ways, bypassing invariants that assume specific execution order.

## Risk Level

**High** — Can bypass access control and break protocol invariants.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A04 (Insecure Design) | CWE-841 (Improper Enforcement of Behavioral Workflow), CWE-662 (Improper Synchronization) | 

## The Problem

### PTB Characteristics

- Multiple Move calls in one atomic transaction
- Caller controls the order of calls
- Intermediate results can be passed between calls
- All calls see the same object state (within the PTB)

### Vulnerability Pattern

``` move
Expected:  auth_check() → perform_action()
Attacker:  perform_action() → some_cleanup()  // Skip auth entirely
```

## Vulnerable Example

```move
module vulnerable::multistep {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    public struct AuthSession has key {
        id: UID,
        user: address,
        is_authenticated: bool,
    }

    public struct Vault has key {
        id: UID,
        balance: u64,
    }

    /// Step 1: User calls this to authenticate
    public entry fun authenticate(
        session: &mut AuthSession,
        password_hash: vector<u8>,
    ) {
        // Verify password
        assert!(verify_password(password_hash), E_WRONG_PASSWORD);
        session.is_authenticated = true;
    }

    /// Step 2: User calls this to withdraw (should be after auth)
    /// VULNERABLE: Assumes authenticate was called first
    public entry fun withdraw(
        session: &AuthSession,
        vault: &mut Vault,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // This check can be bypassed in a PTB!
        assert!(session.is_authenticated, E_NOT_AUTHENTICATED);
        
        vault.balance = vault.balance - amount;
        // ... transfer to user
    }

    /// VULNERABLE: Cleanup resets auth state
    public entry fun logout(session: &mut AuthSession) {
        session.is_authenticated = false;
    }
}

module vulnerable::flashloan {
    public struct Pool has key {
        id: UID,
        balance: u64,
        borrowed: u64,
    }

    /// VULNERABLE: No hot potato to enforce repayment
    public entry fun borrow(
        pool: &mut Pool,
        amount: u64,
    ) {
        assert!(pool.balance >= amount, E_INSUFFICIENT);
        pool.borrowed = pool.borrowed + amount;
        pool.balance = pool.balance - amount;
        // ... give coins to borrower
    }

    /// Repayment can be skipped in PTB
    public entry fun repay(
        pool: &mut Pool,
        amount: u64,
    ) {
        pool.borrowed = pool.borrowed - amount;
        pool.balance = pool.balance + amount;
        // ... receive coins
    }
}
```

### Attack: PTB Reordering

``` move
// Attacker's PTB:
Transaction {
    // Skip authenticate entirely!
    // Or: authenticate with wrong password, then proceed anyway
    
    commands: [
        // Borrow from flash loan
        Call(flashloan::borrow, [pool, 1000000]),
        
        // Use borrowed funds for exploit
        Call(some_protocol::exploit, [borrowed_coins]),
        
        // Never call flashloan::repay
        // Transaction completes successfully!
    ]
}
```

## Secure Example

```move
module secure::multistep {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};

    /// Hot potato pattern — must be consumed in same transaction
    public struct AuthToken {
        user: address,
        expires_at: u64,
        vault_id: ID,
    }

    public struct Vault has key {
        id: UID,
        balance: u64,
    }

    /// SECURE: Returns hot potato that must be consumed
    public fun authenticate(
        password_hash: vector<u8>,
        vault: &Vault,
        clock: &Clock,
        ctx: &TxContext
    ): AuthToken {
        assert!(verify_password(password_hash, ctx), E_WRONG_PASSWORD);
        
        AuthToken {
            user: tx_context::sender(ctx),
            expires_at: clock::timestamp_ms(clock) + 60000, // 1 minute
            vault_id: object::id(vault),
        }
    }

    /// SECURE: Consumes hot potato, ensuring auth happened
    public fun withdraw(
        token: AuthToken,
        vault: &mut Vault,
        amount: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let AuthToken { user, expires_at, vault_id } = token;
        
        // Verify token is for this vault
        assert!(vault_id == object::id(vault), E_WRONG_VAULT);
        
        // Verify token hasn't expired
        assert!(clock::timestamp_ms(clock) < expires_at, E_EXPIRED);
        
        // Verify caller is the authenticated user
        assert!(tx_context::sender(ctx) == user, E_WRONG_USER);
        
        vault.balance = vault.balance - amount;
        // Token is consumed — cannot be reused
    }
}

module secure::flashloan {
    use sui::object::{Self, UID, ID};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    public struct Pool has key {
        id: UID,
        coins: Coin<SUI>,
    }

    /// Hot potato — MUST be repaid before transaction ends
    public struct FlashLoanReceipt {
        pool_id: ID,
        amount: u64,
        fee: u64,
    }

    /// SECURE: Returns receipt that must be consumed
    public fun borrow(
        pool: &mut Pool,
        amount: u64,
        ctx: &mut TxContext
    ): (Coin<SUI>, FlashLoanReceipt) {
        assert!(coin::value(&pool.coins) >= amount, E_INSUFFICIENT);
        
        let borrowed = coin::split(&mut pool.coins, amount, ctx);
        let fee = amount / 1000; // 0.1% fee
        
        let receipt = FlashLoanReceipt {
            pool_id: object::id(pool),
            amount,
            fee,
        };
        
        (borrowed, receipt)
    }

    /// SECURE: Must be called to destroy receipt
    public fun repay(
        pool: &mut Pool,
        receipt: FlashLoanReceipt,
        repayment: Coin<SUI>,
    ) {
        let FlashLoanReceipt { pool_id, amount, fee } = receipt;
        
        // Verify correct pool
        assert!(pool_id == object::id(pool), E_WRONG_POOL);
        
        // Verify full repayment with fee
        assert!(coin::value(&repayment) >= amount + fee, E_INSUFFICIENT_REPAYMENT);
        
        coin::join(&mut pool.coins, repayment);
        
        // Receipt consumed — loan is repaid
    }
}
```

## PTB-Safe Patterns

### Pattern 1: Hot Potato (Must Consume)

```move
/// No abilities — cannot be stored, dropped, or copied
/// MUST be consumed in the same transaction
public struct MustConsume {
    value: u64,
}

public fun start_operation(): MustConsume {
    MustConsume { value: 100 }
}

public fun finish_operation(potato: MustConsume) {
    let MustConsume { value: _ } = potato;
    // Potato consumed — operation complete
}
```

### Pattern 2: Atomic Operations

```move
/// Combine check and action in single function
public entry fun authenticated_withdraw(
    password_hash: vector<u8>,
    vault: &mut Vault,
    amount: u64,
    ctx: &mut TxContext
) {
    // Auth and action in same call — cannot be separated
    assert!(verify_password(password_hash, ctx), E_WRONG_PASSWORD);
    vault.balance = vault.balance - amount;
}
```

### Pattern 3: Sequence Numbers

```move
public struct StateMachine has key {
    id: UID,
    current_step: u64,
    expected_next: u64,
}

public entry fun step_one(state: &mut StateMachine) {
    assert!(state.current_step == 0, E_WRONG_STEP);
    state.current_step = 1;
    state.expected_next = 2;
}

public entry fun step_two(state: &mut StateMachine) {
    assert!(state.current_step == 1, E_WRONG_STEP);
    state.current_step = 2;
    // ...
}
```

### Pattern 4: Invariant Assertions

```move
/// Check invariants at function boundaries
public entry fun operation(state: &mut State, ...) {
    // Pre-conditions
    assert_invariants(state);
    
    // Perform operation
    // ...
    
    // Post-conditions
    assert_invariants(state);
}

fun assert_invariants(state: &State) {
    assert!(state.total == state.a + state.b, E_INVARIANT_BROKEN);
    assert!(state.balance >= state.minimum, E_UNDERCOLLATERALIZED);
}
```

## Recommended Mitigations

### 1. Use Hot Potatoes for Multi-Step Operations

```move
// Force the caller to complete the operation
public fun start(): Receipt { }
public fun finish(receipt: Receipt) { }
// Receipt has no abilities — must be consumed
```

### 2. Validate Invariants in Every Function

```move
public entry fun any_function(state: &mut State, ...) {
    // Don't assume previous function was called
    // Validate everything this function needs
}
```

### 3. Make Operations Atomic When Possible

```move
// Instead of: check() → action()
// Use: check_and_action()
```

### 4. Use Object Ownership for Authorization

```move
// Object ownership is enforced by Sui itself
public entry fun action(cap: &AdminCap, ...) {
    // Caller must own cap — cannot be bypassed
}
```

## Testing Checklist

- [ ] Test each function in isolation (not just expected sequence)
- [ ] Test with functions called in reversed order
- [ ] Test skipping intermediate steps
- [ ] Verify hot potatoes cannot be stored or dropped
- [ ] Test that invariants hold regardless of call order

## Related Vulnerabilities

- [PTB Refund Issues](../ptb-refund-issues/)
- [General Move Logic Errors](../general-move-logic-errors/)
- [Access-Control Mistakes](../access-control-mistakes/)