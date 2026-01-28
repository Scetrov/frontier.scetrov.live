+++
title = '24. Transfer API Misuse'
date = '2025-11-26T21:02:54Z'
weight = 24
+++

## Overview

Transfer API misuse occurs when developers incorrectly use Sui's object transfer functions, leading to objects being sent to wrong addresses, locked permanently, or transferred with incorrect ownership semantics. Sui provides multiple transfer functions (`transfer::transfer`, `transfer::public_transfer`, `transfer::share_object`, `transfer::freeze_object`) each with specific requirements and behaviors that must be understood.

## Risk Level

**Critical** — Can result in permanent loss of assets or complete protocol failure.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control) | CWE-284 (Improper Access Control) |

## The Problem

### Common Transfer API Issues

| Issue | Risk | Description |
|-------|------|-------------|
| Using `transfer` without `store` | Critical | Compile error or runtime panic |
| Sharing owned objects incorrectly | High | Can break ownership invariants |
| Freezing mutable state | Critical | Permanently locks needed functionality |
| Transfer to wrong address | Critical | Assets sent to unrecoverable address |
| `public_transfer` vs `transfer` confusion | High | Security implications differ |

## Transfer API Quick Reference

| Function | Requires `store` | Use Case |
|----------|------------------|----------|
| `transfer::transfer` | No | Internal module transfers of objects without `store` |
| `transfer::public_transfer` | Yes | External transfers of objects with `store` |
| `transfer::share_object` | No | Making objects shared (accessible by anyone) |
| `transfer::public_share_object` | Yes | External sharing of objects with `store` |
| `transfer::freeze_object` | No | Making objects immutable |
| `transfer::public_freeze_object` | Yes | External freezing of objects with `store` |

## Vulnerable Example

```move
module vulnerable::token {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::coin::{Self, Coin};

    const E_NOT_OWNER: u64 = 1;

    /// Has `store` ability - can use public_transfer
    public struct Token has key, store {
        id: UID,
        value: u64,
    }

    /// VULNERABLE: Transfers to sender without verification
    public entry fun claim_airdrop(
        amount: u64,
        ctx: &mut TxContext
    ) {
        let token = Token {
            id: object::new(ctx),
            value: amount,
        };
        
        // Who is sender? Could be anyone, including a contract
        // that can't receive objects
        transfer::public_transfer(token, tx_context::sender(ctx));
    }

    /// VULNERABLE: Typo in address loses funds forever
    public entry fun send_to_treasury(
        token: Token,
        _ctx: &mut TxContext
    ) {
        // Hardcoded address - typo = permanent loss
        transfer::public_transfer(token, @0x1234567890abcdef);
    }

    /// VULNERABLE: Shares object that should stay owned
    public entry fun make_accessible(
        token: Token,
        _ctx: &mut TxContext
    ) {
        // Now ANYONE can access this token!
        transfer::share_object(token);
    }
}

module vulnerable::vault {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::balance::{Self, Balance};

    /// Missing `store` ability
    public struct Vault<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        owner: address,
    }

    /// VULNERABLE: Can't use public_transfer without `store`
    public entry fun transfer_vault<T>(
        vault: Vault<T>,
        new_owner: address,
        ctx: &mut TxContext
    ) {
        // This will fail! Vault doesn't have `store`
        // transfer::public_transfer(vault, new_owner);
        
        // And using transfer from outside the module won't work either
        // Only this module can call transfer::transfer on Vault
    }

    /// VULNERABLE: Freezes vault, locking funds forever
    public entry fun secure_vault<T>(
        vault: Vault<T>,
        _ctx: &mut TxContext
    ) {
        // Frozen = immutable forever = funds locked!
        transfer::freeze_object(vault);
    }
}

module vulnerable::nft {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    public struct NFT has key, store {
        id: UID,
        name: vector<u8>,
    }

    public struct NFTCollection has key {
        id: UID,
        nfts: vector<NFT>,  // Owned NFTs inside collection
    }

    /// VULNERABLE: Shares collection, exposing all NFTs
    public entry fun publish_collection(
        collection: NFTCollection,
        _ctx: &mut TxContext
    ) {
        // All NFTs in the collection are now accessible!
        transfer::share_object(collection);
    }

    /// VULNERABLE: No validation of recipient
    public entry fun gift_nft(
        nft: NFT,
        recipient: address,
        _ctx: &mut TxContext
    ) {
        // What if recipient is @0x0?
        // What if recipient is a module address that can't hold objects?
        transfer::public_transfer(nft, recipient);
    }
}
```

### Attack Scenario

```move
module attack::steal_shared {
    use vulnerable::token::{Self, Token};
    use sui::tx_context::TxContext;

    /// After token is incorrectly shared, anyone can take it
    public entry fun steal_shared_token(
        token: &mut Token,  // Shared object = mutable by anyone
        ctx: &mut TxContext
    ) {
        // Attacker can now manipulate the token
        // that was accidentally shared
    }
}
```

## Secure Example

```move
module secure::token {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::event;

    const E_ZERO_ADDRESS: u64 = 1;
    const E_SELF_TRANSFER: u64 = 2;
    const E_NOT_OWNER: u64 = 3;

    public struct Token has key, store {
        id: UID,
        value: u64,
        original_owner: address,
    }

    public struct TokenTransferred has copy, drop {
        token_id: ID,
        from: address,
        to: address,
    }

    /// SECURE: Validates recipient before transfer
    public entry fun safe_transfer(
        token: Token,
        recipient: address,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        // Validate recipient
        assert!(recipient != @0x0, E_ZERO_ADDRESS);
        assert!(recipient != sender, E_SELF_TRANSFER);
        
        let token_id = object::id(&token);
        
        // Emit event for tracking
        event::emit(TokenTransferred {
            token_id,
            from: sender,
            to: recipient,
        });
        
        transfer::public_transfer(token, recipient);
    }

    /// SECURE: Treasury address as a verified constant
    const TREASURY: address = @0xTREASURY_ADDRESS_HERE;

    public entry fun send_to_treasury(
        token: Token,
        ctx: &mut TxContext
    ) {
        let token_id = object::id(&token);
        let sender = tx_context::sender(ctx);
        
        event::emit(TokenTransferred {
            token_id,
            from: sender,
            to: TREASURY,
        });
        
        transfer::public_transfer(token, TREASURY);
    }
}

module secure::vault {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};

    const E_NOT_OWNER: u64 = 1;
    const E_ZERO_ADDRESS: u64 = 2;
    const E_HAS_BALANCE: u64 = 3;

    /// Note: No `store` - transfers controlled by this module only
    public struct Vault<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        owner: address,
    }

    /// SECURE: Module-controlled transfer with validation
    public entry fun transfer_vault<T>(
        vault: Vault<T>,
        new_owner: address,
        ctx: &mut TxContext
    ) {
        // Verify current ownership
        assert!(vault.owner == tx_context::sender(ctx), E_NOT_OWNER);
        
        // Validate new owner
        assert!(new_owner != @0x0, E_ZERO_ADDRESS);
        
        // Update internal owner tracking
        let Vault { id, balance, owner: _ } = vault;
        
        let new_vault = Vault {
            id,
            balance,
            owner: new_owner,
        };
        
        // Use transfer (not public_transfer) since no `store`
        transfer::transfer(new_vault, new_owner);
    }

    /// SECURE: Withdraw before destroying, never freeze with balance
    public entry fun close_vault<T>(
        vault: Vault<T>,
        ctx: &mut TxContext
    ) {
        assert!(vault.owner == tx_context::sender(ctx), E_NOT_OWNER);
        
        let Vault { id, balance, owner } = vault;
        
        // Return any remaining balance to owner
        if (balance::value(&balance) > 0) {
            let coins = coin::from_balance(balance, ctx);
            transfer::public_transfer(coins, owner);
        } else {
            balance::destroy_zero(balance);
        };
        
        object::delete(id);
        
        // Vault is properly destroyed, not frozen with funds
    }
}

module secure::nft {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::dynamic_object_field as dof;

    const E_NOT_OWNER: u64 = 1;
    const E_ZERO_ADDRESS: u64 = 2;

    public struct NFT has key, store {
        id: UID,
        name: vector<u8>,
        creator: address,
    }

    /// Collection owns NFTs via dynamic fields, not vector
    public struct NFTCollection has key {
        id: UID,
        owner: address,
        nft_count: u64,
    }

    /// SECURE: Share collection but NFTs remain owned separately
    public entry fun create_collection(
        ctx: &mut TxContext
    ) {
        let collection = NFTCollection {
            id: object::new(ctx),
            owner: tx_context::sender(ctx),
            nft_count: 0,
        };
        
        // Sharing collection is safe - it only contains metadata
        // Individual NFTs are transferred separately
        transfer::share_object(collection);
    }

    /// SECURE: Add NFT to collection as dynamic field
    public entry fun add_to_collection(
        collection: &mut NFTCollection,
        nft: NFT,
        ctx: &mut TxContext
    ) {
        assert!(collection.owner == tx_context::sender(ctx), E_NOT_OWNER);
        
        let nft_id = object::id(&nft);
        dof::add(&mut collection.id, nft_id, nft);
        collection.nft_count = collection.nft_count + 1;
    }

    /// SECURE: Validated gift with proper checks
    public entry fun gift_nft(
        nft: NFT,
        recipient: address,
        ctx: &mut TxContext
    ) {
        // Validate recipient
        assert!(recipient != @0x0, E_ZERO_ADDRESS);
        
        // Additional validation could include:
        // - Checking recipient is not a known module address
        // - Requiring recipient acknowledgment via separate flow
        
        transfer::public_transfer(nft, recipient);
    }
}
```

## Transfer Pattern Guidelines

### Pattern 1: Choosing the Right Transfer Function

```move
/// Object WITHOUT store - use transfer (module-only)
public struct InternalAsset has key {
    id: UID,
}

/// Object WITH store - can use public_transfer
public struct TransferableAsset has key, store {
    id: UID,
}

/// Correct usage:
fun transfer_internal(asset: InternalAsset, recipient: address) {
    // Only callable from within this module
    transfer::transfer(asset, recipient);
}

public entry fun transfer_external(asset: TransferableAsset, recipient: address) {
    // Callable from PTBs or other modules
    transfer::public_transfer(asset, recipient);
}
```

### Pattern 2: Safe Sharing Decisions

```move
/// SAFE to share: Configuration/registry with no sensitive data
public struct PublicRegistry has key {
    id: UID,
    entries: Table<ID, RegistryEntry>,
}

/// UNSAFE to share: Objects containing value or authority
public struct Vault has key {
    id: UID,
    balance: Balance<SUI>,  // Don't share!
}

/// When in doubt, keep objects owned
public fun should_share(obj_type: &str): bool {
    // Share: registries, oracles, public state
    // Don't share: vaults, tokens, capabilities, user assets
    false  // Default to not sharing
}
```

### Pattern 3: Freeze vs Delete

```move
/// Use freeze for truly immutable data
public struct ImmutableMetadata has key {
    id: UID,
    name: vector<u8>,
    image_url: vector<u8>,
    // No balance, no mutable state
}

public entry fun publish_metadata(
    metadata: ImmutableMetadata,
    _ctx: &mut TxContext
) {
    // Safe to freeze - no funds, metadata is permanent
    transfer::freeze_object(metadata);
}

/// Use delete for objects with value
public entry fun close_account(
    vault: Vault,
    ctx: &mut TxContext
) {
    // Withdraw value first, then delete
    let Vault { id, balance } = vault;
    let coins = coin::from_balance(balance, ctx);
    transfer::public_transfer(coins, tx_context::sender(ctx));
    object::delete(id);
    // Never freeze a vault!
}
```

### Pattern 4: Transfer with Receipts

```move
public struct TransferReceipt has key {
    id: UID,
    asset_id: ID,
    from: address,
    to: address,
    timestamp: u64,
}

public entry fun tracked_transfer(
    asset: TransferableAsset,
    recipient: address,
    clock: &Clock,
    ctx: &mut TxContext
) {
    let asset_id = object::id(&asset);
    let sender = tx_context::sender(ctx);
    
    // Create receipt before transfer
    let receipt = TransferReceipt {
        id: object::new(ctx),
        asset_id,
        from: sender,
        to: recipient,
        timestamp: clock::timestamp_ms(clock),
    };
    
    // Keep receipt with sender for records
    transfer::transfer(receipt, sender);
    
    // Transfer asset
    transfer::public_transfer(asset, recipient);
}
```

## Recommended Mitigations

### 1. Always Validate Recipients

```move
assert!(recipient != @0x0, E_ZERO_ADDRESS);
assert!(recipient != tx_context::sender(ctx), E_SELF_TRANSFER);
```

### 2. Use the Correct Transfer Function

```move
// Check if object has `store` ability
// - With store: use public_transfer
// - Without store: use transfer (module-internal only)
```

### 3. Never Freeze Objects with Value

```move
// BAD: Funds locked forever
transfer::freeze_object(vault_with_balance);

// GOOD: Withdraw first, then delete
let coins = withdraw_all(vault);
delete_vault(vault);
```

### 4. Be Intentional About Sharing

```move
// Ask: "Should anyone be able to access this?"
// If no, use transfer to specific address
// If yes, carefully consider the implications
```

### 5. Emit Events for Transfers

```move
event::emit(TransferEvent {
    object_id: object::id(&obj),
    from: sender,
    to: recipient,
});
```

## Testing Checklist

- [ ] Verify `store` ability matches transfer function used
- [ ] Test transfer to zero address is rejected
- [ ] Confirm self-transfers are handled appropriately
- [ ] Test that frozen objects don't contain value
- [ ] Verify shared objects don't expose sensitive capabilities
- [ ] Check hardcoded addresses are correct
- [ ] Test transfer events are emitted correctly
- [ ] Verify ownership updates when using internal owner fields

## Related Vulnerabilities

- [Object Transfer Misuse](../object-transfer-misuse/)
- [Object Freezing Misuse](../object-freezing-misuse/)
- [Improper Object Sharing](../improper-object-sharing/)
- [Ownership Model Confusion](../ownership-model-confusion/)
- [Ability Misconfiguration](../ability-misconfiguration/)
