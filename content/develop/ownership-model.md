+++
date = '2026-02-21T12:23:00Z'
title = "Ownership Model"
weight = 8
description = "Capability-based access control hierarchy in EVE Frontier — GovernorCap, AdminACL, OwnerCap, and the borrow-use-return pattern."
+++

EVE Frontier uses a **capability-based** access control system. Instead of relying on wallet addresses for ownership, transferable capability objects (`OwnerCap`) grant access to on-chain objects.

## Access Hierarchy

```text
GovernorCap  (deployer — top-level authority)
    └── AdminACL  (shared object — authorized sponsor addresses)
            └── OwnerCap<T>  (player — mutates a specific object)
```

* **`GovernorCap`** — Created at deploy time in [`world.move`](world-contracts/world.move/). Can add/remove sponsors in `AdminACL`.
* **`AdminACL`** — A shared object containing a list of authorized sponsor addresses. Functions protected by `AdminACL` call `verify_sponsor(ctx)`, which checks the transaction sponsor.
* **`OwnerCap<T>`** — A phantom-typed "keycard" that authorizes mutation of **one specific object**.

```move
public struct OwnerCap<phantom T> has key {
    id: UID,
    authorized_object_id: ID,
}
```

---

## Character as a Keychain

All `OwnerCap`s are stored inside the player's `Character` object (not in their wallet directly). This is inspired by a real-world **keychain pattern** — a single master key (the character) grants access to many capabilities.

```text
User Wallet
    └── Character (shared object, mapped to user address)
            ├── OwnerCap<NetworkNode>
            ├── OwnerCap<Gate>
            ├── OwnerCap<StorageUnit>
            └── ...
```

When a Smart Assembly is created, its `OwnerCap` is minted and transferred to the `Character` object. If the user has access to the character, they have access to all its capabilities.

---

## Borrow-Use-Return Pattern

To use an `OwnerCap`, the player **borrows** it from the character, uses it, and **returns** it — all within a single transaction. This uses Sui's [`Receiving`](https://docs.sui.io/guides/developer/objects/transfers/transfer-to-object) pattern.

```move
// 1. Borrow the OwnerCap from the character
public fun borrow_owner_cap<T: key>(
    character: &mut Character,
    owner_cap_ticket: Receiving<OwnerCap<T>>,
    ctx: &TxContext,
): (OwnerCap<T>, ReturnOwnerCapReceipt)

// 2. Use it (e.g., bring a storage unit online)
public fun online(
    storage_unit: &mut StorageUnit,
    network_node: &mut NetworkNode,
    energy_config: &EnergyConfig,
    owner_cap: &OwnerCap<StorageUnit>,
)

// 3. Return it to the character
public fun return_owner_cap<T: key>(
    character: &Character,
    owner_cap: OwnerCap<T>,
    receipt: ReturnOwnerCapReceipt,
)
```

A `ReturnOwnerCapReceipt` (hot potato) ensures the cap is always returned or explicitly transferred — it cannot be silently dropped.

### TypeScript Example

A typical owner-authenticated call (e.g., bringing a network node online):

```typescript
// 1. Borrow OwnerCap from character
const [ownerCap, receipt] = tx.moveCall({
  target: `${packageId}::character::borrow_owner_cap`,
  typeArguments: [`${packageId}::network_node::NetworkNode`],
  arguments: [tx.object(characterId), tx.object(ownerCapId)],
});

// 2. Use OwnerCap to bring network node online
tx.moveCall({
  target: `${packageId}::network_node::online`,
  arguments: [tx.object(nwnId), ownerCap, tx.object(CLOCK_OBJECT_ID)],
});

// 3. Return OwnerCap to character
tx.moveCall({
  target: `${packageId}::character::return_owner_cap`,
  arguments: [tx.object(characterId), ownerCap, receipt],
});
```

---

## Benefits

* **Centralized ownership** — manage all capabilities from a single character object
* **Granular access** — each `OwnerCap<T>` only authorizes one specific object
* **Delegatable** — transfer an `OwnerCap` without moving the underlying assembly
* **Composable** — the borrow-use-return pattern works within programmable transactions

---

## Related Code

* [`access_control.move`](/develop/world-contracts/access/access_control.move/) — Access control implementation
* [`character.move`](/develop/world-contracts/entities/character/character.move/) — Character and keychain pattern

{{% tip-menu-search %}}
