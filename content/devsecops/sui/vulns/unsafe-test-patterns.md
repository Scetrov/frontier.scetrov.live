+++
title = '30. Unsafe Test Patterns'
date = '2025-11-26T21:44:34Z'
weight = 30
+++

## Overview

Unsafe test patterns occur when test-only code, debug functionality, or development shortcuts accidentally make it into production smart contracts. In Sui Move, the `#[test_only]` attribute should isolate test code, but improper patterns can leak test utilities, create backdoors, or leave vulnerabilities that only manifest in production environments.

## Risk Level

**High** — Can create backdoors, bypass security controls, or cause unexpected production behavior.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A04 (Insecure Design) | CWE-704 (Incorrect Type Conversion or Cast), CWE-665 (Improper Initialization) |

## The Problem

### Common Unsafe Test Patterns

| Issue | Risk | Description |
|-------|------|-------------|
| Test functions without `#[test_only]` | Critical | Test code callable in production |
| `test_scenario` in production | Critical | Fake context manipulation |
| Debug mint functions | Critical | Unlimited token creation |
| Hardcoded test addresses | High | Known addresses exploitable |
| Disabled security checks | High | Guards removed for testing |
| Mock oracles in production | Critical | Fake price data accepted |

## Vulnerable Example

```move
module vulnerable::token {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin, TreasuryCap};

    /// VULNERABLE: No #[test_only] - callable in production!
    public fun mint_for_testing(
        cap: &mut TreasuryCap<TOKEN>,
        amount: u64,
        ctx: &mut TxContext
    ): Coin<TOKEN> {
        // Anyone who has the cap can mint unlimited tokens
        // This was meant for tests only!
        coin::mint(cap, amount, ctx)
    }

    /// VULNERABLE: Debug function left in production
    public entry fun debug_set_balance(
        vault: &mut Vault,
        new_balance: u64,
        _ctx: &mut TxContext
    ) {
        // No access control - was "temporary" for debugging
        vault.balance = new_balance;
    }

    /// VULNERABLE: Test bypass flag
    public entry fun transfer_tokens(
        vault: &mut Vault,
        amount: u64,
        recipient: address,
        skip_checks: bool,  // "For testing" - but callable by anyone!
        ctx: &mut TxContext
    ) {
        if (!skip_checks) {
            assert!(vault.owner == tx_context::sender(ctx), E_NOT_OWNER);
            assert!(amount <= vault.balance, E_INSUFFICIENT);
        };
        
        // Transfer proceeds even without checks if skip_checks = true
        vault.balance = vault.balance - amount;
        // ...
    }
}

module vulnerable::oracle {
    /// VULNERABLE: Test oracle mode in production
    public struct Oracle has key {
        id: UID,
        price: u64,
        /// VULNERABLE: Allows anyone to set price in "test mode"
        test_mode: bool,
    }

    public entry fun set_price(
        oracle: &mut Oracle,
        new_price: u64,
        _ctx: &mut TxContext
    ) {
        if (oracle.test_mode) {
            // No signature verification in test mode!
            oracle.price = new_price;
        } else {
            // Normal verification...
        };
    }

    /// VULNERABLE: Anyone can enable test mode
    public entry fun enable_test_mode(
        oracle: &mut Oracle,
        _ctx: &mut TxContext
    ) {
        oracle.test_mode = true;
    }
}

module vulnerable::admin {
    /// VULNERABLE: Hardcoded test admin address
    const TEST_ADMIN: address = @0x1234;

    public entry fun admin_action(
        state: &mut State,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        // VULNERABLE: Test admin works in production!
        if (sender == TEST_ADMIN || sender == state.admin) {
            // Perform admin action
        };
    }
}

module vulnerable::escrow {
    /// VULNERABLE: Emergency bypass without proper guards
    const EMERGENCY_WITHDRAW_ENABLED: bool = true;  // Forgot to disable!

    public entry fun emergency_withdraw(
        escrow: &mut Escrow,
        ctx: &mut TxContext
    ) {
        // VULNERABLE: This was for testing emergencies
        if (EMERGENCY_WITHDRAW_ENABLED) {
            // Anyone can withdraw everything!
            let all_funds = withdraw_all(escrow, ctx);
            transfer::public_transfer(all_funds, tx_context::sender(ctx));
        };
    }
}

// VULNERABLE: Test helper module without #[test_only]
module vulnerable::test_helpers {
    use sui::tx_context::TxContext;

    /// Should be test_only but isn't!
    public fun create_fake_admin_cap(ctx: &mut TxContext): AdminCap {
        AdminCap { id: object::new(ctx) }
    }

    /// Should be test_only but isn't!
    public fun set_timestamp(clock: &mut Clock, new_time: u64) {
        clock.timestamp_ms = new_time;
    }
}
```

### Attack Scenario

```move
module attack::exploit_test_code {
    use vulnerable::token;
    use vulnerable::oracle;
    use vulnerable::test_helpers;

    /// Attacker uses "test" functions in production
    public entry fun exploit(
        oracle: &mut Oracle,
        treasury_cap: &mut TreasuryCap<TOKEN>,
        ctx: &mut TxContext
    ) {
        // Step 1: Enable test mode on oracle
        oracle::enable_test_mode(oracle);
        
        // Step 2: Set price to manipulate protocol
        oracle::set_price(oracle, 1, ctx);  // Crash the price
        
        // Step 3: Mint unlimited tokens
        let free_money = token::mint_for_testing(treasury_cap, 1000000000, ctx);
        
        // Step 4: Create fake admin cap
        let fake_admin = test_helpers::create_fake_admin_cap(ctx);
        
        // Complete protocol takeover!
    }
}
```

## Secure Example

```move
module secure::token {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin, TreasuryCap};

    /// SECURE: Test function properly annotated
    #[test_only]
    public fun mint_for_testing(
        cap: &mut TreasuryCap<TOKEN>,
        amount: u64,
        ctx: &mut TxContext
    ): Coin<TOKEN> {
        coin::mint(cap, amount, ctx)
    }

    /// SECURE: No debug functions in production code
    // debug_set_balance doesn't exist at all

    /// SECURE: No bypass flags
    public entry fun transfer_tokens(
        vault: &mut Vault,
        amount: u64,
        recipient: address,
        ctx: &mut TxContext
    ) {
        // Always enforce security checks
        assert!(vault.owner == tx_context::sender(ctx), E_NOT_OWNER);
        assert!(amount <= vault.balance, E_INSUFFICIENT);
        
        vault.balance = vault.balance - amount;
        // Transfer...
    }
}

module secure::oracle {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::ed25519;

    /// SECURE: No test mode in production struct
    public struct Oracle has key {
        id: UID,
        price: u64,
        last_update: u64,
        trusted_pubkey: vector<u8>,
    }

    /// SECURE: Always requires signature verification
    public entry fun set_price(
        oracle: &mut Oracle,
        new_price: u64,
        timestamp: u64,
        signature: vector<u8>,
        _ctx: &mut TxContext
    ) {
        // Always verify signature - no test mode bypass
        let message = create_price_message(new_price, timestamp);
        let valid = ed25519::ed25519_verify(
            &signature,
            &oracle.trusted_pubkey,
            &message
        );
        assert!(valid, E_INVALID_SIGNATURE);
        
        oracle.price = new_price;
        oracle.last_update = timestamp;
    }

    /// SECURE: Test-only mock oracle
    #[test_only]
    public fun create_test_oracle(price: u64, ctx: &mut TxContext): Oracle {
        Oracle {
            id: object::new(ctx),
            price,
            last_update: 0,
            trusted_pubkey: vector::empty(),  // Not used in tests
        }
    }

    #[test_only]
    public fun set_price_for_testing(oracle: &mut Oracle, new_price: u64) {
        oracle.price = new_price;
    }
}

module secure::admin {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};

    /// SECURE: No hardcoded addresses
    public struct AdminCap has key {
        id: UID,
        state_id: ID,
    }

    /// SECURE: Capability-based access control
    public entry fun admin_action(
        cap: &AdminCap,
        state: &mut State,
        _ctx: &mut TxContext
    ) {
        assert!(cap.state_id == object::id(state), E_WRONG_STATE);
        // Perform admin action
    }

    /// SECURE: Test admin cap creation is test-only
    #[test_only]
    public fun create_admin_cap_for_testing(
        state: &State,
        ctx: &mut TxContext
    ): AdminCap {
        AdminCap {
            id: object::new(ctx),
            state_id: object::id(state),
        }
    }
}

module secure::escrow {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::clock::{Self, Clock};

    const EMERGENCY_DELAY_MS: u64 = 86400000;  // 24 hours

    /// SECURE: Emergency withdraw with proper controls
    public struct Escrow has key {
        id: UID,
        owner: address,
        balance: u64,
        emergency_requested_at: Option<u64>,
    }

    /// SECURE: Emergency requires time delay and ownership
    public entry fun request_emergency_withdraw(
        escrow: &mut Escrow,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        assert!(tx_context::sender(ctx) == escrow.owner, E_NOT_OWNER);
        escrow.emergency_requested_at = option::some(clock::timestamp_ms(clock));
    }

    public entry fun execute_emergency_withdraw(
        escrow: &mut Escrow,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        assert!(tx_context::sender(ctx) == escrow.owner, E_NOT_OWNER);
        assert!(option::is_some(&escrow.emergency_requested_at), E_NOT_REQUESTED);
        
        let requested_at = *option::borrow(&escrow.emergency_requested_at);
        let now = clock::timestamp_ms(clock);
        
        // SECURE: Must wait 24 hours
        assert!(now >= requested_at + EMERGENCY_DELAY_MS, E_TOO_EARLY);
        
        // Proceed with withdrawal
        escrow.emergency_requested_at = option::none();
        // ...
    }
}

/// SECURE: Test helpers are properly isolated
#[test_only]
module secure::test_helpers {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::test_scenario;

    public fun setup_test_env(sender: address): test_scenario::Scenario {
        test_scenario::begin(sender)
    }

    public fun create_test_clock(timestamp: u64, ctx: &mut TxContext): Clock {
        // Only available in tests
        Clock {
            id: object::new(ctx),
            timestamp_ms: timestamp,
        }
    }
}
```

## Test Pattern Guidelines

### Pattern 1: Proper Test Annotation

```move
/// Production code - always present
public fun calculate_fee(amount: u64): u64 {
    (amount * FEE_BPS) / 10000
}

/// Test code - only compiled in tests
#[test_only]
public fun calculate_fee_for_testing(amount: u64, custom_bps: u64): u64 {
    (amount * custom_bps) / 10000
}

#[test]
fun test_fee_calculation() {
    assert!(calculate_fee(1000) == 30, 0);  // 0.3% fee
}
```

### Pattern 2: Test-Only Module

```move
/// Production module
module myprotocol::core {
    public struct State has key {
        id: UID,
        value: u64,
    }

    public fun get_value(state: &State): u64 {
        state.value
    }

    // No test utilities here
}

/// Completely separate test module
#[test_only]
module myprotocol::core_tests {
    use myprotocol::core::{Self, State};
    use sui::test_scenario;

    fun create_test_state(ctx: &mut TxContext): State {
        // Test-only state creation
    }

    #[test]
    fun test_get_value() {
        // Test implementation
    }
}
```

### Pattern 3: Feature Flags (Compile-Time)

```move
/// Use Move.toml for environment-specific builds
/// NOT runtime flags that can be toggled

// In Move.toml:
// [package]
// name = "MyProtocol"
// 
// [dev-addresses]
// myprotocol = "0x0"
//
// [addresses]  
// myprotocol = "0xPRODUCTION_ADDRESS"

/// Code uses compile-time address
module myprotocol::config {
    // Address is set at compile time, not runtime
    const ADMIN: address = @myprotocol;
}
```

### Pattern 4: Separate Test Scenarios

```move
#[test_only]
module myprotocol::integration_tests {
    use sui::test_scenario::{Self, Scenario};
    use sui::test_utils;

    const ALICE: address = @0xA;
    const BOB: address = @0xB;

    fun setup(): Scenario {
        let mut scenario = test_scenario::begin(ALICE);
        // Setup test environment
        scenario
    }

    #[test]
    fun test_full_flow() {
        let mut scenario = setup();
        
        // Test as Alice
        test_scenario::next_tx(&mut scenario, ALICE);
        {
            // Alice's actions
        };
        
        // Test as Bob
        test_scenario::next_tx(&mut scenario, BOB);
        {
            // Bob's actions
        };
        
        test_scenario::end(scenario);
    }
}
```

## Pre-Deployment Checklist

### Code Review Items

```markdown
1. [ ] Search for "test" in function names - all should be #[test_only]
2. [ ] Search for "debug" in function names - should not exist
3. [ ] Search for "mock" - should be #[test_only]
4. [ ] Search for "skip" or "bypass" parameters - should not exist
5. [ ] Search for hardcoded addresses - should use capabilities
6. [ ] Search for boolean flags that disable security - remove them
7. [ ] Verify no `test_scenario` usage outside #[test_only]
8. [ ] Check for "TODO" or "FIXME" comments about security
```

### Automated Checks

```bash
# Find potential test code in production
grep -r "for_testing\|_test\|debug_\|mock_" src/ --include="*.move" | \
  grep -v "#\[test_only\]" | \
  grep -v "#\[test\]"

# Find bypass flags
grep -r "skip_check\|bypass\|test_mode\|debug_mode" src/ --include="*.move"

# Find hardcoded addresses (excluding @0x0, @0x1, @0x2 system addresses)
grep -r "@0x[3-9a-fA-F]" src/ --include="*.move"
```

## Recommended Mitigations

### 1. Always Use #[test_only]

```move
#[test_only]
public fun any_test_helper(...) { }

#[test_only]
module mypackage::test_utils { }
```

### 2. No Runtime Test Flags

```move
// BAD: Runtime flag
public struct Config {
    test_mode: bool,
}

// GOOD: No test mode in production structs
public struct Config {
    // Only production fields
}
```

### 3. Capability-Based Access, Not Addresses

```move
// BAD: Hardcoded address
if (sender == @0x1234) { }

// GOOD: Capability check
public fun admin_action(cap: &AdminCap) { }
```

### 4. Separate Test Modules

```move
// Production code in src/
module myprotocol::core { }

// Test code with #[test_only]
#[test_only]
module myprotocol::core_tests { }
```

### 5. Pre-Deployment Audit

```move
// Before mainnet:
// 1. Remove all #[test_only] modules from build
// 2. Verify no test patterns in production code
// 3. Check for debug/mock functions
// 4. Review all public functions
```

## Testing Checklist

- [ ] All test functions have `#[test_only]` attribute
- [ ] No `test_scenario` usage in production code
- [ ] No debug/mock functions without `#[test_only]`
- [ ] No hardcoded test addresses
- [ ] No runtime "test mode" or "skip checks" flags
- [ ] No emergency bypasses without proper controls
- [ ] Automated grep checks pass
- [ ] Code review specifically for test patterns

## Related Vulnerabilities

- [Weak Initializers](../weak-initializers/)
- [Access-Control Mistakes](../access-control-mistakes/)
- [Capability Leakage](../capability-leakage/)
- [Ability Misconfiguration](../ability-misconfiguration/)
