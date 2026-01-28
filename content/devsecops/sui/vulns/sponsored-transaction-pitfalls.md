+++
title = '9. Sponsored Transaction Pitfalls'
date = '2025-11-26T20:07:13Z'
weight = 9
+++

## Overview

Sui supports sponsored transactions where one account pays gas fees for another account's transaction. Confusing the gas sponsor with the transaction sender can lead to impersonation attacks, unauthorized actions, and broken access control.

## Risk Level

**High** — Can lead to complete access control bypass and impersonation.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE | 
 | -------------- | ----------- | 
 | A01 (Broken Access Control) | CWE-285 (Improper Authorization), CWE-863 (Incorrect Authorization) | 

## The Problem

### Transaction Participants

 | Role | Function | Example | 
 | ------ | ---------- | --------- | 
 | **Sender** | Signs transaction, authorizes actions | User performing action | 
 | **Sponsor** | Pays gas fees | Relayer, dApp backend | 
 | **Validator** | Executes transaction | Network node | 

### The Confusion

Developers sometimes assume:

- The gas payer is the "real" user
- `sender()` returns the sponsor
- Only the sponsor can initiate transactions

In reality:

- `sender()` returns the **transaction sender**, not sponsor
- Sponsor only pays gas — they don't authorize object operations
- Sender's signature authorizes accessing their owned objects

## Vulnerable Example

```move
module vulnerable::gasless {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    public struct RelayerConfig has key {
        id: UID,
        authorized_relayer: address,  // Gas sponsor
        trusted_users: vector<address>,
    }

    public struct UserVault has key {
        id: UID,
        owner: address,
        balance: u64,
    }

    /// VULNERABLE: Checks sponsor instead of sender
    /// Attacker can get anyone to sponsor their malicious tx
    public entry fun withdraw_via_relayer(
        config: &RelayerConfig,
        vault: &mut UserVault,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // WRONG: This might check the wrong entity
        // In sponsored TX, sender() is still the actual sender
        // But developer might be thinking of the sponsor
        
        // Suppose they meant to check if relayer is calling:
        // This is STILL wrong because it doesn't verify
        // the sender is authorized to access this vault!
        
        assert!(tx_context::sender(ctx) == config.authorized_relayer, E_NOT_RELAYER);
        
        // No check that the vault owner authorized this!
        vault.balance = vault.balance - amount;
    }

    /// VULNERABLE: Assumes sponsor = authorized party
    public entry fun admin_action_gasless(
        config: &RelayerConfig,
        ctx: &mut TxContext
    ) {
        // If sponsor is the admin, attacker creates TX where:
        // - Attacker is sender
        // - Admin is sponsor (pays gas)
        // Attacker's action gets authorized because admin sponsors it!
        
        // This is logically backwards
    }
}

module vulnerable::meta_tx {
    use sui::ecdsa_k1;
    use sui::tx_context::TxContext;

    /// VULNERABLE: Replay attack possible
    public entry fun execute_meta_tx(
        user_signature: vector<u8>,
        action_data: vector<u8>,
        ctx: &mut TxContext
    ) {
        // Missing: nonce check
        // Missing: deadline check  
        // Missing: chain ID check
        
        let signer = ecdsa_k1::secp256k1_ecrecover(&user_signature, &action_data, 0);
        
        // Signature can be replayed indefinitely!
        // ... execute action
    }
}
```

### Attack Scenario

``` move
1. Attacker finds a contract that checks "authorized_relayer"
2. Attacker tricks the relayer into sponsoring their transaction
   (e.g., through a legitimate-looking request)
3. Transaction is sponsored by relayer, but attacker is sender
4. If contract only checks sponsor is authorized, attacker gets access
```

## Secure Example

```move
module secure::gasless {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::table::{Self, Table};
    use sui::clock::{Self, Clock};
    use sui::ecdsa_k1;
    use sui::hash;

    const E_NOT_OWNER: u64 = 0;
    const E_INVALID_SIGNATURE: u64 = 1;
    const E_NONCE_USED: u64 = 2;
    const E_EXPIRED: u64 = 3;
    const E_WRONG_CHAIN: u64 = 4;

    /// Chain ID for replay protection
    const CHAIN_ID: u64 = 1;

    public struct UserVault has key {
        id: UID,
        owner: address,
        balance: u64,
    }

    public struct NonceRegistry has key {
        id: UID,
        used_nonces: Table<vector<u8>, bool>,
    }

    /// SECURE: Sender must own the vault (object ownership)
    /// Gas sponsor is irrelevant — ownership is what matters
    public entry fun withdraw(
        vault: &mut UserVault,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // sender() returns the transaction sender, who must own vault
        // This is enforced by Sui's object model — no explicit check needed
        // if vault is address-owned
        
        vault.balance = vault.balance - amount;
        // Transfer to sender...
    }

    /// SECURE: For shared objects, verify sender is owner
    public entry fun withdraw_from_shared(
        vault: &mut UserVault,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // For shared objects, explicitly verify sender
        assert!(tx_context::sender(ctx) == vault.owner, E_NOT_OWNER);
        
        vault.balance = vault.balance - amount;
    }

    /// SECURE: Meta-transaction with proper protections
    public entry fun execute_meta_tx(
        nonce_registry: &mut NonceRegistry,
        clock: &Clock,
        user_pubkey: vector<u8>,
        user_signature: vector<u8>,
        action_type: u8,
        action_data: vector<u8>,
        nonce: vector<u8>,
        deadline: u64,
        chain_id: u64,
        ctx: &mut TxContext
    ) {
        // Check chain ID
        assert!(chain_id == CHAIN_ID, E_WRONG_CHAIN);
        
        // Check deadline
        let now = clock::timestamp_ms(clock);
        assert!(now < deadline, E_EXPIRED);
        
        // Check nonce not used
        assert!(!table::contains(&nonce_registry.used_nonces, nonce), E_NONCE_USED);
        
        // Mark nonce as used
        table::add(&mut nonce_registry.used_nonces, nonce, true);
        
        // Build message that was signed
        let mut message = vector::empty<u8>();
        vector::append(&mut message, action_data);
        vector::append(&mut message, nonce);
        vector::append(&mut message, bcs::to_bytes(&deadline));
        vector::append(&mut message, bcs::to_bytes(&chain_id));
        
        // Hash the message
        let message_hash = hash::keccak256(&message);
        
        // Verify signature
        let recovered = ecdsa_k1::secp256k1_ecrecover(
            &user_signature,
            &message_hash,
            0
        );
        assert!(recovered == user_pubkey, E_INVALID_SIGNATURE);
        
        // Now execute action on behalf of verified user
        // The signer of user_signature authorized this, not tx sender
    }
}
```

## Meta-Transaction Best Practices

### 1. Include Replay Protection

```move
public struct MetaTxData has drop {
    action: vector<u8>,
    nonce: u64,           // Unique per user
    deadline: u64,        // Expiration timestamp
    chain_id: u64,        // Network identifier
    contract_address: address,  // Target contract
}
```

### 2. Verify User Intent, Not Sponsor

```move
/// User signature proves intent, sponsor just pays gas
public entry fun user_authorized_action(
    user_signature: vector<u8>,
    action_data: vector<u8>,
    ctx: &mut TxContext
) {
    // Verify USER signed the action
    let authorized_user = verify_signature(user_signature, action_data);
    
    // Execute action AS the authorized user
    // Transaction sender (possibly sponsor) is irrelevant
}
```

### 3. Domain Separation

```move
/// Different actions have different signature domains
const DOMAIN_WITHDRAW: vector<u8> = b"WITHDRAW_V1:";
const DOMAIN_TRANSFER: vector<u8> = b"TRANSFER_V1:";

fun build_withdraw_message(amount: u64, recipient: address, nonce: u64): vector<u8> {
    let mut msg = DOMAIN_WITHDRAW;
    vector::append(&mut msg, bcs::to_bytes(&amount));
    vector::append(&mut msg, bcs::to_bytes(&recipient));
    vector::append(&mut msg, bcs::to_bytes(&nonce));
    msg
}
```

### 4. Use Object Ownership When Possible

```move
/// Sui's object model provides natural authorization
/// If vault is address-owned, only owner can include it in TX

public entry fun secure_withdraw(
    vault: &mut UserVault,  // Must be owned by sender
    amount: u64,
) {
    // No authorization check needed!
    // Sui verifies sender owns this object
    vault.balance = vault.balance - amount;
}
```

## Recommended Mitigations

### 1. Never Use Sponsor for Authorization

```move
// WRONG: Don't do this
assert!(is_sponsor(ctx), E_NOT_AUTHORIZED);

// RIGHT: Check sender or capability
assert!(tx_context::sender(ctx) == expected_user, E_NOT_AUTHORIZED);
// OR
assert!(has_capability(cap), E_NOT_AUTHORIZED);
```

### 2. Prefer Object Ownership to Explicit Checks

```move
// Object ownership is the strongest authorization in Sui
public entry fun action(owned_object: &mut MyObject) {
    // Only owner can include this in their transaction
}
```

### 3. Implement Full Meta-TX Protection

```move
struct MetaTxParams {
    nonce: u64,
    deadline: u64,
    chain_id: u64,
    target_contract: address,
}
// All must be verified before execution
```

## Testing Checklist

- [ ] Test that sponsor cannot perform actions requiring sender authorization
- [ ] Verify meta-transactions reject replayed signatures
- [ ] Test deadline expiration
- [ ] Verify chain ID mismatch is rejected
- [ ] Test nonce reuse prevention
- [ ] Confirm object ownership is the primary authorization for owned objects

## Related Vulnerabilities

- [Access-Control Mistakes](../access-control-mistakes/)
- [Object Transfer Misuse](../object-transfer-misuse/)
- [Capability Leakage](../capability-leakage/)