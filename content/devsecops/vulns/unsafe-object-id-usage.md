+++
title = '13. Unsafe Object ID Usage'
date = '2025-11-26T20:11:50Z'
weight = 13
+++

## Overview

Object IDs (`object::ID`) in Sui are unique identifiers, but using them as stable identity anchors for child objects or in access control can lead to vulnerabilities. Child object IDs can change when objects are unwrapped, rewrapped, or transferred between parents.

## Risk Level

**Medium** — Can lead to authorization bypasses and state inconsistencies.

## OWASP / CWE Mapping

 | OWASP Top 10 | MITRE CWE |
 | -------------- | ----------- |
 | A01 (Broken Access Control) | CWE-639 (Authorization Bypass), CWE-915 (Improperly Controlled Modification) |

## The Problem

### Object ID Characteristics

 | Object Type | ID Stability | Notes |
 | ------------- | -------------- | ------- |
 | Address-owned | Stable | ID persists across transfers |
 | Shared | Stable | ID fixed after sharing |
 | Dynamic field child | Unstable | ID can change on wrap/unwrap |
 | Wrapped object | Lost | Inner object's ID changes when unwrapped |

### Common Mistakes

1. **Using child object IDs as permanent identifiers** — IDs change when structure changes
2. **Storing IDs for authorization** — Referenced object may no longer exist
3. **Cross-referencing by ID without verification** — IDs may point to wrong objects
4. **Assuming ID uniqueness across time** — Same ID could be reused after deletion

## Vulnerable Example

```move
module vulnerable::membership {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::dynamic_object_field as dof;

    public struct Organization has key {
        id: UID,
        /// VULNERABLE: Storing child object IDs as member identifiers
        member_ids: vector<ID>,
        admin_member_id: ID,
    }

    public struct MemberBadge has key, store {
        id: UID,
        org_id: ID,
        role: u8,
    }

    /// VULNERABLE: Uses ID for permanent reference
    public entry fun add_member(
        org: &mut Organization,
        ctx: &mut TxContext
    ) {
        let badge = MemberBadge {
            id: object::new(ctx),
            org_id: object::id(org),
            role: 0,
        };

        let badge_id = object::id(&badge);
        vector::push_back(&mut org.member_ids, badge_id);

        // Badge stored as dynamic field
        dof::add(&mut org.id, badge_id, badge);
    }

    /// VULNERABLE: ID-based lookup can fail or return wrong object
    public entry fun promote_member(
        org: &mut Organization,
        member_id: ID,
    ) {
        // What if badge was removed and re-added with same ID?
        // What if member_id doesn't exist?
        assert!(vector::contains(&org.member_ids, &member_id), E_NOT_MEMBER);

        let badge: &mut MemberBadge = dof::borrow_mut(&mut org.id, member_id);
        badge.role = 1;
    }

    /// VULNERABLE: Admin check using potentially invalid ID
    public entry fun admin_action(
        org: &mut Organization,
        actor_badge_id: ID,
    ) {
        // If admin badge was rewrapped, this ID is stale
        assert!(actor_badge_id == org.admin_member_id, E_NOT_ADMIN);
        // ... perform admin action
    }

    /// VULNERABLE: ID reuse after deletion
    public entry fun remove_member(
        org: &mut Organization,
        member_id: ID,
    ) {
        let badge: MemberBadge = dof::remove(&mut org.id, member_id);

        // Remove from member list
        let (found, idx) = vector::index_of(&org.member_ids, &member_id);
        if (found) {
            vector::remove(&mut org.member_ids, idx);
        };

        // Delete badge
        let MemberBadge { id, org_id: _, role: _ } = badge;
        object::delete(id);

        // Problem: member_id is now "free" and could theoretically be reused
        // (not in practice for UID, but the logic is still flawed)
    }
}
```

## Secure Example

```move
module secure::membership {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::table::{Self, Table};

    /// Use a stable identifier separate from object ID
    public struct MemberId has copy, drop, store {
        value: u64,
    }

    public struct Organization has key {
        id: UID,
        /// SECURE: Use stable member ID, not object ID
        next_member_id: u64,
        /// Map stable ID to member data
        members: Table<MemberId, MemberRecord>,
        admin_id: MemberId,
    }

    public struct MemberRecord has store {
        address: address,
        role: u8,
        joined_at: u64,
    }

    /// SECURE: Member badge references stable ID, owned by member
    public struct MemberBadge has key {
        id: UID,
        org_id: ID,
        member_id: MemberId,  // Stable identifier
    }

    public entry fun add_member(
        org: &mut Organization,
        member_address: address,
        ctx: &mut TxContext
    ) {
        // Generate stable member ID
        let member_id = MemberId { value: org.next_member_id };
        org.next_member_id = org.next_member_id + 1;

        // Store member record
        table::add(&mut org.members, member_id, MemberRecord {
            address: member_address,
            role: 0,
            joined_at: tx_context::epoch(ctx),
        });

        // Create badge with stable ID
        transfer::transfer(
            MemberBadge {
                id: object::new(ctx),
                org_id: object::id(org),
                member_id,
            },
            member_address
        );
    }

    /// SECURE: Verify both badge ownership and org membership
    public entry fun promote_member(
        org: &mut Organization,
        badge: &MemberBadge,
        ctx: &TxContext
    ) {
        // Verify badge is for this org
        assert!(badge.org_id == object::id(org), E_WRONG_ORG);

        // Verify member exists in org
        assert!(table::contains(&org.members, badge.member_id), E_NOT_MEMBER);

        let record = table::borrow_mut(&mut org.members, badge.member_id);
        record.role = 1;
    }

    /// SECURE: Admin check using badge possession
    public entry fun admin_action(
        org: &mut Organization,
        admin_badge: &MemberBadge,
        ctx: &TxContext
    ) {
        // Verify badge is for this org
        assert!(admin_badge.org_id == object::id(org), E_WRONG_ORG);

        // Verify caller holds the admin badge
        assert!(admin_badge.member_id == org.admin_id, E_NOT_ADMIN);

        // Additional: verify sender owns the badge
        // (implicit through object ownership)

        // ... perform admin action
    }

    /// SECURE: Clean removal with stable ID
    public entry fun remove_member(
        org: &mut Organization,
        badge: MemberBadge,
        ctx: &TxContext
    ) {
        let MemberBadge { id, org_id, member_id } = badge;

        // Verify badge is for this org
        assert!(org_id == object::id(org), E_WRONG_ORG);

        // Remove from membership table
        assert!(table::contains(&org.members, member_id), E_NOT_MEMBER);
        let _record = table::remove(&mut org.members, member_id);

        // Delete badge
        object::delete(id);
    }
}
```

## Safe ID Usage Patterns

### Pattern 1: Stable Application-Level IDs

```move
/// Use incrementing counter for stable IDs
public struct StableId has copy, drop, store {
    value: u64,
}

public struct IdGenerator has key {
    id: UID,
    next_id: u64,
}

public fun generate_id(gen: &mut IdGenerator): StableId {
    let id = StableId { value: gen.next_id };
    gen.next_id = gen.next_id + 1;
    id
}
```

### Pattern 2: Object Ownership for Authorization

```move
/// Don't store IDs for auth — use object possession
public entry fun authorized_action(
    cap: &AuthCap,      // Possession proves authorization
    target: &mut Target,
) {
    // No ID comparison needed
    // Caller must own cap to include it in transaction
}
```

### Pattern 3: Verify ID References

```move
/// When IDs must be used, verify they point to valid objects
public fun use_reference(
    registry: &Registry,
    obj_id: ID,
) {
    // Verify object still exists in registry
    assert!(table::contains(&registry.objects, obj_id), E_OBJECT_NOT_FOUND);

    // Get the actual object and verify properties
    let obj = table::borrow(&registry.objects, obj_id);
    assert!(obj.valid, E_OBJECT_INVALID);
}
```

### Pattern 4: Immutable Reference Objects

```move
/// Create immutable reference objects for stable identity
public struct IdentityAnchor has key {
    id: UID,
    // Never modified after creation
    owner: address,
    created_at: u64,
}

public fun create_anchor(ctx: &mut TxContext): IdentityAnchor {
    let anchor = IdentityAnchor {
        id: object::new(ctx),
        owner: tx_context::sender(ctx),
        created_at: tx_context::epoch(ctx),
    };

    // Immediately freeze — ID now permanently stable
    transfer::freeze_object(anchor);

    anchor
}
```

## Recommended Mitigations

### 1. Use Application-Level Identifiers

```move
// Instead of object::id(obj)
// Use a stable counter-based ID
let stable_id = StableId { value: counter.next() };
```

### 2. Prefer Object Possession Over ID Checks

```move
// BAD: ID comparison
assert!(user_id == stored_admin_id, E_NOT_ADMIN);

// GOOD: Object possession
public entry fun admin_action(admin_cap: &AdminCap, ...) { }
```

### 3. Verify Referenced Objects Still Exist

```move
public fun safe_lookup(registry: &Registry, id: ID): &Object {
    assert!(registry.contains(id), E_NOT_FOUND);
    registry.borrow(id)
}
```

### 4. Document ID Stability Requirements

```move
/// NOTE: This ID is stable because:
/// - Object is address-owned (not wrapped)
/// - Object is never transferred to dynamic field
/// - Object is immutable after creation
```

## Testing Checklist

- [ ] Test that removing and re-adding objects doesn't reuse stale IDs
- [ ] Verify authorization works after objects are transferred
- [ ] Test behavior when referenced objects are deleted
- [ ] Confirm child object ID changes are handled correctly
- [ ] Test with wrapped and unwrapped object scenarios

## Related Vulnerabilities

- [Dynamic Field Misuse](../dynamic-field-misuse/)
- [Ownership Model Confusion](../ownership-model-confusion/)
- [Access-Control Mistakes](../access-control-mistakes/)
