+++
title = '32. Inefficient PTB Composition'
date = '2025-11-26T00:00:00Z'
weight = 32
+++

## Overview

Inefficient PTB (Programmable Transaction Block) composition occurs when transactions are structured in ways that waste gas, hit execution limits, or create unnecessary complexity. Sui's PTB model allows composing multiple operations in a single transaction, but poor composition can lead to gas exhaustion attacks, failed transactions, or denial of service through resource exhaustion.

## Risk Level

**Medium to High** — Can lead to gas exhaustion, transaction failures, or denial of service.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A05 (Security Misconfiguration) / A06 (Vulnerable and Outdated Components) | CWE-400 (Uncontrolled Resource Consumption) |

## The Problem

### Common PTB Inefficiencies

| Issue | Risk | Description |
|-------|------|-------------|
| Too many commands | High | Exceeds PTB command limit |
| Redundant object reads | Medium | Reading same object multiple times |
| Unbounded loops in PTB | High | Gas exhaustion from large iterations |
| Inefficient coin operations | Medium | Unnecessary splits and merges |
| Sequential instead of parallel | Medium | Missing optimization opportunities |

## Sui PTB Limits

```
PTB Constraints:
- Max 1024 commands per PTB
- Max 2048 inputs per PTB
- Max gas budget (network configured)
- Max object size (network configured)
- Execution time limits
```

## Vulnerable Example

```move
module vulnerable::batch {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};

    /// VULNERABLE: Forces many separate transactions
    public entry fun process_single(
        item: &mut Item,
        ctx: &mut TxContext
    ) {
        // Each call is a separate command
        // Processing 1000 items = 1000 commands
        item.processed = true;
        item.processed_by = tx_context::sender(ctx);
    }

    /// VULNERABLE: Inefficient coin handling
    public entry fun pay_many(
        payment: Coin<SUI>,
        recipient1: address,
        recipient2: address,
        recipient3: address,
        amount1: u64,
        amount2: u64,
        amount3: u64,
        ctx: &mut TxContext
    ) {
        // Creates many intermediate coins
        let coin1 = coin::split(&mut payment, amount1, ctx);
        transfer::public_transfer(coin1, recipient1);
        
        let coin2 = coin::split(&mut payment, amount2, ctx);
        transfer::public_transfer(coin2, recipient2);
        
        let coin3 = coin::split(&mut payment, amount3, ctx);
        transfer::public_transfer(coin3, recipient3);
        
        // Return remainder
        transfer::public_transfer(payment, tx_context::sender(ctx));
    }
}

module vulnerable::registry {
    /// VULNERABLE: O(n) lookup for each operation
    public entry fun register_batch(
        registry: &mut Registry,
        names: vector<vector<u8>>,
        values: vector<u64>,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&names);
        let mut i = 0;
        
        while (i < len) {
            let name = vector::pop_back(&mut names);
            let value = vector::pop_back(&mut values);
            
            // VULNERABLE: Each add might trigger O(n) operations
            // if registry uses a vector internally
            add_to_registry(registry, name, value);
            
            i = i + 1;
        };
    }
}

module vulnerable::airdrop {
    /// VULNERABLE: Unbounded batch size
    public entry fun airdrop_tokens<T>(
        treasury_cap: &mut TreasuryCap<T>,
        recipients: vector<address>,
        amounts: vector<u64>,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&recipients);
        // No limit check - could be millions of recipients!
        
        let mut i = 0;
        while (i < len) {
            let recipient = *vector::borrow(&recipients, i);
            let amount = *vector::borrow(&amounts, i);
            
            // Each mint + transfer is expensive
            let coins = coin::mint(treasury_cap, amount, ctx);
            transfer::public_transfer(coins, recipient);
            
            i = i + 1;
        };
    }
}
```

### Inefficient PTB Construction (Off-Chain)

```typescript
// VULNERABLE: Inefficient PTB construction
async function inefficientBatchTransfer(
    client: SuiClient,
    items: {recipient: string, amount: bigint}[]
) {
    const tx = new Transaction();
    
    // VULNERABLE: Creates coin for each transfer separately
    for (const item of items) {
        // Each iteration adds multiple commands
        const [coin] = tx.splitCoins(tx.gas, [tx.pure.u64(item.amount)]);
        tx.transferObjects([coin], tx.pure.address(item.recipient));
    }
    
    // Could exceed 1024 command limit with ~500 transfers
    // Each transfer = ~2 commands (split + transfer)
    
    return client.signAndExecuteTransaction({ transaction: tx, signer });
}

// VULNERABLE: Reading same object multiple times
async function redundantReads(client: SuiClient, poolId: string) {
    const tx = new Transaction();
    
    // Reading pool in each command - wasteful
    tx.moveCall({
        target: `${PACKAGE}::pool::get_balance`,
        arguments: [tx.object(poolId)],  // Read 1
    });
    
    tx.moveCall({
        target: `${PACKAGE}::pool::get_fee`,
        arguments: [tx.object(poolId)],  // Read 2 - same object!
    });
    
    tx.moveCall({
        target: `${PACKAGE}::pool::get_volume`,
        arguments: [tx.object(poolId)],  // Read 3 - same object!
    });
}
```

## Secure Example

```move
module secure::batch {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};
    use sui::pay;

    const E_BATCH_TOO_LARGE: u64 = 1;
    const E_LENGTH_MISMATCH: u64 = 2;

    const MAX_BATCH_SIZE: u64 = 100;

    /// SECURE: Batch processing with limits
    public entry fun process_batch(
        items: vector<Item>,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&items);
        
        // SECURE: Enforce batch size limit
        assert!(len <= MAX_BATCH_SIZE, E_BATCH_TOO_LARGE);
        
        let sender = tx_context::sender(ctx);
        
        while (!vector::is_empty(&items)) {
            let mut item = vector::pop_back(&mut items);
            item.processed = true;
            item.processed_by = sender;
            transfer::public_transfer(item, sender);
        };
    }

    /// SECURE: Efficient multi-recipient payment
    public entry fun pay_many_efficient(
        coins: vector<Coin<SUI>>,
        recipients: vector<address>,
        amounts: vector<u64>,
        ctx: &mut TxContext
    ) {
        let num_recipients = vector::length(&recipients);
        assert!(num_recipients == vector::length(&amounts), E_LENGTH_MISMATCH);
        assert!(num_recipients <= MAX_BATCH_SIZE, E_BATCH_TOO_LARGE);
        
        // SECURE: Use pay module for efficient splitting
        pay::split_vec_and_transfer(&mut coins, amounts, recipients, ctx);
        
        // Return any remaining coins to sender
        while (!vector::is_empty(&coins)) {
            let coin = vector::pop_back(&mut coins);
            transfer::public_transfer(coin, tx_context::sender(ctx));
        };
        vector::destroy_empty(coins);
    }
}

module secure::registry {
    use sui::table::{Self, Table};

    const E_BATCH_TOO_LARGE: u64 = 1;
    const E_LENGTH_MISMATCH: u64 = 2;

    const MAX_BATCH_SIZE: u64 = 100;

    public struct Registry has key {
        id: UID,
        /// SECURE: O(1) lookups with Table
        entries: Table<vector<u8>, Entry>,
        entry_count: u64,
    }

    public struct Entry has store {
        value: u64,
        registered_by: address,
        registered_at: u64,
    }

    /// SECURE: Bounded batch with O(1) operations
    public entry fun register_batch(
        registry: &mut Registry,
        names: vector<vector<u8>>,
        values: vector<u64>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&names);
        
        // SECURE: Enforce batch limits
        assert!(len <= MAX_BATCH_SIZE, E_BATCH_TOO_LARGE);
        assert!(len == vector::length(&values), E_LENGTH_MISMATCH);
        
        let sender = tx_context::sender(ctx);
        let now = clock::timestamp_ms(clock);
        
        let mut i = 0;
        while (i < len) {
            let name = *vector::borrow(&names, i);
            let value = *vector::borrow(&values, i);
            
            // SECURE: O(1) table operations
            if (!table::contains(&registry.entries, name)) {
                table::add(&mut registry.entries, name, Entry {
                    value,
                    registered_by: sender,
                    registered_at: now,
                });
                registry.entry_count = registry.entry_count + 1;
            };
            
            i = i + 1;
        };
    }
}

module secure::airdrop {
    use sui::coin::{Self, Coin, TreasuryCap};
    use sui::balance::{Self, Balance};

    const E_BATCH_TOO_LARGE: u64 = 1;
    const E_LENGTH_MISMATCH: u64 = 2;
    const E_INSUFFICIENT_BALANCE: u64 = 3;

    const MAX_AIRDROP_BATCH: u64 = 50;  // Conservative limit

    /// SECURE: Bounded airdrop with pre-validation
    public entry fun airdrop_tokens<T>(
        treasury_cap: &mut TreasuryCap<T>,
        recipients: vector<address>,
        amounts: vector<u64>,
        ctx: &mut TxContext
    ) {
        let len = vector::length(&recipients);
        
        // SECURE: Strict batch limits
        assert!(len <= MAX_AIRDROP_BATCH, E_BATCH_TOO_LARGE);
        assert!(len == vector::length(&amounts), E_LENGTH_MISMATCH);
        
        // Pre-calculate total to mint once
        let mut total = 0u64;
        let mut i = 0;
        while (i < len) {
            total = total + *vector::borrow(&amounts, i);
            i = i + 1;
        };
        
        // SECURE: Single mint, then split
        let mut minted = coin::mint(treasury_cap, total, ctx);
        
        i = 0;
        while (i < len) {
            let recipient = *vector::borrow(&recipients, i);
            let amount = *vector::borrow(&amounts, i);
            
            let payment = coin::split(&mut minted, amount, ctx);
            transfer::public_transfer(payment, recipient);
            
            i = i + 1;
        };
        
        // Destroy zero coin or return remainder
        if (coin::value(&minted) == 0) {
            coin::destroy_zero(minted);
        } else {
            transfer::public_transfer(minted, tx_context::sender(ctx));
        };
    }
}
```

### Efficient PTB Construction (Off-Chain)

```typescript
import { Transaction } from '@mysten/sui/transactions';

const MAX_COMMANDS_PER_PTB = 1024;
const SAFE_BATCH_SIZE = 100;  // Leave room for overhead

// SECURE: Efficient batch transfer
async function efficientBatchTransfer(
    client: SuiClient,
    signer: Signer,
    items: {recipient: string, amount: bigint}[]
): Promise<string[]> {
    const results: string[] = [];
    
    // SECURE: Chunk into safe batch sizes
    for (let i = 0; i < items.length; i += SAFE_BATCH_SIZE) {
        const batch = items.slice(i, i + SAFE_BATCH_SIZE);
        const txDigest = await executeBatch(client, signer, batch);
        results.push(txDigest);
    }
    
    return results;
}

async function executeBatch(
    client: SuiClient,
    signer: Signer,
    items: {recipient: string, amount: bigint}[]
): Promise<string> {
    const tx = new Transaction();
    
    // SECURE: Single split for all amounts
    const amounts = items.map(item => tx.pure.u64(item.amount));
    const coins = tx.splitCoins(tx.gas, amounts);
    
    // SECURE: Batch transfer
    items.forEach((item, index) => {
        tx.transferObjects([coins[index]], tx.pure.address(item.recipient));
    });
    
    const result = await client.signAndExecuteTransaction({
        transaction: tx,
        signer,
    });
    
    return result.digest;
}

// SECURE: Reuse object references
async function efficientMultiRead(client: SuiClient, poolId: string) {
    const tx = new Transaction();
    
    // SECURE: Single object reference, multiple uses
    const pool = tx.object(poolId);
    
    const balance = tx.moveCall({
        target: `${PACKAGE}::pool::get_balance`,
        arguments: [pool],  // Reuse reference
    });
    
    const fee = tx.moveCall({
        target: `${PACKAGE}::pool::get_fee`,
        arguments: [pool],  // Same reference
    });
    
    const volume = tx.moveCall({
        target: `${PACKAGE}::pool::get_volume`,
        arguments: [pool],  // Same reference
    });
    
    return { tx, results: [balance, fee, volume] };
}

// SECURE: Parallel execution where possible
async function parallelOperations(client: SuiClient) {
    const tx = new Transaction();
    
    // These operations are independent - can be parallelized
    const results = await Promise.all([
        tx.moveCall({ target: `${PACKAGE}::a::operation1`, arguments: [] }),
        tx.moveCall({ target: `${PACKAGE}::b::operation2`, arguments: [] }),
        tx.moveCall({ target: `${PACKAGE}::c::operation3`, arguments: [] }),
    ]);
    
    // Dependent operations must be sequential
    const combined = tx.moveCall({
        target: `${PACKAGE}::d::combine`,
        arguments: results,
    });
    
    return tx;
}
```

## PTB Optimization Patterns

### Pattern 1: Batch Size Limits

```move
const MAX_BATCH_SIZE: u64 = 100;

public entry fun batch_operation(
    items: vector<Item>,
    ctx: &mut TxContext
) {
    assert!(vector::length(&items) <= MAX_BATCH_SIZE, E_BATCH_TOO_LARGE);
    // Process batch
}
```

### Pattern 2: Single Mint, Multiple Splits

```move
// Instead of minting many times:
// ❌ for each recipient: mint(amount)

// Mint total once, then split:
// ✅ mint(total), then split for each recipient
let total_coins = coin::mint(cap, total_amount, ctx);
// Split and distribute
```

### Pattern 3: Pre-Aggregation

```move
/// Aggregate data before sending to reduce commands
public struct BatchPayment has drop {
    recipients: vector<address>,
    amounts: vector<u64>,
    total: u64,
}

public fun create_batch(): BatchPayment {
    BatchPayment {
        recipients: vector::empty(),
        amounts: vector::empty(),
        total: 0,
    }
}

public fun add_payment(batch: &mut BatchPayment, recipient: address, amount: u64) {
    vector::push_back(&mut batch.recipients, recipient);
    vector::push_back(&mut batch.amounts, amount);
    batch.total = batch.total + amount;
}

public fun execute_batch(batch: BatchPayment, coins: Coin<SUI>, ctx: &mut TxContext) {
    // Single execution with pre-calculated total
}
```

### Pattern 4: Chunked Processing

```typescript
// Process large operations in chunks
async function processLargeDataset(
    client: SuiClient,
    signer: Signer,
    items: Item[]
): Promise<void> {
    const CHUNK_SIZE = 50;
    
    for (let i = 0; i < items.length; i += CHUNK_SIZE) {
        const chunk = items.slice(i, i + CHUNK_SIZE);
        
        const tx = new Transaction();
        tx.moveCall({
            target: `${PACKAGE}::processor::process_batch`,
            arguments: [tx.pure(bcs.vector(ItemType).serialize(chunk))],
        });
        
        await client.signAndExecuteTransaction({ transaction: tx, signer });
        
        // Optional: Add delay to avoid rate limiting
        await sleep(100);
    }
}
```

## Recommended Mitigations

### 1. Enforce Batch Size Limits

```move
assert!(batch_size <= MAX_BATCH_SIZE, E_TOO_LARGE);
```

### 2. Use Efficient Data Structures

```move
// Use Table instead of vector for O(1) operations
entries: Table<K, V>,
```

### 3. Pre-Calculate Totals

```move
// Calculate once, execute once
let total = calculate_total(&amounts);
let coins = mint_once(total);
// Then distribute
```

### 4. Reuse Object References

```typescript
const obj = tx.object(objectId);
// Use 'obj' in multiple calls, not tx.object() each time
```

### 5. Chunk Large Operations

```typescript
for (let i = 0; i < items.length; i += CHUNK_SIZE) {
    await processChunk(items.slice(i, i + CHUNK_SIZE));
}
```

## Testing Checklist

- [ ] Test batch operations at maximum allowed size
- [ ] Test operations that exceed limits (should fail gracefully)
- [ ] Measure gas consumption for batch operations
- [ ] Verify chunking produces correct results
- [ ] Test edge cases (empty batches, single items)
- [ ] Profile PTB command count for complex operations
- [ ] Test under high load conditions
- [ ] Verify no redundant object reads

## Related Vulnerabilities

- [Unbounded Vector Growth](../unbounded-vector-growth/)
- [Shared Object DoS](../shared-object-dos/)
- [PTB Ordering Issues](../ptb-ordering-issues/)
- [General Move Logic Errors](../general-move-logic-errors/)
