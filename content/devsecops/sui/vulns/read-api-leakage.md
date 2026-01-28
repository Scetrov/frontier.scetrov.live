+++
title = '28. Read API Leakage'
date = '2025-11-26T00:00:00Z'
weight = 28
+++

## Overview

Read API leakage occurs when view functions or public getters expose sensitive information that should remain private. In Sui Move, while direct state access requires ownership, public functions can inadvertently reveal private keys, internal state, user data, or security-critical information. Attackers can use this leaked information to plan attacks, front-run transactions, or compromise user privacy.

## Risk Level

**Medium to High** — Can enable attacks, compromise privacy, or reveal competitive information.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE |
 | -------------- | ----------- |
 | A01 (Broken Access Control) | CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor) |

## The Problem

### Common Read API Leakage Issues

 | Issue | Risk | Description |
 | ------- | ------ | ------------- |
 | Exposing private keys/seeds | Critical | Admin keys or secrets readable |
 | Revealing pending orders | High | Front-running opportunity |
 | Leaking user balances | Medium | Privacy violation |
 | Exposing internal thresholds | Medium | Attack planning information |
 | Revealing algorithm parameters | Medium | Gaming/manipulation enablement |

## Vulnerable Example

```move
module vulnerable::exchange {
    use sui::object::{Self, UID};
    use sui::table::{Self, Table};

    public struct Exchange has key {
        id: UID,
        /// VULNERABLE: Internal fee calculation parameters
        fee_numerator: u64,
        fee_denominator: u64,
        /// VULNERABLE: Liquidation thresholds
        liquidation_threshold_bps: u64,
        /// VULNERABLE: Oracle update key
        oracle_private_seed: vector<u8>,
        /// VULNERABLE: Pending orders visible
        pending_orders: Table<ID, Order>,
        /// VULNERABLE: User position data
        user_positions: Table<address, Position>,
    }

    public struct Order has store {
        owner: address,
        amount: u64,
        price: u64,
        order_type: u8,
        /// VULNERABLE: Stop-loss prices visible
        stop_loss: u64,
        take_profit: u64,
    }

    public struct Position has store {
        collateral: u64,
        debt: u64,
        /// VULNERABLE: Liquidation price calculable
        entry_price: u64,
    }

    /// VULNERABLE: Exposes internal fee parameters
    public fun get_fee_params(exchange: &Exchange): (u64, u64) {
        (exchange.fee_numerator, exchange.fee_denominator)
    }

    /// VULNERABLE: Reveals liquidation thresholds
    public fun get_liquidation_threshold(exchange: &Exchange): u64 {
        exchange.liquidation_threshold_bps
    }

    /// VULNERABLE: Leaks oracle seed!
    public fun get_oracle_config(exchange: &Exchange): vector<u8> {
        exchange.oracle_private_seed
    }

    /// VULNERABLE: Anyone can see pending orders
    public fun get_order(exchange: &Exchange, order_id: ID): &Order {
        table::borrow(&exchange.pending_orders, order_id)
    }

    /// VULNERABLE: Anyone can enumerate all orders
    public fun get_all_order_ids(exchange: &Exchange): vector<ID> {
        // Returns all pending order IDs - front-running goldmine
        table::keys(&exchange.pending_orders)
    }

    /// VULNERABLE: Anyone can see any user's position
    public fun get_user_position(exchange: &Exchange, user: address): &Position {
        table::borrow(&exchange.user_positions, user)
    }

    /// VULNERABLE: Reveals when user will be liquidated
    public fun get_liquidation_price(exchange: &Exchange, user: address): u64 {
        let position = table::borrow(&exchange.user_positions, user);
        // Calculation reveals exact liquidation trigger
        (position.debt * 10000) / (position.collateral * exchange.liquidation_threshold_bps)
    }
}

module vulnerable::auction {
    public struct Auction has key {
        id: UID,
        /// VULNERABLE: Reserve price visible
        reserve_price: u64,
        /// VULNERABLE: All bids visible before reveal
        bids: vector<Bid>,
    }

    public struct Bid has store {
        bidder: address,
        amount: u64,
        /// VULNERABLE: Sealed bid amount visible
        sealed_amount: u64,
    }

    /// VULNERABLE: Reserve price should be hidden
    public fun get_reserve_price(auction: &Auction): u64 {
        auction.reserve_price
    }

    /// VULNERABLE: Sealed bids exposed before reveal phase
    public fun get_all_bids(auction: &Auction): &vector<Bid> {
        &auction.bids
    }
}

module vulnerable::governance {
    public struct Proposal has key {
        id: UID,
        votes_for: u64,
        votes_against: u64,
        /// VULNERABLE: Individual votes visible
        voter_choices: Table<address, bool>,
        /// VULNERABLE: Quorum threshold visible
        quorum_threshold: u64,
    }

    /// VULNERABLE: See how anyone voted
    public fun get_vote(proposal: &Proposal, voter: address): bool {
        *table::borrow(&proposal.voter_choices, voter)
    }

    /// VULNERABLE: Calculate exactly how many votes needed
    public fun votes_until_quorum(proposal: &Proposal): u64 {
        let total = proposal.votes_for + proposal.votes_against;
        if (total >= proposal.quorum_threshold) {
            0
        } else {
            proposal.quorum_threshold - total
        }
    }
}
```

### Attack Scenarios

```move
module attack::frontrun {
    /// Attacker reads pending orders and front-runs
    public entry fun frontrun_large_order(
        exchange: &Exchange,
        order_id: ID,
        ctx: &mut TxContext
    ) {
        // Read victim's order details
        let order = vulnerable::exchange::get_order(exchange, order_id);

        // If large buy order, buy before them
        if (order.amount > 1000000 && order.order_type == BUY) {
            // Execute trade before victim's order fills
            // Sell to victim at higher price
        };
    }

    /// Attacker targets positions near liquidation
    public entry fun hunt_liquidations(
        exchange: &Exchange,
        target: address,
        ctx: &mut TxContext
    ) {
        // Read target's exact liquidation price
        let liq_price = vulnerable::exchange::get_liquidation_price(exchange, target);

        // Push price to trigger liquidation
        // Profit from liquidation bonus
    }
}
```

## Secure Example

```move
module secure::exchange {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::table::{Self, Table};
    use sui::hash;

    const E_NOT_OWNER: u64 = 1;
    const E_NOT_ADMIN: u64 = 2;

    public struct Exchange has key {
        id: UID,
        admin: address,
        /// Internal parameters - no public getters
        fee_numerator: u64,
        fee_denominator: u64,
        liquidation_threshold_bps: u64,
        /// Sensitive data not stored on-chain
        oracle_config_hash: vector<u8>,  // Only hash, not actual seed
        /// Orders indexed by owner
        user_orders: Table<address, vector<ID>>,
        order_data: Table<ID, Order>,
        user_positions: Table<address, Position>,
    }

    public struct Order has store {
        owner: address,
        /// Only store commitment, not actual values
        order_commitment: vector<u8>,  // hash(amount, price, salt)
        created_at: u64,
    }

    public struct Position has store {
        owner: address,
        collateral: u64,
        debt: u64,
        entry_price: u64,
    }

    /// SECURE: Only expose fee rate, not internal calculation params
    public fun get_effective_fee_rate(exchange: &Exchange): u64 {
        // Return calculated rate, not components
        (exchange.fee_numerator * 10000) / exchange.fee_denominator
    }

    /// SECURE: No getter for liquidation threshold
    // Liquidation logic is internal only

    /// SECURE: Oracle config hash only, no secrets
    public fun get_oracle_config_hash(exchange: &Exchange): vector<u8> {
        exchange.oracle_config_hash
    }

    /// SECURE: Only owner can view their own orders
    public fun get_my_orders(
        exchange: &Exchange,
        ctx: &TxContext
    ): vector<ID> {
        let owner = tx_context::sender(ctx);
        if (table::contains(&exchange.user_orders, owner)) {
            *table::borrow(&exchange.user_orders, owner)
        } else {
            vector::empty()
        }
    }

    /// SECURE: Only owner can view their order details
    public fun get_my_order(
        exchange: &Exchange,
        order_id: ID,
        ctx: &TxContext
    ): &Order {
        let order = table::borrow(&exchange.order_data, order_id);
        assert!(order.owner == tx_context::sender(ctx), E_NOT_OWNER);
        order
    }

    /// SECURE: Only owner can view their position
    public fun get_my_position(
        exchange: &Exchange,
        ctx: &TxContext
    ): &Position {
        let owner = tx_context::sender(ctx);
        let position = table::borrow(&exchange.user_positions, owner);
        assert!(position.owner == owner, E_NOT_OWNER);
        position
    }

    /// SECURE: Health check without revealing exact values
    public fun is_position_healthy(
        exchange: &Exchange,
        user: address
    ): bool {
        if (!table::contains(&exchange.user_positions, user)) {
            return true  // No position = healthy
        };

        let position = table::borrow(&exchange.user_positions, user);
        // Return boolean only, not the actual ratio
        let health_ratio = (position.collateral * 10000) / position.debt;
        health_ratio > exchange.liquidation_threshold_bps
    }

    /// SECURE: Admin-only access to sensitive data
    public fun admin_get_liquidation_threshold(
        exchange: &Exchange,
        ctx: &TxContext
    ): u64 {
        assert!(tx_context::sender(ctx) == exchange.admin, E_NOT_ADMIN);
        exchange.liquidation_threshold_bps
    }
}

module secure::auction {
    use sui::object::{Self, UID};
    use sui::hash;

    public struct Auction has key {
        id: UID,
        /// Reserve price stored as commitment
        reserve_price_commitment: vector<u8>,
        /// Sealed bids - only commitments visible
        bid_commitments: vector<BidCommitment>,
        /// Revealed bids (after reveal phase)
        revealed_bids: vector<RevealedBid>,
        phase: u8,  // 0=bidding, 1=reveal, 2=complete
    }

    public struct BidCommitment has store {
        bidder: address,
        commitment: vector<u8>,  // hash(amount, nonce)
        timestamp: u64,
    }

    public struct RevealedBid has store {
        bidder: address,
        amount: u64,
    }

    /// SECURE: Only commitment visible during bidding
    public fun get_bid_count(auction: &Auction): u64 {
        vector::length(&auction.bid_commitments)
    }

    /// SECURE: Actual bids only visible after reveal phase
    public fun get_revealed_bids(auction: &Auction): &vector<RevealedBid> {
        assert!(auction.phase >= 1, E_STILL_BIDDING);
        &auction.revealed_bids
    }

    /// SECURE: Reserve only revealed at end
    public fun get_reserve_price(
        auction: &Auction,
        reserve_salt: vector<u8>
    ): u64 {
        assert!(auction.phase == 2, E_NOT_COMPLETE);
        // Verify caller knows the salt (is the auctioneer)
        // Then reveal reserve
        0  // placeholder
    }
}

module secure::governance {
    use sui::object::{Self, UID};
    use sui::table::{Self, Table};

    public struct Proposal has key {
        id: UID,
        /// Only totals visible, not individual votes
        votes_for: u64,
        votes_against: u64,
        total_voters: u64,
        /// Individual votes are private
        voter_commitments: Table<address, vector<u8>>,
        /// Quorum expressed as percentage, not absolute
        quorum_percentage: u64,
        eligible_voters: u64,
    }

    /// SECURE: Only aggregate data visible
    public fun get_vote_totals(proposal: &Proposal): (u64, u64) {
        (proposal.votes_for, proposal.votes_against)
    }

    /// SECURE: No individual vote visibility
    public fun has_voted(proposal: &Proposal, voter: address): bool {
        table::contains(&proposal.voter_commitments, voter)
    }

    /// SECURE: Quorum status, not exact numbers needed
    public fun has_quorum(proposal: &Proposal): bool {
        let total = proposal.votes_for + proposal.votes_against;
        let required = (proposal.eligible_voters * proposal.quorum_percentage) / 100;
        total >= required
    }

    /// SECURE: Percentage, not absolute votes needed
    public fun get_participation_rate(proposal: &Proposal): u64 {
        let total = proposal.votes_for + proposal.votes_against;
        (total * 100) / proposal.eligible_voters
    }
}
```

## Information Exposure Patterns

### Pattern 1: Return Aggregates, Not Details

```move
// BAD: Exposes individual data
public fun get_all_balances(pool: &Pool): &Table<address, u64> {
    &pool.balances
}

// GOOD: Return aggregate only
public fun get_total_liquidity(pool: &Pool): u64 {
    pool.total_liquidity
}

public fun get_participant_count(pool: &Pool): u64 {
    table::length(&pool.balances)
}
```

### Pattern 2: Owner-Only Access

```move
/// Only the data owner can read their data
public fun get_my_data(
    registry: &Registry,
    ctx: &TxContext
): &UserData {
    let user = tx_context::sender(ctx);
    let data = table::borrow(&registry.user_data, user);
    assert!(data.owner == user, E_NOT_OWNER);
    data
}
```

### Pattern 3: Commitment Schemes

```move
/// Store commitment, not actual value
public struct HiddenValue has store {
    commitment: vector<u8>,  // hash(value, salt)
}

public fun create_commitment(value: u64, salt: vector<u8>): vector<u8> {
    let mut data = bcs::to_bytes(&value);
    vector::append(&mut data, salt);
    hash::keccak256(&data)
}

public fun verify_and_reveal(
    hidden: &HiddenValue,
    claimed_value: u64,
    salt: vector<u8>
): u64 {
    let expected = create_commitment(claimed_value, salt);
    assert!(expected == hidden.commitment, E_INVALID_REVEAL);
    claimed_value
}
```

### Pattern 4: Role-Based Access

```move
public fun admin_view_sensitive_data(
    state: &State,
    admin_cap: &AdminCap
): &SensitiveData {
    assert!(admin_cap.state_id == object::id(state), E_WRONG_CAP);
    &state.sensitive_data
}

public fun user_view_own_data(
    state: &State,
    ctx: &TxContext
): &UserData {
    let user = tx_context::sender(ctx);
    table::borrow(&state.user_data, user)
}

// No public getter for cross-user data
```

### Pattern 5: Time-Delayed Revelation

```move
public struct TimeLocked has key {
    id: UID,
    hidden_data: vector<u8>,
    reveal_time: u64,
}

public fun get_data(
    locked: &TimeLocked,
    clock: &Clock
): vector<u8> {
    assert!(clock::timestamp_ms(clock) >= locked.reveal_time, E_TOO_EARLY);
    locked.hidden_data
}
```

## Recommended Mitigations

### 1. Minimize Public Getters

```move
// Only expose what's absolutely necessary
// Ask: "Does the public need this?"
public fun get_total(): u64 { }  // OK: aggregate
// Don't expose: get_user_balance(user: address)
```

### 2. Require Ownership for User Data

```move
public fun get_my_balance(ctx: &TxContext): u64 {
    let user = tx_context::sender(ctx);
    // Return only caller's data
}
```

### 3. Use Commitments for Sensitive Values

```move
// Store hash during sensitive phase
reserve_price_commitment: vector<u8>,
// Reveal after phase ends
public fun reveal(commitment: vector<u8>, value: u64, salt: vector<u8>)
```

### 4. Return Booleans Instead of Values

```move
// BAD: Reveals exact threshold
public fun get_liquidation_threshold(): u64

// GOOD: Reveals only status
public fun is_above_threshold(user: address): bool
```

### 5. Audit All Public Functions

```move
// Review every `public fun` for information leakage
// Document what information is exposed and why
```

## Testing Checklist

- [ ] Audit all public functions for sensitive data exposure
- [ ] Verify user data requires ownership to read
- [ ] Check that internal thresholds are not exposed
- [ ] Confirm pending transactions are not enumerable
- [ ] Test that sealed/committed values stay hidden
- [ ] Verify admin-only functions check capability
- [ ] Review aggregates don't leak individual data
- [ ] Check time-locked data respects reveal time

## Related Vulnerabilities

- [Access-Control Mistakes](../access-control-mistakes/)
- [Capability Leakage](../capability-leakage/)
- [Event Design Vulnerabilities](../event-design-vulnerabilities/)
- [Dynamic Field Misuse](../dynamic-field-misuse/)
