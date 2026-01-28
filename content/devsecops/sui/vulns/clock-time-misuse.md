+++
title = '23. Clock Time Misuse'
date = '2025-11-26T00:00:00Z'
weight = 23
+++

## Overview

Clock time misuse occurs when smart contracts improperly use Sui's `Clock` object for time-sensitive operations. Unlike traditional blockchains where block timestamps can be manipulated by validators, Sui provides a system `Clock` object with millisecond precision. However, misusing this clock—through incorrect comparisons, time zone assumptions, or precision errors—can lead to serious vulnerabilities.

## Risk Level

**High** — Can lead to premature unlocks, expired deadlines being bypassed, or time-locked funds becoming inaccessible.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A04 (Insecure Design) | CWE-682 (Incorrect Calculation), CWE-664 (Improper Control of a Resource Through its Lifetime) |

## The Problem

### Common Clock Misuse Issues

| Issue | Risk | Description |
|-------|------|-------------|
| Seconds vs milliseconds | Critical | Sui Clock uses milliseconds, not seconds |
| Off-by-one in comparisons | High | `<` vs `<=` can lock or unlock prematurely |
| No clock validation | Medium | Accepting arbitrary clock objects |
| Hardcoded timestamps | High | Timestamps that don't account for network delays |
| Integer overflow in time math | Medium | Adding durations to timestamps unsafely |

## Vulnerable Example

```move
module vulnerable::timelock {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::clock::{Self, Clock};

    const E_TOO_EARLY: u64 = 1;
    const E_EXPIRED: u64 = 2;

    public struct TimeLock<phantom T> has key {
        id: UID,
        coins: Coin<T>,
        beneficiary: address,
        /// VULNERABLE: Stored in seconds, but Clock uses milliseconds!
        unlock_time: u64,
    }

    /// VULNERABLE: Mixes seconds and milliseconds
    public entry fun create_lock<T>(
        coins: Coin<T>,
        beneficiary: address,
        unlock_delay_seconds: u64,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // BUG: clock::timestamp_ms returns milliseconds
        // but we're adding seconds!
        let unlock_time = clock::timestamp_ms(clock) + unlock_delay_seconds;
        
        let lock = TimeLock {
            id: object::new(ctx),
            coins,
            beneficiary,
            unlock_time,  // This is way too soon!
        };
        
        transfer::share_object(lock);
    }

    /// VULNERABLE: Wrong comparison operator
    public entry fun claim<T>(
        lock: TimeLock<T>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let TimeLock { id, coins, beneficiary, unlock_time } = lock;
        
        // BUG: Should be >=, using > means you can't claim AT unlock_time
        assert!(clock::timestamp_ms(clock) > unlock_time, E_TOO_EARLY);
        
        object::delete(id);
        transfer::public_transfer(coins, beneficiary);
    }
}

module vulnerable::auction {
    use sui::clock::{Self, Clock};

    const E_AUCTION_ENDED: u64 = 1;
    const E_AUCTION_NOT_ENDED: u64 = 2;

    public struct Auction has key {
        id: UID,
        /// VULNERABLE: No validation this is a reasonable time
        end_time: u64,
        highest_bid: u64,
        highest_bidder: address,
    }

    /// VULNERABLE: Accepts any clock object
    public entry fun place_bid(
        auction: &mut Auction,
        clock: &Clock,  // What if this isn't the system clock?
        bid_amount: u64,
        ctx: &mut TxContext
    ) {
        // No validation that clock is 0x6 (system clock)
        assert!(clock::timestamp_ms(clock) < auction.end_time, E_AUCTION_ENDED);
        
        // Process bid...
    }

    /// VULNERABLE: Race condition at exact end time
    public entry fun finalize(
        auction: &mut Auction,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // What happens if current_time == end_time?
        // Both place_bid and finalize could succeed in same ms
        assert!(clock::timestamp_ms(clock) >= auction.end_time, E_AUCTION_NOT_ENDED);
        
        // Finalize auction...
    }
}

module vulnerable::vesting {
    use sui::clock::{Self, Clock};

    public struct VestingSchedule has key {
        id: UID,
        total_amount: u64,
        claimed_amount: u64,
        start_time: u64,
        /// VULNERABLE: Overflow possible
        duration_ms: u64,
    }

    /// VULNERABLE: Integer overflow in time calculation
    public fun calculate_vested(
        schedule: &VestingSchedule,
        clock: &Clock
    ): u64 {
        let current_time = clock::timestamp_ms(clock);
        
        // BUG: What if start_time + duration_ms overflows?
        let end_time = schedule.start_time + schedule.duration_ms;
        
        if (current_time >= end_time) {
            return schedule.total_amount
        };
        
        // BUG: What if current_time < start_time? Underflow!
        let elapsed = current_time - schedule.start_time;
        
        // BUG: Multiplication can overflow
        (schedule.total_amount * elapsed) / schedule.duration_ms
    }
}
```

### Attack Scenario

```move
module attack::time_exploit {
    use vulnerable::timelock;
    use sui::clock::Clock;

    /// Exploit: Lock meant for 1 year unlocks in ~16 minutes
    public entry fun exploit_timelock(ctx: &mut TxContext) {
        // User creates lock with 31536000 "seconds" (1 year)
        // But code adds this to milliseconds!
        // 31536000ms = ~8.76 hours, not 1 year
        // 
        // Even worse: if they use 86400 for "1 day"
        // That's only 86.4 seconds in the vulnerable code
    }
}
```

## Secure Example

```move
module secure::timelock {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::clock::{Self, Clock};

    const E_TOO_EARLY: u64 = 1;
    const E_INVALID_DURATION: u64 = 2;
    const E_OVERFLOW: u64 = 3;

    /// Constants clearly named with units
    const MS_PER_SECOND: u64 = 1_000;
    const MS_PER_MINUTE: u64 = 60_000;
    const MS_PER_HOUR: u64 = 3_600_000;
    const MS_PER_DAY: u64 = 86_400_000;
    
    const MIN_LOCK_DURATION_MS: u64 = 60_000;  // 1 minute minimum
    const MAX_LOCK_DURATION_MS: u64 = 31_536_000_000;  // ~1 year maximum
    const MAX_TIMESTAMP: u64 = 253_402_300_799_999;  // Year 9999

    public struct TimeLock<phantom T> has key {
        id: UID,
        coins: Coin<T>,
        beneficiary: address,
        unlock_time_ms: u64,  // Clear naming: this is milliseconds
        created_at_ms: u64,
    }

    /// SECURE: Explicit millisecond conversion with validation
    public entry fun create_lock<T>(
        coins: Coin<T>,
        beneficiary: address,
        duration_seconds: u64,  // Accept seconds from user (more intuitive)
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // Convert seconds to milliseconds explicitly
        let duration_ms = checked_mul(duration_seconds, MS_PER_SECOND);
        
        // Validate duration bounds
        assert!(duration_ms >= MIN_LOCK_DURATION_MS, E_INVALID_DURATION);
        assert!(duration_ms <= MAX_LOCK_DURATION_MS, E_INVALID_DURATION);
        
        let current_time_ms = clock::timestamp_ms(clock);
        
        // Safe addition with overflow check
        let unlock_time_ms = checked_add(current_time_ms, duration_ms);
        assert!(unlock_time_ms <= MAX_TIMESTAMP, E_OVERFLOW);
        
        let lock = TimeLock {
            id: object::new(ctx),
            coins,
            beneficiary,
            unlock_time_ms,
            created_at_ms: current_time_ms,
        };
        
        transfer::share_object(lock);
    }

    /// SECURE: Correct comparison with clear semantics
    public entry fun claim<T>(
        lock: TimeLock<T>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let TimeLock { 
            id, 
            coins, 
            beneficiary, 
            unlock_time_ms,
            created_at_ms: _,
        } = lock;
        
        let current_time_ms = clock::timestamp_ms(clock);
        
        // >= means claimable at or after unlock time
        assert!(current_time_ms >= unlock_time_ms, E_TOO_EARLY);
        
        // Verify sender is beneficiary
        assert!(tx_context::sender(ctx) == beneficiary, E_NOT_BENEFICIARY);
        
        object::delete(id);
        transfer::public_transfer(coins, beneficiary);
    }

    /// Safe multiplication with overflow check
    fun checked_mul(a: u64, b: u64): u64 {
        if (a == 0 || b == 0) {
            return 0
        };
        let result = a * b;
        assert!(result / a == b, E_OVERFLOW);
        result
    }

    /// Safe addition with overflow check
    fun checked_add(a: u64, b: u64): u64 {
        let result = a + b;
        assert!(result >= a, E_OVERFLOW);
        result
    }
}

module secure::auction {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::clock::{Self, Clock};

    const E_AUCTION_ENDED: u64 = 1;
    const E_AUCTION_NOT_ENDED: u64 = 2;
    const E_BID_TOO_LOW: u64 = 3;
    const E_INVALID_DURATION: u64 = 4;

    const CLOCK_OBJECT_ID: address = @0x6;
    const MIN_AUCTION_DURATION_MS: u64 = 3_600_000;  // 1 hour
    const EXTENSION_THRESHOLD_MS: u64 = 300_000;  // 5 minutes
    const EXTENSION_DURATION_MS: u64 = 300_000;  // 5 minutes

    public struct Auction has key {
        id: UID,
        end_time_ms: u64,
        highest_bid: u64,
        highest_bidder: address,
        finalized: bool,
    }

    /// SECURE: Clear time boundaries with anti-sniping
    public entry fun place_bid(
        auction: &mut Auction,
        clock: &Clock,
        bid_amount: u64,
        ctx: &mut TxContext
    ) {
        let current_time_ms = clock::timestamp_ms(clock);
        
        // Strict less-than: auction is open until end_time, not at end_time
        assert!(current_time_ms < auction.end_time_ms, E_AUCTION_ENDED);
        assert!(!auction.finalized, E_AUCTION_ENDED);
        assert!(bid_amount > auction.highest_bid, E_BID_TOO_LOW);
        
        auction.highest_bid = bid_amount;
        auction.highest_bidder = tx_context::sender(ctx);
        
        // Anti-sniping: extend if bid near end
        let time_remaining = auction.end_time_ms - current_time_ms;
        if (time_remaining < EXTENSION_THRESHOLD_MS) {
            auction.end_time_ms = current_time_ms + EXTENSION_DURATION_MS;
        };
    }

    /// SECURE: No race condition with bidding
    public entry fun finalize(
        auction: &mut Auction,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let current_time_ms = clock::timestamp_ms(clock);
        
        // Strict greater-than: can only finalize AFTER end_time
        // This ensures no overlap with place_bid
        assert!(current_time_ms > auction.end_time_ms, E_AUCTION_NOT_ENDED);
        assert!(!auction.finalized, E_AUCTION_ENDED);
        
        auction.finalized = true;
        
        // Process winner...
    }
}

module secure::vesting {
    use sui::object::{Self, UID};
    use sui::clock::{Self, Clock};

    const E_OVERFLOW: u64 = 1;
    const E_NOT_STARTED: u64 = 2;

    public struct VestingSchedule has key {
        id: UID,
        total_amount: u64,
        claimed_amount: u64,
        start_time_ms: u64,
        end_time_ms: u64,  // Pre-calculated, no runtime overflow
        cliff_time_ms: u64,
    }

    /// SECURE: Pre-calculate end time at creation
    public fun create_schedule(
        total_amount: u64,
        start_time_ms: u64,
        duration_ms: u64,
        cliff_duration_ms: u64,
        ctx: &mut TxContext
    ): VestingSchedule {
        // Validate and calculate at creation time
        let end_time_ms = checked_add(start_time_ms, duration_ms);
        let cliff_time_ms = checked_add(start_time_ms, cliff_duration_ms);
        
        assert!(cliff_time_ms <= end_time_ms, E_INVALID_SCHEDULE);
        
        VestingSchedule {
            id: object::new(ctx),
            total_amount,
            claimed_amount: 0,
            start_time_ms,
            end_time_ms,
            cliff_time_ms,
        }
    }

    /// SECURE: Safe vesting calculation
    public fun calculate_vested(
        schedule: &VestingSchedule,
        clock: &Clock
    ): u64 {
        let current_time_ms = clock::timestamp_ms(clock);
        
        // Before start: nothing vested
        if (current_time_ms < schedule.start_time_ms) {
            return 0
        };
        
        // Before cliff: nothing claimable
        if (current_time_ms < schedule.cliff_time_ms) {
            return 0
        };
        
        // After end: everything vested
        if (current_time_ms >= schedule.end_time_ms) {
            return schedule.total_amount
        };
        
        // Linear vesting between start and end
        let elapsed = current_time_ms - schedule.start_time_ms;
        let total_duration = schedule.end_time_ms - schedule.start_time_ms;
        
        // Use u128 for intermediate calculation to prevent overflow
        let vested = ((schedule.total_amount as u128) * (elapsed as u128) 
                      / (total_duration as u128)) as u64;
        
        vested
    }

    /// SECURE: Claimable amount accounts for already claimed
    public fun calculate_claimable(
        schedule: &VestingSchedule,
        clock: &Clock
    ): u64 {
        let vested = calculate_vested(schedule, clock);
        if (vested > schedule.claimed_amount) {
            vested - schedule.claimed_amount
        } else {
            0
        }
    }
}
```

## Time Handling Patterns

### Pattern 1: Explicit Time Unit Constants

```move
module time_utils {
    // Always define constants with clear units
    const MS_PER_SECOND: u64 = 1_000;
    const MS_PER_MINUTE: u64 = 60_000;
    const MS_PER_HOUR: u64 = 3_600_000;
    const MS_PER_DAY: u64 = 86_400_000;
    const MS_PER_WEEK: u64 = 604_800_000;
    
    public fun seconds_to_ms(seconds: u64): u64 {
        seconds * MS_PER_SECOND
    }
    
    public fun days_to_ms(days: u64): u64 {
        days * MS_PER_DAY
    }
}
```

### Pattern 2: Time Window Validation

```move
/// Ensure time windows don't overlap and are valid
public fun validate_time_window(
    start_ms: u64,
    end_ms: u64,
    clock: &Clock
): bool {
    let now = clock::timestamp_ms(clock);
    
    // End must be after start
    if (end_ms <= start_ms) {
        return false
    };
    
    // Start must be in reasonable future (not in past)
    if (start_ms < now) {
        return false
    };
    
    // Duration must be reasonable
    let duration = end_ms - start_ms;
    if (duration < MIN_DURATION || duration > MAX_DURATION) {
        return false
    };
    
    true
}
```

### Pattern 3: Grace Periods for Time-Critical Operations

```move
const GRACE_PERIOD_MS: u64 = 60_000;  // 1 minute grace

public fun is_deadline_passed_with_grace(
    deadline_ms: u64,
    clock: &Clock
): bool {
    let current_time = clock::timestamp_ms(clock);
    // Add grace period to account for network delays
    current_time > deadline_ms + GRACE_PERIOD_MS
}
```

### Pattern 4: Cooldown Management

```move
public struct RateLimited has key {
    id: UID,
    last_action_ms: u64,
    cooldown_ms: u64,
}

public fun can_perform_action(
    state: &RateLimited,
    clock: &Clock
): bool {
    let current_time = clock::timestamp_ms(clock);
    let next_allowed = state.last_action_ms + state.cooldown_ms;
    current_time >= next_allowed
}

public fun record_action(
    state: &mut RateLimited,
    clock: &Clock
) {
    state.last_action_ms = clock::timestamp_ms(clock);
}
```

## Recommended Mitigations

### 1. Always Use Milliseconds Consistently

```move
// Sui Clock returns milliseconds - be consistent
let current_ms = clock::timestamp_ms(clock);
let deadline_ms = current_ms + (duration_seconds * 1000);
```

### 2. Use Clear Naming Conventions

```move
// Good: suffix indicates unit
unlock_time_ms: u64,
duration_seconds: u64,
cooldown_hours: u64,

// Bad: ambiguous
unlock_time: u64,
duration: u64,
```

### 3. Validate Time Bounds

```move
// Check for reasonable values
assert!(duration_ms >= MIN_DURATION, E_TOO_SHORT);
assert!(duration_ms <= MAX_DURATION, E_TOO_LONG);
assert!(deadline_ms > current_time, E_IN_PAST);
```

### 4. Use Safe Arithmetic for Time Calculations

```move
// Use u128 for intermediate calculations
let result = ((amount as u128) * (elapsed as u128) / (total as u128)) as u64;

// Or use explicit overflow checks
let sum = checked_add(a, b);
```

### 5. Define Clear Boundary Semantics

```move
// Document whether boundaries are inclusive or exclusive
// start_time: inclusive (>= start means active)
// end_time: exclusive (< end means active, >= end means ended)
```

## Testing Checklist

- [ ] Verify all time values use milliseconds consistently
- [ ] Test boundary conditions (exactly at start/end times)
- [ ] Check for integer overflow in time arithmetic
- [ ] Test with timestamps far in the future
- [ ] Verify underflow protection when subtracting times
- [ ] Test cooldown periods reset correctly
- [ ] Confirm grace periods work as intended
- [ ] Test time-based state transitions at boundaries

## Related Vulnerabilities

- [Oracle Validation Failures](../oracle-validation-failures/)
- [Numeric / Bitwise Pitfalls](../numeric-bitwise-pitfalls/)
- [PTB Ordering Issues](../ptb-ordering-issues/)
- [General Move Logic Errors](../general-move-logic-errors/)
