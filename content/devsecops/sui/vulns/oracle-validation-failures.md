+++
title = '21. Oracle Validation Failures'
date = '2025-11-26T00:00:00Z'
weight = 21
+++

## Overview

Oracle validation failures occur when smart contracts blindly trust off-chain data sources without proper verification. In Sui Move, oracles provide critical data like prices, random numbers, or external state, but improper validation can lead to manipulation, stale data exploitation, or complete protocol compromise.

## Risk Level

**Critical** — Can lead to significant financial losses, especially in DeFi protocols.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A08 (Software and Data Integrity Failures) | CWE-345 (Insufficient Verification of Data Authenticity), CWE-353 (Missing Support for Integrity Check) | 

## The Problem

### Common Oracle Trust Issues

 | Issue | Risk | Description | 
 | ------- | ------ | ------------- | 
 | No staleness check | High | Using outdated prices that no longer reflect market | 
 | No source verification | Critical | Accepting data from untrusted oracles | 
 | No price bounds | High | Accepting unrealistic price values | 
 | Single oracle dependency | Medium | No fallback if oracle fails | 
 | No signature verification | Critical | Accepting unsigned or improperly signed data | 

## Vulnerable Example

```move
module vulnerable::lending {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};

    const E_INSUFFICIENT_COLLATERAL: u64 = 1;

    public struct LendingPool<phantom T> has key {
        id: UID,
        total_deposits: Balance<T>,
        oracle: address,  // Just stores an address!
    }

    public struct PriceData has copy, drop {
        asset: vector<u8>,
        price: u64,
        timestamp: u64,
    }

    /// VULNERABLE: No validation of oracle data
    public entry fun borrow<T, C>(
        pool: &mut LendingPool<T>,
        collateral: Coin<C>,
        borrow_amount: u64,
        price_data: PriceData,  // Anyone can pass any price!
        ctx: &mut TxContext
    ) {
        let collateral_value = coin::value(&collateral);
        
        // VULNERABLE: No check on who provided price_data
        // VULNERABLE: No check if price_data is stale
        // VULNERABLE: No signature verification
        let required_collateral = (borrow_amount * 150) / price_data.price;
        
        assert!(collateral_value >= required_collateral, E_INSUFFICIENT_COLLATERAL);
        
        // Process borrow...
    }

    /// VULNERABLE: Oracle address can be set by anyone
    public entry fun set_oracle<T>(
        pool: &mut LendingPool<T>,
        new_oracle: address,
        _ctx: &mut TxContext
    ) {
        // No access control!
        pool.oracle = new_oracle;
    }
}

module vulnerable::price_oracle {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    public struct PriceFeed has key {
        id: UID,
        price: u64,
        last_update: u64,
    }

    /// VULNERABLE: Anyone can update the price
    public entry fun update_price(
        feed: &mut PriceFeed,
        new_price: u64,
        _ctx: &mut TxContext
    ) {
        // No access control!
        // No validation of price bounds!
        feed.price = new_price;
        feed.last_update = 0;  // Timestamp not even set properly
    }

    /// VULNERABLE: Returns stale data without warning
    public fun get_price(feed: &PriceFeed): u64 {
        // No staleness check!
        feed.price
    }
}
```

### Attack Scenario

```move
module attack::oracle_manipulation {
    use vulnerable::lending;
    use vulnerable::price_oracle;

    /// Attacker manipulates price to undercollateralize
    public entry fun exploit(ctx: &mut TxContext) {
        // Step 1: Create fake price data with inflated collateral price
        let fake_price = lending::PriceData {
            asset: b"ETH",
            price: 1_000_000_000,  // Massively inflated price
            timestamp: 0,
        };
        
        // Step 2: Use tiny collateral to borrow huge amounts
        // With price of 1B, $1 of collateral = $1B value
        // lending::borrow(..., fake_price, ...);
    }
}
```

## Secure Example

```move
module secure::oracle {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::clock::{Self, Clock};
    use sui::ed25519;
    use sui::bcs;

    const E_INVALID_SIGNATURE: u64 = 1;
    const E_STALE_PRICE: u64 = 2;
    const E_PRICE_OUT_OF_BOUNDS: u64 = 3;
    const E_WRONG_ASSET: u64 = 4;
    const E_INVALID_ORACLE: u64 = 5;
    
    const MAX_STALENESS_MS: u64 = 60_000;  // 1 minute
    const MIN_PRICE: u64 = 1;
    const MAX_PRICE: u64 = 1_000_000_000_000;  // $1T max

    public struct OracleRegistry has key {
        id: UID,
        trusted_oracles: vector<vector<u8>>,  // Public keys
        min_confirmations: u64,
    }

    public struct AdminCap has key {
        id: UID,
        registry_id: ID,
    }

    public struct PriceFeed has key {
        id: UID,
        asset: vector<u8>,
        price: u64,
        last_update_ms: u64,
        oracle_pubkey: vector<u8>,
    }

    public struct SignedPriceData has copy, drop {
        asset: vector<u8>,
        price: u64,
        timestamp_ms: u64,
        signature: vector<u8>,
        oracle_pubkey: vector<u8>,
    }

    /// SECURE: Only admin can manage oracle registry
    fun init(ctx: &mut TxContext) {
        let registry = OracleRegistry {
            id: object::new(ctx),
            trusted_oracles: vector::empty(),
            min_confirmations: 1,
        };
        
        let registry_id = object::id(&registry);
        
        let admin_cap = AdminCap {
            id: object::new(ctx),
            registry_id,
        };
        
        transfer::share_object(registry);
        transfer::transfer(admin_cap, tx_context::sender(ctx));
    }

    /// SECURE: Admin-controlled oracle registration
    public entry fun register_oracle(
        cap: &AdminCap,
        registry: &mut OracleRegistry,
        oracle_pubkey: vector<u8>,
    ) {
        assert!(cap.registry_id == object::id(registry), E_INVALID_ORACLE);
        vector::push_back(&mut registry.trusted_oracles, oracle_pubkey);
    }

    /// SECURE: Validates signature, staleness, and bounds
    public fun validate_and_get_price(
        registry: &OracleRegistry,
        signed_data: &SignedPriceData,
        expected_asset: vector<u8>,
        clock: &Clock,
    ): u64 {
        // 1. Verify the oracle is trusted
        let is_trusted = is_oracle_trusted(registry, &signed_data.oracle_pubkey);
        assert!(is_trusted, E_INVALID_ORACLE);
        
        // 2. Verify signature
        let message = create_price_message(
            &signed_data.asset,
            signed_data.price,
            signed_data.timestamp_ms
        );
        let valid_sig = ed25519::ed25519_verify(
            &signed_data.signature,
            &signed_data.oracle_pubkey,
            &message
        );
        assert!(valid_sig, E_INVALID_SIGNATURE);
        
        // 3. Check staleness
        let current_time = clock::timestamp_ms(clock);
        let age = current_time - signed_data.timestamp_ms;
        assert!(age <= MAX_STALENESS_MS, E_STALE_PRICE);
        
        // 4. Verify asset matches
        assert!(signed_data.asset == expected_asset, E_WRONG_ASSET);
        
        // 5. Check price bounds
        assert!(signed_data.price >= MIN_PRICE, E_PRICE_OUT_OF_BOUNDS);
        assert!(signed_data.price <= MAX_PRICE, E_PRICE_OUT_OF_BOUNDS);
        
        signed_data.price
    }

    fun is_oracle_trusted(
        registry: &OracleRegistry, 
        pubkey: &vector<u8>
    ): bool {
        let len = vector::length(&registry.trusted_oracles);
        let mut i = 0;
        while (i < len) {
            if (*vector::borrow(&registry.trusted_oracles, i) == *pubkey) {
                return true
            };
            i = i + 1;
        };
        false
    }

    fun create_price_message(
        asset: &vector<u8>,
        price: u64,
        timestamp: u64
    ): vector<u8> {
        let mut msg = vector::empty<u8>();
        vector::append(&mut msg, *asset);
        vector::append(&mut msg, bcs::to_bytes(&price));
        vector::append(&mut msg, bcs::to_bytes(&timestamp));
        msg
    }
}

module secure::lending {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};
    use sui::clock::Clock;
    use secure::oracle::{Self, OracleRegistry, SignedPriceData};

    const E_INSUFFICIENT_COLLATERAL: u64 = 1;
    const COLLATERAL_RATIO_BPS: u64 = 15000;  // 150%

    public struct LendingPool<phantom T> has key {
        id: UID,
        total_deposits: Balance<T>,
        collateral_asset: vector<u8>,
        borrow_asset: vector<u8>,
    }

    /// SECURE: Uses validated oracle data
    public entry fun borrow<T, C>(
        pool: &mut LendingPool<T>,
        registry: &OracleRegistry,
        collateral: Coin<C>,
        borrow_amount: u64,
        collateral_price_data: SignedPriceData,
        borrow_price_data: SignedPriceData,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // Get validated prices
        let collateral_price = oracle::validate_and_get_price(
            registry,
            &collateral_price_data,
            pool.collateral_asset,
            clock
        );
        
        let borrow_price = oracle::validate_and_get_price(
            registry,
            &borrow_price_data,
            pool.borrow_asset,
            clock
        );
        
        // Calculate collateral requirement with validated prices
        let collateral_value = coin::value(&collateral) * collateral_price;
        let borrow_value = borrow_amount * borrow_price;
        let required_collateral_value = (borrow_value * COLLATERAL_RATIO_BPS) / 10000;
        
        assert!(collateral_value >= required_collateral_value, E_INSUFFICIENT_COLLATERAL);
        
        // Process borrow safely...
    }
}
```

## Oracle Integration Patterns

### Pattern 1: Pyth Network Integration

```move
module example::pyth_consumer {
    use pyth::price::{Self, Price};
    use pyth::price_feed::{Self, PriceFeed};
    use pyth::pyth;
    use sui::clock::Clock;

    const E_STALE_PRICE: u64 = 1;
    const E_NEGATIVE_PRICE: u64 = 2;
    const MAX_AGE_SECONDS: u64 = 60;

    public fun get_validated_price(
        price_feed: &PriceFeed,
        clock: &Clock,
    ): u64 {
        let price = price_feed::get_price(price_feed);
        
        // Check price age
        let price_timestamp = price::get_timestamp(&price);
        let current_time = clock::timestamp_ms(clock) / 1000;
        assert!(current_time - price_timestamp <= MAX_AGE_SECONDS, E_STALE_PRICE);
        
        // Get price value (handle negative prices)
        let price_i64 = price::get_price(&price);
        assert!(price_i64 > 0, E_NEGATIVE_PRICE);
        
        (price_i64 as u64)
    }
}
```

### Pattern 2: Multi-Oracle Aggregation

```move
module secure::aggregated_oracle {
    use sui::clock::Clock;

    const E_INSUFFICIENT_ORACLES: u64 = 1;
    const E_PRICE_DEVIATION_TOO_HIGH: u64 = 2;
    const MAX_DEVIATION_BPS: u64 = 500;  // 5%

    public struct AggregatedPrice has copy, drop {
        median_price: u64,
        num_sources: u64,
        timestamp_ms: u64,
    }

    /// Aggregate multiple oracle prices with deviation check
    public fun aggregate_prices(
        prices: vector<u64>,
        clock: &Clock,
        min_sources: u64,
    ): AggregatedPrice {
        let num_prices = vector::length(&prices);
        assert!(num_prices >= min_sources, E_INSUFFICIENT_ORACLES);
        
        // Sort prices to find median
        let sorted = sort_prices(prices);
        let median_price = *vector::borrow(&sorted, num_prices / 2);
        
        // Check all prices are within acceptable deviation
        let mut i = 0;
        while (i < num_prices) {
            let price = *vector::borrow(&sorted, i);
            let deviation = calculate_deviation(price, median_price);
            assert!(deviation <= MAX_DEVIATION_BPS, E_PRICE_DEVIATION_TOO_HIGH);
            i = i + 1;
        };
        
        AggregatedPrice {
            median_price,
            num_sources: num_prices,
            timestamp_ms: clock::timestamp_ms(clock),
        }
    }

    fun calculate_deviation(price: u64, median: u64): u64 {
        if (price > median) {
            ((price - median) * 10000) / median
        } else {
            ((median - price) * 10000) / median
        }
    }

    fun sort_prices(prices: vector<u64>): vector<u64> {
        // Implementation of sorting algorithm
        prices  // Simplified
    }
}
```

### Pattern 3: Heartbeat Monitoring

```move
module secure::heartbeat_oracle {
    use sui::object::{Self, UID};
    use sui::clock::{Self, Clock};

    const E_ORACLE_DEAD: u64 = 1;
    const HEARTBEAT_INTERVAL_MS: u64 = 30_000;  // 30 seconds

    public struct HeartbeatOracle has key {
        id: UID,
        price: u64,
        last_heartbeat_ms: u64,
        is_active: bool,
    }

    /// Check oracle health before using
    public fun is_oracle_healthy(
        oracle: &HeartbeatOracle,
        clock: &Clock,
    ): bool {
        if (!oracle.is_active) {
            return false
        };
        
        let current_time = clock::timestamp_ms(clock);
        let time_since_heartbeat = current_time - oracle.last_heartbeat_ms;
        
        time_since_heartbeat <= HEARTBEAT_INTERVAL_MS
    }

    public fun get_price_if_healthy(
        oracle: &HeartbeatOracle,
        clock: &Clock,
    ): u64 {
        assert!(is_oracle_healthy(oracle, clock), E_ORACLE_DEAD);
        oracle.price
    }
}
```

## Recommended Mitigations

### 1. Always Verify Oracle Signatures

```move
// Verify the data comes from a trusted oracle
let valid = ed25519::ed25519_verify(
    &signature,
    &trusted_pubkey,
    &message
);
assert!(valid, E_INVALID_SIGNATURE);
```

### 2. Check Data Freshness

```move
// Never use stale data
let age = current_time - data_timestamp;
assert!(age <= MAX_STALENESS, E_STALE_DATA);
```

### 3. Validate Price Bounds

```move
// Sanity check price values
assert!(price >= MIN_REASONABLE_PRICE, E_PRICE_TOO_LOW);
assert!(price <= MAX_REASONABLE_PRICE, E_PRICE_TOO_HIGH);
```

### 4. Use Multiple Oracle Sources

```move
// Aggregate from multiple sources
let prices = get_prices_from_multiple_oracles();
let median = calculate_median(prices);
```

### 5. Implement Circuit Breakers

```move
// Pause on extreme price movements
let price_change = calculate_change(old_price, new_price);
if (price_change > MAX_CHANGE_THRESHOLD) {
    pause_protocol();
    emit_alert();
}
```

## Testing Checklist

- [ ] Verify signature validation cannot be bypassed
- [ ] Test with stale price data — should be rejected
- [ ] Test with prices outside bounds — should be rejected
- [ ] Test with untrusted oracle addresses — should be rejected
- [ ] Verify fallback behavior when primary oracle fails
- [ ] Test multi-oracle aggregation with malicious minority
- [ ] Verify circuit breakers trigger on extreme price movements

## Related Vulnerabilities

- [Access-Control Mistakes](../access-control-mistakes/)
- [Clock Time Misuse](../clock-time-misuse/)
- [Unsafe BCS Parsing](../unsafe-bcs-parsing/)
- [Weak Initializers](../weak-initializers/)