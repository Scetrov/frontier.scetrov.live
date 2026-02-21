+++
date = '2026-02-21T12:23:00Z'
title = 'storage_unit.move'
weight = 2
codebase = 'https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/assemblies/storage_unit.move'
+++

## Overview

This report provides a comprehensive technical analysis of the `storage_unit.move` module. As a specialized implementation of the Assembly architecture, the Storage Unit serves as the primary persistence layer for items within the EVE Frontier universe, facilitating the secure bridging of assets between the game server and the blockchain.

## Learning Objectives

By the end of this article, you will be able to:

1. **Analyze** the `StorageUnit` data structure and its use of Dynamic Fields for multi-tenant inventory management.
2. **Explain** the dependency between `StorageUnit` lifecycle states and [`NetworkNode`](/develop/world-contracts/primitives/network_node.move/) energy handling.
3. **Trace** the execution flow of item bridging (Game-to-Chain and Chain-to-Game).
4. **Evaluate** the security model governing access control and sponsorship requirements.

---

## 1. Core Component Architecture

The `StorageUnit` is a shared object that acts as a container for operational [primitives](/develop/world-contracts/primitives/) and user [inventories](/develop/world-contracts/primitives/inventory.move/). Unlike simple assemblies, it must handle storage for multiple users (Character inventories) and the structure itself (Output [inventory](/develop/world-contracts/primitives/inventory.move/)).

```mermaid
classDiagram
    class StorageUnit {
        +UID id
        +TenantItemId key
        +AssemblyStatus status
        +Location location
        +Option<Metadata> metadata
        +vector<ID> inventory_keys
        +Option<ID> energy_source_id
        +ID owner_cap_id
        +u64 type_id
        +Option<TypeName> extension
    }
    class Inventory {
        +Dynamic Field
    }
    class NetworkNode {
        +EnergySource
    }

    StorageUnit *-- AssemblyStatus : contains
    StorageUnit *-- Location : contains
    StorageUnit *-- Metadata : contains
    StorageUnit "1" *-- "*" Inventory : manages via Dynamic Fields
    StorageUnit ..> NetworkNode : connects to
```

### Key Components

* **`inventory_keys`**: A vector tracking the IDs of all inventories attached to this unit. This allows the contract to iterate through and manage all stored assets during destruction.
* **Dynamic Field Inventories**: Instead of a single flat inventory, the Storage Unit uses Sui's Dynamic Fields to attach separate [`Inventory`](../../primitives/inventory.move/) objects.
  * **Structure Inventory**: Attached using the `StorageUnit`'s own `OwnerCap` ID.
  * **Character Inventories**: Attached using the Character's `OwnerCap` ID (ephemeral inventories created on demand).
* **`energy_source_id`**: Stores the ID of the [`NetworkNode`](/develop/world-contracts/primitives/network_node.move/) currently powering the unit. This enforces the requirement that storage must be powered to function.
* **`extension`**: An optional `TypeName` representing a third-party extension authorized to interact with this unit via the Typed Witness Pattern.

---

## 2. Functional Lifecycle

The Storage Unit's lifecycle is tightly coupled with the energy grid. It cannot operate (allow item transfers) without an active connection to a [`NetworkNode`](../../primitives/network_node.move/) providing energy.

```mermaid
stateDiagram-v2
    [*] --> Created: anchor() + share_storage_unit()
    Created --> Online: online() (Requires NetworkNode + OwnerCap)
    Online --> Offline: offline() (Releases Energy)
    Online --> Offline: Network Energy Depletion
    Offline --> Online: online()
    Offline --> [*]: unanchor() (Releases resources)
```

### Lifecycle Hooks

* **Initialization (`anchor` + `share_storage_unit`)**: Sets up the `StorageUnit`, creates its primary "Structure Inventory" (the default storage bin for the unit itself), connects to a `NetworkNode`, and creates an `OwnerCap` transferred to the owning character.
* **Activation (`online`)**:
  1. Verifies the [`NetworkNode`](/develop/world-contracts/primitives/network_node.move/) has sufficient energy capacity.
  2. **Reserves Energy**: Calls `reserve_energy` on the node, locking a portion of the grid's capacity for this unit.
  3. Updates [`AssemblyStatus`](../../primitives/status.move/) to active.
* **Deactivation (`offline`)**:
  1. **Releases Energy**: Calls `release_energy` on the node, freeing up capacity on the grid.
  2. Sets state to inactive.
* **Energy Source Management**: The admin can reassign the unit's `NetworkNode` via `update_energy_source()`. When a network node's connected assemblies change, the system uses **"Hot Potato" patterns** (`UpdateEnergySources`, `OfflineAssemblies`, `HandleOrphanedAssemblies`) to ensure all affected units are updated atomically.
* **Orphaned Unit Handling**: If a `NetworkNode` is unanchored, connected storage units become "orphaned". The `offline_orphaned_storage_unit()` function brings them offline, releases energy, and clears their energy source. `unanchor_orphan()` can then destroy the orphaned unit.
* **Destruction (`unanchor`)**:
  * Disconnects from the [`NetworkNode`](/develop/world-contracts/primitives/network_node.move/) and releases energy if online.
  * Iterates through `inventory_keys` to destroy **all** attached inventories (both structure and character).
  * Cleans up [metadata](/develop/world-contracts/primitives/metadata.move/), unanchors the unit, and deletes the `UID`.

---

## 3. Logic Deep Dive: Item Bridging

The primary "physics" of this module is the movement of items between the off-chain game state and on-chain ownership.

### Game-to-Chain (Minting)

This process "imports" items from the game world into the blockchain inventory.

```mermaid
sequenceDiagram
    participant Admin as Game Server (Sponsor)
    participant User
    participant StorageUnit
    participant Inventory
    
    User->>StorageUnit: game_item_to_chain_inventory(Item Data, Quantity)
    activate StorageUnit
    StorageUnit->>Admin: check verify_sponsor(ctx)
    StorageUnit->>StorageUnit: check character_address == sender
    StorageUnit->>StorageUnit: check status.is_online()
    
    alt User Inventory Missing
        StorageUnit->>Inventory: create new Inventory
        StorageUnit->>StorageUnit: bound as Dynamic Field
    end
    
    StorageUnit->>Inventory: mint_items(Item Data)
    Inventory-->>User: Items Added
    deactivate StorageUnit
```

**Critical Check**: The transaction **must** be sponsored by an address authorized in the `AdminACL`. This prevents users from arbitrarily minting items without the game server verifying they actually found those items in-game. Additionally, the sender's address must match the `Character`'s registered address.

### Chain-to-Game (Burning)

This process "exports" items back to the game, effectively burning them on-chain to credit the player in the database.

* **Function**: `chain_item_to_game_inventory`
* **Mechanism**: Calls `inventory.burn_items_with_proof`.
* **Verification**: Requires the `StorageUnit` to be Online and the sender's address to match the `Character`'s registered address. This ensures players can't extract items from a "powered down" or "destroyed" station.

---

## 4. Security & Access Patterns

Access control is enforced through a combination of Capabilities (`OwnerCap`) and Access Control Lists (`AdminACL`).

| Function | Required Authority | Scope |
| :--- | :--- | :--- |
| `anchor` + `share_storage_unit` | `AdminACL` (Sponsor) | Initial deployment and sharing of storage unit. |
| `online` | `OwnerCap<StorageUnit>` | Only the owner can activate the unit. |
| `offline` | `OwnerCap<StorageUnit>` | Only the owner can deactivate the unit. |
| `game_item_to_chain_inventory` | `OwnerCap` + `AdminACL` | **Hybrid**: Owner requests, Game Server (Admin) allows via sponsorship. Sender must match Character address. |
| `chain_item_to_game_inventory` | `OwnerCap` | Owner can burn their own items to move them in-game. Sender must match Character address. |
| `deposit_by_owner` | `OwnerCap` + `AdminACL` | **Hybrid**: Owner deposits items, Game Server verifies via sponsorship. Requires same-location check. |
| `withdraw_by_owner` | `OwnerCap` + `AdminACL` | **Hybrid**: Owner withdraws items, Game Server verifies via sponsorship. |
| `deposit_item<Auth>` | Extension Witness | Extension-controlled deposit with authorized type. |
| `withdraw_item<Auth>` | Extension Witness | Extension-controlled withdrawal with authorized type. |
| `authorize_extension<Auth>` | `OwnerCap<StorageUnit>` | Register an extension type for this unit. |

### The `AdminACL` Role

The `AdminACL` is crucial specifically for **minting** (Game -> Chain). It acts as a bridge of trust. The Move contract cannot verify game events (like "Player looted Item X"), so it trusts transactions signed/sponsored by the Game Server logic.

### Dynamic Field Security

The helper function `check_inventory_authorization` performs a type check on the `OwnerCap`:

* If `OwnerCap` is `StorageUnit`: Checks if `access::is_authorized` for the storage unit ID.
* If `OwnerCap` is `Character`: Checks if `access::is_authorized` for the character ID.

This distinction ensures that a user can only interact with their *own* ephemeral inventory within the storage unit, or the *unit's* main inventory if they own the unit.

---
