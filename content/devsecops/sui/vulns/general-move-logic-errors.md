+++
title = '10. General Move Logic Errors'
date = '2025-11-26T00:00:00Z'
weight = 10
+++

## Overview

General logic errors in Move contracts include PTB (Programmable Transaction Block) reordering effects, incorrect mutation order, fee miscalculations, and state inconsistencies. These bugs are often subtle and can lead to fund loss or protocol manipulation.

## Risk Level

**Medium to Critical** — Varies based on the specific logic error.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control), A04 (Insecure Design) | CWE-841 (Improper Enforcement of Behavioral Workflow), CWE-362 (Race Condition) |

## The Problem

### Categories of Logic Errors

1. **State mutation order** — Operations performed in wrong sequence
2. **PTB assumptions** — Expecting specific call ordering in transactions
3. **Arithmetic errors** — Rounding, precision loss, fee calculations
4. **Invariant violations** — Protocol rules not enforced consistently
5. **Edge cases** — Zero values, empty collections, boundary conditions

## Vulnerable Examples

### Example 1: Incorrect Mutation Order

```move
module vulnerable::lending {
    use sui::object::UID;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    public struct LendingPool has key {
        id: UID,
        total_deposits: u64,
        total_borrows: u64,
        interest_rate: u64,
    }

    /// VULNERABLE: Interest calculated on old balance
    public entry fun deposit(
        pool: &mut LendingPool,
        payment: Coin<SUI>,
    ) {
        let amount = coin::value(&payment);
        
        // WRONG: Accruing interest AFTER updating deposits
        // New deposit earns interest it shouldn't
        pool.total_deposits = pool.total_deposits + amount;
        
        // Interest calculated on inflated total
        accrue_interest(pool);
        
        // ... store payment
    }

    /// VULNERABLE: Withdraw before interest accrual
    public entry fun withdraw(
        pool: &mut LendingPool,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // WRONG: Withdrawing before accruing interest
        // User avoids paying accumulated interest
        pool.total_deposits = pool.total_deposits - amount;
        
        accrue_interest(pool);  // Too late!
    }
}
```

### Example 2: Fee Calculation Errors

```move
module vulnerable::exchange {
    const FEE_BPS: u64 = 30;  // 0.3%
    const BPS_DENOMINATOR: u64 = 10000;

    public struct Exchange has key {
        id: UID,
        accumulated_fees: u64,
    }

    /// VULNERABLE: Precision loss in fee calculation
    public fun calculate_fee(amount: u64): u64 {
        // For small amounts, this can round to 0
        // amount = 100, fee = 100 * 30 / 10000 = 0
        amount * FEE_BPS / BPS_DENOMINATOR
    }

    /// VULNERABLE: Fee-on-fee calculation
    public fun swap_with_fee(
        exchange: &mut Exchange,
        input_amount: u64,
    ): u64 {
        let fee = calculate_fee(input_amount);
        let net_input = input_amount - fee;
        
        // Calculate output
        let output = calculate_output(net_input);
        
        // WRONG: Taking fee again on output!
        let output_fee = calculate_fee(output);
        let net_output = output - output_fee;
        
        // User pays fee twice
        exchange.accumulated_fees = exchange.accumulated_fees + fee + output_fee;
        
        net_output
    }

    /// VULNERABLE: Integer division ordering
    public fun calculate_share(amount: u64, user_balance: u64, total_balance: u64): u64 {
        // WRONG: Division before multiplication loses precision
        // If user_balance < total_balance, this might return 0
        amount * (user_balance / total_balance)
        
        // Should be: (amount * user_balance) / total_balance
    }
}
```

### Example 3: State Invariant Violations

```move
module vulnerable::amm {
    public struct Pool has key {
        id: UID,
        reserve_a: u64,
        reserve_b: u64,
        k: u64,  // Constant product: reserve_a * reserve_b = k
    }

    /// VULNERABLE: k not updated after liquidity change
    public entry fun add_liquidity(
        pool: &mut Pool,
        amount_a: u64,
        amount_b: u64,
    ) {
        pool.reserve_a = pool.reserve_a + amount_a;
        pool.reserve_b = pool.reserve_b + amount_b;
        
        // FORGOT to update k!
        // pool.k = pool.reserve_a * pool.reserve_b;
        
        // Now k invariant is broken
        // Swaps will use stale k value
    }

    /// VULNERABLE: No check that k is maintained after swap
    public entry fun swap_a_for_b(
        pool: &mut Pool,
        amount_a_in: u64,
    ): u64 {
        let new_reserve_a = pool.reserve_a + amount_a_in;
        
        // Calculate output to maintain k
        // But rounding might break the invariant
        let amount_b_out = pool.reserve_b - (pool.k / new_reserve_a);
        
        pool.reserve_a = new_reserve_a;
        pool.reserve_b = pool.reserve_b - amount_b_out;
        
        // No assertion that k is still valid!
        // assert!(pool.reserve_a * pool.reserve_b >= pool.k, E_K_VIOLATED);
        
        amount_b_out
    }
}
```

## Secure Examples

### Secure Lending Pool

```move
module secure::lending {
    use sui::object::UID;
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::clock::{Self, Clock};

    public struct LendingPool has key {
        id: UID,
        total_deposits: u64,
        total_borrows: u64,
        interest_rate_per_ms: u64,
        last_update_ms: u64,
        accumulated_interest: u64,
    }

    /// SECURE: Always accrue interest first
    fun accrue_interest_internal(pool: &mut LendingPool, clock: &Clock) {
        let now = clock::timestamp_ms(clock);
        let elapsed = now - pool.last_update_ms;
        
        if (elapsed > 0) {
            let interest = (pool.total_borrows as u128) 
                * (pool.interest_rate_per_ms as u128) 
                * (elapsed as u128) 
                / 1_000_000_000_000;
            
            pool.accumulated_interest = pool.accumulated_interest + (interest as u64);
            pool.last_update_ms = now;
        }
    }

    /// SECURE: Interest accrued before state change
    public entry fun deposit(
        pool: &mut LendingPool,
        payment: Coin<SUI>,
        clock: &Clock,
    ) {
        // FIRST: Accrue interest on existing state
        accrue_interest_internal(pool, clock);
        
        // THEN: Update deposits
        let amount = coin::value(&payment);
        pool.total_deposits = pool.total_deposits + amount;
        
        // ... store payment
    }

    /// SECURE: Consistent ordering
    public entry fun withdraw(
        pool: &mut LendingPool,
        amount: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // FIRST: Accrue interest
        accrue_interest_internal(pool, clock);
        
        // THEN: Process withdrawal
        assert!(pool.total_deposits >= amount, E_INSUFFICIENT_LIQUIDITY);
        pool.total_deposits = pool.total_deposits - amount;
    }
}
```

### Secure Fee Calculations

```move
module secure::exchange {
    const FEE_BPS: u64 = 30;
    const BPS_DENOMINATOR: u64 = 10000;
    const MIN_FEE: u64 = 1;  // Minimum fee to prevent zero-fee exploits

    /// SECURE: Handle precision loss
    public fun calculate_fee(amount: u64): u64 {
        let fee = (amount * FEE_BPS) / BPS_DENOMINATOR;
        
        // Ensure minimum fee on non-zero amounts
        if (amount > 0 && fee == 0) {
            MIN_FEE
        } else {
            fee
        }
    }

    /// SECURE: Use u128 for intermediate calculations
    public fun calculate_share(
        amount: u64, 
        user_balance: u64, 
        total_balance: u64
    ): u64 {
        if (total_balance == 0) {
            return 0
        };
        
        // Use u128 to prevent overflow and maintain precision
        let result = ((amount as u128) * (user_balance as u128)) / (total_balance as u128);
        
        (result as u64)
    }

    /// SECURE: Single fee, clear calculation
    public fun swap_with_fee(
        exchange: &mut Exchange,
        input_amount: u64,
    ): u64 {
        assert!(input_amount > 0, E_ZERO_INPUT);
        
        let fee = calculate_fee(input_amount);
        let net_input = input_amount - fee;
        
        // Calculate output — no additional fee
        let output = calculate_output(net_input);
        
        exchange.accumulated_fees = exchange.accumulated_fees + fee;
        
        output
    }
}
```

### Secure AMM with Invariant Checks

```move
module secure::amm {
    const E_K_VIOLATED: u64 = 1;
    const E_ZERO_LIQUIDITY: u64 = 2;
    const E_SLIPPAGE: u64 = 3;

    public struct Pool has key {
        id: UID,
        reserve_a: u64,
        reserve_b: u64,
    }

    /// Calculate k from current reserves
    fun get_k(pool: &Pool): u128 {
        (pool.reserve_a as u128) * (pool.reserve_b as u128)
    }

    /// SECURE: Update reserves and verify invariant
    public entry fun add_liquidity(
        pool: &mut Pool,
        amount_a: u64,
        amount_b: u64,
    ) {
        assert!(amount_a > 0 && amount_b > 0, E_ZERO_LIQUIDITY);
        
        // For existing pool, require proportional deposit
        if (pool.reserve_a > 0) {
            let expected_b = ((amount_a as u128) * (pool.reserve_b as u128)) 
                / (pool.reserve_a as u128);
            // Allow small deviation for rounding
            assert!(
                amount_b >= (expected_b as u64) - 1 && 
                amount_b <= (expected_b as u64) + 1,
                E_SLIPPAGE
            );
        };
        
        pool.reserve_a = pool.reserve_a + amount_a;
        pool.reserve_b = pool.reserve_b + amount_b;
    }

    /// SECURE: Verify k maintained after swap
    public entry fun swap_a_for_b(
        pool: &mut Pool,
        amount_a_in: u64,
        min_b_out: u64,
    ): u64 {
        let k_before = get_k(pool);
        
        let new_reserve_a = pool.reserve_a + amount_a_in;
        
        // Calculate output using u128 for precision
        let new_reserve_b = (k_before / (new_reserve_a as u128)) as u64;
        let amount_b_out = pool.reserve_b - new_reserve_b;
        
        // Slippage check
        assert!(amount_b_out >= min_b_out, E_SLIPPAGE);
        
        // Update reserves
        pool.reserve_a = new_reserve_a;
        pool.reserve_b = new_reserve_b;
        
        // CRITICAL: Verify k invariant (with tolerance for rounding)
        let k_after = get_k(pool);
        assert!(k_after >= k_before, E_K_VIOLATED);
        
        amount_b_out
    }
}
```

## Logic Error Prevention Patterns

### Pattern 1: Check-Effects-Interactions

```move
public entry fun secure_operation(state: &mut State, input: u64) {
    // 1. CHECKS - Validate all preconditions
    assert!(input > 0, E_ZERO_INPUT);
    assert!(state.balance >= input, E_INSUFFICIENT);
    
    // 2. EFFECTS - Update state
    state.balance = state.balance - input;
    state.processed = state.processed + 1;
    
    // 3. INTERACTIONS - External calls last
    emit_event(...);
}
```

### Pattern 2: Invariant Assertions

```move
/// Always assert invariants at function end
public entry fun modify_state(state: &mut State, ...) {
    // ... make changes
    
    // Assert invariants before returning
    assert_invariants(state);
}

fun assert_invariants(state: &State) {
    assert!(state.total == state.a + state.b + state.c, E_TOTAL_MISMATCH);
    assert!(state.balance >= state.minimum_required, E_UNDERCOLLATERALIZED);
}
```

### Pattern 3: Use Receipts for Multi-Step Operations

```move
/// Hot potato pattern for operations that must complete
public struct OperationReceipt {
    expected_outcome: u64,
}

public fun start_operation(state: &mut State, amount: u64): OperationReceipt {
    state.locked = state.locked + amount;
    OperationReceipt { expected_outcome: calculate_expected(amount) }
}

public fun finish_operation(state: &mut State, receipt: OperationReceipt, actual: u64) {
    let OperationReceipt { expected_outcome } = receipt;
    assert!(actual >= expected_outcome, E_UNEXPECTED_OUTCOME);
    // Receipt consumed — operation must complete
}
```

## Testing Checklist

- [ ] Test all functions with zero values
- [ ] Test with maximum (u64::MAX) values
- [ ] Verify interest/fee calculations across time boundaries
- [ ] Test invariants hold after every state-changing operation
- [ ] Test PTB with reordered calls
- [ ] Verify precision in all arithmetic with small and large values

## Related Vulnerabilities

- [PTB Ordering Issues](../ptb-ordering-issues/)
- [Numeric / Bitwise Pitfalls](../numeric-bitwise-pitfalls/)
- [Event State Inconsistency](../event-state-inconsistency/)
