+++
title = '5. Access-Control Mistakes'
date = '2025-11-26T00:00:00Z'
weight = 5
+++

## Overview

Access control mistakes occur when authorization checks are missing, incorrectly implemented, or rely on wrong assumptions about `TxContext::sender()`. These vulnerabilities allow unauthorized users to perform privileged operations.

## Risk Level

**Critical** — Direct path to unauthorized access and fund theft.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control) | CWE-285 (Improper Authorization), CWE-639 (Authorization Bypass) |

## The Problem

### Common Access Control Mistakes

1. **Missing authorization checks** — Functions accessible to anyone
2. **Checking wrong sender** — Confusing gas sponsor with transaction sender
3. **Hardcoded addresses** — Addresses that cannot be updated or rotated
4. **Race conditions** — Authorization state changes between check and use
5. **Inconsistent models** — Mixing capability-based and address-based checks

## Vulnerable Example

```move
module vulnerable::vault {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::transfer;

    const ADMIN: address = @0xDEADBEEF;

    public struct Vault has key {
        id: UID,
        funds: Coin<SUI>,
        admin: address,
    }

    public struct AdminCap has key, store {
        id: UID,
    }

    /// VULNERABLE: No access control at all!
    public entry fun withdraw_all(
        vault: &mut Vault,
        ctx: &mut TxContext
    ) {
        let amount = coin::value(&vault.funds);
        let withdrawn = coin::split(&mut vault.funds, amount, ctx);
        transfer::public_transfer(withdrawn, tx_context::sender(ctx));
    }

    /// VULNERABLE: Hardcoded address cannot be updated
    public entry fun emergency_withdraw(
        vault: &mut Vault,
        ctx: &mut TxContext
    ) {
        // What if ADMIN key is compromised? No way to rotate!
        assert!(tx_context::sender(ctx) == ADMIN, E_NOT_ADMIN);
        // ... withdraw logic
    }

    /// VULNERABLE: Checks sender but ignores capability
    public entry fun update_admin(
        vault: &mut Vault,
        _cap: &AdminCap,  // Cap is ignored!
        new_admin: address,
        ctx: &mut TxContext
    ) {
        // This checks sender even though cap is passed
        // If cap was transferred, wrong person might have access
        assert!(tx_context::sender(ctx) == vault.admin, E_NOT_ADMIN);
        vault.admin = new_admin;
    }

    /// VULNERABLE: Time-of-check to time-of-use issue
    public entry fun conditional_withdraw(
        vault: &mut Vault,
        amount: u64,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        // Check is performed...
        assert!(is_authorized(sender), E_NOT_AUTHORIZED);
        
        // ...but in a PTB, authorization might change before this executes
        let withdrawn = coin::split(&mut vault.funds, amount, ctx);
        transfer::public_transfer(withdrawn, sender);
    }
}
```

## Secure Example

```move
module secure::vault {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::transfer;
    use sui::event;

    const E_NOT_ADMIN: u64 = 0;
    const E_ZERO_AMOUNT: u64 = 1;
    const E_INSUFFICIENT_FUNDS: u64 = 2;

    /// SECURE: No `store` — only this module controls the cap
    public struct AdminCap has key {
        id: UID,
        vault_id: ID,  // Tied to specific vault
    }

    public struct Vault has key {
        id: UID,
        funds: Coin<SUI>,
    }

    public struct WithdrawEvent has copy, drop {
        vault_id: ID,
        amount: u64,
        recipient: address,
    }

    fun init(ctx: &mut TxContext) {
        let vault = Vault {
            id: object::new(ctx),
            funds: coin::zero(ctx),
        };
        
        let vault_id = object::id(&vault);
        
        // Create admin cap tied to this vault
        let admin_cap = AdminCap {
            id: object::new(ctx),
            vault_id,
        };
        
        transfer::share_object(vault);
        transfer::transfer(admin_cap, tx_context::sender(ctx));
    }

    /// SECURE: Capability-based access control
    public entry fun withdraw(
        cap: &AdminCap,
        vault: &mut Vault,
        amount: u64,
        recipient: address,
        ctx: &mut TxContext
    ) {
        // Verify cap is for this vault
        assert!(cap.vault_id == object::id(vault), E_NOT_ADMIN);
        assert!(amount > 0, E_ZERO_AMOUNT);
        assert!(coin::value(&vault.funds) >= amount, E_INSUFFICIENT_FUNDS);
        
        let withdrawn = coin::split(&mut vault.funds, amount, ctx);
        
        event::emit(WithdrawEvent {
            vault_id: object::id(vault),
            amount,
            recipient,
        });
        
        transfer::public_transfer(withdrawn, recipient);
    }

    /// SECURE: Explicit admin transfer with cap consumption
    public entry fun transfer_admin(
        cap: AdminCap,
        new_admin: address,
        ctx: &mut TxContext
    ) {
        // Old cap is consumed, new one is created
        let AdminCap { id, vault_id } = cap;
        object::delete(id);
        
        transfer::transfer(
            AdminCap {
                id: object::new(ctx),
                vault_id,
            },
            new_admin
        );
    }

    /// SECURE: Multi-sig pattern for critical operations
    public struct MultiSigProposal has key {
        id: UID,
        action: vector<u8>,
        approvals: vector<address>,
        threshold: u64,
        vault_id: ID,
    }

    public entry fun approve_and_execute(
        proposal: &mut MultiSigProposal,
        cap: &AdminCap,
        ctx: &TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        // Add approval if not already present
        if (!vector::contains(&proposal.approvals, &sender)) {
            vector::push_back(&mut proposal.approvals, sender);
        };
        
        // Execute if threshold reached
        if (vector::length(&proposal.approvals) >= proposal.threshold) {
            // ... execute action
        }
    }
}
```

## Access Control Patterns

### Pattern 1: Pure Capability-Based

```move
/// Best for most cases — clear, composable
public entry fun admin_action(cap: &AdminCap, ...) {
    // Whoever holds the cap can perform the action
    // No sender checks needed
}
```

### Pattern 2: Capability + Sender Verification

```move
/// For soul-bound capabilities
public struct SoulBoundCap has key {
    id: UID,
    owner: address,
}

public entry fun action(cap: &SoulBoundCap, ctx: &TxContext) {
    assert!(tx_context::sender(ctx) == cap.owner, E_NOT_OWNER);
    // Both cap possession AND sender match required
}
```

### Pattern 3: Role-Based Access

```move
public struct RoleRegistry has key {
    id: UID,
    admins: vector<address>,
    operators: vector<address>,
}

public fun is_admin(registry: &RoleRegistry, addr: address): bool {
    vector::contains(&registry.admins, &addr)
}

public entry fun admin_action(
    registry: &RoleRegistry,
    ctx: &TxContext
) {
    assert!(is_admin(registry, tx_context::sender(ctx)), E_NOT_ADMIN);
}
```

### Pattern 4: Time-Locked Operations

```move
public struct TimeLock has key {
    id: UID,
    operation: vector<u8>,
    execute_after: u64,
}

public entry fun execute_timelock(
    lock: TimeLock,
    clock: &Clock,
) {
    assert!(clock::timestamp_ms(clock) >= lock.execute_after, E_TOO_EARLY);
    let TimeLock { id, operation, execute_after: _ } = lock;
    object::delete(id);
    // ... execute operation
}
```

## Recommended Mitigations

### 1. Choose One Authorization Model

```move
// GOOD: Consistent capability-based
public entry fun action1(cap: &AdminCap, ...) { }
public entry fun action2(cap: &AdminCap, ...) { }
public entry fun action3(cap: &AdminCap, ...) { }

// BAD: Mixed models
public entry fun action1(cap: &AdminCap, ...) { }
public entry fun action2(ctx: &TxContext) {  // sender check
    assert!(sender(ctx) == ADMIN, 0);
}
```

### 2. Tie Capabilities to Resources

```move
public struct VaultCap has key {
    id: UID,
    vault_id: ID,  // Can only control this specific vault
}
```

### 3. Implement Emergency Procedures

```move
public struct EmergencyConfig has key {
    id: UID,
    guardians: vector<address>,
    pause_threshold: u64,
}

public entry fun emergency_pause(
    config: &EmergencyConfig,
    signatures: vector<vector<u8>>,
    // ... verify multi-sig
) { }
```

## Testing Checklist

- [ ] Every state-modifying function has explicit access control
- [ ] No hardcoded addresses without upgrade path
- [ ] Capabilities are tied to specific resources where appropriate
- [ ] No mixing of authorization models
- [ ] Emergency procedures exist for key rotation
- [ ] All access control paths are tested with unauthorized callers

## Related Vulnerabilities

- [Object Transfer Misuse](../object-transfer-misuse/)
- [Sponsored Transaction Pitfalls](../sponsored-transaction-pitfalls/)
- [Capability Leakage](../capability-leakage/)
