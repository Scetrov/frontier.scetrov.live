+++
title = '31. Unvalidated Struct Fields'
date = '2025-11-26T21:46:35Z'
weight = 31
+++

## Overview

Unvalidated struct fields occur when smart contracts accept user-provided data to populate struct fields without proper validation, leading to invalid state, security bypasses, or protocol corruption. In Sui Move, structs often represent critical protocol state, and failing to validate inputs during construction or modification can have severe consequences.

## Risk Level

**High** — Can lead to invalid state, security bypasses, or financial losses.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A04 (Insecure Design) | CWE-20 (Improper Input Validation) |

## The Problem

### Common Validation Failures

| Issue | Risk | Description |
|-------|------|-------------|
| No range validation | High | Values outside acceptable bounds |
| No format validation | Medium | Invalid strings or identifiers |
| No relationship validation | High | Fields that must be consistent |
| No business rule validation | High | Values that violate protocol logic |
| No sanitization | Medium | Malicious or unexpected input |

## Vulnerable Example

```move
module vulnerable::lending {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    public struct LendingPool has key {
        id: UID,
        /// VULNERABLE: No validation on interest rate
        interest_rate_bps: u64,  // Could be 0 or 1000000
        /// VULNERABLE: No validation on ratios
        collateral_ratio_bps: u64,
        liquidation_ratio_bps: u64,
        /// VULNERABLE: No validation on addresses
        treasury: address,
        oracle: address,
    }

    /// VULNERABLE: Accepts any values without validation
    public entry fun create_pool(
        interest_rate_bps: u64,
        collateral_ratio_bps: u64,
        liquidation_ratio_bps: u64,
        treasury: address,
        oracle: address,
        ctx: &mut TxContext
    ) {
        let pool = LendingPool {
            id: object::new(ctx),
            interest_rate_bps,        // Could be 100% or 0%
            collateral_ratio_bps,     // Could be less than liquidation!
            liquidation_ratio_bps,
            treasury,                  // Could be @0x0
            oracle,                    // Could be attacker's address
        };
        
        transfer::share_object(pool);
    }

    /// VULNERABLE: Update without validation
    public entry fun update_rates(
        pool: &mut LendingPool,
        new_interest_rate: u64,
        new_collateral_ratio: u64,
        _ctx: &mut TxContext
    ) {
        // No validation - could set absurd rates
        pool.interest_rate_bps = new_interest_rate;
        pool.collateral_ratio_bps = new_collateral_ratio;
    }
}

module vulnerable::nft {
    use sui::object::{Self, UID};
    use std::string::{Self, String};

    public struct NFT has key, store {
        id: UID,
        /// VULNERABLE: No length limits
        name: String,
        description: String,
        /// VULNERABLE: No URL validation
        image_url: String,
        /// VULNERABLE: No bounds on attributes
        rarity: u64,
        power: u64,
    }

    /// VULNERABLE: Accepts any string content
    public fun create_nft(
        name: String,
        description: String,
        image_url: String,
        rarity: u64,
        power: u64,
        ctx: &mut TxContext
    ): NFT {
        // No validation at all!
        NFT {
            id: object::new(ctx),
            name,          // Could be empty or 10MB
            description,   // Could contain malicious content
            image_url,     // Could be javascript: or data: URI
            rarity,        // Could be any number
            power,         // Could break game balance
        }
    }
}

module vulnerable::auction {
    use sui::object::{Self, UID};
    use sui::clock::Clock;

    public struct Auction has key {
        id: UID,
        /// VULNERABLE: Time relationships not validated
        start_time: u64,
        end_time: u64,
        /// VULNERABLE: Price relationships not validated
        starting_price: u64,
        reserve_price: u64,
        minimum_increment: u64,
    }

    /// VULNERABLE: Invalid time/price configurations allowed
    public fun create_auction(
        start_time: u64,
        end_time: u64,
        starting_price: u64,
        reserve_price: u64,
        minimum_increment: u64,
        ctx: &mut TxContext
    ): Auction {
        // No validation of relationships!
        Auction {
            id: object::new(ctx),
            start_time,         // Could be in the past
            end_time,           // Could be before start_time!
            starting_price,     // Could be higher than reserve
            reserve_price,
            minimum_increment,  // Could be 0
        }
    }
}

module vulnerable::user {
    public struct UserProfile has key {
        id: UID,
        owner: address,
        /// VULNERABLE: No validation on username
        username: vector<u8>,
        /// VULNERABLE: Tier can be set to anything
        tier: u8,
        /// VULNERABLE: Points can be manipulated
        points: u64,
    }

    /// VULNERABLE: User can set their own tier
    public entry fun create_profile(
        username: vector<u8>,
        tier: u8,        // User chooses their tier!
        points: u64,     // User chooses their points!
        ctx: &mut TxContext
    ) {
        let profile = UserProfile {
            id: object::new(ctx),
            owner: tx_context::sender(ctx),
            username,
            tier,
            points,
        };
        
        transfer::transfer(profile, tx_context::sender(ctx));
    }
}
```

### Attack Scenarios

```move
module attack::exploit_unvalidated {
    use vulnerable::lending;
    use vulnerable::user;

    /// Set up a lending pool that always liquidates
    public entry fun create_trap_pool(ctx: &mut TxContext) {
        lending::create_pool(
            10000,      // 100% interest rate
            5000,       // 50% collateral ratio
            9999,       // 99.99% liquidation ratio (> collateral!)
            @attacker,  // Treasury to attacker
            @attacker,  // Fake oracle
            ctx
        );
    }

    /// Create an admin-tier user profile
    public entry fun become_admin(ctx: &mut TxContext) {
        user::create_profile(
            b"hacker",
            255,          // Max tier = admin?
            1000000000,   // Billion points
            ctx
        );
    }
}
```

## Secure Example

```move
module secure::lending {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    const E_INVALID_INTEREST_RATE: u64 = 1;
    const E_INVALID_COLLATERAL_RATIO: u64 = 2;
    const E_INVALID_LIQUIDATION_RATIO: u64 = 3;
    const E_RATIOS_INCONSISTENT: u64 = 4;
    const E_INVALID_ADDRESS: u64 = 5;
    const E_NOT_ADMIN: u64 = 6;

    /// Bounds for validation
    const MIN_INTEREST_RATE_BPS: u64 = 0;
    const MAX_INTEREST_RATE_BPS: u64 = 5000;  // Max 50% APR
    const MIN_COLLATERAL_RATIO_BPS: u64 = 10000;  // Min 100%
    const MAX_COLLATERAL_RATIO_BPS: u64 = 30000;  // Max 300%
    const MIN_LIQUIDATION_RATIO_BPS: u64 = 10000;  // Min 100%
    const LIQUIDATION_BUFFER_BPS: u64 = 500;  // 5% buffer required

    public struct AdminCap has key {
        id: UID,
        pool_id: ID,
    }

    public struct LendingPool has key {
        id: UID,
        interest_rate_bps: u64,
        collateral_ratio_bps: u64,
        liquidation_ratio_bps: u64,
        treasury: address,
        oracle: address,
    }

    /// SECURE: Validates all inputs before creating pool
    public entry fun create_pool(
        interest_rate_bps: u64,
        collateral_ratio_bps: u64,
        liquidation_ratio_bps: u64,
        treasury: address,
        oracle: address,
        ctx: &mut TxContext
    ) {
        // Validate interest rate
        assert!(
            interest_rate_bps >= MIN_INTEREST_RATE_BPS &&
            interest_rate_bps <= MAX_INTEREST_RATE_BPS,
            E_INVALID_INTEREST_RATE
        );
        
        // Validate collateral ratio
        assert!(
            collateral_ratio_bps >= MIN_COLLATERAL_RATIO_BPS &&
            collateral_ratio_bps <= MAX_COLLATERAL_RATIO_BPS,
            E_INVALID_COLLATERAL_RATIO
        );
        
        // Validate liquidation ratio
        assert!(
            liquidation_ratio_bps >= MIN_LIQUIDATION_RATIO_BPS,
            E_INVALID_LIQUIDATION_RATIO
        );
        
        // SECURE: Validate relationship between ratios
        // Collateral must be higher than liquidation + buffer
        assert!(
            collateral_ratio_bps >= liquidation_ratio_bps + LIQUIDATION_BUFFER_BPS,
            E_RATIOS_INCONSISTENT
        );
        
        // Validate addresses
        assert!(treasury != @0x0, E_INVALID_ADDRESS);
        assert!(oracle != @0x0, E_INVALID_ADDRESS);
        
        let pool = LendingPool {
            id: object::new(ctx),
            interest_rate_bps,
            collateral_ratio_bps,
            liquidation_ratio_bps,
            treasury,
            oracle,
        };
        
        let pool_id = object::id(&pool);
        
        // Create admin cap for authorized updates
        let admin_cap = AdminCap {
            id: object::new(ctx),
            pool_id,
        };
        
        transfer::share_object(pool);
        transfer::transfer(admin_cap, tx_context::sender(ctx));
    }

    /// SECURE: Validated updates with admin authorization
    public entry fun update_rates(
        admin_cap: &AdminCap,
        pool: &mut LendingPool,
        new_interest_rate: u64,
        new_collateral_ratio: u64,
        _ctx: &mut TxContext
    ) {
        // Verify admin
        assert!(admin_cap.pool_id == object::id(pool), E_NOT_ADMIN);
        
        // Validate new values
        assert!(
            new_interest_rate <= MAX_INTEREST_RATE_BPS,
            E_INVALID_INTEREST_RATE
        );
        
        assert!(
            new_collateral_ratio >= MIN_COLLATERAL_RATIO_BPS &&
            new_collateral_ratio >= pool.liquidation_ratio_bps + LIQUIDATION_BUFFER_BPS,
            E_INVALID_COLLATERAL_RATIO
        );
        
        pool.interest_rate_bps = new_interest_rate;
        pool.collateral_ratio_bps = new_collateral_ratio;
    }
}

module secure::nft {
    use sui::object::{Self, UID};
    use std::string::{Self, String};
    use std::vector;

    const E_NAME_TOO_SHORT: u64 = 1;
    const E_NAME_TOO_LONG: u64 = 2;
    const E_DESCRIPTION_TOO_LONG: u64 = 3;
    const E_INVALID_URL: u64 = 4;
    const E_INVALID_RARITY: u64 = 5;
    const E_INVALID_POWER: u64 = 6;
    const E_INVALID_CHARACTERS: u64 = 7;

    const MIN_NAME_LENGTH: u64 = 3;
    const MAX_NAME_LENGTH: u64 = 64;
    const MAX_DESCRIPTION_LENGTH: u64 = 1024;
    const MAX_URL_LENGTH: u64 = 256;
    const MAX_RARITY: u64 = 5;
    const MAX_POWER: u64 = 100;

    public struct NFT has key, store {
        id: UID,
        name: String,
        description: String,
        image_url: String,
        rarity: u64,
        power: u64,
    }

    /// SECURE: Validates all NFT fields
    public fun create_nft(
        name: String,
        description: String,
        image_url: String,
        rarity: u64,
        power: u64,
        ctx: &mut TxContext
    ): NFT {
        // Validate name
        let name_len = string::length(&name);
        assert!(name_len >= MIN_NAME_LENGTH, E_NAME_TOO_SHORT);
        assert!(name_len <= MAX_NAME_LENGTH, E_NAME_TOO_LONG);
        assert!(is_valid_name(&name), E_INVALID_CHARACTERS);
        
        // Validate description
        assert!(string::length(&description) <= MAX_DESCRIPTION_LENGTH, E_DESCRIPTION_TOO_LONG);
        
        // Validate URL
        assert!(string::length(&image_url) <= MAX_URL_LENGTH, E_INVALID_URL);
        assert!(is_valid_url(&image_url), E_INVALID_URL);
        
        // Validate numeric fields
        assert!(rarity <= MAX_RARITY, E_INVALID_RARITY);
        assert!(power <= MAX_POWER, E_INVALID_POWER);
        
        NFT {
            id: object::new(ctx),
            name,
            description,
            image_url,
            rarity,
            power,
        }
    }

    /// Validate name contains only allowed characters
    fun is_valid_name(name: &String): bool {
        let bytes = string::bytes(name);
        let len = vector::length(bytes);
        let mut i = 0;
        
        while (i < len) {
            let byte = *vector::borrow(bytes, i);
            // Allow alphanumeric, space, hyphen, underscore
            let valid = (byte >= 48 && byte <= 57) ||  // 0-9
                       (byte >= 65 && byte <= 90) ||   // A-Z
                       (byte >= 97 && byte <= 122) ||  // a-z
                       byte == 32 || byte == 45 || byte == 95;  // space, -, _
            
            if (!valid) {
                return false
            };
            i = i + 1;
        };
        
        true
    }

    /// Validate URL format (basic check)
    fun is_valid_url(url: &String): bool {
        let bytes = string::bytes(url);
        let len = vector::length(bytes);
        
        // Must have minimum length for https://x
        if (len < 10) {
            return false
        };
        
        // Must start with https://
        let https_prefix = b"https://";
        let mut i = 0;
        while (i < 8) {
            if (*vector::borrow(bytes, i) != *vector::borrow(&https_prefix, i)) {
                return false
            };
            i = i + 1;
        };
        
        // Block dangerous schemes
        // (Already handled by requiring https://)
        
        true
    }
}

module secure::auction {
    use sui::object::{Self, UID};
    use sui::clock::{Self, Clock};

    const E_INVALID_START_TIME: u64 = 1;
    const E_INVALID_END_TIME: u64 = 2;
    const E_DURATION_TOO_SHORT: u64 = 3;
    const E_DURATION_TOO_LONG: u64 = 4;
    const E_INVALID_STARTING_PRICE: u64 = 5;
    const E_RESERVE_BELOW_START: u64 = 6;
    const E_INCREMENT_TOO_SMALL: u64 = 7;

    const MIN_DURATION_MS: u64 = 3600_000;     // 1 hour
    const MAX_DURATION_MS: u64 = 604800_000;   // 1 week
    const MIN_INCREMENT_BPS: u64 = 100;        // 1% minimum increment

    public struct Auction has key {
        id: UID,
        start_time: u64,
        end_time: u64,
        starting_price: u64,
        reserve_price: u64,
        minimum_increment: u64,
    }

    /// SECURE: Validates time and price relationships
    public fun create_auction(
        start_time: u64,
        end_time: u64,
        starting_price: u64,
        reserve_price: u64,
        minimum_increment: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ): Auction {
        let now = clock::timestamp_ms(clock);
        
        // Validate start time is in the future
        assert!(start_time > now, E_INVALID_START_TIME);
        
        // Validate end time is after start time
        assert!(end_time > start_time, E_INVALID_END_TIME);
        
        // Validate duration bounds
        let duration = end_time - start_time;
        assert!(duration >= MIN_DURATION_MS, E_DURATION_TOO_SHORT);
        assert!(duration <= MAX_DURATION_MS, E_DURATION_TOO_LONG);
        
        // Validate prices
        assert!(starting_price > 0, E_INVALID_STARTING_PRICE);
        assert!(reserve_price >= starting_price, E_RESERVE_BELOW_START);
        
        // Validate minimum increment
        let min_increment = (starting_price * MIN_INCREMENT_BPS) / 10000;
        assert!(minimum_increment >= min_increment, E_INCREMENT_TOO_SMALL);
        
        Auction {
            id: object::new(ctx),
            start_time,
            end_time,
            starting_price,
            reserve_price,
            minimum_increment,
        }
    }
}

module secure::user {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};

    const E_USERNAME_TOO_SHORT: u64 = 1;
    const E_USERNAME_TOO_LONG: u64 = 2;
    const E_INVALID_USERNAME: u64 = 3;

    const MIN_USERNAME_LENGTH: u64 = 3;
    const MAX_USERNAME_LENGTH: u64 = 20;
    const STARTING_TIER: u8 = 0;
    const STARTING_POINTS: u64 = 0;

    public struct UserProfile has key {
        id: UID,
        owner: address,
        username: vector<u8>,
        tier: u8,
        points: u64,
    }

    /// SECURE: System-controlled tier and points
    public entry fun create_profile(
        username: vector<u8>,
        ctx: &mut TxContext
    ) {
        // Validate username
        let len = vector::length(&username);
        assert!(len >= MIN_USERNAME_LENGTH, E_USERNAME_TOO_SHORT);
        assert!(len <= MAX_USERNAME_LENGTH, E_USERNAME_TOO_LONG);
        assert!(is_valid_username(&username), E_INVALID_USERNAME);
        
        let profile = UserProfile {
            id: object::new(ctx),
            owner: tx_context::sender(ctx),
            username,
            tier: STARTING_TIER,     // SECURE: System-set, not user input
            points: STARTING_POINTS, // SECURE: System-set, not user input
        };
        
        transfer::transfer(profile, tx_context::sender(ctx));
    }

    /// SECURE: Only authorized upgrades
    public entry fun upgrade_tier(
        admin_cap: &AdminCap,
        profile: &mut UserProfile,
        new_tier: u8,
    ) {
        // Only admin can change tier
        profile.tier = new_tier;
    }

    fun is_valid_username(username: &vector<u8>): bool {
        let len = vector::length(username);
        let mut i = 0;
        
        while (i < len) {
            let byte = *vector::borrow(username, i);
            // Alphanumeric and underscore only
            let valid = (byte >= 48 && byte <= 57) ||  // 0-9
                       (byte >= 65 && byte <= 90) ||   // A-Z
                       (byte >= 97 && byte <= 122) ||  // a-z
                       byte == 95;                      // _
            
            if (!valid) {
                return false
            };
            i = i + 1;
        };
        
        true
    }
}
```

## Validation Patterns

### Pattern 1: Range Validation

```move
const MIN_VALUE: u64 = 1;
const MAX_VALUE: u64 = 1000;

fun validate_range(value: u64) {
    assert!(value >= MIN_VALUE && value <= MAX_VALUE, E_OUT_OF_RANGE);
}
```

### Pattern 2: Relationship Validation

```move
fun validate_time_range(start: u64, end: u64, now: u64) {
    assert!(start > now, E_START_IN_PAST);
    assert!(end > start, E_END_BEFORE_START);
    assert!(end - start <= MAX_DURATION, E_DURATION_TOO_LONG);
}
```

### Pattern 3: Builder Pattern

```move
public struct ConfigBuilder {
    interest_rate: Option<u64>,
    collateral_ratio: Option<u64>,
}

public fun new_builder(): ConfigBuilder {
    ConfigBuilder {
        interest_rate: option::none(),
        collateral_ratio: option::none(),
    }
}

public fun with_interest_rate(builder: ConfigBuilder, rate: u64): ConfigBuilder {
    assert!(rate <= MAX_RATE, E_INVALID_RATE);
    ConfigBuilder {
        interest_rate: option::some(rate),
        ..builder
    }
}

public fun build(builder: ConfigBuilder): Config {
    assert!(option::is_some(&builder.interest_rate), E_MISSING_FIELD);
    assert!(option::is_some(&builder.collateral_ratio), E_MISSING_FIELD);
    
    Config {
        interest_rate: option::extract(&mut builder.interest_rate),
        collateral_ratio: option::extract(&mut builder.collateral_ratio),
    }
}
```

### Pattern 4: Whitelist Validation

```move
const ALLOWED_TIERS: vector<u8> = vector[0, 1, 2, 3];

fun validate_tier(tier: u8) {
    let mut valid = false;
    let len = vector::length(&ALLOWED_TIERS);
    let mut i = 0;
    
    while (i < len) {
        if (*vector::borrow(&ALLOWED_TIERS, i) == tier) {
            valid = true;
            break
        };
        i = i + 1;
    };
    
    assert!(valid, E_INVALID_TIER);
}
```

## Recommended Mitigations

### 1. Define Clear Bounds

```move
const MIN_VALUE: u64 = X;
const MAX_VALUE: u64 = Y;
```

### 2. Validate All Inputs

```move
public fun create(value: u64): Object {
    validate_value(value);  // Always validate
    Object { value }
}
```

### 3. Validate Relationships

```move
assert!(end_time > start_time, E_INVALID_TIME_RANGE);
assert!(collateral > liquidation, E_INVALID_RATIO);
```

### 4. System-Controlled Sensitive Fields

```move
// User provides: username
// System controls: tier, points, permissions
```

### 5. Sanitize String Inputs

```move
assert!(is_valid_format(input), E_INVALID_FORMAT);
assert!(length <= MAX_LENGTH, E_TOO_LONG);
```

## Testing Checklist

- [ ] Test boundary values (min, max, min-1, max+1)
- [ ] Test zero values where inappropriate
- [ ] Test maximum length strings
- [ ] Test invalid characters in strings
- [ ] Test inconsistent relationship values
- [ ] Test that sensitive fields cannot be user-set
- [ ] Test validation error messages are informative
- [ ] Fuzz test with random inputs

## Related Vulnerabilities

- [Numeric / Bitwise Pitfalls](../numeric-bitwise-pitfalls/)
- [Access-Control Mistakes](../access-control-mistakes/)
- [Unsafe BCS Parsing](../unsafe-bcs-parsing/)
- [General Move Logic Errors](../general-move-logic-errors/)
