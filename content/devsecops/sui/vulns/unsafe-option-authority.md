+++
title = '22. Unsafe Option Authority'
date = '2025-11-26T20:48:47Z'
weight = 22
+++

## Overview

Unsafe Option authority occurs when developers use `Option<T>` types to toggle permissions or authority states, creating vulnerabilities where attackers can manipulate authorization by extracting, replacing, or exploiting the optional nature of authority objects. This pattern is particularly dangerous when capabilities or access tokens are wrapped in Option types.

## Risk Level

**High** — Can lead to privilege escalation or unauthorized access.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE |
 | -------------- | ----------- |
 | A04 (Insecure Design) | CWE-696 (Incorrect Behavior Order), CWE-693 (Protection Mechanism Failure) |

## The Problem

### Common Option Authority Issues

 | Issue | Risk | Description |
 | ------- | ------ | ------------- |
 | Mutable Option capability | Critical | Authority can be extracted and replaced |
 | None as "no permission" | High | Missing != denied, logic can be bypassed |
 | Option in shared objects | High | Race conditions on authority state |
 | fill/extract patterns | Medium | Authority can be temporarily removed |

## Vulnerable Example

```move
module vulnerable::vault {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};
    use std::option::{Self, Option};

    const E_NOT_AUTHORIZED: u64 = 1;
    const E_NO_ADMIN: u64 = 2;

    public struct AdminCap has key, store {
        id: UID,
    }

    public struct Vault<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        /// VULNERABLE: Admin stored as Option in shared object
        admin_cap: Option<AdminCap>,
        withdraw_enabled: bool,
    }

    /// VULNERABLE: Admin can be extracted
    public fun extract_admin(vault: &mut Vault<SUI>): AdminCap {
        assert!(option::is_some(&vault.admin_cap), E_NO_ADMIN);
        option::extract(&mut vault.admin_cap)
    }

    /// VULNERABLE: Anyone can fill when empty
    public fun set_admin(vault: &mut Vault<SUI>, cap: AdminCap) {
        // If admin was extracted, anyone can become admin!
        assert!(option::is_none(&vault.admin_cap), E_NOT_AUTHORIZED);
        option::fill(&mut vault.admin_cap, cap);
    }

    /// VULNERABLE: Check passes when Option is None
    public entry fun emergency_withdraw<T>(
        vault: &mut Vault<T>,
        ctx: &mut TxContext
    ) {
        // Attacker extracts admin, making this None
        // Then this check becomes meaningless
        if (option::is_some(&vault.admin_cap)) {
            // Only check if admin exists - but it was extracted!
            let admin = option::borrow(&vault.admin_cap);
            // No actual verification of caller
        };

        // Withdraw proceeds even without proper auth
        let amount = balance::value(&vault.balance);
        let coins = coin::take(&mut vault.balance, amount, ctx);
        transfer::public_transfer(coins, tx_context::sender(ctx));
    }
}

module vulnerable::toggle_auth {
    use sui::object::{Self, UID};
    use std::option::{Self, Option};

    public struct Permission has store, drop {}

    public struct Resource has key {
        id: UID,
        /// VULNERABLE: Permission as toggle
        permission: Option<Permission>,
        data: vector<u8>,
    }

    /// VULNERABLE: Toggle-based auth can be manipulated
    public fun modify_if_permitted(
        resource: &mut Resource,
        new_data: vector<u8>
    ) {
        // Attacker can swap in their own Permission
        if (option::is_some(&resource.permission)) {
            resource.data = new_data;
        }
        // Also: if Permission has `drop`, it can be destroyed
        // leaving permanent "no permission" state
    }

    /// VULNERABLE: Permission can be stolen via swap
    public fun swap_permission(
        resource: &mut Resource,
        new_perm: Permission
    ): Option<Permission> {
        // Returns the old permission to caller!
        let old = option::swap(&mut resource.permission, new_perm);
        option::some(old)
    }
}
```

### Attack Scenario

```move
module attack::option_exploit {
    use vulnerable::vault::{Self, Vault, AdminCap};
    use sui::tx_context::TxContext;

    /// Step 1: Extract admin during legitimate operation
    public fun steal_admin(vault: &mut Vault<SUI>): AdminCap {
        // If we can call extract, we become the admin holder
        vault::extract_admin(vault)
    }

    /// Step 2: Vault now has no admin, emergency_withdraw check fails open
    public entry fun drain_vault(
        vault: &mut Vault<SUI>,
        ctx: &mut TxContext
    ) {
        // Admin check sees None, doesn't properly deny access
        vault::emergency_withdraw(vault, ctx);
    }

    /// Alternative: Front-run admin reinsertion
    public entry fun become_admin(
        vault: &mut Vault<SUI>,
        ctx: &mut TxContext
    ) {
        // Create our own admin cap
        let fake_admin = AdminCap {
            id: object::new(ctx)
        };
        // Race to fill the empty slot
        vault::set_admin(vault, fake_admin);
    }
}
```

## Secure Example

```move
module secure::vault {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};

    const E_NOT_ADMIN: u64 = 1;
    const E_WRONG_VAULT: u64 = 2;

    /// SECURE: Capability is a separate object, not embedded
    public struct AdminCap has key {
        id: UID,
        vault_id: ID,  // Bound to specific vault
    }

    public struct Vault<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        admin: address,  // Store admin address, not capability
        withdraw_enabled: bool,
    }

    fun init(ctx: &mut TxContext) {
        let vault = Vault {
            id: object::new(ctx),
            balance: balance::zero(),
            admin: tx_context::sender(ctx),
            withdraw_enabled: true,
        };

        let vault_id = object::id(&vault);

        let admin_cap = AdminCap {
            id: object::new(ctx),
            vault_id,
        };

        transfer::share_object(vault);
        transfer::transfer(admin_cap, tx_context::sender(ctx));
    }

    /// SECURE: Requires capability proof, not Option check
    public entry fun emergency_withdraw<T>(
        cap: &AdminCap,
        vault: &mut Vault<T>,
        ctx: &mut TxContext
    ) {
        // Verify cap matches vault
        assert!(cap.vault_id == object::id(vault), E_WRONG_VAULT);

        let amount = balance::value(&vault.balance);
        let coins = coin::take(&mut vault.balance, amount, ctx);
        transfer::public_transfer(coins, tx_context::sender(ctx));
    }

    /// SECURE: Transfer admin to new address
    public entry fun transfer_admin(
        cap: AdminCap,
        vault: &mut Vault<SUI>,
        new_admin: address,
        ctx: &mut TxContext
    ) {
        assert!(cap.vault_id == object::id(vault), E_WRONG_VAULT);
        vault.admin = new_admin;
        transfer::transfer(cap, new_admin);
    }
}

module secure::optional_feature {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use std::option::{Self, Option};

    const E_FEATURE_DISABLED: u64 = 1;
    const E_NOT_OWNER: u64 = 2;

    /// SECURE: Feature flag is a simple bool, not authority
    public struct FeatureConfig has key {
        id: UID,
        owner: address,
        premium_enabled: bool,
        max_operations: Option<u64>,  // Optional limit, not authority
    }

    /// SECURE: Authority check is separate from optional config
    public entry fun use_premium_feature(
        config: &FeatureConfig,
        ctx: &TxContext
    ) {
        // First: verify ownership (authority)
        assert!(tx_context::sender(ctx) == config.owner, E_NOT_OWNER);

        // Then: check feature flag (configuration)
        assert!(config.premium_enabled, E_FEATURE_DISABLED);

        // Optional config affects behavior, not authorization
        let limit = if (option::is_some(&config.max_operations)) {
            *option::borrow(&config.max_operations)
        } else {
            1000  // Default limit
        };

        // Proceed with operation...
    }
}
```

## Safe Option Patterns

### Pattern 1: Option for Optional Data, Not Authority

```move
module safe::optional_data {
    use std::option::{Self, Option};

    public struct UserProfile has key {
        id: UID,
        owner: address,           // Authority: non-optional
        name: vector<u8>,         // Required field
        bio: Option<vector<u8>>,  // Optional data - OK
        avatar_url: Option<vector<u8>>,  // Optional data - OK
    }

    /// Safe: Option used for optional data, not permissions
    public fun get_bio(profile: &UserProfile): Option<vector<u8>> {
        profile.bio
    }

    /// Safe: Authority check uses address, not Option
    public fun update_bio(
        profile: &mut UserProfile,
        new_bio: Option<vector<u8>>,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == profile.owner, E_NOT_OWNER);
        profile.bio = new_bio;
    }
}
```

### Pattern 2: Capability References, Never Embedded Options

```move
module safe::capability_pattern {
    use sui::object::{Self, UID, ID};

    public struct AdminCap has key {
        id: UID,
        resource_id: ID,
    }

    public struct ManagedResource has key {
        id: UID,
        // NO Option<AdminCap> here!
        // Admin holds cap separately
        data: vector<u8>,
    }

    /// Capability passed as reference, not extracted from Option
    public fun admin_modify(
        cap: &AdminCap,
        resource: &mut ManagedResource,
        new_data: vector<u8>
    ) {
        assert!(cap.resource_id == object::id(resource), E_WRONG_RESOURCE);
        resource.data = new_data;
    }
}
```

### Pattern 3: Immutable Authority with Optional Delegation

```move
module safe::delegation {
    use sui::object::{Self, UID, ID};
    use std::option::{Self, Option};

    public struct PrimaryAdmin has key {
        id: UID,
        resource_id: ID,
    }

    public struct DelegatedAdmin has key {
        id: UID,
        resource_id: ID,
        delegated_by: ID,
        expires_at: u64,
    }

    public struct Resource has key {
        id: UID,
        primary_admin: address,  // Immutable primary authority
        // Delegation is separate objects, not Options
        data: vector<u8>,
    }

    /// Primary admin always works
    public fun primary_modify(
        cap: &PrimaryAdmin,
        resource: &mut Resource,
        new_data: vector<u8>
    ) {
        assert!(cap.resource_id == object::id(resource), E_WRONG_RESOURCE);
        resource.data = new_data;
    }

    /// Delegated admin requires valid, non-expired delegation
    public fun delegated_modify(
        cap: &DelegatedAdmin,
        resource: &mut Resource,
        new_data: vector<u8>,
        clock: &Clock
    ) {
        assert!(cap.resource_id == object::id(resource), E_WRONG_RESOURCE);
        assert!(clock::timestamp_ms(clock) < cap.expires_at, E_DELEGATION_EXPIRED);
        resource.data = new_data;
    }
}
```

### Pattern 4: Option for Grace Periods, Not Access

```move
module safe::grace_period {
    use std::option::{Self, Option};
    use sui::clock::{Self, Clock};

    public struct Subscription has key {
        id: UID,
        owner: address,
        active: bool,
        expires_at: u64,
        grace_period_end: Option<u64>,  // Optional extension, not authority
    }

    public fun can_access(
        sub: &Subscription,
        clock: &Clock,
        ctx: &TxContext
    ): bool {
        // Authority: must be owner
        if (tx_context::sender(ctx) != sub.owner) {
            return false
        };

        if (!sub.active) {
            return false
        };

        let now = clock::timestamp_ms(clock);

        // Active subscription
        if (now < sub.expires_at) {
            return true
        };

        // Check grace period (optional feature, not authority)
        if (option::is_some(&sub.grace_period_end)) {
            let grace_end = *option::borrow(&sub.grace_period_end);
            return now < grace_end
        };

        false
    }
}
```

## Recommended Mitigations

### 1. Never Store Capabilities in Option

```move
// BAD: Capability in Option can be extracted
public struct Bad has key {
    admin: Option<AdminCap>,
}

// GOOD: Capability is separate object
public struct Good has key {
    admin_address: address,
}
```

### 2. Use Address or ID for Authority Reference

```move
// Store who has authority, not the authority itself
public struct Resource has key {
    id: UID,
    owner: address,
    admin_cap_id: ID,  // Reference, not embedded
}
```

### 3. Require Capability Proof, Not Option Check

```move
// BAD: Check if Option contains value
if (option::is_some(&resource.admin)) { ... }

// GOOD: Require capability as parameter
public fun admin_action(cap: &AdminCap, resource: &mut Resource) {
    assert!(cap.resource_id == object::id(resource), E_WRONG_CAP);
}
```

### 4. Use Option Only for Optional Data

```move
// GOOD: Optional configuration data
public struct Config has key {
    max_limit: Option<u64>,     // Optional setting
    description: Option<String>, // Optional metadata
}
```

## Testing Checklist

- [ ] Verify no capabilities are stored in Option types
- [ ] Test that extracting optional values doesn't bypass auth
- [ ] Confirm authority checks don't rely on Option::is_some
- [ ] Test race conditions on shared objects with Option fields
- [ ] Verify None state doesn't grant unexpected access
- [ ] Check that swap/extract patterns can't steal authority

## Related Vulnerabilities

- [Capability Leakage](../capability-leakage/)
- [Access-Control Mistakes](../access-control-mistakes/)
- [Ability Misconfiguration](../ability-misconfiguration/)
- [Shared Object DoS](../shared-object-dos/)
