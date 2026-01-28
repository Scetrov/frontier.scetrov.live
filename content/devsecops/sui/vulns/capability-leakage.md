+++
title = '11. Capability Leakage'
date = '2025-11-26T00:00:00Z'
weight = 11
+++

## Overview

Capability leakage occurs when authority-granting objects (capabilities) are unintentionally exposed through return values, public functions, or parent struct access. Once a capability leaks, unauthorized parties can perform privileged operations.

## Risk Level

**Critical** — Direct path to unauthorized privileged access.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-668 (Exposure of Resource to Wrong Sphere) |

## The Problem

### How Capabilities Leak

1. **Returning capabilities by value** — Functions that return capability objects
2. **Parent struct exposure** — Returning structs containing capability children
3. **Public field access** — Capabilities stored in accessible fields
4. **Dynamic field exposure** — Capabilities stored as retrievable dynamic fields

## Vulnerable Example

```move
module vulnerable::protocol {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::dynamic_field as df;

    public struct AdminCap has key, store {
        id: UID,
    }

    public struct ProtocolState has key {
        id: UID,
        admin_cap: AdminCap,  // Capability embedded in state!
    }

    public struct CapWrapper has key, store {
        id: UID,
        cap: AdminCap,
    }

    /// VULNERABLE: Returns parent containing capability
    public fun get_state(state: &mut ProtocolState): ProtocolState {
        // Caller now has access to admin_cap!
        *state
    }

    /// VULNERABLE: Exposes capability through wrapper
    public fun get_wrapper(state: &ProtocolState): &CapWrapper {
        // If wrapper is extractable, cap is leaked
        &state.wrapper
    }

    /// VULNERABLE: Creates accessor that leaks authority
    public fun borrow_admin_cap(state: &ProtocolState): &AdminCap {
        // Even a reference can be used to call admin functions!
        &state.admin_cap
    }

    /// VULNERABLE: Dynamic field stores capability
    public fun store_cap_in_field(
        parent: &mut UID,
        cap: AdminCap,
    ) {
        df::add(parent, b"admin", cap);
    }

    /// Anyone who knows the key can retrieve it
    public fun get_cap_from_field(parent: &mut UID): &AdminCap {
        df::borrow(parent, b"admin")
    }
}

module vulnerable::treasury {
    use vulnerable::protocol::AdminCap;

    /// VULNERABLE: Accepts capability reference
    /// Anyone who leaked the reference can call this
    public entry fun drain_treasury(
        _cap: &AdminCap,
        treasury: &mut Treasury,
        ctx: &mut TxContext
    ) {
        // No additional checks — trusting the capability
        let all_funds = treasury.balance;
        treasury.balance = 0;
        // ... transfer funds
    }
}
```

### Attack Scenario

```move
module attack::exploit {
    use vulnerable::protocol;

    public entry fun steal_admin(
        state: &vulnerable::protocol::ProtocolState,
        treasury: &mut Treasury,
        ctx: &mut TxContext
    ) {
        // Leak the capability reference
        let cap_ref = protocol::borrow_admin_cap(state);
        
        // Use leaked capability to drain treasury
        vulnerable::treasury::drain_treasury(cap_ref, treasury, ctx);
    }
}
```

## Secure Example

```move
module secure::protocol {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    /// Capability with no `store` — cannot be wrapped or transferred
    public struct AdminCap has key {
        id: UID,
        protocol_id: ID,
        authorized_address: address,
    }

    /// State does NOT contain capability
    public struct ProtocolState has key {
        id: UID,
        admin_cap_id: ID,  // Only stores the ID, not the cap itself
        treasury_balance: u64,
    }

    fun init(ctx: &mut TxContext) {
        let state = ProtocolState {
            id: object::new(ctx),
            admin_cap_id: object::id_from_address(@0x0),  // Placeholder
            treasury_balance: 0,
        };
        
        let state_id = object::id(&state);
        
        let cap = AdminCap {
            id: object::new(ctx),
            protocol_id: state_id,
            authorized_address: tx_context::sender(ctx),
        };
        
        // Update state with cap ID
        state.admin_cap_id = object::id(&cap);
        
        transfer::share_object(state);
        transfer::transfer(cap, tx_context::sender(ctx));
    }

    /// SECURE: No capability return — action performed internally
    public entry fun admin_withdraw(
        cap: &AdminCap,
        state: &mut ProtocolState,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // Verify cap matches this protocol
        assert!(cap.protocol_id == object::id(state), E_WRONG_PROTOCOL);
        
        // Verify caller is authorized holder
        assert!(tx_context::sender(ctx) == cap.authorized_address, E_NOT_AUTHORIZED);
        
        // Perform action directly — no capability exposure
        assert!(state.treasury_balance >= amount, E_INSUFFICIENT);
        state.treasury_balance = state.treasury_balance - amount;
        
        // ... transfer funds
    }

    /// SECURE: View function returns data, not capability
    public fun get_admin_cap_id(state: &ProtocolState): ID {
        state.admin_cap_id
    }

    /// SECURE: Check authorization without exposing capability
    public fun is_admin(cap: &AdminCap, state: &ProtocolState): bool {
        cap.protocol_id == object::id(state)
    }
}
```

## Capability Protection Patterns

### Pattern 1: Action Functions Instead of Capability Exposure

```move
/// BAD: Exposes capability
public fun get_admin_cap(state: &State): &AdminCap {
    &state.admin_cap
}

/// GOOD: Performs action with internal capability
public entry fun perform_admin_action(
    cap: &AdminCap,
    state: &mut State,
    action_params: ActionParams,
) {
    verify_cap(cap, state);
    // Perform action internally
}
```

### Pattern 2: Separate Capability Storage

```move
/// Capabilities stored separately, not in protocol state
public struct CapabilityRegistry has key {
    id: UID,
    // Only IDs, not actual capabilities
    admin_cap_ids: vector<ID>,
}

/// Capabilities owned by users, not stored centrally
public struct AdminCap has key {
    id: UID,
    registry_id: ID,
}
```

### Pattern 3: Witness Pattern for One-Time Auth

```move
/// Witness can only be created once (in init)
public struct PROTOCOL has drop {}

/// Auth checked via witness possession
public fun authorized_action<T: drop>(
    _witness: T,
    state: &mut State,
) {
    // Only code with the witness type can call
}
```

### Pattern 4: Hot Potato for Scoped Authority

```move
/// Hot potato — must be consumed in same transaction
public struct AdminSession {
    state_id: ID,
    action_count: u64,
    max_actions: u64,
}

public fun start_admin_session(
    cap: &AdminCap,
    state: &State,
): AdminSession {
    verify_cap(cap, state);
    AdminSession {
        state_id: object::id(state),
        action_count: 0,
        max_actions: 10,
    }
}

public fun admin_action(
    session: &mut AdminSession,
    state: &mut State,
) {
    assert!(session.state_id == object::id(state), E_WRONG_STATE);
    assert!(session.action_count < session.max_actions, E_MAX_ACTIONS);
    session.action_count = session.action_count + 1;
    // Perform action
}

public fun end_admin_session(session: AdminSession) {
    let AdminSession { state_id: _, action_count: _, max_actions: _ } = session;
    // Session consumed
}
```

## Recommended Mitigations

### 1. Never Return Capabilities

```move
// BAD
public fun get_cap(): AdminCap { ... }
public fun borrow_cap(): &AdminCap { ... }

// GOOD
public entry fun use_cap_for_action(cap: &AdminCap, ...) { ... }
```

### 2. Remove `store` from Capabilities

```move
/// Without `store`, cap cannot be wrapped or dynamically stored
public struct AdminCap has key {
    id: UID,
}
```

### 3. Tie Capabilities to Specific Resources

```move
public struct VaultAdminCap has key {
    id: UID,
    vault_id: ID,  // Only valid for this specific vault
}
```

### 4. Use Capability References, Not Values

```move
/// Functions should borrow capabilities, not consume them
public entry fun action(cap: &AdminCap, ...) { }  // Borrow

/// Only transfer functions should consume
public entry fun transfer_admin(cap: AdminCap, new_admin: address) { }
```

## Testing Checklist

- [ ] Verify no functions return capability objects
- [ ] Confirm no functions return structs containing capabilities
- [ ] Check that capabilities lack `store` ability
- [ ] Verify capabilities are not stored in dynamic fields accessibly
- [ ] Test that leaked references cannot bypass access control
- [ ] Audit all places where capability references are passed

## Related Vulnerabilities

- [Object Transfer Misuse](../object-transfer-misuse/)
- [Ability Misconfiguration](../ability-misconfiguration/)
- [Access-Control Mistakes](../access-control-mistakes/)
