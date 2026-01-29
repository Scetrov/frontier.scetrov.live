+++
title = '34. Parent-Child Authority'
date = 2025-05-15T00:00:00+00:00
draft = false
weight = 34
+++

## Overview

**Parent-Child Authority** vulnerabilities occur when developers make incorrect assumptions about the authority relationships between parent and child objects in Sui's object model. In Sui, objects can own other objects (dynamic fields, wrapped objects), creating hierarchical relationships. Security issues arise when code assumes that access to a parent object automatically implies authorization over child objects, or conversely, when child objects can be manipulated independently in ways that violate intended invariants.

## Risk Level

**Severity**: High

**OWASP Classification**: A01:2021 – Broken Access Control

**CWE Reference**: CWE-863: Incorrect Authorization

## Vulnerable Example

```move
module game::inventory {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_object_field as dof;

    public struct Player has key {
        id: UID,
        owner: address,
        name: vector<u8>,
    }

    public struct Weapon has key, store {
        id: UID,
        name: vector<u8>,
        damage: u64,
        bound_to: Option<address>, // Intended to be soulbound
    }

    /// VULNERABLE: Assumes parent ownership implies authority
    /// But child was added independently and may have its own rules
    public fun equip_weapon(
        player: &mut Player,
        weapon: Weapon,
    ) {
        // Just adds weapon as child - no validation of weapon's bound_to
        dof::add(&mut player.id, b"weapon", weapon);
    }

    /// VULNERABLE: Anyone with player access can remove any child
    public fun unequip_weapon(
        player: &mut Player,
    ): Weapon {
        // No check if weapon should be removable
        dof::remove(&mut player.id, b"weapon")
    }

    /// VULNERABLE: Soulbound check can be bypassed via parent manipulation
    public fun transfer_weapon(
        weapon: Weapon,
        recipient: address,
    ) {
        // This check exists but can be bypassed by:
        // 1. Adding weapon to a player as child
        // 2. Transferring the player
        // 3. Removing weapon from player
        assert!(option::is_none(&weapon.bound_to), 0);
        transfer::transfer(weapon, recipient);
    }
}
```

```move
module defi::wrapped_tokens {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_field as df;
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};

    public struct Vault has key {
        id: UID,
        owner: address,
    }

    public struct LockedBalance<phantom T> has store {
        balance: Balance<T>,
        unlock_time: u64,
        original_depositor: address,
    }

    /// VULNERABLE: Lock tokens with time restriction
    public fun lock_tokens<T>(
        vault: &mut Vault,
        coin: Coin<T>,
        unlock_time: u64,
        ctx: &TxContext
    ) {
        let locked = LockedBalance {
            balance: coin::into_balance(coin),
            unlock_time,
            original_depositor: tx_context::sender(ctx),
        };

        // Add as dynamic field
        let key = tx_context::sender(ctx);
        df::add(&mut vault.id, key, locked);
    }

    /// VULNERABLE: Check is on child but parent can be transferred
    public fun unlock_tokens<T>(
        vault: &mut Vault,
        clock: &Clock,
        ctx: &mut TxContext
    ): Coin<T> {
        let sender = tx_context::sender(ctx);
        let locked: LockedBalance<T> = df::remove(&mut vault.id, sender);

        // Time check exists
        assert!(clock::timestamp_ms(clock) >= locked.unlock_time, 0);
        // Depositor check exists
        assert!(locked.original_depositor == sender, 1);

        let LockedBalance { balance, unlock_time: _, original_depositor: _ } = locked;
        coin::from_balance(balance, ctx)
    }

    /// VULNERABLE: Vault can be transferred, bypassing child restrictions
    /// New owner can access locked balances of original depositors
    public fun transfer_vault(
        vault: Vault,
        recipient: address,
    ) {
        // Children move with parent - new owner gets access
        transfer::transfer(vault, recipient);
    }
}
```

```move
module nft::collection {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_object_field as dof;
    use sui::vec_map::{Self, VecMap};

    public struct Collection has key {
        id: UID,
        creator: address,
        royalty_bps: u64,
    }

    public struct NFT has key, store {
        id: UID,
        name: vector<u8>,
        // NFT thinks it belongs to collection
        collection_id: address,
        // Royalty settings from collection
        enforces_royalty: bool,
    }

    /// VULNERABLE: NFT stores collection reference but doesn't verify parent
    public fun create_nft(
        collection: &mut Collection,
        name: vector<u8>,
        ctx: &mut TxContext
    ): NFT {
        let nft = NFT {
            id: object::new(ctx),
            name,
            collection_id: object::uid_to_address(&collection.id),
            enforces_royalty: true,
        };

        nft
    }

    /// VULNERABLE: Royalty check uses stored ID, not actual parent
    public fun sell_nft(
        nft: NFT,
        collection: &Collection,
        price: u64,
        buyer: address,
    ) {
        // Check collection_id matches - but NFT might not actually be child
        assert!(nft.collection_id == object::uid_to_address(&collection.id), 0);

        // Royalty would be paid to this collection
        // But NFT could have been removed from collection and sold independently
        let royalty = (price * collection.royalty_bps) / 10000;

        // Process sale...
        transfer::transfer(nft, buyer);
    }

    /// VULNERABLE: Can remove NFT from collection, breaking royalty enforcement
    public fun remove_from_collection(
        collection: &mut Collection,
        nft_key: vector<u8>,
    ): NFT {
        // NFT removed but still has collection_id set
        // Royalty enforcement now broken
        dof::remove(&mut collection.id, nft_key)
    }
}
```

## Secure Example

```move
module game::secure_inventory {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_object_field as dof;

    public struct Player has key {
        id: UID,
        owner: address,
        name: vector<u8>,
    }

    public struct Weapon has key, store {
        id: UID,
        name: vector<u8>,
        damage: u64,
        // Track actual parent relationship
        equipped_to: Option<address>,
        soulbound: bool,
        original_owner: address,
    }

    /// SECURE: Validate weapon can be equipped
    public fun equip_weapon(
        player: &mut Player,
        weapon: Weapon,
        ctx: &TxContext
    ) {
        let player_addr = object::uid_to_address(&player.id);
        let sender = tx_context::sender(ctx);

        // Verify caller owns the player
        assert!(player.owner == sender, 0);

        // Check soulbound restrictions
        if (weapon.soulbound) {
            assert!(weapon.original_owner == sender, 1);
        };

        // Verify weapon isn't already equipped
        assert!(option::is_none(&weapon.equipped_to), 2);

        // Update weapon state before adding as child
        let mut weapon = weapon;
        weapon.equipped_to = option::some(player_addr);

        dof::add(&mut player.id, b"weapon", weapon);
    }

    /// SECURE: Validate unequip permissions
    public fun unequip_weapon(
        player: &mut Player,
        ctx: &TxContext
    ): Weapon {
        let sender = tx_context::sender(ctx);

        // Only player owner can unequip
        assert!(player.owner == sender, 0);

        let mut weapon: Weapon = dof::remove(&mut player.id, b"weapon");

        // Clear equipped state
        weapon.equipped_to = option::none();

        weapon
    }

    /// SECURE: Transfer validates all constraints
    public fun transfer_weapon(
        weapon: Weapon,
        recipient: address,
        ctx: &TxContext
    ) {
        // Cannot transfer if equipped
        assert!(option::is_none(&weapon.equipped_to), 0);

        // Cannot transfer if soulbound
        assert!(!weapon.soulbound, 1);

        transfer::transfer(weapon, recipient);
    }

    /// SECURE: Player transfer updates ownership properly
    public fun transfer_player(
        mut player: Player,
        recipient: address,
        ctx: &TxContext
    ) {
        let sender = tx_context::sender(ctx);
        assert!(player.owner == sender, 0);

        // Check for soulbound items that would prevent transfer
        if (dof::exists_(&player.id, b"weapon")) {
            let weapon: &Weapon = dof::borrow(&player.id, b"weapon");
            // Soulbound items block player transfer
            assert!(!weapon.soulbound, 1);
        };

        player.owner = recipient;
        transfer::transfer(player, recipient);
    }
}
```

```move
module defi::secure_locked_tokens {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};
    use sui::clock::{Self, Clock};

    /// SECURE: Lock is its own object, not a child
    /// Cannot be accessed via parent manipulation
    public struct TimeLock<phantom T> has key {
        id: UID,
        balance: Balance<T>,
        unlock_time: u64,
        beneficiary: address,
        // Cannot be transferred or modified
    }

    /// SECURE: Create independent lock object
    public fun lock_tokens<T>(
        coin: Coin<T>,
        unlock_time: u64,
        beneficiary: address,
        ctx: &mut TxContext
    ) {
        let lock = TimeLock {
            id: object::new(ctx),
            balance: coin::into_balance(coin),
            unlock_time,
            beneficiary,
        };

        // Share so beneficiary can claim, but no one can transfer
        transfer::share_object(lock);
    }

    /// SECURE: Only beneficiary can unlock after time
    public fun unlock_tokens<T>(
        lock: TimeLock<T>,
        clock: &Clock,
        ctx: &mut TxContext
    ): Coin<T> {
        let TimeLock { id, balance, unlock_time, beneficiary } = lock;

        // Verify caller is beneficiary
        assert!(tx_context::sender(ctx) == beneficiary, 0);

        // Verify time has passed
        assert!(clock::timestamp_ms(clock) >= unlock_time, 1);

        object::delete(id);
        coin::from_balance(balance, ctx)
    }

    // No transfer function - lock cannot be moved
}
```

```move
module nft::secure_collection {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_object_field as dof;
    use sui::event;

    public struct Collection has key {
        id: UID,
        creator: address,
        royalty_bps: u64,
    }

    /// SECURE: NFT wrapped in collection-specific container
    public struct CollectionNFT has key, store {
        id: UID,
        inner: NFTData,
        // Parent collection address for verification
        collection: address,
    }

    public struct NFTData has store {
        name: vector<u8>,
        attributes: vector<u8>,
    }

    /// Capability to prove NFT is in collection
    public struct CollectionMembership has key {
        id: UID,
        nft_id: address,
        collection_id: address,
    }

    /// SECURE: Create NFT that's bound to collection
    public fun mint_nft(
        collection: &mut Collection,
        name: vector<u8>,
        ctx: &mut TxContext
    ): CollectionNFT {
        let nft = CollectionNFT {
            id: object::new(ctx),
            inner: NFTData {
                name,
                attributes: vector::empty(),
            },
            collection: object::uid_to_address(&collection.id),
        };

        nft
    }

    /// SECURE: Sale must go through collection to enforce royalties
    public fun sell_through_collection(
        collection: &Collection,
        nft: CollectionNFT,
        payment: Coin<SUI>,
        buyer: address,
        ctx: &mut TxContext
    ) {
        // Verify NFT belongs to this collection
        assert!(nft.collection == object::uid_to_address(&collection.id), 0);

        let price = coin::value(&payment);
        let royalty_amount = (price * collection.royalty_bps) / 10000;

        // Pay royalty to creator
        let royalty = coin::split(&mut payment, royalty_amount, ctx);
        transfer::public_transfer(royalty, collection.creator);

        // Rest to seller (current owner via PTB)
        transfer::public_transfer(payment, tx_context::sender(ctx));

        // Transfer NFT to buyer
        transfer::transfer(nft, buyer);
    }

    /// SECURE: Direct transfer still respects collection binding
    /// Collection field remains - royalties enforced on next sale
    public fun transfer_nft(
        nft: CollectionNFT,
        recipient: address,
    ) {
        // NFT keeps collection binding
        transfer::transfer(nft, recipient);
    }
}
```

```move
module patterns::capability_children {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_object_field as dof;

    /// Parent object
    public struct Vault has key {
        id: UID,
        admin: address,
    }

    /// Child object with its own access rules
    public struct SecureAsset has key, store {
        id: UID,
        value: u64,
        // Asset tracks its own authority, not relying on parent
        authorized_users: vector<address>,
        requires_capability: bool,
    }

    /// Capability for accessing specific asset
    public struct AssetCap has key {
        id: UID,
        asset_id: address,
        holder: address,
    }

    /// SECURE: Add child with explicit authority setup
    public fun store_asset(
        vault: &mut Vault,
        asset: SecureAsset,
        key: vector<u8>,
        ctx: &TxContext
    ) {
        // Only vault admin can add assets
        assert!(vault.admin == tx_context::sender(ctx), 0);

        dof::add(&mut vault.id, key, asset);
    }

    /// SECURE: Access requires capability, not just parent access
    public fun access_asset(
        vault: &Vault,
        cap: &AssetCap,
        key: vector<u8>,
        ctx: &TxContext
    ): &SecureAsset {
        let asset: &SecureAsset = dof::borrow(&vault.id, key);

        // Verify capability matches asset
        assert!(cap.asset_id == object::uid_to_address(&asset.id), 0);

        // Verify caller holds capability
        assert!(cap.holder == tx_context::sender(ctx), 1);

        asset
    }

    /// SECURE: Modify requires capability
    public fun modify_asset(
        vault: &mut Vault,
        cap: &AssetCap,
        key: vector<u8>,
        new_value: u64,
        ctx: &TxContext
    ) {
        let asset: &mut SecureAsset = dof::borrow_mut(&mut vault.id, key);

        assert!(cap.asset_id == object::uid_to_address(&asset.id), 0);
        assert!(cap.holder == tx_context::sender(ctx), 1);

        asset.value = new_value;
    }

    /// SECURE: Remove requires both admin and capability
    public fun remove_asset(
        vault: &mut Vault,
        cap: AssetCap,
        key: vector<u8>,
        ctx: &TxContext
    ): SecureAsset {
        // Must be vault admin
        assert!(vault.admin == tx_context::sender(ctx), 0);

        let asset: SecureAsset = dof::remove(&mut vault.id, key);

        // Capability must match
        assert!(cap.asset_id == object::uid_to_address(&asset.id), 1);

        // Destroy capability
        let AssetCap { id, asset_id: _, holder: _ } = cap;
        object::delete(id);

        asset
    }
}
```

## Vulnerable Patterns

### Pattern 1: Implicit Parent Authority

```move
/// VULNERABLE: Assumes owning parent means owning children
public fun access_child(parent: &Parent): &Child {
    // Anyone who can borrow parent can access child
    dof::borrow(&parent.id, b"child")
}

/// SECURE: Validate access rights explicitly
public fun access_child(parent: &Parent, ctx: &TxContext): &Child {
    assert!(parent.owner == tx_context::sender(ctx), 0);
    dof::borrow(&parent.id, b"child")
}
```

### Pattern 2: Orphaned Authority References

```move
/// VULNERABLE: Child stores parent reference but doesn't verify
public struct Child has key, store {
    id: UID,
    parent_id: address, // Can become stale
}

public fun do_something(child: &Child, parent: &Parent) {
    // Check passes even if child was removed from parent
    assert!(child.parent_id == object::uid_to_address(&parent.id), 0);
}
```

### Pattern 3: Child Removal Bypasses Constraints

```move
/// VULNERABLE: Locked child can be removed from parent
public fun emergency_unlock(parent: &mut Parent): LockedAsset {
    // Bypass time lock by removing from parent
    dof::remove(&mut parent.id, b"locked")
}
```

### Pattern 4: Parent Transfer Inherits Children

```move
/// VULNERABLE: Transferring parent transfers all children
public fun transfer_container(container: Container, to: address) {
    // All children move with container
    // Children may have their own transfer restrictions
    transfer::transfer(container, to);
}
```

### Pattern 5: Wrapped Object Authority Leak

```move
/// VULNERABLE: Wrapping doesn't prevent unwrapping
public struct Wrapper has key {
    id: UID,
    inner: RestrictedAsset, // Has transfer restrictions
}

public fun unwrap(wrapper: Wrapper): RestrictedAsset {
    let Wrapper { id, inner } = wrapper;
    object::delete(id);
    inner // Restrictions bypassed
}
```

## Mitigation Strategies

1. **Explicit Authority Checks**: Never assume parent access implies child authority. Always validate permissions explicitly for child access.

2. **Capability-Based Child Access**: Require capabilities to access children, separate from parent ownership.

3. **Immutable Parent References**: Use immutable references to children when possible to prevent extraction.

4. **Child Self-Protection**: Design children to validate their own constraints, not relying on parent enforcement.

5. **Transfer Hooks**: Implement checks before parent transfers to validate child constraints.

6. **Prevent Unauthorized Removal**: Add access control to functions that remove children from parents.

7. **Use Wrapped Types**: Create wrapper types that enforce invariants and cannot be unwrapped.

8. **Event Tracking**: Emit events for parent-child relationship changes for off-chain monitoring.

## Object Model Considerations

```move
/// Understanding Sui object relationships:

// 1. Owned objects - single owner, transferable
public struct Owned has key { id: UID }

// 2. Shared objects - multiple accessors
public struct Shared has key { id: UID }

// 3. Dynamic fields - attached to parent, move with parent
public fun add_child(parent: &mut Parent, child: Child) {
    dof::add(&mut parent.id, key, child);
}

// 4. Wrapped objects - embedded in parent struct
public struct Parent has key {
    id: UID,
    wrapped_child: Child, // Moves with parent, same lifetime
}

// Each has different authority implications!
```

## Testing Checklist

- [ ] Verify child access functions validate caller authority
- [ ] Test that parent transfers respect child constraints
- [ ] Validate that child removal functions have proper access control
- [ ] Check for orphaned authority references after child removal
- [ ] Test soulbound/locked items cannot be transferred via parent
- [ ] Verify capabilities are required where parent access is insufficient
- [ ] Test wrapped object extraction doesn't bypass restrictions
- [ ] Validate authority checks in all parent-child operations
- [ ] Review dynamic field usage for authority assumptions
- [ ] Test cross-transaction parent-child relationship integrity

## Related Vulnerabilities

- [Access Control Mistakes](../access-control-mistakes/) - General access control issues
- [Transfer API Misuse](../transfer-api-misuse/) - Object transfer vulnerabilities
- [Capability Leakage](../capability-leakage/) - Improper capability handling
- [Dynamic Field Key Collisions](../dynamic-field-key-collisions/) - Dynamic field security issues
