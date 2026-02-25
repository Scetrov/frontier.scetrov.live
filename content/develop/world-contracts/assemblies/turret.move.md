+++
date = '2026-02-25T00:00:00Z'
title = 'turret.move'
weight = 4
draft = false
codebase = "https://github.com/evefrontier/world-contracts/tree/main/contracts/world/sources/assemblies"
+++

{{% pre-release pr_number="95" description="The Turret API and architecture are subject to significant changes before the official release." %}}

The Turret is a **programmable defense structure** in the EVE Frontier world. It is a Sui shared object anchored to a [Network Node](../network-node/network_node.move/), projecting offensive or defensive power over a fixed location based on builder-defined targeting rules.

Builders control two key behaviors:

* **InProximity** — reacts to ships entering the turret's engagement range.
* **Aggression** — responds to hostile actions from ships within range.

A configurable on-chain **priority queue** determines how targets are ranked and engaged. Owners can define custom targeting logic through extension contracts using the [typed witness pattern](/develop/smart-assemblies-intro/#extension-pattern).

## Architecture

The implementation composes several [Layer 1 primitives](/develop/world-contracts/primitives/) and supports custom targeting logic through the typed witness extension pattern.

```mermaid
flowchart TD
    subgraph Turret Assembly
        T[Turret Object]
    end

    subgraph Primitives
        Status["status.move"]
        Location["location.move"]
        Energy["energy.move"]
        Metadata["metadata.move"]
    end

    subgraph Targeting
        P["Priority Queue (BCS)"]
        Rules["Default Rules"]
        Ext["Custom Extension"]
    end

    subgraph Infrastructure
        NWN["Network Node"]
        Receipt["OnlineReceipt (hot potato)"]
    end

    T --> Status
    T --> Location
    T --> Energy
    T --> Metadata
    T -->|energy_source_id| NWN
    T --> P
    Rules -->|apply_target_priority_rules| P
    Ext -.->|typed witness| T
    Receipt -.->|verify_online| T
```

## Key Concepts

* **Two Behaviors** — The game invokes turret logic through two triggers: **InProximity** (a new ship enters range) and **Aggression** (a hostile action occurs on-grid). Both call `get_target_priority_list` to update the targeting queue.
* **Priority Queue** — Targets are ranked in a `vector<TurretTarget>` serialized as BCS bytes. The function `get_target_priority_list` receives the current list plus a new target and returns the updated list.
* **Default Targeting Rules** — When no extension is configured, the built-in `apply_target_priority_rules` function applies: aggressors are always added; non-aggressive targets from a different tribe than the owner are added; same-tribe non-aggressors are ignored.
* **Energy Dependency** — Turrets must be anchored to a [Network Node](../network-node/network_node.move/) and consume energy from it to remain online.
* **Extension Pattern** — Uses `authorize_extension<Auth>` to register a typed witness, allowing builders to inject custom targeting priority logic. When an extension is configured, the game resolves the extension package and calls `get_target_priority_list` in that package instead.
* **OnlineReceipt (Hot Potato)** — Calling `verify_online` returns a non-storable `OnlineReceipt` proving the turret is active. The default `get_target_priority_list` consumes it internally; extensions must call `destroy_online_receipt(receipt, auth_witness)` to destroy it.

## Data Structures

### `Turret`

The core shared object representing the turret assembly.

| Field              | Type                  | Description                                                                 |
| ------------------ | --------------------- | --------------------------------------------------------------------------- |
| `id`               | `UID`                 | Unique Sui object identifier.                                               |
| `key`              | `TenantItemId`        | Composite key derived from the in-game item ID and tenant.                  |
| `owner_cap_id`     | `ID`                  | ID of the `OwnerCap<Turret>` transferred to the owner's character.          |
| `type_id`          | `u64`                 | The turret's type identifier (determines energy cost and specialization).   |
| `status`           | `AssemblyStatus`      | Tracks whether the turret is anchored, online, offline, or unanchored.      |
| `location`         | `Location`            | The spatial coordinates of the turret (hashed).                             |
| `energy_source_id` | `Option<ID>`          | The ID of the connected Network Node (empty when orphaned).                |
| `metadata`         | `Option<Metadata>`    | Optional metadata attached to the turret.                                   |
| `extension`        | `Option<TypeName>`    | The registered extension's type name, if any.                               |

### `TurretTarget`

Represents a potential target in the turret's proximity. Serialized via BCS for on-chain priority list management.

| Field                      | Type   | Description                                                       |
| -------------------------- | ------ | ----------------------------------------------------------------- |
| `target_id`                | `ID`   | Sui object ID of the target.                                      |
| `target_type_id`           | `u64`  | Type identifier of the target (ship or NPC).                      |
| `target_group_id`          | `u64`  | Group ID for ship classification (0 for NPCs); see table below.   |
| `target_character_id`      | `ID`   | Pilot's character ID (zero-address for NPCs).                     |
| `target_character_tribe`   | `u32`  | Tribe ID of the target's pilot.                                   |
| `hp_ratio`                 | `u64`  | Percentage of structure HP remaining (0–100).                     |
| `shield_ratio`             | `u64`  | Percentage of shield HP remaining (0–100).                        |
| `armor_ratio`              | `u64`  | Percentage of armor HP remaining (0–100).                         |
| `is_agressor`              | `bool` | `true` if the target is attacking anything on-grid.               |
| `weight`                   | `u64`  | Priority weight for queue ordering.                               |

### `OnlineReceipt`

A **hot potato** (non-storable, non-droppable struct) returned by `verify_online`. It proves the turret was online at call time and must be consumed before the transaction ends.

| Field       | Type | Description                            |
| ----------- | ---- | -------------------------------------- |
| `turret_id` | `ID` | The turret whose online status was verified. |

## Turret Specializations

Different turret types are specialized against specific ship classes via `target_group_id`:

| Turret Type        | Type ID | Specialized Against                      |
| ------------------ | ------- | ---------------------------------------- |
| Autocannon         | 92402   | Shuttle (group 31), Corvette (group 237) |
| Plasma             | 92403   | Frigate (group 25), Destroyer (group 420)|
| Howitzer            | 92484   | Cruiser (group 26), Combat BC (group 419)|

These group IDs can be used in extension logic to prioritize targets or lower their priority based on the turret's specialization.

## Error Codes

| Code | Constant                  | Description                                          |
| ---- | ------------------------- | ---------------------------------------------------- |
| 0    | `ETurretNotAuthorized`    | Caller's `OwnerCap` does not match the turret.       |
| 1    | `ENetworkNodeMismatch`    | Provided network node does not match `energy_source_id`. |
| 2    | `ENotOnline`              | Turret must be online for this operation.             |
| 3    | `ETurretTypeIdEmpty`      | `type_id` must be non-zero when anchoring.            |
| 4    | `ETurretItemIdEmpty`      | `item_id` must be non-zero when anchoring.            |
| 5    | `ETurretAlreadyExists`    | A turret with this item ID is already registered.     |
| 6    | `ETurretHasEnergySource`  | Cannot unanchor orphan while energy source is set.    |
| 7    | `EExtensionConfigured`    | Default `get_target_priority_list` cannot run when an extension is configured. |
| 8    | `EInvalidOnlineReceipt`   | The `OnlineReceipt` turret ID does not match.         |

## Events

| Event                       | Fields                                            | Emitted When                         |
| --------------------------- | ------------------------------------------------- | ------------------------------------ |
| `TurretCreatedEvent`        | `turret_id`, `turret_key`, `owner_cap_id`, `type_id` | A new turret is anchored.            |
| `PriorityListUpdatedEvent`  | `turret_id`, `priority_list`                      | The targeting priority list changes. |

## Core Functions

### Owner Functions

These require a valid `OwnerCap<Turret>` borrowed from the owner's [Character](../../entities/character/character.move/).

* **`authorize_extension<Auth>`** — Registers (or replaces) a custom extension witness type on the turret. Once set, the game routes `get_target_priority_list` calls to the extension package.
* **`online`** — Brings the turret online, reserving energy from its connected Network Node.
* **`offline`** — Takes the turret offline and releases its energy reservation.

### Targeting Functions

* **`verify_online`** — Returns an `OnlineReceipt` (hot potato) proving the turret is online. Aborts with `ENotOnline` if offline.
* **`get_target_priority_list`** — The default targeting entry point. Accepts the turret, owner character, current priority list (BCS bytes), new target (BCS bytes), and an `OnlineReceipt`. Applies default rules and returns the updated list. Aborts with `EExtensionConfigured` if an extension is registered (the game should call the extension's function instead).
* **`destroy_online_receipt<Auth>`** — Consumes an `OnlineReceipt` using a typed witness. Used by extension contracts after custom targeting logic.
* **`unpack_priority_list`** — Deserializes `vector<TurretTarget>` from BCS bytes.
* **`peel_turret_target`** — Deserializes a single `TurretTarget` from BCS bytes.

### Network Node Integration (Hot Potato)

These functions handle the hot-potato patterns used when [Network Node](../network-node/network_node.move/) state changes affect connected turrets.

* **`update_energy_source_connected_turret`** — Processes the `UpdateEnergySources` hot potato when a turret is connected to a new network node via `connect_assemblies`.
* **`offline_connected_turret`** — Processes the `OfflineAssemblies` hot potato when a network node is brought offline, taking connected turrets offline.
* **`offline_orphaned_turret`** — Processes the `HandleOrphanedAssemblies` hot potato when a network node is unanchored, taking connected turrets offline and clearing their energy source.

### Admin Functions

These require `AdminACL` sponsor verification.

* **`anchor`** — Creates a new Turret, connects it to a Network Node, creates an `OwnerCap<Turret>`, and emits `TurretCreatedEvent`. Returns the `Turret` object (must be shared via `share_turret`).
* **`share_turret`** — Converts the turret into a Sui shared object.
* **`update_energy_source`** — Reconnects an offline turret to a different Network Node (e.g., after the original was destroyed).
* **`unanchor`** — Destroys a turret, releases energy, disconnects from its network node, and cleans up all composed primitives.
* **`unanchor_orphan`** — Destroys an orphaned turret (no energy source). Asserts the turret is offline and has no energy source.

### View Functions

| Function                   | Returns              | Description                                       |
| -------------------------- | -------------------- | ------------------------------------------------- |
| `status`                   | `&AssemblyStatus`    | Current assembly status.                          |
| `location`                 | `&Location`          | Hashed spatial coordinates.                       |
| `is_online`                | `bool`               | Whether the turret is online.                     |
| `owner_cap_id`             | `ID`                 | ID of the turret's `OwnerCap`.                    |
| `energy_source_id`         | `&Option<ID>`        | Connected network node ID.                        |
| `extension_type`           | `TypeName`           | The configured extension type (aborts if none).   |
| `is_extension_configured`  | `bool`               | Whether an extension is registered.               |
| `type_id`                  | `u64`                | The turret's type identifier.                     |

`TurretTarget` field accessors: `target_id`, `target_type_id`, `target_group_id`, `target_character_id`, `target_character_tribe`, `hp_ratio`, `shield_ratio`, `armor_ratio`, `is_agressor`, `weight`.

`OnlineReceipt` accessor: `turret_id`.

## Default Targeting Rules

When no extension is configured, `apply_target_priority_rules` applies these rules to each new target:

```mermaid
flowchart TD
    A[New Target] --> B{is_agressor?}
    B -->|Yes| C[Add to priority list]
    B -->|No| D{Same tribe as owner?}
    D -->|No| C
    D -->|Yes| E[Ignore target]
```

1. **Aggressors** — Any target flagged as `is_agressor` (attacking something on-grid) is always added.
2. **Different Tribe** — Non-aggressive targets from a different tribe than the turret owner are added.
3. **Same Tribe** — Non-aggressive same-tribe targets are ignored.

## Lifecycle Example

```mermaid
sequenceDiagram
    participant Admin
    participant NWN as Network Node
    participant Turret
    participant Owner
    participant Game

    Admin->>Turret: anchor(registry, nwn, character, ...)
    Admin->>Turret: share_turret()
    Owner->>NWN: deposit fuel & online
    Owner->>Turret: online(nwn, energy_config, owner_cap)
    Game->>Turret: verify_online() → OnlineReceipt
    Game->>Turret: get_target_priority_list(turret, character, list, target, receipt)
    Turret-->>Game: updated priority list (BCS bytes)
    Owner->>Turret: offline(nwn, energy_config, owner_cap)
    Admin->>Turret: unanchor(nwn, energy_config)
```

## Related Documentation

* [Assembly Framework](../assembly.move/) — Base assembly lifecycle
* [Network Node](../network-node/network_node.move/) — Providing energy to turrets
* [Extension Examples](../../extension-examples/) — Examples of custom logic, including [Turret Extension](../../extension-examples/turret.move/)
* [Smart Assemblies Overview](/develop/smart-assemblies-intro/) — High-level guide to programmable assemblies
* [Ownership Model](/develop/ownership-model/) — Borrow-use-return pattern for `OwnerCap`
* [Status Primitive](../../primitives/status.move/) — Assembly status lifecycle
* [Location Primitive](../../primitives/location.move/) — Spatial coordinate management
* [Energy Primitive](../../primitives/energy.move/) — Energy reservation and release

{{% tip-menu-search %}}
