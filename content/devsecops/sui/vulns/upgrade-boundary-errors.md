+++
title = '26. Upgrade Boundary Errors'
date = '2025-11-26T21:18:20Z'
weight = 26
+++

## Overview

Upgrade boundary errors occur when package upgrades break compatibility with existing on-chain state, cause ABI mismatches, or violate upgrade policies. Sui Move packages can be upgraded, but upgrades must maintain compatibility with objects created by previous versions. Failing to handle upgrade boundaries correctly can corrupt state, break integrations, or lock funds permanently.

## Risk Level

**Critical** — Can lead to permanent protocol breakage or locked funds.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A04 (Insecure Design) / A06 (Vulnerable and Outdated Components) | CWE-685 (Function Call With Incorrect Number of Arguments), CWE-694 (Use of Multiple Resources with Duplicate Identifier) | 

## The Problem

### Common Upgrade Boundary Issues

 | Issue | Risk | Description | 
 | ------- | ------ | ------------- | 
 | Struct field changes | Critical | Adding/removing/reordering fields breaks existing objects | 
 | Function signature changes | High | Callers using old signatures fail | 
 | Removing public functions | High | Dependent packages break | 
 | Changing type parameters | Critical | Type mismatches on existing objects | 
 | Incompatible upgrade policy | Medium | Upgrades blocked unexpectedly | 

## Sui Upgrade Policies

 | Policy | Description | Restrictions | 
 | -------- | ------------- | -------------- | 
| `compatible` | Default, allows compatible changes | Cannot change struct layouts |
| `additive` | Only additions allowed | No removals or modifications |
| `dep_only` | Dependency updates only | No code changes |
| `immutable` | No upgrades allowed | Package frozen forever |

## Vulnerable Example

```move
// === VERSION 1 (Original Deployment) ===
module vulnerable::token_v1 {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    public struct Token has key, store {
        id: UID,
        value: u64,
        owner: address,
    }

    public fun get_value(token: &Token): u64 {
        token.value
    }

    public fun transfer_value(
        from: &mut Token,
        to: &mut Token,
        amount: u64
    ) {
        from.value = from.value - amount;
        to.value = to.value + amount;
    }
}

// === VERSION 2 (BROKEN UPGRADE) ===
module vulnerable::token_v2 {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    /// VULNERABLE: Added field breaks existing Token objects!
    public struct Token has key, store {
        id: UID,
        value: u64,
        owner: address,
        created_at: u64,  // NEW FIELD - breaks deserialization!
    }

    /// VULNERABLE: Changed function signature
    public fun get_value(token: &Token, _ctx: &TxContext): u64 {
        // Added parameter breaks all callers
        token.value
    }

    /// VULNERABLE: Removed function breaks dependent packages
    // transfer_value is gone!

    /// VULNERABLE: New function with same logic but different name
    public fun send_value(
        from: &mut Token,
        to: &mut Token,
        amount: u64,
        fee: u64,  // Added fee parameter
    ) {
        from.value = from.value - amount - fee;
        to.value = to.value + amount;
    }
}

// === ANOTHER BROKEN PATTERN ===
module vulnerable::registry_v1 {
    public struct Registry has key {
        id: UID,
        entries: vector<Entry>,
    }

    public struct Entry has store {
        name: vector<u8>,
        value: u64,
    }
}

module vulnerable::registry_v2 {
    public struct Registry has key {
        id: UID,
        /// VULNERABLE: Changed from vector to Table
        /// Existing Registry objects can't be read!
        entries: Table<vector<u8>, Entry>,
    }

    /// VULNERABLE: Entry struct layout changed
    public struct Entry has store {
        value: u64,      // Reordered!
        name: vector<u8>,
        active: bool,    // Added field
    }
}
```

### Breaking Scenarios

```move
// Scenario 1: Existing objects become unreadable
public entry fun use_old_token(token: &Token) {
    // After v2 upgrade, Token struct has different layout
    // Old tokens created in v1 can't be deserialized
    // This function will abort!
}

// Scenario 2: Dependent packages break
module other_package::integration {
    use vulnerable::token_v1;  // Compiled against v1

    public fun do_transfer(from: &mut Token, to: &mut Token) {
        // After upgrade, transfer_value doesn't exist
        // This call fails at runtime
        token_v1::transfer_value(from, to, 100);
    }
}

// Scenario 3: Type parameter mismatch
module vulnerable::pool_v1 {
    public struct Pool<phantom T> has key {
        id: UID,
        balance: Balance<T>,
    }
}

module vulnerable::pool_v2 {
    // Changed phantom to non-phantom - incompatible!
    public struct Pool<T: store> has key {
        id: UID,
        balance: Balance<T>,
        fee_rate: u64,
    }
}
```

## Secure Example

```move
// === VERSION 1 (Original - Upgrade-Safe Design) ===
module secure::token_v1 {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::dynamic_field as df;

    const VERSION: u64 = 1;

    /// Core struct - fields are FINAL after deployment
    public struct Token has key, store {
        id: UID,
        value: u64,
        owner: address,
        version: u64,  // Track version for migrations
    }

    /// Use dynamic fields for extensibility
    public fun set_metadata(token: &mut Token, key: vector<u8>, value: vector<u8>) {
        df::add(&mut token.id, key, value);
    }

    public fun get_value(token: &Token): u64 {
        token.value
    }

    /// Keep original function signature forever
    public fun transfer_value(
        from: &mut Token,
        to: &mut Token,
        amount: u64
    ) {
        transfer_value_internal(from, to, amount, 0);
    }

    /// Internal implementation can change
    fun transfer_value_internal(
        from: &mut Token,
        to: &mut Token,
        amount: u64,
        _fee: u64
    ) {
        from.value = from.value - amount;
        to.value = to.value + amount;
    }

    public fun create(value: u64, ctx: &mut TxContext): Token {
        Token {
            id: object::new(ctx),
            value,
            owner: tx_context::sender(ctx),
            version: VERSION,
        }
    }
}

// === VERSION 2 (Safe Upgrade) ===
module secure::token_v2 {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::dynamic_field as df;

    const VERSION: u64 = 2;
    const CREATED_AT_KEY: vector<u8> = b"created_at";

    /// SECURE: Struct layout is IDENTICAL to v1
    public struct Token has key, store {
        id: UID,
        value: u64,
        owner: address,
        version: u64,
    }

    /// SECURE: Original function signature preserved
    public fun get_value(token: &Token): u64 {
        token.value
    }

    /// SECURE: Original function still works
    public fun transfer_value(
        from: &mut Token,
        to: &mut Token,
        amount: u64
    ) {
        // Internally uses new logic with zero fee
        transfer_value_with_fee(from, to, amount, 0);
    }

    /// SECURE: New functionality via new function
    public fun transfer_value_with_fee(
        from: &mut Token,
        to: &mut Token,
        amount: u64,
        fee: u64
    ) {
        from.value = from.value - amount - fee;
        to.value = to.value + amount;
    }

    /// SECURE: New data stored in dynamic fields
    public fun set_created_at(token: &mut Token, timestamp: u64) {
        if (df::exists_(&token.id, CREATED_AT_KEY)) {
            *df::borrow_mut(&mut token.id, CREATED_AT_KEY) = timestamp;
        } else {
            df::add(&mut token.id, CREATED_AT_KEY, timestamp);
        };
    }

    public fun get_created_at(token: &Token): Option<u64> {
        if (df::exists_(&token.id, CREATED_AT_KEY)) {
            option::some(*df::borrow(&token.id, CREATED_AT_KEY))
        } else {
            option::none()
        }
    }

    /// SECURE: Migration function for version updates
    public fun migrate_token(token: &mut Token, clock: &Clock) {
        if (token.version < VERSION) {
            // Perform any necessary migration
            if (!df::exists_(&token.id, CREATED_AT_KEY)) {
                df::add(&mut token.id, CREATED_AT_KEY, clock::timestamp_ms(clock));
            };
            token.version = VERSION;
        };
    }

    /// New tokens get new features automatically
    public fun create(value: u64, clock: &Clock, ctx: &mut TxContext): Token {
        let mut token = Token {
            id: object::new(ctx),
            value,
            owner: tx_context::sender(ctx),
            version: VERSION,
        };
        
        df::add(&mut token.id, CREATED_AT_KEY, clock::timestamp_ms(clock));
        
        token
    }
}
```

## Upgrade-Safe Patterns

### Pattern 1: Version Tracking

```move
const CURRENT_VERSION: u64 = 3;

public struct Protocol has key {
    id: UID,
    version: u64,
    // ... other fields unchanged
}

public fun check_version(protocol: &Protocol) {
    assert!(protocol.version <= CURRENT_VERSION, E_FUTURE_VERSION);
}

public entry fun migrate(protocol: &mut Protocol, ctx: &TxContext) {
    // Only admin can migrate
    assert!(is_admin(ctx), E_NOT_ADMIN);
    
    if (protocol.version == 1) {
        // v1 -> v2 migration logic
        protocol.version = 2;
    };
    
    if (protocol.version == 2) {
        // v2 -> v3 migration logic
        protocol.version = 3;
    };
}
```

### Pattern 2: Dynamic Fields for Extensions

```move
/// Never add fields to this struct after deployment
public struct CoreData has key {
    id: UID,
    essential_field: u64,
}

/// Extension data lives in dynamic fields
public fun add_extension<T: store>(core: &mut CoreData, key: vector<u8>, data: T) {
    df::add(&mut core.id, key, data);
}

public fun get_extension<T: store>(core: &CoreData, key: vector<u8>): &T {
    df::borrow(&core.id, key)
}
```

### Pattern 3: Wrapper Structs for New Versions

```move
// V1 struct - never changes
public struct DataV1 has key, store {
    id: UID,
    value: u64,
}

// V2 adds features via wrapper
public struct DataV2Wrapper has key {
    id: UID,
    inner: DataV1,  // Contains V1 data
    new_field: u64, // New functionality
}

// Migration function
public fun upgrade_to_v2(data: DataV1, ctx: &mut TxContext): DataV2Wrapper {
    DataV2Wrapper {
        id: object::new(ctx),
        inner: data,
        new_field: 0,
    }
}
```

### Pattern 4: Function Deprecation (Not Removal)

```move
/// Original function - NEVER remove, keep forever
public fun old_function(data: &Data): u64 {
    // Delegate to new implementation
    new_function(data, default_options())
}

/// New function with more features
public fun new_function(data: &Data, options: Options): u64 {
    // New implementation
}

/// Mark as deprecated in documentation, not in code
/// #[deprecated = "Use new_function instead"]
/// But the function still works!
```

### Pattern 5: Upgrade Capability Control

```move
public struct UpgradeCap has key {
    id: UID,
    package_id: ID,
    policy: u8,  // 0=compatible, 1=additive, 2=dep_only
}

public fun restrict_upgrades(cap: &mut UpgradeCap, new_policy: u8) {
    // Can only make more restrictive
    assert!(new_policy >= cap.policy, E_CANNOT_RELAX_POLICY);
    cap.policy = new_policy;
}

public fun make_immutable(cap: UpgradeCap) {
    // Destroy cap - no more upgrades possible
    let UpgradeCap { id, package_id: _, policy: _ } = cap;
    object::delete(id);
}
```

## Upgrade Checklist

### Before Upgrading

```markdown
1. [ ] All struct layouts are IDENTICAL to previous version
2. [ ] No fields added, removed, or reordered in existing structs
3. [ ] All public function signatures are unchanged
4. [ ] No public functions removed
5. [ ] Type parameters unchanged (phantom status, constraints)
6. [ ] New functionality uses new functions or dynamic fields
7. [ ] Migration path exists for version-specific logic
```

### Compatible Changes (Allowed)

```move
// ✅ Add new public functions
public fun new_feature() { }

// ✅ Add new structs
public struct NewData has key { }

// ✅ Change function implementations (not signatures)
public fun existing_fn(): u64 {
    // Changed implementation is OK
    new_calculation()
}

// ✅ Add private/internal functions
fun helper() { }

// ✅ Use dynamic fields for new data
df::add(&mut obj.id, b"new_data", value);
```

### Incompatible Changes (Forbidden)

```move
// ❌ Change struct fields
public struct Data {
    new_field: u64,  // BREAKS existing objects
}

// ❌ Change function signature
public fun func(new_param: u64) { }  // BREAKS callers

// ❌ Remove public function
// (deleted function)  // BREAKS dependent packages

// ❌ Change type parameters
public struct Pool<T: store> { }  // Was phantom T

// ❌ Change abilities
public struct Data has key { }  // Had key, store
```

## Recommended Mitigations

### 1. Design for Extensibility from Day One

```move
public struct Protocol has key {
    id: UID,
    version: u64,  // Always include version
    // Core fields only - use dynamic fields for rest
}
```

### 2. Never Remove Public Functions

```move
// Keep old function, delegate to new
public fun old_api(): u64 { new_api(defaults()) }
public fun new_api(opts: Options): u64 { /* new impl */ }
```

### 3. Use Dynamic Fields for Extensions

```move
// Add new data without changing struct
df::add(&mut obj.id, b"v2_data", new_data);
```

### 4. Test Upgrades Thoroughly

```move
#[test]
fun test_upgrade_compatibility() {
    // Create objects with v1
    // Upgrade package
    // Verify v1 objects still work with v2 code
}
```

### 5. Document Breaking Changes

```move
/// UPGRADE NOTES:
/// - v1 -> v2: No breaking changes
/// - v2 -> v3: Call migrate() on existing objects
```

## Testing Checklist

- [ ] Verify existing objects deserialize after upgrade
- [ ] Test all public functions work with old objects
- [ ] Confirm dependent packages still compile
- [ ] Test migration functions handle all versions
- [ ] Verify new features don't affect old code paths
- [ ] Check upgrade policy allows planned changes
- [ ] Test rollback scenarios if possible

## Related Vulnerabilities

- [Weak Initializers](../weak-initializers/)
- [Ability Misconfiguration](../ability-misconfiguration/)
- [Dynamic Field Misuse](../dynamic-field-misuse/)
- [Ownership Model Confusion](../ownership-model-confusion/)