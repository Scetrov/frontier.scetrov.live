+++
title = '20. Weak Initializers'
date = '2025-11-26T20:16:25Z'
weight = 20
+++

## Overview

Weak or improperly protected initialization functions can allow attackers to reinitialize protocol state, overwrite critical settings, or take control of the protocol. The `init` function in Sui Move has special protections, but custom initialization patterns often lack similar safeguards.

## Risk Level

**Critical** — Can lead to complete protocol takeover.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-665 (Improper Initialization) |

## The Problem

### Safe vs Unsafe Initialization

| Pattern | Safety | Notes |
|---------|--------|-------|
| `fun init(ctx)` | Safe | Called once at publish, not callable after |
| `fun init(witness: WITNESS, ctx)` | Safe | One-Time Witness pattern |
| `public fun initialize(...)` | **Unsafe** | Can be called by anyone, anytime |
| `public entry fun setup(...)` | **Unsafe** | Unless properly guarded |

## Vulnerable Example

```move
module vulnerable::protocol {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    public struct ProtocolState has key {
        id: UID,
        admin: address,
        fee_bps: u64,
        treasury: address,
        initialized: bool,
    }

    /// VULNERABLE: Public init can be called by anyone
    public entry fun initialize(
        fee_bps: u64,
        treasury: address,
        ctx: &mut TxContext
    ) {
        let state = ProtocolState {
            id: object::new(ctx),
            admin: tx_context::sender(ctx),  // Caller becomes admin!
            fee_bps,
            treasury,
            initialized: true,
        };
        
        transfer::share_object(state);
    }

    /// VULNERABLE: Boolean check can be bypassed
    public entry fun reinitialize(
        state: &mut ProtocolState,
        new_admin: address,
        ctx: &mut TxContext
    ) {
        // Attacker sets initialized = false first
        // Then calls reinitialize
        assert!(!state.initialized, E_ALREADY_INITIALIZED);
        
        state.admin = new_admin;
        state.initialized = true;
    }

    /// VULNERABLE: Allows resetting initialized flag
    public entry fun reset(state: &mut ProtocolState) {
        // Anyone can reset, then reinitialize
        state.initialized = false;
    }
}

module vulnerable::token {
    use sui::coin::{Self, TreasuryCap};

    /// VULNERABLE: TreasuryCap created in callable function
    public fun create_currency<T: drop>(
        witness: T,
        ctx: &mut TxContext
    ): TreasuryCap<T> {
        // If witness type has `drop`, attacker can call this
        let (treasury_cap, metadata) = coin::create_currency(
            witness,
            9,
            b"VULN",
            b"Vulnerable Token",
            b"",
            option::none(),
            ctx
        );
        
        transfer::public_freeze_object(metadata);
        treasury_cap  // Attacker gets minting rights!
    }
}
```

### Attack Scenario

```move
// Attacker sees protocol deployed without calling init
module attack::takeover {
    use vulnerable::protocol;

    public entry fun exploit(ctx: &mut TxContext) {
        // Attacker becomes admin
        protocol::initialize(
            9999,           // Max fees
            @attacker,      // Treasury to attacker
            ctx
        );
    }
}
```

## Secure Example

```move
module secure::protocol {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::package;

    /// One-Time Witness — can only be used in init
    public struct PROTOCOL has drop {}

    public struct ProtocolState has key {
        id: UID,
        admin: address,
        fee_bps: u64,
        treasury: address,
    }

    /// SECURE: Admin capability created at init
    public struct AdminCap has key {
        id: UID,
        protocol_id: ID,
    }

    /// SECURE: Called exactly once at package publish
    fun init(witness: PROTOCOL, ctx: &mut TxContext) {
        // Create publisher for package
        let publisher = package::claim(witness, ctx);
        
        let state = ProtocolState {
            id: object::new(ctx),
            admin: tx_context::sender(ctx),
            fee_bps: 100,  // Default fee
            treasury: tx_context::sender(ctx),
        };
        
        let state_id = object::id(&state);
        
        let admin_cap = AdminCap {
            id: object::new(ctx),
            protocol_id: state_id,
        };
        
        transfer::share_object(state);
        transfer::transfer(admin_cap, tx_context::sender(ctx));
        transfer::public_transfer(publisher, tx_context::sender(ctx));
    }

    /// SECURE: Admin updates require capability
    public entry fun update_config(
        cap: &AdminCap,
        state: &mut ProtocolState,
        new_fee_bps: u64,
        new_treasury: address,
    ) {
        assert!(cap.protocol_id == object::id(state), E_WRONG_PROTOCOL);
        assert!(new_fee_bps <= 1000, E_FEE_TOO_HIGH);  // Max 10%
        
        state.fee_bps = new_fee_bps;
        state.treasury = new_treasury;
    }

    /// SECURE: No reinitialize function exists
    // Initialization happens exactly once in init()
}

module secure::token {
    use sui::coin::{Self, TreasuryCap, CoinMetadata};
    use sui::tx_context::TxContext;
    use sui::transfer;

    /// SECURE: One-Time Witness
    public struct MY_TOKEN has drop {}

    /// SECURE: Called once at publish
    fun init(witness: MY_TOKEN, ctx: &mut TxContext) {
        let (treasury_cap, metadata) = coin::create_currency(
            witness,
            9,
            b"MYT",
            b"My Token",
            b"A secure token",
            option::none(),
            ctx
        );
        
        // Freeze metadata
        transfer::public_freeze_object(metadata);
        
        // Transfer cap to deployer only
        transfer::transfer(treasury_cap, tx_context::sender(ctx));
    }

    // No public function to create additional currencies
}
```

## Initialization Patterns

### Pattern 1: One-Time Witness (OTW)

```move
/// The module name, in CAPS, with `drop` ability only
public struct MY_MODULE has drop {}

/// init receives the OTW and can only be called once
fun init(witness: MY_MODULE, ctx: &mut TxContext) {
    // Guaranteed to run exactly once at publish
    // witness cannot be created elsewhere
}
```

### Pattern 2: Package Publisher

```move
use sui::package::{Self, Publisher};

fun init(otw: MY_MODULE, ctx: &mut TxContext) {
    let publisher = package::claim(otw, ctx);
    // Publisher proves package ownership
    transfer::transfer(publisher, tx_context::sender(ctx));
}
```

### Pattern 3: Capability Created at Init

```move
fun init(ctx: &mut TxContext) {
    let admin_cap = AdminCap { id: object::new(ctx) };
    // Cap only exists because init was called
    // Cannot be recreated
    transfer::transfer(admin_cap, tx_context::sender(ctx));
}
```

### Pattern 4: Post-Deploy Configuration (Safe)

```move
/// State created in init, configured later
public struct PendingSetup has key {
    id: UID,
    deployer: address,
    setup_deadline: u64,
}

fun init(ctx: &mut TxContext) {
    transfer::share_object(PendingSetup {
        id: object::new(ctx),
        deployer: tx_context::sender(ctx),
        setup_deadline: 0,  // Set during first setup
    });
}

/// SECURE: Only deployer, only once, with deadline
public entry fun complete_setup(
    pending: PendingSetup,
    config: SetupConfig,
    clock: &Clock,
    ctx: &TxContext
) {
    let PendingSetup { id, deployer, setup_deadline } = pending;
    
    assert!(tx_context::sender(ctx) == deployer, E_NOT_DEPLOYER);
    
    if (setup_deadline > 0) {
        assert!(clock::timestamp_ms(clock) < setup_deadline, E_SETUP_EXPIRED);
    };
    
    object::delete(id);
    
    // Create actual protocol state
    let state = ProtocolState { /* ... */ };
    transfer::share_object(state);
}
```

## Recommended Mitigations

### 1. Always Use the `init` Function

```move
/// This is the ONLY safe way to initialize
fun init(ctx: &mut TxContext) {
    // Called exactly once at publish
}
```

### 2. Use One-Time Witness for Important Setup

```move
public struct MY_PROTOCOL has drop {}

fun init(witness: MY_PROTOCOL, ctx: &mut TxContext) {
    // witness guarantees single execution
}
```

### 3. Never Provide Public Initialize Functions

```move
// BAD: Anyone can call
public fun initialize(...) { }

// BAD: Entry doesn't help
public entry fun initialize(...) { }

// GOOD: Use init only
fun init(ctx: &mut TxContext) { }
```

### 4. Create Capabilities at Init Time

```move
fun init(ctx: &mut TxContext) {
    // Admin cap created here cannot be recreated
    let cap = AdminCap { id: object::new(ctx) };
    transfer::transfer(cap, tx_context::sender(ctx));
}
```

## Testing Checklist

- [ ] Verify init() is the only initialization function
- [ ] Confirm no public initialize/setup functions exist
- [ ] Test that OTW cannot be created outside init
- [ ] Verify state cannot be reinitialized after init
- [ ] Confirm capabilities created in init cannot be recreated

## Related Vulnerabilities

- [Access-Control Mistakes](../access-control-mistakes/)
- [Capability Leakage](../capability-leakage/)
- [Object Transfer Misuse](../object-transfer-misuse/)
