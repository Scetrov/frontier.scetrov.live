+++
title = '4. Ability Misconfiguration'
date = '2025-11-26T00:00:00Z'
weight = 4
+++

## Overview

Move's four abilities (`copy`, `drop`, `store`, `key`) control what operations can be performed on types. Misconfiguring these abilities can allow duplication of assets, unintended destruction of resources, wrapping of objects, or unauthorized global storage access.

## Risk Level

**Critical** — Incorrect abilities can break fundamental economic invariants.

## OWASP / CWE Mapping

| OWASP Top 10 | MITRE CWE |
|--------------|-----------|
| A01 (Broken Access Control) | CWE-284 (Improper Access Control), CWE-266 (Incorrect Privilege Assignment) |

## The Problem

### Ability Overview

| Ability | Allows | Danger |
|---------|--------|--------|
| `copy` | Duplicating values | Assets can be infinitely copied |
| `drop` | Implicit destruction | Resources can be silently discarded |
| `store` | Storing inside other objects | Objects can be wrapped/transferred |
| `key` | Top-level object status | Can be stored in global storage |

### Common Mistakes

1. **Giving `copy` to assets** — Allows infinite minting
2. **Giving `drop` to valuable items** — Allows destroying value without proper handling
3. **Giving `store` to capabilities** — Allows unauthorized transfer/wrapping
4. **Over-granting abilities** — Default to minimal abilities

## Vulnerable Example

```move
module vulnerable::token {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    /// CRITICAL VULNERABILITY: Token with `copy` ability
    /// Anyone can duplicate tokens infinitely!
    public struct Token has copy, drop, store {
        value: u64,
    }

    /// VULNERABLE: Capability with `store` allows transfer
    public struct MintCap has key, store {
        id: UID,
        max_supply: u64,
    }

    public fun mint(cap: &MintCap, amount: u64): Token {
        Token { value: amount }
    }

    /// VULNERABLE: Ticket that can be dropped silently
    /// User might accidentally lose their ticket
    public struct EventTicket has key, drop, store {
        id: UID,
        event_id: u64,
        seat: u64,
    }
}
```

### Attack: Infinite Token Duplication

```move
module attack::duplicate {
    use vulnerable::token::{Self, Token};

    public fun exploit(): (Token, Token, Token) {
        let original = token::mint(cap, 1000);
        
        // Because Token has `copy`, we can duplicate it infinitely!
        let copy1 = copy original;
        let copy2 = copy original;
        let copy3 = copy original;
        // ... unlimited copies
        
        (original, copy1, copy2)
    }
}
```

### Attack: Capability Transfer

```move
module attack::steal_cap {
    use vulnerable::token::MintCap;
    use sui::transfer;

    public entry fun steal(cap: MintCap) {
        // MintCap has `store`, so anyone who gets it can transfer it
        transfer::public_transfer(cap, @attacker);
    }
}
```

## Secure Example

```move
module secure::token {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::event;

    /// SECURE: No `copy` or `drop` — true asset semantics
    /// Must be explicitly created and explicitly consumed
    public struct Token has key, store {
        id: UID,
        value: u64,
    }

    /// SECURE: No `store` — only this module controls transfers
    public struct MintCap has key {
        id: UID,
        max_supply: u64,
        minted: u64,
    }

    /// SECURE: No `drop` — must be explicitly used or refunded
    public struct EventTicket has key {
        id: UID,
        event_id: u64,
        seat: u64,
        owner: address,
    }

    /// Event for ticket redemption
    public struct TicketRedeemed has copy, drop {
        ticket_id: object::ID,
        event_id: u64,
        seat: u64,
    }

    public fun mint(
        cap: &mut MintCap, 
        amount: u64, 
        recipient: address,
        ctx: &mut TxContext
    ) {
        assert!(cap.minted + amount <= cap.max_supply, E_EXCEEDS_SUPPLY);
        cap.minted = cap.minted + amount;
        
        transfer::transfer(
            Token { id: object::new(ctx), value: amount },
            recipient
        );
    }

    /// Tokens must be explicitly merged or split
    public fun merge(token1: Token, token2: Token, ctx: &mut TxContext): Token {
        let Token { id: id1, value: v1 } = token1;
        let Token { id: id2, value: v2 } = token2;
        object::delete(id1);
        object::delete(id2);
        
        Token { id: object::new(ctx), value: v1 + v2 }
    }

    /// Tickets must be explicitly redeemed — cannot be dropped
    public entry fun redeem_ticket(ticket: EventTicket, ctx: &TxContext) {
        let EventTicket { id, event_id, seat, owner } = ticket;
        
        // Verify caller is the ticket owner
        assert!(tx_context::sender(ctx) == owner, E_NOT_OWNER);
        
        event::emit(TicketRedeemed {
            ticket_id: object::uid_to_inner(&id),
            event_id,
            seat,
        });
        
        object::delete(id);
    }

    /// Explicit refund path for tickets
    public entry fun refund_ticket(
        ticket: EventTicket,
        ctx: &mut TxContext
    ) {
        let EventTicket { id, event_id: _, seat: _, owner } = ticket;
        assert!(tx_context::sender(ctx) == owner, E_NOT_OWNER);
        object::delete(id);
        // ... refund logic
    }
}
```

## Ability Selection Guidelines

### For Assets (Tokens, NFTs, Items)

```move
/// Minimal abilities for fungible-like assets
public struct Asset has key, store {
    id: UID,
    value: u64,
}

/// For assets that should never leave the protocol
public struct LockedAsset has key {
    id: UID,
    value: u64,
}
```

### For Capabilities

```move
/// Capability that can only be transferred by your module
public struct AdminCap has key {
    id: UID,
}

/// Witness pattern — one-time use, no abilities needed
public struct WITNESS has drop {}
```

### For Receipts/Proofs

```move
/// Hot potato — must be consumed in same transaction
public struct Receipt {
    amount: u64,
}

/// Cannot be stored, copied, or dropped — forces handling
```

### For Events

```move
/// Events should always have copy + drop
public struct TransferEvent has copy, drop {
    from: address,
    to: address,
    amount: u64,
}
```

## Recommended Mitigations

### 1. Start with Minimal Abilities

```move
/// Start with nothing, add only what's needed
public struct MyType { }

/// Then add based on requirements:
public struct MyType has key { }  // If it needs to be an object
public struct MyType has key, store { }  // If it needs transfer
```

### 2. Document Why Each Ability is Needed

```move
/// `key`: Required for object storage
/// `store`: Required for marketplace listing (intentional risk accepted)
/// NO `copy`: Asset must not be duplicable
/// NO `drop`: Asset must be explicitly consumed
public struct NFT has key, store {
    id: UID,
    // ...
}
```

### 3. Use Wrapper Types for Different Contexts

```move
/// Internal representation — minimal abilities
public struct TokenInner {
    value: u64,
}

/// Transferable version
public struct TransferableToken has key, store {
    id: UID,
    inner: TokenInner,
}

/// Locked version — no `store`
public struct LockedToken has key {
    id: UID,
    inner: TokenInner,
    unlock_time: u64,
}
```

## Testing Checklist

- [ ] Verify no asset types have `copy` ability
- [ ] Verify valuable resources don't have `drop` unless explicitly intended
- [ ] Verify capabilities lack `store` unless transfer is explicitly required
- [ ] Test that types without `drop` must be explicitly consumed
- [ ] Audit all `has` declarations against security requirements

## Related Vulnerabilities

- [Object Transfer Misuse](../object-transfer-misuse/)
- [Object Freezing Misuse](../object-freezing-misuse/)
- [Capability Leakage](../capability-leakage/)
