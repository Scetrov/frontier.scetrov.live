+++
title = '3. Numeric / Bitwise Pitfalls'
date = '2025-11-26T00:00:00Z'
weight = 3
+++

## Overview

Move's numeric and bitwise operations have specific semantics that differ from other languages. Arithmetic operations **abort on overflow/underflow** (rather than wrapping), while bitwise shifts beyond the type width **silently produce zero**. These behaviors can lead to unexpected results and security vulnerabilities.

## Risk Level

**Medium to High** — Can cause denial of service or bypass access control checks.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A06 (Vulnerable Components), A03 (Injection) | CWE-681 (Incorrect Conversion), CWE-190 (Integer Overflow) |

## The Problem

### Overflow/Underflow Behavior

Move aborts on overflow rather than wrapping:

```move
let x: u64 = 18446744073709551615; // MAX_U64
let y = x + 1; // ABORTS! Not wrapping to 0
```

This is generally safer than wrapping, but can be exploited for DoS attacks.

### Bitwise Shift Behavior

Shifts beyond type width silently produce zero:

```move
let x: u64 = 1;
let y = x << 64; // Returns 0, not an error!
let z = x << 100; // Also returns 0
```

This can bypass role/permission checks that use bitmasks.

## Vulnerable Example

```move
module vulnerable::roles {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    const E_NOT_AUTHORIZED: u64 = 1;

    public struct RoleManager has key {
        id: UID,
        /// Bitmask of roles: bit 0 = admin, bit 1 = operator, etc.
        user_roles: vector<u64>,  // indexed by user_id
    }

    /// VULNERABLE: No validation of role_index
    public fun has_role(
        manager: &RoleManager,
        user_id: u64,
        role_index: u64
    ): bool {
        let roles = *vector::borrow(&manager.user_roles, user_id);
        
        // VULNERABLE: If role_index >= 64, this returns 0!
        // Attacker can bypass role check by passing role_index = 64
        let bit = 1u64 << role_index;
        
        (roles & bit) != 0
    }

    /// VULNERABLE: Attacker can set arbitrary roles
    public entry fun grant_role(
        manager: &mut RoleManager,
        user_id: u64,
        role_index: u64,
        ctx: &mut TxContext
    ) {
        // If role_index >= 64, bit = 0, and roles unchanged
        // But function appears to succeed!
        let bit = 1u64 << role_index;
        let roles = vector::borrow_mut(&mut manager.user_roles, user_id);
        *roles = *roles | bit;
    }
}

module vulnerable::fees {
    const MAX_FEE_BPS: u64 = 10000; // 100%

    public struct FeeConfig has key {
        id: UID,
        fee_bps: u64,
    }

    /// VULNERABLE: Can cause DoS via overflow abort
    public fun calculate_fee(config: &FeeConfig, amount: u64): u64 {
        // If amount * fee_bps overflows, transaction aborts
        // Attacker can prevent any transaction with large amounts
        (amount * config.fee_bps) / MAX_FEE_BPS
    }

    /// VULNERABLE: Underflow abort as DoS vector
    public fun withdraw(balance: &mut u64, amount: u64) {
        // Attacker can cause abort by requesting more than balance
        *balance = *balance - amount;  // Aborts if amount > balance
    }
}
```

### Attack Scenarios

**Shift-based bypass:**
```move
// Attacker calls:
let can_admin = has_role(manager, my_id, 64);
// Returns false (bit = 0), but the check is meaningless
// Attacker found a way to make role_index bypass validation
```

**Overflow DoS:**
```move
// Attacker creates scenario where amount * fee_bps overflows
// All fee calculations abort, protocol becomes unusable
let fee = calculate_fee(config, 18446744073709551615);  // Aborts!
```

## Secure Example

```move
module secure::roles {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    const E_INVALID_ROLE_INDEX: u64 = 1;
    const E_NOT_AUTHORIZED: u64 = 2;
    const MAX_ROLE_INDEX: u64 = 63;  // Maximum valid bit position for u64

    public struct RoleManager has key {
        id: UID,
        user_roles: vector<u64>,
    }

    /// SECURE: Validate shift amount before use
    public fun has_role(
        manager: &RoleManager,
        user_id: u64,
        role_index: u64
    ): bool {
        // Validate role_index is within valid range
        assert!(role_index <= MAX_ROLE_INDEX, E_INVALID_ROLE_INDEX);
        
        let roles = *vector::borrow(&manager.user_roles, user_id);
        let bit = 1u64 << role_index;
        
        (roles & bit) != 0
    }

    /// SECURE: Use enumerated roles instead of arbitrary indices
    public fun has_admin_role(manager: &RoleManager, user_id: u64): bool {
        has_role(manager, user_id, 0)  // Admin is always bit 0
    }

    public fun has_operator_role(manager: &RoleManager, user_id: u64): bool {
        has_role(manager, user_id, 1)  // Operator is always bit 1
    }
}

module secure::fees {
    const MAX_FEE_BPS: u64 = 10000;
    const E_OVERFLOW: u64 = 1;
    const E_INSUFFICIENT_BALANCE: u64 = 2;

    public struct FeeConfig has key {
        id: UID,
        fee_bps: u64,
    }

    /// SECURE: Check for overflow before arithmetic
    public fun calculate_fee(config: &FeeConfig, amount: u64): u64 {
        // Use u128 for intermediate calculation to prevent overflow
        let amount_128 = (amount as u128);
        let fee_bps_128 = (config.fee_bps as u128);
        let max_fee_bps_128 = (MAX_FEE_BPS as u128);
        
        let result_128 = (amount_128 * fee_bps_128) / max_fee_bps_128;
        
        // Safe to downcast since result <= amount
        (result_128 as u64)
    }

    /// Alternative: Use checked arithmetic with explicit handling
    public fun calculate_fee_checked(
        config: &FeeConfig, 
        amount: u64
    ): Option<u64> {
        // Check if multiplication would overflow
        if (amount > 0 && config.fee_bps > 18446744073709551615 / amount) {
            return option::none()
        };
        
        option::some((amount * config.fee_bps) / MAX_FEE_BPS)
    }

    /// SECURE: Explicit underflow check with meaningful error
    public fun withdraw(balance: &mut u64, amount: u64) {
        assert!(*balance >= amount, E_INSUFFICIENT_BALANCE);
        *balance = *balance - amount;
    }
}
```

## Recommended Mitigations

### 1. Validate Shift Amounts

```move
const MAX_SHIFT: u8 = 63;

public fun safe_shift_left(value: u64, shift: u8): u64 {
    assert!(shift <= MAX_SHIFT, E_INVALID_SHIFT);
    value << (shift as u64)
}
```

### 2. Use Wider Types for Intermediate Calculations

```move
public fun safe_multiply_divide(a: u64, b: u64, divisor: u64): u64 {
    let a_128 = (a as u128);
    let b_128 = (b as u128);
    let divisor_128 = (divisor as u128);
    
    ((a_128 * b_128) / divisor_128 as u64)
}
```

### 3. Avoid Bitwise Logic for Access Control

```move
/// Instead of bitmasks, use explicit role structs
public struct Roles has store, drop {
    is_admin: bool,
    is_operator: bool,
    is_minter: bool,
}
```

### 4. Use Checked Arithmetic Helpers

```move
/// Returns None on overflow
public fun checked_add(a: u64, b: u64): Option<u64> {
    if (a > 18446744073709551615 - b) {
        option::none()
    } else {
        option::some(a + b)
    }
}

/// Returns None on underflow
public fun checked_sub(a: u64, b: u64): Option<u64> {
    if (a < b) {
        option::none()
    } else {
        option::some(a - b)
    }
}
```

## Testing Checklist

- [ ] Test all shift operations with edge values (0, 63, 64, 255)
- [ ] Test arithmetic operations with MAX values for overflow
- [ ] Test subtraction operations with edge cases for underflow
- [ ] Verify bitmask operations have proper bounds checking
- [ ] Test fee calculations with maximum possible amounts

## Related Vulnerabilities

- [Access-Control Mistakes](../access-control-mistakes/)
- [General Move Logic Errors](../general-move-logic-errors/)
- [Unvalidated Struct Fields](../unvalidated-struct-fields/)
